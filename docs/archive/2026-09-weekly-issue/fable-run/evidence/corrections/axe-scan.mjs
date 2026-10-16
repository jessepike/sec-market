// THROWAWAY axe scan for T6-13, following the pattern in
// docs/archive/2026-09-weekly-issue/fable-run/evidence/wave1/axe-scan.mjs (read-only reference,
// not modified). Runs against the local preview server.
import { chromium } from '@playwright/test'
import fs from 'node:fs'

const base = process.argv[2] ?? 'http://127.0.0.1:4173'
const outPath = process.argv[3] ?? '/mnt/mac/Users/jessepike/code/projects/sec-market/docs/active/fable-run/evidence/corrections/axe-results.json'
const pages = [
  { path: '/', name: 'home' },
  { path: '/corrections/', name: 'corrections' },
]
const widths = [1440, 390]

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

fs.writeFileSync(outPath, JSON.stringify(results, null, 2))

await browser.close()
console.log('done')
