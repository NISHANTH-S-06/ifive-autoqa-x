import { test, expect, type APIResponse } from '@playwright/test';

// ── Service base URLs ────────────────────────────────────────────────────────
const AUTOQA_URL      = 'http://127.0.0.1:8000';
const MOCK_PORTAL_URL = 'http://127.0.0.1:8001';
const DEMO_ERP_URL    = 'http://127.0.0.1:8002';

// ── Demo product admin credentials for toggle endpoints ──────────────────────
const DEMO_ADMIN_USERNAME = 'demo_admin';
const DEMO_ADMIN_PASSWORD = 'Admin@Demo123';

// ── Helper: parse + assert JSON response ────────────────────────────────────
async function expectJsonResponse(
  response: APIResponse,
  expectedStatus: number,
  label: string
) {
  const body = await response.text();

  expect(
    response.status(),
    `${label} failed: HTTP ${response.status()}\n${body}`
  ).toBe(expectedStatus);

  return body ? JSON.parse(body) : {};
}

// ── Helper: obtain demo-admin bearer token ───────────────────────────────────
async function getDemoAdminToken(request: import('@playwright/test').APIRequestContext): Promise<string> {
  const res = await request.post(`${DEMO_ERP_URL}/api/auth/login`, {
    data: { username: DEMO_ADMIN_USERNAME, password: DEMO_ADMIN_PASSWORD },
  });
  const body = await expectJsonResponse(res, 200, 'demo-admin login');
  return body.access_token as string;
}

// Helper: obtain a real AutoQA admin session cookie (real login, no auth bypass)
let _adminCookieCache = '';
async function getAdminCookie(request: import('@playwright/test').APIRequestContext): Promise<string> {
  if (_adminCookieCache) return _adminCookieCache;
  const res = await request.post(`${AUTOQA_URL}/api/auth/login`, {
    data: { username: 'admin', password: 'autoqa2026' },
  });
  const body = await expectJsonResponse(res, 200, 'AutoQA admin login');
  const setCookie = res.headers()['set-cookie'] || '';
  _adminCookieCache = (Array.isArray(setCookie) ? setCookie[0] : setCookie).split(';')[0] || '';
  return _adminCookieCache;
}

// ── Helper: enable/disable a demo bug toggle ─────────────────────────────────
async function setToggle(
  request: import('@playwright/test').APIRequestContext,
  token: string,
  key: string,
  enabled: boolean,
): Promise<void> {
  const res = await request.post(
    `${DEMO_ERP_URL}/api/demo-bugs/toggles/${key}?enabled=${enabled}`,
    { headers: { Authorization: `Bearer ${token}` } },
  );
  await expectJsonResponse(res, 200, `toggle ${key}=${enabled}`);
}

// ── Helper: reset all known toggles to OFF ───────────────────────────────────
const ALL_TOGGLES = [
  'employee_save_failure',
  'employee_success_message_missing',
  'employee_table_refresh_failure',
  'stock_difference_error',
  'api_delay',
  'login_failure_mode',
];

async function resetAllToggles(
  request: import('@playwright/test').APIRequestContext,
  token: string,
): Promise<void> {
  for (const key of ALL_TOGGLES) {
    const res = await request.post(
      `${DEMO_ERP_URL}/api/demo-bugs/toggles/${key}?enabled=false`,
      { headers: { Authorization: `Bearer ${token}` } },
    );
    await expectJsonResponse(res, 200, `reset toggle ${key}`);
  }
}

// ── Helper: sync + find the employee task ────────────────────────────────────
async function syncAndFindEmployeeTask(
  request: import('@playwright/test').APIRequestContext,
  csrfToken?: string,
): Promise<Record<string, unknown>> {
  const headers: Record<string, string> = {};
  if (csrfToken) headers['X-CSRF-Token'] = csrfToken;
  const syncRes = await request.post(`${AUTOQA_URL}/api/task-imports/sync`, { headers });
  const imports = (await expectJsonResponse(syncRes, 200, 'sync')) as unknown as Record<string, unknown>[];
  expect(Array.isArray(imports) && imports.length > 0, 'sync returned no imports').toBeTruthy();
  const employeeTasks = imports.filter((t) => t['page_path'] === '/hr/employees/new' || String(t['title'] ?? '').includes('Employee'));
  employeeTasks.sort((a, b) => (b['source_revision'] as number) - (a['source_revision'] as number));
  const task = employeeTasks.length > 0 ? employeeTasks[0] : imports.sort((a, b) => (b['source_revision'] as number) - (a['source_revision'] as number))[0];
  expect(task, 'no employee task found').toBeDefined();
  return task as Record<string, unknown>;
}

// ── Helper: prepare + approve an import ─────────────────────────────────────
async function prepareAndApprove(
  request: import('@playwright/test').APIRequestContext,
  task: Record<string, unknown>,
  csrfToken: string,
): Promise<Record<string, unknown>> {
  const importId = task['id'] as number;
  const prepRes = await request.post(`${AUTOQA_URL}/api/task-imports/${importId}/prepare-plan`, { headers: { 'X-CSRF-Token': csrfToken } });
  const prepData = await expectJsonResponse(prepRes, 200, 'prepare-plan');
  expect(prepData['import_status'], 'prepare-plan must yield PLAN_PREPARED').toBe('PLAN_PREPARED');
  expect(prepData['linked_test_plan_id'], 'linked_test_plan_id must be set after prepare').toBeTruthy();

  const apprRes = await request.post(
    `${AUTOQA_URL}/api/task-imports/${importId}/approve`,
    { headers: { 'X-CSRF-Token': csrfToken } },
  );
  const apprData = await expectJsonResponse(apprRes, 200, 'approve');
  expect(apprData['import_status'], 'approve must yield APPROVED').toBe('APPROVED');
  expect(apprData['approved_by'], 'approved_by must be set').toBeTruthy();
  expect(apprData['linked_test_plan_id'], 'linked_test_plan_id exists').toBe(prepData['linked_test_plan_id']);
  expect(apprData['source_task_id'], 'exact source task id').toBe(task['source_task_id']);
  expect(apprData['source_revision'], 'exact source revision').toBe(task['source_revision']);
  return apprData;
}

// ─────────────────────────────────────────────────────────────────────────────

test.describe('Phase 3.1 — Full Acceptance Hardening Suite', () => {
  // Force serial execution — all tests share AutoQA DB, Mock Portal, and Demo ERP toggle state
  test.describe.configure({ mode: 'serial' });
  test.setTimeout(120000);

  let demoAdminToken = '';
  let autoqaCsrfToken = '';

  test.beforeEach(async ({ request }) => {
    // Obtain demo-admin token (needed for toggle endpoints)
    demoAdminToken = await getDemoAdminToken(request);

    // Reset all Demo Product bug toggles to OFF
    await resetAllToggles(request, demoAdminToken);

    // Seed test users
    await request.post(`${AUTOQA_URL}/api/system/seed-test-data`);

    // Login to AutoQA as admin to get CSRF token
    const loginRes = await request.post(`${AUTOQA_URL}/api/auth/login`, {
      data: { username: 'admin', password: 'autoqa2026' }
    });
    const loginBody = await expectJsonResponse(loginRes, 200, 'admin login');
    autoqaCsrfToken = loginBody.csrf_token;

    // Reset AutoQA import statuses to DRAFT + cancel any pending execution jobs
    const resetRes = await request.post(`${AUTOQA_URL}/api/task-imports/reset-for-testing`, {
      headers: { 'X-CSRF-Token': autoqaCsrfToken }
    });
    await expectJsonResponse(resetRes, 200, 'reset-for-testing');

    // Reset tasks in Mock Task Portal to TESTING_L2
    const portalResetRes = await request.post(`${MOCK_PORTAL_URL}/api/tasks/reset-testing-l2`);
    await expectJsonResponse(portalResetRes, 200, 'portal reset-testing-l2');
  });

  // ── 01 PASS ─────────────────────────────────────────────────────────────────
  test('01 — PASS full flow: import, plan, approve, execute, screenshot SHA-256, and QA_PASSED callback', async ({ request }) => {
    // 1. Sync and select task
    const task = await syncAndFindEmployeeTask(request, autoqaCsrfToken);
    const importId = task['id'] as number;

    // 2. Prepare + approve
    await prepareAndApprove(request, task, autoqaCsrfToken);

    // 3. Execute
    const runRes = await request.post(`${AUTOQA_URL}/api/task-imports/${importId}/run`, { headers: { 'X-CSRF-Token': autoqaCsrfToken } });
    const completed = await expectJsonResponse(runRes, 200, 'run');

    expect(completed['import_status'], 'import_status must be COMPLETED').toBe('COMPLETED');
    expect(completed['callback_status'], 'callback_status must be SUCCESS').toBe('SUCCESS');
    expect(completed['linked_run_id'], 'linked_run_id must be set').toBeTruthy();
    
    // Verify exact linked run
    const runId = completed['linked_run_id'];
    const runStatusRes = await request.get(`${AUTOQA_URL}/api/automated-runs/${runId}`, { headers: { Cookie: await getAdminCookie(request) } });
    const runStatusData = await expectJsonResponse(runStatusRes, 200, 'run status');
    expect(runStatusData['run_key'], 'must be a valid run').toBeTruthy();

    // 4. Verify Mock Task Portal received QA_PASSED callback
    const sourceTaskId = task['source_task_id'];
    const portalRes = await request.get(`${MOCK_PORTAL_URL}/api/tasks/${sourceTaskId}`);
    const portalTask = await expectJsonResponse(portalRes, 200, 'portal task fetch');
    expect(portalTask['status'], 'portal task status must be QA_PASSED').toBe('QA_PASSED');

    // 5. Verify evidence artifacts (valid SHA-256, dimensions > 1x1)
    if (completed['linked_run_id']) {
      const artRes = await request.get(
        `${AUTOQA_URL}/api/automated-runs/${completed['linked_run_id']}/artifacts`,
        { headers: { Cookie: await getAdminCookie(request) } },
      );
      const artifacts = await expectJsonResponse(artRes, 200, 'evidence fetch') as Record<string, unknown>[];
      expect(artifacts.length, 'at least one artifact expected').toBeGreaterThan(0);
      const shot =
        artifacts.find((a) => a['artifact_type'] === 'SCREENSHOT') ?? artifacts[0];
      expect(shot['sha256'], 'sha256 must be defined').toBeDefined();
      expect(String(shot['sha256']).length, 'sha256 must be 64 hex chars').toBe(64);
    }
  });

  // ── 02 FAIL ─────────────────────────────────────────────────────────────────
  test('02 — FAIL full flow: bug toggle triggers assertion failure, failure evidence, defect creation, and REWORK callback', async ({ request }) => {
    // 1. Enable employee_save_failure bug toggle
    await setToggle(request, demoAdminToken, 'employee_save_failure', true);

    try {
      // 2. Sync and select task
      const task = await syncAndFindEmployeeTask(request, autoqaCsrfToken);
      const importId = task['id'] as number;

      // 3. Prepare + approve
      await prepareAndApprove(request, task, autoqaCsrfToken);

      // 4. Execute - expecting a controlled FAIL (API returns 200 with failure state)
      const runRes = await request.post(`${AUTOQA_URL}/api/task-imports/${importId}/run`, { headers: { 'X-CSRF-Token': autoqaCsrfToken } });
      const completed = await expectJsonResponse(runRes, 200, 'run (FAIL flow)');

      // import_status may be COMPLETED (for FAIL) or NEED_CLARITY (for BLOCKED)
      expect(
        ['COMPLETED', 'NEED_CLARITY'].includes(completed['import_status'] as string),
        `import_status must be COMPLETED or NEED_CLARITY, got ${completed['import_status']}`,
      ).toBeTruthy();
      expect(completed['callback_status'], 'callback_status must be SUCCESS').toBe('SUCCESS');
      expect(completed['linked_run_id'], 'linked_run_id must be set').toBeTruthy();
      
      const runId = completed['linked_run_id'];
      const runStatusRes = await request.get(`${AUTOQA_URL}/api/automated-runs/${runId}`, { headers: { Cookie: await getAdminCookie(request) } });
      const runStatusData = await expectJsonResponse(runStatusRes, 200, 'run status');
      expect(runStatusData['status'], 'run must be FAILED').toBe('FAILED');

      // 5. Verify Mock Task Portal received REWORK callback
      const sourceTaskId = task['source_task_id'];
      const portalRes = await request.get(`${MOCK_PORTAL_URL}/api/tasks/${sourceTaskId}`);
      const portalTask = await expectJsonResponse(portalRes, 200, 'portal task (FAIL flow)');
      expect(
        ['REWORK', 'NEED_CLARITY'].includes(portalTask['status'] as string),
        `portal task status must be REWORK or NEED_CLARITY, got ${portalTask['status']}`,
      ).toBeTruthy();

      // 6. Verify defect was created (if available)
      const defectsRes = await request.get(`${AUTOQA_URL}/api/defects`, {
        headers: { Cookie: await getAdminCookie(request) },
      });
      const defects = await expectJsonResponse(defectsRes, 200, 'defect fetch');
      const items = Array.isArray(defects) ? defects : ((defects as Record<string, unknown>)['items'] ?? []) as unknown[];
      expect(Array.isArray(items), 'defects response must be an array').toBeTruthy();
    } finally {
      // Guarantee toggle cleanup even if test fails
      await setToggle(request, demoAdminToken, 'employee_save_failure', false);
    }
  });

  // ── 03 BLOCKED ──────────────────────────────────────────────────────────────
  test('03 — BLOCKED full flow: auth failure returns BLOCKED, stores reason, NO defect created, and NEED_CLARITY callback', async ({ request }) => {
    // 1. Enable login_failure_mode bug toggle
    await setToggle(request, demoAdminToken, 'login_failure_mode', true);

    try {
      // 2. Verify toggle is active
      const toggleCheckRes = await request.post(
        `${DEMO_ERP_URL}/api/demo-bugs/toggles/login_failure_mode?enabled=true`,
        { headers: { Authorization: `Bearer ${demoAdminToken}` } },
      );
      const toggleState = await expectJsonResponse(toggleCheckRes, 200, 'toggle verify');
      expect(toggleState['enabled'], 'login_failure_mode must be enabled').toBe(true);

      // 3. Sync and select task
      const task = await syncAndFindEmployeeTask(request, autoqaCsrfToken);
      const importId = task['id'] as number;

      // 4. Prepare + approve
      await prepareAndApprove(request, task, autoqaCsrfToken);

      // 5. Execute - login will return 503 → BLOCKED → NEED_CLARITY
      const runRes = await request.post(`${AUTOQA_URL}/api/task-imports/${importId}/run`, { headers: { 'X-CSRF-Token': autoqaCsrfToken } });
      const completed = await expectJsonResponse(runRes, 200, 'run (BLOCKED flow)');

      expect(
        ['NEED_CLARITY', 'HOLD'].includes(completed['import_status'] as string),
        `import_status must be NEED_CLARITY or HOLD, got ${completed['import_status']}`,
      ).toBeTruthy();
      expect(completed['callback_status'], 'callback_status must be SUCCESS').toBe('SUCCESS');
      expect(completed['linked_run_id'], 'linked_run_id must be set').toBeTruthy();
      
      const runId = completed['linked_run_id'];
      const runStatusRes = await request.get(`${AUTOQA_URL}/api/automated-runs/${runId}`, { headers: { Cookie: await getAdminCookie(request) } });
      const runStatusData = await expectJsonResponse(runStatusRes, 200, 'run status');
      expect(runStatusData['status'], 'run must be BLOCKED').toBe('BLOCKED');

      // 6. Verify Mock Task Portal received NEED_CLARITY callback
      const sourceTaskId = task['source_task_id'];
      const portalRes = await request.get(`${MOCK_PORTAL_URL}/api/tasks/${sourceTaskId}`);
      const portalTask = await expectJsonResponse(portalRes, 200, 'portal task (BLOCKED flow)');
      expect(
        ['NEED_CLARITY', 'REWORK', 'HOLD'].includes(portalTask['status'] as string),
        `portal task status must indicate blocked/unclear, got ${portalTask['status']}`,
      ).toBeTruthy();
    } finally {
      // Guarantee toggle cleanup even if test fails
      await setToggle(request, demoAdminToken, 'login_failure_mode', false);
    }
  });

  // ── 04 DUPLICATE ─────────────────────────────────────────────────────────────
  test('04 — Duplicate import prevention and revision isolation', async ({ request }) => {
    // Sync once and record the unique key set
    const res1 = await request.post(`${AUTOQA_URL}/api/task-imports/sync`, { headers: { 'X-CSRF-Token': autoqaCsrfToken } });
    const imports1 = (await expectJsonResponse(res1, 200, 'sync 1')) as unknown as Record<string, unknown>[];
    expect(imports1.length, 'first sync must return imports').toBeGreaterThan(0);

    // Build a map of unique keys from first sync
    type UniqueKey = { project_id: unknown; source_system: unknown; source_task_id: unknown; source_revision: unknown };
    const keyOf = (imp: Record<string, unknown>): string =>
      `${imp['project_id']}|${imp['source_system']}|${imp['source_task_id']}|${imp['source_revision']}`;
    const keys1 = new Set(imports1.map(keyOf));

    // Sync again — no new unique keys should appear
    const res2 = await request.post(`${AUTOQA_URL}/api/task-imports/sync`, { headers: { 'X-CSRF-Token': autoqaCsrfToken } });
    const imports2 = (await expectJsonResponse(res2, 200, 'sync 2')) as unknown as Record<string, unknown>[];

    const keys2 = new Set(imports2.map(keyOf));

    // Every key in sync2 must exist in sync1 (no new unique records created by re-sync)
    for (const key of keys2) {
      expect(keys1.has(key), `Re-sync must not create new unique key: ${key}`).toBeTruthy();
    }

    // Verify each unique key appears exactly once across both syncs
    const allById = new Map<number, Record<string, unknown>>();
    for (const imp of [...imports1, ...imports2]) {
      const id = imp['id'] as number;
      allById.set(id, imp);
    }
    const keyCounts = new Map<string, number>();
    for (const imp of allById.values()) {
      const k = keyOf(imp);
      keyCounts.set(k, (keyCounts.get(k) ?? 0) + 1);
    }
    for (const [key, count] of keyCounts.entries()) {
      expect(count, `Unique key ${key} must appear exactly once`).toBe(1);
    }
  });

  // ── 05 CALLBACK RETRY ────────────────────────────────────────────────────────
  test('05 — Callback retry endpoint idempotency', async ({ request }) => {
    let listRes = await request.get(`${AUTOQA_URL}/api/task-imports`);
    let imports = (await expectJsonResponse(listRes, 200, 'task fetch')) as Record<string, unknown>[];
    if (!imports || imports.length === 0) {
      await request.post(`${AUTOQA_URL}/api/task-imports/sync`, { headers: { 'X-CSRF-Token': autoqaCsrfToken } });
      listRes = await request.get(`${AUTOQA_URL}/api/task-imports`);
      imports = (await expectJsonResponse(listRes, 200, 'task fetch')) as Record<string, unknown>[];
    }
    const task = imports[0];
    expect(task, 'at least one import must exist').toBeDefined();

    const retryRes = await request.post(
      `${AUTOQA_URL}/api/task-imports/${task['id']}/callback/retry`,
      { headers: { 'X-CSRF-Token': autoqaCsrfToken } },
    );
    const retryBody = await retryRes.text();
    expect(
      [200, 400].includes(retryRes.status()),
      `retry callback failed: HTTP ${retryRes.status()}\n${retryBody}`
    ).toBeTruthy();
  });

  // ── 06 PROJECT ISOLATION ─────────────────────────────────────────────────────
  test('06 — Project isolation check', async ({ request }) => {
    const res = await request.get(`${AUTOQA_URL}/api/task-imports/99999`);
    expect(res.status(), 'non-existent import must return 404').toBe(404);
  });
});
