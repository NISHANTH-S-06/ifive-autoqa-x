/**
 * Playwright E2E tests for Demo Product Website.
 * Drives real frontend (port 5175) against real backend (port 8002).
 */

import { test, expect, type Page } from '@playwright/test';

const BACKEND = 'http://localhost:8002';

async function apiLogin(username: string, password: string) {
  const res = await fetch(`${BACKEND}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) throw new Error(`Login failed: ${res.status}`);
  return res.json();
}

async function apiPatchSetting(key: string, enabled: boolean) {
  const adminLogin = await apiLogin('demo_admin', 'Admin@Demo123');
  const token = adminLogin.access_token;
  const res = await fetch(`${BACKEND}/api/demo-settings/${key}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ enabled }),
  });
  if (!res.ok) throw new Error(`Failed to toggle setting ${key}: ${res.status}`);
  return res.json();
}

async function uiLogin(page: Page, username: string, password: string) {
  await page.goto('/login');
  await page.locator('[data-testid="login-username"]').fill(username);
  await page.locator('[data-testid="login-password"]').fill(password);
  await page.locator('[data-testid="login-submit"]').click();
  await page.waitForURL('/dashboard');
}

test('1. Login and dashboard', async ({ page }) => {
  await uiLogin(page, 'demo_admin', 'Admin@Demo123');
  await expect(page.locator('h1')).toContainText('Dashboard');
  await expect(page.locator('text=Demo ERP System Overview')).toBeVisible();
});

test('2. Create employee PASS flow', async ({ page }) => {
  const empEmail = `test.pass.${Date.now()}@demo.local`;
  await uiLogin(page, 'demo_hr_user', 'Hr@Demo123');
  await page.goto('/hr/employees/new');

  await page.locator('[data-testid="employee-name"]').fill('Automated Test Employee');
  await page.locator('[data-testid="employee-email"]').fill(empEmail);
  await page.locator('[data-testid="employee-joining-date"]').fill('2026-03-01');
  await page.locator('[data-testid="employee-notes"]').fill('Playwright test creation notes');
  await page.locator('[data-testid="employee-save"]').click();

  // Verify success banner appears
  await expect(page.locator('[data-testid="employee-success"]')).toBeVisible();
  await expect(page.locator('[data-testid="employee-success"]')).toContainText('created successfully');

  // Verify employee appears in directory table
  await page.goto('/hr/employees');
  await page.waitForSelector('[data-testid="employee-table"]');
  await expect(page.locator('[data-testid="employee-table"]')).toContainText(empEmail);
});

test('3. Employee required-field validation', async ({ page }) => {
  await uiLogin(page, 'demo_hr_user', 'Hr@Demo123');
  await page.goto('/hr/employees/new');

  // Clear required fields and click submit
  await page.locator('[data-testid="employee-name"]').fill('');
  await page.locator('[data-testid="employee-email"]').fill('invalid-email-format');
  await page.locator('[data-testid="employee-save"]').click();

  // Native HTML5 or Pydantic validation prevents redirect
  await expect(page).toHaveURL('/hr/employees/new');
});

test('4. Duplicate email rejection', async ({ page }) => {
  const dupEmail = `dup.${Date.now()}@demo.local`;
  await uiLogin(page, 'demo_hr_user', 'Hr@Demo123');

  // Create first employee
  await page.goto('/hr/employees/new');
  await page.locator('[data-testid="employee-name"]').fill('Emp Original');
  await page.locator('[data-testid="employee-email"]').fill(dupEmail);
  await page.locator('[data-testid="employee-joining-date"]').fill('2026-03-01');
  await page.locator('[data-testid="employee-save"]').click();
  await expect(page.locator('[data-testid="employee-success"]')).toBeVisible();

  // Create second employee with same email
  await page.goto('/hr/employees/new');
  await page.locator('[data-testid="employee-name"]').fill('Emp Duplicate');
  await page.locator('[data-testid="employee-email"]').fill(dupEmail);
  await page.locator('[data-testid="employee-joining-date"]').fill('2026-03-01');
  await page.locator('[data-testid="employee-save"]').click();

  // Verify conflict error alert appears
  await expect(page.locator('.alert-error')).toBeVisible();
  await expect(page.locator('.alert-error')).toContainText('already exists');
});

test('5. Employee details values', async ({ page }) => {
  await uiLogin(page, 'demo_admin', 'Admin@Demo123');
  await page.goto('/hr/employees');
  await page.waitForSelector('[data-testid="employee-table"]');

  // Click View Details on first employee row
  await page.locator('[data-testid^="employee-view-"]').first().click();
  await page.waitForURL(/\/hr\/employees\/\d+/);

  await expect(page.locator('[data-testid="detail-name"]')).toBeVisible();
  await expect(page.locator('[data-testid="detail-email"]')).toBeVisible();
});

test('6. Inventory stock count calculation', async ({ page }) => {
  await uiLogin(page, 'demo_inventory_user', 'Inv@Demo123');
  await page.goto('/inventory/stock-count');

  await page.waitForSelector('[data-testid="stock-product"]');
  // Enter counted quantity
  await page.locator('[data-testid="stock-counted-quantity"]').fill('120');

  // Verify calculated difference is visible
  await expect(page.locator('[data-testid="stock-difference"]')).toBeVisible();

  // Submit adjustment
  await page.locator('[data-testid="stock-notes"]').fill('Playwright audit count');
  await page.locator('[data-testid="stock-submit"]').click();

  // Verify success banner and table update
  await expect(page.locator('.alert-success')).toBeVisible();
  await expect(page.locator('[data-testid="stock-history-table"]')).toContainText('Playwright audit count');
});

test('7. Employee Save failure toggle', async ({ page }) => {
  try {
    // Turn ON employee_save_failure toggle via API
    await apiPatchSetting('employee_save_failure', true);

    await uiLogin(page, 'demo_hr_user', 'Hr@Demo123');
    await page.goto('/hr/employees/new');

    await page.locator('[data-testid="employee-name"]').fill('Save Fail Test');
    await page.locator('[data-testid="employee-email"]').fill(`fail.${Date.now()}@demo.local`);
    await page.locator('[data-testid="employee-joining-date"]').fill('2026-03-01');
    await page.locator('[data-testid="employee-save"]').click();

    // Expect real observable HTTP 500 error alert
    await expect(page.locator('.alert-error')).toBeVisible();
    await expect(page.locator('.alert-error')).toContainText('Internal Server Error');
  } finally {
    await apiPatchSetting('employee_save_failure', false).catch(() => {});
  }
});

test('8. Missing success-message toggle', async ({ page }) => {
  try {
    // Turn ON employee_success_message_missing toggle via API
    await apiPatchSetting('employee_success_message_missing', true);

    await uiLogin(page, 'demo_hr_user', 'Hr@Demo123');
    await page.goto('/hr/employees/new');

    await page.locator('[data-testid="employee-name"]').fill('No Success Message Test');
    await page.locator('[data-testid="employee-email"]').fill(`nosuccess.${Date.now()}@demo.local`);
    await page.locator('[data-testid="employee-joining-date"]').fill('2026-03-01');
    await page.locator('[data-testid="employee-save"]').click();

    // Success message banner should be MISSING/hidden
    await page.waitForTimeout(1000);
    await expect(page.locator('[data-testid="employee-success"]')).not.toBeVisible();
  } finally {
    await apiPatchSetting('employee_success_message_missing', false).catch(() => {});
  }
});

test('9. Login failure BLOCKED-style scenario', async ({ page }) => {
  // Obtain token BEFORE enabling login_failure_mode
  const adminLogin = await apiLogin('demo_admin', 'Admin@Demo123');
  const adminToken = adminLogin.access_token;

  try {
    // Turn ON login_failure_mode toggle via API
    await fetch(`${BACKEND}/api/demo-settings/login_failure_mode`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${adminToken}` },
      body: JSON.stringify({ enabled: true }),
    });

    await page.goto('/login');
    await page.locator('[data-testid="login-username"]').fill('demo_admin');
    await page.locator('[data-testid="login-password"]').fill('Admin@Demo123');
    await page.locator('[data-testid="login-submit"]').click();

    // Expect HTTP 503 error message preventing login
    await expect(page.locator('.alert-error')).toBeVisible();
    await expect(page.locator('.alert-error')).toContainText('unavailable');
  } finally {
    // Turn OFF login_failure_mode using pre-obtained admin token
    await fetch(`${BACKEND}/api/demo-settings/login_failure_mode`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${adminToken}` },
      body: JSON.stringify({ enabled: false }),
    });
  }
});

test('10. Role-based menu visibility', async ({ page }) => {
  // Log in as Inventory user
  await uiLogin(page, 'demo_inventory_user', 'Inv@Demo123');
  await page.goto('/dashboard');

  // Verify Inventory links visible, HR create & Demo Settings hidden
  await expect(page.locator('.nav-link', { hasText: 'Stock Count' })).toBeVisible();
  await expect(page.locator('.nav-link', { hasText: '+ Create Employee' })).not.toBeVisible();
  await expect(page.locator('.nav-link', { hasText: '⚙ Demo Bug Toggles' })).not.toBeVisible();
});

test('11. Responsive layout at 1366x768 and 375x812', async ({ page }) => {
  // Desktop resolution
  await page.setViewportSize({ width: 1366, height: 768 });
  await uiLogin(page, 'demo_admin', 'Admin@Demo123');
  await page.goto('/dashboard');
  await expect(page.locator('.sidebar')).toBeVisible();

  // Mobile resolution
  await page.setViewportSize({ width: 375, height: 812 });
  await page.goto('/dashboard');
  await expect(page.locator('h1')).toBeVisible();
});
