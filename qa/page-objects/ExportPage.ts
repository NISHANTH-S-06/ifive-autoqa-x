import { expect, type Page } from '@playwright/test';

export class ExportPage {
  constructor(private readonly page: Page) {}

  async expectExportButton(label = /Export|Download/i) {
    await expect(this.page.getByRole('button', { name: label })).toBeVisible();
  }
}

