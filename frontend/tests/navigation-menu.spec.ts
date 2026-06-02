import { test, expect } from './fixtures/fixtures';

test.describe('Navigation Menu', () => {
    test('user navigation menu is displayed correctly', async ({ authenticatedUserPage: page }) => {
        const navbar = page.locator('nav');
        await expect(navbar.getByRole('link', { name: 'Home' })).toBeVisible();
        await expect(navbar.getByRole('link', { name: 'Books' })).toBeVisible();
        await expect(navbar.getByRole('link', { name: 'My Loans' })).toBeVisible();
        await expect(navbar.getByRole('link', { name: 'Admin Dashboard' })).not.toBeVisible();
        await expect(navbar.getByRole('button', { name: 'Logout' })).toBeVisible();
    });

    test('admin navigation menu is displayed correctly', async ({ authenticatedAdminPage: page }) => {
        const navbar = page.locator('nav');
        await expect(navbar.getByRole('link', { name: 'Home' })).toBeVisible();
        await expect(navbar.getByRole('link', { name: 'Books' })).toBeVisible();
        await expect(navbar.getByRole('link', { name: 'My Loans' })).toBeVisible();
        await expect(navbar.getByRole('link', { name: 'Admin Dashboard' })).toBeVisible();
        await expect(navbar.getByRole('button', { name: 'Logout' })).toBeVisible();
    });

    test('user can logout and is redirected to login', async ({ authenticatedUserPage: page }) => {
        await page.goto('/my-loans');
        await page.getByRole('button', { name: 'Logout' }).click();
        await expect(page).toHaveURL('/login');
        await expect(page.getByRole('button', { name: 'Login' })).toBeVisible();

        const storage = await page.evaluate(() => ({
            accessToken: localStorage.getItem('access_token'),
            username: localStorage.getItem('username'),
            role: localStorage.getItem('role'),
        }));

        expect(storage.accessToken).toBeNull();
        expect(storage.username).toBeNull();
        expect(storage.role).toBeNull();
    });
});