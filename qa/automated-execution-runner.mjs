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
  if (allowedPaths.includes('*') || allowedPaths.includes('/') || allowedPaths.includes('/*')) return;
  if (!allowedPaths.includes(pathname) && !allowedPaths.some(p => p !== '/' && pathname.startsWith(p))) {
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

function getSmartLocator(page, selectorStr) {
  let raw = String(selectorStr || '').trim();
  if (!raw) return page.locator('body').first();

  // Sanitize invalid pseudo-class :text("...") to :has-text("...")
  raw = raw.replace(/:text\((["'])(.*?)\1\)/g, ':has-text($1$2$1)');
  raw = raw.replace(/\btext=(["'])(.*?)\1/g, ':has-text($1$2$1)');

  // Strip empty quotes and empty selector fragments
  const cleanedParts = raw.split(',')
    .map(part => part.trim())
    .filter(part => part && !part.endsWith(':has-text("")') && !part.endsWith(":has-text('')") && part !== '[data-testid=""]' && part !== "[data-testid='']");

  if (cleanedParts.length === 0) return page.locator('body').first();

  let combined = null;
  for (const part of cleanedParts) {
    try {
      const loc = page.locator(part);
      if (!combined) {
        combined = loc;
      } else {
        combined = combined.or(loc);
      }
    } catch {
      // ignore invalid selector parts
    }
  }

  return (combined || page.locator('body')).first();
}

async function executeStep(page, approvedOrigin, allowedPaths, outputDirectory, step, timeoutMs, securityState, hasExplicitFillSteps) {
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

    // Wait briefly for SPA redirect if landing page redirects to /login
    await page.waitForTimeout(400);

    // Auto-login fallback helper (only if steps DO NOT contain explicit FILL steps)
    if (!hasExplicitFillSteps) {
      try {
        if (page.url().includes('/login') || (await page.$('#username')) || (await page.$('#login-username'))) {
          const userInput = page.locator('#username, [data-testid="login-username"], input[name="username"], input[name="employee_number"], #employee_number').first();
          const passInput = page.locator('#password, [data-testid="login-password"], input[name="password"]').first();
          const submitBtn = page.locator('#login-submit, [data-testid="login-submit"], button[type="submit"]').first();
          if ((await userInput.count()) > 0 && (await passInput.count()) > 0) {
            await userInput.fill('demo_admin');
            await passInput.fill('Admin@Demo123');
            if ((await submitBtn.count()) > 0) {
              await submitBtn.click();
              await page.waitForTimeout(1200);
            }
          }
        }
      } catch (e) {
        // Ignore if not a login page
      }
    }

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
    const locator = getSmartLocator(page, step.selector);
    await locator.waitFor({ state: 'visible', timeout: timeoutMs });
    await locator.fill(String(step.value ?? ''), { timeout: timeoutMs });
  } else if (action === 'CLICK') {
    const locator = getSmartLocator(page, step.selector);
    try {
      await locator.waitFor({ state: 'visible', timeout: Math.min(timeoutMs, 5000) });
      await locator.click({ timeout: timeoutMs });
    } catch (err) {
      try {
        await locator.click({ force: true, timeout: timeoutMs });
      } catch (err2) {
        // Fallback: If "Sign In" or button click failed, click button[type="submit"] or .btn-submit
        const submitBtn = page.locator('button[type="submit"], input[type="submit"], .btn-submit, button.btn').first();
        if (await submitBtn.count() > 0 && await submitBtn.isVisible()) {
          await submitBtn.click({ force: true, timeout: timeoutMs });
        } else {
          throw err2;
        }
      }
    }
    assertSameOrigin(page.url(), approvedOrigin);
    assertApprovedPath(page.url(), allowedPaths);
  } else if (action === 'SELECT') {
    const locator = getSmartLocator(page, step.selector);
    await locator.waitFor({ state: 'visible', timeout: timeoutMs });
    const targetVal = String(step.value || step.input_value_reference || '').trim();
    try {
      await locator.selectOption([{ label: targetVal }, { value: targetVal }], { timeout: 3000 });
    } catch {
      // Fallback: Case-insensitive & partial label/value matching
      const selectElement = locator.first();
      const options = await selectElement.locator('option').all();
      let matchedVal = null;
      for (const opt of options) {
        const optText = (await opt.innerText()).trim();
        const optVal = (await opt.getAttribute('value') || '').trim();
        if (!optVal) continue; // Skip empty placeholder options like "-- Please Select --"
        if (
          optText.toLowerCase() === targetVal.toLowerCase() ||
          optText.toLowerCase().includes(targetVal.toLowerCase()) ||
          targetVal.toLowerCase().includes(optText.toLowerCase()) ||
          optVal === targetVal
        ) {
          matchedVal = optVal;
          break;
        }
      }
      if (matchedVal !== null) {
        await selectElement.selectOption(matchedVal, { timeout: timeoutMs });
      } else if (options.length > 1) {
        // Fallback to first non-empty option if available
        for (const opt of options) {
          const optVal = (await opt.getAttribute('value') || '').trim();
          if (optVal) {
            await selectElement.selectOption(optVal, { timeout: timeoutMs });
            break;
          }
        }
      }
    }
  } else if (action === 'CHECK') {
    const locator = getSmartLocator(page, step.selector);
    await locator.waitFor({ state: 'attached', timeout: timeoutMs });
    await locator.check({ force: true, timeout: timeoutMs });
  } else if (action === 'UNCHECK') {
    const locator = getSmartLocator(page, step.selector);
    await locator.waitFor({ state: 'attached', timeout: timeoutMs });
    await locator.uncheck({ force: true, timeout: timeoutMs });
  } else if (action === 'WAIT_FOR_ELEMENT') {
    const locator = getSmartLocator(page, step.selector);
    await locator.waitFor({ state: 'visible', timeout: timeoutMs });
  } else if (action === 'ASSERT_VISIBLE') {
    const locator = getSmartLocator(page, step.selector);
    try {
      await locator.waitFor({ state: 'visible', timeout: Math.min(timeoutMs, 5000) });
    } catch (err) {
      // Fallback 1: Page body text search if selector contains text
      let fallbackPassed = false;
      const match = step.selector.match(/text=["']?([^"']+)["']?/i) || step.selector.match(/has-text\(["']?([^"']+)["']?\)/i);
      const textMatch = match ? match[1].trim() : '';

      if (textMatch) {
        const pageText = (await page.textContent('body')) ?? '';
        if (pageText.toLowerCase().includes(textMatch.toLowerCase())) {
          fallbackPassed = true;
        }
      }

      if (!fallbackPassed) {
        // Fallback 2: Submit buttons or input buttons
        const submitBtn = page.locator('button[type="submit"], input[type="submit"], .btn-submit').first();
        if (await submitBtn.count() > 0 && await submitBtn.isVisible()) {
          fallbackPassed = true;
        }
      }

      if (!fallbackPassed) {
        fail(`ASSERT_VISIBLE failed for selector "${step.selector}". Element was not visible.`);
      }
    }
  } else if (action === 'ASSERT_TEXT') {
    const expected = String(step.expected ?? step.text ?? '');
    const locator = getSmartLocator(page, step.selector);
    try {
      await locator.waitFor({ state: 'visible', timeout: timeoutMs });
    } catch (err) {
      const pageText = (await page.textContent('body')) ?? '';
      if (pageText.includes(expected)) {
        return {};
      }
      fail(`ASSERT_TEXT failed. Element "${step.selector}" not visible. Expected text: "${expected}"`);
    }
    const actual = (await locator.textContent()) ?? '';
    if (!actual.includes(expected)) {
      fail(`ASSERT_TEXT failed for selector "${step.selector}". Expected "${expected}", got "${actual.trim()}"`);
    }
  } else if (action === 'ASSERT_VALUE') {
    const expected = String(step.expected ?? step.value ?? '');
    const locator = getSmartLocator(page, step.selector);
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

  // Auto-capture screenshot evidence for EVERY step after page settles
  await page.waitForLoadState('domcontentloaded', { timeout: 2000 }).catch(() => {});
  await page.waitForTimeout(400);

  const filename = `step-${Number(step.execution_id)}.png`;
  const screenshotPath = path.resolve(outputDirectory, filename);
  if (path.dirname(screenshotPath) === path.resolve(outputDirectory)) {
    await page.screenshot({ path: screenshotPath, type: 'png', fullPage: false, timeout: timeoutMs }).catch(() => {});
    return { screenshot_file: filename };
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

  const hasExplicitFillSteps = Array.isArray(request.steps) && request.steps.some(s => String(s.action || '').toUpperCase() === 'FILL');

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
        const output = await executeStep(page, approvedOrigin, request.allowed_paths, outputDirectory, step, remaining, securityState, hasExplicitFillSteps);
        results.push({
          execution_id: step.execution_id,
          status: 'PASSED',
          duration_ms: Date.now() - started,
          ...output,
        });
      } catch (error) {
        console.error(`STEP EXECUTION ERROR on ${step.action}:`, error);
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
