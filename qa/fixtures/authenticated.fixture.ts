import { test as base, expect } from '@playwright/test';

const projects = [
  { id: 1, name: 'iFive AutoQA Dashboard', product_code: 'AUTOQA', description: 'Local demo', base_url: null, environment: 'local', is_active: true, created_at: '2026-07-11', updated_at: '2026-07-11' },
  { id: 2, name: 'iFive ERP', product_code: 'ERP', description: 'Local demo', base_url: null, environment: 'local', is_active: true, created_at: '2026-07-11', updated_at: '2026-07-11' },
  { id: 3, name: 'iFive HRMS', product_code: 'HRMS', description: 'Local demo', base_url: null, environment: 'local', is_active: true, created_at: '2026-07-11', updated_at: '2026-07-11' },
  { id: 4, name: 'iFive CRM', product_code: 'CRM', description: 'Local demo', base_url: null, environment: 'local', is_active: true, created_at: '2026-07-11', updated_at: '2026-07-11' },
  { id: 5, name: 'iFive IIoT', product_code: 'IIOT', description: 'Local demo', base_url: null, environment: 'local', is_active: true, created_at: '2026-07-11', updated_at: '2026-07-11' },
  { id: 6, name: 'iFive Application Integration', product_code: 'INTEGRATION', description: 'Local demo', base_url: null, environment: 'local', is_active: true, created_at: '2026-07-11', updated_at: '2026-07-11' },
];
const summary = { total_projects: 6, active_projects: 6, total_runs: 0, passed_runs: 0, failed_runs: 0, queued_runs: 0, running_runs: 0, pass_rate: 0, total_tests: 0, average_duration_seconds: 0, recent_runs: [] };

export const test = base.extend<{ authenticatedApi: void }>({
  authenticatedApi: [async ({ page }, use) => {
    await page.route('**/api/auth/me', (route) => route.fulfill({ json: { id: 900, username: 'mock-admin', display_name: 'Mock Admin', role: 'ADMIN', is_active: true } }));
    await page.route('**/api/auth/csrf', (route) => route.fulfill({ json: { csrf_token: 'mock-csrf' } }));
    await page.route('**/api/operators', (route) => route.fulfill({ json: [] }));
    await page.route('**/api/audit/events?limit=50', (route) => route.fulfill({ json: [] }));
    await page.route('**/api/test-projects**', (route) => route.fulfill({ json: { items: [], page: { limit: 50, offset: 0, total: 0 } } }));
    await page.route('**/api/test-modules**', (route) => route.fulfill({ json: [] }));
    await page.route('**/api/test-suites**', (route) => route.fulfill({ json: [] }));
    await page.route('**/api/test-cases**', (route) => route.fulfill({ json: route.request().url().includes('/versions') ? [] : { items: [], page: { limit: 50, offset: 0, total: 0 } } }));
    await page.route('**/api/manual-test-runs**', (route) => route.fulfill({ json: [] }));
    await page.route('**/api/connection-targets**', (route) => route.fulfill({ json: route.request().url().includes('/versions') || route.request().url().includes('/checks') || route.request().url().includes('/credential-profiles') ? [] : { items: [], page: { limit: 50, offset: 0, total: 0 } } }));
    await page.route('**/api/connection-checks**', (route) => route.fulfill({ json: {} }));
    await page.route('**/api/automated-runs**', (route) => {
      const url = route.request().url();
      if (url.includes('/automated-runs/readiness')) return route.fulfill({ json: { active_admin_count: 0, admin_prerequisite_met: false, real_target_authorized: false, real_target_status: 'PENDING_EXPLICIT_NON_PRODUCTION_AUTHORIZATION', dns_pinning_status: 'ENFORCED', runtime_secret_status: 'PENDING_SAFE_EPHEMERAL_INPUT', allowed_risk_levels: ['READ_ONLY', 'SAFE_INTERACTION'], blocked_risk_levels: ['MUTATING', 'DESTRUCTIVE'] } });
      if (url.match(/automated-runs\/\d+\/preflight/)) return route.fulfill({ json: { run_id: 1, status: 'PENDING', checks: {}, risk_level: 'READ_ONLY', dns_pinning_status: 'ENFORCED', runtime_secret_status: 'NOT_REQUIRED', safe_message: null } });
      return route.fulfill({ json: url.match(/automated-runs\/\d+\/(cases|steps|events|artifacts)/) ? [] : { items: [], page: { limit: 50, offset: 0, total: 0 } } });
    });
    await page.route('**/api/execution-workers**', (route) => route.fulfill({ json: route.request().method() === 'GET' ? [] : null }));
    await page.route('**/api/execution-artifacts**', (route) => route.fulfill({ json: {} }));
    await page.route('**/api/projects', (route) => route.fulfill({ json: projects }));
    await page.route('**/api/dashboard/summary', (route) => route.fulfill({ json: summary }));
    await page.route('**/api/test-runs?limit=10', (route) => route.fulfill({ json: [] }));
    await use();
  }, { auto: true }],
});
export { expect };
export type { Page } from '@playwright/test';
