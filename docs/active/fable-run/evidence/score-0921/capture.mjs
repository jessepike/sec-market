// Adapted capture script for T7-7 live-site scoring. Copy of evidence/after/capture.mjs,
// target changed to the live production host only (this scorer scores the live site).
// Captures screenshots at 1440x900 and 390x844 viewports for:
// / , /thesis/ , /issues/2026-w36/
// Files saved to docs/active/fable-run/evidence/score-0921/

import { chromium } from '@playwright/test'

const prodBase = 'https://securitymarketpulse.com'

const urls = [
  { name: 'live-home', url: `${prodBase}/` },
  { name: 'live-thesis', url: `${prodBase}/thesis/` },
  { name: 'live-issue-w36', url: `${prodBase}/issues/2026-w36/` },
]

const viewports = [
  { width: 1440, height: 900 },
  { width: 390, height: 844 },
]

const browser = await chromium.launch()

for (const { name, url } of urls) {
  for (const { width, height } of viewports) {
    const page = await browser.newPage({ viewport: { width, height } })
    await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 })
    // Charts load through a dynamic import after mount; give them time to paint.
    await page.waitForTimeout(2500)

    const viewportOut = `${name}-${width}-viewport.png`
    await page.screenshot({ path: viewportOut, fullPage: false })
    console.log(`${url} @ ${width}px -> ${viewportOut} (first viewport, ${width}x${height})`)

    const pageHeight = await page.evaluate(() => document.documentElement.scrollHeight)
    const fullOut = `${name}-${width}-full.png`
    await page.screenshot({ path: fullOut, fullPage: true })
    console.log(`${url} @ ${width}px -> ${fullOut} (full page, page height ${pageHeight}px)`)

    await page.close()
  }
}

await browser.close()
console.log('All screenshots captured.')
