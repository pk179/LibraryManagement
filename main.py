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


if __name__ == "__main__":
    init_db()
    print("Baza danych została zainicjalizowana!")
