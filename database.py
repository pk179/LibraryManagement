import sqlite3
from datetime import datetime
from typing import List

DB_NAME = "library.db"


def init_db():
    """Creates the database and tables if they do not exist."""
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()

        c.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                year INTEGER,
                quantity INTEGER DEFAULT 1,
                genre TEXT DEFAULT '',
                isbn TEXT UNIQUE
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'user'
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS loans (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                book_id INTEGER NOT NULL,
                borrow_date TEXT NOT NULL,
                return_date TEXT,
                due_date TEXT,
                fine REAL DEFAULT 0,
                FOREIGN KEY(user_id) REFERENCES users(id),
                FOREIGN KEY(book_id) REFERENCES books(id)
            )
        ''')


def get_connection():
    """Returns a new connection to the database."""
    return sqlite3.connect(DB_NAME)


def user_exists(username):
    """Checks if a user with the given username exists."""
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT 1 FROM users WHERE username = ?", (username,))
        row = c.fetchone()
        return row is not None


def get_user_by_id(user_id):
    """Returns user as dict."""
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute(
            "SELECT id, username, password, role FROM users WHERE id = ?", (user_id,))
        row = c.fetchone()
        return dict(row) if row else None


def get_user_by_username(username):
    """Returns user as dict."""
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute(
            "SELECT id, username, password, role FROM users WHERE username = ?", (username,))
        row = c.fetchone()
        return dict(row) if row else None


def get_all_users():
    """Returns list of users."""
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT id, username, role FROM users")
        return [dict(row) for row in c.fetchall()]


def delete_user(user_id):
    """Deletes user by ID."""
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM users WHERE id = ?", (user_id,))
        return c.rowcount > 0


def book_exists(book_id):
    """Checks if a book with the given ID exists."""
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT 1 FROM books WHERE id = ?", (book_id,))
        row = c.fetchone()
        return row is not None


def get_book_by_id(book_id):
    """Returns book as dict."""
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute(
            "SELECT id, title, author, year, quantity, genre, isbn FROM books WHERE id = ?", (book_id,))
        row = c.fetchone()
        return dict(row) if row else None


def get_book_quantity(book_id):
    """Returns available quantity for a given book."""
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT quantity FROM books WHERE id = ?", (book_id,))
        row = c.fetchone()
        return row["quantity"] if row else 0


def get_all_books(only_available=False):
    """Returns all books."""
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        if only_available:
            c.execute("SELECT * FROM books WHERE quantity > 0")
        else:
            c.execute("SELECT * FROM books")

        return [dict(row) for row in c.fetchall()]


def add_book_row(title, author, year, quantity=1, genre=None, isbn=None):
    """Inserts new book and returns inserted row."""
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        try:
            c.execute("""
                INSERT INTO books(title, author, year, quantity, genre, isbn)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (title, author, year, quantity, genre, isbn))
            book_id = c.lastrowid
            conn.commit()
        except sqlite3.IntegrityError:
            return None

    return get_book_by_id(book_id)


def update_book_row(book_id, **updates):
    """Updates fields of a book. Returns updated book or None."""
    if not updates:
        return get_book_by_id(book_id)

    fields = ", ".join([f"{k} = ?" for k in updates.keys()])
    values = list(updates.values()) + [book_id]

    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute(f"UPDATE books SET {fields} WHERE id = ?", values)
        if c.rowcount == 0:
            return None

    return get_book_by_id(book_id)


def delete_book(book_id):
    """Deletes book by ID."""
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM books WHERE id = ?", (book_id,))
        return c.rowcount > 0


def delete_books(ids: List[int]):
    """
    Deletes multiple books by IDs using single SQL query.
    """
    if not ids:
        return []

    placeholders = ",".join("?" for _ in ids)
    query = f"DELETE FROM books WHERE id IN ({placeholders})"

    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute(query, ids)


def decrease_book_quantity(book_id):
    """Decreases book quantity by 1."""
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT quantity FROM books WHERE id = ?", (book_id,))
        row = c.fetchone()
        if not row or row[0] < 1:
            return False

        c.execute(
            "UPDATE books SET quantity = quantity - 1 WHERE id = ?", (book_id,))
        return True


def increase_book_quantity(book_id):
    """Increases book quantity by 1."""
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute(
            "UPDATE books SET quantity = quantity + 1 WHERE id = ?", (book_id,))
        return True


def insert_loan(user_id, book_id, due_date):
    """Creates a new loan record."""
    borrow_date = datetime.now().isoformat()

    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        try:
            c.execute("""
                INSERT INTO loans(user_id, book_id, borrow_date, due_date)
                VALUES (?, ?, ?, ?)
            """, (user_id, book_id, borrow_date, due_date))
            loan_id = c.lastrowid
        except sqlite3.IntegrityError:
            return None

        c.execute("SELECT * FROM loans WHERE id = ?", (loan_id,))
        row = c.fetchone()
        return dict(row)


def close_loan(loan_id, fine=0):
    """Marks loan as returned and updates fine."""
    return_date = datetime.now().isoformat()

    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("""
            UPDATE loans
            SET return_date = ?, fine = ?
            WHERE id = ? AND return_date IS NULL
        """, (return_date, fine, loan_id))

        if c.rowcount == 0:
            return None

        c.execute("SELECT * FROM loans WHERE id = ?", (loan_id,))
        return dict(c.fetchone())


def get_loans_by_user(user_id):
    """Returns user's active loans."""
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("""
            SELECT loans.id, loans.book_id, books.title, books.author,
                   loans.borrow_date, loans.due_date, loans.fine
            FROM loans
            JOIN books ON books.id = loans.book_id
            WHERE loans.user_id = ? AND loans.return_date IS NULL
        """, (user_id,))
        return [dict(row) for row in c.fetchall()]


def get_returned_loans_by_user(user_id):
    """Returns user's returned loans."""
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("""
            SELECT loans.id, loans.book_id, books.title, books.author,
                   loans.borrow_date, loans.due_date, loans.return_date, loans.fine
            FROM loans
            JOIN books ON books.id = loans.book_id
            WHERE loans.user_id = ? AND loans.return_date IS NOT NULL
        """, (user_id,))
        return [dict(row) for row in c.fetchall()]


def get_overdue_loans_by_user(user_id):
    """Returns user's overdue loans."""
    now = datetime.now().isoformat()

    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("""
            SELECT loans.id, loans.book_id, books.title, books.author,
                   loans.borrow_date, loans.due_date, loans.fine
            FROM loans
            JOIN books ON books.id = loans.book_id
            WHERE loans.user_id = ? AND loans.return_date IS NULL
              AND loans.due_date < ?
        """, (user_id, now))
        return [dict(row) for row in c.fetchall()]


def get_all_loans():
    """Returns all loans."""
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("""
            SELECT loans.id, loans.user_id, users.username,
                   loans.book_id, books.title, books.author,
                   loans.borrow_date, loans.due_date, loans.return_date, loans.fine
            FROM loans
            JOIN books ON books.id = loans.book_id
            JOIN users ON users.id = loans.user_id
            ORDER BY loans.id DESC
        """)
        return [dict(row) for row in c.fetchall()]


def count_all_loans():
    """Returns total number of loans."""
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM loans")
        return c.fetchone()[0]


def count_active_loans():
    """Returns number of active (not returned) loans."""
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM loans WHERE return_date IS NULL")
        return c.fetchone()[0]


def count_returned_loans():
    """Returns number of returned loans."""
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM loans WHERE return_date IS NOT NULL")
        return c.fetchone()[0]


def search_books(query, only_available=False, genre_filter=None):
    """
    Search books by title or author.
    Optionally filter by availability and genre.
    """
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        sql = """
            SELECT id, title, author, year, quantity, genre, isbn
            FROM books
            WHERE (LOWER(title) LIKE LOWER(?) OR LOWER(author) LIKE LOWER(?))
        """
        params = [f"%{query}%", f"%{query}%"]

        if genre_filter:
            sql += " AND LOWER(genre) = LOWER(?)"
            params.append(genre_filter)

        if only_available:
            sql += " AND quantity > 0"

        sql += " ORDER BY title"

        c.execute(sql, params)
        return [dict(row) for row in c.fetchall()]
