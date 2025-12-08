import sqlite3
import bcrypt
import validation as v
import database as db
import logger


def register_user(username: str, password: str, role: str = "user") -> bool:
    """
    Registers a new user with validation.
    User has a role of 'user' by default and a hashed password.
    """

    # Validate inputs
    v.validate_user_registration(username, password, role)

    if db.user_exists(username):
        logger.log_warning(
            f"Registration failed: username '{username}' already exists."
        )
        raise ValueError("Username already exists")

    # Hash the password before storing it
    hashed_password = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    )

    # Add the new user
    try:
        with db.get_connection() as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (username, hashed_password, role)
            )

        logger.log_info(f"New user registered: {username} (role={role})")
        return True

    except sqlite3.IntegrityError as e:
        logger.log_error(f"Database integrity error during registration: {e}")
        raise ValueError("Database integrity error")


def authenticate_user(username: str, password: str):
    """
    Verifies user credentials.
    """

    user = db.get_user_by_username(username)

    if not user:
        return None

    hashed_password = user["password"]

    if bcrypt.checkpw(password.encode("utf-8"), hashed_password):
        return {
            "id": user["id"],
            "username": user["username"],
            "role": user["role"],
        }

    return None


def delete_user_by_id(user_id: int, admin_user: dict | None = None) -> bool:
    """
    Deletes a user by ID if the requesting user has admin privileges.
    """

    # Verify admin privileges
    if not admin_user or admin_user.get("role") != "admin":
        logger.log_warning("Unauthorized delete_user_by_id attempt.")
        raise ValueError("Admin privileges required")

    if admin_user["id"] == user_id:
        raise ValueError("Admin cannot delete their own account")

    # Delete target user
    success = db.delete_user(user_id)

    if not success:
        return False

    logger.log_info(
        f"User {user_id} deleted by admin {admin_user['username']}"
    )
    return True
