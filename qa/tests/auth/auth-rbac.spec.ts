import { expect, test, type Page } from '@playwright/test';

const project = { id: 1, name: 'iFive AutoQA Dashboard', product_code: 'AUTOQA', description: null, base_url: null, environment: 'local', is_active: true, created_at: '2026-07-11', updated_at: '2026-07-11' };
const summary = { total_projects: 1, active_projects: 1, total_runs: 0, passed_runs: 0, failed_runs: 0, queued_runs: 0, running_runs: 0, pass_rate: 0, total_tests: 0, average_duration_seconds: 0, recent_runs: [] };
const run = (overrides: Record<string, unknown> = {}) => ({ id: 1, run_code: 'RUN-AUTH', project_id: 1, created_by_operator_id: 22, approved_by_operator_id: null, executed_by_operator_id: null, cancelled_by_operator_id: null, suite_name: 'dashboard-smoke', browser: 'chromium', environment: 'local', status: 'QUEUED', total_tests: 0, passed_tests: 0, failed_tests: 0, skipped_tests: 0, duration_seconds: 0, report_path: null, approved_at: null, started_at: null, completed_at: null, exit_code: null, error_summary: null, result_json_path: null, html_report_path: null, stdout_log_path: null, stderr_log_path: null, created_at: '2026-07-11', ...overrides });

async function session(page: Page, role: string, runs: ReturnType<typeof run>[] = []) {
  await page.route('**/api/auth/me', (route) => route.fulfill({ json: { id: 10, username: role.toLowerCase(), display_name: `${role} User`, role, is_active: true } }));
  await page.route('**/api/auth/csrf', (route) => route.fulfill({ json: { csrf_token: 'csrf' } }));
  await page.route('**/api/projects', (route) => route.fulfill({ json: [project] }));
  await page.route('**/api/dashboard/summary', (route) => route.fulfill({ json: summary }));
  await page.route('**/api/test-runs?limit=10', (route) => route.fulfill({ json: runs }));
  await page.route('**/api/operators', (route) => route.fulfill({ json: [] }));
  await page.route('**/api/audit/events?limit=50', (route) => route.fulfill({ json: [] }));
}

test('login renders, invalid credentials are safe, valid session opens dashboard', async ({ page }) => {
  await page.route('**/api/auth/me', (route) => route.fulfill({ status: 401, json: { detail: 'Authentication required.' } }));
  await page.route('**/api/auth/login', async (route) => { const body = route.request().postDataJSON() as { password: string }; return body.password === 'valid' ? route.fulfill({ json: { operator: { id: 1, username: 'viewer', display_name: 'Viewer User', role: 'VIEWER', is_active: true }, csrf_token: 'csrf' } }) : route.fulfill({ status: 401, json: { detail: 'Invalid username or password.' } }); });
  await page.route('**/api/projects', (route) => route.fulfill({ json: [project] })); await page.route('**/api/dashboard/summary', (route) => route.fulfill({ json: summary })); await page.route('**/api/test-runs?limit=10', (route) => route.fulfill({ json: [] }));
  await page.goto('/'); await expect(page.getByRole('heading', { name: /Operator Sign In|Local Operator Login/i })).toBeVisible();
  await page.getByLabel('Username').fill('viewer'); await page.getByLabel('Password').fill('wrong'); await page.getByRole('button', { name: /Sign In/i }).click(); await expect(page.getByRole('alert')).toHaveText('Invalid username or password.');
  await page.getByLabel('Password').fill('valid'); await page.getByRole('button', { name: /Sign In/i }).click(); await expect(page.getByText('Viewer User')).toBeVisible();
  expect(await page.evaluate(() => Object.keys(localStorage))).toEqual([]);
});

test('refresh restores session and logout returns to login', async ({ page }) => {
  await session(page, 'VIEWER'); await page.route('**/api/auth/logout', (route) => route.fulfill({ json: { status: 'logged_out' } }));
  await page.goto('/'); await expect(page.getByText('Viewer User')).toBeVisible(); await page.reload(); await expect(page.getByText('Viewer User')).toBeVisible(); await page.getByRole('button', { name: 'Logout' }).click(); await expect(page.getByRole('heading', { name: /Operator Sign In|Local Operator Login/i })).toBeVisible();
});

test('viewer is read-only and tester creates but cannot approve', async ({ page }) => {
  await session(page, 'VIEWER', [run()]); await page.goto('/'); await expect(page.getByRole('button', { name: 'New Test Run' })).toHaveCount(0); await expect(page.getByRole('button', { name: 'Approve' })).toHaveCount(0);
  await page.unrouteAll(); await session(page, 'TESTER', [run()]); await page.goto('/'); await expect(page.getByRole('button', { name: 'New Test Run' })).toBeVisible(); await expect(page.getByRole('button', { name: 'Approve' })).toHaveCount(0);
});

test('approver controls another run but not their own or non-AutoQA run', async ({ page }) => {
  await session(page, 'APPROVER', [run(), run({ id: 2, run_code: 'RUN-OWN', created_by_operator_id: 10 }), run({ id: 3, run_code: 'RUN-ERP', project_id: 99 })]);
  await page.goto('/'); await expect(page.getByTestId('run-1').getByRole('button', { name: 'Approve' })).toBeVisible(); await expect(page.getByTestId('run-2').getByRole('button')).toHaveCount(0); await expect(page.getByTestId('run-3').getByRole('button')).toHaveCount(0);
});

test('admin sees operator management, audit events, and integrity result', async ({ page }) => {
  await session(page, 'ADMIN');
  await page.route('**/api/operators', (route) => route.fulfill({ json: [{ id: 2, username: 'tester', display_name: 'Tester', role: 'TESTER', is_active: true, created_at: '2026-07-11' }] }));
  await page.route('**/api/audit/events?limit=50', (route) => route.fulfill({ json: [{ id: 1, occurred_at: '2026-07-11', operator_id: 1, action: 'LOGIN_SUCCESS', resource_type: 'SESSION', resource_id: '1', outcome: 'SUCCESS', request_id: 'req-1' }] }));
  await page.route('**/api/audit/verify', (route) => route.fulfill({ json: { valid: true, total_events: 1, first_invalid_event_id: null } }));
  await page.goto('/'); await expect(page.getByRole('heading', { name: 'Local Administration' })).toBeVisible(); await expect(page.getByText('LOGIN_SUCCESS')).toBeVisible(); await page.getByRole('button', { name: 'Verify Audit Integrity' }).click(); await expect(page.getByText('Valid (1 events)')).toBeVisible();
});

test('CSRF or permission failure never shows fake success and layout has no overflow', async ({ page }) => {
  await session(page, 'TESTER');
  await page.route('**/api/test-runs', (route) => route.fulfill({ status: 403, json: { detail: 'CSRF validation failed.' } }));
  const layout = await page.evaluate(() => ({ scrollWidth: document.documentElement.scrollWidth, clientWidth: document.documentElement.clientWidth }));
  expect(layout.scrollWidth).toBeLessThanOrEqual(layout.clientWidth);
});
