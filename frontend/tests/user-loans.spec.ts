import { test, expect } from './fixtures/fixtures';

test.describe('User loans', () => {
    test('user can borrow and return a book', async ({ authenticatedUserPage: page }) => {
        await page.goto("/books");

        const title = await page.getByTestId('book-title').first().innerText();

        const dialogPromise = page.waitForEvent('dialog');
        await page.getByRole('button', { name: 'Borrow' }).first().click();
        const dialog = await dialogPromise;
        expect(dialog.message()).toBe('Book borrowed successfully!');
        await dialog.accept();

        await page.getByRole('link', { name: 'My Loans' }).click();

        await expect(page.getByTestId('book-title').first()).toHaveText(title);
        const borrowDate = await page.getByTestId('borrow-date').first().innerText();
        expect(borrowDate).toMatch(/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$/);
        const dueDate = await page.getByTestId('due-date').first().innerText();
        expect(dueDate).toMatch(/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$/);

        const returnDialogPromise = page.waitForEvent('dialog');
        await page.getByRole('button', { name: 'Return Book' }).first().click();
        const returnDialog = await returnDialogPromise;
        expect(returnDialog.message()).toBe('Book returned successfully!');
        await returnDialog.accept();

        await expect(page.getByTestId('book-title').filter({ hasText: title })).toHaveCount(0);

        await page.getByRole('button', { name: 'Returned' }).click();
        await expect(page.getByTestId('book-title').first()).toHaveText(title);
        const returnDate = await page.getByTestId('return-date').first().innerText();
        expect(returnDate).toMatch(/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$/);
    });

    test('user can see overdue loans with calculated fine', async ({ authenticatedUserPage: page }) => {
        await page.goto("/my-loans");
        await page.getByRole('button', { name: 'Overdue' }).click();

        const dueDateText = await page.getByTestId('due-date').first().innerText();
        const dueDate = new Date(dueDateText.replace(' ', 'T'));
        expect(dueDate.getTime()).toBeLessThan(Date.now());

        const fine = await page.getByTestId('fine').first().innerText();
        expect(fine).toMatch(/^\$\d+(\.\d{2})$/);
    })

    test('user cannot borrow more than 3 books', async ({ testUser, backendRequest, testUserPage: page }) => {
        const token = testUser.token;

        for (let i = 1; i <= 3; i++) {
            const response = await backendRequest.post('/api/loans/', {
                data: { book_id: i },
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });
            expect(response.ok()).toBeTruthy();
        }

        await page.goto("/books");

        const dialogPromise = page.waitForEvent('dialog');
        await page.getByRole('button', { name: 'Borrow' }).first().click();
        const dialog = await dialogPromise;
        expect(dialog.message())
            .toBe('Maximum number of borrowed books reached (3)');
        await dialog.accept();

        await page.getByRole('link', { name: 'My Loans' }).click();
        await expect(page.getByTestId('book-title')).toHaveCount(3);
    })

    test('user cannot borrow an unavailable book', async ({ authenticatedUserPage: page }) => {
        await page.goto("/books");
        const unavailableBookRow = page.getByTestId(/book-row-/).filter({ has: page.getByTestId('book-unavailable') }).first();
        await expect(unavailableBookRow.getByTestId('book-unavailable')).toBeVisible();
        await expect(unavailableBookRow.getByRole('button', { name: 'Borrow' })).toHaveCount(0);
    })
});