# Test that the admin can reset the database and the user table is restored to its initial state.
def test_reset_users(client, admin_token, admin_headers):
    # Add a new user to the database
    r = client.post(
        "/api/auth/register",
        json={"username": "testuser", "password": "Test12345", "role": "user"},
        headers=admin_headers(admin_token),
    )
    assert r.status_code == 201

    # Verify the user was added
    r = client.get("/api/users",
                   headers=admin_headers(admin_token))
    assert r.status_code == 200
    users = r.json()
    assert any(user["username"] == "testuser" for user in users)

    # Reset the database
    r = client.post("/api/admin/reset",
                    headers=admin_headers(admin_token))
    assert r.status_code == 200

    # Verify the user was removed
    r = client.get("/api/users",
                   headers=admin_headers(admin_token))
    assert r.status_code == 200
    users = r.json()

    usernames = [u["username"] for u in users]
    assert "admin" in usernames
    assert "user" in usernames
    assert "testuser" not in usernames
    assert len(usernames) == 2


# Test that the books table is restored to its initial state.
def test_reset_books(client, admin_token, admin_headers):
    # Add a new book to the database
    r = client.post(
        "/api/books",
        json={"title": "Test Book", "author": "Test Author",
              "year": 2024, "quantity": 5},
        headers=admin_headers(admin_token),
    )
    assert r.status_code == 201

    # Verify the book was added
    r = client.get("/api/books",
                   headers=admin_headers(admin_token))
    assert r.status_code == 200
    books = r.json()
    assert any(book["title"] == "Test Book" for book in books)

    # Reset the database
    r = client.post("/api/admin/reset",
                    headers=admin_headers(admin_token))
    assert r.status_code == 200

    # Verify the book was removed
    r = client.get("/api/books",
                   headers=admin_headers(admin_token))
    assert r.status_code == 200
    books = r.json()
    assert all(book["title"] != "Test Book" for book in books)
    assert len(books) == 30


# Test that the loans table is restored to its initial state.
def test_reset_loans(client, admin_token, admin_headers):
    # Add a new loan to the database
    r = client.post(
        "/api/loans",
        json={"user_id": 1, "book_id": 1},
        headers=admin_headers(admin_token),
    )
    assert r.status_code == 201

    # Verify the loan was added
    r = client.get("/api/loans/all",
                   headers=admin_headers(admin_token))
    assert r.status_code == 200
    loans = r.json()
    assert any(loan["user_id"] == 1 and loan["book_id"] == 1 for loan in loans)

    # Reset the database
    r = client.post("/api/admin/reset",
                    headers=admin_headers(admin_token))
    assert r.status_code == 200

    # Verify the loan was removed
    r = client.get("/api/loans/all",
                   headers=admin_headers(admin_token))
    assert r.status_code == 200
    loans = r.json()
    assert all(not (loan["user_id"] == 1 and loan["book_id"] == 1)
               for loan in loans)
    assert len(loans) == 3


# Test that only admins can reset the database.
def test_reset_requires_admin(client, user_token, user_headers):
    r = client.post("/api/admin/reset",
                    headers=user_headers(user_token))
    assert r.status_code == 403

    r = client.post("/api/admin/reset")
    assert r.status_code == 403
