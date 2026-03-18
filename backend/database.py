import sqlite3
from datetime import datetime
from typing import List
import bcrypt
from loans import FINE_PER_DAY, MAX_FINE

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


def seed_db():
    """Inserts initial data into the database."""
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()

        # Create a default admin and user account
        # Demo passwords - public for testing
        for username, password, role in [
            ("admin", "Admin123", "admin"),
            ("user", "User12345", "user"),
        ]:
            hashed_password = bcrypt.hashpw(
                password.encode("utf-8"),
                bcrypt.gensalt()
            )
            try:
                c.execute(
                    "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                    (username, hashed_password, role),
                )
            except sqlite3.IntegrityError:
                pass

        sample_books = [
            ("The Great Gatsby", "F. Scott Fitzgerald",
             1925, 5, "Fiction", "978-0-7432-7356-5"),
            ("To Kill a Mockingbird", "Harper Lee",
             1960, 3, "Fiction", "978-0-06-112008-4"),
            ("1984", "George Orwell", 1949, 4, "Dystopian", "978-0-452-28423-4"),
            ("Pride and Prejudice", "Jane Austen",
             1813, 2, "Romance", "978-0-14-143951-8"),
            ("The Catcher in the Rye", "J.D. Salinger",
             1951, 0, "Fiction", "978-0-316-76948-0"),
            ("Harry Potter and the Sorcerer's Stone", "J.K. Rowling",
             1997, 6, "Fantasy", "978-0-590-35340-3"),
            ("The Lord of the Rings", "J.R.R. Tolkien",
             1954, 2, "Fantasy", "978-0-547-92822-7"),
            ("Dune", "Frank Herbert", 1965, 4,
             "Science Fiction", "978-0-441-17271-9"),
            ("The Hitchhiker's Guide to the Galaxy", "Douglas Adams",
             1979, 5, "Science Fiction", "978-0-345-39180-3"),
            ("Brave New World", "Aldous Huxley", 1932,
             3, "Dystopian", "978-0-06-085052-4"),
            ("The Hobbit", "J.R.R. Tolkien", 1937,
             7, "Fantasy", "978-0-618-00221-3"),
            ("Fahrenheit 451", "Ray Bradbury", 1953,
             5, "Dystopian", "978-1-4516-7331-9"),
            ("Moby-Dick", "Herman Melville", 1851,
             0, "Adventure", "978-0-14-243724-7"),
            ("War and Peace", "Leo Tolstoy", 1869,
             3, "Historical", "978-0-14-303999-0"),
            ("Crime and Punishment", "Fyodor Dostoevsky",
             1866, 4, "Psychological", "978-0-14-305814-4"),
            ("The Alchemist", "Paulo Coelho", 1988,
             10, "Fiction", "978-0-06-112241-5"),
            ("The Little Prince", "Antoine de Saint-Exupéry",
             1943, 6, "Fable", "978-0-15-601219-5"),
            ("The Da Vinci Code", "Dan Brown", 2003,
             8, "Thriller", "978-0-307-47427-8"),
            ("The Girl with the Dragon Tattoo", "Stieg Larsson",
             2005, 0, "Crime", "978-0-307-45454-6"),
            ("The Hunger Games", "Suzanne Collins",
             2008, 9, "Dystopian", "978-0-439-02348-1"),
            ("The Odyssey", "Homer", -800, 4, "Epic", "978-0-140-26886-7"),
            ("The Shining", "Stephen King", 1977,
             3, "Horror", "978-0-307-74165-7"),
            ("Dracula", "Bram Stoker", 1897, 2, "Horror", "978-0-14-143984-6"),
            ("Frankenstein", "Mary Shelley", 1818,
             0, "Gothic", "978-0-14-143947-1"),
            ("The Chronicles of Narnia", "C.S. Lewis",
             1956, 6, "Fantasy", "978-0-06-623850-0"),
            ("Animal Farm", "George Orwell", 1945, 7,
             "Political Satire", "978-0-452-28424-1"),
            ("The Kite Runner", "Khaled Hosseini",
             2003, 5, "Drama", "978-1-59463-193-1"),
            ("Life of Pi", "Yann Martel", 2001,
             4, "Adventure", "978-0-15-602732-8"),
            ("The Road", "Cormac McCarthy", 2006, 2,
             "Post-Apocalyptic", "978-0-307-38789-9"),
            ("Gone Girl", "Gillian Flynn", 2012,
             6, "Thriller", "978-0-307-58837-1"),
        ]

        for title, author, year, quantity, genre, isbn in sample_books:
            try:
                c.execute("""
                    INSERT INTO books (title, author, year, quantity, genre, isbn)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (title, author, year, quantity, genre, isbn))
            except sqlite3.IntegrityError:
                pass

        sample_loans = [
            (2, 1, "2026-01-02T10:00:00",
             "2026-01-22T10:00:00", "2026-02-01T10:00:00"),
            (2, 3, "2026-02-05T14:30:00", None, "2026-03-04T14:30:00"),
            (2, 5, "2026-03-10T09:00:00", None, "2026-04-09T09:00:00"),
        ]

        for user_id, book_id, borrow_date, return_date, due_date in sample_loans:
            try:
                c.execute("""
                    INSERT INTO loans (user_id, book_id, borrow_date, return_date, due_date)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, book_id, borrow_date, return_date, due_date))
                c.execute(
                    "UPDATE books SET quantity = quantity - 1 WHERE id = ?", (book_id,))
            except sqlite3.IntegrityError:
                pass

        conn.commit()


def reset_db():
    """Clears all data from tables and reseeds with initial data."""
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()

        c.execute("DELETE FROM loans")
        c.execute("DELETE FROM books")
        c.execute("DELETE FROM users")

        conn.commit()

    seed_db()


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
        return c.rowcount


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

        c.execute("""
            SELECT loans.id, loans.user_id, loans.book_id,
                books.title, books.author,
                loans.borrow_date, loans.return_date,
                loans.due_date, loans.fine
            FROM loans
            JOIN books ON books.id = loans.book_id
            WHERE loans.id = ?
        """, (loan_id,))
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

        c.execute("""
            SELECT loans.id, loans.user_id, loans.book_id,
                books.title, books.author,
                loans.borrow_date, loans.return_date,
                loans.due_date, loans.fine
            FROM loans
            JOIN books ON books.id = loans.book_id
            WHERE loans.id = ?
        """, (loan_id,))
        return dict(c.fetchone())


def calculate_fine(due_date):
    """Calculates fine based on due date."""
    now = datetime.now()
    due = datetime.fromisoformat(due_date)

    if now <= due:
        return 0

    days_overdue = (now - due).days
    fine = days_overdue * FINE_PER_DAY
    return min(fine, MAX_FINE)


def get_loans_by_user(user_id):
    """Returns user's active loans."""
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("""
            SELECT loans.id, loans.user_id, loans.book_id, books.title, books.author,
                   loans.borrow_date, loans.return_date, loans.due_date, loans.fine
            FROM loans
            JOIN books ON books.id = loans.book_id
            WHERE loans.user_id = ? AND loans.return_date IS NULL
            ORDER BY loans.id DESC
        """, (user_id,))

        loans = []
        rows = c.fetchall()

        for row in rows:
            loan = dict(row)
            if not loan["return_date"]:
                new_fine = calculate_fine(loan["due_date"])
                c.execute(
                    "UPDATE loans SET fine = ? WHERE id = ?",
                    (new_fine, loan["id"]))
                loan["fine"] = new_fine
            loans.append(loan)

        return loans


def get_returned_loans_by_user(user_id):
    """Returns user's returned loans."""
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("""
            SELECT loans.id, loans.user_id, loans.book_id, books.title, books.author,
                   loans.borrow_date, loans.return_date, loans.due_date, loans.fine
            FROM loans
            JOIN books ON books.id = loans.book_id
            WHERE loans.user_id = ? AND loans.return_date IS NOT NULL
            ORDER BY loans.id DESC
        """, (user_id,))
        return [dict(row) for row in c.fetchall()]


def get_overdue_loans_by_user(user_id):
    """Returns user's overdue loans."""
    now = datetime.now().isoformat()

    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("""
            SELECT loans.id, loans.user_id, loans.book_id, books.title, books.author,
                   loans.borrow_date, loans.return_date, loans.due_date, loans.fine
            FROM loans
            JOIN books ON books.id = loans.book_id
            WHERE loans.user_id = ? AND loans.return_date IS NULL
              AND loans.due_date < ?
            ORDER BY loans.id DESC
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
        loans = []
        rows = c.fetchall()

        for row in rows:
            loan = dict(row)
            if not loan["return_date"]:
                new_fine = calculate_fine(loan["due_date"])
                c.execute(
                    "UPDATE loans SET fine = ? WHERE id = ?",
                    (new_fine, loan["id"]))
                loan["fine"] = new_fine
            loans.append(loan)

        return loans


def get_all_overdue_loans():
    """Returns all overdue loans."""
    now = datetime.now().isoformat()

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
            WHERE loans.return_date IS NULL AND loans.due_date < ?
            ORDER BY loans.id DESC
        """, (now,))
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


def count_overdue_loans():
    """Returns number of overdue loans."""
    now = datetime.now().isoformat()

    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute(
            "SELECT COUNT(*) FROM loans WHERE return_date IS NULL AND due_date < ?", (now,))
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
