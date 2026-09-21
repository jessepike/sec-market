// THROWAWAY capture script for the T7-4 reconfirmation evidence step.
// Adapted from docs/active/fable-run/evidence/baseline/capture.mjs (not modified —
// that file stays as the T1-7 baseline capture tool). Same reason for existing:
// web/scripts/shot.mjs needs a real Google Chrome binary, which the OrbStack dev
// VM does not have; this uses chromium.launch() (no channel) instead.
//
// Unlike capture.mjs, this crops to a single element (a JUDGED/RECONFIRMED stamp)
// rather than capturing the whole page, so the evidence images stay small and the
// reviewer can see the stamp's own wrapping behavior directly.
//
// Usage:
//   node capture-stamp.mjs <url> <out-dir>
//
// Writes four PNGs: one domain-board stamp at 1440 and 390, one Platform-pressure
// (mobile stack) stamp at 1440 and 390 — all four carrying the one temporary
// fixture reconfirmation added locally for this evidence step, never committed.
import { chromium } from '@playwright/test'

const [, , url, outDir] = process.argv
if (!url || !outDir) {
  console.error('usage: node capture-stamp.mjs <url> <out-dir>')
  process.exit(1)
}

// The Platform-pressure mobile stack (`.pressure__mobile`) is CSS-hidden above the
// phone breakpoint, so only capture it at 390. The domain-board card is visible at
// both widths, so capture it at both to check the reconfirmed stamp doesn't wrap
// badly at either.
const targets = [
  { name: 'domain-board-stamp', selector: '.domain-card:has-text("RECONFIRMED") .domain-card__layer--judged', widths: [1440, 390] },
  { name: 'platform-pressure-stamp', selector: '.pressure-stack:has-text("RECONFIRMED") .pressure-stack__row', widths: [390] },
]

const browser = await chromium.launch()

for (const { name, selector, widths } of targets) {
  for (const width of widths) {
    const page = await browser.newPage({ viewport: { width, height: 1000 } })
    await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 })
    await page.waitForTimeout(1500)

    const locator = page.locator(selector).first()
    const count = await locator.count()
    if (count === 0) {
      console.error(`${name} @ ${width}px -> NOT FOUND (selector: ${selector})`)
      await page.close()
      continue
    }
    await locator.scrollIntoViewIfNeeded()
    const out = `${outDir}/${name}-${width}.png`
    await locator.screenshot({ path: out })
    console.log(`${url} @ ${width}px -> ${out}`)
    await page.close()
  }
}

await browser.close()
