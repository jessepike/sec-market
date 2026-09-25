// THROWAWAY capture script for the T1-7 site teardown baseline.
// Not part of the product codebase — lives in the evidence folder on purpose.
//
// web/scripts/shot.mjs launches Playwright with { channel: 'chrome' }, which
// requires an actual Google Chrome binary. The OrbStack dev VM only has
// Playwright's own chromium builds installed (no Google Chrome binary), so
// shot.mjs fails there with "Chromium distribution 'chrome' is not found".
// Modifying shot.mjs is out of scope for this task, so this script mirrors
// its logic with chromium.launch() (no channel) instead, and additionally
// captures a first-viewport-only screenshot (no fullPage) at 1440x900 and
// 390x844, which shot.mjs does not support at all.
//
// Usage:
//   node capture.mjs <url> <out-prefix>
//
// Writes, for each of the two widths:
//   <out-prefix>-<width>-full.png       (full-page capture, matches shot.mjs)
//   <out-prefix>-<width>-viewport.png   (first screen only, no scrolling)
import { chromium } from '@playwright/test'

const [, , url, prefix] = process.argv
if (!url || !prefix) {
  console.error('usage: node capture.mjs <url> <out-prefix>')
  process.exit(1)
}

const configs = [
  { width: 1440, height: 900 },
  { width: 390, height: 844 },
]

const browser = await chromium.launch()

for (const { width, height } of configs) {
  const page = await browser.newPage({ viewport: { width, height } })
  await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 })
  // Charts load through a dynamic import after mount; give them time to paint.
  await page.waitForTimeout(2500)

  const viewportOut = `${prefix}-${width}-viewport.png`
  await page.screenshot({ path: viewportOut, fullPage: false })
  console.log(`${url} @ ${width}px -> ${viewportOut} (first viewport, ${width}x${height})`)

  const pageHeight = await page.evaluate(() => document.body.scrollHeight)
  const fullOut = `${prefix}-${width}-full.png`
  await page.screenshot({ path: fullOut, fullPage: true })
  console.log(`${url} @ ${width}px -> ${fullOut} (full page, page height ${pageHeight}px)`)

  await page.close()
}

await browser.close()
