import sqlite3
import bcrypt
import utils


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
    c.execute(
        "SELECT id, username, password, role FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()

    if result:
        user_id, user_name, hashed_password, role = result
        # Check password
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
            utils.set_current_user({"id": user_id,
                                    "username": user_name, "role": role})
            print(f"Welcome, {username}! (Role: {role})")
            return
    print("Invalid username or password.")


def logout_user():
    """
    Logs out the current user.
    """
    current_user = utils.get_current_user()
    if current_user:
        print(f"Logged out: {current_user['username']}")
        current_user = None
    else:
        print("No logged in user.")


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
