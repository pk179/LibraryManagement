import { test, expect } from './fixtures/fixtures';

test.describe('Books management', () => {
    test('admin can search books in admin panel', async ({ authenticatedAdminPage: page }) => {
        await page.goto('/admin/books');

        await expect(page.getByTestId('book-title').first()).toBeVisible();
        await page.getByPlaceholder('Search').fill('hobbit');
        await expect(page.getByTestId('book-title')).toHaveCount(1);
        await expect(page.getByTestId('book-title')).toHaveText(/Hobbit/);

        await page.getByPlaceholder('Search').fill('tolkien');
        const authors = page.getByTestId('book-author');
        await expect(authors).not.toHaveCount(0);
        for (const author of await authors.all())
            await expect(author).toHaveText(/Tolkien/);

        await page.getByPlaceholder('Search').fill('fantasy');
        const genres = page.getByTestId('book-genre');
        await expect(genres).not.toHaveCount(0);
        for (const genre of await genres.all())
            await expect(genre).toHaveText(/Fantasy/);
    })

    test('admin can filter unavailable books in admin panel', async ({ authenticatedAdminPage: page }) => {
        await page.goto('/admin/books');
        await expect(page.getByTestId('book-title').first()).toBeVisible();
        const quantities_before = page.getByTestId('book-quantity');
        await expect(quantities_before).not.toHaveCount(0);

        let hasUnavailable = false;
        for (const quantity of await quantities_before.all()) {
            if (await quantity.innerText() === '0') {
                hasUnavailable = true;
                break;
            }
        }
        expect(hasUnavailable).toBe(true);

        await page.getByTestId('available-checkbox').check();
        const quantities = page.getByTestId('book-quantity');
        await expect(quantities).not.toHaveCount(0);
        for (const quantity of await quantities.all())
            await expect(quantity).not.toHaveText('0');
    });

    test('admin can create a book', async ({ authenticatedAdminPage: page }, testInfo) => {
        await page.goto('/admin/books');
        await page.getByRole('button', { name: 'Add Book' }).click();
        await page.getByLabel('Title').fill(`test add title ${testInfo.project.name}-${Date.now()}`);
        await page.getByLabel('Author').fill('test add author');
        await page.getByLabel('Year').fill('2026');
        await page.getByLabel('Quantity').fill('7');

        const dialogPromise = page.waitForEvent('dialog');
        await page.getByRole('button', { name: 'Create' }).click();
        const dialog = await dialogPromise;
        expect(dialog.message()).toBe('Book created');
        await dialog.accept();

        await expect(page.getByTestId('book-title').first()).toBeVisible();
        await page.getByPlaceholder('Search').fill(`test add title ${testInfo.project.name}`);
        await expect(page.getByTestId('book-title').first()).toContainText(`test add title ${testInfo.project.name}`);
    })

    test('admin can edit book details', async ({ authenticatedAdminPage: page, backendRequest, adminToken }, testInfo) => {
        const title = `edit-test-${testInfo.project.name}-${Date.now()}`;

        const response = await backendRequest.post('/api/books', {
            headers: {
                Authorization: `Bearer ${adminToken}`,
            },
            data: {
                title,
                author: 'test author',
                year: 2026,
                quantity: 5,
                genre: 'test',
                isbn: undefined,
            },
        });

        expect(response.status()).toBe(201);

        await page.goto('/admin/books');

        await expect(page.getByTestId('book-title').first()).toBeVisible();
        await page.getByPlaceholder('Search').fill(title);
        await expect(page.getByTestId('book-title').first()).toContainText(title);

        await page.getByRole('button', { name: 'Edit' }).first().click();
        await page.getByLabel('Title').fill(`edited title ${testInfo.project.name}-${Date.now()}`);
        await page.getByLabel('Author').fill('edited author');
        await page.getByLabel('Year').fill('2025');
        await page.getByLabel('Quantity').fill('5');

        const dialogPromise = page.waitForEvent('dialog');
        await page.getByRole('button', { name: 'Update' }).click();
        const dialog = await dialogPromise;
        expect(dialog.message()).toBe('Book updated');
        await dialog.accept();

        await page.getByPlaceholder('Search').fill(`edited title ${testInfo.project.name}`);
        await expect(page.getByTestId('book-title').first()).toContainText(`edited title ${testInfo.project.name}`);
    })

    test('admin can delete a book', async ({ authenticatedAdminPage: page, backendRequest, adminToken }, testInfo) => {
        const title = `delete-test-${testInfo.project.name}-${Date.now()}`;

        const response = await backendRequest.post('/api/books', {
            headers: {
                Authorization: `Bearer ${adminToken}`,
            },
            data: {
                title,
                author: 'test author',
                year: 2026,
                quantity: 5,
                genre: 'test',
                isbn: undefined,
            },
        });

        expect(response.status()).toBe(201);

        await page.goto('/admin/books');

        await expect(page.getByTestId('book-title').first()).toBeVisible();
        await page.getByPlaceholder('Search').fill(title);
        await expect(page.getByTestId('book-title').first()).toContainText(title);

        page.on('dialog', async dialog => {
            const msg = dialog.message();

            if (msg === 'Delete this book?') {
                await dialog.accept();
            } else if (msg === 'Book deleted') {
                expect(dialog.type()).toBe('alert');
                await dialog.accept();
            }
        });

        await page.getByRole('button', { name: 'Delete', exact: true }).first().click();

        await page.getByPlaceholder('Search').fill(title);
        await expect(page.getByText('No books found.')).toBeVisible();
        await expect(page.getByTestId('book-title')).toHaveCount(0);
    })

    test('admin can bulk delete books', async ({ authenticatedAdminPage: page, backendRequest, adminToken }, testInfo) => {
        const titles: string[] = [];
        const timestamp = Date.now();

        for (let i = 0; i < 3; i++) {
            const title = `bulk-delete-test-${testInfo.project.name}-${timestamp}-${i}`;
            titles.push(title);

            const response = await backendRequest.post('/api/books', {
                headers: {
                    Authorization: `Bearer ${adminToken}`,
                },
                data: {
                    title,
                    author: 'test author',
                    year: 2026,
                    quantity: 5,
                    genre: 'test',
                    isbn: undefined,
                },
            });
            expect(response.status()).toBe(201);
        }

        await page.goto('/admin/books');

        await expect(page.getByTestId('book-title').first()).toBeVisible();
        await page.getByPlaceholder('Search').fill(`bulk-delete-test-${testInfo.project.name}-${timestamp}`);
        await expect(page.getByTestId('book-title')).toHaveCount(3);

        const checkboxes = page.getByTestId('book-checkbox');

        for (let i = 0; i < await checkboxes.count(); i++) {
            await checkboxes.nth(i).check();
            await expect(checkboxes.nth(i)).toBeChecked();
        }

        page.on('dialog', async dialog => {
            const msg = dialog.message();

            if (msg === 'Delete selected books?') {
                await dialog.accept();
            } else if (msg === 'Books deleted') {
                expect(dialog.type()).toBe('alert');
                await dialog.accept();
            }
        });

        await page.getByRole('button', { name: 'Delete Selected' }).click();

        await page.getByPlaceholder('Search').fill(`bulk-delete-test-${testInfo.project.name}-${timestamp}`);
        await expect(page.getByText('No books found.')).toBeVisible();
        await expect(page.getByTestId('book-title')).toHaveCount(0);
    })

    test('admin cannot create book with invalid data', async ({ authenticatedAdminPage: page }) => {
        await page.goto('/admin/books');

        await page.getByRole('button', { name: 'Add Book' }).click();
        await page.getByLabel('Genre').fill('test invalid data');
        await page.getByRole('button', { name: 'Create' }).click();
        await expect(page.getByLabel('Title')).toHaveJSProperty('validity.valueMissing', true);

        await expect(page.getByTestId('book-title').first()).toBeVisible();
        await page.getByPlaceholder('Search').fill('test invalid data');
        await expect(page.getByText('No books found.')).toBeVisible();
        await expect(page.getByTestId('book-title')).toHaveCount(0);

        await page.getByLabel('Title').fill('test title');
        await page.getByRole('button', { name: 'Create' }).click();
        await expect(page.getByLabel('Author')).toHaveJSProperty('validity.valueMissing', true);

        await page.getByPlaceholder('Search').fill('test title');
        await expect(page.getByText('No books found.')).toBeVisible();
        await expect(page.getByTestId('book-title')).toHaveCount(0);

        await page.getByLabel('Author').fill('test author');
        await page.getByLabel('Quantity').fill('-3');

        const dialogPromise = page.waitForEvent('dialog');
        await page.getByRole('button', { name: 'Create' }).click();
        const dialog = await dialogPromise;
        expect(dialog.message()).toBe('Quantity must be >= 0.');
        await dialog.accept();

        await page.getByPlaceholder('Search').fill('test title');
        await expect(page.getByText('No books found.')).toBeVisible();
        await expect(page.getByTestId('book-title')).toHaveCount(0);
    })

    test('admin can update book quantity', async ({ authenticatedAdminPage: page, backendRequest, adminToken }, testInfo) => {
        const title = `quantity-test-${testInfo.project.name}-${Date.now()}`;

        const response = await backendRequest.post('/api/books', {
            headers: {
                Authorization: `Bearer ${adminToken}`,
            },
            data: {
                title,
                author: 'test author',
                year: 2026,
                quantity: 5,
                genre: 'test',
                isbn: undefined,
            },
        });

        expect(response.status()).toBe(201);

        await page.goto('/admin/books');

        await expect(page.getByTestId('book-title').first()).toBeVisible();
        await page.getByPlaceholder('Search').fill(title);
        await expect(page.getByTestId('book-title').first()).toContainText(title);

        await page.getByRole('button', { name: 'Edit' }).first().click();
        await page.getByLabel('Quantity').fill('0');

        const dialogPromise = page.waitForEvent('dialog');
        await page.getByRole('button', { name: 'Update' }).click();
        const dialog = await dialogPromise;
        expect(dialog.message()).toBe('Book updated');
        await dialog.accept();

        await page.goto('/books');
        await expect(page.getByTestId('book-title').first()).toBeVisible();
        await page.getByPlaceholder('Search').fill(title);
        const row = page.getByTestId(/book-row-/);
        await expect(row).toBeVisible();
        await expect(row.getByTestId('book-title')).toHaveText(title);
        await expect(row.getByTestId('book-available')).toHaveText('No');
        await expect(row.getByTestId('book-unavailable')).toBeVisible();
        await expect(row.getByRole('button', { name: 'Borrow' })).toHaveCount(0);
    })
})