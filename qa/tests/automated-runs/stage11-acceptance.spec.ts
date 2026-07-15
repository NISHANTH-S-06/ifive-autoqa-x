import { expect, test } from '@playwright/test';
import http from 'node:http';

const tester = { id: 2, username: 'tester', display_name: 'Tester User', role: 'TESTER', is_active: true, must_change_password: false };
const approver = { id: 3, username: 'approver', display_name: 'Approver User', role: 'APPROVER', is_active: true, must_change_password: false };

function startMockTarget() {
  const server = http.createServer((_request, response) => {
    response.writeHead(200, { 'Content-Type': 'text/html' });
    response.end('<title>Stage11 Mock</title><main id="ready">Ready local target</main>');
  });
  return new Promise<{ server: http.Server; url: string }>((resolve) => {
    server.listen(0, '127.0.0.1', () => {
      const address = server.address();
      if (address && typeof address === 'object') resolve({ server, url: `http://127.0.0.1:${address.port}` });
    });
  });
}

test('Stage 11 readiness and controlled acceptance workflow', async ({ page }) => {
  const { server, url } = await startMockTarget();
  let currentOperator = tester;
  const target: any = {
    id: 11, target_key: 'S11-LOCAL', name: 'Stage 11 Local Mock', description: null, environment_type: 'LOCAL', base_url: url,
    normalized_scheme: 'http', normalized_host: '127.0.0.1', normalized_port: Number(url.split(':').pop()), normalized_origin: url,
    allowed_probe_paths: ['/'], tls_required: false, tls_verify: true, connection_timeout_seconds: 3,
    lifecycle_state: 'APPROVED', enabled: true, owner_operator_id: null, created_by: tester.id, reviewed_by: approver.id, approved_by: approver.id,
    created_at: '2026-07-13', updated_at: '2026-07-13', submitted_at: '2026-07-13', approved_at: '2026-07-13', rejected_at: null, disabled_at: null, archived_at: null,
    rejection_reason: null, last_check_at: null, last_check_status: null, execution_enabled: true, execution_submitted_by: tester.id, execution_submitted_at: '2026-07-13',
    execution_approved_by: approver.id, execution_approved_at: '2026-07-13', version: 4,
  };
  const testCase = { id: 21, project_id: 1, module_id: 1, suite_id: 1, case_key: 'S11-CASE', title: 'Read-only acceptance', objective: null, preconditions: null, test_type: 'SMOKE', priority: 'MEDIUM', severity: 'MEDIUM', status: 'ACTIVE', lifecycle_state: 'APPROVED', owner_operator_id: null, created_by: tester.id, reviewed_by: approver.id, approved_by: approver.id, created_at: '2026-07-13', updated_at: '2026-07-13', reviewed_at: '2026-07-13', approved_at: '2026-07-13', archived_at: null, current_version: 2, steps: [], tags: [] };
  let runs: any[] = [];
  let workers: any[] = [];
  let steps: any[] = [];
  let artifacts: any[] = [];

  await page.route('**/api/**', async (route) => {
    const request = route.request();
    const path = new URL(request.url()).pathname;
    const method = request.method();
    if (path === '/api/auth/me') return route.fulfill({ json: currentOperator });
    if (path === '/api/auth/csrf') return route.fulfill({ json: { csrf_token: 'stage11-csrf' } });
    if (path === '/api/projects') return route.fulfill({ json: [] });
    if (path === '/api/dashboard/summary') return route.fulfill({ json: { total_projects: 0, active_projects: 0, total_runs: 0, passed_runs: 0, failed_runs: 0, queued_runs: 0, running_runs: 0, pass_rate: 0, total_tests: 0, average_duration_seconds: 0, recent_runs: [] } });
    if (path.startsWith('/api/test-runs') || path.startsWith('/api/operators') || path.startsWith('/api/audit') || path.startsWith('/api/auth/sessions')) return route.fulfill({ json: [] });
    if (path.startsWith('/api/test-projects')) return route.fulfill({ json: { items: [], page: { limit: 50, offset: 0, total: 0 } } });
    if (path.startsWith('/api/test-modules') || path.startsWith('/api/test-suites') || path.startsWith('/api/manual-test-runs')) return route.fulfill({ json: [] });
    if (path.startsWith('/api/test-cases')) return route.fulfill({ json: { items: [testCase], page: { limit: 100, offset: 0, total: 1 } } });
    if (path === '/api/connection-targets') return route.fulfill({ json: { items: [target], page: { limit: 50, offset: 0, total: 1 } } });
    if (path === '/api/automated-runs/readiness') return route.fulfill({ json: { active_admin_count: 0, admin_prerequisite_met: false, real_target_authorized: false, real_target_status: 'PENDING_EXPLICIT_NON_PRODUCTION_AUTHORIZATION', dns_pinning_status: 'ENFORCED', runtime_secret_status: 'PENDING_SAFE_EPHEMERAL_INPUT', allowed_risk_levels: ['READ_ONLY', 'SAFE_INTERACTION'], blocked_risk_levels: ['MUTATING', 'DESTRUCTIVE'] } });
    if (path === '/api/automated-runs' && method === 'GET') return route.fulfill({ json: { items: runs, page: { limit: 50, offset: 0, total: runs.length } } });
    if (path === '/api/automated-runs' && method === 'POST') {
      const body = request.postDataJSON();
      const run = { id: 1, run_key: 'ARUN-S11', name: body.name, description: null, target_id: target.id, target_version: 4, target_origin: url, status: 'DRAFT', risk_level: 'READ_ONLY', preflight_status: 'PENDING', dns_pinning_status: 'ENFORCED', runtime_secret_status: 'NOT_REQUIRED', created_by: tester.id, submitted_by: null, approved_by: null, queued_by: null, cancelled_by: null, worker_key: null, timeout_seconds: body.timeout_seconds, max_retries: 1, attempt_count: 0, total_steps: 2, completed_steps: 0, failed_steps: 0, failure_classification: null, safe_error_message: null, created_at: '2026-07-13', updated_at: '2026-07-13', progress: '0/2' };
      runs = [run];
      return route.fulfill({ status: 201, json: run });
    }
    const runMatch = path.match(/\/api\/automated-runs\/(\d+)(?:\/([\w-]+))?/);
    if (runMatch) {
      const run = runs[0];
      const action = runMatch[2];
      if (action === 'cases') return route.fulfill({ json: [{ id: 1, run_id: run.id, test_case_id: testCase.id, test_case_version: 2, status: run.status === 'PASSED' ? 'PASSED' : 'NOT_RUN', failure_classification: null, safe_error_message: null }] });
      if (action === 'steps') return route.fulfill({ json: steps });
      if (action === 'artifacts') return route.fulfill({ json: artifacts });
      if (action === 'preflight') return route.fulfill({ json: { run_id: run.id, status: workers.length ? 'PASS' : 'FAIL', checks: { worker_available: workers.length > 0, dns_pinning_enforced: true, runtime_secret_not_persisted: true }, risk_level: 'READ_ONLY', dns_pinning_status: 'ENFORCED', runtime_secret_status: 'NOT_REQUIRED', safe_message: null } });
      if (action === 'submit') run.status = 'SUBMITTED';
      if (action === 'approve') run.status = 'APPROVED';
      if (action === 'queue') { run.status = 'QUEUED'; run.preflight_status = 'PASS'; }
      if (action === 'cancel') run.status = 'CANCELLED';
      return route.fulfill({ json: run });
    }
    if (path === '/api/execution-workers' && method === 'GET') return route.fulfill({ json: workers });
    if (path === '/api/execution-workers/heartbeat') { workers = [{ id: 1, worker_key: 'local-stage10-worker', status: 'IDLE', max_concurrency: 1, current_run_id: null, heartbeat_at: '2026-07-13' }]; return route.fulfill({ json: workers[0] }); }
    if (path === '/api/execution-workers/run-next') {
      const run = runs[0];
      run.status = 'PASSED'; run.completed_steps = 2; run.progress = '2/2'; run.preflight_status = 'PASS';
      steps = [{ id: 1, run_case_id: 1, step_number: 1, action_type: 'NAVIGATE', selector: null, value_redacted: null, expected_redacted: '/', status: 'PASSED', failure_classification: null, safe_error_message: null, duration_ms: 2 }];
      artifacts = [{ id: 1, run_id: run.id, run_case_id: null, step_result_id: null, artifact_type: 'SUMMARY', original_filename: 'run-summary.json', mime_type: 'application/json', size_bytes: 80, sha256: 'abcdef123456abcdef123456abcdef123456abcdef123456abcdef123456abcd', safe: true, created_at: '2026-07-13' }];
      return route.fulfill({ json: run });
    }
    return route.fulfill({ json: {} });
  });

  try {
    await page.goto('/');
    await page.getByRole('link', { name: 'Automated Runs' }).click();
    const panel = page.locator('#automated-runs');
    await expect(panel.getByText('Stage 11 Readiness')).toBeVisible();
    await expect(panel.getByText('Pending (0)')).toBeVisible();
    await expect(panel.getByText('ENFORCED')).toBeVisible();
    await panel.getByLabel('Automation label').fill('Stage 11 local acceptance');
    await panel.locator('fieldset input[type="checkbox"]').first().check();
    await panel.getByRole('button', { name: 'Create Run' }).click();
    await panel.getByRole('button', { name: 'Submit' }).click();
    currentOperator = approver;
    await page.reload();
    await page.getByRole('link', { name: 'Automated Runs' }).click();
    await panel.getByRole('button', { name: 'Approve' }).click();
    await panel.getByRole('button', { name: 'Start Controlled Acceptance' }).click();
    await expect(panel.getByText('Controlled acceptance completed ARUN-S11 as PASSED.')).toBeVisible();
    await panel.getByRole('button', { name: 'Open' }).click();
    await expect(panel.getByText('Preflight PASS: READ_ONLY, DNS ENFORCED, secrets NOT_REQUIRED')).toBeVisible();
    const storage = await page.evaluate(() => JSON.stringify({ localStorage, sessionStorage }));
    expect(storage.toLowerCase()).not.toContain('password');
    expect(storage.toLowerCase()).not.toContain('token');
    expect(storage.toLowerCase()).not.toContain('cookie');
  } finally {
    await new Promise<void>((resolve) => server.close(() => resolve()));
  }
});
