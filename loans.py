import utils
from datetime import datetime, timedelta
import database as db
import validation as v

MAX_BORROWS = 5
BORROW_DAYS = 14
FINE_PER_DAY = 1.0


def borrow_book(book_id):
    """
    Borrow a book if it is available. Decrease its quantity and add a loan entry.
    """
    if not utils.is_logged_in():
        print("You must be logged in to borrow a book.")
        return

    if not db.book_exists(book_id):
        print("Book not found.")
        return

    current_user = utils.get_current_user()

    conn = db.get_connection()
    c = conn.cursor()

    # Check if the user has reached the maximum number of borrows
    c.execute("SELECT COUNT(*) FROM loans WHERE user_id = ? AND return_date IS NULL",
              (current_user["id"],))
    active_loans = c.fetchone()[0]
    if active_loans >= MAX_BORROWS:
        print(
            f"You have reached the maximum number of borrows ({MAX_BORROWS}). Return some books before borrowing more.")
        conn.close()
        return

    book = db.get_book_by_id(book_id)
    if not book or book[4] <= 0:  # book[4] is the quantity
        print("This book is currently unavailable.")
        conn.close()
        return

    # Borrow the book: decrease quantity and add a loan entry
    due_date = (datetime.now() + timedelta(days=BORROW_DAYS)
                ).strftime("%Y-%m-%d")
    c.execute("""
        INSERT INTO loans (user_id, book_id, borrow_date, due_date, fine)
        VALUES (?, ?, CURRENT_TIMESTAMP, ?, 0)
    """, (current_user["id"], book_id, due_date))
    db.decrease_book_quantity(book_id)

    conn.commit()
    conn.close()
    print(
        f"You have successfully borrowed '{book[1]}'. It is due on {due_date}.")


def return_book(book_id):
    """
    Return a borrowed book. Increase its quantity and update the loan entry with the return date.
    """
    if not utils.is_logged_in():
        print("You must be logged in to return a book.")
        return

    current_user = utils.get_current_user()

    conn = db.get_connection()
    c = conn.cursor()

    # Check if the current user has borrowed this book and not yet returned it
    c.execute(
        "SELECT id, due_date FROM loans WHERE user_id = ? AND book_id = ? AND return_date IS NULL",
        (current_user["id"], book_id)
    )
    loan = c.fetchone()

    if not loan:
        print("You have not borrowed this book or have already returned it.")
        conn.close()
        return

    loan_id, due_date_str = loan
    due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
    today = datetime.now()

    # Calculate fine if the book is returned late
    fine = 0
    if today > due_date:
        days_overdue = (today - due_date).days
        fine = days_overdue * FINE_PER_DAY
        print(
            f"You have a fine of ${fine:.2f} for returning the book {days_overdue} days late.")

    # Update the loan entry with the return date and fine, and increase book quantity
    c.execute(
        "UPDATE loans SET return_date = CURRENT_TIMESTAMP, fine = ? WHERE id = ?", (fine, loan_id))
    db.increase_book_quantity(book_id)

    conn.commit()
    conn.close()
    print("Book returned successfully.")
