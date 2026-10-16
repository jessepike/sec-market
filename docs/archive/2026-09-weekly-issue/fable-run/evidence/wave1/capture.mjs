// THROWAWAY capture script for T6-2 (wave 1 build evidence), adapted from
// docs/archive/2026-09-weekly-issue/fable-run/evidence/baseline/capture.mjs (that file is NOT
// modified — this is a copy). Same chromium.launch() approach (no channel:
// 'chrome'), because the OrbStack dev VM only has Playwright's own chromium
// builds, not a Google Chrome binary. Run from the worktree's web/ folder so
// bare imports resolve from its node_modules.
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
