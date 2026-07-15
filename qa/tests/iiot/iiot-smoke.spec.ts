import { expect, test } from '../../fixtures/authenticated.fixture';

test('IIoT testing scope is listed', async ({ page }) => {
  await page.goto('/');

  await expect(page.getByRole('heading', { name: 'iFive IIoT' })).toBeVisible();
  await expect(page.getByText('Data Freshness')).toBeVisible();
});
