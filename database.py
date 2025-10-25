import sqlite3

DB_NAME = "library.db"


def init_db():
    """
    Creates the database and the 'books' table if they do not exist
    """
    # Connect to the SQLite database
    conn = sqlite3.connect('library.db')
    c = conn.cursor()

    # Create the 'books' table
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

    # Create the 'users' table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    ''')

    # Create the 'loans' table to track book loans
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

    # Commit changes and close the connection
    conn.commit()
    conn.close()


def get_connection():
    """Returns a new connection to the database."""
    return sqlite3.connect(DB_NAME)


def user_exists(username):
    """Checks if a user with the given username exists."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT 1 FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    return result is not None


def get_user_by_id(user_id):
    """Fetches user record by username."""
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT id, username, password, role FROM users WHERE id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result  # Returns tuple or None


def get_user_by_username(username):
    """Fetches user record by username."""
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT id, username, password, role FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    return result  # Returns tuple or None


def book_exists(book_id):
    """Checks if a book with the given ID exists."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT 1 FROM books WHERE id = ?", (book_id,))
    result = c.fetchone()
    conn.close()
    return result is not None


def get_book_by_id(book_id):
    """Returns the full book record by ID."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM books WHERE id = ?", (book_id,))
    result = c.fetchone()
    conn.close()
    return result  # Returns tuple or None


def get_book_quantity(book_id):
    """Returns the number of available copies for a given book."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT quantity FROM books WHERE id = ?", (book_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else 0


def decrease_book_quantity(book_id):
    """Decreases quantity by 1 (when borrowed), if possible."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT quantity FROM books WHERE id = ?", (book_id,))
    result = c.fetchone()
    if result and result[0] > 0:
        c.execute(
            "UPDATE books SET quantity = quantity - 1 WHERE id = ?", (book_id,))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False


def increase_book_quantity(book_id):
    """Increases quantity by 1 (when returned)."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE books SET quantity = quantity + 1 WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()
