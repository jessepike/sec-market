import { chromium } from 'playwright';
import { promises as fs } from 'fs';
import { mkdirSync } from 'fs';

const BASE = '/mnt/mac/Users/jessepike/code/projects/sec-market/docs/active/fable-run/evidence/baseline';
mkdirSync(`${BASE}/drawer`, { recursive: true });

async function measureAt(width, height, widthLabel) {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width, height } });

  await page.goto('https://securitymarketpulse.com/', { waitUntil: 'domcontentloaded' });
  await page.waitForLoadState('networkidle', { timeout: 5000 }).catch(() => {});
  await page.waitForTimeout(500);

  const results = {
    viewport: `${width}x${height}`,
    measurements: []
  };

  // 1a. First evidence button (should be "Return on Security")
  console.log(`[${widthLabel}] Clicking first evidence button...`);
  const firstBtn = await page.getByRole('button', { name: /View evidence:/ }).first();
  if (await firstBtn.isVisible().catch(() => false)) {
    const ariaLabel = await firstBtn.getAttribute('aria-label');
    console.log(`  Found: "${ariaLabel}"`);

    await firstBtn.click();
    await page.waitForTimeout(1000);

    // Screenshot
    const pngPath = `${BASE}/drawer/evidence-open-${widthLabel}.png`;
    await page.screenshot({ path: pngPath });
    console.log(`  Screenshot: ${pngPath}`);

    // Extract drawer content
    const drawer = await page.locator('[role="complementary"], dialog, [role="dialog"]').first();
    if (await drawer.isVisible().catch(() => false)) {
      const text = await drawer.textContent();
      const links = [];
      const allLinks = await drawer.locator('a').all();
      for (const link of allLinks) {
        const href = await link.getAttribute('href');
        const txt = await link.textContent();
        if (href) {
          links.push({ href, text: txt?.trim() || '' });
        }
      }
      results.measurements.push({
        name: '1a-first-evidence',
        button_label: ariaLabel,
        drawer_text_length: text?.length || 0,
        links_found: links.length,
        links: links.slice(0, 5) // Just first 5 for report
      });
    }

    await page.keyboard.press('Escape');
    await page.waitForTimeout(500);
  }

  // 1b. CrowdStrike or Palo Alto evidence button
  console.log(`[${widthLabel}] Looking for CrowdStrike/Palo Alto button...`);
  const allEvidenceBtns = await page.getByRole('button', { name: /View evidence:/ }).all();
  let foundCS = false;
  for (const btn of allEvidenceBtns) {
    const label = await btn.getAttribute('aria-label');
    if (label && (label.includes('CrowdStrike') || label.includes('Palo Alto'))) {
      console.log(`  Found: "${label}"`);
      await btn.click();
      await page.waitForTimeout(1000);

      const drawer = await page.locator('[role="complementary"], dialog, [role="dialog"]').first();
      if (await drawer.isVisible().catch(() => false)) {
        const text = await drawer.textContent();
        const links = [];
        const allLinks = await drawer.locator('a').all();
        for (const link of allLinks) {
          const href = await link.getAttribute('href');
          const txt = await link.textContent();
          if (href) links.push({ href, text: txt?.trim() || '' });
        }
        results.measurements.push({
          name: '1b-crowdstrike-paloalto',
          button_label: label,
          drawer_text_length: text?.length || 0,
          links_found: links.length
        });
      }

      await page.keyboard.press('Escape');
      await page.waitForTimeout(500);
      foundCS = true;
      break;
    }
  }
  if (!foundCS) {
    console.log(`  Not found in viewport`);
  }

  // 1c. First "Sources" button
  console.log(`[${widthLabel}] Looking for Sources button...`);
  const sourcesBtn = await page.getByRole('button', { name: 'Sources' }).first();
  if (await sourcesBtn.isVisible().catch(() => false)) {
    console.log(`  Found Sources button`);
    await sourcesBtn.click();
    await page.waitForTimeout(1000);

    const drawer = await page.locator('[role="complementary"], dialog, [role="dialog"]').first();
    if (await drawer.isVisible().catch(() => false)) {
      const text = await drawer.textContent();
      const links = [];
      const allLinks = await drawer.locator('a').all();
      for (const link of allLinks) {
        const href = await link.getAttribute('href');
        const txt = await link.textContent();
        if (href) links.push({ href, text: txt?.trim() || '' });
      }
      results.measurements.push({
        name: '1c-sources',
        button_label: 'Sources',
        drawer_text_length: text?.length || 0,
        links_found: links.length
      });
    }

    await page.keyboard.press('Escape');
    await page.waitForTimeout(500);
  }

  // 2. Chrome height
  console.log(`[${widthLabel}] Measuring chrome height...`);
  const h1 = await page.locator('h1').first();
  const eyebrow = await page.locator('text=/ISSUE.*W36/i').first();

  const h1Box = await h1.boundingBox().catch(() => null);
  const eyebrowBox = await eyebrow.boundingBox().catch(() => null);

  const chromeHeightPx = eyebrowBox?.y || 0;
  const chromePercent = height > 0 ? ((chromeHeightPx / height) * 100).toFixed(1) : 0;

  results.measurements.push({
    name: '2-chrome-height',
    h1_y_px: h1Box?.y || null,
    eyebrow_y_px: eyebrowBox?.y || null,
    chrome_height_px: chromeHeightPx,
    chrome_height_percent_of_viewport: chromePercent,
    viewport_height: height
  });

  console.log(`  Chrome: ${chromeHeightPx}px (${chromePercent}% of ${height})`);

  await browser.close();
  return results;
}

async function main() {
  console.log('Starting measurements...\n');

  const results_1440 = await measureAt(1440, 900, '1440');
  const results_390 = await measureAt(390, 844, '390');

  const allResults = {
    measurements_1440x900: results_1440,
    measurements_390x844: results_390,
    summary: {
      chrome_height_1440: `${results_1440.measurements.find(m => m.name === '2-chrome-height')?.chrome_height_px || 'N/A'}px`,
      chrome_height_390: `${results_390.measurements.find(m => m.name === '2-chrome-height')?.chrome_height_px || 'N/A'}px (${results_390.measurements.find(m => m.name === '2-chrome-height')?.chrome_height_percent_of_viewport || 'N/A'}% of 844)`
    }
  };

  const reportPath = `${BASE}/evidence-drawer.json`;
  await fs.writeFile(reportPath, JSON.stringify(allResults, null, 2));

  console.log(`\n✓ Report saved: ${reportPath}`);
  console.log('\nSummary:');
  console.log(`  1440x900 chrome: ${allResults.summary.chrome_height_1440}`);
  console.log(`  390x844 chrome: ${allResults.summary.chrome_height_390}`);
}

main().catch(err => {
  console.error('Error:', err);
  process.exit(1);
});
