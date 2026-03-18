import { api } from './config';

export const resetDatabase = async (): Promise<void> => {
    await api.post('/api/admin/reset');
}