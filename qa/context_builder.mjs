import { chromium } from '@playwright/test';

async function main() {
  const url = process.argv[2];
  if (!url) {
    console.error(JSON.stringify({ error: 'URL argument is required' }));
    process.exit(1);
  }

  let browser;
  try {
    browser = await chromium.launch({ headless: true });
    const context = await browser.newContext();
    
    const consoleErrors = [];
    const networkRequests = [];
    const apiCalls = [];

    const page = await context.newPage();
    
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    page.on('request', req => {
      const rt = req.resourceType();
      networkRequests.push({ url: req.url(), method: req.method(), type: rt });
      if (['fetch', 'xhr'].includes(rt)) {
        apiCalls.push({ url: req.url(), method: req.method() });
      }
    });

    const response = await page.goto(url, { waitUntil: 'networkidle', timeout: 25000 });
    const finalUrl = page.url();

    const cookies = await context.cookies();
    
    const pageData = await page.evaluate(() => {
      const getElements = (selector) => {
        return Array.from(document.querySelectorAll(selector)).map(el => {
          const rect = el.getBoundingClientRect();
          return {
            tag: el.tagName.toLowerCase(),
            text: el.innerText ? el.innerText.trim().replace(/\n/g, ' ') : '',
            id: el.id || '',
            className: el.className || '',
            testId: el.getAttribute('data-testid') || '',
            href: el.getAttribute('href') || '',
            type: el.getAttribute('type') || '',
            name: el.getAttribute('name') || '',
            role: el.getAttribute('role') || '',
            ariaLabel: el.getAttribute('aria-label') || '',
            visible: rect.width > 0 && rect.height > 0 && window.getComputedStyle(el).visibility !== 'hidden'
          };
        });
      };

      const meta = {};
      document.querySelectorAll('meta').forEach(m => {
        const name = m.getAttribute('name') || m.getAttribute('property');
        if (name) meta[name] = m.getAttribute('content') || '';
      });

      const domStats = {
        elementCount: document.querySelectorAll('*').length,
        interactiveElements: document.querySelectorAll('button, a, input, select, textarea').length
      };

      let localStorageData = {};
      let sessionStorageData = {};
      try { localStorageData = { ...localStorage }; } catch(e) {}
      try { sessionStorageData = { ...sessionStorage }; } catch(e) {}

      return {
        title: document.title,
        url: window.location.href,
        meta: meta,
        navigation: getElements('nav, [role="navigation"]'),
        buttons: getElements('button, [role="button"], input[type="button"], input[type="submit"]'),
        links: getElements('a'),
        forms: getElements('form'),
        inputs: getElements('input, textarea, select'),
        tables: getElements('table'),
        dom: {
          stats: domStats,
          html_snapshot: document.documentElement.outerHTML.substring(0, 1000) // Truncated to avoid massive payloads
        },
        storage: {
          local: localStorageData,
          session: sessionStorageData
        },
        viewport: {
          width: window.innerWidth,
          height: window.innerHeight
        }
      };
    });

    const finalContext = {
      page_title: pageData.title,
      url: finalUrl,
      meta: pageData.meta,
      navigation: pageData.navigation,
      buttons: pageData.buttons,
      links: pageData.links,
      forms: pageData.forms,
      inputs: pageData.inputs,
      tables: pageData.tables,
      console_errors: consoleErrors,
      network_requests: networkRequests,
      api_calls: apiCalls,
      dom: pageData.dom,
      storage: pageData.storage,
      cookies: cookies,
      viewport: pageData.viewport
    };

    console.log(JSON.stringify(finalContext));
  } catch (err) {
    console.error(JSON.stringify({ error: err.message }));
    process.exit(1);
  } finally {
    if (browser) await browser.close();
  }
}

main();
