import { test, expect } from '@playwright/test';

const AUTOQA_URL = 'http://127.0.0.1:8000';

test.describe('Phase 6.5 — Frontend UI/UX Integration & Visual Upgrade', () => {
  test.beforeAll(async ({ request }) => {
    // Seed test data on backend before running UI acceptance checks
    await request.post(`${AUTOQA_URL}/api/system/seed-test-data`).catch(() => undefined);
  });

  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('01: Login Flow & Session Restoration', async ({ page }) => {
    const usernameInput = page.getByTestId('login-username');
    if (await usernameInput.isVisible()) {
      await usernameInput.fill('admin');
      await page.getByTestId('login-password').fill('autoqa2026');
      await page.getByTestId('login-submit').click();
    }

    await expect(page.locator('h1')).toContainText('QA Platform Dashboard');
  });

  test('02: Main Layout, Collapsible Sidebar & Top Header Controls', async ({ page }) => {
    const usernameInput = page.getByTestId('login-username');
    if (await usernameInput.isVisible()) {
      await usernameInput.fill('admin');
      await page.getByTestId('login-password').fill('autoqa2026');
      await page.getByTestId('login-submit').click();
    }

    const projectSelector = page.getByTestId('project-selector');
    await expect(projectSelector).toBeVisible();

    const globalSearch = page.getByTestId('global-search-input');
    await expect(globalSearch).toBeVisible();

    const themeToggle = page.getByTestId('theme-toggle');
    await expect(themeToggle).toBeVisible();
    await themeToggle.click();

    const sidebarToggle = page.getByTestId('sidebar-toggle');
    await expect(sidebarToggle).toBeVisible();
    await sidebarToggle.click();
  });

  test('03: Sidebar Navigation across all 13 Modules', async ({ page }) => {
    const usernameInput = page.getByTestId('login-username');
    if (await usernameInput.isVisible()) {
      await usernameInput.fill('admin');
      await page.getByTestId('login-password').fill('autoqa2026');
      await page.getByTestId('login-submit').click();
    }

    const modules = [
      { key: 'dashboard', heading: 'QA Platform Dashboard' },
      { key: 'task-imports', heading: 'Task Imports & Requirement Management' },
      { key: 'test-plans', heading: 'Test Plan Management & Visual Editor' },
      { key: 'approval-queue', heading: 'Approval Queue & Governance' },
      { key: 'automated-runs', heading: 'Automated Test Execution Runs' },
      { key: 'advanced-validation', heading: 'Advanced Validation Profile Manager' },
      { key: 'evidence', heading: 'Evidence & Artifact Repository' },
      { key: 'defects', heading: 'Defect Management & Fingerprint Tracking' },
      { key: 'reports', heading: 'Management Reports & Quality Export Engine' },
      { key: 'schedules', heading: 'Local Schedules & Cron Automation' },
      { key: 'projects', heading: 'Test Projects & Multi-Tenant Isolation' },
      { key: 'audit-logs', heading: 'Cryptographic Audit Trail & Integrity Logs' },
      { key: 'settings', heading: 'Platform Administration & System Settings' }
    ];

    for (const mod of modules) {
      const navButton = page.getByTestId(`sidebar-item-${mod.key}`);
      await navButton.click();
      await expect(page.locator('h1')).toContainText(mod.heading);
    }
  });

  test('04: Dashboard KPI Cards & System Health', async ({ page }) => {
    const usernameInput = page.getByTestId('login-username');
    if (await usernameInput.isVisible()) {
      await usernameInput.fill('admin');
      await page.getByTestId('login-password').fill('autoqa2026');
      await page.getByTestId('login-submit').click();
    }

    await page.getByTestId('sidebar-item-dashboard').click();
    await expect(page.getByText('Total Test Runs')).toBeVisible();
    await expect(page.getByText('Pass Rate')).toBeVisible();
    await expect(page.getByText('System Health')).toBeVisible();
  });

  test('05: Audit Log Cryptographic Integrity Verification', async ({ page }) => {
    const usernameInput = page.getByTestId('login-username');
    if (await usernameInput.isVisible()) {
      await usernameInput.fill('admin');
      await page.getByTestId('login-password').fill('autoqa2026');
      await page.getByTestId('login-submit').click();
    }

    await page.getByTestId('sidebar-item-audit-logs').click();
    await expect(page.getByText('Audit Ledger Integrity')).toBeVisible();
  });
});
