import { expect, test } from '../../fixtures/authenticated.fixture';

test('HRMS testing scope is listed', async ({ page }) => {
  await page.goto('/');

  await expect(page.getByRole('heading', { name: 'iFive HRMS' })).toBeVisible();
  await expect(page.getByText('Payroll Preview')).toBeVisible();
});
