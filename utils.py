current_user = None  # Global variable to track the logged-in user


def is_logged_in():
    """
    Checks if a user is currently logged in.
    """
    return current_user is not None
