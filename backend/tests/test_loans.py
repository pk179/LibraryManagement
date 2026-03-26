import pytest
from datetime import datetime, timedelta
from loans import FINE_PER_DAY


# Test that borrowing available books works correctly
@pytest.mark.parametrize("book_id", [3, 7, 18, 26])
def test_borrow_available_book(client, user_token, user_headers, book_id, current_user):
    quantity_before = client.get(
        f"/api/books/view/{book_id}").json()["quantity"]
    assert quantity_before > 0

    r = client.post(
        "/api/loans/", json={"book_id": book_id}, headers=user_headers(user_token))
    assert r.status_code == 201

    response = r.json()

    assert response["message"] == "Book borrowed"
    assert response["loan"]["id"] is not None
    assert response["loan"]["user_id"] == current_user["id"]
    assert response["loan"]["book_id"] == book_id
    assert isinstance(response["loan"]["title"], str)
    assert isinstance(response["loan"]["author"], str)
    assert response["loan"]["borrow_date"] is not None
    assert response["loan"]["due_date"] is not None
    assert response["loan"]["return_date"] is None
    assert response["loan"]["fine"] == 0.0

    borrow_date = datetime.fromisoformat(response["loan"]["borrow_date"])
    now = datetime.now()
    assert abs((now - borrow_date).total_seconds()) < 10

    due_date = datetime.fromisoformat(response["loan"]["due_date"])
    assert due_date.date() == (borrow_date + timedelta(days=30)).date()

    quantity_after = client.get(
        f"/api/books/view/{book_id}").json()["quantity"]
    assert quantity_after == quantity_before - 1

    r = client.get("/api/loans/active/", headers=user_headers(user_token))
    assert r.status_code == 200
    loans = r.json()
    assert any(loan["book_id"] == book_id and loan["return_date"]
               is None for loan in loans)


# Test that borrowing a book requires login.
def test_borrow_book_requires_login(client):
    r = client.post("/api/loans/", json={"book_id": 1})
    assert r.status_code == 403
    assert r.json()["detail"] == "Not authenticated"


# Test that borrowing books above the limit fails and quantity does not change
def test_borrow_books_above_limit(client, admin_token, admin_headers):
    for book_id in [1, 2, 3]:
        r = client.post(
            "/api/loans/", json={"book_id": book_id}, headers=admin_headers(admin_token))
        assert r.status_code == 201

    quantity_before = client.get(f"/api/books/view/4").json()["quantity"]
    assert quantity_before > 0

    r = client.post(
        "/api/loans/", json={"book_id": 4}, headers=admin_headers(admin_token))
    assert r.status_code == 409
    assert r.json()["detail"] == "Maximum number of borrowed books reached (3)"

    quantity_after = client.get(f"/api/books/view/4").json()["quantity"]
    assert quantity_after == quantity_before


# Test that borrowing multiple copies of the same book works correctly.
def test_borrow_multiple_copies(client, admin_token, admin_headers):
    quantity_before = client.get(
        f"/api/books/view/1").json()["quantity"]
    assert quantity_before > 2

    for _ in range(3):
        r = client.post(
            "/api/loans/", json={"book_id": 1}, headers=admin_headers(admin_token))
        assert r.status_code == 201

    quantity_after = client.get(
        f"/api/books/view/1").json()["quantity"]
    assert quantity_after == quantity_before - 3


# Test that borrowing an unavailable book (quantity==0) fails and quantity does not change.
def test_borrow_unavailable_book(client, admin_token, admin_headers):
    quantity_before = client.get(f"/api/books/view/5").json()["quantity"]
    assert quantity_before == 0

    r = client.post(
        "/api/loans/", json={"book_id": 5}, headers=admin_headers(admin_token))
    assert r.status_code == 409
    assert r.json()["detail"] == "Book is not available"

    quantity_after = client.get(f"/api/books/view/5").json()["quantity"]
    assert quantity_after == quantity_before


# Test that borrowing a non-existing book fails.
def test_borrow_non_existing_book(client, admin_token, admin_headers):
    r = client.post(
        "/api/loans/", json={"book_id": 999}, headers=admin_headers(admin_token))
    assert r.status_code == 404
    assert r.json()["detail"] == "Book not found"


# Test that borrowing a book with invalid input fails.
@pytest.mark.parametrize("book_id", ["a", None])
def test_borrow_invalid_book(client, admin_token, admin_headers, book_id):
    r = client.post(
        "/api/loans/", json={"book_id": book_id}, headers=admin_headers(admin_token))
    assert r.status_code == 422
    assert r.json()["detail"][0]["type"] in ["int_parsing", "int_type"]


# Test that returning books works correctly
def test_return_book(client, user_token, user_headers, current_user):
    r = client.post(
        "/api/loans/", json={"book_id": 1}, headers=user_headers(user_token))
    assert r.status_code == 201

    quantity_before = client.get(
        f"/api/books/view/1").json()["quantity"]

    r = client.post(
        "/api/loans/return/", json={"book_id": 1}, headers=user_headers(user_token))
    assert r.status_code == 200

    response = r.json()

    assert response["message"] == "Book returned"
    assert response["loan"]["id"] is not None
    assert response["loan"]["user_id"] == current_user["id"]
    assert response["loan"]["book_id"] == 1
    assert isinstance(response["loan"]["title"], str)
    assert isinstance(response["loan"]["author"], str)
    assert isinstance(response["loan"]["borrow_date"], str)
    assert isinstance(response["loan"]["due_date"], str)
    assert response["loan"]["return_date"] is not None
    assert isinstance(response["loan"]["fine"], float)

    return_date = datetime.fromisoformat(response["loan"]["return_date"])
    now = datetime.now()
    assert abs((now - return_date).total_seconds()) < 30

    quantity_after = client.get(
        f"/api/books/view/1").json()["quantity"]
    assert quantity_after == quantity_before + 1


# Test that returning overdue book and calculating fine works correctly.
def test_return_book_overdue(client, user_token, user_headers):
    # Overdue loan exists in database seed
    r = client.post(
        "/api/loans/return/", json={"book_id": 3}, headers=user_headers(user_token))
    assert r.status_code == 200

    loan = r.json()["loan"]
    fine = loan["fine"]
    due_date = datetime.fromisoformat(loan["due_date"])
    return_date = datetime.fromisoformat(loan["return_date"])

    overdue_days = (return_date.date() - due_date.date()).days
    expected_fine = overdue_days * FINE_PER_DAY
    assert fine == expected_fine


# Test that returning a book requires login.
def test_return_book_requires_login(client):
    r = client.post("/api/loans/return/", json={"book_id": 1})
    assert r.status_code == 403
    assert r.json()["detail"] == "Not authenticated"


# Test that returning a book that was not borrowed by the current user or a non-existing book fails.
@pytest.mark.parametrize("book_id", [1, 3, 25, 999])
def test_return_non_existing_book(client, admin_token, admin_headers, book_id):
    r = client.post(
        "/api/loans/return/", json={"book_id": book_id}, headers=admin_headers(admin_token))
    assert r.status_code == 404
    assert r.json()["detail"] == "Active loan for this book not found"


# Test that returning a book with invalid input fails.
@pytest.mark.parametrize("book_id", ["a", None])
def test_return_invalid_book(client, user_token, user_headers, book_id):
    r = client.post(
        "/api/loans/return/", json={"book_id": book_id}, headers=user_headers(user_token))
    assert r.status_code == 422
    assert r.json()["detail"][0]["type"] in ["int_parsing", "int_type"]


# Test that returning book after it was already returned fails.
def test_return_book_twice(client, user_token, user_headers):
    r = client.post(
        "/api/loans/", json={"book_id": 1}, headers=user_headers(user_token))
    assert r.status_code == 201

    r = client.post(
        "/api/loans/return/", json={"book_id": 1}, headers=user_headers(user_token))
    assert r.status_code == 200

    r = client.post(
        "/api/loans/return/", json={"book_id": 1}, headers=user_headers(user_token))
    assert r.status_code == 404
    assert r.json()["detail"] == "Active loan for this book not found"


# Test that displaying active loans made by the current user works correctly.
def test_get_active_user_loans(client, user_token, user_headers, current_user):
    r = client.post(
        "/api/loans/", json={"book_id": 3}, headers=user_headers(user_token))
    assert r.status_code == 201

    r = client.get("/api/loans/active/", headers=user_headers(user_token))
    assert r.status_code == 200

    loans = r.json()
    assert isinstance(loans, list)
    assert len(loans) > 0
    assert all(loan["id"] is not None for loan in loans)
    assert all(loan["user_id"] == current_user["id"] for loan in loans)
    assert all(loan["book_id"] is not None for loan in loans)
    assert all(isinstance(loan["title"], str) for loan in loans)
    assert all(isinstance(loan["author"], str) for loan in loans)
    assert all(isinstance(loan["borrow_date"], str) for loan in loans)
    assert all(isinstance(loan["due_date"], str) for loan in loans)
    assert all(loan["return_date"] is None for loan in loans)
    assert all(isinstance(loan["fine"], float) for loan in loans)


# Test that displaying active loans requires login.
def test_get_active_user_loans_requires_login(client):
    r = client.get("/api/loans/active/")
    assert r.status_code == 403
    assert r.json()["detail"] == "Not authenticated"


# Test that displaying returned loans made by the current user works correctly.
def test_get_returned_user_loans(client, user_token, user_headers, current_user):
    r = client.post(
        "/api/loans/", json={"book_id": 3}, headers=user_headers(user_token))
    assert r.status_code == 201

    r = client.post(
        "/api/loans/return/", json={"book_id": 3}, headers=user_headers(user_token))
    assert r.status_code == 200

    r = client.get("/api/loans/returned/", headers=user_headers(user_token))
    assert r.status_code == 200

    loans = r.json()
    assert isinstance(loans, list)
    assert len(loans) > 0
    assert all(loan["id"] is not None for loan in loans)
    assert all(loan["user_id"] == current_user["id"] for loan in loans)
    assert all(loan["book_id"] is not None for loan in loans)
    assert all(isinstance(loan["title"], str) for loan in loans)
    assert all(isinstance(loan["author"], str) for loan in loans)
    assert all(isinstance(loan["borrow_date"], str) for loan in loans)
    assert all(isinstance(loan["due_date"], str) for loan in loans)
    assert all(loan["return_date"] is not None for loan in loans)
    assert all(isinstance(loan["fine"], float) for loan in loans)


# Test that displaying returned loans requires login.
def test_get_returned_user_loans_requires_login(client):
    r = client.get("/api/loans/returned/")
    assert r.status_code == 403
    assert r.json()["detail"] == "Not authenticated"


# Test that displaying overdue loans made by the current user and calculating fine works correctly.
def test_get_overdue_user_loans(client, user_token, user_headers, current_user):
    r = client.get("/api/loans/overdue/", headers=user_headers(user_token))
    assert r.status_code == 200

    loans = r.json()
    assert isinstance(loans, list)
    assert len(loans) > 0
    assert all(loan["id"] is not None for loan in loans)
    assert all(loan["user_id"] == current_user["id"] for loan in loans)
    assert all(loan["book_id"] is not None for loan in loans)
    assert all(isinstance(loan["title"], str) for loan in loans)
    assert all(isinstance(loan["author"], str) for loan in loans)
    assert all(isinstance(loan["borrow_date"], str) for loan in loans)
    assert all(isinstance(loan["due_date"], str) for loan in loans)
    assert all(loan["return_date"] is None for loan in loans)
    assert all(loan["fine"] > 0.0 for loan in loans)

    for loan in loans:
        due_date = datetime.fromisoformat(loan["due_date"])
        now = datetime.now()
        assert now.date() > due_date.date()

        overdue_days = (now.date() - due_date.date()).days
        expected_fine = overdue_days * FINE_PER_DAY
        assert loan["fine"] == expected_fine


# Test that displaying overdue loans requires login.
def test_get_overdue_user_loans_requires_login(client):
    r = client.get("/api/loans/overdue/")
    assert r.status_code == 403
    assert r.json()["detail"] == "Not authenticated"


# Test that displaying all loans works correctly.
def test_get_all_loans(client, admin_token, admin_headers):
    r = client.get("/api/loans/all/", headers=admin_headers(admin_token))
    assert r.status_code == 200

    loans = r.json()
    assert isinstance(loans, list)
    assert len(loans) > 0
    assert all(loan["id"] is not None for loan in loans)
    assert all(loan["user_id"] is not None for loan in loans)
    assert all(loan["book_id"] is not None for loan in loans)
    assert all(isinstance(loan["title"], str) for loan in loans)
    assert all(isinstance(loan["author"], str) for loan in loans)
    assert all(isinstance(loan["borrow_date"], str) for loan in loans)
    assert all(isinstance(loan["due_date"], str) for loan in loans)
    assert all(isinstance(loan["return_date"], str)
               or loan["return_date"] is None for loan in loans)
    assert all(isinstance(loan["fine"], float) for loan in loans)


# Test that displaying all loans requires admin role.
def test_get_all_loans_requires_admin(client, user_token, user_headers):
    r = client.get("/api/loans/all/", headers=user_headers(user_token))
    assert r.status_code == 403

    r = client.get("/api/loans/all/")
    assert r.status_code == 403


# Test that displaying all overdue loans works correctly.
def test_get_all_overdue_loans(client, admin_token, admin_headers):
    r = client.get("/api/loans/all/overdue/",
                   headers=admin_headers(admin_token))
    assert r.status_code == 200

    loans = r.json()
    assert isinstance(loans, list)
    assert len(loans) > 0
    assert all(loan["id"] is not None for loan in loans)
    assert all(loan["user_id"] is not None for loan in loans)
    assert all(loan["book_id"] is not None for loan in loans)
    assert all(isinstance(loan["title"], str) for loan in loans)
    assert all(isinstance(loan["author"], str) for loan in loans)
    assert all(isinstance(loan["borrow_date"], str) for loan in loans)
    assert all(isinstance(loan["due_date"], str) for loan in loans)
    assert all(loan["return_date"] is None for loan in loans)
    assert all(loan["fine"] > 0.0 for loan in loans)

    for loan in loans:
        due_date = datetime.fromisoformat(loan["due_date"])
        now = datetime.now()
        assert now.date() > due_date.date()

        overdue_days = (now.date() - due_date.date()).days
        expected_fine = overdue_days * FINE_PER_DAY
        assert loan["fine"] == expected_fine


# Test that displaying all overdue loans requires admin role.
def test_get_all_overdue_loans_requires_admin(client, user_token, user_headers):
    r = client.get("/api/loans/all/overdue/", headers=user_headers(user_token))
    assert r.status_code == 403

    r = client.get("/api/loans/all/overdue/")
    assert r.status_code == 403


# Test that overdue loans are a subset of all loans.
def test_overdue_is_subset(client, admin_token, admin_headers):
    all_loans = client.get(
        "/api/loans/all/", headers=admin_headers(admin_token)).json()
    overdue_loans = client.get(
        "/api/loans/all/overdue/", headers=admin_headers(admin_token)).json()

    assert len(overdue_loans) <= len(all_loans)

    all_ids = {loan["id"] for loan in all_loans}
    for loan in overdue_loans:
        assert loan["id"] in all_ids


# Test that displaying loan statistics works correctly.
def test_get_loan_stats(client, admin_token, admin_headers):
    r = client.get("/api/loans/stats/", headers=admin_headers(admin_token))
    assert r.status_code == 200

    stats = r.json()
    assert isinstance(stats["total_loans"], int)
    assert isinstance(stats["active_loans"], int)
    assert isinstance(stats["overdue_loans"], int)
    assert isinstance(stats["returned_loans"], int)

    assert stats["total_loans"] == stats["active_loans"] + \
        stats["returned_loans"]

    r = client.get("/api/loans/all/", headers=admin_headers(admin_token))
    assert r.status_code == 200

    all_loans_length = len(r.json())
    assert stats["total_loans"] == all_loans_length

    r = client.get("/api/loans/all/overdue/",
                   headers=admin_headers(admin_token))
    assert r.status_code == 200

    overdue_loans_length = len(r.json())
    assert stats["overdue_loans"] == overdue_loans_length


# Test that displaying loan statistics requires admin role.
def test_get_loan_stats_requires_admin(client, user_token, user_headers):
    r = client.get("/api/loans/stats/", headers=user_headers(user_token))
    assert r.status_code == 403

    r = client.get("/api/loans/stats/")
    assert r.status_code == 403
