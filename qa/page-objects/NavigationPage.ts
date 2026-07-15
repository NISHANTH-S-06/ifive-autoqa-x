import type { Page } from '@playwright/test';

export class NavigationPage {
  constructor(private readonly page: Page) {}

  async openSection(name: string) {
    await this.page.getByRole('link', { name }).click();
  }
}

