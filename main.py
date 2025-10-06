import sqlite3


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
            title TEXT,
            author TEXT,
            year INTEGER,
            available BOOLEAN
        )
    ''')

    # Commit changes and close the connection
    conn.commit()
    conn.close()


def add_book(title, author, year):
    """
    Creates a new book entry in the database
    """
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    # Check if the book already exists
    c.execute(
        "SELECT * FROM books WHERE title = ? AND author = ? AND year = ?",
        (title, author, year)
    )
    if not c.fetchone():
        # Add the new book
        c.execute(
            "INSERT INTO books (title, author, year, available) VALUES (?, ?, ?, ?)",
            (title, author, year, True)
        )
        conn.commit()
    conn.close()


def display_books():
    """
    Display all books from the 'books' table in the database.
    """
    conn = sqlite3.connect('library.db')
    c = conn.cursor()

    c.execute("SELECT * FROM books")
    books = c.fetchall()

    for book in books:
        # book = (id, title, author, year, available)
        status = "Available" if book[4] else "Not available"
        print(f"{book[1]} by {book[2]}, {book[3]} - {status}")

    conn.close()


if __name__ == "__main__":
    init_db()
    add_book("It", "Stephen King", 1986)
    add_book("1984", "George Orwell", 1949)

    print("Books in library:")
    display_books()
