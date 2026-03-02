import { api } from './config';
import type { LoanResponse, LoanActionResponse, LoanStatsResponse } from './types';

export const borrowBook = async (bookId: number): Promise<LoanActionResponse> => {
    const response = await api.post<LoanActionResponse>('/api/loans', { book_id: bookId });
    return response.data;
};

export const returnBook = async (bookId: number): Promise<LoanActionResponse> => {
    const response = await api.post<LoanActionResponse>('/api/loans/return', { book_id: bookId });
    return response.data;
};

export const getMyReturnedLoans = async (): Promise<LoanResponse[]> => {
    const response = await api.get<LoanResponse[]>('/api/loans/returned');
    return response.data;
};

export const getMyOverdueLoans = async (): Promise<LoanResponse[]> => {
    const response = await api.get<LoanResponse[]>('/api/loans/overdue');
    return response.data;
};

export const getMyActiveLoans = async (): Promise<LoanResponse[]> => {
    const response = await api.get<LoanResponse[]>('/api/loans/active');
    return response.data;
};

export const getAllLoans = async (): Promise<LoanResponse[]> => {
    const response = await api.get<LoanResponse[]>('/api/loans/all');
    return response.data;
};

export const getAllOverdueLoans = async (): Promise<LoanResponse[]> => {
    const response = await api.get<LoanResponse[]>('/api/loans/all/overdue');
    return response.data;
};

export const getLoanStats = async (): Promise<LoanStatsResponse> => {
    const response = await api.get<LoanStatsResponse>('/api/loans/stats');
    return response.data;
};