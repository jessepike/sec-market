// Visual review capture — required by AGENTS.md "Visual review before publish".
//
// Usage:
//   node scripts/shot.mjs <url> <out-prefix>
//
// Writes <out-prefix>-1440.png and <out-prefix>-390.png as full-page captures.
// Run it against production and against the preview URL, then look at both.
//
// Note: launch uses { channel: 'chrome' } on purpose. Playwright's bundled
// chromium headless shell is not installed on this host and installing it
// would violate the host-protection rule; the system Chrome is already here.
import { chromium } from '@playwright/test'

const [, , url, prefix] = process.argv
if (!url || !prefix) {
  console.error('usage: node scripts/shot.mjs <url> <out-prefix>')
  process.exit(1)
}

const widths = [1440, 390]
const browser = await chromium.launch({ channel: 'chrome' })

for (const width of widths) {
  const page = await browser.newPage({ viewport: { width, height: 1000 } })
  await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 })
  // Charts load through a dynamic import after mount; give them time to paint.
  await page.waitForTimeout(2500)
  const height = await page.evaluate(() => document.body.scrollHeight)
  const out = `${prefix}-${width}.png`
  await page.screenshot({ path: out, fullPage: true })
  console.log(`${url} @ ${width}px -> ${out} (page height ${height}px)`)
  await page.close()
}

await browser.close()
