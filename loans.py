import sqlite3
from utils import current_user, is_logged_in


def borrow_book(book_id):
    """
    Borrow a book if it is available. Marks it as not available and logs the loan.
    """
    if not is_logged_in():
        print("You must be logged in to borrow a book.")
        return

    conn = sqlite3.connect('library.db')
    c = conn.cursor()

    # Check if the book exists and is available
    c.execute("SELECT available FROM books WHERE id = ?", (book_id,))
    book = c.fetchone()
    if not book:
        print("Book not found.")
        conn.close()
        return
    if not book[0]:
        print("Book is currently not available.")
        conn.close()
        return

    # Mark the book as unavailable
    c.execute("UPDATE books SET available = ? WHERE id = ?", (False, book_id))

    # Add a loan entry
    c.execute(
        "INSERT INTO loans (user_id, book_id) VALUES (?, ?)",
        (current_user["id"], book_id)
    )

    conn.commit()
    conn.close()
    print("Book borrowed successfully.")


def return_book(book_id):
    """
    Return a borrowed book. Marks it as available and updates the return date.
    """
    if not is_logged_in():
        print("You must be logged in to return a book.")
        return

    conn = sqlite3.connect('library.db')
    c = conn.cursor()

    # Check if the current user has borrowed this book and not yet returned it
    c.execute(
        "SELECT id FROM loans WHERE user_id = ? AND book_id = ? AND return_date IS NULL",
        (current_user["id"], book_id)
    )
    loan = c.fetchone()
    if not loan:
        print("You have not borrowed this book or already returned it.")
        conn.close()
        return

    # Mark the book as available
    c.execute("UPDATE books SET available = ? WHERE id = ?", (True, book_id))

    # Update the return date
    c.execute(
        "UPDATE loans SET return_date = CURRENT_TIMESTAMP WHERE id = ?",
        (loan[0],)
    )

    conn.commit()
    conn.close()
    print("Book returned successfully.")
