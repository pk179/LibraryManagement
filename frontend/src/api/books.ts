import { api } from './config';
import type { BookResponse, BookCreate, BookUpdate, PostBookResponse, MessageResponse, BulkDeleteResponse } from './types';

export const getBooks = async (availableOnly: boolean = false): Promise<BookResponse[]> => {
    const response = await api.get<BookResponse[]>('/api/books', {
        params: { available: availableOnly },
    });
    return response.data;
};

export const getBook = async (bookId: number): Promise<BookResponse> => {
    const response = await api.get<BookResponse>(`/api/books/view/${bookId}`);
    return response.data;
};

export const createBook = async (bookData: BookCreate): Promise<PostBookResponse> => {
    const response = await api.post<PostBookResponse>('/api/books', bookData);
    return response.data;
};

export const updateBook = async (bookId: number, bookData: BookUpdate): Promise<PostBookResponse> => {
    const response = await api.put<PostBookResponse>(`/api/books/${bookId}`, bookData);
    return response.data;
};

export const deleteBook = async (bookId: number): Promise<MessageResponse> => {
    const response = await api.delete<MessageResponse>(`/api/books/${bookId}`);
    return response.data;
};

export const bulkDeleteBooks = async (bookIds: number[]): Promise<BulkDeleteResponse> => {
    const response = await api.delete<BulkDeleteResponse>('/api/books', { data: bookIds });
    return response.data;
};

export const searchBooks = async (query: string, availableOnly: boolean = false, genre?: string): Promise<BookResponse[]> => {
    const response = await api.get<BookResponse[]>('/api/books/search', {
        params: { q: query, available: availableOnly, genre },
    });
    return response.data;
};