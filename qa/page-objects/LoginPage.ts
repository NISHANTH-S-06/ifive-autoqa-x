import type { Page } from '@playwright/test';

export class LoginPage {
  constructor(private readonly page: Page) {}

  async goto(path = '/login') {
    await this.page.goto(path);
  }

  async login(username: string, password: string) {
    await this.page.getByLabel(/email|username/i).fill(username);
    await this.page.getByLabel(/password/i).fill(password);
    await this.page.getByRole('button', { name: /sign in|login/i }).click();
  }
}

