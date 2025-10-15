import utils
import validation as v
import database as db
import logger
import sqlite3


def add_book(title, author, year, quantity=1, genre=None, isbn=None):
    """
    Creates a new book entry in the database
    If the book already exists (same title, author, year, and isbn), increase its quantity.
    """
    try:
        if not utils.is_logged_in():
            print("You must be logged in to add a book.")
            logger.log_warning("Add book attempt without being logged in.")
            return

        current_user = utils.get_current_user()
        if current_user["role"] != "admin":
            print("Access denied: only admins can add books.")
            logger.log_warning(
                f"Unauthorized add book attempt by non-admin user: {current_user['username']}")
            return

        # Validate inputs

        v.validate_book_data(title, author, year, quantity, genre, isbn)

        conn = db.get_connection()
        c = conn.cursor()

        normalized_isbn = v.normalize_isbn(isbn)

        # Check if ISBN already exists, if it does, increase quantity
        if normalized_isbn:
            c.execute("SELECT id FROM books WHERE isbn = ?",
                      (normalized_isbn,))
            existing_isbn = c.fetchone()
            if existing_isbn:
                c.execute("UPDATE books SET quantity = quantity + ? WHERE id = ?",
                          (int(quantity), existing_isbn[0]))
                conn.commit()
                conn.close()
                logger.log_info(
                    f"Updated quantity of existing book (ISBN: {isbn}) by {quantity}.")
                print(f"Added {quantity} more copies of '{title}'.")
        else:
            # Insert new book entry
            c.execute(
                "INSERT INTO books (title, author, year, quantity, genre, isbn) VALUES (?, ?, ?, ?, ?, ?)",
                (title, author, year, quantity, genre, isbn)
            )
            print(f"Added new book '{title}' to the database.")
            logger.log_info(f"New book added: '{title}' by {author} ({year})")
            conn.commit()
        conn.close()

    except ValueError as e:
        print(f"Error adding book: {e}")
        logger.log_warning(f"Validation error while adding book: {e}")
    except sqlite3.IntegrityError as e:
        print("Database integrity error while adding book.")
        logger.log_error(f"Integrity error while adding book: {e}")
    except Exception as e:
        print("An unexpected error occurred while adding a book.")
        logger.log_exception(f"Unexpected error in add_book: {e}")


def display_books(only_available=False):
    """
    Display all books from the 'books' table in the database.
    If only_available is True, show only books with quantity > 0.
    """
    try:
        conn = db.get_connection()
        c = conn.cursor()

        # Build the SQL query based on the availability filter
        if only_available:
            c.execute("SELECT * FROM books WHERE quantity > 0 ORDER BY title")
        else:
            c.execute("SELECT * FROM books ORDER BY title")

        books = c.fetchall()
        conn.close()

        # Display the books
        print("Books in the library:")
        for book in books:
            book_id, title, author, year, quantity, genre, isbn = book
            status = f"Quantity: {quantity}" if quantity > 0 else "Not available"
            print(
                f"{book_id}: {title} by {author}, {year} | Genre: {genre or '-'} | ISBN: {isbn or '-'} | {status}")

        logger.log_info(
            f"Displayed books list successfully (filter: only_available={only_available})")

    except Exception as e:
        print("An unexpected error occurred while displaying books.")
        logger.log_exception(f"Unexpected error in display_books: {e}")


def update_book(book_id, title=None, author=None, year=None, quantity=None, genre=None, isbn=None):
    """
    Update the book with the given ID.
    You can change the title, author, year, quantity, genre and ISBN.
    """
    try:
        if not utils.is_logged_in() or utils.get_current_user()["role"] != "admin":
            print("Access denied: only admins can update books.")
            logger.log_warning("Update book attempt without admin rights.")
            return

        if not db.book_exists(book_id):
            print("Book not found.")
            logger.log_warning(f"Update failed: book ID {book_id} not found.")
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
            logger.log_info(f"Book ID {book_id} updated successfully.")

        conn.close()

    except ValueError as e:
        print(f"Validation error while updating book: {e}")
        logger.log_warning(f"Validation error while updating book: {e}")
    except Exception as e:
        print("An unexpected error occurred while updating the book.")
        logger.log_exception(f"Unexpected error in update_book: {e}")


def delete_book(book_id):
    """
    Delete a book from the 'books' table by its ID.
    """
    try:
        if not utils.is_logged_in() or utils.get_current_user()["role"] != "admin":
            print("Access denied: only admins can delete books.")
            logger.log_warning("Delete book attempt without admin rights.")
            return

        if not db.book_exists(book_id):
            print("Book not found.")
            logger.log_warning(f"Delete failed: book ID {book_id} not found.")
            return

        conn = db.get_connection()
        c = conn.cursor()

        c.execute("DELETE FROM books WHERE id = ?", (book_id,))

        conn.commit()
        conn.close()

        print(f"Book ID {book_id} deleted.")
        logger.log_info(f"Book ID {book_id} deleted successfully.")

    except Exception as e:
        print("An unexpected error occurred while deleting the book.")
        logger.log_exception(f"Unexpected error in delete_book: {e}")


def search_books(query, only_available=False, genre_filter=None):
    """
    Search for books by title or author or genre.
    Optionally filter by availability and genre. 
    """
    try:
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
        conn.close()

        # Display results
        if results:
            print("Found books:")
            for book in results:
                book_id, title, author, year, quantity, genre, isbn = book
                status = f"Quantity: {quantity}" if quantity > 0 else "Not available"
                print(
                    f"{book_id}: {title} by {author}, {year} | Genre: {genre or '-'} | ISBN: {isbn or '-'} | {status}")
            logger.log_info(
                f"Search completed: query='{query}', only_available={only_available}, genre_filter='{genre_filter}' ({len(results)} results)")
        else:
            print("No books found.")
            logger.log_info(
                f"Search completed: query='{query}', only_available={only_available}, genre_filter='{genre_filter}' (no results found)")

    except Exception as e:
        print("An unexpected error occurred while searching for books.")
        logger.log_exception(f"Unexpected error in search_books: {e}")
