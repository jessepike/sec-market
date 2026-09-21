// THROWAWAY script for locating tab-stop offsets around the "Signed by" region.
// Copy of baseline/measure/keyboard-walk-offsets.mjs, target changed to preview.
import { chromium } from '@playwright/test'
const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })
await page.goto('https://securitymarketpulse.com/', { waitUntil: 'networkidle', timeout: 60000 })
await page.waitForTimeout(1000)
const rows = []
for (let i = 1; i <= 80; i++) {
  await page.keyboard.press('Tab')
  await page.waitForTimeout(40)
  const info = await page.evaluate(() => {
    const el = document.activeElement
    if (!el || el === document.body) return null
    const rect = el.getBoundingClientRect()
    return { tag: el.tagName, absoluteTop: Math.round(rect.top + window.scrollY), text: (el.textContent||'').trim().slice(0,30) }
  })
  rows.push({ press: i, ...info })
}
console.log(JSON.stringify(rows))
await browser.close()
