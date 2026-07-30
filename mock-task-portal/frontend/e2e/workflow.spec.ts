/**
 * Playwright E2E workflow tests for Mock Task Portal.
 *
 * These tests drive the real frontend UI against the local backend.
 * Backend must be running on http://localhost:8001
 * Frontend must be running on http://localhost:5174
 *
 * Run with: npx playwright test
 */

import { test, expect, type Page } from '@playwright/test';

const BACKEND = 'http://localhost:8001';

// ── API helpers ──
async function apiLogin(username: string, password: string) {
  const res = await fetch(`${BACKEND}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) throw new Error(`Login failed: ${res.status}`);
  return res.json();
}

async function apiPatch(path: string, token: string, body: object) {
  const res = await fetch(`${BACKEND}/api${path}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(`PATCH ${path} failed ${res.status}: ${JSON.stringify(err)}`);
  }
  return res.json();
}

async function apiPost(path: string, token: string, body: object) {
  const res = await fetch(`${BACKEND}/api${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(`POST ${path} failed ${res.status}: ${JSON.stringify(err)}`);
  }
  return res.json();
}

async function apiGet(path: string, token: string) {
  const res = await fetch(`${BACKEND}/api${path}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error(`GET ${path} failed: ${res.status}`);
  return res.json();
}

// ── UI helpers ──
async function uiLogin(page: Page, username: string, password: string) {
  await page.goto('/login');
  await page.locator('#username').fill(username);
  await page.locator('#password').fill(password);
  await page.locator('#login-submit').click();
  await page.waitForURL('/');
}

// ── Tests ──

test('1. Login page renders and login succeeds', async ({ page }) => {
  await page.goto('/login');
  await expect(page.locator('h1')).toContainText('Mock Task Portal');
  await page.locator('#username').fill('admin');
  await page.locator('#password').fill('Admin@Demo123');
  await page.locator('#login-submit').click();
  await page.waitForURL('/');
  await expect(page).toHaveURL('/');
});

test('2. Login with wrong password shows error', async ({ page }) => {
  await page.goto('/login');
  await page.locator('#username').fill('admin');
  await page.locator('#password').fill('wrongpassword');
  await page.locator('#login-submit').click();
  await expect(page.locator('.alert-error')).toBeVisible();
});

test('3. Create task via UI', async ({ page }) => {
  const code = `UI-${Date.now()}`;
  await uiLogin(page, 'admin', 'Admin@Demo123');
  await page.goto('/tasks/create');
  await page.locator('#task-code').fill(code);
  await page.locator('#task-project').fill('Demo ERP');
  await page.locator('#task-module').fill('E2E Module');
  await page.locator('#task-title').fill('E2E UI Create Task');
  await page.locator('#task-developer').fill('dev1');
  await page.locator('#task-tester').fill('tester1');
  await page.locator('#create-task-submit').click();
  // Wait for success alert to appear (task was created)
  await expect(page.locator('.alert-success')).toBeVisible({ timeout: 10_000 });
  await expect(page.locator('.alert-success')).toContainText('created successfully');
});

test('4. Developer moves task to TESTING_L2', async ({ page }) => {
  // Setup via API: create task and move to ASSIGNED
  const adminLogin = await apiLogin('admin', 'Admin@Demo123');
  const adminToken = adminLogin.access_token;

  const task = await apiPost('/tasks', adminToken, {
    task_code: `E2E-DEV-${Date.now()}`,
    project_name: 'Demo ERP',
    module_name: 'E2E',
    title: 'Dev To Testing L2 Task',
    assigned_developer: 'dev1',
    priority: 'HIGH',
  });

  await apiPatch(`/tasks/${task.id}/status`, adminToken, { new_status: 'ASSIGNED' });

  const devLogin = await apiLogin('dev1', 'Dev@Demo123');
  const devToken = devLogin.access_token;
  await apiPatch(`/tasks/${task.id}/status`, devToken, { new_status: 'IN_PROGRESS' });
  await apiPatch(`/tasks/${task.id}/status`, devToken, { new_status: 'TESTING_L1' });

  // Now use UI to move to TESTING_L2 as developer
  await uiLogin(page, 'dev1', 'Dev@Demo123');
  await page.goto(`/tasks/${task.id}`);
  await page.locator('#btn-change-status').click();
  await page.locator('#modal-new-status').selectOption('TESTING_L2');
  await page.locator('#modal-reason').fill('Ready for L2 QA');
  await page.locator('#modal-confirm-status').click();
  await expect(page.locator('.badge-TESTING_L2')).toBeVisible();
});

test('5. Tester sees task in Testing L2 queue', async ({ page }) => {
  // Create a fresh TESTING_L2 task via API to ensure the queue is not empty
  const adminLogin = await apiLogin('admin', 'Admin@Demo123');
  const adminToken = adminLogin.access_token;
  const task = await apiPost('/tasks', adminToken, {
    task_code: `E2E-L2-${Date.now()}`,
    project_name: 'Demo ERP',
    module_name: 'L2 Queue',
    title: 'L2 Queue Verification Task',
    assigned_developer: 'dev1',
    assigned_tester: 'tester1',
    priority: 'HIGH',
  });
  await apiPatch(`/tasks/${task.id}/status`, adminToken, { new_status: 'ASSIGNED' });
  const devToken = (await apiLogin('dev1', 'Dev@Demo123')).access_token;
  await apiPatch(`/tasks/${task.id}/status`, devToken, { new_status: 'IN_PROGRESS' });
  await apiPatch(`/tasks/${task.id}/status`, devToken, { new_status: 'TESTING_L1' });
  await apiPatch(`/tasks/${task.id}/status`, devToken, { new_status: 'TESTING_L2' });

  await uiLogin(page, 'tester1', 'Test@Demo123');
  await page.goto('/testing-l2-queue');
  // Wait for table to be present (page loads tasks asynchronously)
  await page.waitForSelector('table tbody tr', { timeout: 10_000 });
  const rows = page.locator('table tbody tr');
  const count = await rows.count();
  expect(count).toBeGreaterThanOrEqual(1);
  const firstRow = rows.first();
  await expect(firstRow.locator('.badge-TESTING_L2')).toBeVisible();
});

test('6. Tester records PASS — task moves to QA_PASSED', async ({ page }) => {
  // Create a task via API and advance to TESTING_L2
  const adminLogin = await apiLogin('admin', 'Admin@Demo123');
  const adminToken = adminLogin.access_token;
  const task = await apiPost('/tasks', adminToken, {
    task_code: `E2E-PASS-${Date.now()}`,
    project_name: 'Demo ERP',
    module_name: 'E2E',
    title: 'QA Pass Test',
    assigned_developer: 'dev1',
    assigned_tester: 'tester1',
    priority: 'MEDIUM',
  });
  await apiPatch(`/tasks/${task.id}/status`, adminToken, { new_status: 'ASSIGNED' });
  const devToken = (await apiLogin('dev1', 'Dev@Demo123')).access_token;
  await apiPatch(`/tasks/${task.id}/status`, devToken, { new_status: 'IN_PROGRESS' });
  await apiPatch(`/tasks/${task.id}/status`, devToken, { new_status: 'TESTING_L1' });
  await apiPatch(`/tasks/${task.id}/status`, devToken, { new_status: 'TESTING_L2' });

  // Tester records PASS via UI
  await uiLogin(page, 'tester1', 'Test@Demo123');
  await page.goto(`/tasks/${task.id}`);
  await page.locator('#btn-qa-result').click();
  await page.locator('#qa-pass').click();
  await page.locator('#modal-confirm-qa').click();
  await expect(page.locator('.badge-QA_PASSED')).toBeVisible();
});

test('7. FAIL task moves to REWORK', async ({ page }) => {
  const adminLogin = await apiLogin('admin', 'Admin@Demo123');
  const adminToken = adminLogin.access_token;
  const task = await apiPost('/tasks', adminToken, {
    task_code: `E2E-FAIL-${Date.now()}`,
    project_name: 'Demo ERP',
    module_name: 'E2E',
    title: 'QA Fail Test',
    assigned_developer: 'dev1',
    assigned_tester: 'tester1',
    priority: 'MEDIUM',
  });
  await apiPatch(`/tasks/${task.id}/status`, adminToken, { new_status: 'ASSIGNED' });
  const devToken = (await apiLogin('dev1', 'Dev@Demo123')).access_token;
  await apiPatch(`/tasks/${task.id}/status`, devToken, { new_status: 'IN_PROGRESS' });
  await apiPatch(`/tasks/${task.id}/status`, devToken, { new_status: 'TESTING_L1' });
  await apiPatch(`/tasks/${task.id}/status`, devToken, { new_status: 'TESTING_L2' });

  // Tester records FAIL via UI
  await uiLogin(page, 'tester1', 'Test@Demo123');
  await page.goto(`/tasks/${task.id}`);
  await page.locator('#btn-qa-result').click();
  await page.locator('#qa-fail').click();
  await page.locator('#modal-qa-reason').fill('Button click not working');
  await page.locator('#modal-confirm-qa').click();
  await expect(page.locator('.badge-QA_FAILED')).toBeVisible();

  // Move to REWORK via status change
  await page.locator('#btn-change-status').click();
  await page.locator('#modal-new-status').selectOption('REWORK');
  await page.locator('#modal-confirm-status').click();
  await expect(page.locator('.badge-REWORK')).toBeVisible();
});

test('8. Delivery user completes task', async ({ page }) => {
  const adminLogin = await apiLogin('admin', 'Admin@Demo123');
  const adminToken = adminLogin.access_token;
  const task = await apiPost('/tasks', adminToken, {
    task_code: `E2E-DEL-${Date.now()}`,
    project_name: 'Demo ERP',
    module_name: 'E2E',
    title: 'Delivery Test',
    assigned_developer: 'dev1',
    priority: 'LOW',
  });
  const devToken = (await apiLogin('dev1', 'Dev@Demo123')).access_token;
  const testerToken = (await apiLogin('tester1', 'Test@Demo123')).access_token;
  await apiPatch(`/tasks/${task.id}/status`, adminToken, { new_status: 'ASSIGNED' });
  await apiPatch(`/tasks/${task.id}/status`, devToken, { new_status: 'IN_PROGRESS' });
  await apiPatch(`/tasks/${task.id}/status`, devToken, { new_status: 'TESTING_L1' });
  await apiPatch(`/tasks/${task.id}/status`, devToken, { new_status: 'TESTING_L2' });
  await apiPost(`/tasks/${task.id}/qa-result`, testerToken, { result: 'PASS' });
  await apiPatch(`/tasks/${task.id}/status`, adminToken, { new_status: 'DELIVERY_READY' });

  // Delivery user completes via UI
  await uiLogin(page, 'delivery1', 'Del@Demo123');
  await page.goto(`/tasks/${task.id}`);
  await page.locator('#btn-change-status').click();
  await page.locator('#modal-new-status').selectOption('DELIVERY_COMPLETED');
  await page.locator('#modal-confirm-status').click();
  await expect(page.locator('.badge-DELIVERY_COMPLETED')).toBeVisible();
});
