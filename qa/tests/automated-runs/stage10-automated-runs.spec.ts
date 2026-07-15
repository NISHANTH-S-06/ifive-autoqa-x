import { expect, test } from '@playwright/test';
import http from 'node:http';

const tester = { id: 2, username: 'tester', display_name: 'Tester User', role: 'TESTER', is_active: true, must_change_password: false };
const approver = { id: 3, username: 'approver', display_name: 'Approver User', role: 'APPROVER', is_active: true, must_change_password: false };

function startMockTarget() {
  const server = http.createServer((request, response) => {
    if (request.url === '/redirect') {
      response.writeHead(302, { Location: 'http://example.com/escape' });
      response.end();
      return;
    }
    response.writeHead(200, { 'Content-Type': 'text/html', 'Set-Cookie': 'unsafe=session' });
    response.end('<title>Stage10 Mock</title><main id="ready">Ready local target</main>');
  });
  return new Promise<{ server: http.Server; url: string }>((resolve) => {
    server.listen(0, '127.0.0.1', () => {
      const address = server.address();
      if (address && typeof address === 'object') resolve({ server, url: `http://127.0.0.1:${address.port}` });
    });
  });
}

test('Stage 10 controlled automated execution workflow', async ({ page }) => {
  const { server, url } = await startMockTarget();
  let currentOperator = tester;
  const target: any = {
    id: 10, target_key: 'S10-LOCAL', name: 'Stage 10 Local Mock', description: null, environment_type: 'LOCAL', base_url: url,
    normalized_scheme: 'http', normalized_host: '127.0.0.1', normalized_port: Number(url.split(':').pop()), normalized_origin: url,
    allowed_probe_paths: ['/', '/redirect'], tls_required: false, tls_verify: true, connection_timeout_seconds: 3,
    lifecycle_state: 'APPROVED', enabled: true, owner_operator_id: null, created_by: tester.id, reviewed_by: approver.id, approved_by: approver.id,
    created_at: '2026-07-13', updated_at: '2026-07-13', submitted_at: '2026-07-13', approved_at: '2026-07-13', rejected_at: null, disabled_at: null, archived_at: null,
    rejection_reason: null, last_check_at: null, last_check_status: null, execution_enabled: false, execution_submitted_by: null, execution_submitted_at: null,
    execution_approved_by: null, execution_approved_at: null, version: 3,
  };
  const testCase = { id: 20, project_id: 1, module_id: 1, suite_id: 1, case_key: 'S10-CASE', title: 'Structured local automation', objective: null, preconditions: null, test_type: 'SMOKE', priority: 'MEDIUM', severity: 'MEDIUM', status: 'ACTIVE', lifecycle_state: 'APPROVED', owner_operator_id: null, created_by: tester.id, reviewed_by: approver.id, approved_by: approver.id, created_at: '2026-07-13', updated_at: '2026-07-13', reviewed_at: '2026-07-13', approved_at: '2026-07-13', archived_at: null, current_version: 2, steps: [], tags: [] };
  let runs: any[] = [];
  let steps: any[] = [];
  let artifacts: any[] = [];
  let workers: any[] = [];

  await page.route('**/api/**', async (route) => {
    const request = route.request();
    const path = new URL(request.url()).pathname;
    const method = request.method();
    if (path === '/api/auth/me') return route.fulfill({ json: currentOperator });
    if (path === '/api/auth/csrf') return route.fulfill({ json: { csrf_token: 'stage10-csrf' } });
    if (path === '/api/projects') return route.fulfill({ json: [] });
    if (path === '/api/dashboard/summary') return route.fulfill({ json: { total_projects: 0, active_projects: 0, total_runs: 0, passed_runs: 0, failed_runs: 0, queued_runs: 0, running_runs: 0, pass_rate: 0, total_tests: 0, average_duration_seconds: 0, recent_runs: [] } });
    if (path.startsWith('/api/test-runs')) return route.fulfill({ json: [] });
    if (path.startsWith('/api/operators') || path.startsWith('/api/audit')) return route.fulfill({ json: [] });
    if (path.startsWith('/api/security')) return route.fulfill({ json: { active_operators: 2, locked_operators: 0, must_change_password_count: 0, active_sessions: 1, failed_logins_last_24h: 0, audit_chain_valid: true } });
    if (path.startsWith('/api/auth/sessions')) return route.fulfill({ json: [] });
    if (path.startsWith('/api/test-projects')) return route.fulfill({ json: { items: [], page: { limit: 50, offset: 0, total: 0 } } });
    if (path.startsWith('/api/test-modules') || path.startsWith('/api/test-suites') || path.startsWith('/api/manual-test-runs')) return route.fulfill({ json: [] });
    if (path.startsWith('/api/test-cases')) return route.fulfill({ json: { items: [testCase], page: { limit: 100, offset: 0, total: 1 } } });
    if (path === '/api/connection-targets') return route.fulfill({ json: { items: [target], page: { limit: 50, offset: 0, total: 1 } } });
    if (path.endsWith('/execution-submit')) { target.execution_submitted_by = tester.id; target.execution_submitted_at = '2026-07-13'; target.execution_enabled = false; return route.fulfill({ json: target }); }
    if (path.endsWith('/execution-approve')) { target.execution_enabled = true; target.execution_approved_by = approver.id; target.execution_approved_at = '2026-07-13'; return route.fulfill({ json: target }); }
    if (path.includes('/connection-targets/') && (path.endsWith('/checks') || path.endsWith('/credential-profiles') || path.endsWith('/versions'))) return route.fulfill({ json: [] });
    if (path === '/api/automated-runs/readiness') return route.fulfill({ json: { active_admin_count: 0, admin_prerequisite_met: false, real_target_authorized: false, real_target_status: 'PENDING_EXPLICIT_NON_PRODUCTION_AUTHORIZATION', dns_pinning_status: 'ENFORCED', runtime_secret_status: 'PENDING_SAFE_EPHEMERAL_INPUT', allowed_risk_levels: ['READ_ONLY', 'SAFE_INTERACTION'], blocked_risk_levels: ['MUTATING', 'DESTRUCTIVE'] } });
    if (path === '/api/automated-runs' && method === 'GET') return route.fulfill({ json: { items: runs, page: { limit: 50, offset: 0, total: runs.length } } });
    if (path === '/api/automated-runs' && method === 'POST') {
      const body = request.postDataJSON();
      const run = { id: runs.length + 1, run_key: `ARUN-${runs.length + 1}`, name: body.name, description: null, target_id: body.target_id, target_version: 3, target_origin: url, status: 'DRAFT', risk_level: 'READ_ONLY', preflight_status: 'PENDING', dns_pinning_status: 'ENFORCED', runtime_secret_status: 'NOT_REQUIRED', created_by: tester.id, submitted_by: null, approved_by: null, queued_by: null, cancelled_by: null, worker_key: null, timeout_seconds: body.timeout_seconds, max_retries: 1, attempt_count: 0, total_steps: 4, completed_steps: 0, failed_steps: 0, failure_classification: null, safe_error_message: null, created_at: '2026-07-13', updated_at: '2026-07-13', progress: '0/4' };
      runs = [run, ...runs];
      return route.fulfill({ status: 201, json: run });
    }
    const runMatch = path.match(/\/api\/automated-runs\/(\d+)(?:\/(\w+))?/);
    if (runMatch) {
      const run = runs.find((item) => item.id === Number(runMatch[1]))!;
      const action = runMatch[2];
      if (action === 'cases') return route.fulfill({ json: [{ id: 1, run_id: run.id, test_case_id: testCase.id, test_case_version: 2, status: run.status === 'PASSED' ? 'PASSED' : 'NOT_RUN', failure_classification: null, safe_error_message: null }] });
      if (action === 'steps') return route.fulfill({ json: steps });
      if (action === 'artifacts') return route.fulfill({ json: artifacts });
      if (action === 'preflight') return route.fulfill({ json: { run_id: run.id, status: 'PASS', checks: { worker_available: true, dns_pinning_enforced: true }, risk_level: run.risk_level, dns_pinning_status: run.dns_pinning_status, runtime_secret_status: run.runtime_secret_status, safe_message: null } });
      if (action === 'submit') run.status = 'SUBMITTED';
      if (action === 'approve') run.status = 'APPROVED';
      if (action === 'queue') run.status = 'QUEUED';
      if (action === 'cancel') run.status = 'CANCELLED';
      if (action === 'retry') run.status = 'QUEUED';
      return route.fulfill({ json: run });
    }
    if (path === '/api/execution-workers' && method === 'GET') return route.fulfill({ json: workers });
    if (path === '/api/execution-workers/heartbeat') { workers = [{ id: 1, worker_key: 'local-stage10-worker', status: 'IDLE', max_concurrency: 1, current_run_id: null, heartbeat_at: '2026-07-13' }]; return route.fulfill({ json: workers[0] }); }
    if (path === '/api/execution-workers/run-next') {
      const run = runs.find((item) => item.status === 'QUEUED');
      if (!run) return route.fulfill({ json: null });
      run.status = 'PASSED'; run.completed_steps = 4; run.progress = '4/4'; run.worker_key = 'local-stage10-worker';
      steps = [1, 2, 3, 4].map((number) => ({ id: number, run_case_id: 1, step_number: number, action_type: number === 4 ? 'SCREENSHOT' : 'NAVIGATE', selector: null, value_redacted: null, expected_redacted: '/', status: 'PASSED', failure_classification: null, safe_error_message: null, duration_ms: 2 }));
      artifacts = [{ id: 1, run_id: run.id, run_case_id: 1, step_result_id: 4, artifact_type: 'SCREENSHOT', original_filename: 'step-4.png', mime_type: 'image/png', size_bytes: 68, sha256: 'abcdef123456abcdef123456abcdef123456abcdef123456abcdef123456abcd', safe: true, created_at: '2026-07-13' }];
      return route.fulfill({ json: run });
    }
    return route.fulfill({ json: {} });
  });

  try {
    await page.goto('/');
    await page.getByRole('link', { name: 'Connection Targets' }).click();
    await expect(page.getByText('Execution Disabled')).toBeVisible();
    await page.getByRole('button', { name: 'Submit Execution' }).click();
    await expect(page.getByText('Execution submit completed.')).toBeVisible();
    currentOperator = approver;
    await page.reload();
    await page.getByRole('link', { name: 'Connection Targets' }).click();
    await page.getByRole('button', { name: 'Approval' }).click();
    await page.getByRole('button', { name: 'Approve Execution' }).click();
    target.execution_enabled = true;
    target.execution_approved_by = approver.id;
    target.execution_approved_at = '2026-07-13';

    currentOperator = tester;
    await page.reload();
    await page.getByRole('link', { name: 'Automated Runs' }).click();
    const panel = page.locator('#automated-runs');
    await panel.getByLabel('Automation label').fill('Local structured run');
    await panel.locator('fieldset input[type="checkbox"]').first().check();
    await panel.getByRole('button', { name: 'Create Run' }).click();
    await expect(panel.getByText('ARUN-1')).toBeVisible();
    await panel.getByRole('button', { name: 'Submit' }).click();
    currentOperator = approver;
    await page.reload();
    await page.getByRole('link', { name: 'Automated Runs' }).click();
    await panel.getByRole('button', { name: 'Approve' }).click();
    await panel.getByRole('button', { name: 'Queue' }).click();
    await panel.getByRole('button', { name: 'Run Local Worker' }).click();
    await expect(panel.getByText('Worker completed ARUN-1 as PASSED.')).toBeVisible();
    await panel.getByRole('button', { name: 'Open' }).click();
    await expect(panel.getByText('SCREENSHOT', { exact: true }).first()).toBeVisible();
    await expect(panel.getByText(/abcdef123456/)).toBeVisible();
    const storage = await page.evaluate(() => JSON.stringify({ localStorage, sessionStorage }));
    expect(storage.toLowerCase()).not.toContain('password');
    expect(storage.toLowerCase()).not.toContain('token');
    expect(storage.toLowerCase()).not.toContain('cookie');
    await expect(page.getByText(url)).toBeVisible();
  } finally {
    await new Promise<void>((resolve) => server.close(() => resolve()));
  }
});
