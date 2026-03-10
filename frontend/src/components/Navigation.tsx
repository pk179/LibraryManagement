import { Link, useNavigate } from 'react-router-dom';
import { logout } from '../api/auth';

function Navigation() {
    const navigate = useNavigate();
    const token = localStorage.getItem('access_token');
    const role = localStorage.getItem('role');
    const username = localStorage.getItem('username');

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <nav style={{ padding: '8px', borderBottom: '1px solid #ccc' }}>
            <Link to="/">Home</Link> |{' '}
            <Link to="/books">Books</Link> |{' '}
            <Link to="/my-loans">My Loans</Link> |{' '}
            {token ? (
                <>
                    {role === 'admin' && (
                        <>
                            <Link to="/admin">Admin Dashboard</Link> |{' '}
                        </>
                    )}
                    <span>Logged in as {username}</span>{' '}
                    <button onClick={handleLogout}>Logout</button>
                </>
            ) : (
                <>
                    <Link to="/login">Login</Link> |{' '}
                    <Link to="/register">Register</Link>
                </>
            )}
        </nav>
    );
}

export default Navigation;
