import { chromium } from 'playwright';

async function measureChrome(width, height, label) {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width, height } });

  await page.goto('https://securitymarketpulse.com/', { waitUntil: 'domcontentloaded' });
  await page.waitForLoadState('networkidle', { timeout: 5000 }).catch(() => {});
  await page.waitForTimeout(500);

  // Find eyebrow - try different selectors
  let eyebrowBox = null;

  // Try finding by text content
  const eyebrowText = await page.locator('text=/ISSUE.*2026.*W36/i').first();
  try {
    eyebrowBox = await eyebrowText.boundingBox({ timeout: 2000 });
  } catch {
    console.log(`${label}: Could not find via text regex`);
  }

  // If not found, try finding the actual eyebrow element
  if (!eyebrowBox) {
    const allText = await page.locator('text=/ISSUE/i').all();
    for (const el of allText) {
      const box = await el.boundingBox().catch(() => null);
      if (box && box.y > 0 && box.y < 500) { // Chrome should be near top
        console.log(`${label}: Found potential eyebrow at y=${box.y}`);
        eyebrowBox = box;
        break;
      }
    }
  }

  // Get all visible elements near the top
  if (!eyebrowBox) {
    console.log(`${label}: Scanning all elements to find chrome...`);
    const allElements = await page.locator('*').all();
    const topElements = [];
    for (let i = 0; i < Math.min(100, allElements.length); i++) {
      const el = allElements[i];
      const box = await el.boundingBox().catch(() => null);
      const text = await el.textContent().catch(() => '');
      if (box && box.y >= 0 && box.y < 300) {
        topElements.push({ y: box.x, text: text?.substring(0, 50) || '(empty)' });
      }
    }
    topElements.sort((a, b) => a.y - b.y);
    topElements.slice(0, 10).forEach(el => {
      console.log(`  ${el.y}px: ${el.text}`);
    });
  }

  const h1Box = await page.locator('h1').first().boundingBox().catch(() => null);

  console.log(`\n${label} results:`);
  console.log(`  H1 (headline) y: ${h1Box?.y || 'not found'}`);
  console.log(`  Eyebrow y: ${eyebrowBox?.y || 'not found'}`);

  if (eyebrowBox) {
    const chromeHeight = eyebrowBox.y;
    const chromePercent = ((chromeHeight / height) * 100).toFixed(1);
    console.log(`  Chrome height: ${chromeHeight}px (${chromePercent}% of ${height})`);
  }

  await browser.close();
}

async function main() {
  await measureChrome(1440, 900, '1440x900');
  console.log('');
  await measureChrome(390, 844, '390x844');
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
