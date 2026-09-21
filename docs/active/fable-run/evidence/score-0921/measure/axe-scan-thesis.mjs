// Supplementary axe scan for /thesis/, not in the rubric's named D10 routes but useful
// context since the task instructions list /thesis/ among pages to check.
import { chromium } from '@playwright/test'
import fs from 'node:fs'

const base = 'https://securitymarketpulse.com'
const widths = [1440, 390]
const OUT = '/mnt/mac/Users/jessepike/code/projects/sec-market/docs/active/fable-run/evidence/score-0921/measure'

const browser = await chromium.launch()
const results = {}
for (const width of widths) {
  const page = await browser.newPage({ viewport: { width, height: 900 } })
  await page.goto(base + '/thesis/', { waitUntil: 'networkidle', timeout: 60000 })
  await page.waitForTimeout(1500)
  await page.addScriptTag({ url: 'https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.10.2/axe.min.js' })
  const axeResult = await page.evaluate(async () => {
    return await axe.run(document, { resultTypes: ['violations'] })
  })
  const key = `thesis-${width}`
  results[key] = axeResult.violations
  console.log(`${key}: ${axeResult.violations.length} rules violated`)
  await page.close()
}
fs.writeFileSync(`${OUT}/axe-results-thesis.json`, JSON.stringify(results, null, 2))
await browser.close()
console.log('done')
