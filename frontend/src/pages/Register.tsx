import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { register } from '../api/auth';
import type { UserRegister } from '../api/types';
import axios from 'axios';

function Register() {
    const [credentials, setCredentials] = useState<UserRegister>({ username: '', password: '', role: 'user' });
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        setCredentials({ ...credentials, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e: React.SyntheticEvent<HTMLFormElement>) => {
        e.preventDefault();
        setError(null);
        setLoading(true);
        try {
            await register(credentials);
            alert('Registration successful! Please login.');
            navigate('/login');
        } catch (err: unknown) {
            if (axios.isAxiosError(err)) {
                setError(err.response?.data?.detail ?? 'Registration failed');
            } else {
                setError('Registration failed');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <h2>Register</h2>
            {error && <p style={{ color: 'red' }}>{error}</p>}
            <form onSubmit={handleSubmit}>
                <div>
                    <label htmlFor='username'>Username:</label>
                    <input id='username' name="username" value={credentials.username} onChange={handleChange} placeholder='Username' required />
                </div>
                <div>
                    <label htmlFor='password'>Password:</label>
                    <input id='password' type="password" name="password" value={credentials.password} onChange={handleChange} placeholder='Password' required />
                </div>
                <button type="submit" disabled={loading}>{loading ? 'Registering...' : 'Register'}</button>
            </form>
        </div>
    );
}

export default Register;
