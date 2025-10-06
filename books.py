import sqlite3
from utils import current_user, is_logged_in


def add_book(title, author, year):
    """
    Creates a new book entry in the database
    """
    if not is_logged_in():
        print("You must be logged in to add a book.")
        return

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
    if not is_logged_in() or current_user["role"] != "admin":
        print("Access denied: only admins can update books.")
        return

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
    if not is_logged_in() or current_user["role"] != "admin":
        print("Access denied: only admins can delete books.")
        return

    conn = sqlite3.connect('library.db')
    c = conn.cursor()

    c.execute("DELETE FROM books WHERE id = ?", (book_id,))

    conn.commit()
    conn.close()


def search_books(query):
    """
    Search for books by title or author containing the query string.    
    """
    conn = sqlite3.connect('library.db')
    c = conn.cursor()

    # Execute search query for title or author
    c.execute("SELECT * FROM books WHERE LOWER(title) LIKE LOWER(?) OR LOWER(author) LIKE LOWER(?)",
              ('%' + query + '%', '%' + query + '%'))

    # Fetch all matching results
    results = c.fetchall()

    # Display results
    if results:
        print("Found books:")
        for book in results:
            # book = (id, title, author, year, available)
            print(
                f"{book[1]} by {book[2]}, {book[3]} - {'Available' if book[4] else 'Not available'}")
    else:
        print("No books found.")

    conn.close()
