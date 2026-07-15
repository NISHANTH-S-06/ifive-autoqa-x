import { expect, type Page } from '@playwright/test';

export class DashboardPage {
  constructor(private readonly page: Page) {}

  async expectLoaded() {
    await expect(this.page.getByText(/Dashboard|Total Tests|Pass Rate/i).first()).toBeVisible();
  }
}

