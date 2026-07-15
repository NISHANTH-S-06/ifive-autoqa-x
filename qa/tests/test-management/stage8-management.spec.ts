import { expect, test, type Page, type Route } from '@playwright/test';

type Operator = { id: number; username: string; display_name: string; role: 'ADMIN' | 'TESTER' | 'APPROVER'; is_active: boolean; must_change_password: boolean };

const admin: Operator = { id: 1, username: 'admin', display_name: 'Admin User', role: 'ADMIN', is_active: true, must_change_password: false };
const tester: Operator = { id: 2, username: 'tester', display_name: 'Tester User', role: 'TESTER', is_active: true, must_change_password: false };
const approver: Operator = { id: 3, username: 'approver', display_name: 'Approver User', role: 'APPROVER', is_active: true, must_change_password: false };

async function mockStage8Api(page: Page) {
  let current = admin;
  let nextProject = 1;
  let nextModule = 1;
  let nextSuite = 1;
  let nextCase = 1;
  let nextRun = 1;
  const projects: any[] = [];
  const modules: any[] = [];
  const suites: any[] = [];
  const cases: any[] = [];
  const versions = new Map<number, any[]>();
  const runs: any[] = [];
  const runCases: any[] = [];
  const evidence: any[] = [];
  await page.exposeFunction('setStage8Role', (role: Operator['role']) => {
    current = role === 'ADMIN' ? admin : role === 'TESTER' ? tester : approver;
  });
  await page.route('**/api/**', async (route: Route) => {
    const url = new URL(route.request().url());
    const path = url.pathname;
    const method = route.request().method();
    const contentType = route.request().headers()['content-type'] ?? '';
    const body = method !== 'GET' && contentType.includes('application/json') ? route.request().postDataJSON() : null;
    if (path === '/api/auth/me') return route.fulfill({ json: current });
    if (path === '/api/auth/csrf') return route.fulfill({ json: { csrf_token: 'stage8-csrf' } });
    if (path.includes('/api/auth/sessions')) return route.fulfill({ json: [] });
    if (path.includes('/api/security/summary')) return route.fulfill({ json: { active_operators: 3, locked_operators: 0, must_change_password_count: 0, active_sessions: 1, failed_logins_last_24h: 0, audit_chain_valid: true } });
    if (path.includes('/api/security/operators')) return route.fulfill({ json: [] });
    if (path === '/api/operators' || path.includes('/api/audit/events')) return route.fulfill({ json: [] });
    if (path === '/api/projects') return route.fulfill({ json: [] });
    if (path.includes('/api/dashboard/summary')) return route.fulfill({ json: { total_projects: 0, active_projects: 0, total_runs: 0, passed_runs: 0, failed_runs: 0, queued_runs: 0, running_runs: 0, pass_rate: 0, total_tests: 0, average_duration_seconds: 0, recent_runs: [] } });
    if (path === '/api/test-runs') return route.fulfill({ json: [] });
    if (path.startsWith('/api/connection-targets')) return route.fulfill({ json: { items: [], page: { limit: 50, offset: 0, total: 0 } } });
    if (path.startsWith('/api/connection-checks')) return route.fulfill({ json: {} });
    if (path === '/api/automated-runs/readiness') return route.fulfill({ json: { active_admin_count: 0, admin_prerequisite_met: false, real_target_authorized: false, real_target_status: 'PENDING_EXPLICIT_NON_PRODUCTION_AUTHORIZATION', dns_pinning_status: 'ENFORCED', runtime_secret_status: 'PENDING_SAFE_EPHEMERAL_INPUT', allowed_risk_levels: ['READ_ONLY', 'SAFE_INTERACTION'], blocked_risk_levels: ['MUTATING', 'DESTRUCTIVE'] } });
    if (path.match(/\/api\/automated-runs\/\d+\/preflight/)) return route.fulfill({ json: { run_id: 1, status: 'PENDING', checks: {}, risk_level: 'READ_ONLY', dns_pinning_status: 'ENFORCED', runtime_secret_status: 'NOT_REQUIRED', safe_message: null } });
    if (path.startsWith('/api/automated-runs')) return route.fulfill({ json: path.match(/\/automated-runs\/\d+\/(cases|steps|events|artifacts)/) ? [] : { items: [], page: { limit: 50, offset: 0, total: 0 } } });
    if (path.startsWith('/api/execution-workers')) return route.fulfill({ json: method === 'GET' ? [] : null });
    if (path.startsWith('/api/execution-artifacts')) return route.fulfill({ json: {} });
    if (path === '/api/test-projects' && method === 'GET') return route.fulfill({ json: { items: projects, page: { limit: 50, offset: 0, total: projects.length } } });
    if (path === '/api/test-projects' && method === 'POST') {
      const item = { id: nextProject++, status: 'ACTIVE', created_by: current.id, created_at: new Date().toISOString(), updated_at: new Date().toISOString(), archived_at: null, version: 1, owner_operator_id: null, ...body };
      projects.push(item); return route.fulfill({ status: 201, json: item });
    }
    if (path === '/api/test-modules' && method === 'GET') return route.fulfill({ json: modules });
    if (path === '/api/test-modules' && method === 'POST') {
      const item = { id: nextModule++, status: 'ACTIVE', created_by: current.id, created_at: new Date().toISOString(), updated_at: new Date().toISOString(), archived_at: null, sort_order: 0, ...body };
      modules.push(item); return route.fulfill({ status: 201, json: item });
    }
    if (path === '/api/test-suites' && method === 'GET') return route.fulfill({ json: suites });
    if (path === '/api/test-suites' && method === 'POST') {
      const item = { id: nextSuite++, status: 'ACTIVE', created_by: current.id, created_at: new Date().toISOString(), updated_at: new Date().toISOString(), archived_at: null, owner_operator_id: null, suite_type: 'MANUAL', ...body };
      suites.push(item); return route.fulfill({ status: 201, json: item });
    }
    if (path === '/api/test-cases' && method === 'GET') {
      const search = url.searchParams.get('search')?.toLowerCase() ?? '';
      const state = url.searchParams.get('lifecycle_state') ?? '';
      const items = cases.filter((item) => (!search || item.title.toLowerCase().includes(search) || item.case_key.toLowerCase().includes(search)) && (!state || item.lifecycle_state === state));
      return route.fulfill({ json: { items, page: { limit: 50, offset: 0, total: items.length } } });
    }
    if (path === '/api/test-cases' && method === 'POST') {
      const item = { id: nextCase++, status: 'ACTIVE', lifecycle_state: 'DRAFT', created_by: current.id, reviewed_by: null, approved_by: null, created_at: new Date().toISOString(), updated_at: new Date().toISOString(), reviewed_at: null, approved_at: null, archived_at: null, current_version: 1, owner_operator_id: null, ...body };
      cases.push(item); versions.set(item.id, [{ id: 1, test_case_id: item.id, version_number: 1, snapshot_json: JSON.stringify(item), change_summary: 'Initial draft', created_by: current.id, created_at: new Date().toISOString(), source_state: 'DRAFT' }]);
      return route.fulfill({ status: 201, json: item });
    }
    const submit = path.match(/^\/api\/test-cases\/(\d+)\/submit$/);
    if (submit) {
      const item = cases.find((entry) => entry.id === Number(submit[1]));
      item.lifecycle_state = 'IN_REVIEW'; item.current_version += 1;
      versions.get(item.id)?.push({ id: item.current_version, test_case_id: item.id, version_number: item.current_version, snapshot_json: JSON.stringify(item), change_summary: 'Submitted', created_by: current.id, created_at: new Date().toISOString(), source_state: 'IN_REVIEW' });
      return route.fulfill({ json: item });
    }
    const approve = path.match(/^\/api\/test-cases\/(\d+)\/approve$/);
    if (approve) {
      const item = cases.find((entry) => entry.id === Number(approve[1]));
      if (item.created_by === current.id) return route.fulfill({ status: 400, json: { detail: 'Creators cannot approve their own test cases.' } });
      item.lifecycle_state = 'APPROVED'; item.approved_by = current.id; item.current_version += 1;
      versions.get(item.id)?.push({ id: item.current_version, test_case_id: item.id, version_number: item.current_version, snapshot_json: JSON.stringify(item), change_summary: 'Approved', created_by: current.id, created_at: new Date().toISOString(), source_state: 'APPROVED' });
      return route.fulfill({ json: item });
    }
    const versionMatch = path.match(/^\/api\/test-cases\/(\d+)\/versions$/);
    if (versionMatch) return route.fulfill({ json: versions.get(Number(versionMatch[1])) ?? [] });
    if (path === '/api/manual-test-runs' && method === 'GET') return route.fulfill({ json: runs });
    if (path === '/api/manual-test-runs' && method === 'POST') {
      const run = { id: nextRun++, run_key: 'MRUN-STAGE8', status: 'PLANNED', created_by: current.id, assigned_to: current.id, started_at: null, completed_at: null, created_at: new Date().toISOString(), updated_at: new Date().toISOString(), progress: '0/1', ...body };
      runs.push(run);
      runCases.push({ id: 1, run_id: run.id, test_case_id: body.case_ids[0], test_case_version: cases.find((item) => item.id === body.case_ids[0])?.current_version ?? 1, status: 'NOT_RUN', assigned_to: current.id, started_at: null, completed_at: null, actual_result: null, notes: null, executed_by: null });
      return route.fulfill({ status: 201, json: run });
    }
    const start = path.match(/^\/api\/manual-test-runs\/(\d+)\/start$/);
    if (start) { const run = runs.find((item) => item.id === Number(start[1])); run.status = 'IN_PROGRESS'; return route.fulfill({ json: run }); }
    const complete = path.match(/^\/api\/manual-test-runs\/(\d+)\/complete$/);
    if (complete) { const run = runs.find((item) => item.id === Number(complete[1])); run.status = 'COMPLETED'; return route.fulfill({ json: run }); }
    const runCaseList = path.match(/^\/api\/manual-test-runs\/(\d+)\/cases$/);
    if (runCaseList) return route.fulfill({ json: runCases.filter((item) => item.run_id === Number(runCaseList[1])) });
    const runCaseUpdate = path.match(/^\/api\/manual-test-runs\/(\d+)\/cases\/(\d+)$/);
    if (runCaseUpdate) { const item = runCases.find((entry) => entry.id === Number(runCaseUpdate[2])); Object.assign(item, body, { executed_by: current.id }); return route.fulfill({ json: item }); }
    const stepUpdate = path.match(/^\/api\/manual-test-runs\/(\d+)\/cases\/(\d+)\/steps\/(\d+)$/);
    if (stepUpdate) return route.fulfill({ json: { id: 1, run_case_id: Number(stepUpdate[2]), step_number: Number(stepUpdate[3]), status: body.status, actual_result: body.actual_result, notes: body.notes, executed_at: new Date().toISOString(), executed_by: current.id } });
    const evidenceList = path.match(/^\/api\/manual-test-runs\/(\d+)\/cases\/(\d+)\/evidence$/);
    if (evidenceList && method === 'GET') return route.fulfill({ json: evidence });
    if (evidenceList && method === 'POST') return route.fulfill({ status: 422, json: { detail: 'Evidence file type is not allowed.' } });
    return route.fulfill({ json: {} });
  });
}

test('Stage 8 controlled test management workflow', async ({ page }) => {
  const errors: string[] = [];
  page.on('console', (message) => { if (message.type() === 'error' && !message.text().includes('status of 422')) errors.push(message.text()); });
  await mockStage8Api(page);
  await page.goto('/');
  await page.getByRole('link', { name: /Test Management/i }).click();
  await page.getByLabel('Project name').fill('Stage 8 UI Project');
  await page.getByLabel('Project code').fill('S8UI');
  await page.getByRole('button', { name: 'Create Project' }).click();
  await expect(page.getByText('Project created.')).toBeVisible();
  await page.getByLabel('Module name').fill('Login Module');
  await page.getByLabel('Module code').fill('LOGIN');
  await page.getByRole('button', { name: 'Create Module' }).click();
  await page.getByLabel('Suite name').fill('Manual Suite');
  await page.getByLabel('Suite code').fill('MANUAL');
  await page.getByRole('button', { name: 'Create Suite' }).click();

  await page.getByRole('button', { name: 'Test Cases' }).click();
  await page.getByLabel('Case key').fill('S8-UI-001');
  await page.getByLabel('Title').fill('Manual login is verified');
  await page.getByLabel('Objective').fill('Confirm the manual workflow can be tracked.');
  await page.getByLabel('Preconditions').fill('Local dashboard is available.');
  await page.getByLabel('Action 1').fill('Open the local dashboard.');
  await page.getByLabel('Expected result 1').fill('Dashboard appears.');
  await page.getByLabel('Action 2').fill('Inspect the test-management section.');
  await page.getByLabel('Expected result 2').fill('Section is usable.');
  await page.getByRole('button', { name: 'Add Step' }).click();
  await page.getByLabel('Action 3').fill('Record a manual result.');
  await page.getByLabel('Expected result 3').fill('Result is saved.');
  await page.getByRole('button', { name: 'Down' }).first().click();
  await page.getByRole('button', { name: 'Remove' }).last().click();
  await page.getByRole('button', { name: 'Create Draft' }).click();
  await expect(page.getByText('Test case draft created.')).toBeVisible();
  await page.getByRole('button', { name: 'Submit' }).click();
  await expect(page.getByRole('button', { name: 'Self Approval Blocked' })).toBeDisabled();

  await page.evaluate(() => (window as any).setStage8Role('APPROVER'));
  await page.reload();
  await page.getByRole('button', { name: 'Review' }).click();
  await page.getByRole('button', { name: 'Approve' }).click();
  await page.getByRole('button', { name: 'Test Cases' }).click();
  await page.getByRole('button', { name: 'Versions' }).click();
  const versionDialog = page.getByRole('dialog', { name: 'Version History' });
  await expect(versionDialog).toBeVisible();
  await expect(versionDialog.locator('span').filter({ hasText: /^APPROVED$/ })).toBeVisible();
  await page.getByRole('button', { name: 'Close' }).click();
  await page.getByLabel('Search').fill('login');
  await page.getByRole('button', { name: 'Apply' }).click();
  await expect(page.getByText('S8-UI-001')).toBeVisible();

  await page.evaluate(() => (window as any).setStage8Role('TESTER'));
  await page.reload();
  await page.getByRole('button', { name: 'Manual Runs' }).click();
  await page.getByLabel('Run name').fill('Stage 8 Manual Run');
  await page.getByLabel(/S8-UI-001/).check();
  await page.getByRole('button', { name: 'Create Manual Run' }).click();
  await expect(page.getByText('Manual run created.')).toBeVisible();
  await page.getByRole('button', { name: 'Start' }).click();
  await page.getByRole('button', { name: 'Open' }).click();
  await page.getByLabel('Actual result').fill('All expected UI states were visible.');
  await page.getByRole('button', { name: 'Save Progress' }).click();
  await expect(page.getByText('Manual result saved.')).toBeVisible();
  await page.getByLabel('Evidence').setInputFiles({ name: 'bad.exe', mimeType: 'application/octet-stream', buffer: Buffer.from('MZ') });
  await expect(page.getByRole('alert').filter({ hasText: 'Evidence file type is not allowed.' })).toBeVisible();
  await page.getByRole('button', { name: 'Complete' }).click();
  await expect(page.getByText('COMPLETED')).toBeVisible();

  for (const width of [320, 375, 768, 1024, 1440]) {
    await page.setViewportSize({ width, height: 900 });
    await expect(page.locator('#test-management')).toBeVisible();
    const overflow = await page.evaluate(() => Array.from(document.querySelectorAll('body *')).map((element) => {
      const rect = element.getBoundingClientRect();
      return { tag: element.tagName, className: String(element.getAttribute('class') ?? ''), text: String(element.textContent ?? '').trim().slice(0, 60), left: Math.floor(rect.left), right: Math.ceil(rect.right) };
    }).filter((item) => item.right > document.documentElement.clientWidth || item.left < 0).slice(0, 8));
    expect(overflow, `viewport ${width} overflow`).toEqual([]);
  }

  const storage = await page.evaluate(() => `${JSON.stringify(localStorage)} ${JSON.stringify(sessionStorage)}`.toLowerCase());
  expect(storage).not.toContain('password');
  expect(storage).not.toContain('bearer');
  expect(storage).not.toContain('csrf');
  expect(errors).toEqual([]);
});
