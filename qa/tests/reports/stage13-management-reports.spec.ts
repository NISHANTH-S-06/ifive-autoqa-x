import { expect, test, type Page, type Route } from '@playwright/test';

type Role = 'ADMIN' | 'VIEWER';

const admin = { id: 1, username: 'admin', display_name: 'Admin User', role: 'ADMIN', is_active: true, must_change_password: false };
const viewer = { id: 4, username: 'viewer', display_name: 'Viewer User', role: 'VIEWER', is_active: true, must_change_password: false };

const emptyDashboard = { total_projects: 0, active_projects: 0, total_runs: 0, passed_runs: 0, failed_runs: 0, queued_runs: 0, running_runs: 0, pass_rate: 0, total_tests: 0, average_duration_seconds: 0, recent_runs: [] };
const pageInfo = { limit: 50, offset: 0, total: 0 };

async function mockStage13Api(page: Page) {
  let role: Role = 'ADMIN';
  let nextExport = 1;
  let nextDefinition = 1;
  const exports: any[] = [];
  const definitions: any[] = [];
  const requestedFilters: string[] = [];

  await page.exposeFunction('setStage13Role', (nextRole: Role) => { role = nextRole; });
  await page.exposeFunction('stage13RequestedFilters', () => requestedFilters);

  await page.route('**/api/**', async (route: Route) => {
    const request = route.request();
    const url = new URL(request.url());
    const path = url.pathname;
    const method = request.method();
    const body = method === 'GET' ? null : request.postDataJSON();
    const operator = role === 'ADMIN' ? admin : viewer;

    if (path === '/api/auth/me') return route.fulfill({ json: operator });
    if (path === '/api/auth/csrf') return route.fulfill({ json: { csrf_token: 'stage13-csrf' } });
    if (path === '/api/projects') return route.fulfill({ json: [] });
    if (path === '/api/dashboard/summary') return route.fulfill({ json: emptyDashboard });
    if (path.startsWith('/api/test-runs')) return route.fulfill({ json: [] });
    if (path.startsWith('/api/operators') || path.startsWith('/api/audit') || path.startsWith('/api/auth/sessions')) return route.fulfill({ json: [] });
    if (path.startsWith('/api/security')) return route.fulfill({ json: { active_operators: 2, locked_operators: 0, must_change_password_count: 0, active_sessions: 1, failed_logins_last_24h: 0, audit_chain_valid: true } });
    if (path === '/api/test-projects') return route.fulfill({ json: { items: [], page: pageInfo } });
    if (path === '/api/test-modules' || path === '/api/test-suites' || path === '/api/manual-test-runs') return route.fulfill({ json: [] });
    if (path.startsWith('/api/test-cases')) return route.fulfill({ json: { items: [], page: pageInfo } });
    if (path === '/api/connection-targets') return route.fulfill({ json: { items: [], page: pageInfo } });
    if (path.startsWith('/api/connection-targets/') || path.startsWith('/api/connection-checks')) return route.fulfill({ json: [] });
    if (path === '/api/automated-runs/readiness') return route.fulfill({ json: { active_admin_count: 0, admin_prerequisite_met: false, real_target_authorized: false, real_target_status: 'PENDING_EXPLICIT_NON_PRODUCTION_AUTHORIZATION', dns_pinning_status: 'ENFORCED', runtime_secret_status: 'NOT_REQUIRED', allowed_risk_levels: ['READ_ONLY', 'SAFE_INTERACTION'], blocked_risk_levels: ['MUTATING', 'DESTRUCTIVE'] } });
    if (path.startsWith('/api/automated-runs')) return route.fulfill({ json: path.match(/\/automated-runs\/\d+\/(cases|steps|events|artifacts)/) ? [] : { items: [], page: pageInfo } });
    if (path.startsWith('/api/execution-workers')) return route.fulfill({ json: method === 'GET' ? [] : null });
    if (path.startsWith('/api/execution-artifacts')) return route.fulfill({ json: {} });
    if (path === '/api/defects') return route.fulfill({ json: { items: [], page: pageInfo } });
    if (path.startsWith('/api/defects/') || path.startsWith('/api/traceability')) return route.fulfill({ json: {} });

    if (path === '/api/reports/summary') return route.fulfill({ json: [{ label: 'Pass Rate', value: '82%' }, { label: 'Open Defects', value: '5' }] });
    if (path.startsWith('/api/reports/')) requestedFilters.push(url.search);
    if (path === '/api/reports/dashboard') return route.fulfill({ json: { filters: Object.fromEntries(url.searchParams), summary: { test_projects: 2, test_cases: 14, approved_test_cases: 11, manual_runs: 5, automated_runs: 7, result_counts: { PASSED: 15, FAILED: 4, BLOCKED: 2, SKIPPED: 1 }, defects: 6, open_defects: 4, closed_defects: 1, duplicate_defects: 1, retest_results: { PASSED: 2, FAILED: 1 }, target_health: { REACHABLE: 2, FAILED: 1 }, worker_status: { IDLE: 1, OFFLINE: 1 } }, recent_activity: [] } });
    if (path === '/api/reports/executions') return route.fulfill({ json: { manual: { run_count: 5, case_statuses: { PASSED: 8, BLOCKED: 2 } }, automated: { run_count: 7, case_statuses: { PASSED: 7, FAILED: 4 }, failure_categories: { ASSERTION: 3, TIMEOUT: 1 } }, project_results: [{ project_id: 1, project_name: 'Stage 13 Project', passed: 15, failed: 4 }], operator_execution: [{ operator_id: 2, display_name: 'Tester User', run_count: 5 }], environment_results: [{ environment: 'LOCAL', passed: 15, failed: 4 }] } });
    if (path === '/api/reports/defects') return route.fulfill({ json: { by_status: { NEW: 2, TRIAGED: 1, CLOSED: 1, DUPLICATE: 1 }, by_severity: { HIGH: 3, MEDIUM: 2, LOW: 1 }, by_priority: { P1: 1, P2: 3, P3: 2 }, by_project: [{ project_id: 1, project_name: 'Stage 13 Project', defect_count: 6 }], ageing: { '0-7': 3, '8-30': 2, '31+': 1 }, reopened: 1, duplicates: 1, retest_results: { PASSED: 2, FAILED: 1 }, average_time_to_close_hours: 4, traceability: [] } });
    if (path === '/api/reports/trends') return route.fulfill({ json: { filters: Object.fromEntries(url.searchParams), execution_trend: [{ date: '2026-07-13', passed: 4, failed: 1 }], defect_trend: [{ date: '2026-07-13', opened: 2, closed: 1 }], quality_trend: [{ date: '2026-07-13', pass_percentage: 82 }] } });
    if (path === '/api/reports/quality') return route.fulfill({ json: { pass_percentage: 82, failure_percentage: 18, blocked_percentage: 5, skipped_percentage: 2, test_coverage_count: 14, approved_test_case_percentage: 78, automation_coverage: 50, defect_density: 42, defect_reopen_rate: 16, retest_success_rate: 66 } });
    if (path === '/api/reports/traceability') return route.fulfill({ json: { items: [{ defect_id: 9, defect_key: 'DEF-S13', status: 'NEW', project_id: 1, test_case_id: 14, test_case_version: 3, automated_run_id: 7, evidence_count: 1, artifact_count: 1 }] } });
    if (path === '/api/reports/targets') return route.fulfill({ json: { target_health: { REACHABLE: 2, BLOCKED: 1 }, target_lifecycle: { APPROVED: 2 }, execution_enabled: { true: 1, false: 1 }, credential_profile_counts: { METADATA_ONLY: 2 }, filters: Object.fromEntries(url.searchParams) } });
    if (path === '/api/reports/workers') return route.fulfill({ json: { status_counts: { IDLE: 1, OFFLINE: 1 }, heartbeat_health: { HEALTHY: 1, STALE: 1 }, lease_health: { ACTIVE: 0, STALE: 0 } } });
    if (path === '/api/reports/exports' && method === 'GET') return route.fulfill({ status: role === 'ADMIN' ? 200 : 403, json: role === 'ADMIN' ? { items: exports } : { detail: 'ADMIN required.' } });
    if (path === '/api/reports/export' && method === 'POST') {
      expect(JSON.stringify(body).toLowerCase()).not.toContain('password');
      expect(JSON.stringify(body).toLowerCase()).not.toContain('token');
      if (role !== 'ADMIN') return route.fulfill({ status: 403, json: { detail: 'ADMIN required.' } });
      const created = { id: nextExport++, export_key: `RPT-S13-${nextExport}`, report_type: body.report_type, export_format: body.export_format, original_filename: 'stage13-report.csv', mime_type: 'text/csv', size_bytes: 120, sha256: 'abcdef123456abcdef123456abcdef123456abcdef123456abcdef123456abcd', row_count: 24, created_by: admin.id, created_at: '2026-07-13T10:00:00Z', expires_at: null };
      exports.unshift(created);
      return route.fulfill({ status: 201, json: created });
    }
    if (path.match(/^\/api\/reports\/exports\/\d+\/download$/)) return route.fulfill({ body: "case_key,title\n'=S13,Safe local report\n", headers: { 'content-type': 'text/csv' } });
    if (path === '/api/report-definitions' && method === 'GET') return route.fulfill({ status: role === 'ADMIN' ? 200 : 403, json: role === 'ADMIN' ? definitions : { detail: 'ADMIN required.' } });
    if (path === '/api/report-definitions' && method === 'POST') {
      if (role !== 'ADMIN') return route.fulfill({ status: 403, json: { detail: 'ADMIN required.' } });
      const created = { id: nextDefinition++, name: body.name, report_type: body.report_type, filters: body.filters, frequency: body.frequency, enabled: true, owner_operator_id: admin.id, last_run_at: null, next_run_at: '2026-07-14T10:00:00Z', last_error: null };
      definitions.unshift(created);
      return route.fulfill({ status: 201, json: created });
    }
    const definitionRun = path.match(/^\/api\/report-definitions\/(\d+)\/run$/);
    if (definitionRun) {
      const created = { id: nextExport++, export_key: `RPT-SAVED-${nextExport}`, report_type: 'quality', export_format: 'csv', original_filename: 'saved-report.csv', mime_type: 'text/csv', size_bytes: 80, sha256: '123456abcdef123456abcdef123456abcdef123456abcdef123456abcdefabcd', row_count: 10, created_by: admin.id, created_at: '2026-07-13T11:00:00Z', expires_at: null };
      exports.unshift(created);
      return route.fulfill({ json: created });
    }
    const definitionDisable = path.match(/^\/api\/report-definitions\/(\d+)\/disable$/);
    if (definitionDisable) {
      const item = definitions.find((entry) => entry.id === Number(definitionDisable[1]));
      if (item) item.enabled = false;
      return route.fulfill({ json: item });
    }
    return route.fulfill({ json: {} });
  });
}

test('Stage 13 management reports dashboard exports and role boundaries', async ({ page }) => {
  const errors: string[] = [];
  page.on('console', (message) => { if (message.type() === 'error' && !message.text().includes('status of 403')) errors.push(message.text()); });
  await mockStage13Api(page);

  await page.goto('/');
  await expect(page.getByRole('link', { name: 'Management Reports' })).toBeVisible();
  const panel = page.locator('#management-reports');
  await panel.scrollIntoViewIfNeeded();
  await expect(panel.getByRole('heading', { name: 'Management Reports' })).toBeVisible();
  await expect(panel.getByText('Projects')).toBeVisible();
  await expect(panel.getByText('Execution Results')).toBeVisible();
  await expect(panel.getByRole('heading', { name: 'Defect Status' })).toBeVisible();
  await expect(panel.getByText('DEF-S13')).toBeVisible();

  await panel.getByLabel('Report date range').selectOption('last_7_days');
  await panel.getByLabel('Report project id').fill('1');
  await panel.getByRole('button', { name: 'Refresh Reports' }).click();
  await expect.poll(async () => (await page.evaluate(() => (window as any).stage13RequestedFilters())).some((item: string) => item.includes('project_id=1') && item.includes('last_7_days'))).toBe(true);

  await panel.getByLabel('Export report type').selectOption('quality');
  await panel.getByLabel('Export format').selectOption('csv');
  await panel.getByRole('button', { name: 'Create Report Export' }).click();
  await expect(panel.getByText(/Report export RPT-S13-/)).toBeVisible();
  await expect(panel.getByRole('link', { name: 'Download' }).first()).toHaveAttribute('href', /\/api\/reports\/exports\/\d+\/download/);

  await panel.getByLabel('Saved report name').fill('Daily quality rollup');
  await panel.getByLabel('Saved report type').selectOption('quality');
  await panel.getByLabel('Saved report frequency').selectOption('DAILY');
  await panel.getByRole('button', { name: 'Save Report Definition' }).click();
  await expect(panel.getByText('Saved report definition created.')).toBeVisible();
  await panel.getByRole('button', { name: 'Run Now' }).click();
  await expect(panel.getByText(/Saved report generated RPT-SAVED-/)).toBeVisible();
  await panel.getByRole('button', { name: 'Disable' }).click();
  await expect(panel.getByText('Saved report disabled.')).toBeVisible();

  for (const width of [320, 375, 768, 1024, 1440]) {
    await page.setViewportSize({ width, height: 900 });
    await expect(panel).toBeVisible();
    const overflow = await page.evaluate(() => Array.from(document.querySelectorAll('body *')).map((element) => {
      const rect = element.getBoundingClientRect();
      return { tag: element.tagName, className: String(element.getAttribute('class') ?? ''), text: String(element.textContent ?? '').trim().slice(0, 60), left: Math.floor(rect.left), right: Math.ceil(rect.right) };
    }).filter((item) => item.right > document.documentElement.clientWidth || item.left < 0).slice(0, 8));
    expect(overflow, `viewport ${width} overflow`).toEqual([]);
  }

  await page.evaluate(() => (window as any).setStage13Role('VIEWER'));
  await page.reload();
  await panel.scrollIntoViewIfNeeded();
  await expect(panel.getByText('Report exports and saved definitions require ADMIN.')).toBeVisible();
  await expect(panel.getByRole('button', { name: 'Create Report Export' })).toHaveCount(0);

  const panelText = (await panel.innerText()).toLowerCase();
  expect(panelText).not.toContain('d:\\');
  expect(panelText).not.toContain('password');
  expect(panelText).not.toContain('token');
  expect(panelText).not.toContain('cookie');
  const storage = await page.evaluate(() => `${JSON.stringify(localStorage)} ${JSON.stringify(sessionStorage)}`.toLowerCase());
  expect(storage).not.toContain('password');
  expect(storage).not.toContain('bearer');
  expect(storage).not.toContain('csrf');
  expect(errors).toEqual([]);
});
