import { test, expect } from './fixtures/fixtures'

test.describe('Reset database', () => {
    //test.skip(({ browserName }) => browserName !== 'chromium');

    test('admin can reset database', async ({ authenticatedAdminPage: page }) => {
        await page.goto('/admin');
        await expect(page.getByRole('button', { name: 'Reset database' })).toBeVisible();

        page.on('dialog', async dialog => {
            expect(dialog.message()).toBe('This will reset all data to the initial seed state. Continue?');
            await dialog.accept();
        });

        await page.getByRole('button', { name: 'Reset database' }).click();

        await expect(page.getByRole('heading', { name: "Login" })).toBeVisible({ timeout: 10000 });
        await expect(page).toHaveURL('/login');

        const storage = await page.evaluate(() => ({
            accessToken: localStorage.getItem('access_token'),
            username: localStorage.getItem('username'),
            role: localStorage.getItem('role'),
        }));

        expect(storage.accessToken).toBeNull();
        expect(storage.username).toBeNull();
        expect(storage.role).toBeNull();
    });

    test('database returns to seed state after reset', async ({ authenticatedAdminPage: page, backendRequest, adminToken }) => {
        const bookResponse = await backendRequest.post('/api/books', {
            headers: {
                Authorization: `Bearer ${adminToken}`,
            },
            data: {
                title: 'reset database test',
                author: 'reset database test',
                year: 2026,
                quantity: 5,
                genre: 'test',
                isbn: undefined,
            },
        });
        expect(bookResponse.status()).toBe(201);

        const userResponse = await backendRequest.post('/api/auth/register', {
            data: {
                username: 'reset_database_test_user',
                password: 'User12345',
                role: 'user',
            },
        });
        expect(userResponse.ok()).toBeTruthy();

        const loanResponse = await backendRequest.post('/api/loans', {
            headers: {
                Authorization: `Bearer ${adminToken}`,
            },
            data: {
                book_id: 2,
            },
        });
        expect(loanResponse.status()).toBe(201);

        await page.goto('/admin');
        await expect(page.getByRole('button', { name: 'Reset database' })).toBeVisible();

        page.on('dialog', async dialog => {
            expect(dialog.message()).toBe('This will reset all data to the initial seed state. Continue?');
            await dialog.accept();
        });

        await page.getByRole('button', { name: 'Reset database' }).click();
        await expect(page.getByRole('heading', { name: "Login" })).toBeVisible({ timeout: 10000 });
        await expect(page).toHaveURL('/login');

        await page.getByLabel('Username:').fill('admin');
        await page.getByLabel('Password:').fill('Admin123');
        await page.getByRole('button', { name: 'Login' }).click();

        await page.goto('/admin');
        await expect(page.getByText('Total loans')).toContainText(/\d+/);
        const totalLoans = Number((await page.getByText('Total loans').textContent())!.match(/\d+/)?.[0]);
        const activeLoans = Number((await page.getByText('Active').textContent())!.match(/\d+/)?.[0]);
        const overdueLoans = Number((await page.getByText('Overdue').textContent())!.match(/\d+/)?.[0]);
        const returnedLoans = Number((await page.getByText('Returned').textContent())!.match(/\d+/)?.[0]);
        expect(totalLoans).toEqual(6);
        expect(activeLoans).toEqual(5);
        expect(overdueLoans).toEqual(5);
        expect(returnedLoans).toEqual(1);

        await page.goto('/admin/books');
        await expect(page.getByTestId('book-title').first()).toBeVisible();
        await expect(page.getByTestId('book-title')).toHaveCount(30);
        await page.getByPlaceholder('Search').fill('reset database test');
        await expect(page.getByTestId('book-title')).toHaveCount(0);

        await page.goto('/admin/users');
        await expect(page.getByTestId(/user-row/).first()).toBeVisible();
        await expect(page.getByTestId(/user-row/)).toHaveCount(5);
        await expect(page.getByTestId('username').filter({ hasText: 'reset_database_test_user' })).toHaveCount(0);

        await page.goto('/admin/loans');
        await expect(page.getByTestId(/loan-row/).first()).toBeVisible();
        await expect(page.getByTestId(/loan-row/)).toHaveCount(6);
        await expect(page.getByTestId('userid').filter({ hasText: '1' })).toHaveCount(0);
    });
});