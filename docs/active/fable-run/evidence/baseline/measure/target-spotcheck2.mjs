import { chromium } from '@playwright/test'
const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 390, height: 844 } })
await page.goto('https://securitymarketpulse.com/', { waitUntil: 'networkidle', timeout: 60000 })
await page.waitForTimeout(1000)
const sizes = await page.evaluate(() => {
  const els = Array.from(document.querySelectorAll('a, button, summary'))
  return els.map(el => {
    const r = el.getBoundingClientRect()
    return { tag: el.tagName, w: Math.round(r.width*10)/10, h: Math.round(r.height*10)/10, text: (el.textContent||'').trim().slice(0,30) }
  }).filter(x => !(x.w===0 && x.h===0)).sort((a,b) => (a.w*a.h)-(b.w*b.h))
})
console.log(JSON.stringify(sizes.slice(0,20), null, 2))
await browser.close()
