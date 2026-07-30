import { defineConfig, devices } from '@playwright/test';

const baseURL = process.env.AUTOQA_QA_BASE_URL ?? 'http://127.0.0.1:5173';
const runOutput = process.env.AUTOQA_OUTPUT_DIR;
const htmlOutput = process.env.PLAYWRIGHT_HTML_OUTPUT_DIR ?? 'reports/html';
const jsonOutput = process.env.PLAYWRIGHT_JSON_OUTPUT_NAME ?? 'reports/logs/results.json';
const skipWebServer = process.env.AUTOQA_SKIP_WEBSERVER === '1';

export default defineConfig({
  testDir: './tests',
  timeout: 60_000,
  expect: {
    timeout: 10_000,
  },
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 2 : undefined,
  reporter: [
    ['list'],
    ['html', { outputFolder: htmlOutput, open: 'never' }],
    ['json', { outputFile: jsonOutput }],
  ],
  use: {
    baseURL,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'off',
  },
  webServer: skipWebServer ? undefined : {
    command: 'cd ..\\frontend && npm run dev',
    url: baseURL,
    reuseExistingServer: true,
    timeout: 30_000,
  },
  outputDir: runOutput ?? 'reports/traces',
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'], channel: 'chrome' },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],
});
