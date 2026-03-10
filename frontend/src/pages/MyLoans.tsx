import { useState, useEffect } from 'react';
import {
    getMyActiveLoans,
    getMyReturnedLoans,
    getMyOverdueLoans,
    returnBook,
} from '../api/loans';
import type { LoanResponse } from '../api/types';
import axios from 'axios';

function MyLoans() {
    const [active, setActive] = useState<LoanResponse[]>([]);
    const [returned, setReturned] = useState<LoanResponse[]>([]);
    const [overdue, setOverdue] = useState<LoanResponse[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [tab, setTab] = useState<'active' | 'returned' | 'overdue'>('active');

    const loadLoans = async () => {
        setLoading(true);
        setError(null);
        try {
            const [activeData, returnedData, overdueData] = await Promise.all([
                getMyActiveLoans(),
                getMyReturnedLoans(),
                getMyOverdueLoans(),
            ]);
            setActive(activeData);
            setReturned(returnedData);
            setOverdue(overdueData);
        } catch (err: unknown) {
            if (axios.isAxiosError(err)) {
                setError(err.response?.data?.detail ?? 'Failed to load loans');
            } else {
                setError('Failed to load loans');
            }
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadLoans();
    }, []);

    const handleReturn = async (bookId: number) => {
        try {
            await returnBook(bookId);
            alert('Book returned successfully!');
            loadLoans();
        } catch (err: unknown) {
            if (axios.isAxiosError(err)) {
                alert(err.response?.data?.detail ?? 'Return failed');
            } else {
                alert('An unexpected error occurred');
            }
        }
    };

    const renderLoansTable = (loans: LoanResponse[], showReturnButton: boolean) => {
        if (loans.length === 0) {
            return <p>No loans in this category.</p>;
        }

        return (
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                    <tr style={{ borderBottom: '1px solid #ccc' }}>
                        <th style={{ textAlign: 'left', padding: '8px' }}>Book ID</th>
                        <th style={{ textAlign: 'left', padding: '8px' }}>Borrow Date</th>
                        <th style={{ textAlign: 'left', padding: '8px' }}>Due Date</th>
                        <th style={{ textAlign: 'left', padding: '8px' }}>Return Date</th>
                        <th style={{ textAlign: 'left', padding: '8px' }}>Fine</th>
                        {showReturnButton && <th style={{ textAlign: 'left', padding: '8px' }}>Action</th>}
                    </tr>
                </thead>
                <tbody>
                    {loans.map((loan) => (
                        <tr key={loan.id} style={{ borderBottom: '1px solid #eee' }}>
                            <td style={{ padding: '8px' }}>{loan.book_id}</td>
                            <td style={{ padding: '8px' }}>{loan.borrow_date}</td>
                            <td style={{ padding: '8px' }}>{loan.due_date}</td>
                            <td style={{ padding: '8px' }}>{loan.return_date || '-'}</td>
                            <td style={{ padding: '8px' }}>${loan.fine.toFixed(2)}</td>
                            {showReturnButton && (
                                <td style={{ padding: '8px' }}>
                                    <button onClick={() => handleReturn(loan.book_id)}>
                                        Return Book
                                    </button>
                                </td>
                            )}
                        </tr>
                    ))}
                </tbody>
            </table>
        );
    };

    return (
        <div>
            <h2>My Loans</h2>

            <div style={{ marginBottom: '12px' }}>
                <button
                    onClick={() => setTab('active')}
                    style={{
                        padding: '8px 12px',
                        marginRight: '4px',
                        fontWeight: tab === 'active' ? 'bold' : 'normal',
                        backgroundColor: tab === 'active' ? '#0b006e' : '#505050',
                    }}
                >
                    Active ({active.length})
                </button>
                <button
                    onClick={() => setTab('returned')}
                    style={{
                        padding: '8px 12px',
                        marginRight: '4px',
                        fontWeight: tab === 'returned' ? 'bold' : 'normal',
                        backgroundColor: tab === 'returned' ? '#0b006e' : '#505050',
                    }}
                >
                    Returned ({returned.length})
                </button>
                <button
                    onClick={() => setTab('overdue')}
                    style={{
                        padding: '8px 12px',
                        fontWeight: tab === 'overdue' ? 'bold' : 'normal',
                        backgroundColor: tab === 'overdue' ? '#0b006e' : '#505050',
                    }}
                >
                    Overdue ({overdue.length})
                </button>
            </div>

            {loading && <p>Loading loans...</p>}
            {error && <p style={{ color: 'red' }}>Error: {error}</p>}

            {!loading && tab === 'active' && renderLoansTable(active, true)}
            {!loading && tab === 'returned' && renderLoansTable(returned, false)}
            {!loading && tab === 'overdue' && renderLoansTable(overdue, false)}
        </div>
    );
}

export default MyLoans;