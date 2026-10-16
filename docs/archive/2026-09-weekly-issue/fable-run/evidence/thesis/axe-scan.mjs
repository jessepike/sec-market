// THROWAWAY axe scan for SEC-MARKET-FABLE-001 T6-16, following the pattern in
// docs/archive/2026-09-weekly-issue/fable-run/evidence/wave1/axe-scan.mjs (read-only reference).
// Not committed — a copy is saved to docs/archive/2026-09-weekly-issue/fable-run/evidence/thesis/axe-scan.mjs.
import { chromium } from '@playwright/test'
import fs from 'node:fs'

const base = 'http://127.0.0.1:4181'
const pages = [{ path: '/thesis/', name: 'thesis' }]
const widths = [1440, 390]

const browser = await chromium.launch()
const results = {}

for (const { path, name } of pages) {
  for (const width of widths) {
    const page = await browser.newPage({ viewport: { width, height: 900 } })
    await page.goto(base + path, { waitUntil: 'networkidle', timeout: 60000 })
    await page.waitForTimeout(1000)
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
  '/mnt/mac/Users/jessepike/code/projects/sec-market/docs/active/fable-run/evidence/thesis/axe-results.json',
  JSON.stringify(results, null, 2),
)

await browser.close()
console.log('done')
