from database import init_db
from users import register_user, login_user, logout_user, display_users
from books import add_book, display_books, update_book, delete_book, search_books
from loans import borrow_book, return_book


if __name__ == "__main__":
    init_db()

    login_user("alice", "password123")
    borrow_book(5)
    display_books()
    return_book(5)
    display_books()
    logout_user()
