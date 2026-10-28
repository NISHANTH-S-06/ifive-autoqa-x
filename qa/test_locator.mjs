import { chromium } from 'playwright';

async function main() {
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();
    await page.setContent('<div><button class="btn">Create Standard</button></div>');
    
    const sel = 'a:has-text("Create Standard"), button:has-text("Create Standard"), [data-testid="create-standard"], :text("Create Standard")';
    
    let raw = sel.replace(/:text\((["'])(.*?)\1\)/g, ':has-text($1$2$1)');
    raw = raw.replace(/\btext=(["'])(.*?)\1/g, ':has-text($1$2$1)');
    const parts = raw.split(',').map(s => s.trim()).filter(Boolean);
    
    let loc = null;
    for (const part of parts) {
        try {
            const l = page.locator(part);
            if (!loc) loc = l;
            else loc = loc.or(l);
        } catch (e) {
            console.log('Ignored invalid part:', part);
        }
    }
    
    console.log('LOCATOR MATCHED TEXT:', await loc.first().innerText());
    await browser.close();
}

main();
