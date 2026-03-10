import { useState, useEffect } from 'react';
import { getLoanStats } from '../api/loans';
import type { LoanStatsResponse } from '../api/types';
import { Link } from 'react-router-dom';
import axios from 'axios';

function AdminDashboard() {
    const [stats, setStats] = useState<LoanStatsResponse | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetch = async () => {
            setLoading(true);
            setError(null);
            try {
                const data = await getLoanStats();
                setStats(data);
            } catch (err: unknown) {
                if (axios.isAxiosError(err)) {
                    setError(err.response?.data?.detail ?? 'Failed to fetch stats');
                } else {
                    setError('Failed to fetch stats');
                }
            } finally {
                setLoading(false);
            }
        };
        fetch();
    }, []);

    return (
        <div>
            <h2>Admin Dashboard</h2>
            {loading && <p>Loading stats...</p>}
            {error && <p style={{ color: 'red' }}>{error}</p>}
            {stats && (
                <ul>
                    <li>Total loans: {stats.total_loans}</li>
                    <li>Active: {stats.active_loans}</li>
                    <li>Overdue: {stats.overdue_loans}</li>
                    <li>Returned: {stats.returned_loans}</li>
                </ul>
            )}
            <div style={{ marginTop: '16px' }}>
                <h3>Manage</h3>
                <ul>
                    <li><Link to="/admin/books">Books</Link></li>
                    <li><Link to="/admin/users">Users</Link></li>
                    <li><Link to="/admin/loans">Loans</Link></li>
                </ul>
            </div>
        </div>
    );
}

export default AdminDashboard;
