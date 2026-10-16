import { chromium } from 'playwright';

async function debug() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

  await page.goto('https://securitymarketpulse.com/', { waitUntil: 'domcontentloaded' });
  await page.waitForLoadState('networkidle', { timeout: 5000 }).catch(() => {});
  await page.waitForTimeout(1000);

  console.log('=== ALL BUTTONS ===');
  const buttons = await page.locator('button').all();
  console.log(`Found ${buttons.length} buttons\n`);

  for (let i = 0; i < Math.min(20, buttons.length); i++) {
    const btn = buttons[i];
    const text = await btn.textContent();
    const ariaLabel = await btn.getAttribute('aria-label');
    const visible = await btn.isVisible().catch(() => false);
    console.log(`Button ${i}:`);
    console.log(`  Text: "${text}"`);
    console.log(`  Aria-label: "${ariaLabel}"`);
    console.log(`  Visible: ${visible}`);
    console.log();
  }

  // Look for evidence-related buttons
  console.log('=== EVIDENCE BUTTONS ===');
  const evidenceBtn = await page.locator('button').filter({ hasText: /evidence/i }).all();
  console.log(`Found ${evidenceBtn.length} evidence buttons\n`);

  for (let i = 0; i < evidenceBtn.length; i++) {
    const btn = evidenceBtn[i];
    const text = await btn.textContent();
    const ariaLabel = await btn.getAttribute('aria-label');
    console.log(`Evidence button ${i}: "${text.trim()}"`);
    console.log(`  Aria-label: "${ariaLabel}"`);
    console.log();
  }

  await browser.close();
}

debug().catch(console.error);
