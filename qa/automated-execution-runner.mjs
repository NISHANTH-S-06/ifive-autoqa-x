import fs from 'node:fs/promises';
import net from 'node:net';
import path from 'node:path';
import process from 'node:process';

import { chromium } from '@playwright/test';

const ALLOWED_ACTIONS = new Set([
  'NAVIGATE',
  'FILL',
  'CLICK',
  'ASSERT_VISIBLE',
  'ASSERT_TEXT',
  'SCREENSHOT',
  'SELECT',
  'CHECK',
  'UNCHECK',
  'WAIT_FOR_ELEMENT',
  'ASSERT_VALUE',
  'ASSERT_URL',
  'READ_TEXT',
  'ASSERT_TABLE_ROW',
]);

function fail(message) {
  throw new Error(message);
}

function assertSameOrigin(candidate, approvedOrigin) {
  const resolved = new URL(candidate, approvedOrigin);
  if (resolved.origin !== approvedOrigin) {
    const error = new Error('Navigation outside the approved target origin was blocked.');
    error.code = 'POLICY_BLOCKED';
    throw error;
  }
  return resolved.href;
}

function assertApprovedPath(candidate, allowedPaths) {
  const pathname = new URL(candidate).pathname || '/';
  if (!allowedPaths.includes(pathname)) {
    const error = new Error('Navigation to a path not approved for this target was blocked.');
    error.code = 'POLICY_BLOCKED';
    throw error;
  }
}

function safeFailure(action, error, currentUrl = '', authState = { failed: false, status: 200 }, isAuthErrorVisible = false) {
  if (error?.code === 'POLICY_BLOCKED') {
    return {
      failure_classification: 'POLICY_BLOCKED',
      safe_error_message: 'Navigation outside the approved target origin was blocked.',
      status: 'BLOCKED',
    };
  }
  if (error?.name === 'TimeoutError' && action === 'NAVIGATE') {
    return {
      failure_classification: 'TIMEOUT',
      safe_error_message: `${action} timed out in Playwright.`,
      status: 'FAILED',
    };
  }
  if (authState.failed || isAuthErrorVisible || 
      error?.message?.includes('Authentication service unavailable') ||
      error?.message?.includes('503') ||
      error?.message?.includes('401') ||
      error?.message?.includes('Unauthorized') ||
      error?.message?.includes('Invalid credentials')) {
    return {
      failure_classification: 'AUTHENTICATION_FAILED',
      safe_error_message: 'Authentication failed or target login unavailable.',
      status: 'BLOCKED',
    };
  }
  if (action.startsWith('ASSERT_') || action === 'READ_TEXT') {
    return { failure_classification: 'ASSERTION', safe_error_message: `${action} assertion failed.`, status: 'FAILED' };
  }
  return {
    failure_classification: 'PLAYWRIGHT',
    safe_error_message: `${action} failed in Playwright.`,
    status: 'FAILED',
  };
}

async function executeStep(page, approvedOrigin, allowedPaths, outputDirectory, step, timeoutMs, securityState) {
  const action = String(step.action || '').toUpperCase();
  if (!ALLOWED_ACTIONS.has(action)) {
    fail('Unsupported automated action.');
  }
  page.setDefaultTimeout(timeoutMs);
  page.setDefaultNavigationTimeout(timeoutMs);

  if (action === 'NAVIGATE') {
    const url = assertSameOrigin(step.path, approvedOrigin);
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: timeoutMs });
    assertSameOrigin(page.url(), approvedOrigin);
    assertApprovedPath(page.url(), allowedPaths);
    if (securityState.blocked) {
      const error = new Error('Navigation outside the approved target origin was blocked.');
      error.code = 'POLICY_BLOCKED';
      throw error;
    }
    return {};
  }

  if (page.url() === 'about:blank') {
    fail('A NAVIGATE action must run before page interaction.');
  }

  if (action === 'FILL') {
    const locator = page.locator(step.selector);
    await locator.waitFor({ state: 'visible', timeout: timeoutMs });
    await locator.fill(String(step.value), { timeout: timeoutMs });
  } else if (action === 'CLICK') {
    const locator = page.locator(step.selector);
    await locator.waitFor({ state: 'visible', timeout: timeoutMs });
    await locator.click({ timeout: timeoutMs });
    assertSameOrigin(page.url(), approvedOrigin);
    assertApprovedPath(page.url(), allowedPaths);
  } else if (action === 'SELECT') {
    const locator = page.locator(step.selector);
    await locator.waitFor({ state: 'visible', timeout: timeoutMs });
    await locator.selectOption(String(step.value), { timeout: timeoutMs });
  } else if (action === 'CHECK') {
    const locator = page.locator(step.selector);
    await locator.waitFor({ state: 'attached', timeout: timeoutMs });
    await locator.check({ force: true, timeout: timeoutMs });
  } else if (action === 'UNCHECK') {
    const locator = page.locator(step.selector);
    await locator.waitFor({ state: 'attached', timeout: timeoutMs });
    await locator.uncheck({ force: true, timeout: timeoutMs });
  } else if (action === 'WAIT_FOR_ELEMENT') {
    const locator = page.locator(step.selector);
    await locator.waitFor({ state: 'visible', timeout: timeoutMs });
  } else if (action === 'ASSERT_VISIBLE') {
    const locator = page.locator(step.selector);
    await locator.waitFor({ state: 'visible', timeout: timeoutMs });
    if (!(await locator.isVisible())) {
      fail('Element is not visible.');
    }
  } else if (action === 'ASSERT_TEXT') {
    const expected = String(step.expected ?? step.text ?? '');
    const locator = page.locator(step.selector);
    await locator.waitFor({ state: 'visible', timeout: timeoutMs });
    const actual = (await locator.textContent()) ?? '';
    if (!actual.includes(expected)) {
      fail(`Text does not match. Expected ${expected}, got ${actual}`);
    }
  } else if (action === 'ASSERT_VALUE') {
    const expected = String(step.expected ?? step.value ?? '');
    const locator = page.locator(step.selector);
    await locator.waitFor({ state: 'visible', timeout: timeoutMs });
    let actual = '';
    try {
      actual = await locator.inputValue();
    } catch {
      actual = (await locator.textContent()) ?? '';
    }
    if (!actual.includes(expected)) {
      fail(`Value assertion failed. Expected ${expected}, got ${actual}`);
    }
  } else if (action === 'ASSERT_URL') {
    const expected = String(step.expected ?? step.path ?? step.value ?? '');
    try {
      await page.waitForURL(url => url.href.includes(expected), { timeout: timeoutMs });
    } catch {
      fail(`URL assertion failed. Expected URL to include ${expected}, got ${page.url()}`);
    }
  } else if (action === 'READ_TEXT') {
    const locator = page.locator(step.selector);
    await locator.waitFor({ state: 'visible', timeout: timeoutMs });
    const text = (await locator.textContent()) ?? '';
    return { read_text: text };
  } else if (action === 'ASSERT_TABLE_ROW') {
    const expected = String(step.expected ?? step.text ?? '');
    const tableLocator = page.locator(step.selector);
    await tableLocator.waitFor({ state: 'visible', timeout: timeoutMs });
    const rows = tableLocator.locator('tbody tr', { hasText: expected });
    if ((await rows.count()) === 0) {
      const allText = (await tableLocator.textContent()) ?? '';
      if (!allText.includes(expected)) {
        fail(`Table row assertion failed. Table did not contain text ${expected}`);
      }
    }
  } else if (action === 'SCREENSHOT') {
    const filename = `step-${Number(step.execution_id)}.png`;
    const screenshotPath = path.resolve(outputDirectory, filename);
    if (path.dirname(screenshotPath) !== path.resolve(outputDirectory)) {
      fail('Screenshot output path escaped its work directory.');
    }
    await page.screenshot({ path: screenshotPath, type: 'png', fullPage: false, timeout: timeoutMs });
    return { screenshot_file: filename };
  }
  assertSameOrigin(page.url(), approvedOrigin);
  assertApprovedPath(page.url(), allowedPaths);
  if (securityState.blocked) {
    const error = new Error('Navigation outside the approved target origin was blocked.');
    error.code = 'POLICY_BLOCKED';
    throw error;
  }
  return {};
}

async function main() {
  const [inputPath, outputPath] = process.argv.slice(2);
  if (!inputPath || !outputPath) {
    fail('Input and output paths are required.');
  }
  const request = JSON.parse(await fs.readFile(inputPath, 'utf8'));
  const approvedOrigin = new URL(request.target_origin).origin;
  const outputDirectory = path.resolve(request.output_directory);
  await fs.mkdir(outputDirectory, { recursive: true });

  const resolverArgs = [];
  if (!net.isIP(request.target_host)) {
    resolverArgs.push(`--host-resolver-rules=MAP ${request.target_host} ${request.pinned_address}`);
  }
  const browser = await chromium.launch({ headless: true, args: resolverArgs });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 },
    userAgent: request.user_agent,
    ignoreHTTPSErrors: request.tls_verify === false,
  });
  const page = await context.newPage();
  
  // TEMPORARY DIAGNOSTICS FOR PLAYWRIGHT
  page.on('console', msg => console.error(`PAGE CONSOLE: ${msg.type()} ${msg.text()}`));
  page.on('pageerror', error => console.error(`PAGE ERROR: ${error.message}`));
  page.on('requestfailed', request => console.error(`REQUEST FAILED: ${request.url()} - ${request.failure()?.errorText}`));
  page.on('request', request => {
    if (request.url().includes('/api/auth/login')) {
      console.error(`DIAGNOSTIC REQUEST: ${request.method()} ${request.url()}`);
    }
  });
  
  const authState = { failed: false, status: 200 };
  page.on('response', response => {
    if (response.url().includes('/api/auth/login')) {
      console.error(`DIAGNOSTIC RESPONSE: ${response.status()} ${response.url()}`);
      if (response.status() >= 400) {
        authState.failed = true;
        authState.status = response.status();
      }
    }
  });
  const results = [];
  const deadline = Date.now() + Number(request.timeout_ms);
  const securityState = { blocked: false };

  await context.route('**/*', async route => {
    try {
      const req = route.request();
      const requestOrigin = new URL(req.url()).origin;
      if (requestOrigin !== approvedOrigin) {
        if (req.isNavigationRequest() && req.frame() === page.mainFrame()) {
          console.error(`BLOCKED NAVIGATION BY INTERCEPTOR: ${req.url()} (origin: ${requestOrigin}, approved: ${approvedOrigin})`);
          securityState.blocked = true;
        }
        await route.abort('blockedbyclient');
        return;
      }
      await route.continue();
    } catch (err) {
      console.error(`ERROR IN INTERCEPTOR: ${err}`);
      await route.abort('blockedbyclient');
    }
  });

  try {
    for (const step of request.steps) {
      const started = Date.now();
      const remaining = deadline - started;
      if (remaining <= 0) {
        const error = new Error('Run deadline exceeded.');
        error.name = 'TimeoutError';
        throw error;
      }
      try {
        const output = await executeStep(page, approvedOrigin, request.allowed_paths, outputDirectory, step, remaining, securityState);
        results.push({
          execution_id: step.execution_id,
          status: 'PASSED',
          duration_ms: Date.now() - started,
          ...output,
        });
      } catch (error) {
        if (securityState.blocked) {
          error = new Error('Navigation outside the approved target origin was blocked.');
          error.code = 'POLICY_BLOCKED';
        }
        let currentUrl = '';
        try { currentUrl = page.url(); } catch {}

        let failureScreenshotFile = null;
        if (currentUrl && currentUrl !== 'about:blank') {
          try {
            const failFilename = `step-${Number(step.execution_id)}-failure.png`;
            const failPath = path.resolve(outputDirectory, failFilename);
            await page.screenshot({ path: failPath, type: 'png', timeout: 3000 });
            failureScreenshotFile = failFilename;
          } catch {}
        }

        let isAuthErrorVisible = false;
        if (currentUrl && currentUrl.includes('/login')) {
          try {
            const errorLocator = page.locator('.error, [data-testid*="error"]');
            if (await errorLocator.count() > 0) {
              isAuthErrorVisible = await errorLocator.first().isVisible({ timeout: 500 });
            }
          } catch {}
        }

        const safeInfo = safeFailure(step.action, error, currentUrl, authState, isAuthErrorVisible);
        results.push({
          execution_id: step.execution_id,
          status: safeInfo.status || (error?.code === 'POLICY_BLOCKED' ? 'BLOCKED' : 'FAILED'),
          duration_ms: Date.now() - started,
          ...(failureScreenshotFile ? { screenshot_file: failureScreenshotFile } : {}),
          ...safeInfo,
        });
        break;
      }
    }
  } finally {
    await context.close();
    await browser.close();
  }

  await fs.writeFile(outputPath, JSON.stringify({ results }), 'utf8');
}

main().catch(async error => {
  const outputPath = process.argv[3];
  if (outputPath) {
    await fs.writeFile(outputPath, JSON.stringify({
      fatal_error: safeFailure('PLAYWRIGHT', error),
      results: [],
    }), 'utf8').catch(() => {});
  }
  process.exitCode = 1;
});
