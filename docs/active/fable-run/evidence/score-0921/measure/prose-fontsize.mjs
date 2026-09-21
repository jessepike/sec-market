// D6 level-3 test 4: is BODY/PROSE text (not metadata labels) at least 14px, and is line
// length in prose blocks within about 50-80 characters at 1440?
import { chromium } from '@playwright/test'
import fs from 'node:fs'
const OUT = '/mnt/mac/Users/jessepike/code/projects/sec-market/docs/active/fable-run/evidence/score-0921/measure'
const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })
await page.goto('https://securitymarketpulse.com/', { waitUntil: 'networkidle', timeout: 60000 })
await page.waitForTimeout(2000)
const data = await page.evaluate(() => {
  // sample known prose selectors: issue-lane "why" text, we-think paragraph, domain descriptions,
  // masthead description
  const selectors = [
    '.site-masthead__description',
    '.issue-lane__item p',
    '.we-think p',
    'section#we-think p',
    '.market-picture__caption',
    'p',
  ]
  const seen = new Set()
  const results = []
  for (const sel of selectors) {
    document.querySelectorAll(sel).forEach(el => {
      if (seen.has(el)) return
      const text = el.textContent.trim()
      if (text.length < 40) return // skip short labels
      seen.add(el)
      const cs = getComputedStyle(el)
      const rect = el.getBoundingClientRect()
      results.push({
        selector: sel,
        fontSize: parseFloat(cs.fontSize),
        width: Math.round(rect.width),
        text: text.slice(0, 60),
      })
    })
  }
  const fontSizes = results.map(r => r.fontSize)
  const under14 = results.filter(r => r.fontSize < 14)
  return { totalProseNodes: results.length, under14Count: under14.length, under14Sample: under14.slice(0, 10), fontSizeDistribution: [...new Set(fontSizes)].sort((a,b)=>a-b) }
})
fs.writeFileSync(`${OUT}/prose-fontsize.json`, JSON.stringify(data, null, 2))
console.log(JSON.stringify(data, null, 2))
await browser.close()
