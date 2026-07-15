import http from 'node:http';
import { expect, test, type Page, type Route } from '@playwright/test';

type Role = 'ADMIN' | 'TESTER' | 'APPROVER';
const admin = { id: 1, username: 'admin', display_name: 'Admin User', role: 'ADMIN', is_active: true, must_change_password: false };
const tester = { id: 2, username: 'tester', display_name: 'Tester User', role: 'TESTER', is_active: true, must_change_password: false };
const approver = { id: 3, username: 'approver', display_name: 'Approver User', role: 'APPROVER', is_active: true, must_change_password: false };

async function localTarget(): Promise<{ url: string; close: () => Promise<void> }> {
  const server = http.createServer((request, response) => {
    if (request.url === '/redirect') {
      response.writeHead(302, { Location: 'http://example.com/unsafe', 'Set-Cookie': 'unsafe=session' });
      response.end();
      return;
    }
    response.writeHead(200, { 'Content-Type': 'text/plain', 'Set-Cookie': 'unsafe=session', 'X-Visible': 'safe' });
    if (request.method === 'GET') response.end('body-not-for-ui');
    else response.end();
  });
  await new Promise<void>((resolve) => server.listen(0, '127.0.0.1', resolve));
  const address = server.address();
  if (!address || typeof address === 'string') throw new Error('Mock server did not start.');
  return { url: `http://127.0.0.1:${address.port}`, close: () => new Promise((resolve) => server.close(() => resolve())) };
}

async function mockStage9Api(page: Page) {
  let current: any = tester;
  let nextTarget = 1;
  let nextCheck = 1;
  let nextProfile = 1;
  const targets: any[] = [];
  const checks: any[] = [];
  const versions = new Map<number, any[]>();
  const profiles: any[] = [];
  await page.exposeFunction('setStage9Role', (role: Role) => { current = role === 'ADMIN' ? admin : role === 'APPROVER' ? approver : tester; });
  await page.route('**/api/**', async (route: Route) => {
    const url = new URL(route.request().url());
    const path = url.pathname;
    const method = route.request().method();
    let body: any = null;
    if (method !== 'GET') {
      try { body = route.request().postDataJSON(); }
      catch { body = null; }
    }
    if (path === '/api/auth/me') return route.fulfill({ json: current });
    if (path === '/api/auth/csrf') return route.fulfill({ json: { csrf_token: 'stage9-csrf' } });
    if (path.includes('/api/auth/sessions')) return route.fulfill({ json: [] });
    if (path.includes('/api/security/summary')) return route.fulfill({ json: { active_operators: 3, locked_operators: 0, must_change_password_count: 0, active_sessions: 1, failed_logins_last_24h: 0, audit_chain_valid: true } });
    if (path.includes('/api/security/operators') || path === '/api/operators' || path.includes('/api/audit/events')) return route.fulfill({ json: [] });
    if (path === '/api/projects' || path === '/api/test-runs') return route.fulfill({ json: [] });
    if (path.includes('/api/dashboard/summary')) return route.fulfill({ json: { total_projects: 0, active_projects: 0, total_runs: 0, passed_runs: 0, failed_runs: 0, queued_runs: 0, running_runs: 0, pass_rate: 0, total_tests: 0, average_duration_seconds: 0, recent_runs: [] } });
    if (path === '/api/test-projects') return route.fulfill({ json: { items: [], page: { limit: 50, offset: 0, total: 0 } } });
    if (path === '/api/test-modules' || path === '/api/test-suites' || path === '/api/manual-test-runs') return route.fulfill({ json: [] });
    if (path.startsWith('/api/test-cases')) return route.fulfill({ json: path.includes('/versions') ? [] : { items: [], page: { limit: 50, offset: 0, total: 0 } } });
    if (path === '/api/automated-runs/readiness') return route.fulfill({ json: { active_admin_count: 0, admin_prerequisite_met: false, real_target_authorized: false, real_target_status: 'PENDING_EXPLICIT_NON_PRODUCTION_AUTHORIZATION', dns_pinning_status: 'ENFORCED', runtime_secret_status: 'PENDING_SAFE_EPHEMERAL_INPUT', allowed_risk_levels: ['READ_ONLY', 'SAFE_INTERACTION'], blocked_risk_levels: ['MUTATING', 'DESTRUCTIVE'] } });
    if (path.match(/\/api\/automated-runs\/\d+\/preflight/)) return route.fulfill({ json: { run_id: 1, status: 'PENDING', checks: {}, risk_level: 'READ_ONLY', dns_pinning_status: 'ENFORCED', runtime_secret_status: 'NOT_REQUIRED', safe_message: null } });
    if (path.startsWith('/api/automated-runs')) return route.fulfill({ json: path.match(/\/automated-runs\/\d+\/(cases|steps|events|artifacts)/) ? [] : { items: [], page: { limit: 50, offset: 0, total: 0 } } });
    if (path.startsWith('/api/execution-workers')) return route.fulfill({ json: method === 'GET' ? [] : null });
    if (path.startsWith('/api/execution-artifacts')) return route.fulfill({ json: {} });
    if (path === '/api/connection-targets' && method === 'GET') return route.fulfill({ json: { items: targets, page: { limit: 50, offset: 0, total: targets.length } } });
    if (path === '/api/connection-targets' && method === 'POST') {
      const parsed = new URL((body as any).base_url);
      const origin = `${parsed.protocol}//${parsed.host}`;
      const item = { id: nextTarget++, lifecycle_state: 'DRAFT', enabled: false, created_by: current.id, reviewed_by: null, approved_by: null, created_at: new Date().toISOString(), updated_at: new Date().toISOString(), submitted_at: null, approved_at: null, rejected_at: null, disabled_at: null, archived_at: null, rejection_reason: null, last_check_at: null, last_check_status: null, version: 1, normalized_scheme: parsed.protocol.replace(':', ''), normalized_host: parsed.hostname, normalized_port: Number(parsed.port || 80), normalized_origin: origin, ...body };
      targets.push(item); versions.set(item.id, [{ id: 1, target_id: item.id, version_number: 1, snapshot_json: JSON.stringify(item), change_summary: 'Initial draft', created_by: current.id, created_at: new Date().toISOString(), source_state: 'DRAFT' }]);
      return route.fulfill({ status: 201, json: item });
    }
    const submit = path.match(/^\/api\/connection-targets\/(\d+)\/submit$/);
    if (submit) { const item = targets.find((entry) => entry.id === Number(submit[1])); item.lifecycle_state = 'IN_REVIEW'; item.version += 1; versions.get(item.id)?.push({ id: item.version, target_id: item.id, version_number: item.version, snapshot_json: JSON.stringify(item), change_summary: 'Submitted', created_by: current.id, created_at: new Date().toISOString(), source_state: 'IN_REVIEW' }); return route.fulfill({ json: item }); }
    const approve = path.match(/^\/api\/connection-targets\/(\d+)\/approve$/);
    if (approve) { const item = targets.find((entry) => entry.id === Number(approve[1])); if (item.created_by === current.id) return route.fulfill({ status: 400, json: { detail: 'Target creators cannot approve their own target.' } }); item.lifecycle_state = 'APPROVED'; item.enabled = true; item.approved_by = current.id; item.version += 1; versions.get(item.id)?.push({ id: item.version, target_id: item.id, version_number: item.version, snapshot_json: JSON.stringify(item), change_summary: 'Approved', created_by: current.id, created_at: new Date().toISOString(), source_state: 'APPROVED' }); return route.fulfill({ json: item }); }
    const versionList = path.match(/^\/api\/connection-targets\/(\d+)\/versions$/);
    if (versionList) return route.fulfill({ json: versions.get(Number(versionList[1])) ?? [] });
    const checkList = path.match(/^\/api\/connection-targets\/(\d+)\/checks$/);
    if (checkList && method === 'GET') return route.fulfill({ json: checks.filter((item) => item.target_id === Number(checkList[1])) });
    if (checkList && method === 'POST') {
      const status = (body as any).probe_path === '/redirect' ? 'REDIRECT_BLOCKED' : 'REACHABLE';
      const item = { id: nextCheck++, check_key: `CONN-${nextCheck}`, target_id: Number(checkList[1]), target_version: 3, method: (body as any).method, probe_path: (body as any).probe_path, requested_origin: targets[0].normalized_origin, resolved_addresses: ['127.0.0.1'], started_at: new Date().toISOString(), completed_at: new Date().toISOString(), duration_ms: 12, status, http_status: status === 'REACHABLE' ? 200 : 302, final_origin: targets[0].normalized_origin, redirect_count: status === 'REDIRECT_BLOCKED' ? 1 : 0, tls_protocol: null, tls_certificate_summary: null, response_headers: { 'content-type': 'text/plain', 'x-visible': 'safe' }, response_size_bytes: (body as any).method === 'GET' ? 12 : 0, error_category: status === 'REDIRECT_BLOCKED' ? 'REDIRECT' : null, safe_error_message: status === 'REDIRECT_BLOCKED' ? 'Redirect target origin is not approved.' : null, initiated_by: current.id, created_at: new Date().toISOString() };
      checks.unshift(item); targets[0].last_check_status = status; return route.fulfill({ status: 201, json: item });
    }
    const profileList = path.match(/^\/api\/connection-targets\/(\d+)\/credential-profiles$/);
    if (profileList && method === 'GET') return route.fulfill({ json: profiles.filter((item) => item.target_id === Number(profileList[1])) });
    if (profileList && method === 'POST') { const item = { id: nextProfile++, target_id: Number(profileList[1]), created_by: current.id, created_at: new Date().toISOString(), updated_at: new Date().toISOString(), last_used_at: null, enabled: true, ...body }; profiles.push(item); return route.fulfill({ status: 201, json: item }); }
    return route.fulfill({ json: {} });
  });
}

test('Stage 9 controlled connection target workflow', async ({ page }) => {
  const target = await localTarget();
  const errors: string[] = [];
  page.on('console', (message) => { if (message.type() === 'error') errors.push(message.text()); });
  try {
    await mockStage9Api(page);
    await page.goto('/');
    await page.getByRole('link', { name: /Connection Targets/i }).click();
    await page.getByLabel('Target key').fill('S9-LOCAL');
    await page.getByLabel('Name').fill('Stage 9 Local Target');
    await page.getByLabel('Base URL').fill(target.url);
    await page.getByLabel('Probe paths').fill('/\n/health\n/redirect');
    await page.getByRole('button', { name: 'Create Target Draft' }).click();
    await expect(page.getByText('Connection target draft created.')).toBeVisible();
    await page.getByRole('button', { name: 'Submit' }).click();
    await expect(page.getByRole('button', { name: 'Approve' })).toHaveCount(0);
    await page.evaluate(() => (window as any).setStage9Role('APPROVER'));
    await page.reload();
    await page.getByRole('button', { name: 'Approval' }).click();
    await page.getByRole('button', { name: 'Approve' }).click();
    await page.getByRole('button', { name: 'Targets' }).click();
    await page.getByRole('button', { name: 'Versions' }).click();
    await expect(page.getByRole('dialog', { name: 'Target Versions' }).locator('span').filter({ hasText: /^APPROVED$/ })).toBeVisible();
    await page.getByRole('button', { name: 'Close' }).click();
    await page.getByRole('button', { name: 'Checks' }).click();
    await page.getByRole('button', { name: /S9-LOCAL/ }).click();
    await page.getByLabel('Probe path').selectOption('/');
    await page.getByLabel('Method').selectOption('HEAD');
    await page.getByRole('button', { name: 'Start Check' }).click();
    await expect(page.getByText('Connection check REACHABLE.')).toBeVisible();
    await page.getByLabel('Method').selectOption('GET');
    await page.getByRole('button', { name: 'Start Check' }).click();
    await expect(page.getByText('text/plain').first()).toBeVisible();
    await expect(page.getByText('body-not-for-ui')).toHaveCount(0);
    await expect(page.getByText(/set-cookie/i)).toHaveCount(0);
    await page.getByLabel('Probe path').selectOption('/redirect');
    await page.getByRole('button', { name: 'Start Check' }).click();
    await expect(page.getByText('REDIRECT_BLOCKED').first()).toBeVisible();
    await expect(page.getByLabel('Method').locator('option', { hasText: 'POST' })).toHaveCount(0);
    await expect(page.getByLabel('Probe path').locator('option', { hasText: 'http://example.com' })).toHaveCount(0);
    await page.getByRole('button', { name: 'Credentials' }).click();
    await expect(page.getByText('No password or token is stored in AutoQA.')).toBeVisible();
    await expect(page.locator('#connection-targets input[type="password"]')).toHaveCount(0);
    await page.getByLabel('Profile name').fill('Prompt later');
    await page.getByLabel('Username hint').fill('qa-user');
    await page.getByRole('button', { name: 'Save Metadata' }).click();
    await expect(page.getByText('Credential metadata saved. No password or token was stored.')).toBeVisible();
    await page.getByRole('link', { name: /Test Management/i }).click();
    await expect(page.locator('#test-management')).toBeVisible();
    await expect(page.getByText('Approve and execute only allowlisted local AutoQA test suites.')).toBeVisible();
    for (const width of [320, 375, 768, 1024, 1440]) {
      await page.setViewportSize({ width, height: 900 });
      await expect(page.locator('#connection-targets')).toBeVisible();
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth);
      expect(overflow, `viewport ${width} overflow`).toBe(false);
    }
    const storage = await page.evaluate(() => `${JSON.stringify(localStorage)} ${JSON.stringify(sessionStorage)}`.toLowerCase());
    expect(storage).not.toContain('password');
    expect(storage).not.toContain('token');
    expect(storage).not.toContain('cookie');
    expect(errors).toEqual([]);
  } finally {
    await target.close();
  }
});
