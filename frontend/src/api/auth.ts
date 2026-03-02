import { api } from './config';
import type { UserRegister, RegisterResponse, UserLogin, TokenResponse } from './types';

export const register = async (userData: UserRegister): Promise<RegisterResponse> => {
    const response = await api.post<RegisterResponse>('/api/auth/register', userData);
    return response.data;
};

export const login = async (credentials: UserLogin): Promise<TokenResponse> => {
    const response = await api.post<TokenResponse>('/api/auth/login', credentials);
    localStorage.setItem('access_token', response.data.access_token);
    return response.data;
};

export const logout = (): void => {
    localStorage.removeItem('access_token');
};
