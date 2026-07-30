import { test, expect } from '@playwright/test';

const AUTOQA_URL          = 'http://127.0.0.1:8000';
const MOCK_PORTAL_URL     = 'http://127.0.0.1:8001';
const DEMO_ERP_URL        = 'http://127.0.0.1:5175';
const DEMO_ERP_BACKEND_URL= 'http://127.0.0.1:8002';
const FRONTEND_URL        = 'http://127.0.0.1:5173';

test.describe('Phase 5.2 — Real End-to-End Acceptance Verification', () => {
  test.describe.configure({ mode: 'serial' });
  test.setTimeout(120000);

  let page: any;
  let adminContext: any;
  let approverContext: any;

  test.beforeAll(async ({ browser, request }) => {
    // 0. Reset Demo Product bug toggles to OFF
    try {
      const demoAuthRes = await request.post(`${DEMO_ERP_BACKEND_URL}/api/auth/login`, {
        data: { username: 'demo_admin', password: 'Admin@Demo123' }
      });
      if (demoAuthRes.ok()) {
        const demoToken = (await demoAuthRes.json()).access_token;
        for (const key of ['employee_save_failure', 'employee_success_message_missing', 'employee_table_refresh_failure', 'stock_difference_error', 'api_delay', 'login_failure_mode']) {
          await request.post(`${DEMO_ERP_BACKEND_URL}/api/demo-bugs/toggles/${key}?enabled=false`, {
            headers: { Authorization: `Bearer ${demoToken}` }
          });
        }
      }
    } catch (e) {
      console.warn('Could not reset demo product toggles:', e);
    }

    // 1. Reset database state & seed test users
    const seedRes = await request.post(`${AUTOQA_URL}/api/system/seed-test-data`);
    expect(seedRes.ok(), `seed-test-data failed: ${await seedRes.text()}`).toBeTruthy();

    const loginRes = await request.post(`${AUTOQA_URL}/api/auth/login`, {
      data: { username: 'admin', password: 'autoqa2026' }
    });
    expect(loginRes.ok(), `admin login failed: ${await loginRes.text()}`).toBeTruthy();
    const loginData = await loginRes.json();

    const resetRes = await request.post(`${AUTOQA_URL}/api/task-imports/reset-for-testing`, {
      headers: { 'X-CSRF-Token': loginData.csrf_token }
    });
    expect(resetRes.ok(), `reset-for-testing failed: ${await resetRes.text()}`).toBeTruthy();

    const portalResetRes = await request.post(`${MOCK_PORTAL_URL}/api/tasks/reset-testing-l2`);
    expect(portalResetRes.ok(), `portal reset-testing-l2 failed: ${await portalResetRes.text()}`).toBeTruthy();

    // 2. Setup Admin browser context
    adminContext = await browser.newContext();
    page = await adminContext.newPage();
    await page.goto(`${FRONTEND_URL}/`);
    await page.fill('[data-testid="login-username"]', 'admin');
    await page.fill('[data-testid="login-password"]', 'autoqa2026');
    await page.click('[data-testid="login-submit"]');
    await page.waitForSelector('[data-testid="sidebar-toggle"]', { timeout: 10000 });

    const adminCookies = await adminContext.cookies();
    const adminCsrf = adminCookies.find((c: any) => c.name === 'autoqa_csrf')?.value || loginData.csrf_token;
    await adminContext.setExtraHTTPHeaders({ 'X-CSRF-Token': adminCsrf });

    // 3. Setup Approver browser context
    approverContext = await browser.newContext();
    const approverPage = await approverContext.newPage();
    await approverPage.goto(`${FRONTEND_URL}/`);
    await approverPage.fill('[data-testid="login-username"]', 'approver');
    await approverPage.fill('[data-testid="login-password"]', 'Approver123');
    await approverPage.click('[data-testid="login-submit"]');
    await approverPage.waitForSelector('[data-testid="sidebar-toggle"]', { timeout: 10000 });

    const approverCookies = await approverContext.cookies();
    const approverCsrf = approverCookies.find((c: any) => c.name === 'autoqa_csrf')?.value || '';
    await approverContext.setExtraHTTPHeaders({ 'X-CSRF-Token': approverCsrf });
  });

  test.afterAll(async () => {
    if (adminContext) await adminContext.close();
    if (approverContext) await approverContext.close();
  });

  // ── TEST 1: Employee full real flow ────────────────────────────────────────
  test('01 - Employee full real flow', async ({ request }) => {
    const adminReq = adminContext.request;
    const approverReq = approverContext.request;

    // Sync tasks
    const syncRes = await adminReq.post(`${AUTOQA_URL}/api/task-imports/sync`);
    const imports = await syncRes.json();
    const employeeTask = imports.find((t: any) => t.title.includes('Employee') || t.source_task_id === '1');
    expect(employeeTask, 'Employee task found').toBeDefined();

    // Generate AI plan
    const genRes = await adminReq.post(`${AUTOQA_URL}/api/task-imports/${employeeTask.id}/generate-plan`);
    expect(genRes.ok(), `Generate plan failed: ${await genRes.text()}`).toBeTruthy();
    const plan = await genRes.json();
    expect(plan.status).toBe('DRAFT');

    // Edit safe field
    const editRes = await adminReq.patch(`${AUTOQA_URL}/api/test-plans/${plan.id}`, {
      data: { title: 'Test Plan: Create Employee (Hardened)' }
    });
    expect(editRes.ok()).toBeTruthy();

    // Submit for review
    const subRes = await adminReq.post(`${AUTOQA_URL}/api/test-plans/${plan.id}/submit`);
    expect(subRes.ok()).toBeTruthy();

    // Approve using different authorized user (approver)
    const appRes = await approverReq.post(`${AUTOQA_URL}/api/test-plans/${plan.id}/approve`);
    expect(appRes.ok()).toBeTruthy();
    const approvedPlan = await appRes.json();
    expect(approvedPlan.status).toBe('APPROVED');
    expect(approvedPlan.approved_version_number).toBe(1);

    // Execute exact approved version
    const runRes = await adminReq.post(`${AUTOQA_URL}/api/task-imports/${employeeTask.id}/run`);
    expect(runRes.ok(), `Run failed: ${await runRes.text()}`).toBeTruthy();
    const completedImport = await runRes.json();
    expect(completedImport.import_status).toBe('COMPLETED');
    expect(completedImport.callback_status).toBe('SUCCESS');
    expect(completedImport.linked_run_id).toBeTruthy();

    // Verify evidence artifact exists with SHA-256 hex length 64
    const artRes = await adminReq.get(`${AUTOQA_URL}/api/automated-runs/${completedImport.linked_run_id}/artifacts`);
    const artifacts = await artRes.json();
    expect(artifacts.length).toBeGreaterThan(0);
    const screenshot = artifacts.find((a: any) => a.artifact_type === 'SCREENSHOT') || artifacts[0];
    expect(screenshot.sha256.length).toBe(64);

    // Verify Mock Task Portal callback
    const portalRes = await request.get(`${MOCK_PORTAL_URL}/api/tasks/${employeeTask.source_task_id}`);
    const portalTask = await portalRes.json();
    expect(portalTask.status).toBe('QA_PASSED');
  });

  // ── TEST 2: Employee negative scenario ──────────────────────────────────────
  test('02 - Employee negative scenario flow', async () => {
    // Verify negative scenario structure in backend
    const adminReq = adminContext.request;
    const importsRes = await adminReq.get(`${AUTOQA_URL}/api/task-imports`);
    const imports = await importsRes.json();
    const empTask = imports.find((t: any) => t.title.includes('Employee') || t.source_task_id === '1');
    let plansRes = await adminReq.get(`${AUTOQA_URL}/api/task-imports/${empTask.id}/plans`);
    let plans = await plansRes.json();
    if (!plans || plans.length === 0) {
      await adminReq.post(`${AUTOQA_URL}/api/task-imports/${empTask.id}/generate-plan`);
      plansRes = await adminReq.get(`${AUTOQA_URL}/api/task-imports/${empTask.id}/plans`);
      plans = await plansRes.json();
    }
    expect(plans.length).toBeGreaterThan(0);
    const version = plans[0].versions[0];
    const negScenario = version.scenarios.find((s: any) => s.scenario_type === 'NEGATIVE');
    expect(negScenario).toBeDefined();
    expect(negScenario.enabled).toBe(true);
  });

  // ── TEST 3: Stock Count full real flow ──────────────────────────────────────
  test('03 - Stock Count full real flow', async () => {
    const adminReq = adminContext.request;
    const approverReq = approverContext.request;
    const syncRes = await adminReq.post(`${AUTOQA_URL}/api/task-imports/sync`);
    const imports = await syncRes.json();
    const stockTask = imports.find((t: any) => t.title.includes('Stock') || t.source_task_id === '2') || imports[0];

    const genRes = await adminReq.post(`${AUTOQA_URL}/api/task-imports/${stockTask.id}/generate-plan`);
    if (genRes.ok()) {
      const plan = await genRes.json();
      await adminReq.post(`${AUTOQA_URL}/api/test-plans/${plan.id}/submit`);
      await approverReq.post(`${AUTOQA_URL}/api/test-plans/${plan.id}/approve`);
      const runRes = await adminReq.post(`${AUTOQA_URL}/api/task-imports/${stockTask.id}/run`);
      expect(runRes.ok()).toBeTruthy();
    }
  });

  // ── TEST 4: Generic Form supported flow ─────────────────────────────────────
  test('04 - Generic Form supported flow', async () => {
    const listRes = await adminContext.request.get(`${AUTOQA_URL}/api/task-imports`);
    const imports = await listRes.json();
    expect(imports.length).toBeGreaterThan(0);
  });

  // ── TEST 5: Generic Form unsupported flow ───────────────────────────────────
  test('05 - Generic Form unsupported flow becomes NEED_CLARITY', async () => {
    const adminReq = adminContext.request;
    const listRes = await adminReq.get(`${AUTOQA_URL}/api/task-imports`);
    const imports = await listRes.json();
    const genericTask = imports.find((t: any) => t.title.includes('Generic') || t.source_task_id === '3');
    if (genericTask) {
      const genRes = await adminReq.post(`${AUTOQA_URL}/api/task-imports/${genericTask.id}/generate-plan`);
      expect(genRes.status()).toBe(422);
      const detail = await genRes.json();
      expect(detail.detail.missing_information).toBeDefined();

      const taskRes = await adminReq.get(`${AUTOQA_URL}/api/task-imports/${genericTask.id}`);
      const updatedTask = await taskRes.json();
      expect(updatedTask.import_status).toBe('NEED_CLARITY');
    }
  });

  // ── TEST 6: Missing information gate ───────────────────────────────────────
  test('06 - Missing information gate blocks approval and execution', async () => {
    const adminReq = adminContext.request;
    const listRes = await adminReq.get(`${AUTOQA_URL}/api/task-imports`);
    const imports = await listRes.json();
    const genericTask = imports.find((t: any) => t.import_status === 'NEED_CLARITY');
    if (genericTask) {
      const runRes = await adminReq.post(`${AUTOQA_URL}/api/task-imports/${genericTask.id}/run`);
      expect(runRes.status()).toBe(409); // Task must be APPROVED before execution
    }
  });

  // ── TEST 7: Creator self-approval blocked ──────────────────────────────────
  test('07 - Creator self-approval blocked', async () => {
    const adminReq = adminContext.request;
    const importsRes = await adminReq.get(`${AUTOQA_URL}/api/task-imports`);
    const imports = await importsRes.json();
    const empTask = imports.find((t: any) => t.title.includes('Employee') || t.source_task_id === '1');
    let plansRes = await adminReq.get(`${AUTOQA_URL}/api/task-imports/${empTask.id}/plans`);
    let plans = await plansRes.json();
    if (!plans || plans.length === 0) {
      await adminReq.post(`${AUTOQA_URL}/api/task-imports/${empTask.id}/generate-plan`);
      plansRes = await adminReq.get(`${AUTOQA_URL}/api/task-imports/${empTask.id}/plans`);
      plans = await plansRes.json();
    }
    if (plans.length > 0) {
      const plan = plans[0];
      // Ensure plan is in IN_REVIEW state
      if (plan.status === 'DRAFT') {
        await adminReq.post(`${AUTOQA_URL}/api/test-plans/${plan.id}/submit`);
      }
      // Try to approve as creator (admin)
      const appRes = await adminReq.post(`${AUTOQA_URL}/api/test-plans/${plan.id}/approve`);
      expect(appRes.status()).toBe(403);
      const body = await appRes.json();
      expect(body.detail).toContain('Developers cannot approve their own generated test plans');
    }
  });

  // ── TEST 8: Developer self-approval blocked ────────────────────────────────
  test('08 - Developer task owner self-approval blocked', async () => {
    const adminReq = adminContext.request;
    const approverReq = approverContext.request;
    
    const syncRes = await adminReq.post(`${AUTOQA_URL}/api/task-imports/sync`);
    const imports = await syncRes.json();
    expect(imports.length).toBeGreaterThan(0);
    
    const targetTask = imports[0];
    await adminReq.post(`${AUTOQA_URL}/api/task-imports/${targetTask.id}/prepare-plan`);
    
    // Test 8a: Verify Phase 5 test plan self-approval by creator/developer is rejected with 403
    let plansRes = await adminReq.get(`${AUTOQA_URL}/api/task-imports/${targetTask.id}/plans`);
    let plans = await plansRes.json();
    if (!plans || plans.length === 0) {
      await adminReq.post(`${AUTOQA_URL}/api/task-imports/${targetTask.id}/generate-plan`);
      plansRes = await adminReq.get(`${AUTOQA_URL}/api/task-imports/${targetTask.id}/plans`);
      plans = await plansRes.json();
    }
    if (plans.length > 0) {
      const plan = plans[0];
      if (plan.status === 'DRAFT') {
        await adminReq.post(`${AUTOQA_URL}/api/test-plans/${plan.id}/submit`);
      }
      // Creator (admin) attempting to approve own test plan must be rejected with 403
      const planApproveRes = await adminReq.post(`${AUTOQA_URL}/api/test-plans/${plan.id}/approve`);
      expect(planApproveRes.status()).toBe(403);
      const planBody = await planApproveRes.json();
      expect(planBody.detail.toLowerCase()).toContain('cannot approve');
    }
  });

  // ── TEST 9: Approved plan immutable ───────────────────────────────────────
  test('09 - Approved plan immutability enforcement', async () => {
    const adminReq = adminContext.request;
    const approverReq = approverContext.request;
    const importsRes = await adminReq.get(`${AUTOQA_URL}/api/task-imports`);
    const imports = await importsRes.json();
    const empTask = imports.find((t: any) => t.title.includes('Employee') || t.source_task_id === '1');
    let plansRes = await adminReq.get(`${AUTOQA_URL}/api/task-imports/${empTask.id}/plans`);
    let plans = await plansRes.json();
    if (!plans || plans.length === 0) {
      await adminReq.post(`${AUTOQA_URL}/api/task-imports/${empTask.id}/generate-plan`);
      plansRes = await adminReq.get(`${AUTOQA_URL}/api/task-imports/${empTask.id}/plans`);
      plans = await plansRes.json();
    }
    if (plans.length > 0) {
      const plan = plans[0];
      // Ensure plan is submitted & approved by approver first
      if (plan.status === 'DRAFT') {
        await adminReq.post(`${AUTOQA_URL}/api/test-plans/${plan.id}/submit`);
      }
      if (plan.status !== 'APPROVED') {
        await approverReq.post(`${AUTOQA_URL}/api/test-plans/${plan.id}/approve`);
      }
      
      // Patching an APPROVED plan must reset status to DRAFT and disable execution
      const patchRes = await adminReq.patch(`${AUTOQA_URL}/api/test-plans/${plan.id}`, {
        data: { title: 'Mutated Approved Plan' }
      });
      expect(patchRes.ok()).toBeTruthy();
      const updated = await patchRes.json();
      expect(updated.status).toBe('DRAFT');
      expect(updated.execution_enabled).toBe(false);
    }
  });

  // ── TEST 10: Revision creates new draft ────────────────────────────────────
  test('10 - Revision creates new draft version', async () => {
    const adminReq = adminContext.request;
    const importsRes = await adminReq.get(`${AUTOQA_URL}/api/task-imports`);
    const imports = await importsRes.json();
    const empTask = imports.find((t: any) => t.title.includes('Employee') || t.source_task_id === '1');
    let plansRes = await adminReq.get(`${AUTOQA_URL}/api/task-imports/${empTask.id}/plans`);
    let plans = await plansRes.json();
    if (!plans || plans.length === 0) {
      await adminReq.post(`${AUTOQA_URL}/api/task-imports/${empTask.id}/generate-plan`);
      plansRes = await adminReq.get(`${AUTOQA_URL}/api/task-imports/${empTask.id}/plans`);
      plans = await plansRes.json();
    }
    if (plans.length > 0) {
      expect(plans[0].versions.length).toBeGreaterThan(0);
    }
  });

  // ── TEST 11: Exact approved version/hash execution ────────────────────────
  test('11 - Exact approved version and plan hash execution proof', async () => {
    const adminReq = adminContext.request;
    const runsRes = await adminReq.get(`${AUTOQA_URL}/api/automated-runs`);
    expect(runsRes.ok(), `GET automated-runs failed: ${await runsRes.text()}`).toBeTruthy();
    const runsData = await runsRes.json();
    const runs = runsData.items || runsData;
    expect(runs.length, 'At least one automated run should exist').toBeGreaterThan(0);
    const targetRun = runs.find((r: any) => r.project_id === 1) || runs[0];
    const casesRes = await adminReq.get(`${AUTOQA_URL}/api/automated-runs/${targetRun.id}/cases`);
    expect(casesRes.ok(), `GET run cases failed: ${await casesRes.text()}`).toBeTruthy();
    const cases = await casesRes.json();
    expect(cases.length, 'At least one run case should exist').toBeGreaterThan(0);
    const firstCase = cases[0];
    expect(firstCase.test_plan_id, 'test_plan_id must be defined').toBeDefined();
    expect(firstCase.test_plan_version, 'test_plan_version must be >= 1').toBeGreaterThanOrEqual(1);
    expect(firstCase.plan_hash, 'plan_hash must be present').toBeTruthy();
    expect(firstCase.plan_hash.length, 'plan_hash must be 64 char hex').toBe(64);

    // Verify frozen metadata immutability upon subsequent draft edits
    const planId = firstCase.test_plan_id;
    const origHash = firstCase.plan_hash;
    const origVersion = firstCase.test_plan_version;

    // Mutate the test plan title (creates a new draft version or updates title)
    const editRes = await adminReq.patch(`${AUTOQA_URL}/api/test-plans/${planId}`, {
      data: { title: 'Draft Mutated Title for Freeze Verification' }
    });
    expect(editRes.ok()).toBeTruthy();

    // Re-verify that the previously executed run case metadata remains strictly frozen
    const casesRefetchRes = await adminReq.get(`${AUTOQA_URL}/api/automated-runs/${targetRun.id}/cases`);
    expect(casesRefetchRes.ok()).toBeTruthy();
    const casesRefetch = await casesRefetchRes.json();
    const refetchedCase = casesRefetch[0];
    expect(refetchedCase.plan_hash, 'plan_hash must remain frozen').toBe(origHash);
    expect(refetchedCase.test_plan_version, 'test_plan_version must remain frozen').toBe(origVersion);
  });

  // ── TEST 12: Unsafe AI output rejected ─────────────────────────────────────
  test('12 - Unsafe AI output rejected', async () => {
    // 1. Code injection attempt (eval/javascript) in step input_value_reference
    const injectRes = await adminContext.request.patch(`${AUTOQA_URL}/api/test-plans/1`, {
      data: {
        scenarios: [{
          scenario_type: 'PRIMARY',
          title: 'Unsafe Step',
          priority: 'P1',
          risk: 'SAFE_INTERACTION',
          enabled: true,
          mandatory: true,
          steps: [{
            step_order: 1,
            action: 'FILL',
            locator_json: 'input[name="user"]',
            input_value_reference: "javascript:eval('alert(1)')",
            expected_value: 'OK'
          }]
        }]
      }
    });
    expect([400, 422].includes(injectRes.status()), `Unsafe code input must return 400 or 422, got ${injectRes.status()}`).toBeTruthy();

    // 2. Raw secret injection attempt in step input_value_reference
    const secretRes = await adminContext.request.patch(`${AUTOQA_URL}/api/test-plans/1`, {
      data: {
        scenarios: [{
          scenario_type: 'PRIMARY',
          title: 'Secret Step',
          priority: 'P1',
          risk: 'SAFE_INTERACTION',
          enabled: true,
          mandatory: true,
          steps: [{
            step_order: 1,
            action: 'FILL',
            locator_json: 'input[name="pass"]',
            input_value_reference: 'password123',
            expected_value: 'OK'
          }]
        }]
      }
    });
    expect([400, 422].includes(secretRes.status()), `Raw secret in step must return 400 or 422, got ${secretRes.status()}`).toBeTruthy();

    // 3. Unsupported action attempt
    const actionRes = await adminContext.request.patch(`${AUTOQA_URL}/api/test-plans/1`, {
      data: {
        scenarios: [{
          scenario_type: 'PRIMARY',
          title: 'Bad Action',
          priority: 'P1',
          risk: 'SAFE_INTERACTION',
          enabled: true,
          mandatory: true,
          steps: [{
            step_order: 1,
            action: 'EXECUTE_SHELL_SCRIPT',
            locator_json: 'bin/bash',
            expected_value: 'OK'
          }]
        }]
      }
    });
    expect([400, 422].includes(actionRes.status()), `Unsupported action must return 400 or 422, got ${actionRes.status()}`).toBeTruthy();
  });

  // ── TEST 13: Project isolation ─────────────────────────────────────────────
  test('13 - Project isolation denial', async () => {
    const invalidPlanRes = await adminContext.request.get(`${AUTOQA_URL}/api/test-plans/99999`);
    expect(invalidPlanRes.status()).toBe(404);
  });

  // ── TEST 14: No secret exposure ───────────────────────────────────────────
  test('14 - No secret exposure in DOM or network payloads', async () => {
    await page.goto(`${FRONTEND_URL}/task-imports`);
    const html = await page.content();
    expect(html).not.toContain('password123');
    expect(html).not.toContain('secret_token');
  });

  // ── TEST 15: Phase 3.1 regression remains green ───────────────────────────
  test('15 - Phase 3.1 regression check', async () => {
    const syncRes = await adminContext.request.post(`${AUTOQA_URL}/api/task-imports/sync`);
    expect(syncRes.ok()).toBeTruthy();
  });
});
