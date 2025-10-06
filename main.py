import sqlite3

import bcrypt


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

    # Create the 'users' table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT DEFAULT 'user'
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


def register_user(username, password, role='user'):
    """
    Registers a new user in the database if the username is not already taken.
    User has a role of 'user' by default and a hashed password.
    """
    conn = sqlite3.connect('library.db')
    c = conn.cursor()

    # Check if the username already exists
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    if c.fetchone():
        print("This username is already taken.")
        conn.close()
        return False

    # Hash the password before storing it
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Add the new user
    c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
              (username, hashed_password, role))
    conn.commit()
    conn.close()
    print(f"User '{username}' registered successfully as'{role}'.")
    return True


def login_user(username, password):
    """
    Logs in the user if the credentials are correct.
    """
    conn = sqlite3.connect('library.db')
    c = conn.cursor()

    # Get user by username
    c.execute("SELECT password, role FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()

    if result:
        hashed_password, role = result
        # Check password
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
            print(f"Welcome, {username}! (Role: {role})")
            return {'username': username, 'role': role}
    print("Invalid username or password.")
    return None


if __name__ == "__main__":
    init_db()
    register_user("admin", "password123", "admin")
    register_user("admin", "password123", "admin")
    register_user("user", "mypassword")

    print("\nLogin tests:")
    login_user("admin", "password123")
    login_user("admin", "wrongpass")
