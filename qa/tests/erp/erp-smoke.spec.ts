import { expect, test } from '../../fixtures/authenticated.fixture';

test('ERP testing scope is listed', async ({ page }) => {
  await page.goto('/');

  await expect(page.getByRole('heading', { name: 'iFive ERP' })).toBeVisible();
  await expect(page.getByText('Inventory')).toBeVisible();
});
