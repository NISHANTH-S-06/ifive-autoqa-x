import { chromium } from '@playwright/test';

async function main() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();
  
  await page.goto('https://ifive.in/', { waitUntil: 'networkidle' });
  console.log('Title:', await page.title());
  console.log('URL:', page.url());

  const links = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('a')).map(a => ({
      text: a.innerText.trim(),
      href: a.getAttribute('href'),
    }));
  });

  console.log('Total links found:', links.length);
  for (const l of links) {
    if (l.text.toLowerCase().includes('product') || l.text.toLowerCase().includes('iot') || (l.href && (l.href.includes('product') || l.href.includes('iot')))) {
      console.log(`Text: "${l.text}" | Href: "${l.href}"`);
    }
  }

  // Search elements containing "Products" or "IoT"
  const elements = await page.evaluate(() => {
    const all = Array.from(document.querySelectorAll('a, button, span, div, li'));
    return all
      .filter(el => el.textContent.toLowerCase().includes('product') || el.textContent.toLowerCase().includes('iot') || el.textContent.toLowerCase().includes('iiot'))
      .map(el => ({ tag: el.tagName, text: el.textContent.trim().substring(0, 50), href: el.getAttribute('href'), class: el.className }));
  });
  console.log('\nRelevant Text Elements:', JSON.stringify(elements, null, 2));

  await browser.close();
}

main().catch(console.error);
