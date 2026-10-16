import { chromium } from '@playwright/test'
const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 390, height: 844 } })
await page.goto('https://securitymarketpulse.com/', { waitUntil: 'networkidle', timeout: 60000 })
await page.waitForTimeout(1000)
const sizes = await page.evaluate(() => {
  const els = Array.from(document.querySelectorAll('a, button, summary')).slice(0, 15)
  return els.map(el => {
    const r = el.getBoundingClientRect()
    return { tag: el.tagName, w: Math.round(r.width), h: Math.round(r.height), text: (el.textContent||'').trim().slice(0,30) }
  })
})
console.log(JSON.stringify(sizes, null, 2))
await browser.close()
