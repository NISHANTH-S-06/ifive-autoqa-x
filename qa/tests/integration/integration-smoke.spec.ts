import { expect, test } from '../../fixtures/authenticated.fixture';

test('integration testing scope is listed', async ({ page }) => {
  await page.goto('/');

  await expect(page.getByRole('heading', { name: 'iFive Application Integration' })).toBeVisible();
  await expect(page.getByText('Duplicate Handling')).toBeVisible();
});
