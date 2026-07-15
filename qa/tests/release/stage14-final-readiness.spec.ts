import { expect, test, type Page, type Route } from '@playwright/test';

type Role = 'ADMIN' | 'VIEWER';

const operators = {
  ADMIN: { id: 1, username: 'release-admin', display_name: 'Release Admin', role: 'ADMIN', is_active: true, must_change_password: false },
  VIEWER: { id: 2, username: 'release-viewer', display_name: 'Release Viewer', role: 'VIEWER', is_active: true, must_change_password: false },
};

const health = {
  status: 'ok', environment: 'local-release', safe_mode: true, debug: false,
  production_execution_enabled: false, real_target_execution_enabled: false, tls_verification_enabled: true,
  database: { ready: true, migrations_current: true, immutable_triggers_installed: true },
  storage: { execution_artifacts: true, evidence: true, report_exports: true, runtime: true, backups: true },
  worker: { active_count: 1, heartbeat_ok: true }, queue: { queued: 2, running: 0, terminal: 18 },
  frontend: { available: true }, disk: { warning: false, free_mb: 4096 },
  playwright: { installed: true, chromium_available: true },
};

async function mockReleaseApi(page: Page) {
  let role: Role = 'ADMIN';
  let failHealth = false;
  let backupCount = 0;
  let cleanupCount = 0;
  await page.exposeFunction('setStage14Role', (value: Role) => { role = value; });
  await page.exposeFunction('setStage14HealthError', (value: boolean) => { failHealth = value; });
  await page.exposeFunction('stage14Actions', () => ({ backupCount, cleanupCount }));
  await page.route('**/api/**', async (route: Route) => {
    const request = route.request();
    const path = new URL(request.url()).pathname;
    if (path === '/api/auth/me') return route.fulfill({ json: operators[role] });
    if (path === '/api/auth/csrf') return route.fulfill({ json: { csrf_token: 'fixture-csrf-value' } });
    if (path === '/api/system/health') {
      await new Promise((resolve) => setTimeout(resolve, 250));
      return failHealth ? route.fulfill({ status: 503, json: { detail: 'Diagnostics unavailable.' } }) : route.fulfill({ json: health });
    }
    if (path === '/api/system/backups' && request.method() === 'GET') return route.fulfill({ json: [] });
    if (path === '/api/system/backups' && request.method() === 'POST') {
      const body = request.postDataJSON();
      expect(body.confirmation).toBe('CREATE LOCAL BACKUP');
      backupCount += 1;
      return route.fulfill({ status: 201, json: { backup_id: 'AUTOQA-20260713T120000-000001Z', file_count: 8, total_bytes: 2048, manifest_sha256: 'a'.repeat(64) } });
    }
    if (path === '/api/system/cleanup-preview') return route.fulfill({ json: { dry_run: true, candidate_files: 3, candidate_bytes: 3072, deleted_files: 0, deleted_bytes: 0, records_removed: { connection_checks: 1, expired_sessions: 2, completed_jobs: 1 }, categories: { report_exports: 3 }, protected: { active_run_artifacts: true, audit_history: true, password_history: true, immutable_histories: true } } });
    if (path === '/api/system/cleanup' && request.method() === 'POST') {
      const body = request.postDataJSON();
      expect(body.confirmation).toBe('DELETE RETAINED FILES');
      cleanupCount += 1;
      return route.fulfill({ json: { dry_run: false, candidate_files: 3, candidate_bytes: 3072, deleted_files: 3, deleted_bytes: 3072, records_removed: {}, categories: {}, protected: {} } });
    }
    return route.fulfill({ status: 503, json: { detail: 'Fixture endpoint intentionally empty.' } });
  });
}

test('Stage 14 final readiness health maintenance safety and responsive regression', async ({ page }) => {
  const consoleErrors: string[] = [];
  page.on('console', (message) => { if (message.type() === 'error' && !message.text().includes('status of 503')) consoleErrors.push(message.text()); });
  await mockReleaseApi(page);
  const navigation = page.goto('/');
  await expect(page.getByText('Loading system health...')).toBeVisible();
  await navigation;

  const panel = page.locator('#system-health');
  await panel.scrollIntoViewIfNeeded();
  await expect(panel.getByRole('heading', { name: 'Final Release Readiness' })).toBeVisible();
  await expect(panel.getByText('Ready', { exact: true }).first()).toBeVisible();
  await expect(panel.getByText('Online')).toBeVisible();
  await expect(panel.getByText('2 queued')).toBeVisible();
  await expect(panel.getByText('Production execution').locator('strong')).toHaveText('Blocked');
  await expect(panel.getByText('Real target execution').locator('strong')).toHaveText('Disabled');
  await expect(panel.getByText('No validated backups recorded yet.')).toBeVisible();
  await expect(panel.getByText(/3 files \(3.0 KB\) in the current dry-run/)).toBeVisible();

  const backupButton = panel.getByRole('button', { name: 'Create Backup' });
  const cleanupButton = panel.getByRole('button', { name: 'Apply Cleanup' });
  await expect(backupButton).toBeDisabled();
  await expect(cleanupButton).toBeDisabled();
  await panel.getByLabel('Type CREATE LOCAL BACKUP').fill('wrong confirmation');
  await panel.getByLabel('Type DELETE RETAINED FILES').fill('wrong confirmation');
  await expect.poll(async () => page.evaluate(() => (window as any).stage14Actions())).toEqual({ backupCount: 0, cleanupCount: 0 });
  await panel.getByLabel('Type CREATE LOCAL BACKUP').fill('CREATE LOCAL BACKUP');
  await backupButton.click();
  await expect(panel.getByText(/created and checksummed/)).toBeVisible();
  await panel.getByLabel('Type DELETE RETAINED FILES').fill('DELETE RETAINED FILES');
  await cleanupButton.click();
  await expect(panel.getByText('Cleanup completed: 3 files removed.')).toBeVisible();

  for (const name of ['Test Management', 'Connection Targets', 'Automated Runs', 'Defects', 'Management Reports', 'System Health']) {
    await expect(page.getByRole('link', { name, exact: true })).toBeVisible();
  }
  const reportsLink = page.getByRole('link', { name: 'Management Reports', exact: true });
  const healthLink = page.getByRole('link', { name: 'System Health', exact: true });
  await reportsLink.focus();
  await expect(reportsLink).toBeFocused();
  await page.keyboard.press('Tab');
  await expect(healthLink).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(page).toHaveURL(/#system-health$/);
  for (const width of [320, 375, 768, 1024, 1440]) {
    await page.setViewportSize({ width, height: 900 });
    await panel.scrollIntoViewIfNeeded();
    await expect(panel).toBeVisible();
    const overflow = await page.evaluate(() => Array.from(document.querySelectorAll('#system-health *')).some((element) => {
      const rect = element.getBoundingClientRect();
      return rect.right > document.documentElement.clientWidth + 1 || rect.left < -1;
    }));
    expect(overflow, `system health overflow at ${width}px`).toBe(false);
  }

  const panelText = (await panel.innerText()).toLowerCase();
  for (const forbidden of ['d:\\', 'c:\\users', 'password', 'token', 'cookie', 'authorization', 'traceback']) expect(panelText).not.toContain(forbidden);
  const storage = await page.evaluate(() => `${JSON.stringify(localStorage)} ${JSON.stringify(sessionStorage)}`.toLowerCase());
  expect(storage).not.toContain('password'); expect(storage).not.toContain('bearer'); expect(storage).not.toContain('csrf');

  await page.evaluate(() => (window as any).setStage14Role('VIEWER'));
  await page.reload();
  await panel.scrollIntoViewIfNeeded();
  await expect(panel.getByText('Backup and cleanup controls require ADMIN access.')).toBeVisible();
  await expect(panel.getByRole('button', { name: 'Apply Cleanup' })).toHaveCount(0);

  await page.evaluate(() => (window as any).setStage14HealthError(true));
  await page.reload();
  await panel.scrollIntoViewIfNeeded();
  await expect(panel.getByRole('alert')).toContainText('Diagnostics unavailable.');
  await expect(panel.getByRole('button', { name: 'Retry' })).toBeVisible();
  expect(consoleErrors).toEqual([]);
});
