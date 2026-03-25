import pytest


# Test that get all books endpoint works correctly.
def test_get_all_books(client):
    r = client.get("/api/books")
    assert r.status_code == 200

    books = r.json()
    assert isinstance(books, list)
    assert len(books) > 0
    assert any(book["quantity"] == 0 for book in books)
    assert any(book["quantity"] > 0 for book in books)


# Test that available filter works correctly.
def test_get_available_books(client):
    r = client.get("/api/books?available=true")
    assert r.status_code == 200

    books = r.json()
    assert isinstance(books, list)
    assert len(books) > 0
    assert all(book["quantity"] > 0 for book in books)


# Test that available books are a subset of all books.
def test_available_is_subset(client):
    all_books = client.get("/api/books").json()
    available_books = client.get("/api/books?available=true").json()

    assert len(available_books) <= len(all_books)

    for book in available_books:
        assert book in all_books


# Test that the search endpoint returns correct results for title and author queries.
@pytest.mark.parametrize("query", ["girl", "1984", "hitch"])
def test_search_book_by_title(client, query):
    r = client.get(f"/api/books/search?q={query}")
    assert r.status_code == 200

    books = r.json()
    assert isinstance(books, list)
    assert len(books) > 0
    assert all(query in book["title"].lower() for book in books)


@pytest.mark.parametrize("query", ["tolkien", "rowling", "dosto"])
def test_search_book_by_author(client, query):
    r = client.get(f"/api/books/search?q={query}")
    assert r.status_code == 200

    books = r.json()
    assert isinstance(books, list)
    assert len(books) > 0
    assert all(query in book["author"].lower() for book in books)


# Test that the search endpoint returns an empty list when no matches are found.
def test_search_non_existing_book(client):
    r = client.get("/api/books/search?q=nonexistingbook")
    assert r.status_code == 200

    books = r.json()
    assert isinstance(books, list)
    assert len(books) == 0


# Test that the correct book is returned when requested by id.
@pytest.mark.parametrize("book_id", [1, 12, 23])
def test_get_book_by_id(client, book_id):
    r = client.get(f"/api/books/view/{book_id}")
    assert r.status_code == 200

    book = r.json()
    assert isinstance(book, dict)
    assert book["id"] == book_id


# Test that book details are correct when requested by id.
def test_get_book_data(client):
    r = client.get("/api/books/view/1")
    assert r.status_code == 200

    book = r.json()
    assert isinstance(book, dict)
    assert book["id"] == 1
    assert book["title"] == "The Great Gatsby"
    assert book["author"] == "F. Scott Fitzgerald"
    assert book["year"] == 1925
    assert book["quantity"] == 4
    assert book["genre"] == "Fiction"
    assert book["isbn"] == "9780743273565"


# Test that requesting a non-existing book by id returns 404.
def test_get_book_by_non_existing_id(client):
    r = client.get("/api/books/view/9999")
    assert r.status_code == 404


# Test that creating a new book works correctly and returns the correct response.
def test_create_book(client, admin_token, admin_headers):
    new_book = {
        "title": "Test Book",
        "author": "Test Author",
        "year": 2026,
        "quantity": 10,
        "genre": "Test Genre",
        "isbn": "9788364702082",
    }
    r = client.post("/api/books", json=new_book,
                    headers=admin_headers(admin_token))
    assert r.status_code == 201
    assert r.json()["message"] == "Book added"
    assert r.json()["book"]["id"] is not None
    assert r.json()["book"]["title"] == new_book["title"]
    assert r.json()["book"]["author"] == new_book["author"]
    assert r.json()["book"]["year"] == new_book["year"]
    assert r.json()["book"]["quantity"] == new_book["quantity"]
    assert r.json()["book"]["isbn"] == new_book["isbn"]
    assert r.json()["book"]["genre"] == new_book["genre"]


# Test that only admins can create books.
def test_create_book_requires_admin(client, user_token, user_headers):
    new_book = {
        "title": "Test Book",
        "author": "Test Author",
        "year": 2026,
        "quantity": 10,
        "genre": "Test Genre",
        "isbn": "9788364702082",
    }
    r = client.post("/api/books", json=new_book,
                    headers=user_headers(user_token))
    assert r.status_code == 403


# Test that creating a book with negative quantity fails.
def test_create_book_with_negative_quantity(client, admin_token, admin_headers):
    new_book = {
        "title": "Test Book",
        "author": "Test Author",
        "year": 2026,
        "quantity": -5,
        "genre": "Test Genre",
        "isbn": "9788364702082",
    }
    r = client.post("/api/books", json=new_book,
                    headers=admin_headers(admin_token))
    assert r.status_code == 400


# Test that creating a book with invalid ISBN fails.
def test_create_book_with_invalid_isbn(client, admin_token, admin_headers):
    new_book = {
        "title": "Test Book",
        "author": "Test Author",
        "year": 2026,
        "quantity": 10,
        "genre": "Test Genre",
        "isbn": "1234567890",
    }
    r = client.post("/api/books", json=new_book,
                    headers=admin_headers(admin_token))
    assert r.status_code == 400


# Test that creating a book with empty ISBN and genre works and sets them to null in the database.
def test_create_book_with_empty_isbn_and_genre(client, admin_token, admin_headers):
    new_book = {
        "title": "Test Book",
        "author": "Test Author",
        "year": 2026,
        "quantity": 10,
        "genre": "",
        "isbn": "",
    }
    r = client.post("/api/books", json=new_book,
                    headers=admin_headers(admin_token))
    assert r.status_code == 201
    assert r.json()["message"] == "Book added"
    assert r.json()["book"]["id"] is not None
    assert r.json()["book"]["title"] == new_book["title"]
    assert r.json()["book"]["author"] == new_book["author"]
    assert r.json()["book"]["year"] == new_book["year"]
    assert r.json()["book"]["quantity"] == new_book["quantity"]
    assert r.json()["book"]["isbn"] is None
    assert r.json()["book"]["genre"] is None


# Test that creating a book with an ISBN that already exists updates the quantity of the existing book instead of creating a new one.
def test_create_book_with_duplicate_isbn(client, admin_token, admin_headers):
    existing_book = client.get(
        "/api/books/view/1", headers=admin_headers(admin_token)).json()
    quantity_before = existing_book["quantity"]

    new_book = {
        "title": "Test Book",
        "author": "Test Author",
        "year": 2026,
        "quantity": 10,
        "genre": "Test Genre",
        "isbn": "978-0-7432-7356-5",
    }
    r = client.post("/api/books", json=new_book,
                    headers=admin_headers(admin_token))
    assert r.status_code == 201
    assert r.json()["message"] == "Quantity updated"

    updated_book = client.get(
        "/api/books/view/1", headers=admin_headers(admin_token)).json()
    assert updated_book["quantity"] == quantity_before + new_book["quantity"]


# Test that creating a book with empty required fields fails.
def test_create_book_with_empty_required_fields(client, admin_token, admin_headers):
    new_book = {
        "title": "",
        "author": "",
        "year": 2026,
        "quantity": 10,
        "genre": "Test Genre",
        "isbn": "9788364702082",
    }
    r = client.post("/api/books", json=new_book,
                    headers=admin_headers(admin_token))
    assert r.status_code == 400


# Test that creating a book with missing required fields fails.
def test_create_book_with_missing_fields(client, admin_token, admin_headers):
    new_book = {
        "author": "Test Author",
        "year": 2026,
        "quantity": 10,
    }
    r = client.post("/api/books", json=new_book,
                    headers=admin_headers(admin_token))
    assert r.status_code == 422


# Test that updating an existing book works correctly and returns the correct response.
def test_update_book(client, admin_token, admin_headers):
    updated_data = {
        "title": "Updated Title",
        "author": "Updated Author",
        "year": 2020,
        "quantity": 7,
        "genre": "Updated Genre",
        "isbn": "9780743273565",
    }
    r = client.put("/api/books/1", json=updated_data,
                   headers=admin_headers(admin_token))
    assert r.status_code == 200
    assert r.json()["message"] == "Book updated"
    assert r.json()["book"]["id"] == 1
    assert r.json()["book"]["title"] == updated_data["title"]
    assert r.json()["book"]["author"] == updated_data["author"]
    assert r.json()["book"]["year"] == updated_data["year"]
    assert r.json()["book"]["quantity"] == updated_data["quantity"]
    assert r.json()["book"]["genre"] == updated_data["genre"]
    assert r.json()["book"]["isbn"] == updated_data["isbn"]


# Test that updating a book requires admin role.
def test_update_book_requires_admin(client, user_token, user_headers):
    updated_data = {
        "title": "Updated Title",
        "author": "Updated Author",
        "year": 2020,
        "quantity": 7,
        "genre": "Updated Genre",
        "isbn": "9788364702082",
    }
    r = client.put("/api/books/1", json=updated_data,
                   headers=user_headers(user_token))
    assert r.status_code == 403


# Test that partial update works correctly.
def test_update_with_missing_fields(client, admin_token, admin_headers):
    old_book = client.get("/api/books/view/1").json()
    updated_data = {
        "title": "Updated Title",
        "quantity": 12,
        "genre": "Updated Genre",
    }
    r = client.put("/api/books/1", json=updated_data,
                   headers=admin_headers(admin_token))
    assert r.status_code == 200
    assert r.json()["message"] == "Book updated"
    assert r.json()["book"]["id"] == 1
    assert r.json()["book"]["title"] == updated_data["title"]
    assert r.json()["book"]["author"] == old_book["author"]
    assert r.json()["book"]["year"] == old_book["year"]
    assert r.json()["book"]["quantity"] == updated_data["quantity"]
    assert r.json()["book"]["genre"] == updated_data["genre"]
    assert r.json()["book"]["isbn"] == old_book["isbn"]


# Test that updating a book with empty fields fails.
def test_update_with_empty_fields(client, admin_token, admin_headers):
    updated_data = {
        "title": "",
        "author": "Updated Author",
        "year": 2020,
        "quantity": 7,
        "genre": "Updated Genre",
        "isbn": "9788364702082",
    }
    r = client.put("/api/books/1", json=updated_data,
                   headers=admin_headers(admin_token))
    assert r.status_code == 400


# Test that updating an existing book with a negative quantity fails.
def test_update_book_with_negative_quantity(client, admin_token, admin_headers):
    updated_data = {
        "title": "Updated Title",
        "author": "Updated Author",
        "year": 2020,
        "quantity": -5,
        "genre": "Updated Genre",
        "isbn": "9788364702082",
    }
    r = client.put("/api/books/1", json=updated_data,
                   headers=admin_headers(admin_token))
    assert r.status_code == 400


# Test that updating an existing book with isbn of another existing book fails.
def test_update_book_with_existing_isbn(client, admin_token, admin_headers):
    updated_data = {
        "title": "Updated Title",
        "author": "Updated Author",
        "year": 2020,
        "quantity": 7,
        "genre": "Updated Genre",
        "isbn": "9780141439518",
    }
    r = client.put("/api/books/1", json=updated_data,
                   headers=admin_headers(admin_token))
    assert r.status_code == 409
    assert r.json()["detail"] == "ISBN already exists"


# Test that updating a non-existing book fails.
def test_update_non_existing_book(client, admin_token, admin_headers):
    updated_data = {
        "title": "Updated Title",
        "author": "Updated Author",
        "year": 2020,
        "quantity": 7,
        "genre": "Updated Genre",
        "isbn": "9788364702082",
    }
    r = client.put("/api/books/9999", json=updated_data,
                   headers=admin_headers(admin_token))
    assert r.status_code == 404


# Test that deleting an existing book works correctly.
def test_delete_book(client, admin_token, admin_headers):
    r = client.delete("/api/books/1", headers=admin_headers(admin_token))
    assert r.status_code == 200
    assert r.json()["message"] == "Book deleted"

    r = client.get("/api/books/view/1", headers=admin_headers(admin_token))
    assert r.status_code == 404


# Test that deleting a book requires admin role.
def test_delete_book_requires_admin(client, user_token, user_headers):
    r = client.delete("/api/books/2", headers=user_headers(user_token))
    assert r.status_code == 403


# Test that deleting a non-existing book fails.
def test_delete_non_existing_book(client, admin_token, admin_headers):
    r = client.delete("/api/books/9999", headers=admin_headers(admin_token))
    assert r.status_code == 404


# Test that bulk deleting books with valid and invalid IDs works correctly.
def test_bulk_delete_books(client, admin_token, admin_headers):
    # Bulk delete three existing books and two non-existing books
    r = client.request("DELETE", "/api/books/",
                       json=[5, 12, 25, 134, 9999],
                       headers=admin_headers(admin_token))
    assert r.status_code == 200
    assert r.json()["deleted"] == [5, 12, 25]
    assert r.json()["not_found"] == [134, 9999]

    r = client.get("/api/books/view/12", headers=admin_headers(admin_token))
    assert r.status_code == 404

    r = client.get("/api/books/view/11", headers=admin_headers(admin_token))
    assert r.status_code == 200


# Test that bulk deleting books with invalid data type fails.
def test_bulk_delete_books_with_invalid_type(client, admin_token, admin_headers):
    r = client.request("DELETE", "/api/books/",
                       json=["a", "bcd"],
                       headers=admin_headers(admin_token))
    assert r.status_code == 422


# Test that bulk deleting books requires admin role
def test_bulk_delete_books_requires_admin(client, user_token, user_headers):
    r = client.request("DELETE", "/api/books/",
                       json=[3, 8, 45],
                       headers=user_headers(user_token))
    assert r.status_code == 403
