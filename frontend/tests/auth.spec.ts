import { test, expect } from './fixtures/fixtures';

test.describe('Authentication', () => {
    test('user can register and login', async ({ page }) => {
        await page.goto("/register")

        const username = `newuser${Date.now()}`;
        const password = 'NewUser12345';

        await page.getByLabel('Username:').fill(username);
        await page.getByLabel('Password:').fill(password);

        const dialogPromise = page.waitForEvent('dialog');
        await page.getByRole('button', { name: 'Register' }).click();
        const dialog = await dialogPromise;
        expect(dialog.message()).toBe('Registration successful! Please login.');
        await dialog.accept();

        await expect(page).toHaveURL("/login");
        await expect(page.getByLabel('Username:')).toBeVisible();
        await page.getByLabel('Username:').fill(username);
        await page.getByLabel('Password:').fill(password);
        await page.getByRole('button', { name: 'Login' }).click();

        await expect(page.getByRole('heading', { name: `Welcome, ${username}!` })).toBeVisible()
        await expect(page).toHaveURL("/");
        await expect(page.locator('nav span')).toHaveText(`Logged in as ${username}`);

        const storage = await page.evaluate(() => ({
            accessToken: localStorage.getItem('access_token'),
            username: localStorage.getItem('username'),
            role: localStorage.getItem('role'),
        }));

        expect(storage.accessToken).toBeTruthy();
        expect(storage.username).toBe(username);
        expect(storage.role).toBe('user');
    });

    test('admin can login and see admin page', async ({ page }) => {
        await page.goto("/")

        const username = 'admin';
        const password = 'Admin123';

        await page.getByLabel('Username:').fill(username);
        await page.getByLabel('Password:').fill(password);
        await page.getByRole('button', { name: 'Login' }).click();

        await expect(page.getByRole('heading', { name: `Welcome, ${username}!` })).toBeVisible()
        await page.getByRole('link', { name: 'Admin Dashboard' }).click();

        await expect(page.getByRole('heading', { name: 'Admin Dashboard' })).toBeVisible();
        await expect(page.getByText('Total loans')).toBeVisible();
        await expect(page.getByRole('link', { name: 'Users' })).toBeVisible();

        const storage = await page.evaluate(() => ({
            accessToken: localStorage.getItem('access_token'),
            username: localStorage.getItem('username'),
            role: localStorage.getItem('role'),
        }));

        expect(storage.accessToken).toBeTruthy();
        expect(storage.username).toBe(username);
        expect(storage.role).toBe('admin');
    });

    test('unauthenticated user is redirected to login page', async ({ page }) => {
        await page.goto("/");
        await page.getByRole('link', { name: 'Books' }).click();
        await expect(page).toHaveURL("/login");
    });

    test('user cannot access admin pages', async ({ authenticatedUserPage: page }) => {
        await page.goto("/admin/books");
        await expect(page).toHaveURL("/");
        await expect(page.getByRole('heading', { name: 'Welcome, user_' })).toBeVisible();
        await expect(page.getByRole('heading', { name: 'Admin Dashboard' })).not.toBeVisible();
    });
});
