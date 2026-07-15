import { expect, test } from '../../fixtures/authenticated.fixture';

test('CRM testing scope is listed', async ({ page }) => {
  await page.goto('/');

  await expect(page.getByRole('heading', { name: 'iFive CRM' })).toBeVisible();
  await expect(page.getByText('Opportunity')).toBeVisible();
});
