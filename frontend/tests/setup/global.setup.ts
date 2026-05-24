import { request } from '@playwright/test';

const backendBaseURL =
    process.env.VITE_API_BASE_URL || 'http://localhost:8000';

async function globalSetup() {
    const api = await request.newContext({
        baseURL: backendBaseURL,
        extraHTTPHeaders: {
            'Content-Type': 'application/json',
        },
    });

    const login = await api.post('/api/auth/login', {
        data: {
            username: 'admin',
            password: 'Admin123',
        },
    });

    if (!login.ok()) {
        throw new Error(`Admin login failed: ${login.status()}`);
    }

    const body = await login.json();

    const reset = await api.post('/api/admin/reset', {
        data: {},
        headers: {
            Authorization: `Bearer ${body.access_token}`,
        },
    });

    if (!reset.ok()) {
        throw new Error(`Reset failed: ${reset.status()}`);
    }

    await api.dispose();
}

export default globalSetup;