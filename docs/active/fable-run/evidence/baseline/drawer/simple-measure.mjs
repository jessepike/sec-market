import { chromium } from 'playwright';
import { promises as fs } from 'fs';
import { mkdirSync } from 'fs';
import { resolve } from 'path';

const BASE = '/mnt/mac/Users/jessepike/code/projects/sec-market/docs/active/fable-run/evidence/baseline';
mkdirSync(`${BASE}/drawer`, { recursive: true });

async function run() {
  const browser = await chromium.launch();

  // Measure at 1440x900
  console.log('Testing 1440x900...');
  const page1 = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page1.goto('https://securitymarketpulse.com/', { waitUntil: 'domcontentloaded' });
  await page1.waitForLoadState('networkidle', { timeout: 5000 }).catch(() => {});
  await page1.waitForTimeout(500);

  // Find and click first evidence button
  const evBtn1 = await page1.locator('button').filter({ hasText: /View evidence:/ }).first();
  if (await evBtn1.isVisible().catch(() => false)) {
    console.log('Found evidence button at 1440');
    await evBtn1.click();
    await page1.waitForTimeout(1000);

    // Take screenshot
    await page1.screenshot({ path: `${BASE}/drawer/evidence-open-1440.png` });
    console.log('Screenshot saved: evidence-open-1440.png');

    // Get drawer content
    const drawer = await page1.locator('[role="complementary"]').first();
    if (await drawer.isVisible().catch(() => false)) {
      const text = await drawer.textContent();
      const links = [];
      const allLinks = await drawer.locator('a').all();
      for (const link of allLinks) {
        const href = await link.getAttribute('href');
        const txt = await link.textContent();
        if (href) links.push({ href, text: txt?.trim() });
      }

      console.log('Drawer content captured');
      console.log('Text length:', text?.length);
      console.log('Links found:', links.length);
    }

    await page1.keyboard.press('Escape');
    await page1.waitForTimeout(300);
  }

  // Measure chrome height at 1440
  const h1 = await page1.locator('h1').first();
  const eyebrow = await page1.locator('text=/ISSUE.*W36/i').first();
  const h1box = await h1.boundingBox().catch(() => null);
  const eyebrightbox = await eyebrow.boundingBox().catch(() => null);

  console.log('1440x900 chrome height:');
  console.log('  H1 y:', h1box?.y);
  console.log('  Eyebrow y:', eyebrightbox?.y);

  await page1.close();

  // Measure at 390x844
  console.log('\nTesting 390x844...');
  const page2 = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await page2.goto('https://securitymarketpulse.com/', { waitUntil: 'domcontentloaded' });
  await page2.waitForLoadState('networkidle', { timeout: 5000 }).catch(() => {});
  await page2.waitForTimeout(500);

  // Find and click first evidence button
  const evBtn2 = await page2.locator('button').filter({ hasText: /View evidence:/ }).first();
  if (await evBtn2.isVisible().catch(() => false)) {
    console.log('Found evidence button at 390');
    await evBtn2.click();
    await page2.waitForTimeout(1000);

    // Take screenshot
    await page2.screenshot({ path: `${BASE}/drawer/evidence-open-390.png` });
    console.log('Screenshot saved: evidence-open-390.png');

    await page2.keyboard.press('Escape');
    await page2.waitForTimeout(300);
  }

  // Measure chrome height at 390
  const h1_2 = await page2.locator('h1').first();
  const eyebrow_2 = await page2.locator('text=/ISSUE.*W36/i').first();
  const h1box_2 = await h1_2.boundingBox().catch(() => null);
  const eyebrow_box_2 = await eyebrow_2.boundingBox().catch(() => null);

  console.log('390x844 chrome height:');
  console.log('  H1 y:', h1box_2?.y);
  console.log('  Eyebrow y:', eyebrow_box_2?.y);

  const chromePercent = eyebrow_box_2 ? ((eyebrow_box_2.y / 844) * 100).toFixed(1) : 'N/A';
  console.log('  Chrome % of 844:', chromePercent);

  await page2.close();
  await browser.close();

  console.log('\nDone!');
}

run().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
