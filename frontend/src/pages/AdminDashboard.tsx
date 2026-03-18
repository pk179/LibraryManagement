import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { getLoanStats } from '../api/loans';
import { resetDatabase } from '../api/admin';
import type { LoanStatsResponse } from '../api/types';
import axios from 'axios';

function AdminDashboard() {
    const navigate = useNavigate();
    const [stats, setStats] = useState<LoanStatsResponse | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [resetting, setResetting] = useState(false);
    const [resetMessage, setResetMessage] = useState<string | null>(null);
    const [resetError, setResetError] = useState<string | null>(null);

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

    const handleReset = async () => {
        if (!window.confirm('This will reset all data to the initial seed state. Continue?')) {
            return;
        }

        setResetting(true);
        setResetMessage(null);
        setResetError(null);

        try {
            await resetDatabase();
            setResetMessage('Database reset successfully. You will be logged out.');
            localStorage.clear();
            navigate('/login');
        } catch (err: unknown) {
            if (axios.isAxiosError(err)) {
                setResetError(err.response?.data?.detail ?? 'Failed to reset database');
            } else {
                setResetError('Failed to reset database');
            }
        } finally {
            setResetting(false);
        }
    };

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

                <div style={{ marginTop: '16px' }}>
                    <button onClick={handleReset} disabled={resetting}>
                        {resetting ? 'Resetting…' : 'Reset database'}
                    </button>
                    {resetMessage && <p style={{ color: 'green' }}>{resetMessage}</p>}
                    {resetError && <p style={{ color: 'red' }}>{resetError}</p>}
                </div>
            </div>
        </div>
    );
}

export default AdminDashboard;
