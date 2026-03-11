import { useState, useEffect, useCallback } from 'react';
import { getBooks, searchBooks } from '../api/books';
import { borrowBook } from '../api/loans';
import type { BookResponse } from '../api/types';
import axios from 'axios';

function BooksList() {
    const [books, setBooks] = useState<BookResponse[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [availableOnly, setAvailableOnly] = useState(false);
    const [query, setQuery] = useState('');

    const loadBooks = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            let results: BookResponse[];
            if (query.trim()) {
                results = await searchBooks(query, availableOnly);
            } else {
                results = await getBooks(availableOnly);
            }
            setBooks(results);
        } catch (err: unknown) {
            if (axios.isAxiosError(err)) {
                setError(err.response?.data?.detail ?? 'Failed to load books');
            } else {
                setError('Failed to load books');
            }
        } finally {
            setLoading(false);
        }
    }, [query, availableOnly]);

    useEffect(() => {
        loadBooks();
    }, [loadBooks]);

    const handleBorrow = async (bookId: number) => {
        try {
            await borrowBook(bookId);
            alert('Book borrowed successfully!');
            loadBooks();
        } catch (err: unknown) {
            if (axios.isAxiosError(err)) {
                alert(err.response?.data?.detail ?? 'Failed to borrow book');
            } else {
                alert('Failed to borrow book');
            }
        }
    };

    return (
        <div>
            <h2>Books Catalog</h2>

            <form style={{ marginBottom: '12px' }}>
                <input
                    type="text"
                    placeholder="Search by title, author, or genre..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    style={{ padding: '4px', minWidth: '300px' }}
                />
            </form>

            <label style={{ marginBottom: '12px', display: 'block' }}>
                <input
                    type="checkbox"
                    checked={availableOnly}
                    onChange={(e) => setAvailableOnly(e.target.checked)}
                />
                {' '}Show only available books
            </label>

            {loading && <p>Loading books...</p>}
            {error && <p style={{ color: 'red' }}>Error: {error}</p>}
            {!loading && books.length === 0 && <p>No books found.</p>}

            {!loading && books.length > 0 && (
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                    <thead>
                        <tr style={{ borderBottom: '1px solid #ccc' }}>
                            <th style={{ textAlign: 'left', padding: '8px' }}>Title</th>
                            <th style={{ textAlign: 'left', padding: '8px' }}>Author</th>
                            <th style={{ textAlign: 'left', padding: '8px' }}>Year</th>
                            <th style={{ textAlign: 'left', padding: '8px' }}>Genre</th>
                            <th style={{ textAlign: 'left', padding: '8px' }}>Available</th>
                            <th style={{ textAlign: 'left', padding: '8px' }}>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {books.map((book) => (
                            <tr key={book.id} style={{ borderBottom: '1px solid #eee' }}>
                                <td style={{ padding: '8px' }}>{book.title}</td>
                                <td style={{ padding: '8px' }}>{book.author}</td>
                                <td style={{ padding: '8px' }}>{book.year >= 0 ? book.year : Math.abs(book.year) + ' BC'}</td>
                                <td style={{ padding: '8px' }}>{book.genre || '-'}</td>
                                <td style={{ padding: '8px' }}>
                                    {book.quantity > 0 ? `Yes (${book.quantity})` : 'No'}
                                </td>
                                <td style={{ padding: '8px' }}>
                                    {book.quantity > 0 ? (
                                        <button onClick={() => handleBorrow(book.id)}>
                                            Borrow
                                        </button>
                                    ) : (
                                        <span style={{ color: '#999' }}>Unavailable</span>
                                    )}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    );
}

export default BooksList;