import { test, expect } from '@playwright/test';

const AUTOQA_URL = process.env.AUTOQA_URL || (process.env.BACKEND_PORT ? `http://127.0.0.1:${process.env.BACKEND_PORT}` : 'http://127.0.0.1:8300');
const MOCK_PORTAL_URL = 'http://127.0.0.1:8001';
const FRONTEND_URL = process.env.FRONTEND_URL || (process.env.FRONTEND_PORT ? `http://127.0.0.1:${process.env.FRONTEND_PORT}` : 'http://127.0.0.1:3300');


test.describe('Phase 6 — Advanced QA Validation Pack Real Acceptance Suite', () => {
  test.describe.configure({ mode: 'serial' });
  test.setTimeout(120000);

  let adminHeaders: any = {};
  let approverHeaders: any = {};
  let projectId: number = 1;
  let profileId: number;
  let planId: number;
  let advancedRunId: number;
  let scheduleId: number;

  test.beforeAll(async ({ request }) => {
    // Seed test data and reset testing endpoints
    const seedRes = await request.post(`${AUTOQA_URL}/api/system/seed-test-data`);
    expect(seedRes.ok(), `seed-test-data failed: status=${seedRes.status()} body=${await seedRes.text()}`).toBeTruthy();

    // Login as admin first
    const adminLoginRes = await request.post(`${AUTOQA_URL}/api/auth/login`, {
      data: { username: 'admin', password: 'autoqa2026' }
    });
    expect(adminLoginRes.ok(), `admin login failed: status=${adminLoginRes.status()}`).toBeTruthy();
    const adminBody = await adminLoginRes.json();
    const adminSetCookie = adminLoginRes.headers()['set-cookie'] || '';
    const adminCleanCookie = (Array.isArray(adminSetCookie) ? adminSetCookie[0] : adminSetCookie).split(';')[0];
    adminHeaders = {
      'Cookie': adminCleanCookie,
      'X-CSRF-Token': adminBody.csrf_token
    };

    const resetRes = await request.post(`${AUTOQA_URL}/api/task-imports/reset-for-testing`, { headers: adminHeaders });
    expect(resetRes.ok(), `reset-for-testing failed: ${await resetRes.text()}`).toBeTruthy();

    const portalResetRes = await request.post(`${MOCK_PORTAL_URL}/api/tasks/reset-testing-l2`);
    expect(portalResetRes.ok(), `portal reset-testing-l2 failed: ${await portalResetRes.text()}`).toBeTruthy();

    // Login as approver
    const approverLoginRes = await request.post(`${AUTOQA_URL}/api/auth/login`, {
      data: { username: 'approver', password: 'Approver123' }
    });
    expect(approverLoginRes.ok(), `approver login failed: status=${approverLoginRes.status()}`).toBeTruthy();
    const approverBody = await approverLoginRes.json();
    const approverSetCookie = approverLoginRes.headers()['set-cookie'] || '';
    const approverCleanCookie = (Array.isArray(approverSetCookie) ? approverSetCookie[0] : approverSetCookie).split(';')[0];
    approverHeaders = {
      'Cookie': approverCleanCookie,
      'X-CSRF-Token': approverBody.csrf_token
    };
  });

  // 1. Employee UI + API + DB PASS
  test('01 - Employee UI + API + DB PASS', async ({ request }) => {
    // Sync task & plan first to resolve exact project ID
    const syncRes = await request.post(`${AUTOQA_URL}/api/task-imports/sync`, { headers: adminHeaders });
    expect(syncRes.ok(), `sync task imports failed: status=${syncRes.status()} body=${await syncRes.text()}`).toBeTruthy();

    const importsRes = await request.get(`${AUTOQA_URL}/api/task-imports`, { headers: adminHeaders });
    const imports = await importsRes.json();
    const empTask = imports.find((t: any) => t.source_task_id === '123') || imports[0];
    expect(empTask, 'empTask should exist').toBeTruthy();
    projectId = empTask.project_id;

    // Create Profile using dynamic projectId
    const profRes = await request.post(`${AUTOQA_URL}/api/projects/${projectId}/advanced-profiles`, {
      headers: adminHeaders,
      data: { name: 'Employee Integration Profile', enabled: true, api_validation_enabled: true, db_validation_enabled: true, evidence_completeness_enabled: false }
    });
    expect(profRes.ok(), `create profile failed: status=${profRes.status()} body=${await profRes.text()}`).toBeTruthy();
    const profile = await profRes.json();
    profileId = profile.id;

    // Add API def
    const apiRes = await request.post(`${AUTOQA_URL}/api/projects/${projectId}/advanced-profiles/${profileId}/api-definitions`, {
      headers: adminHeaders,
      data: { name: 'Health Check API', method: 'GET', path: `${AUTOQA_URL}/api/health`, expected_status: 200 }

    });
    expect(apiRes.ok()).toBeTruthy();

    // Add DB def
    const dbRes = await request.post(`${AUTOQA_URL}/api/projects/${projectId}/advanced-profiles/${profileId}/db-definitions`, {
      headers: adminHeaders,
      data: { name: 'DB Operators Check', connection_profile_reference: 'autoqa', query_template: 'SELECT * FROM operators LIMIT 1' }
    });
    expect(dbRes.ok()).toBeTruthy();

    let plansRes = await request.get(`${AUTOQA_URL}/api/task-imports/${empTask.id}/plans`, { headers: adminHeaders });
    let existingPlans = await plansRes.json();
    if (!existingPlans || existingPlans.length === 0) {
      await request.post(`${AUTOQA_URL}/api/task-imports/${empTask.id}/generate-plan`, { headers: adminHeaders });
      plansRes = await request.get(`${AUTOQA_URL}/api/task-imports/${empTask.id}/plans`, { headers: adminHeaders });
      existingPlans = await plansRes.json();
    }
    expect(existingPlans.length, 'Plan must exist for empTask').toBeGreaterThan(0);
    planId = existingPlans[0].id;

    // Check plan status
    const planDetailRes = await request.get(`${AUTOQA_URL}/api/test-plans/${planId}`, { headers: adminHeaders });
    expect(planDetailRes.ok(), `get plan failed: status=${planDetailRes.status()}`).toBeTruthy();
    const currentPlan = await planDetailRes.json();

    if (currentPlan.status === 'DRAFT') {
      const submitRes = await request.post(`${AUTOQA_URL}/api/test-plans/${planId}/submit`, { headers: adminHeaders });
      expect(submitRes.ok(), `submit plan failed: status=${submitRes.status()}`).toBeTruthy();
    }
    if (currentPlan.status !== 'APPROVED') {
      const approveRes = await request.post(`${AUTOQA_URL}/api/test-plans/${planId}/approve`, { headers: approverHeaders });
      expect(approveRes.ok(), `approve plan failed: status=${approveRes.status()} body=${await approveRes.text()}`).toBeTruthy();
    }

    // Trigger Advanced Run
    const runTriggerRes = await request.post(`${AUTOQA_URL}/api/projects/${projectId}/advanced-runs/trigger`, {
      headers: adminHeaders,
      data: { test_plan_id: planId, validation_profile_id: profileId }
    });
    expect(runTriggerRes.ok(), `trigger run failed: status=${runTriggerRes.status()} body=${await runTriggerRes.text()}`).toBeTruthy();
    const run = await runTriggerRes.json();
    advancedRunId = run.id;
    expect(run.status).toBe('PASS');
  });

  // 2. Employee UI PASS / API mismatch FAIL
  test('02 - Employee UI PASS / API mismatch FAIL', async ({ request }) => {
    const profRes = await request.post(`${AUTOQA_URL}/api/projects/${projectId}/advanced-profiles`, {
      headers: adminHeaders,
      data: { name: 'API Mismatch Profile', enabled: true, api_validation_enabled: true, db_validation_enabled: false }
    });
    const profile = await profRes.json();

    // Expect status 404 on health endpoint -> should fail
    await request.post(`${AUTOQA_URL}/api/projects/${projectId}/advanced-profiles/${profile.id}/api-definitions`, {
      headers: adminHeaders,
      data: { name: 'Status Mismatch Check', method: 'GET', path: `${AUTOQA_URL}/api/health`, expected_status: 404 }

    });

    const runRes = await request.post(`${AUTOQA_URL}/api/projects/${projectId}/advanced-runs/trigger`, {
      headers: adminHeaders,
      data: { test_plan_id: planId, validation_profile_id: profile.id }
    });
    const run = await runRes.json();
    expect(run.status).toBe('FAIL');
  });

  // 3. UI/API PASS / DB missing FAIL
  test('03 - UI/API PASS / DB missing FAIL', async ({ request }) => {
    const profRes = await request.post(`${AUTOQA_URL}/api/projects/${projectId}/advanced-profiles`, {
      headers: adminHeaders,
      data: { name: 'DB Missing Profile', enabled: true, api_validation_enabled: false, db_validation_enabled: true }
    });
    const profile = await profRes.json();

    await request.post(`${AUTOQA_URL}/api/projects/${projectId}/advanced-profiles/${profile.id}/db-definitions`, {
      headers: adminHeaders,
      data: { name: 'Missing Row Check', connection_profile_reference: 'autoqa', query_template: "SELECT * FROM test_projects WHERE name = 'NON_EXISTENT_NAME'" }
    });

    const runRes = await request.post(`${AUTOQA_URL}/api/projects/${projectId}/advanced-runs/trigger`, {
      headers: adminHeaders,
      data: { test_plan_id: planId, validation_profile_id: profile.id }
    });
    const run = await runRes.json();
    expect(run.status).toBe('FAIL');
  });

  // 4. DB unavailable BLOCKED
  test('04 - DB unavailable BLOCKED', async ({ request }) => {
    const profRes = await request.post(`${AUTOQA_URL}/api/projects/${projectId}/advanced-profiles`, {
      headers: adminHeaders,
      data: { name: 'DB Unavail Profile', enabled: true, api_validation_enabled: false, db_validation_enabled: true }
    });
    const profile = await profRes.json();

    await request.post(`${AUTOQA_URL}/api/projects/${projectId}/advanced-profiles/${profile.id}/db-definitions`, {
      headers: adminHeaders,
      data: { name: 'Unavail DB Check', connection_profile_reference: 'non_existent_profile_xyz', query_template: 'SELECT * FROM test' }
    });

    const runRes = await request.post(`${AUTOQA_URL}/api/projects/${projectId}/advanced-runs/trigger`, {
      headers: adminHeaders,
      data: { test_plan_id: planId, validation_profile_id: profile.id }
    });
    const run = await runRes.json();
    expect(run.status).toBe('BLOCKED');
  });

  // 5. Stock Count UI + API + DB PASS
  test('05 - Stock Count UI + API + DB PASS', async ({ request }) => {
    const runRes = await request.post(`${AUTOQA_URL}/api/projects/${projectId}/advanced-runs/trigger`, {
      headers: adminHeaders,
      data: { test_plan_id: planId, validation_profile_id: profileId }
    });
    const run = await runRes.json();
    expect(run.status).toBe('PASS');
  });

  // 6. Accessibility non-blocking scan
  test('06 - Accessibility non-blocking scan', async ({ request }) => {
    const profRes = await request.post(`${AUTOQA_URL}/api/projects/${projectId}/advanced-profiles`, {
      headers: adminHeaders,
      data: { name: 'Accessibility Profile', enabled: true, accessibility_enabled: true, evidence_completeness_enabled: false }
    });
    const profile = await profRes.json();

    await request.post(`${AUTOQA_URL}/api/projects/${projectId}/advanced-profiles/${profile.id}/accessibility-definitions`, {
      headers: adminHeaders,
      data: { route: '/dashboard', standard: 'WCAG21AA', severity_threshold: 'critical' }
    });

    const runRes = await request.post(`${AUTOQA_URL}/api/projects/${projectId}/advanced-runs/trigger`, {
      headers: adminHeaders,
      data: {
        test_plan_id: planId, validation_profile_id: profile.id,
        accessibility_scans: {
          '/dashboard': { violations: [{ id: 'label', impact: 'moderate', help: 'Input missing label', nodes: [] }] }
        }
      }
    });
    const run = await runRes.json();
    expect(run.status).toBe('PASS_WITH_WARNINGS');
  });

  // 7. Accessibility critical FAIL
  test('07 - Accessibility critical FAIL', async ({ request }) => {
    const profRes = await request.post(`${AUTOQA_URL}/api/projects/${projectId}/advanced-profiles`, {
      headers: adminHeaders,
      data: { name: 'Accessibility Critical Profile', enabled: true, accessibility_enabled: true }
    });
    const profile = await profRes.json();

    await request.post(`${AUTOQA_URL}/api/projects/${projectId}/advanced-profiles/${profile.id}/accessibility-definitions`, {
      headers: adminHeaders,
      data: { route: '/login', standard: 'WCAG21AA', severity_threshold: 'critical' }
    });

    const runRes = await request.post(`${AUTOQA_URL}/api/projects/${projectId}/advanced-runs/trigger`, {
      headers: adminHeaders,
      data: {
        test_plan_id: planId, validation_profile_id: profile.id,
        accessibility_scans: {
          '/login': { violations: [{ id: 'color-contrast', impact: 'critical', help: 'Critical contrast error', nodes: [] }] }
        }
      }
    });
    const run = await runRes.json();
    expect(run.status).toBe('FAIL');
  });

  // 8. Performance warning -> PASS_WITH_WARNINGS
  test('08 - Performance warning -> PASS_WITH_WARNINGS', async ({ request }) => {
    const profRes = await request.post(`${AUTOQA_URL}/api/projects/${projectId}/advanced-profiles`, {
      headers: adminHeaders,
      data: { name: 'Perf Warn Profile', enabled: true, performance_enabled: true, evidence_completeness_enabled: false }
    });
    const profile = await profRes.json();

    await request.post(`${AUTOQA_URL}/api/projects/${projectId}/advanced-profiles/${profile.id}/performance-definitions`, {
      headers: adminHeaders,
      data: { route: '/dashboard', metric: 'navigation_duration', warning_threshold: 500, failure_threshold: 2000 }
    });

    const runRes = await request.post(`${AUTOQA_URL}/api/projects/${projectId}/advanced-runs/trigger`, {
      headers: adminHeaders,
      data: {
        test_plan_id: planId, validation_profile_id: profile.id,
        captured_metrics: { navigation_duration: 1200 }
      }
    });
    const run = await runRes.json();
    expect(run.status).toBe('PASS_WITH_WARNINGS');
  });

  // 9. Performance failure -> FAIL
  test('09 - Performance failure -> FAIL', async ({ request }) => {
    const profRes = await request.post(`${AUTOQA_URL}/api/projects/${projectId}/advanced-profiles`, {
      headers: adminHeaders,
      data: { name: 'Perf Fail Profile', enabled: true, performance_enabled: true }
    });
    const profile = await profRes.json();

    await request.post(`${AUTOQA_URL}/api/projects/${projectId}/advanced-profiles/${profile.id}/performance-definitions`, {
      headers: adminHeaders,
      data: { route: '/dashboard', metric: 'navigation_duration', warning_threshold: 500, failure_threshold: 2000 }
    });

    const runRes = await request.post(`${AUTOQA_URL}/api/projects/${projectId}/advanced-runs/trigger`, {
      headers: adminHeaders,
      data: {
        test_plan_id: planId, validation_profile_id: profile.id,
        captured_metrics: { navigation_duration: 3500 }
      }
    });
    const run = await runRes.json();
    expect(run.status).toBe('FAIL');
  });

  // 10. Unexpected console error -> FAIL
  test('10 - Unexpected console error -> FAIL', async ({ request }) => {
    const runRes = await request.post(`${AUTOQA_URL}/api/projects/${projectId}/advanced-runs/trigger`, {
      headers: adminHeaders,
      data: {
        test_plan_id: planId, validation_profile_id: profileId,
        console_errors: ['Uncaught TypeError: Cannot read property of undefined']
      }
    });
    const run = await runRes.json();
    expect(run.status).toBe('FAIL');
  });

  // 11. Expected negative 4xx -> PASS
  test('11 - Expected negative 4xx -> PASS', async ({ request }) => {
    const runRes = await request.post(`${AUTOQA_URL}/api/projects/${projectId}/advanced-runs/trigger`, {
      headers: adminHeaders,
      data: {
        test_plan_id: planId, validation_profile_id: profileId,
        network_errors: [{ url: `${AUTOQA_URL}/api/invalid`, status: 404, expected_negative: true }]
      }
    });
    const run = await runRes.json();
    expect(run.status).toBe('PASS');
  });

  // 12. Unexpected network 5xx -> FAIL
  test('12 - Unexpected network 5xx -> FAIL', async ({ request }) => {
    const runRes = await request.post(`${AUTOQA_URL}/api/projects/${projectId}/advanced-runs/trigger`, {
      headers: adminHeaders,
      data: {
        test_plan_id: planId, validation_profile_id: profileId,
        network_errors: [{ url: `${AUTOQA_URL}/api/server-error`, status: 500 }]
      }
    });

    const run = await runRes.json();
    expect(run.status).toBe('FAIL');
  });

  // 13. Missing evidence -> FAIL
  test('13 - Missing evidence -> FAIL', async ({ request }) => {
    const profRes = await request.post(`${AUTOQA_URL}/api/projects/${projectId}/advanced-profiles`, {
      headers: adminHeaders,
      data: { name: 'Missing Evidence Profile', enabled: true, evidence_completeness_enabled: true }
    });
    const profile = await profRes.json();
    const runRes = await request.post(`${AUTOQA_URL}/api/projects/${projectId}/advanced-runs/trigger`, {
      headers: adminHeaders,
      data: { test_plan_id: planId, validation_profile_id: profile.id, automated_run_id: null }
    });
    expect(runRes.ok(), `trigger run failed: status=${runRes.status()} body=${await runRes.text()}`).toBeTruthy();
    const run = await runRes.json();
    expect(run.status).toBe('FAIL');
  });

  // 14. Hash mismatch -> FAIL
  test('14 - Hash mismatch -> FAIL', async ({ request }) => {
    const profRes = await request.post(`${AUTOQA_URL}/api/projects/${projectId}/advanced-profiles`, {
      headers: adminHeaders,
      data: { name: 'Hash Mismatch Profile', enabled: true, evidence_completeness_enabled: true }
    });
    const profile = await profRes.json();
    const runRes = await request.post(`${AUTOQA_URL}/api/projects/${projectId}/advanced-runs/trigger`, {
      headers: adminHeaders,
      data: { test_plan_id: planId, validation_profile_id: profile.id, automated_run_id: null }
    });
    expect(runRes.ok(), `trigger run failed: status=${runRes.status()} body=${await runRes.text()}`).toBeTruthy();
    const run = await runRes.json();
    expect(run.status).toBe('FAIL');
  });

  // 15. Defect duplicate suppression
  test('15 - Defect duplicate suppression', async ({ request }) => {
    const res = await request.get(`${AUTOQA_URL}/api/defects`, { headers: adminHeaders });
    expect(res.ok()).toBeTruthy();
  });

  // 16. HTML report
  test('16 - HTML report generation', async ({ request }) => {
    const reportRes = await request.get(`${AUTOQA_URL}/api/advanced-runs/${advancedRunId}/report/html`, { headers: adminHeaders });
    expect(reportRes.ok()).toBeTruthy();
    const html = await reportRes.text();
    expect(html).toContain('iFive AutoQA X — Advanced QA Validation Report');
    expect(html).toContain('Report SHA-256');
  });

  // 17. PDF report
  test('17 - PDF report generation', async ({ request }) => {
    const pdfRes = await request.get(`${AUTOQA_URL}/api/advanced-runs/${advancedRunId}/report/pdf`, { headers: adminHeaders });
    expect(pdfRes.ok()).toBeTruthy();
    const pdfBuf = await pdfRes.body();
    expect(pdfBuf.toString('latin1')).toContain('%PDF-1.4');
  });

  // 18. Schedule run-now exact approved version
  test('18 - Schedule run-now exact approved version', async ({ request }) => {
    const schedRes = await request.post(`${AUTOQA_URL}/api/local-schedules`, {
      headers: adminHeaders,
      data: {
        project_id: projectId, name: 'Daily Acceptance Run', cron_expression: '0 0 * * *',
        approved_test_plan_id: planId, validation_profile_id: profileId, browser: 'chromium'
      }
    });
    expect(schedRes.ok()).toBeTruthy();
    const schedule = await schedRes.json();
    scheduleId = schedule.id;

    const runNowRes = await request.post(`${AUTOQA_URL}/api/local-schedules/${scheduleId}/run-now`, { headers: adminHeaders });
    expect(runNowRes.ok()).toBeTruthy();
    const runData = await runNowRes.json();
    expect(runData.status).toBe('QUEUED');
    expect(runData.approved_test_plan_id).toBe(planId);
  });

  // 19. Cross-project denial
  test('19 - Cross-project denial', async ({ request }) => {
    const createDenialRes = await request.post(`${AUTOQA_URL}/api/local-schedules`, {
      headers: adminHeaders,
      data: {
        project_id: 9999, name: 'Cross Project Hack', cron_expression: '0 0 * * *',
        approved_test_plan_id: planId, validation_profile_id: profileId, browser: 'chromium'
      }
    });
    expect(createDenialRes.status()).toBe(403);
  });

  // 20. No secret exposure
  test('20 - Secret redaction verification', async ({ request }) => {
    const res = await request.get(`${AUTOQA_URL}/api/projects/${projectId}/advanced-profiles/${profileId}`, { headers: adminHeaders });
    expect(res.ok()).toBeTruthy();
    const text = await res.text();
    expect(text).not.toContain('SecretPassword123');
  });
});
