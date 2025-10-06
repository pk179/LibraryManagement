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


def update_book(book_id, title=None, author=None, year=None, available=None):
    """
    Update the book with the given ID.
    You can change the title, author, year, and availability status.
    """
    conn = sqlite3.connect('library.db')
    c = conn.cursor()

    # Prepare list of fields to update
    fields = []
    values = []

    if title is not None:
        fields.append("title = ?")
        values.append(title)
    if author is not None:
        fields.append("author = ?")
        values.append(author)
    if year is not None:
        fields.append("year = ?")
        values.append(year)
    if available is not None:
        fields.append("available = ?")
        values.append(available)

    # Execute update if there are any fields to update
    if fields:
        sql = f"UPDATE books SET {', '.join(fields)} WHERE id = ?"
        values.append(book_id)
        c.execute(sql, values)
        conn.commit()

    conn.close()


def delete_book(book_id):
    """
    Delete a book from the 'books' table by its ID.
    """
    conn = sqlite3.connect('library.db')
    c = conn.cursor()

    c.execute("DELETE FROM books WHERE id = ?", (book_id,))

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    add_book("The Shining", "Stephen King", 1977)
    add_book("It", "Stephen King", 1986)
    add_book("1984", "George Orwell", 1949)

    print("Before deletion:")
    display_books()

    delete_book(3)

    print("\nAfter deletion:")
    display_books()
