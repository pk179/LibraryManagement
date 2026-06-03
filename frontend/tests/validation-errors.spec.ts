import { test, expect } from './fixtures/fixtures';

test.describe('Validation Errors', () => {
    test('user registration fails with duplicate username', async ({ page }) => {
        await page.goto('/register');
        await page.getByLabel('Username:').fill('user');
        await page.getByLabel('Password:').fill('User12345');
        await page.getByRole('button', { name: 'Register' }).click();
        await expect(page.getByText('Username already exists')).toBeVisible();
        await expect(page).toHaveURL('/register');
    });

    test('user registration fails with weak password', async ({ page }) => {
        await page.goto('/register');
        await page.getByLabel('Username:').fill('test_user_weak_password');
        await page.getByLabel('Password:').fill('123');
        await page.getByRole('button', { name: 'Register' }).click();
        await expect(page.getByText('Password must be at least 8 characters long.')).toBeVisible();
        await expect(page).toHaveURL('/register');

        await page.goto('/login');
        await page.getByLabel('Username:').fill('test_user_weak_password');
        await page.getByLabel('Password:').fill('123');
        await page.getByRole('button', { name: 'Login' }).click();
        await expect(page.getByText('Invalid username or password')).toBeVisible();
    });

    test('login fails with wrong password', async ({ page }) => {
        await page.goto('/login');
        await page.getByLabel('Username:').fill('user');
        await page.getByLabel('Password:').fill('123');
        await page.getByRole('button', { name: 'Login' }).click();
        await expect(page.getByText('Invalid username or password')).toBeVisible();
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

    test('user can borrow the same book twice', async ({ authenticatedUserPage: page }) => {
        await page.goto('/books');
        await expect(page.getByTestId('book-title').first()).toBeVisible();
        await page.getByPlaceholder('Search').fill('hobbit');

        const dialogPromise = page.waitForEvent('dialog');
        await page.getByRole('button', { name: 'Borrow' }).first().click();
        const dialog = await dialogPromise;
        expect(dialog.message()).toBe('Book borrowed successfully!');
        await dialog.accept();

        const dialogPromise2 = page.waitForEvent('dialog');
        await page.getByRole('button', { name: 'Borrow' }).first().click();
        const dialog2 = await dialogPromise2;
        expect(dialog2.message()).toBe('Book borrowed successfully!');
        await dialog2.accept();

        await page.goto('/my-loans');
        await expect(page.getByTestId('book-title').nth(0)).toHaveText('The Hobbit');
        await expect(page.getByTestId('book-title').nth(1)).toHaveText('The Hobbit');
    });

    test('admin cannot create a book with invalid ISBN', async ({ authenticatedAdminPage: page }) => {
        await page.goto('/admin/books');
        await page.getByRole('button', { name: 'Add Book' }).click();
        await page.getByLabel('Title').fill('test wrong isbn');
        await page.getByLabel('Author').fill('test');
        await page.getByLabel('ISBN').fill('1234567890123');

        const dialogPromise = page.waitForEvent('dialog');
        await page.getByRole('button', { name: 'Create' }).click();
        const dialog = await dialogPromise;
        expect(dialog.message()).toBe('Invalid ISBN (must be valid ISBN-10 or ISBN-13).');
        await dialog.accept();

        await page.getByPlaceholder('Search').fill('test wrong isbn');
        await expect(page.getByTestId('book-title')).toHaveCount(0);
    });
});