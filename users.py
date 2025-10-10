import sqlite3
import bcrypt
import utils
import validation as v
import database as db


def register_user(username, password, role='user'):
    """
    Registers a new user with validation.
    User has a role of 'user' by default and a hashed password.
    """
    # Validate inputs
    try:
        v.validate_user_registration(username, password, role)
    except ValueError as e:
        print(f"Registration error: {e}")
        return False

    if db.user_exists(username):
        print("This username is already taken.")
        return False

    conn = db.get_connection()
    c = conn.cursor()

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
    Logs in the user if the credentials are correct (with validation).
    """
    # Validate inputs
    try:
        v.validate_non_empty_string("Username", username)
        v.validate_non_empty_string("Password", password)
    except ValueError as e:
        print(f"Login error: {e}")
        return False

    user = db.get_user_by_username(username)
    if not user:
        print("Invalid username or password.")
        return False

    user_id, user_name, hashed_password, role = user
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
        utils.set_current_user(None)
    else:
        print("No logged in user.")


def delete_user(admin_username, target_username):
    """
    Deletes another user if the requesting user has an admin role.
    """
    # Verify admin privileges
    user = db.get_user_by_username(admin_username)
    if not user or user[3] != 'admin':  # user[3] is the role
        print("Access denied. Only admins can delete users.")
        return False

    if admin_username == target_username:
        print("Admin cannot delete their own account.")
        return False

    if not db.user_exists(target_username):
        print("User not found.")
        return False

    conn = db.get_connection()
    c = conn.cursor()

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
    current_user = utils.get_current_user()
    if not current_user:
        print("You must be logged in.")
        return

    if current_user["role"] != "admin":
        print("Access denied. Admins only.")
        return

    conn = db.get_connection()
    c = conn.cursor()
    c.execute("SELECT id, username, role FROM users ORDER BY id")
    users = c.fetchall()

    print("All users:")
    for user in users:
        print(f"ID: {user[0]} | Username: {user[1]} | Role: {user[2]}")

    conn.close()
