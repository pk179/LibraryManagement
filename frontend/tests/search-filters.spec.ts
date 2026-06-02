import { test, expect } from './fixtures/fixtures';

test.describe('Search Filters', () => {
    test('user can search books by title, author or genre', async ({ authenticatedUserPage: page }) => {
        await page.goto('/books');

        await expect(page.getByTestId('book-title').first()).toBeVisible();
        await page.getByPlaceholder('Search').fill('great gatsby');
        await expect(page.getByTestId('book-title')).toHaveCount(1);
        await expect(page.getByTestId('book-title')).toHaveText(/Great Gatsby/);

        await page.getByPlaceholder('Search').fill('orwell');
        const authors = page.getByTestId('book-author');
        await expect(authors).not.toHaveCount(0);
        for (const author of await authors.all())
            await expect(author).toHaveText(/Orwell/);

        await page.getByPlaceholder('Search').fill('horror');
        const genres = page.getByTestId('book-genre');
        await expect(genres).not.toHaveCount(0);
        for (const genre of await genres.all())
            await expect(genre).toHaveText(/Horror/);
    });

    test('user can filter books by availability', async ({ authenticatedUserPage: page }) => {
        await page.goto('/books');
        await expect(page.getByTestId('book-title').first()).toBeVisible();
        const availability_before = await page.getByTestId('book-available').allInnerTexts();
        expect(availability_before.some(t => t.trim() === 'No')).toBe(true);

        await page.getByTestId('available-checkbox').check();
        await expect(page.getByTestId('book-title').first()).toBeVisible();
        const availability = await page.getByTestId('book-available').allInnerTexts();
        expect(availability.every(t => t.trim().startsWith('Yes'))).toBe(true);
        expect(availability.some(t => t.trim() === 'No')).toBe(false);
    });

    test('user can combine multiple filters', async ({ authenticatedUserPage: page }) => {
        await page.goto('/books');
        await expect(page.getByTestId(/book-row-/).first()).toBeVisible();
        await page.getByPlaceholder('Search').fill('en');
        await page.getByTestId('available-checkbox').check();
        await expect(page.getByTestId(/book-row-/).first()).toBeVisible();

        const rows = page.getByTestId(/book-row-/);
        for (const row of await rows.all()) {
            const title = await row.getByTestId('book-title').textContent();
            const author = await row.getByTestId('book-author').textContent();
            const genre = await row.getByTestId('book-genre').textContent();
            const availability = await row.getByTestId('book-available').textContent();

            const text = `${title} ${author} ${genre}`.toLowerCase();
            expect(text).toContain('en');
            expect(availability).toContain('Yes');
            expect(availability).not.toContain('No');
        }
    });

    test('user sees no results when searching for nonexistent terms', async ({ authenticatedUserPage: page }) => {
        await page.goto('/books');
        await expect(page.getByTestId(/book-row-/).first()).toBeVisible();

        await page.getByPlaceholder('Search').fill('nonsense search example');
        await expect(page.getByTestId(/book-row-/).first()).not.toBeVisible();
        await expect(page.getByText('No books found.')).toBeVisible();
    });
});