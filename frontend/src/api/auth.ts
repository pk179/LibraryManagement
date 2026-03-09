import { api } from './config';
import type { UserRegister, RegisterResponse, UserLogin, TokenResponse, JwtPayload } from './types';

export const register = async (userData: UserRegister): Promise<RegisterResponse> => {
    const response = await api.post<RegisterResponse>('/api/auth/register', userData);
    return response.data;
};

function parseJwt(token: string): JwtPayload | null {
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        return JSON.parse(atob(base64));
    } catch {
        return null;
    }
}

export const login = async (credentials: UserLogin): Promise<TokenResponse> => {
    const response = await api.post<TokenResponse>('/api/auth/login', credentials);
    const token = response.data.access_token;
    localStorage.setItem('access_token', token);
    const payload = parseJwt(token);
    if (payload?.role) localStorage.setItem('role', payload.role);
    if (payload?.username) localStorage.setItem('username', payload.username);
    return response.data;
};

export const logout = (): void => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('role');
    localStorage.removeItem('username');
};
