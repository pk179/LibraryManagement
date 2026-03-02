import { api } from './config';
import type { UserResponse, MessageResponse } from './types';

export const getAllUsers = async (): Promise<UserResponse[]> => {
    const response = await api.get<UserResponse[]>('/api/users');
    return response.data;
};

export const deleteUser = async (userId: number): Promise<MessageResponse> => {
    const response = await api.delete<MessageResponse>(`/api/users/${userId}`);
    return response.data;
};