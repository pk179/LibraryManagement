import { test, expect } from './fixtures/fixtures';

test.describe('Users management', () => {
    test('admin can view users', async ({ authenticatedAdminPage: page }) => {
        await page.goto('/admin/users');
        await expect(page.getByTestId('user-row-admin')).toBeVisible();
        await expect(page.getByTestId('user-row-user')).toBeVisible();
        expect(await page.getByTestId(/user-row-/).count()).toBeGreaterThanOrEqual(5);
    })

    test('admin can delete a user', async ({ authenticatedAdminPage: page, testUser, backendRequest }) => {
        await page.goto('/admin/users');
        const username = testUser.username;

        page.on('dialog', async dialog => {
            const msg = dialog.message();

            if (msg === 'Delete this user?') {
                await dialog.accept();
            } else if (msg === 'User deleted') {
                expect(dialog.type()).toBe('alert');
                await dialog.accept();
            }
        });
        await page.getByTestId(`user-row-${username}`).getByRole('button', { name: 'Delete' }).click();
        await expect(page.getByTestId(`user-row-${username}`)).toHaveCount(0);

        const response = await backendRequest.post('/api/auth/login', {
            data: {
                username,
                password: 'User12345',
            },
        });
        expect(response.status()).toBe(401);
    })

    test('admin cannot delete their own account', async ({ authenticatedAdminPage: page }) => {
        await page.goto('/admin/users');

        const messages: string[] = [];
        page.on('dialog', async dialog => {
            messages.push(dialog.message());
            await dialog.accept();
        });

        await page.getByTestId('user-row-admin').getByRole('button', { name: 'Delete' }).click();

        await expect.poll(() => messages).toEqual([
            'Delete this user?',
            'Admin cannot delete themselves',
        ]);

        await expect(page.getByTestId('user-row-admin')).toBeVisible();
    })
})
