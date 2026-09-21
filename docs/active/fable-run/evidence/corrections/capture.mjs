// THROWAWAY capture script for T6-13 (corrections mechanism build evidence),
// adapted from docs/active/fable-run/evidence/wave1/capture.mjs. Same
// chromium.launch() approach (no channel: 'chrome'), because the OrbStack
// dev VM only has Playwright's own chromium builds. Run with cwd set to the
// worktree's web/ folder so the bare '@playwright/test' import resolves from
// its node_modules.
//
// Usage:
//   node capture.mjs <base-url> <out-dir>
//
// Writes:
//   corrections-1440-full.png / corrections-390-full.png       — /corrections/ full page
//   front-1440-full.png / front-390-full.png                   — front page full page (height reference)
//   front-1440-crop-<item>.png / front-390-crop-<item>.png     — cropped corrected lane item
//   issue-1440-crop-<item>.png                                 — issue permalink, corrected item, 1440 only
import { chromium } from '@playwright/test'
import { mkdirSync } from 'node:fs'

const [, , base, outDir] = process.argv
if (!base || !outDir) {
  console.error('usage: node capture.mjs <base-url> <out-dir>')
  process.exit(1)
}
mkdirSync(outDir, { recursive: true })

const widths = [1440, 390]
const items = ['2026-w36-prints-2', '2026-w36-prints-6']

const browser = await chromium.launch()

async function shootFullPage(path, outFile, width) {
  const page = await browser.newPage({ viewport: { width, height: 900 } })
  await page.goto(`${base}${path}`, { waitUntil: 'networkidle', timeout: 60000 })
  await page.waitForTimeout(1500)
  const height = await page.evaluate(() => document.body.scrollHeight)
  await page.screenshot({ path: outFile, fullPage: true })
  console.log(`${base}${path} @ ${width}px -> ${outFile} (full page, height ${height}px)`)
  await page.close()
  return height
}

async function shootItemCrop(path, itemId, outFile, width) {
  const page = await browser.newPage({ viewport: { width, height: 900 } })
  await page.goto(`${base}${path}`, { waitUntil: 'networkidle', timeout: 60000 })
  await page.waitForTimeout(1500)
  const locator = page.locator(`li:has-text("${itemId}")`).first()
  // Items don't render their own id as text — locate by the correction stamp
  // instead, which sits inside the target <li>, then screenshot that <li>.
  const li = page
    .locator('.issue-lane__item')
    .filter({ has: page.locator('.issue-lane__correction') })
    .filter({ hasText: itemId === '2026-w36-prints-2' ? 'Zscaler' : 'Palo Alto' })
    .first()
  await li.scrollIntoViewIfNeeded()
  await li.screenshot({ path: outFile })
  console.log(`${base}${path} @ ${width}px -> ${outFile} (item crop, ${itemId})`)
  await page.close()
  void locator
}

const heights = {}

for (const width of widths) {
  heights[`corrections-${width}`] = await shootFullPage('/corrections/', `${outDir}/corrections-${width}-full.png`, width)
  heights[`front-${width}`] = await shootFullPage('/', `${outDir}/front-${width}-full.png`, width)
  for (const itemId of items) {
    await shootItemCrop('/', itemId, `${outDir}/front-${width}-crop-${itemId}.png`, width)
  }
}

for (const itemId of items) {
  await shootItemCrop(`/issues/2026-w36/`, itemId, `${outDir}/issue-1440-crop-${itemId}.png`, 1440)
}

console.log('HEIGHTS: ' + JSON.stringify(heights, null, 2))

await browser.close()
