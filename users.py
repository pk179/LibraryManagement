import sqlite3
import bcrypt
import utils
import validation as v
import database as db
import logger


def register_user(username, password, role='user'):
    """
    Registers a new user with validation.
    User has a role of 'user' by default and a hashed password.
    """
    # Validate inputs
    try:
        v.validate_user_registration(username, password, role)

        if db.user_exists(username):
            print("This username is already taken.")
            logger.log_warning(
                f"Registration failed: username '{username}' already exists.")
            return False

        conn = db.get_connection()
        c = conn.cursor()

        # Hash the password before storing it
        hashed_password = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt())

        # Add the new user
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                  (username, hashed_password, role))
        conn.commit()
        conn.close()
        print(f"User '{username}' registered successfully as '{role}'.")
        logger.log_info(f"New user registered: {username} (role={role})")
        return True

    except ValueError as e:
        print(f"Registration error: {e}")
        logger.log_warning(f"Validation error during registration: {e}")
        return False
    except sqlite3.IntegrityError as e:
        print("Database integrity error during registration.")
        logger.log_error(f"Database integrity error during registration: {e}")
        return False
    except Exception as e:
        print("An unexpected error occurred during registration.")
        logger.log_exception(f"Unexpected error during registration: {e}")
        return False


def login_user(username, password):
    """
    Logs in the user if the credentials are correct (with validation).
    """
    # Validate inputs
    try:
        v.validate_non_empty_string("Username", username)
        v.validate_non_empty_string("Password", password)

        user = db.get_user_by_username(username)
        if not user:
            print("Invalid username or password.")
            logger.log_warning(f"User '{username}' not found.")
            return False

        user_id, user_name, hashed_password, role = user
        # Check password
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
            utils.set_current_user({"id": user_id,
                                    "username": user_name, "role": role})
            print(f"Welcome, {username}! (Role: {role})")
            logger.log_info(f"User logged in successfully: {username}")
            return True

        print("Invalid username or password.")
        logger.log_warning(
            f"Failed login attempt for user: {username}: incorrect password.")
        return False

    except ValueError as e:
        print(f"Login error: {e}")
        logger.log_warning(f"Validation error during login: {e}")
        return False
    except Exception as e:
        print("An unexpected error occurred during login.")
        logger.log_exception(f"Unexpected error during login: {e}")
        return False


def logout_user():
    """
    Logs out the current user.
    """
    try:
        current_user = utils.get_current_user()
        if current_user:
            utils.set_current_user(None)
            print(f"Logged out: {current_user['username']}")
            logger.log_info(f"User logged out: {current_user['username']}")
        else:
            print("No logged in user.")
            logger.log_warning("Logout attempt with no user logged in.")
    except Exception as e:
        print("An unexpected error occurred during logout.")
        logger.log_exception(f"Unexpected error during logout: {e}")


def delete_user(admin_username, target_username):
    """
    Deletes another user if the requesting user has an admin role.
    """
    try:
        # Verify admin privileges
        user = db.get_user_by_username(admin_username)
        if not user or user[3] != 'admin':  # user[3] is the role
            print("Access denied. Only admins can delete users.")
            logger.log_warning(
                f"Unauthorized delete attempt by non-admin user: {admin_username}")
            return False

        if admin_username == target_username:
            print("Admin cannot delete their own account.")
            logger.log_warning(
                f"Admin '{admin_username}' attempted to delete their own account.")
            return False

        if not db.user_exists(target_username):
            print("User not found.")
            logger.log_warning(
                f"Delete failed: user '{target_username}' not found.")
            return False

        conn = db.get_connection()
        c = conn.cursor()

        # Delete target user
        c.execute("DELETE FROM users WHERE username = ?", (target_username,))
        conn.commit()
        conn.close()

        print(f"User '{target_username}' deleted successfully.")
        logger.log_info(
            f"User '{target_username}' deleted by admin '{admin_username}'.")
        return True

    except Exception as e:
        print("An unexpected error occurred during user deletion.")
        logger.log_exception(f"Unexpected error during user deletion: {e}")
        return False


def display_users():
    """
    Display all users if the current user has the 'admin' role.
    """
    try:
        current_user = utils.get_current_user()
        if not current_user:
            print("You must be logged in.")
            logger.log_warning("Display users attempt with no user logged in.")
            return

        if current_user["role"] != "admin":
            print("Access denied. Admins only.")
            logger.log_warning(
                f"Unauthorized display users attempt by non-admin user: {current_user['username']}")
            return

        conn = db.get_connection()
        c = conn.cursor()
        c.execute("SELECT id, username, role FROM users ORDER BY id")
        users = c.fetchall()
        conn.close()

        print("All users:")
        for user in users:
            print(f"ID: {user[0]} | Username: {user[1]} | Role: {user[2]}")
        logger.log_info(
            f"All users displayed by admin: {current_user['username']}")

    except Exception as e:
        print("An unexpected error occurred while displaying users.")
        logger.log_exception(f"Unexpected error while displaying users: {e}")
