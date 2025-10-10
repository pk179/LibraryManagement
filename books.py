import utils
import validation as v
import database as db


def add_book(title, author, year, quantity=1, genre=None, isbn=None):
    """
    Creates a new book entry in the database
    If the book already exists (same title, author, year, and isbn), increase its quantity.
    """
    if not utils.is_logged_in():
        print("You must be logged in to add a book.")
        return

    current_user = utils.get_current_user()
    if current_user["role"] != "admin":
        print("Access denied: only admins can add books.")
        return

    # Validate inputs
    try:
        v.validate_book_data(title, author, year, quantity, genre, isbn)
    except ValueError as e:
        print(f"Error adding book: {e}")
        return

    conn = db.get_connection()
    c = conn.cursor()

    # Check if the book already exists
    c.execute(
        "SELECT id, quantity FROM books WHERE title = ? AND author = ? AND year = ? AND (isbn = ? OR isbn IS NULL)",
        (title, author, year, isbn)
    )
    existing = c.fetchone()

    # If it exists, update the quantity; otherwise, insert a new record
    if existing:
        book_id, current_quantity = existing
        c.execute(
            "UPDATE books SET quantity = ? WHERE id = ?",
            (current_quantity + int(quantity), book_id)
        )
        print(
            f"Updated quantity of '{title}' to {current_quantity + int(quantity)}.")
    else:
        c.execute(
            "INSERT INTO books (title, author, year, quantity, genre, isbn) VALUES (?, ?, ?, ?, ?, ?)",
            (title, author, year, quantity, genre, isbn)
        )
        print(f"Added new book '{title}' to the database.")

    conn.commit()
    conn.close()


def display_books(only_available=False):
    """
    Display all books from the 'books' table in the database.
    If only_available is True, show only books with quantity > 0.
    """
    conn = db.get_connection()
    c = conn.cursor()

    # Build the SQL query based on the availability filter
    if only_available:
        c.execute("SELECT * FROM books WHERE quantity > 0 ORDER BY title")
    else:
        c.execute("SELECT * FROM books ORDER BY title")

    books = c.fetchall()

    # Display the books
    print("Books in the library:")
    for book in books:
        book_id, title, author, year, quantity, genre, isbn = book
        status = f"Quantity: {quantity}" if quantity > 0 else "Not available"
        print(f"{book_id}: {title} by {author}, {year} | Genre: {genre or '-'} | ISBN: {isbn or '-'} | {status}")

    conn.close()


def update_book(book_id, title=None, author=None, year=None, quantity=None, genre=None, isbn=None):
    """
    Update the book with the given ID.
    You can change the title, author, year, quantity, genre and ISBN.
    """
    if not utils.is_logged_in() or utils.get_current_user()["role"] != "admin":
        print("Access denied: only admins can update books.")
        return

    if not db.book_exists(book_id):
        print("Book not found.")
        return

    conn = db.get_connection()
    c = conn.cursor()

    # Prepare list of fields to update
    fields = []
    values = []

    if title is not None:
        v.validate_non_empty_string("Title", title)
        fields.append("title = ?")
        values.append(title)
    if author is not None:
        v.validate_non_empty_string("Author", author)
        fields.append("author = ?")
        values.append(author)
    if year is not None:
        v.validate_year(year)
        fields.append("year = ?")
        values.append(year)
    if quantity is not None:
        v.validate_quantity(quantity)
        fields.append("quantity = ?")
        values.append(quantity)
    if genre is not None:
        v.validate_genre(genre)
        fields.append("genre = ?")
        values.append(genre)
    if isbn is not None:
        v.validate_isbn_optional(isbn)
        fields.append("isbn = ?")
        values.append(isbn)

    # Execute update if there are any fields to update
    if fields:
        sql = f"UPDATE books SET {', '.join(fields)} WHERE id = ?"
        values.append(book_id)
        c.execute(sql, values)
        conn.commit()
        print(f"Book ID {book_id} updated.")

    conn.close()


def delete_book(book_id):
    """
    Delete a book from the 'books' table by its ID.
    """
    if not utils.is_logged_in() or utils.get_current_user()["role"] != "admin":
        print("Access denied: only admins can delete books.")
        return

    if not db.book_exists(book_id):
        print("Book not found.")
        return

    conn = db.get_connection()
    c = conn.cursor()

    c.execute("DELETE FROM books WHERE id = ?", (book_id,))

    conn.commit()
    conn.close()
    print(f"Book ID {book_id} deleted.")


def search_books(query, only_available=False, genre_filter=None):
    """
    Search for books by title or author or genre.
    Optionally filter by availability and genre. 
    """
    conn = db.get_connection()
    c = conn.cursor()

    # Build the SQL query dynamically based on filters
    sql = "SELECT * FROM books WHERE (LOWER(title) LIKE LOWER(?) OR LOWER(author) LIKE LOWER(?))"
    params = [f"%{query}%", f"%{query}%"]

    if genre_filter:
        sql += " AND LOWER(genre) = LOWER(?)"
        params.append(genre_filter)

    if only_available:
        sql += " AND quantity > 0"

    c.execute(sql, params)
    results = c.fetchall()

    # Display results
    if results:
        print("Found books:")
        for book in results:
            book_id, title, author, year, quantity, genre, isbn = book
            status = f"Quantity: {quantity}" if quantity > 0 else "Not available"
            print(
                f"{book_id}: {title} by {author}, {year} | Genre: {genre or '-'} | ISBN: {isbn or '-'} | {status}")
    else:
        print("No books found.")

    conn.close()
