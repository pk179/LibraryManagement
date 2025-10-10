

import re
from datetime import datetime

# constants
MIN_YEAR = -2000   # allow ancient works
MAX_YEAR = datetime.now().year  # current year
# letters, digits, underscore
USERNAME_REGEX = re.compile(r'^[A-Za-z0-9_]{3,30}$')
# letters, digits, spaces, hyphens
GENRE_REGEX = re.compile(r'^[\w\s\-]{1,50}$')
PASSWORD_MIN_LENGTH = 8


def validate_non_empty_string(name: str, value: str):
    """Raise ValueError if value is empty or only whitespace."""
    if value is None or not str(value).strip():
        raise ValueError(f"{name} must not be empty.")
    return True


def validate_username(username: str):
    """Username: 3-30 chars, letters/digits/underscore only."""
    if username is None:
        raise ValueError("Username is required.")
    if not USERNAME_REGEX.match(username):
        raise ValueError(
            "Username must be 3-30 characters and contain only letters, digits or underscore.")
    return True


def validate_password_strength(password: str):
    """
    Password basic checks:
    - at least PASSWORD_MIN_LENGTH characters
    - contains at least one letter and one digit
    """
    if password is None:
        raise ValueError("Password is required.")
    if len(password) < PASSWORD_MIN_LENGTH:
        raise ValueError(
            f"Password must be at least {PASSWORD_MIN_LENGTH} characters long.")
    if not re.search(r"[A-Za-z]", password):
        raise ValueError("Password must contain at least one letter.")
    if not re.search(r"[0-9]", password):
        raise ValueError("Password must contain at least one digit.")
    return True


def validate_role(role: str):
    """Role must be one of allowed roles."""
    allowed = {"user", "admin"}
    if role not in allowed:
        raise ValueError(f"Role must be one of: {', '.join(sorted(allowed))}.")
    return True


def validate_year(year):
    """Validate publication year (allow negative years for ancient works)."""
    try:
        y = int(year)
    except Exception:
        raise ValueError("Year must be an integer.")
    if y < MIN_YEAR or y > MAX_YEAR:
        raise ValueError(f"Year must be between {MIN_YEAR} and {MAX_YEAR}.")
    return True


def validate_quantity(quantity):
    """Quantity must be integer >= 0."""
    try:
        q = int(quantity)
    except Exception:
        raise ValueError("Quantity must be an integer.")
    if q < 0:
        raise ValueError("Quantity must be >= 0.")
    return True


def normalize_isbn(isbn: str) -> str:
    """Remove hyphens/spaces and return uppercase string."""
    if isbn is None:
        return ""
    return re.sub(r'[^0-9Xx]', '', isbn).upper()


def is_valid_isbn(isbn: str) -> bool:
    """
    Validate ISBN-10 or ISBN-13.
    Returns True if valid, False otherwise.
    """
    s = normalize_isbn(isbn)
    if not s:
        return False

    # ISBN-10
    if len(s) == 10:
        total = 0
        for i, ch in enumerate(s):
            if ch in "Xx":
                if i != 9:
                    return False
                val = 10
            else:
                if not ch.isdigit():
                    return False
                val = ord(ch) - ord('0')
            weight = 10 - i
            total += val * weight
        return total % 11 == 0

    # ISBN-13
    if len(s) == 13 and s.isdigit():
        total = 0
        for i, ch in enumerate(s):
            val = ord(ch) - ord('0')
            if i % 2 == 0:
                total += val
            else:
                total += val * 3
        return total % 10 == 0

    return False


def validate_isbn_optional(isbn: str):
    """
    If isbn is provided (non-empty after normalization) validate it.
    Raises ValueError on invalid format/checksum.
    """
    norm = normalize_isbn(isbn)
    if not norm:
        return True  # empty => allowed
    if not is_valid_isbn(norm):
        raise ValueError("Invalid ISBN (must be valid ISBN-10 or ISBN-13).")
    return True


def validate_genre(genre: str):
    """Genre may be empty or conform to GENRE_REGEX (1-50 chars)."""
    if genre is None or str(genre).strip() == "":
        return True
    if not GENRE_REGEX.match(genre):
        raise ValueError(
            "Genre may contain letters, digits, spaces and hyphens (max 50 chars).")
    return True


def validate_user_registration(username: str, password: str, role: str = "user"):
    """
    Validate all fields required for user registration.
    Raises ValueError on first invalid field.
    """
    validate_username(username)
    validate_password_strength(password)
    validate_role(role)
    return True


def validate_book_data(title: str, author: str, year, quantity, genre: str = None, isbn: str = None):
    """
    Validate book fields prior to insertion/update.
    Raises ValueError on failure.
    """
    validate_non_empty_string("Title", title)
    validate_non_empty_string("Author", author)
    validate_year(year)
    validate_quantity(quantity)
    validate_genre(genre)
    validate_isbn_optional(isbn)
    return True
