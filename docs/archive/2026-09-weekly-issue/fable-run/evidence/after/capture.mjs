// Adapted capture script for T6-8 fable-run evidence collection.
// Captures screenshots at 1440x900 and 390x844 viewports for:
// - preview home, issues archive, and specific issue (w36)
// - production home only
// Files saved to docs/archive/2026-09-weekly-issue/fable-run/evidence/after/

import { chromium } from '@playwright/test'
import { writeFileSync } from 'fs'
import { resolve } from 'path'

const previewBase = 'https://security-market-pulse-git-preview-pikeholdings.vercel.app'
const prodBase = 'https://securitymarketpulse.com'

const urls = [
  { name: 'after-home', url: `${previewBase}/` },
  { name: 'after-issues', url: `${previewBase}/issues/` },
  { name: 'after-issue-w36', url: `${previewBase}/issues/2026-w36/` },
  { name: 'prodnow-home', url: prodBase, prodOnly: true },
]

const viewports = [
  { width: 1440, height: 900 },
  { width: 390, height: 844 },
]

const browser = await chromium.launch()

for (const { name, url, prodOnly } of urls) {
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
