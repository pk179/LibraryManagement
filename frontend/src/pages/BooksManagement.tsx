import { useState, useEffect, useCallback, type SyntheticEvent } from 'react';
import {
    getBooks,
    createBook,
    updateBook,
    deleteBook,
    bulkDeleteBooks,
    searchBooks,
} from '../api/books';
import type { BookResponse, BookCreate, BookUpdate } from '../api/types';
import axios from 'axios';

function BooksManagement() {
    const [books, setBooks] = useState<BookResponse[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
    const [query, setQuery] = useState('');
    const [availableOnly, setAvailableOnly] = useState(false);
    const [editing, setEditing] = useState<BookResponse | null>(null);
    const [form, setForm] = useState<BookCreate>({
        title: '',
        author: '',
        year: new Date().getFullYear(),
        quantity: 1,
        genre: '',
        isbn: '',
    });

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

    const handleSelect = (id: number, checked: boolean) => {
        const set = new Set(selectedIds);
        if (checked) set.add(id);
        else set.delete(id);
        setSelectedIds(set);
    };

    const handleBulkDelete = async () => {
        if (selectedIds.size === 0) return;
        if (!confirm('Delete selected books?')) return;
        try {
            const ids = Array.from(selectedIds);
            await bulkDeleteBooks(ids);
            setSelectedIds(new Set());
            loadBooks();
        } catch (err: unknown) {
            if (axios.isAxiosError(err)) {
                alert(err.response?.data?.detail ?? 'Bulk delete failed');
            } else {
                alert('Bulk delete failed');
            }
        }
    };

    const openNewForm = () => {
        setEditing(null);
        setForm({ title: '', author: '', year: new Date().getFullYear(), quantity: 1, genre: '', isbn: '' });
    };

    const openEditForm = (book: BookResponse) => {
        setEditing(book);
        setForm({
            title: book.title,
            author: book.author,
            year: book.year,
            quantity: book.quantity,
            genre: book.genre || '',
            isbn: book.isbn || '',
        });
    };

    const handleFormChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setForm(prev => ({ ...prev, [name]: name === 'year' || name === 'quantity' ? Number(value) : value }));
    };

    const handleFormSubmit = async (e: SyntheticEvent<HTMLFormElement>) => {
        e.preventDefault();
        try {
            if (editing) {
                await updateBook(editing.id, form as BookUpdate);
                alert('Book updated');
            } else {
                await createBook(form as BookCreate);
                alert('Book created');
            }
            loadBooks();
            openNewForm();
        } catch (err: unknown) {
            if (axios.isAxiosError(err)) {
                alert(err.response?.data?.detail ?? 'Save failed');
            } else {
                alert('Save failed');
            }
        }
    };

    const handleDelete = async (id: number) => {
        if (!confirm('Delete this book?')) return;
        try {
            await deleteBook(id);
            loadBooks();
        } catch (err: unknown) {
            if (axios.isAxiosError(err)) {
                alert(err.response?.data?.detail ?? 'Delete failed');
            } else {
                alert('Delete failed');
            }
        }
    };

    return (
        <div>
            <h2>Books Management</h2>

            <div style={{ marginBottom: '12px' }}>
                <button onClick={openNewForm}>Add Book</button>
                <button onClick={handleBulkDelete} disabled={selectedIds.size === 0} style={{ marginLeft: '8px' }}>
                    Delete Selected
                </button>
            </div>

            <form onSubmit={handleFormSubmit} style={{ marginBottom: '16px', border: '1px solid #ccc', padding: '8px' }}>
                <h3>{editing ? 'Edit Book' : 'New Book'}</h3>
                <div>
                    <label>Title: <input name="title" value={form.title} onChange={handleFormChange} required /></label>
                </div>
                <div>
                    <label>Author: <input name="author" value={form.author} onChange={handleFormChange} required /></label>
                </div>
                <div>
                    <label>Year: <input name="year" type="number" value={form.year} onChange={handleFormChange} required /></label>
                </div>
                <div>
                    <label>Quantity: <input name="quantity" type="number" value={form.quantity} onChange={handleFormChange} required /></label>
                </div>
                <div>
                    <label>Genre: <input name="genre" value={form.genre} onChange={handleFormChange} /></label>
                </div>
                <div>
                    <label>ISBN: <input name="isbn" value={form.isbn} onChange={handleFormChange} /></label>
                </div>
                <button type="submit">{editing ? 'Update' : 'Create'}</button>
            </form>

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
                            <th style={{ textAlign: 'left', padding: '8px' }}></th>
                            <th style={{ textAlign: 'left', padding: '8px' }}>Title</th>
                            <th style={{ textAlign: 'left', padding: '8px' }}>Author</th>
                            <th style={{ textAlign: 'left', padding: '8px' }}>Year</th>
                            <th style={{ textAlign: 'left', padding: '8px' }}>Genre</th>
                            <th style={{ textAlign: 'left', padding: '8px' }}>Quantity</th>
                            <th style={{ textAlign: 'left', padding: '8px' }}>ISBN</th>
                            <th style={{ textAlign: 'left', padding: '8px' }}>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {books.map(book => (
                            <tr key={book.id} style={{ borderBottom: '1px solid #eee' }}>
                                <td style={{ padding: '8px' }}>
                                    <input
                                        type="checkbox"
                                        checked={selectedIds.has(book.id)}
                                        onChange={e => handleSelect(book.id, e.target.checked)}
                                    />
                                </td>
                                <td style={{ padding: '8px' }}>{book.title}</td>
                                <td style={{ padding: '8px' }}>{book.author}</td>
                                <td style={{ padding: '8px' }}>{book.year >= 0 ? book.year : Math.abs(book.year) + ' BC'}</td>
                                <td style={{ padding: '8px' }}>{book.genre || '-'}</td>
                                <td style={{ padding: '8px' }}>{book.quantity}</td>
                                <td style={{ padding: '8px' }}>{book.isbn}</td>
                                <td style={{ padding: '8px' }}>
                                    <button onClick={() => openEditForm(book)}>Edit</button>{' '}
                                    <button onClick={() => handleDelete(book.id)}>Delete</button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    );
}

export default BooksManagement;
