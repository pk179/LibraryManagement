import sqlite3

import bcrypt

current_user = None  # Global variable to track the logged-in user


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
    global current_user
    conn = sqlite3.connect('library.db')
    c = conn.cursor()

    # Get user by username
    c.execute(
        "SELECT id, username, password, role FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()

    if result:
        user_id, user_name, hashed_password, role = result
        # Check password
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
            current_user = {"id": user_id, "username": user_name, "role": role}
            print(f"Welcome, {username}! (Role: {role})")
            return
    print("Invalid username or password.")


def logout_user():
    """
    Logs out the current user.
    """
    global current_user
    if current_user:
        print(f"Logged out: {current_user['username']}")
        current_user = None
    else:
        print("No logged in user.")


def is_logged_in():
    """
    Checks if a user is currently logged in."""
    return current_user is not None


def delete_user(admin_username, target_username):
    """
    Deletes another user if the requesting user has an admin role.
    """
    conn = sqlite3.connect('library.db')
    c = conn.cursor()

    # Check if the requester is admin
    c.execute("SELECT role FROM users WHERE username = ?", (admin_username,))
    result = c.fetchone()

    if not result or result[0] != 'admin':
        print("Access denied. Only admins can delete users.")
        conn.close()
        return False

    # Delete target user
    c.execute("DELETE FROM users WHERE username = ?", (target_username,))
    conn.commit()
    conn.close()

    print(f"User '{target_username}' deleted successfully.")
    return True


def display_users():
    """
    Display all users if the current user has the 'admin' role.
    """
    global current_user
    if current_user is None:
        print("You must be logged in.")
        return

    if current_user["role"] != "admin":
        print("Access denied. Admins only.")
        return

    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute("SELECT id, username, role FROM users")
    users = c.fetchall()

    print("All users:")
    for user in users:
        print(f"ID: {user[0]} | Username: {user[1]} | Role: {user[2]}")

    conn.close()


if __name__ == "__main__":
    init_db()

    register_user("alice", "password123", role="user")
    register_user("admin2", "adminpass", role="admin")

    print("\nTest 1: User login and add book")
    login_user("alice", "password123")
    add_book("The Shining", "Stephen King", 1977)
    display_books()
    logout_user()

    print("\nTest 2: Admin updates a book")
    login_user("admin2", "adminpass")
    update_book(4, available=False)
    display_books()
    logout_user()

    print("\nTest 3: Admin deletes a book")
    login_user("admin2", "adminpass")
    delete_book(4)
    display_books()
    display_users()
    logout_user()

    print("\nTest 4: Access denied scenarios")
    login_user("alice", "password123")
    update_book(5, title="New Title")
    delete_book(5)
    display_users()
    logout_user()
