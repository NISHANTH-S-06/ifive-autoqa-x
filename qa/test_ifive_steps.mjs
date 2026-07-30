import { chromium } from '@playwright/test';

async function testFlow() {
  console.log('Starting iFive IoT Navigation Test Flow...');
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1280, height: 720 } });
  const page = await context.newPage();

  console.log('Step 1: NAVIGATE /');
  await page.goto('https://ifive.in/', { waitUntil: 'domcontentloaded' });

  console.log('Step 2: ASSERT_VISIBLE button.nav-item');
  const btn = page.locator('button.nav-item').first();
  await btn.waitFor({ state: 'visible', timeout: 5000 });
  console.log('Products button visible text:', await btn.textContent());

  console.log('Step 3: SCREENSHOT Homepage');
  await page.screenshot({ path: 'homepage.png' });

  console.log('Step 4: CLICK Products button');
  await btn.click();
  await page.waitForTimeout(500);

  console.log('Step 5: CLICK a[href="/products/iot"]');
  const iotLink = page.locator('a[href="/products/iot"]').first();
  await iotLink.waitFor({ state: 'visible', timeout: 5000 });
  await iotLink.click();
  await page.waitForLoadState('domcontentloaded');

  console.log('Step 6: ASSERT_URL /products/iot');
  console.log('Current URL:', page.url());
  if (!page.url().includes('/products/iot')) {
    throw new Error(`URL check failed! Current URL is ${page.url()}`);
  }

  console.log('Step 7: SCREENSHOT iFive IoT page');
  await page.screenshot({ path: 'ifive_iot_page.png' });

  console.log('Test flow completed SUCCESSFULLY!');
  await browser.close();
}

testFlow().catch(err => {
  console.error('TEST FLOW FAILED:', err);
  process.exit(1);
});
