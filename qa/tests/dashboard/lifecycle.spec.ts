import { expect, test, type Page } from '../../fixtures/authenticated.fixture';

const projects = [
  { id: 1, name: 'iFive AutoQA Dashboard', product_code: 'AUTOQA', description: null, base_url: null, environment: 'local', is_active: true, created_at: '2026-07-11', updated_at: '2026-07-11' },
  { id: 2, name: 'iFive ERP', product_code: 'ERP', description: null, base_url: null, environment: 'local', is_active: true, created_at: '2026-07-11', updated_at: '2026-07-11' },
];

const makeRun = (overrides: Record<string, unknown> = {}) => ({
  id: 11, run_code: 'RUN-LIFECYCLE', project_id: 1, suite_name: 'dashboard-smoke', browser: 'chromium', environment: 'local', status: 'QUEUED',
  total_tests: 0, passed_tests: 0, failed_tests: 0, skipped_tests: 0, duration_seconds: 0, report_path: null,
  approved_at: null, started_at: null, completed_at: null, exit_code: null, error_summary: null,
  result_json_path: null, html_report_path: null, stdout_log_path: null, stderr_log_path: null,
  created_at: '2026-07-11T10:00:00', results: [], evidence: [], ...overrides,
});
const summary = { total_projects: 2, active_projects: 2, total_runs: 1, passed_runs: 0, failed_runs: 0, queued_runs: 1, running_runs: 0, pass_rate: 0, total_tests: 0, average_duration_seconds: 0, recent_runs: [] };

async function baseRoutes(page: Page, runs: ReturnType<typeof makeRun>[]) {
  await page.route('**/api/projects', (route) => route.fulfill({ json: projects }));
  await page.route('**/api/dashboard/summary', (route) => route.fulfill({ json: summary }));
  await page.route('**/api/test-runs?limit=10', (route) => route.fulfill({ json: runs }));
}

test('queued AutoQA shows approval while non-AutoQA has no controls', async ({ page }) => {
  await baseRoutes(page, [makeRun(), makeRun({ id: 12, run_code: 'RUN-ERP', project_id: 2 })]);
  await page.goto('/');
  await expect(page.getByTestId('run-11').getByRole('button', { name: 'Approve' })).toBeVisible();
  await expect(page.getByTestId('run-12').getByRole('button')).toHaveCount(0);
});

test('incorrect confirmation is surfaced and correct confirmation approves', async ({ page }) => {
  await baseRoutes(page, [makeRun()]);
  await page.route('**/api/test-runs/11/approve', async (route) => {
    const body = route.request().postDataJSON() as { confirmation: string };
    if (body.confirmation !== 'APPROVE LOCAL TEST EXECUTION') return route.fulfill({ status: 400, json: { detail: 'Exact local execution confirmation is required.' } });
    return route.fulfill({ json: makeRun({ status: 'APPROVED', approved_at: '2026-07-11T10:01:00' }) });
  });
  await page.goto('/');
  await page.getByRole('button', { name: 'Approve' }).click();
  await page.getByLabel('Safety confirmation').fill('wrong');
  await page.getByRole('button', { name: 'Approve Run' }).click();
  await expect(page.getByRole('alert')).toContainText('Exact local execution confirmation is required.');
  await page.getByLabel('Safety confirmation').fill('APPROVE LOCAL TEST EXECUTION');
  await page.getByRole('button', { name: 'Approve Run' }).click();
  await expect(page.getByTestId('run-11').getByText('APPROVED', { exact: true })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Execute Locally' })).toBeVisible();
});

test('execute displays running, disables duplicate, polls to passed, and renders evidence', async ({ page }) => {
  await baseRoutes(page, [makeRun({ status: 'APPROVED' })]);
  await page.route('**/api/test-runs/11/execute', (route) => route.fulfill({ status: 202, json: { run_id: 11, status: 'ACCEPTED' } }));
  let polls = 0;
  await page.route('**/api/test-runs/11', (route) => {
    polls += 1;
    return route.fulfill({ json: makeRun({ status: 'PASSED', total_tests: 5, passed_tests: 5, duration_seconds: 2.1, evidence: [{ id: 7, evidence_type: 'HTML_REPORT', relative_path: 'safe', file_size_bytes: 100 }] }) });
  });
  await page.goto('/');
  await page.getByRole('button', { name: 'Execute Locally' }).click();
  await expect(page.getByText('RUNNING')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Execute Locally' })).toHaveCount(0);
  await expect(page.getByText('PASSED').first()).toBeVisible({ timeout: 5000 });
  await expect(page.getByText('Total 5')).toBeVisible();
  await expect(page.getByRole('link', { name: 'HTML_REPORT' })).toBeVisible();
  const completedPolls = polls;
  await page.waitForTimeout(2800);
  expect(polls).toBe(completedPolls);
});

test('failed result and API failure never display fake success', async ({ page }) => {
  await baseRoutes(page, [makeRun({ status: 'RUNNING' })]);
  await page.route('**/api/test-runs/11', (route) => route.fulfill({ json: makeRun({ status: 'FAILED', total_tests: 1, failed_tests: 1, error_summary: 'Local Playwright execution reported test failures.' }) }));
  await page.goto('/');
  await expect(page.getByText('Local Playwright execution reported test failures.')).toBeVisible({ timeout: 5000 });
  await expect(page.getByTestId('run-11').getByText('PASSED', { exact: true })).toHaveCount(0);
});

test('running test can be cancelled and production remains unavailable', async ({ page }) => {
  await baseRoutes(page, [makeRun({ status: 'RUNNING' })]);
  await page.route('**/api/test-runs/11/cancel', (route) => route.fulfill({ json: makeRun({ status: 'CANCELLED', completed_at: '2026-07-11T10:03:00' }) }));
  await page.route('**/api/test-runs/11', (route) => route.fulfill({ json: makeRun({ status: 'RUNNING' }) }));
  await page.goto('/');
  await page.getByRole('button', { name: 'Cancel' }).click();
  await expect(page.getByText('CANCELLED')).toBeVisible();
  await page.getByRole('button', { name: 'New Test Run' }).click();
  await expect(page.getByLabel('Environment').locator('option')).toHaveText(['local', 'qa', 'staging']);
});
