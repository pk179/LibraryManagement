import { useState, useEffect } from 'react';
import {
    getAllLoans,
    getAllOverdueLoans,
} from '../api/loans';
import type { LoanResponse } from '../api/types';
import axios from 'axios';

function AllLoans() {
    const [loans, setLoans] = useState<LoanResponse[]>([]);
    const [overdue, setOverdue] = useState<LoanResponse[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [tab, setTab] = useState<'all' | 'overdue' | 'stats'>('all');

    const loadLoans = async () => {
        setLoading(true);
        setError(null);
        try {
            const [a, o] = await Promise.all([
                getAllLoans(),
                getAllOverdueLoans(),
            ]);
            setLoans(a);
            setOverdue(o);
        } catch (err: unknown) {
            if (axios.isAxiosError(err)) {
                setError(err.response?.data?.detail ?? 'Failed to load loan data');
            } else {
                setError('Failed to load loan data');
            }
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadLoans();
    }, []);

    const renderLoansTable = (loans: LoanResponse[], showReturnDate: boolean) => {
        if (loans.length === 0) return <p>No loans found.</p>;
        return (
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                    <tr style={{ borderBottom: '1px solid #ccc' }}>
                        <th style={{ textAlign: 'left', padding: '8px' }}>ID</th>
                        <th style={{ textAlign: 'left', padding: '8px' }}>User ID</th>
                        <th style={{ textAlign: 'left', padding: '8px' }}>Book ID</th>
                        <th style={{ textAlign: 'left', padding: '8px' }}>Borrow Date</th>
                        <th style={{ textAlign: 'left', padding: '8px' }}>Due Date</th>
                        {showReturnDate && (
                            <th style={{ textAlign: 'left', padding: '8px' }}>Return Date</th>
                        )}
                        <th style={{ textAlign: 'left', padding: '8px' }}>Fine</th>
                    </tr>
                </thead>
                <tbody>
                    {loans.map(loan => (
                        <tr key={loan.id} style={{ borderBottom: '1px solid #eee' }}>
                            <td style={{ padding: '8px' }}>{loan.id}</td>
                            <td style={{ padding: '8px' }}>{loan.user_id}</td>
                            <td style={{ padding: '8px' }}>{loan.book_id}</td>
                            <td style={{ padding: '8px' }}>{new Date(loan.borrow_date).toLocaleString('sv-SE').slice(0, 16)}</td>
                            <td style={{ padding: '8px' }}>{new Date(loan.due_date).toLocaleString('sv-SE').slice(0, 16)}</td>
                            {showReturnDate && (
                                <td style={{ padding: '8px' }}>{loan.return_date ? new Date(loan.return_date).toLocaleString('sv-SE').slice(0, 16) : '-'}</td>
                            )}
                            <td style={{ padding: '8px' }}>${loan.fine.toFixed(2)}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        );
    };

    return (
        <div>
            <h2>All Loans</h2>

            <div style={{ marginBottom: '12px' }}>
                <button
                    onClick={() => setTab('all')}
                    style={{
                        padding: '8px 12px',
                        marginRight: '4px',
                        fontWeight: tab === 'all' ? 'bold' : 'normal',
                        backgroundColor: tab === 'all' ? '#0b006e' : '#505050',
                    }}
                >
                    All ({loans.length})
                </button>
                <button
                    onClick={() => setTab('overdue')}
                    style={{
                        padding: '8px 12px',
                        marginRight: '4px',
                        fontWeight: tab === 'overdue' ? 'bold' : 'normal',
                        backgroundColor: tab === 'overdue' ? '#0b006e' : '#505050',
                    }}
                >
                    Overdue ({overdue.length})
                </button>
            </div>
            {loading && <p>Loading loans...</p>}
            {error && <p style={{ color: 'red' }}>Error: {error}</p>}

            {!loading && tab === 'all' && renderLoansTable(loans, true)}
            {!loading && tab === 'overdue' && renderLoansTable(overdue, false)}
        </div>
    );
}

export default AllLoans;
