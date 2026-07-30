import { expect, test, type Page } from '../../fixtures/authenticated.fixture';

const projects = [{
  id: 1, name: 'iFive ERP', product_code: 'ERP', description: 'Local demo', base_url: null,
  environment: 'local', is_active: true, created_at: '2026-07-11T10:00:00', updated_at: '2026-07-11T10:00:00',
}];
const run = {
  id: 1, run_code: 'RUN-TEST', project_id: 1, suite_name: 'ERP Smoke Pack', browser: 'chromium',
  environment: 'local', status: 'QUEUED', total_tests: 0, passed_tests: 0, failed_tests: 0,
  skipped_tests: 0, duration_seconds: 0, report_path: null, started_at: null, completed_at: null,
  created_at: '2026-07-11T10:00:00',
};
const summary = {
  total_projects: 1, active_projects: 1, total_runs: 0, passed_runs: 0, failed_runs: 0,
  queued_runs: 0, running_runs: 0, pass_rate: 0, total_tests: 0, average_duration_seconds: 0, recent_runs: [],
};

async function mockApi(page: Page, runs = [] as typeof run[]) {
  await page.route('**/api/projects', (route) => route.fulfill({ json: projects }));
  await page.route('**/api/dashboard/summary', (route) => route.fulfill({ json: { ...summary, total_runs: runs.length, queued_runs: runs.length, recent_runs: runs } }));
  await page.route('**/api/test-runs?limit=10', (route) => route.fulfill({ json: runs }));
}

test('dashboard loads API projects, empty state, and has no overflow or console errors', async ({ page }) => {
  const errors: string[] = [];
  page.on('console', (message) => { if (message.type() === 'error') errors.push(message.text()); });
  await mockApi(page);
  await page.goto('/');
  await expect(page.getByRole('heading', { name: /Test Every Workflow/i })).toBeVisible();
  await expect(page.getByTestId('project-card').filter({ hasText: 'iFive ERP' })).toBeVisible();
  const layoutWidths = await page.evaluate(() => ({
    scrollWidth: document.documentElement.scrollWidth,
    clientWidth: document.documentElement.clientWidth,
  }));
  expect(layoutWidths.scrollWidth).toBeLessThanOrEqual(layoutWidths.clientWidth);
  expect(errors).toEqual([]);
});

test('loading state is visible while the API is pending', async ({ page }) => {
  await page.route('**/api/**', async (route) => {
    const url = route.request().url();
    if (url.includes('/auth/me')) return route.fulfill({ json: { id: 900, username: 'mock-admin', display_name: 'Mock Admin', role: 'ADMIN', is_active: true } });
    if (url.includes('/auth/csrf')) return route.fulfill({ json: { csrf_token: 'mock-csrf' } });
    await new Promise((resolve) => setTimeout(resolve, 500));
    return route.fulfill({ json: url.includes('projects') ? projects : url.includes('summary') ? summary : [] });
  });
  await page.goto('/');
  await expect(page.getByText('Loading dashboard…')).toBeVisible();
  await expect(page.getByText('No test runs yet. Queue a local run to get started.')).toBeVisible();
});

test('API failure is visible and retry recovers', async ({ page }) => {
  let failed = false;
  await page.route('**/api/dashboard/summary', (route) => { if (!failed) { failed = true; return route.fulfill({ status: 503, json: { detail: 'Backend unavailable.' } }); } return route.fulfill({ json: summary }); });
  await page.route('**/api/projects', (route) => route.fulfill({ json: projects }));
  await page.route('**/api/test-runs?limit=10', (route) => route.fulfill({ json: [] }));
  await page.goto('/');
  await expect(page.getByRole('alert').filter({ hasText: 'Backend unavailable.' })).toBeVisible();
  await page.getByRole('alert').filter({ hasText: 'Backend unavailable.' }).getByRole('button', { name: 'Retry' }).click();
  await expect(page.getByText('No test runs yet. Queue a local run to get started.')).toBeVisible();
});

test('new run dialog sends safe payload and displays queued result', async ({ page }) => {
  await mockApi(page);
  let payload: unknown;
  await page.route('**/api/test-runs', async (route) => { payload = route.request().postDataJSON(); await route.fulfill({ status: 201, json: run }); });
  await page.route('**/api/test-runs?limit=10', (route) => route.fulfill({ json: payload ? [run] : [] }));
  await page.goto('/');
  await page.getByRole('button', { name: 'New Test Run' }).click();
  const dialog = page.getByRole('dialog');
  await expect(dialog).toBeVisible();
  await expect(dialog.getByLabel('Environment').locator('option')).toHaveText(['local', 'qa', 'staging']);
  await expect(dialog.getByLabel('Environment').locator('option', { hasText: 'production' })).toHaveCount(0);
  await dialog.getByLabel('Suite name').fill('ERP Smoke Pack');
  await dialog.getByLabel('Environment').selectOption('qa');
  await dialog.getByRole('button', { name: 'Queue Run' }).click();
  expect(payload).toEqual({ project_id: 1, suite_name: 'ERP Smoke Pack', browser: 'chromium', environment: 'qa' });
  await expect(page.getByText('RUN-TEST')).toBeVisible();
  await expect(page.getByText('QUEUED').last()).toBeVisible();
});

test('real backend integration smoke', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByTestId('project-card').first()).toBeVisible();
  await expect(page.getByRole('button', { name: 'New Test Run' })).toBeEnabled();
});
