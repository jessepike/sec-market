// Coordinator follow-up check: no tracker-table cell should clip its
// content at phone width. Run against a local `npm run preview` build:
//   CAPTURE_BASE=http://localhost:4173 node clip-check.mjs
//
// Checks every `.tracker-table td`/`th` (every domain table on the page,
// not just the first row) at 390 and 320 CSS px, and fails if any cell's
// scrollWidth exceeds its clientWidth — the DOM-level definition of
// "this content doesn't fit in its box."
import { chromium } from 'playwright'

const BASE = process.env.CAPTURE_BASE || 'http://localhost:4173'
const widths = [390, 320]
const browser = await chromium.launch()
let anyClipped = false

for (const width of widths) {
  const page = await browser.newPage({ viewport: { width, height: 844 } })
  await page.goto(`${BASE}/`, { waitUntil: 'networkidle' })
  const clipped = await page.evaluate(() => {
    const out = []
    document.querySelectorAll('.tracker-table td, .tracker-table th, .tracker-table__median td').forEach((el) => {
      if (el.scrollWidth > el.clientWidth + 1) {
        out.push({
          tag: el.tagName,
          label: el.getAttribute('data-label') || el.textContent.slice(0, 40),
          scrollWidth: el.scrollWidth,
          clientWidth: el.clientWidth,
          overflow: el.scrollWidth - el.clientWidth,
        })
      }
    })
    return out
  })
  console.log(`width ${width}: ${clipped.length} clipped cell(s) across every domain table on the page`)
  if (clipped.length) {
    anyClipped = true
    console.log(JSON.stringify(clipped, null, 2))
  }
  await page.close()
}

await browser.close()
if (anyClipped) {
  console.log('FAIL: clipping found')
  process.exit(1)
} else {
  console.log('PASS: no cell clips at any checked width, across every domain table on the page')
}
