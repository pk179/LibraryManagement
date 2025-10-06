import sqlite3


def init_db():
    """
    Tworzy bazę danych 'library.db' i tabelę 'books'
    """
    # Połączenie z bazą danych
    conn = sqlite3.connect('library.db')
    c = conn.cursor()

    # Tworzenie tabeli 'books'
    c.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY,
            title TEXT,
            author TEXT,
            year INTEGER,
            available BOOLEAN
        )
    ''')

    # Zatwierdzenie zmian i zamknięcie połączenia
    conn.commit()
    conn.close()


def add_book(title, author, year):
    """
    Dodaje nową książkę do tabeli 'books'
    """
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    # Sprawdzenie, czy książka już istnieje
    c.execute(
        "SELECT * FROM books WHERE title = ? AND author = ? AND year = ?",
        (title, author, year)
    )
    if not c.fetchone():
        # Dodanie książki do bazy danych
        c.execute(
            "INSERT INTO books (title, author, year, available) VALUES (?, ?, ?, ?)",
            (title, author, year, True)
        )
        conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Baza danych została zainicjalizowana.")
    add_book("It", "Stephen King", 1986)
    print("Dodano książkę do bazy danych.")
