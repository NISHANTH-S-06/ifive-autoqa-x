import { chromium } from 'playwright';

async function main() {
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();
    await page.goto('https://ifiveerp.in/erp_demo/public/login', { waitUntil: 'commit', timeout: 60000 });
    const userInput = page.locator('input[name="username"], input[type="text"]').first();
    await userInput.waitFor({ state: 'attached', timeout: 30000 });
    await userInput.fill('superadmin');
    await page.locator('input[name="password"]').fill('Ifive@123');
    await page.locator('select[name="company_id"]').selectOption('1');
    await page.locator('button.btn-submit, button[type="submit"]').click();
    await page.waitForTimeout(4000);

    console.log('NAVIGATING TO /soorder...');
    await page.goto('https://ifiveerp.in/erp_demo/public/soorder');
    await page.waitForTimeout(3000);

    console.log('SOORDER URL:', page.url());
    console.log('SOORDER TITLE:', await page.title());

    const buttons = await page.evaluate(() => {
        return Array.from(document.querySelectorAll('a, button, input[type="button"], input[type="submit"]')).map(e => ({
            tag: e.tagName,
            text: (e.innerText || e.value || '').trim(),
            href: e.getAttribute('href') || '',
            onclick: e.getAttribute('onclick') || '',
            class: e.className || ''
        })).filter(e => e.text);
    });

    console.log('SOORDER BUTTONS & LINKS:', buttons);

    await browser.close();
}

main();
