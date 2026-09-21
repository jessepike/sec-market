import { chromium } from '@playwright/test'
import fs from 'node:fs'
const OUT = '/mnt/mac/Users/jessepike/code/projects/sec-market/docs/active/fable-run/evidence/score-0921/measure'
const pages = [
  { url: 'https://securitymarketpulse.com/', name: 'home' },
  { url: 'https://securitymarketpulse.com/thesis/', name: 'thesis' },
  { url: 'https://securitymarketpulse.com/issues/2026-w36/', name: 'issue-w36' },
  { url: 'https://securitymarketpulse.com/corrections/', name: 'corrections' },
  { url: 'https://securitymarketpulse.com/method/', name: 'method' },
  { url: 'https://securitymarketpulse.com/issues/', name: 'issues' },
]
const browser = await chromium.launch()
for (const { url, name } of pages) {
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })
  try {
    await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 })
    await page.waitForTimeout(2500)
    // expand all details so text is captured
    await page.evaluate(() => document.querySelectorAll('details').forEach(d => d.open = true))
    await page.waitForTimeout(500)
    const text = await page.evaluate(() => document.body.innerText)
    fs.writeFileSync(`${OUT}/text-${name}.txt`, text)
    console.log(`${name}: ${text.length} chars`)
  } catch (e) {
    console.log(`${name}: ERROR ${e.message}`)
  }
  await page.close()
}
await browser.close()
