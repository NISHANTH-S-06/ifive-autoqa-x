import { expect, test, type Page, type Route } from '@playwright/test';

const adminOperator = {
  id: 700,
  username: 'stage7-admin',
  display_name: 'Stage Seven Admin',
  role: 'ADMIN',
  is_active: true,
  must_change_password: false,
};

const securitySummary = {
  total_operators: 1,
  active_operators: 1,
  inactive_operators: 0,
  operators_by_role: { ADMIN: 1 },
  locked_operators: 0,
  must_change_password_count: 0,
  expired_password_count: 0,
  active_sessions: 1,
  revoked_sessions_last_24h: 0,
  failed_logins_last_24h: 0,
  successful_logins_last_24h: 1,
  password_changes_last_30d: 0,
  password_resets_last_30d: 0,
  audit_chain_valid: true,
  last_audit_verification_at: '2026-07-13T10:00:00',
};

async function routeCommonApi(page: Page, currentOperator = adminOperator) {
  await page.route('**/api/**', (route: Route) => {
    const url = route.request().url();
    if (url.includes('/api/auth/me')) return route.fulfill({ json: currentOperator });
    if (url.includes('/api/auth/csrf')) return route.fulfill({ json: { csrf_token: 'stage7-csrf' } });
    if (url.includes('/api/auth/sessions')) return route.fulfill({ json: [] });
    if (url.includes('/api/security/summary')) return route.fulfill({ json: securitySummary });
    if (url.includes('/api/security/operators')) return route.fulfill({ json: [] });
    if (url.includes('/api/operators')) return route.fulfill({ json: [] });
    if (url.includes('/api/audit/events')) return route.fulfill({ json: [] });
    if (url.includes('/api/test-projects')) return route.fulfill({ json: { items: [], page: { limit: 50, offset: 0, total: 0 } } });
    if (url.includes('/api/test-modules') || url.includes('/api/test-suites') || url.includes('/api/manual-test-runs')) return route.fulfill({ json: [] });
    if (url.includes('/api/test-cases')) return route.fulfill({ json: { items: [], page: { limit: 50, offset: 0, total: 0 } } });
    if (url.includes('/api/connection-targets')) return route.fulfill({ json: { items: [], page: { limit: 50, offset: 0, total: 0 } } });
    if (url.includes('/api/connection-checks')) return route.fulfill({ json: {} });
    if (url.includes('/api/automated-runs/readiness')) return route.fulfill({ json: { active_admin_count: 0, admin_prerequisite_met: false, real_target_authorized: false, real_target_status: 'PENDING_EXPLICIT_NON_PRODUCTION_AUTHORIZATION', dns_pinning_status: 'ENFORCED', runtime_secret_status: 'PENDING_SAFE_EPHEMERAL_INPUT', allowed_risk_levels: ['READ_ONLY', 'SAFE_INTERACTION'], blocked_risk_levels: ['MUTATING', 'DESTRUCTIVE'] } });
    if (url.match(/\/api\/automated-runs\/\d+\/preflight/)) return route.fulfill({ json: { run_id: 1, status: 'PENDING', checks: {}, risk_level: 'READ_ONLY', dns_pinning_status: 'ENFORCED', runtime_secret_status: 'NOT_REQUIRED', safe_message: null } });
    if (url.includes('/api/automated-runs')) return route.fulfill({ json: { items: [], page: { limit: 50, offset: 0, total: 0 } } });
    if (url.includes('/api/execution-workers')) return route.fulfill({ json: [] });
    if (url.includes('/api/execution-artifacts')) return route.fulfill({ json: {} });
    if (url.includes('/api/projects')) return route.fulfill({ json: [] });
    if (url.includes('/api/dashboard/summary')) return route.fulfill({ json: { total_projects: 0, active_projects: 0, total_runs: 0, passed_runs: 0, failed_runs: 0, queued_runs: 0, running_runs: 0, pass_rate: 0, total_tests: 0, average_duration_seconds: 0, recent_runs: [] } });
    if (url.includes('/api/test-runs')) return route.fulfill({ json: [] });
    return route.fulfill({ json: {} });
  });
}

test('forced password change blocks normal dashboard until password rotates', async ({ page }) => {
  let mustChange = true;
  let changeCalls = 0;
  await routeCommonApi(page, { ...adminOperator, must_change_password: true });
  await page.route('**/api/auth/me', (route) => route.fulfill({ json: { ...adminOperator, must_change_password: mustChange } }));
  await page.route('**/api/auth/change-required-password', async (route) => {
    changeCalls += 1;
    mustChange = false;
    return route.fulfill({ json: { status: 'changed' } });
  });

  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Password Change Required' })).toBeVisible();
  await page.getByLabel('Current password').fill('Current!Value123');
  await page.getByLabel('New password').fill('Fresh!Value1234');
  await page.getByLabel('Confirm password').fill('Different!Value1234');
  await page.getByRole('button', { name: 'Change Password' }).click();
  await expect(page.getByRole('alert')).toContainText('do not match');
  expect(changeCalls).toBe(0);

  await page.getByLabel('Current password').fill('Current!Value123');
  await page.getByLabel('New password').fill('Fresh!Value1234');
  await page.getByLabel('Confirm password').fill('Fresh!Value1234');
  await page.getByRole('button', { name: 'Change Password' }).click();
  await expect(page.getByRole('heading', { name: /Test Every Workflow/i })).toBeVisible();
  expect(changeCalls).toBe(1);
});

test('session and admin security panels expose empty states', async ({ page }) => {
  await routeCommonApi(page);
  await page.goto('/');

  await expect(page.getByText('No sessions to display.')).toBeVisible();
  await expect(page.getByText('No operator security records to display.')).toBeVisible();
  await expect(page.getByText('Active Operators')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Revoke Other Sessions' })).toBeDisabled();
});

test('admin security report failure can be retried', async ({ page }) => {
  let failed = false;
  await routeCommonApi(page);
  await page.route('**/api/security/summary', (route) => {
    if (!failed) {
      failed = true;
      return route.fulfill({ status: 503, json: { detail: 'Security report unavailable.' } });
    }
    return route.fulfill({ json: securitySummary });
  });

  await page.goto('/');
  const alert = page.getByRole('alert').filter({ hasText: 'Security report unavailable.' });
  await expect(alert).toBeVisible();
  await alert.getByRole('button', { name: 'Retry' }).click();
  await expect(page.getByText('Active Operators')).toBeVisible();
});
