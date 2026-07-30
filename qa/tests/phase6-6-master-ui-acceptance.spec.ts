import { test, expect } from '@playwright/test';

const AUTOQA_URL = 'http://127.0.0.1:8000';

test.describe('Phase 6.6 — Master UI Acceptance & Complete UX Hardening', () => {
  test.beforeAll(async ({ request }) => {
    // Seed test data on backend before running UI acceptance checks
    await request.post(`${AUTOQA_URL}/api/system/seed-test-data`).catch(() => undefined);
  });

  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    const usernameInput = page.getByTestId('login-username');
    if (await usernameInput.isVisible()) {
      await usernameInput.fill('admin');
      await page.getByTestId('login-password').fill('autoqa2026');
      await page.getByTestId('login-submit').click();
    }
  });

  test('01: Login & Session Restoration', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('QA Platform Dashboard');
    await page.screenshot({ path: 'test-results/01-login-session.png' });
  });

  test('02: AppShell, Navigation & Theme Toggle', async ({ page }) => {
    const projectSelector = page.getByTestId('project-selector');
    await expect(projectSelector).toBeVisible();

    const themeToggle = page.getByTestId('theme-toggle');
    await expect(themeToggle).toBeVisible();
    await themeToggle.click();
    await page.screenshot({ path: 'test-results/02-theme-toggle-light.png' });
    await themeToggle.click();

    const sidebarToggle = page.getByTestId('sidebar-toggle');
    await expect(sidebarToggle).toBeVisible();
    await sidebarToggle.click();
    await page.screenshot({ path: 'test-results/02-sidebar-collapsed.png' });
    await sidebarToggle.click();
  });

  test('03: Dashboard KPI Cards, Pass Rate & Health Status', async ({ page }) => {
    await page.getByTestId('sidebar-item-dashboard').click();
    await expect(page.getByText('Total Test Runs')).toBeVisible();
    await expect(page.getByText('Pass Rate')).toBeVisible();
    await expect(page.getByText('System Health')).toBeVisible();
    await page.screenshot({ path: 'test-results/03-dashboard.png' });
  });

  test('04: Task Imports Module', async ({ page }) => {
    await page.getByTestId('sidebar-item-task-imports').click();
    await expect(page.getByText('Task Integration & Backlog Synchronization')).toBeVisible();
    await page.screenshot({ path: 'test-results/04-task-imports.png' });
  });

  test('05: Test Plans Module & Visual Editor', async ({ page }) => {
    await page.getByTestId('sidebar-item-test-plans').click();
    await expect(page.getByText('Test Plan Management')).toBeVisible();
    await page.screenshot({ path: 'test-results/05-test-plans.png' });
  });

  test('06: Approval Queue & Self-Approval Governance', async ({ page }) => {
    await page.getByTestId('sidebar-item-approval-queue').click();
    await expect(page.getByText('Approval Queue & Governance')).toBeVisible();
    await expect(page.getByText('Self-approval is strictly blocked')).toBeVisible();
    await page.screenshot({ path: 'test-results/06-approval-queue.png' });
  });

  test('07: Automated Runs Module & Readiness Cards', async ({ page }) => {
    await page.getByTestId('sidebar-item-automated-runs').click();
    await expect(page.getByText('Automated Execution Runs Queue')).toBeVisible();
    await expect(page.getByText('Admin Prerequisite')).toBeVisible();
    await page.screenshot({ path: 'test-results/07-automated-runs.png' });
  });

  test('08: Advanced Validation Profiles', async ({ page }) => {
    await page.getByTestId('sidebar-item-advanced-validation').click();
    await expect(page.getByText('Advanced Validation Engine & Multi-Layer Assertions')).toBeVisible();
    await page.screenshot({ path: 'test-results/08-advanced-validation.png' });
  });

  test('09: Evidence Repository & Artifact Gallery', async ({ page }) => {
    await page.getByTestId('sidebar-item-evidence').click();
    await expect(page.getByText('Evidence & Artifact Repository')).toBeVisible();
    await page.screenshot({ path: 'test-results/09-evidence-repository.png' });
  });

  test('10: Defects Management Module', async ({ page }) => {
    await page.getByTestId('sidebar-item-defects').click();
    await expect(page.getByText('Defect Management & Fingerprint Tracking')).toBeVisible();
    await page.screenshot({ path: 'test-results/10-defects-management.png' });
  });

  test('11: Management Reports Engine', async ({ page }) => {
    await page.getByTestId('sidebar-item-reports').click();
    await expect(page.getByText('Management Reports & Quality Export Engine')).toBeVisible();
    await page.screenshot({ path: 'test-results/11-reports-engine.png' });
  });

  test('12: Local Schedules & Cron Automation', async ({ page }) => {
    await page.getByTestId('sidebar-item-schedules').click();
    await expect(page.getByText('Local Schedules & Cron Automation')).toBeVisible();
    await page.screenshot({ path: 'test-results/12-local-schedules.png' });
  });

  test('13: Test Projects Module', async ({ page }) => {
    await page.getByTestId('sidebar-item-projects').click();
    await expect(page.getByText('Test Projects & Multi-Tenant Isolation')).toBeVisible();
    await page.screenshot({ path: 'test-results/13-test-projects.png' });
  });

  test('14: Cryptographic Audit Trail Logs & Verification', async ({ page }) => {
    await page.getByTestId('sidebar-item-audit-logs').click();
    await expect(page.getByText('Cryptographic Audit Trail & Integrity Logs')).toBeVisible();
    await expect(page.getByText('Verify Audit Chain')).toBeVisible();
    await page.screenshot({ path: 'test-results/14-audit-logs.png' });
  });

  test('15: Settings & Platform Administration', async ({ page }) => {
    await page.getByTestId('sidebar-item-settings').click();
    await expect(page.getByText('Platform Administration & System Settings')).toBeVisible();
    await expect(page.getByText('Local Operator Accounts & Governance')).toBeVisible();
    await page.screenshot({ path: 'test-results/15-settings-admin.png' });
  });

  test('16: Responsive Viewport Verification — 1366x768', async ({ page }) => {
    await page.setViewportSize({ width: 1366, height: 768 });
    await expect(page.locator('h1')).toBeVisible();
    await page.screenshot({ path: 'test-results/16-responsive-1366.png' });
  });

  test('17: Responsive Viewport Verification — 1024x768', async ({ page }) => {
    await page.setViewportSize({ width: 1024, height: 768 });
    await expect(page.locator('h1')).toBeVisible();
    await page.screenshot({ path: 'test-results/17-responsive-1024.png' });
  });
});
