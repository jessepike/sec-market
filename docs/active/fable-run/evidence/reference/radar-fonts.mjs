// THROWAWAY script: find computed font-family for a few numeric/data elements
// on Radar's overview page (percentage stats, AS numbers) to answer "what is
// monospace" precisely instead of guessing from a screenshot.
import { chromium } from '@playwright/test'
import fs from 'node:fs'

const UA =
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'

const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, userAgent: UA })
await page.goto('https://radar.cloudflare.com/', { waitUntil: 'load', timeout: 60000 })
await page.waitForTimeout(4000)

const results = await page.evaluate(() => {
  function findByText(re) {
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT)
    const out = []
    let node
    while ((node = walker.nextNode())) {
      const t = node.textContent.trim()
      if (t && re.test(t) && t.length < 30) {
        const el = node.parentElement
        if (el) out.push({ text: t, font: getComputedStyle(el).fontFamily })
      }
    }
    return out
  }
  const pct = findByText(/^\d{1,3}(\.\d+)?%$/).slice(0, 5)
  const asn = findByText(/^AS\d+/).slice(0, 5)
  const bodyFont = getComputedStyle(document.body).fontFamily
  const heading = document.querySelector('h1, h2')
  const headingFont = heading ? getComputedStyle(heading).fontFamily : null
  return { pct, asn, bodyFont, headingFont }
})

fs.writeFileSync(
  '/mnt/mac/Users/jessepike/code/projects/sec-market/docs/active/fable-run/evidence/reference/radar-fonts.txt',
  JSON.stringify(results, null, 2),
  'utf8'
)
console.log('done')
await browser.close()
