from datetime import datetime, timedelta
import database
import logger

MAX_BORROWS = 5
BORROW_DAYS = 30
FINE_PER_DAY = 3.0


def borrow_book(user_id: int, book_id: int):
    """
    Borrow a book if it is available. Decrease its quantity and add a loan entry.
    """

    # Check book existence
    if not database.book_exists(book_id):
        raise ValueError("Book not found")

    # Check quantity
    quantity = database.get_book_quantity(book_id)
    if quantity <= 0:
        raise ValueError("Book is not available")

    # Check active loans limit
    active_loans = database.get_loans_by_user(user_id)
    if len(active_loans) >= MAX_BORROWS:
        raise ValueError(
            f"Maximum number of borrowed books reached ({MAX_BORROWS})")

    # Create loan
    due_date = (datetime.now() + timedelta(days=BORROW_DAYS)).isoformat()

    loan = database.insert_loan(user_id, book_id, due_date)
    if not loan:
        raise RuntimeError("Failed to create loan")

    # Decrease book quantity
    success = database.decrease_book_quantity(book_id)
    if not success:
        raise RuntimeError("Failed to decrease book quantity")

    logger.log_info(
        f"User {user_id} borrowed book {book_id}, due {due_date}"
    )

    return loan


def return_book(user_id: int, book_id: int):
    """
    Return a borrowed book. Increase its quantity and update the loan entry with the return date. Calculate fine if overdue.
    """

    # Find active loan
    loans = database.get_loans_by_user(user_id)
    loan = next((l for l in loans if l["book_id"] == book_id), None)

    if not loan:
        raise ValueError("Active loan for this book not found")

    loan_id = loan["id"]
    due_date = datetime.fromisoformat(loan["due_date"])
    now = datetime.now()

    # Calculate fine
    fine = 0.0
    if now > due_date:
        days_overdue = (now - due_date).days
        fine = days_overdue * FINE_PER_DAY

    # Close loan
    closed = database.close_loan(loan_id, fine)
    if not closed:
        raise RuntimeError("Failed to close loan")

    # Increase quantity
    database.increase_book_quantity(book_id)

    logger.log_info(
        f"User {user_id} returned book {book_id}, fine {fine}"
    )

    return closed
