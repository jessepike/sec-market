import { chromium } from '@playwright/test'
const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })
await page.goto('https://securitymarketpulse.com/', { waitUntil: 'networkidle', timeout: 60000 })
await page.waitForTimeout(1000)
for (let i = 1; i <= 34; i++) {
  await page.keyboard.press('Tab')
  await page.waitForTimeout(40)
  const info = await page.evaluate(() => {
    const el = document.activeElement
    const rect = el.getBoundingClientRect()
    return { tag: el.tagName, absoluteTop: Math.round(rect.top + window.scrollY), text: (el.textContent||'').trim().slice(0,40) }
  })
  if (i >= 32) console.log(i, JSON.stringify(info))
}
await browser.close()
