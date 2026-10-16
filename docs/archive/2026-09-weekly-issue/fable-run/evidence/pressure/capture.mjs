// THROWAWAY capture script for the T7-9 Platform-pressure wording visual
// review (SEC-054, D-75). Not part of the product codebase.
//
// Mirrors docs/archive/2026-09-weekly-issue/fable-run/evidence/baseline/capture.mjs's reason for
// existing (web/scripts/shot.mjs needs a real Google Chrome binary that the
// OrbStack dev VM does not have), but instead of a full-page screenshot this
// crops to just the two areas this task actually changed: the "Buying in
// rather than building" Platform-pressure group, and the /corrections/ page.
// Keeps the evidence set small (at most 8 images, each under 400KB) instead
// of shipping full 1440px page screenshots for a change that touched one
// table group and one standing page.
//
// Usage:
//   node capture.mjs <base-url> <out-prefix>
//
// Writes, for each of the two widths:
//   <out-prefix>-<width>-pressure.png     (crop: the "Buying in..." pressure group)
//   <out-prefix>-<width>-corrections.png  (crop: the /corrections/ page content)
import { chromium } from '@playwright/test'

const [, , baseUrl, prefix] = process.argv
if (!baseUrl || !prefix) {
  console.error('usage: node capture.mjs <base-url> <out-prefix>')
  process.exit(1)
}

const configs = [
  { width: 1440, height: 1400 },
  { width: 390, height: 1400 },
]

const browser = await chromium.launch()

for (const { width, height } of configs) {
  const page = await browser.newPage({ viewport: { width, height } })

  await page.goto(new URL('/', baseUrl).toString(), { waitUntil: 'networkidle', timeout: 60000 })
  await page.waitForTimeout(1000)
  const pressureGroup = page
    .locator('.pressure-table__group--buying-in:visible, .pressure-stack--buying-in:visible')
    .first()
  await pressureGroup.scrollIntoViewIfNeeded()
  const pressureOut = `${prefix}-${width}-pressure.png`
  await pressureGroup.screenshot({ path: pressureOut })
  console.log(`${baseUrl} @ ${width}px -> ${pressureOut} (Platform pressure: buying-in group)`)

  await page.goto(new URL('/corrections/', baseUrl).toString(), { waitUntil: 'networkidle', timeout: 60000 })
  await page.waitForTimeout(500)
  const correctionsOut = `${prefix}-${width}-corrections.png`
  await page.locator('.corrections-page').screenshot({ path: correctionsOut })
  console.log(`${baseUrl} @ ${width}px -> ${correctionsOut} (/corrections/ page)`)

  await page.close()
}

await browser.close()
