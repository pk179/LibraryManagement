current_user = None  # Global variable to track the logged-in user


def is_logged_in():
    """
    Checks if a user is currently logged in.
    """
    return current_user is not None


def get_current_user():
    """
    Returns the current logged-in user.
    """
    return current_user


def set_current_user(user):
    """
    Sets the current logged-in user.
    """
    global current_user
    current_user = user
