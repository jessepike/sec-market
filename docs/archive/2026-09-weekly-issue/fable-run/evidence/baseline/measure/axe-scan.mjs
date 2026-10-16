// THROWAWAY script for accessibility measurement (item 2).
// Run with working directory = web/ so bare imports resolve from web/node_modules,
// per the pattern in docs/archive/2026-09-weekly-issue/fable-run/research/07-site-teardown.md.
import { chromium } from '@playwright/test'
import fs from 'node:fs'

const pages = [
  { path: '/', name: 'home' },
  { path: '/issues/', name: 'issues' },
  { path: '/issues/2026-w36/', name: 'issue-w36' },
]
const widths = [1440, 390]
const base = 'https://securitymarketpulse.com'

const browser = await chromium.launch()
const results = {}

for (const { path, name } of pages) {
  for (const width of widths) {
    const page = await browser.newPage({ viewport: { width, height: 900 } })
    await page.goto(base + path, { waitUntil: 'networkidle', timeout: 60000 })
    await page.waitForTimeout(1500)
    await page.addScriptTag({ url: 'https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.10.2/axe.min.js' })
    const axeResult = await page.evaluate(async () => {
      // @ts-ignore
      return await axe.run(document, { resultTypes: ['violations'] })
    })
    const key = `${name}-${width}`
    results[key] = axeResult.violations
    console.log(`${key}: ${axeResult.violations.length} rules violated`)
    await page.close()
  }
}

fs.writeFileSync(
  '/mnt/mac/Users/jessepike/code/projects/sec-market/docs/active/fable-run/evidence/baseline/measure/axe-results.json',
  JSON.stringify(results, null, 2)
)

await browser.close()
console.log('done')
