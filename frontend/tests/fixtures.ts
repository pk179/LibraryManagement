import { test as base, expect, type APIRequestContext, type Page } from '@playwright/test';

const frontendBaseURL = process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:5173';
const backendBaseURL = process.env.VITE_API_BASE_URL || 'http://localhost:8000';

interface JwtPayload {
    username: string;
    role: string;
}

function decodeJwtPayload(token: string): JwtPayload {
    const payloadBase64 = token.split('.')[1];
    const padded = payloadBase64.padEnd(payloadBase64.length + (4 - (payloadBase64.length % 4)) % 4, '=');
    const payloadJson = Buffer.from(padded.replace(/-/g, '+').replace(/_/g, '/'), 'base64').toString('utf-8');
    return JSON.parse(payloadJson) as JwtPayload;
}

async function setPageAuth(page: Page, token: string) {
    const payload = decodeJwtPayload(token);
    await page.addInitScript(`
      window.localStorage.setItem('access_token', ${JSON.stringify(token)});
      window.localStorage.setItem('username', ${JSON.stringify(payload.username)});
      window.localStorage.setItem('role', ${JSON.stringify(payload.role)});
    `);
}

export const test = base.extend<{
    backendRequest: APIRequestContext;
    userToken: string;
    adminToken: string;
    authenticatedUserPage: Page;
    authenticatedAdminPage: Page;
    resetDatabase: () => Promise<void>;
}>({
    backendRequest: async ({ playwright }, run) => {
        const request = await playwright.request.newContext({
            baseURL: backendBaseURL,
            extraHTTPHeaders: {
                'Content-Type': 'application/json',
            },
        });
        await run(request);
        await request.dispose();
    },

    userToken: async ({ backendRequest }, run) => {
        const response = await backendRequest.post('/api/auth/login', {
            data: {
                username: 'user',
                password: 'User12345',
            },
        });
        expect(response.ok()).toBeTruthy();
        const body = await response.json();
        await run(body.access_token as string);
    },

    adminToken: async ({ backendRequest }, run) => {
        const response = await backendRequest.post('/api/auth/login', {
            data: {
                username: 'admin',
                password: 'Admin123',
            },
        });
        expect(response.ok()).toBeTruthy();
        const body = await response.json();
        await run(body.access_token as string);
    },

    authenticatedUserPage: async ({ page, userToken }, run) => {
        await setPageAuth(page, userToken);
        await page.goto(frontendBaseURL, { waitUntil: 'networkidle' });
        await run(page);
    },

    authenticatedAdminPage: async ({ page, adminToken }, run) => {
        await setPageAuth(page, adminToken);
        await page.goto(frontendBaseURL, { waitUntil: 'networkidle' });
        await run(page);
    },

    resetDatabase: async ({ backendRequest, adminToken }, run) => {
        await run(async () => {
            const response = await backendRequest.post('/api/admin/reset', {
                data: {},
                headers: {
                    Authorization: `Bearer ${adminToken}`,
                },
            });
            expect(response.ok()).toBeTruthy();
        });
    },
});

export { expect } from '@playwright/test';
