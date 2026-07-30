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
    const page = await context.newPage();
    
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 25000 });

    const discovery = await page.evaluate(() => {
      const getElements = (selector) => {
        return Array.from(document.querySelectorAll(selector)).map((el, idx) => {
          const rect = el.getBoundingClientRect();
          return {
            id: el.id || `elem_${idx}`,
            tag: el.tagName.toLowerCase(),
            text: el.innerText ? el.innerText.trim().replace(/\s+/g, ' ').substring(0, 150) : '',
            href: el.getAttribute('href') || '',
            src: el.getAttribute('src') || '',
            type: el.getAttribute('type') || '',
            name: el.getAttribute('name') || '',
            placeholder: el.getAttribute('placeholder') || '',
            testId: el.getAttribute('data-testid') || el.getAttribute('data-test') || '',
            role: el.getAttribute('role') || '',
            ariaLabel: el.getAttribute('aria-label') || '',
            className: el.className ? String(el.className).substring(0, 100) : '',
            visible: rect.width > 0 && rect.height > 0
          };
        });
      };

      const menus = getElements('nav, [role="navigation"], header, .sidebar, .menu, .nav, nav a');
      const buttons = getElements('button, [role="button"], input[type="button"], input[type="submit"], .btn');
      const forms = getElements('form');
      const tables = getElements('table, [role="table"], .table, .grid');
      const cards = getElements('.card, [class*="card"], .panel, [class*="panel"], article');
      const dialogs = getElements('dialog, [role="dialog"], .modal, [class*="modal"]');
      const tabs = getElements('[role="tab"], .tab, [class*="tab"]');
      const dropdowns = getElements('select, [role="combobox"], .dropdown, [class*="dropdown"]');
      const inputs = getElements('input, textarea, select');
      const links = getElements('a[href]');
      const images = getElements('img[src]');

      // Build hierarchical UI Tree Structure
      const tree = {
        name: document.title || 'Root Page',
        url: window.location.href,
        children: [
          { name: 'Navigation & Menus', type: 'MENU_CONTAINER', count: menus.length, items: menus.slice(0, 30) },
          { name: 'Buttons & Triggers', type: 'BUTTON_CONTAINER', count: buttons.length, items: buttons.slice(0, 30) },
          { name: 'Forms & Inputs', type: 'FORM_CONTAINER', count: forms.length + inputs.length, items: [...forms, ...inputs].slice(0, 30) },
          { name: 'Tables & Grids', type: 'DATA_CONTAINER', count: tables.length, items: tables.slice(0, 20) },
          { name: 'Cards & Panels', type: 'CARD_CONTAINER', count: cards.length, items: cards.slice(0, 20) },
          { name: 'Dialogs & Modals', type: 'DIALOG_CONTAINER', count: dialogs.length, items: dialogs.slice(0, 10) },
          { name: 'Tabs & Navigation Links', type: 'TAB_CONTAINER', count: tabs.length + links.length, items: [...tabs, ...links].slice(0, 30) },
          { name: 'Media & Images', type: 'MEDIA_CONTAINER', count: images.length, items: images.slice(0, 20) }
        ]
      };

      return {
        title: document.title,
        url: window.location.href,
        stats: {
          totalElements: document.querySelectorAll('*').length,
          interactiveCount: menus.length + buttons.length + inputs.length + links.length
        },
        menus,
        buttons,
        forms,
        tables,
        cards,
        dialogs,
        tabs,
        dropdowns,
        inputs,
        links,
        images,
        tree
      };
    });

    console.log(JSON.stringify(discovery));
  } catch (err) {
    console.error(JSON.stringify({ error: err.message }));
    process.exit(1);
  } finally {
    if (browser) await browser.close();
  }
}

main();
