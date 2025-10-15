import utils
from datetime import datetime, timedelta
import database as db
import validation as v
import logger
import sqlite3

MAX_BORROWS = 5
BORROW_DAYS = 14
FINE_PER_DAY = 1.0


def borrow_book(book_id):
    """
    Borrow a book if it is available. Decrease its quantity and add a loan entry.
    """
    try:
        if not utils.is_logged_in():
            print("You must be logged in to borrow a book.")
            logger.log_warning("Borrow book attempt without being logged in.")
            return

        if not db.book_exists(book_id):
            print("Book not found.")
            logger.log_warning(
                f"Borrow failed: book ID '{book_id}' not found.")
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
            logger.log_warning(
                f"Borrow failed: user '{current_user['username']}' has reached max borrows.")
            conn.close()
            return

        book = db.get_book_by_id(book_id)
        if not book or book[4] <= 0:  # book[4] is the quantity
            print("This book is currently unavailable.")
            logger.log_warning(
                f"Borrow failed: book ID '{book_id}' is unavailable.")
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
        logger.log_info(
            f"Book ID '{book_id}' borrowed by user '{current_user['username']}', due on {due_date}.")

    except sqlite3.IntegrityError as e:
        print("Database integrity error occurred while borrowing the book.")
        logger.log_error(f"Database integrity error in borrow_book: {e}")
    except Exception as e:
        print("An unexpected error occurred while borrowing the book.")
        logger.log_exception(f"Unexpected error in borrow_book: {e}")


def return_book(book_id):
    """
    Return a borrowed book. Increase its quantity and update the loan entry with the return date.
    """
    try:
        if not utils.is_logged_in():
            print("You must be logged in to return a book.")
            logger.log_warning("Return book attempt without being logged in.")
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
            logger.log_warning(
                f"Return failed: user '{current_user['username']}' has no active loan for book ID '{book_id}'.")
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
            logger.log_info(
                f"Book ID '{book_id}' returned {days_overdue} days late by user '{current_user['username']}', fine: ${fine:.2f}.")

        # Update the loan entry with the return date and fine, and increase book quantity
        c.execute(
            "UPDATE loans SET return_date = CURRENT_TIMESTAMP, fine = ? WHERE id = ?", (fine, loan_id))
        db.increase_book_quantity(book_id)

        conn.commit()
        conn.close()

        print("Book returned successfully.")
        logger.log_info(
            f"Book ID '{book_id}' successfully returned by user '{current_user['username']}' (fine={fine:.2f}).")

    except sqlite3.IntegrityError as e:
        print("Database integrity error occurred while returning the book.")
        logger.log_error(f"Database integrity error in return_book: {e}")
    except Exception as e:
        print("An unexpected error occurred while returning the book.")
        logger.log_exception(f"Unexpected error in return_book: {e}")


def show_active_loans():
    """
    Display active loans:
    - Regular users: see only their own loans.
    - Admins: see all active loans.
    """
    try:
        if not utils.is_logged_in():
            print("You must be logged in to view loans.")
            logger.log_warning(
                "Attempt to view loans without being logged in.")
            return

        user = utils.get_current_user()
        conn = db.get_connection()
        c = conn.cursor()

        if user["role"] == "admin":
            # Admin sees all loans
            c.execute("""
                SELECT u.username, b.title, b.author, l.due_date
                FROM loans l
                JOIN users u ON l.user_id = u.id
                JOIN books b ON l.book_id = b.id
                WHERE l.return_date IS NULL
                ORDER BY l.due_date ASC
            """)
            loans = c.fetchall()
            if loans:
                print("\nAll active loans:")
                for username, title, author, due_date in loans:
                    print(
                        f"- {title} by {author} (user: {username}, due: {due_date})")
            else:
                print("No active loans found.")
            logger.log_info(
                f"Admin '{user['username']}' viewed all active loans.")
        else:
            # Regular user sees their own loans
            c.execute("""
                SELECT b.title, b.author, l.due_date
                FROM loans l
                JOIN books b ON l.book_id = b.id
                WHERE l.user_id = ? AND l.return_date IS NULL
                ORDER BY l.due_date ASC
            """, (user["id"],))
            loans = c.fetchall()
            if loans:
                print("\nYour current loans:")
                for title, author, due_date in loans:
                    print(f"- {title} by {author} (due: {due_date})")
            else:
                print("You have no active loans.")
            logger.log_info(
                f"User '{user['username']}' viewed their active loans.")
        conn.close()

    except Exception as e:
        print("An unexpected error occurred while displaying loans.")
        logger.log_exception(
            f"Unexpected error while displaying loans: {e}")


def show_returned_loans():
    """
    Display returned loans:
    - Regular users: see their own returned loans.
    - Admins: see all returned loans.
    """
    try:
        if not utils.is_logged_in():
            print("You must be logged in to view returned loans.")
            logger.log_warning(
                "Attempt to view returned loans without being logged in.")
            return

        user = utils.get_current_user()
        conn = db.get_connection()
        c = conn.cursor()

        if user["role"] == "admin":
            # Admin sees all returned loans
            c.execute("""
                SELECT u.username, b.title, b.author, l.return_date, l.fine
                FROM loans l
                JOIN users u ON l.user_id = u.id
                JOIN books b ON l.book_id = b.id
                WHERE l.return_date IS NOT NULL
                ORDER BY l.return_date DESC
            """)
            loans = c.fetchall()
            if loans:
                print("\nAll returned loans:")
                for username, title, author, return_date, fine in loans:
                    fine_text = f", fine: ${fine:.2f}" if fine > 0 else ""
                    print(
                        f"- {title} by {author} (user: {username}, returned: {return_date}{fine_text})")
            else:
                print("No returned loans found.")
            logger.log_info(
                f"Admin '{user['username']}' viewed all returned loans.")
        else:
            # Regular user sees their own returned loans
            c.execute("""
                SELECT b.title, b.author, l.return_date, l.fine
                FROM loans l
                JOIN books b ON l.book_id = b.id
                WHERE l.user_id = ? AND l.return_date IS NOT NULL
                ORDER BY l.return_date DESC
            """, (user["id"],))
            loans = c.fetchall()
            if loans:
                print("\nYour returned loans:")
                for title, author, return_date, fine in loans:
                    fine_text = f", fine: ${fine:.2f}" if fine > 0 else ""
                    print(
                        f"- {title} by {author} (returned: {return_date}{fine_text})")
            else:
                print("You have no returned loans.")
            logger.log_info(
                f"User '{user['username']}' viewed their returned loans.")

        conn.close()

    except Exception as e:
        print("An unexpected error occurred while displaying returned loans.")
        logger.log_exception(
            f"Unexpected error while displaying returned loans: {e}")


def show_overdue_loans():
    """
    Display overdue loans:
    - Regular users: see their own overdue loans.
    - Admins: see all overdue loans in the system.
    """
    try:
        if not utils.is_logged_in():
            print("You must be logged in to view overdue loans.")
            logger.log_warning(
                "Attempt to view overdue loans without being logged in.")
            return

        user = utils.get_current_user()
        conn = db.get_connection()
        c = conn.cursor()

        if user["role"] == "admin":
            # Admin sees all overdue loans
            c.execute("""
                SELECT u.username, b.title, b.author, l.due_date, l.fine
                FROM loans l
                JOIN users u ON l.user_id = u.id
                JOIN books b ON l.book_id = b.id
                WHERE l.return_date IS NULL AND DATE(l.due_date) < DATE('now')
                ORDER BY l.due_date ASC
            """)
            loans = c.fetchall()

            if loans:
                print("\nAll overdue loans:")
                for username, title, author, due_date, fine in loans:
                    fine_text = f", current fine: ${fine:.2f}" if fine > 0 else ""
                    print(
                        f"- {title} by {author} (user: {username}, due: {due_date}{fine_text})")
            else:
                print("No overdue loans found.")
            logger.log_info(
                f"Admin '{user['username']}' viewed all overdue loans.")
        else:
            # Regular user sees their own overdue loans
            c.execute("""
                SELECT b.title, b.author, l.due_date, l.fine
                FROM loans l
                JOIN books b ON l.book_id = b.id
                WHERE l.user_id = ? AND l.return_date IS NULL AND DATE(l.due_date) < DATE('now')
                ORDER BY l.due_date ASC
            """, (user["id"],))
            loans = c.fetchall()

            if loans:
                print("\nYour overdue loans:")
                for title, author, due_date, fine in loans:
                    fine_text = f", current fine: ${fine:.2f}" if fine > 0 else ""
                    print(f"- {title} by {author} (due: {due_date}{fine_text})")
            else:
                print("You have no overdue loans.")
            logger.log_info(
                f"User '{user['username']}' viewed their overdue loans.")

        conn.close()

    except Exception as e:
        print("An unexpected error occurred while displaying overdue loans.")
        logger.log_exception(
            f"Unexpected error while displaying overdue loans: {e}")
