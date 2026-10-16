// Visual review capture — required by AGENTS.md "Visual review before publish".
//
// Usage:
//   node scripts/shot.mjs <url> <out-prefix> [--fold]
//
// Writes <out-prefix>-1440.png and <out-prefix>-390.png as full-page captures.
// Run it against production and against the preview URL, then look at both.
//
// --fold captures the viewport alone instead: 1440x900 and 390x844, what a
// reader sees before scrolling. A full-page image of a 17,000px page cannot
// answer what is on the first screen, and the first screen is where this site
// has twice shipped a composition nobody had looked at.
//
// Browser: the system Google Chrome when present (the owner's laptop and VMs
// do not carry Playwright's bundled Chromium), otherwise Playwright's own
// Chromium (CI and cloud containers).
import { chromium } from '@playwright/test'

const args = process.argv.slice(2)
const fold = args.includes('--fold')
const [url, prefix] = args.filter((arg) => arg !== '--fold')
if (!url || !prefix) {
  console.error('usage: node scripts/shot.mjs <url> <out-prefix> [--fold]')
  process.exit(1)
}

const viewports = [
  { width: 1440, height: 900 },
  { width: 390, height: 844 },
]
const browser = await chromium.launch({ channel: 'chrome' }).catch(() => chromium.launch())

for (const viewport of viewports) {
  const page = await browser.newPage({
    viewport: fold ? viewport : { width: viewport.width, height: 1000 },
  })
  await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 })
  // Charts load through a dynamic import after mount; give them time to paint.
  await page.waitForTimeout(2500)
  const height = await page.evaluate(() => document.body.scrollHeight)
  const out = `${prefix}${fold ? '-fold' : ''}-${viewport.width}.png`
  await page.screenshot({ path: out, fullPage: !fold })
  console.log(
    fold
      ? `${url} @ ${viewport.width}x${viewport.height} first screen -> ${out}`
      : `${url} @ ${viewport.width}px -> ${out} (page height ${height}px)`,
  )
  await page.close()
}

await browser.close()
