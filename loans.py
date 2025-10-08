import sqlite3
import utils
from datetime import datetime, timedelta

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

    conn = sqlite3.connect('library.db')
    c = conn.cursor()

    # Check if the user has reached the maximum number of borrows
    c.execute("SELECT COUNT(*) FROM loans WHERE user_id = ? AND return_date IS NULL",
              (utils.get_current_user()["id"],))
    active_loans = c.fetchone()[0]
    if active_loans >= MAX_BORROWS:
        print(
            f"You have reached the maximum number of borrows ({MAX_BORROWS}). Return some books before borrowing more.")
        conn.close()
        return

    # Check if the book exists and is available
    c.execute("SELECT quantity, title FROM books WHERE id = ?", (book_id,))
    book = c.fetchone()
    if not book:
        print("Book not found.")
        conn.close()
        return
    quantity, title = book
    if quantity <= 0:
        print(f"Sorry, '{title}' is currently not available.")
        conn.close()
        return

    # Borrow the book: decrease quantity and add a loan entry
    due_date = (datetime.now() + timedelta(days=BORROW_DAYS)
                ).strftime("%Y-%m-%d")
    c.execute("""
        INSERT INTO loans (user_id, book_id, borrow_date, due_date, fine)
        VALUES (?, ?, CURRENT_TIMESTAMP, ?, 0)
    """, (utils.get_current_user()["id"], book_id, due_date))
    c.execute("UPDATE books SET quantity = quantity - 1 WHERE id = ?", (book_id,))

    conn.commit()
    conn.close()
    print(
        f"You have successfully borrowed '{title}'. It is due on {due_date}.")


def return_book(book_id):
    """
    Return a borrowed book. Increase its quantity and update the loan entry with the return date.
    """
    if not utils.is_logged_in():
        print("You must be logged in to return a book.")
        return

    conn = sqlite3.connect('library.db')
    c = conn.cursor()

    # Check if the current user has borrowed this book and not yet returned it
    c.execute(
        "SELECT id, due_date FROM loans WHERE user_id = ? AND book_id = ? AND return_date IS NULL",
        (utils.get_current_user()["id"], book_id)
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
    c.execute("UPDATE books SET quantity = quantity + 1 WHERE id = ?", (book_id,))

    conn.commit()
    conn.close()
    print("Book returned successfully.")
