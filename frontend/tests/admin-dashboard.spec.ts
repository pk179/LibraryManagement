import { test, expect } from './fixtures/fixtures';

test.describe('Admin Dashboard', () => {
    test('Admin can view all loans and overdue loans', async ({ authenticatedAdminPage: page }) => {
        await page.goto('/admin/loans');

        await expect(page.getByTestId(/loan-row-/).first()).toBeVisible();
        const allLoansCount = await page.getByTestId(/loan-row-/).count();
        expect(allLoansCount).toBeGreaterThanOrEqual(6);

        await page.getByRole('button', { name: 'Overdue' }).click();
        await expect(page.getByTestId(/loan-row-/).first()).toBeVisible();
        const overdueLoansCount = await page.getByTestId(/loan-row-/).count();
        expect(overdueLoansCount).toBeGreaterThanOrEqual(5);

        expect(allLoansCount).toBeGreaterThanOrEqual(overdueLoansCount);
    });

    test('Admin can view dashboard statistics', async ({ authenticatedAdminPage: page }) => {
        await page.goto('/admin');
        await expect(page.getByText('Total loans')).toContainText(/\d+/);

        const totalLoans = Number((await page.getByText('Total loans').textContent())!.match(/\d+/)?.[0]);
        const activeLoans = Number((await page.getByText('Active').textContent())!.match(/\d+/)?.[0]);
        const overdueLoans = Number((await page.getByText('Overdue').textContent())!.match(/\d+/)?.[0]);
        const returnedLoans = Number((await page.getByText('Returned').textContent())!.match(/\d+/)?.[0]);

        expect(totalLoans).toBeGreaterThanOrEqual(6);
        expect(activeLoans).toBeGreaterThanOrEqual(5);
        expect(overdueLoans).toBeGreaterThanOrEqual(5);
        expect(returnedLoans).toBeGreaterThanOrEqual(1);
    });
});