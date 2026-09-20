import { chromium } from 'playwright';
import { promises as fs } from 'fs';
import { existsSync, mkdirSync } from 'fs';
import { dirname, resolve } from 'path';

const BASE_DIR = '/mnt/mac/Users/jessepike/code/projects/sec-market/docs/active/fable-run/evidence/baseline';
const DRAWER_DIR = resolve(BASE_DIR, 'drawer');

async function ensureDir(path) {
  const dir = dirname(path);
  if (!existsSync(dir)) {
    mkdirSync(dir, { recursive: true });
  }
}

async function waitForNetworkIdle(page, timeout = 10000) {
  try {
    await page.waitForLoadState('networkidle', { timeout });
  } catch {
    // Network idle timed out; continue anyway
  }
  await page.waitForTimeout(1000);
}

async function extractDrawerContent(page) {
  // Find what opened: dialog, drawer, popover, or expanded region
  const dialogs = await page.locator('dialog').all();
  const drawers = await page.locator('[role="complementary"]').all();
  const popovers = await page.locator('[role="dialog"]').all();

  let openedElement = null;
  let elementType = '';

  // Check each in order
  for (const dialog of dialogs) {
    if (await dialog.isVisible().catch(() => false)) {
      openedElement = dialog;
      elementType = 'dialog';
      break;
    }
  }

  if (!openedElement) {
    for (const drawer of drawers) {
      if (await drawer.isVisible().catch(() => false)) {
        openedElement = drawer;
        elementType = 'drawer';
        break;
      }
    }
  }

  if (!openedElement) {
    for (const popover of popovers) {
      if (await popover.isVisible().catch(() => false)) {
        openedElement = popover;
        elementType = 'popover';
        break;
      }
    }
  }

  if (!openedElement) {
    return { elementType: 'unknown', text: '', links: [] };
  }

  // Extract all text
  const text = await openedElement.textContent();

  // Extract all links
  const links = [];
  const linkElements = await openedElement.locator('a').all();
  for (const link of linkElements) {
    const href = await link.getAttribute('href');
    const linkText = await link.textContent();
    if (href) {
      links.push({ href, text: linkText?.trim() || '' });
    }
  }

  return { elementType, text: text?.trim() || '', links };
}

async function measureAt(width, height, urlLabel) {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width, height } });

  // Load page
  await page.goto('https://securitymarketpulse.com/', { waitUntil: 'domcontentloaded' });
  await waitForNetworkIdle(page);

  const results = [];

  // Measurement 1a: First "View evidence:" button
  console.log(`[${urlLabel} ${width}x${height}] Finding first evidence button...`);
  try {
    const firstEvidenceBtn = await page.locator('button').filter({ hasText: /View evidence:/ }).first();

    if (await firstEvidenceBtn.isVisible({ timeout: 5000 }).catch(() => false)) {
      await firstEvidenceBtn.click();
      await page.waitForTimeout(1000);

      const content = await extractDrawerContent(page);
      results.push({
        measurement: '1a - First evidence button',
        button_text: 'View evidence: [Return on Security]',
        ...content
      });

      // Capture screenshot
      if (width === 1440) {
        await ensureDir(`${DRAWER_DIR}/dummy`);
        const screenshotPath = `${DRAWER_DIR}/evidence-open-1440.png`;
        await page.screenshot({ path: screenshotPath });
        console.log(`Saved: ${screenshotPath}`);
      } else if (width === 390) {
        await ensureDir(`${DRAWER_DIR}/dummy`);
        const screenshotPath = `${DRAWER_DIR}/evidence-open-390.png`;
        await page.screenshot({ path: screenshotPath });
        console.log(`Saved: ${screenshotPath}`);
      }

      // Close by pressing Escape
      await page.keyboard.press('Escape');
      await page.waitForTimeout(300);
    }
  } catch (e) {
    console.log(`Warning: First evidence button error: ${e.message}`);
  }

  // Measurement 1b: Evidence button mentioning CrowdStrike or Palo Alto
  console.log(`[${urlLabel} ${width}x${height}] Finding CrowdStrike/Palo Alto evidence button...`);
  try {
    const csBtn = await page.locator('button').filter({ hasText: /View evidence:/ }).filter({ hasText: /CrowdStrike|Palo Alto/ }).first();

    if (await csBtn.isVisible({ timeout: 5000 }).catch(() => false)) {
      await csBtn.click();
      await page.waitForTimeout(1000);

      const content = await extractDrawerContent(page);
      results.push({
        measurement: '1b - CrowdStrike/Palo Alto evidence',
        ...content
      });

      await page.keyboard.press('Escape');
      await page.waitForTimeout(300);
    } else {
      console.log(`Note: CrowdStrike evidence button not found in viewport`);
    }
  } catch (e) {
    console.log(`Note: CrowdStrike evidence button error: ${e.message}`);
  }

  // Measurement 1c: First "Sources" button
  console.log(`[${urlLabel} ${width}x${height}] Finding first Sources button...`);
  try {
    const firstSourcesBtn = await page.locator('button').filter({ hasText: /^Sources$/ }).first();

    if (await firstSourcesBtn.isVisible({ timeout: 5000 }).catch(() => false)) {
      await firstSourcesBtn.click();
      await page.waitForTimeout(1000);

      const content = await extractDrawerContent(page);
      results.push({
        measurement: '1c - First Sources button',
        ...content
      });

      await page.keyboard.press('Escape');
      await page.waitForTimeout(300);
    }
  } catch (e) {
    console.log(`Warning: First sources button error: ${e.message}`);
  }

  // Measurement 2: Chrome height
  console.log(`[${urlLabel} ${width}x${height}] Measuring chrome height...`);

  try {
    // Get H1 bounding rect
    const h1 = await page.locator('h1').first();
    const h1Rect = await h1.boundingBox({ timeout: 5000 });

    // Get eyebrow element - look for the text containing ISSUE
    const eyebrowText = await page.locator('text=/ISSUE.*2026.*W36/', { timeout: 5000 }).first();
    let eyebrowRect = null;

    try {
      eyebrowRect = await eyebrowText.boundingBox();
    } catch {
      // Try finding parent element
      const eyebrowParent = await page.locator('[class*="issue"i][class*="eyebrow"i]').first();
      try {
        eyebrowRect = await eyebrowParent.boundingBox();
      } catch {
        console.log('Could not find eyebrow element');
      }
    }

    const chromeHeight = eyebrowRect ? eyebrowRect.y : 0;
    const chromePercent = height > 0 ? ((chromeHeight / height) * 100).toFixed(1) : 0;

    results.push({
      measurement: '2 - Chrome height',
      h1_y: h1Rect?.y || null,
      eyebrow_y: eyebrowRect?.y || null,
      chrome_height_px: chromeHeight,
      chrome_percent_of_viewport: `${chromePercent}%`,
      viewport_height: height
    });
  } catch (e) {
    console.log(`Warning: Chrome height measurement error: ${e.message}`);
    results.push({
      measurement: '2 - Chrome height',
      error: e.message
    });
  }

  await browser.close();
  return results;
}

async function main() {
  const all_results = [];

  // Run at both sizes
  console.log('Starting measurements at 1440x900...');
  const results_1440 = await measureAt(1440, 900, 'prod');
  all_results.push(...results_1440);

  console.log('Starting measurements at 390x844...');
  const results_390 = await measureAt(390, 844, 'prod');
  all_results.push(...results_390);

  // Write results as JSON for now
  await ensureDir(`${DRAWER_DIR}/dummy`);
  const reportPath = resolve(BASE_DIR, 'evidence-drawer-raw.json');
  await fs.writeFile(
    reportPath,
    JSON.stringify(all_results, null, 2)
  );

  console.log(`\nResults written to ${reportPath}`);
}

main().catch(console.error);
