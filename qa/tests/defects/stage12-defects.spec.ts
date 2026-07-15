import { expect, test } from '@playwright/test';

const tester = { id: 2, username: 'tester', display_name: 'Tester User', role: 'TESTER', is_active: true, must_change_password: false };
const approver = { id: 3, username: 'approver', display_name: 'Approver User', role: 'APPROVER', is_active: true, must_change_password: false };
const viewer = { id: 4, username: 'viewer', display_name: 'Viewer User', role: 'VIEWER', is_active: true, must_change_password: false };
const project = { id: 1, name: 'Stage 12 Project', code: 'S12', description: null, status: 'ACTIVE', owner_operator_id: null, created_by: 3, created_at: '2026-07-13', updated_at: '2026-07-13', archived_at: null, version: 1 };
const testCase = { id: 20, project_id: 1, module_id: 1, suite_id: 1, case_key: 'S12-CASE', title: 'Defect source case', objective: null, preconditions: null, test_type: 'SMOKE', priority: 'HIGH', severity: 'HIGH', status: 'ACTIVE', lifecycle_state: 'APPROVED', owner_operator_id: null, created_by: 2, reviewed_by: 3, approved_by: 3, created_at: '2026-07-13', updated_at: '2026-07-13', reviewed_at: '2026-07-13', approved_at: '2026-07-13', archived_at: null, current_version: 2, steps: [], tags: [] };
const failedRun = { id: 7, run_key: 'ARUN-S12-FAIL', name: 'Failed local automated run', description: null, target_id: 9, target_version: 4, target_origin: 'http://127.0.0.1:4312', status: 'FAILED', risk_level: 'READ_ONLY', preflight_status: 'PASS', dns_pinning_status: 'PINNED', runtime_secret_status: 'NOT_REQUIRED', created_by: 2, submitted_by: 2, approved_by: 3, queued_by: 3, cancelled_by: null, worker_key: 'local-worker', timeout_seconds: 30, max_retries: 1, attempt_count: 1, total_steps: 1, completed_steps: 1, failed_steps: 1, failure_classification: 'ASSERTION', safe_error_message: 'Expected safe banner was absent.', created_at: '2026-07-13', updated_at: '2026-07-13', progress: '1/1' };

test('Stage 12 defect management traceability workflow', async ({ page }) => {
  let currentOperator: any = tester;
  let nextDefect = 1;
  let defects: any[] = [];
  let comments: any[] = [];
  let history: any[] = [];
  let retests: any[] = [];
  const evidence = [{ id: 1, defect_id: 1, manual_evidence_id: null, execution_artifact_id: 44, link_type: 'SOURCE', created_by: tester.id, created_at: '2026-07-13T10:00:00Z' }];

  await page.exposeFunction('setStage12Role', (role: string) => {
    currentOperator = role === 'APPROVER' ? approver : role === 'VIEWER' ? viewer : tester;
  });
  page.on('dialog', (dialog) => void dialog.accept());

  await page.route('**/api/**', async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    const path = url.pathname;
    const method = request.method();
    const body = method === 'GET' ? null : request.postDataJSON();
    if (path === '/api/auth/me') return route.fulfill({ json: currentOperator });
    if (path === '/api/auth/csrf') return route.fulfill({ json: { csrf_token: 'stage12-csrf' } });
    if (path === '/api/projects' || path.startsWith('/api/test-runs') || path.startsWith('/api/operators') || path.startsWith('/api/audit') || path.startsWith('/api/auth/sessions')) return route.fulfill({ json: [] });
    if (path === '/api/dashboard/summary') return route.fulfill({ json: { total_projects: 0, active_projects: 0, total_runs: 0, passed_runs: 0, failed_runs: 0, queued_runs: 0, running_runs: 0, pass_rate: 0, total_tests: 0, average_duration_seconds: 0, recent_runs: [] } });
    if (path.startsWith('/api/security')) return route.fulfill({ json: { active_operators: 3, locked_operators: 0, must_change_password_count: 0, active_sessions: 1, failed_logins_last_24h: 0, audit_chain_valid: true } });
    if (path === '/api/test-projects') return route.fulfill({ json: { items: [project], page: { limit: 100, offset: 0, total: 1 } } });
    if (path === '/api/test-modules' || path === '/api/test-suites' || path === '/api/manual-test-runs') return route.fulfill({ json: [] });
    if (path.startsWith('/api/test-cases')) return route.fulfill({ json: { items: [testCase], page: { limit: 100, offset: 0, total: 1 } } });
    if (path === '/api/connection-targets') return route.fulfill({ json: { items: [], page: { limit: 50, offset: 0, total: 0 } } });
    if (path.startsWith('/api/connection-targets/') || path.startsWith('/api/connection-checks')) return route.fulfill({ json: [] });
    if (path === '/api/automated-runs/readiness') return route.fulfill({ json: { active_admin_count: 0, admin_prerequisite_met: false, real_target_authorized: false, real_target_status: 'PENDING_EXPLICIT_NON_PRODUCTION_AUTHORIZATION', dns_pinning_status: 'ENFORCED', runtime_secret_status: 'NOT_REQUIRED', allowed_risk_levels: ['READ_ONLY', 'SAFE_INTERACTION'], blocked_risk_levels: ['MUTATING', 'DESTRUCTIVE'] } });
    if (path === '/api/automated-runs') return route.fulfill({ json: { items: [failedRun], page: { limit: 100, offset: 0, total: 1 } } });
    if (path === '/api/automated-runs/7/cases') return route.fulfill({ json: [{ id: 70, run_id: 7, test_case_id: testCase.id, test_case_version: 2, status: 'FAILED', failure_classification: 'ASSERTION', safe_error_message: 'Case failed safely.' }] });
    if (path.match(/\/api\/automated-runs\/\d+\/(steps|events|artifacts|preflight)/)) return route.fulfill({ json: path.endsWith('/preflight') ? { run_id: 7, status: 'PASS', checks: {}, risk_level: 'READ_ONLY', dns_pinning_status: 'PINNED', runtime_secret_status: 'NOT_REQUIRED', safe_message: null } : [] });
    if (path.startsWith('/api/execution-workers')) return route.fulfill({ json: method === 'GET' ? [] : null });
    if (path.startsWith('/api/execution-artifacts')) return route.fulfill({ json: {} });
    if (path === '/api/defects' && method === 'GET') {
      const search = url.searchParams.get('search')?.toLowerCase() ?? '';
      const status = url.searchParams.get('status') ?? '';
      const items = defects.filter((item) => (!search || item.title.toLowerCase().includes(search) || item.defect_key.toLowerCase().includes(search)) && (!status || item.status === status));
      return route.fulfill({ json: { items, page: { limit: 50, offset: 0, total: items.length } } });
    }
    if (path === '/api/defects' && method === 'POST') {
      const item = { id: nextDefect++, defect_key: `DEF-0000${nextDefect}`, description: null, module_id: null, suite_id: null, test_case_id: null, test_case_version: null, manual_run_id: null, manual_run_case_id: null, manual_step_result_id: null, automated_run_id: null, automated_run_case_id: null, automated_step_result_id: null, severity: 'MEDIUM', priority: 'MEDIUM', status: 'NEW', assigned_to: null, reporter_id: currentOperator.id, environment: 'LOCAL', target_id: null, target_version: null, failure_category: null, expected_result: null, actual_result: null, reproduction_steps: null, resolution: null, duplicate_of_defect_id: null, created_by: currentOperator.id, created_at: new Date().toISOString(), updated_at: new Date().toISOString(), closed_at: null, archived_at: null, ...body };
      defects = [item, ...defects]; history.unshift({ id: history.length + 1, defect_id: item.id, event_type: 'CREATED', old_value: null, new_value: 'NEW', safe_message: null, created_by: currentOperator.id, created_at: new Date().toISOString() });
      return route.fulfill({ status: 201, json: item });
    }
    if (path === '/api/defects/from-run') {
      if (!body.confirm) return route.fulfill({ json: { requires_confirmation: true, possible_existing: defects.slice(0, 1) } });
      const item = { id: nextDefect++, defect_key: 'DEF-S12-AUTO', title: 'Automated failure ARUN-S12-FAIL', description: null, project_id: 1, module_id: 1, suite_id: 1, test_case_id: testCase.id, test_case_version: 2, manual_run_id: null, manual_run_case_id: null, manual_step_result_id: null, automated_run_id: failedRun.id, automated_run_case_id: 70, automated_step_result_id: null, severity: 'HIGH', priority: 'HIGH', status: 'NEW', assigned_to: null, reporter_id: currentOperator.id, environment: 'LOCAL', target_id: 9, target_version: 4, failure_category: 'ASSERTION', expected_result: null, actual_result: 'Expected safe banner was absent.', reproduction_steps: '{"run_key":"ARUN-S12-FAIL"}', resolution: null, duplicate_of_defect_id: null, created_by: currentOperator.id, created_at: new Date().toISOString(), updated_at: new Date().toISOString(), closed_at: null, archived_at: null };
      defects = [item, ...defects]; history.unshift({ id: history.length + 1, defect_id: item.id, event_type: 'SOURCE_LINKED', old_value: null, new_value: 'AUTOMATED_RUN_CASE', safe_message: null, created_by: currentOperator.id, created_at: new Date().toISOString() });
      return route.fulfill({ json: item });
    }
    const defectRoute = path.match(/^\/api\/defects\/(\d+)(?:\/([\w-]+))?$/);
    if (defectRoute) {
      const id = Number(defectRoute[1]);
      const action = defectRoute[2];
      const defect = defects.find((item) => item.id === id);
      if (!defect) return route.fulfill({ status: 404, json: { detail: 'Defect not found.' } });
      if (!action && method === 'GET') return route.fulfill({ json: defect });
      if (!action && method === 'PATCH') { Object.assign(defect, body, { updated_at: new Date().toISOString() }); return route.fulfill({ json: defect }); }
      if (action === 'comments' && method === 'GET') return route.fulfill({ json: comments.filter((item) => item.defect_id === id) });
      if (action === 'comments' && method === 'POST') { const item = { id: comments.length + 1, defect_id: id, body: body.body, created_by: currentOperator.id, created_at: new Date().toISOString() }; comments.push(item); history.unshift({ id: history.length + 1, defect_id: id, event_type: 'COMMENT_ADDED', old_value: null, new_value: null, safe_message: null, created_by: currentOperator.id, created_at: new Date().toISOString() }); return route.fulfill({ status: 201, json: item }); }
      if (action === 'history') return route.fulfill({ json: history.filter((item) => item.defect_id === id) });
      if (action === 'evidence') return route.fulfill({ json: evidence });
      if (action === 'traceability') return route.fulfill({ json: { defect: { id, defect_key: defect.defect_key, status: defect.status }, project, module: { id: 1, code: 'MOD', name: 'Module', status: 'ACTIVE' }, suite: { id: 1, code: 'AUTO', name: 'Automated Suite', status: 'ACTIVE' }, test_case: { id: testCase.id, case_key: testCase.case_key, title: testCase.title, status: 'ACTIVE', lifecycle_state: 'APPROVED' }, test_case_version: 2, manual_run_id: null, manual_run_case_id: null, manual_step_result_id: null, automated_run_id: failedRun.id, automated_run_case_id: 70, automated_step_result_id: null, evidence_links: [{ manual_evidence_id: null, execution_artifact_id: 44 }], retests: retests.map((item) => ({ manual_run_id: item.manual_run_id, result_status: item.result_status, test_case_version: item.test_case_version })) } });
      if (action === 'retest') { const item = { id: retests.length + 1, defect_id: id, manual_run_id: 500 + retests.length, automated_run_id: null, test_case_id: testCase.id, test_case_version: 2, target_id: 9, target_version: 4, result_status: body.result_status, safe_notes: body.notes, created_by: currentOperator.id, created_at: new Date().toISOString() }; retests.push(item); defect.status = body.result_status === 'PASSED' ? 'RETEST_PASSED' : 'REOPENED'; return route.fulfill({ status: 201, json: item }); }
      const transitions: Record<string, string> = { triage: 'TRIAGED', assign: 'ASSIGNED', start: 'IN_PROGRESS', fix: 'FIXED', 'ready-for-retest': 'READY_FOR_RETEST', close: 'CLOSED', reject: 'REJECTED' };
      if (transitions[action]) {
        defect.status = transitions[action];
        if (action === 'assign') defect.assigned_to = body.assigned_to;
        if (action === 'close') { defect.resolution = body.resolution; defect.closed_at = new Date().toISOString(); }
        defect.updated_at = new Date().toISOString();
        history.unshift({ id: history.length + 1, defect_id: id, event_type: 'STATUS_CHANGED', old_value: null, new_value: defect.status, safe_message: body.reason ?? body.resolution ?? null, created_by: currentOperator.id, created_at: new Date().toISOString() });
        return route.fulfill({ json: defect });
      }
    }
    if (path.startsWith('/api/traceability')) return route.fulfill({ json: { defects } });
    return route.fulfill({ json: {} });
  });

  await page.goto('/');
  const panel = page.locator('#defects');
  await page.getByRole('link', { name: 'Defects' }).click();
  await panel.getByRole('button', { name: 'Create From Run' }).click();
  await expect(panel.getByText('Created DEF-S12-AUTO from failed run.')).toBeVisible();
  await expect(panel.getByRole('heading', { name: 'DEF-S12-AUTO' })).toBeVisible();
  await panel.getByRole('button', { name: 'Open' }).first().click();
  await expect(panel.getByText('Execution artifact 44')).toBeVisible();
  await expect(panel.getByText('Stage 12 Project', { exact: true })).toBeVisible();
  await panel.locator('.card', { hasText: 'Comments' }).locator('textarea').fill('Clean local investigation note.');
  await panel.getByRole('button', { name: 'Add Comment' }).click();
  await expect(panel.getByText('Clean local investigation note.')).toBeVisible();

  await page.evaluate(() => (window as any).setStage12Role('APPROVER'));
  await page.reload();
  await page.getByRole('link', { name: 'Defects' }).click();
  await panel.getByRole('button', { name: 'Open' }).first().click();
  await panel.getByRole('button', { name: 'Triage' }).click();
  await panel.getByRole('button', { name: 'Assign' }).click();
  await panel.getByRole('button', { name: 'Start' }).click();
  await panel.getByRole('button', { name: 'Fix' }).click();
  await panel.getByRole('button', { name: 'Ready' }).click();
  await expect(panel.getByRole('button', { name: 'Record Retest' })).toBeDisabled();

  await page.evaluate(() => (window as any).setStage12Role('TESTER'));
  await page.reload();
  await page.getByRole('link', { name: 'Defects' }).click();
  await panel.getByRole('button', { name: 'Open' }).first().click();
  await panel.locator('.card', { hasText: 'Retest' }).getByLabel('Notes').fill('Safe local retest passed.');
  await panel.getByRole('button', { name: 'Record Retest' }).click();
  await expect(panel.getByText('Retest recorded.')).toBeVisible();

  await page.evaluate(() => (window as any).setStage12Role('APPROVER'));
  await page.reload();
  await page.getByRole('link', { name: 'Defects' }).click();
  await panel.getByRole('button', { name: 'Open' }).first().click();
  await panel.getByLabel('Resolution or reason').fill('Fixed and retested with local evidence.');
  await panel.getByRole('button', { name: 'Close' }).click();
  await expect(panel.getByText('DEF-S12-AUTO moved to CLOSED.')).toBeVisible();
  await panel.getByLabel('Defect state').selectOption('CLOSED');
  await panel.getByRole('button', { name: 'Filter Defects' }).click();
  await expect(panel.getByRole('heading', { name: 'DEF-S12-AUTO' })).toBeVisible();

  await page.evaluate(() => (window as any).setStage12Role('VIEWER'));
  await page.reload();
  await page.getByRole('link', { name: 'Defects' }).click();
  await expect(panel.getByText('Defect creation requires TESTER or ADMIN.')).toBeVisible();
  await expect(panel.getByRole('button', { name: 'Create From Run' })).toHaveCount(0);
  for (const width of [320, 375, 768, 1024, 1440]) {
    await page.setViewportSize({ width, height: 900 });
    await expect(panel).toBeVisible();
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth);
    expect(overflow, `viewport ${width} overflow`).toBe(false);
  }
  const storage = await page.evaluate(() => JSON.stringify({ localStorage, sessionStorage }).toLowerCase());
  expect(storage).not.toContain('password');
  expect(storage).not.toContain('token');
  expect(storage).not.toContain('cookie');
});
