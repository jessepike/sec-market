// THROWAWAY capture script for SEC-MARKET-FABLE-001 T6-16 evidence, following
// the pattern in docs/archive/2026-09-weekly-issue/fable-run/evidence/final/capture.mjs (read-only
// reference, not modified). Runs against two local `vite preview` servers:
// baseline (origin/preview build, port 4180) and after (mon/thesis build,
// port 4181). Not committed — a copy of this file's content is saved to
// docs/archive/2026-09-weekly-issue/fable-run/evidence/thesis/capture.mjs for the record.
import { chromium } from '@playwright/test'
import { writeFileSync } from 'fs'

const baselineBase = 'http://127.0.0.1:4180'
const afterBase = 'http://127.0.0.1:4181'
const outDir = '/mnt/mac/Users/jessepike/code/projects/sec-market/docs/active/fable-run/evidence/thesis'

const viewports = [
  { width: 1440, height: 900 },
  { width: 390, height: 844 },
]

const sectionIds = ['overview', 'market', 'we-think', 'follow', 'landscape', 'platforms', 'prints', 'hypotheses', 'read', 'method']

async function measure(page) {
  return page.evaluate((ids) => {
    const pageHeight = document.documentElement.scrollHeight
    const result = { pageHeight }
    for (const id of ids) {
      const el = document.getElementById(id)
      result[id] = el ? Math.round(el.getBoundingClientRect().top + window.scrollY) : null
    }
    return result
  }, sectionIds)
}

const browser = await chromium.launch()
const measurements = {}

// --- Front page: baseline vs after, both widths --------------------------
for (const [label, base] of [['before', baselineBase], ['after', afterBase]]) {
  measurements[label] = {}
  for (const { width, height } of viewports) {
    const page = await browser.newPage({ viewport: { width, height } })
    await page.goto(`${base}/`, { waitUntil: 'networkidle', timeout: 60000 })
    await page.waitForTimeout(1200)

    await page.screenshot({ path: `${outDir}/${label}-home-${width}-viewport.png`, fullPage: false })
    await page.screenshot({ path: `${outDir}/${label}-home-${width}-full.png`, fullPage: true })

    measurements[label][`${width}px`] = await measure(page)

    if (width === 1440) {
      const readEl = await page.$('#read')
      if (readEl) {
        await readEl.screenshot({ path: `${outDir}/${label}-crop-read-${width}.png` })
      }
      const weThinkEl = await page.$('#we-think')
      if (weThinkEl) {
        await weThinkEl.screenshot({ path: `${outDir}/${label}-crop-we-think-${width}.png` })
      }
    } else {
      const readEl = await page.$('#read')
      if (readEl) {
        await readEl.screenshot({ path: `${outDir}/${label}-crop-read-${width}.png` })
      }
    }

    await page.close()
  }
}

// --- /thesis/ (after build only), both widths -----------------------------
for (const { width, height } of viewports) {
  const page = await browser.newPage({ viewport: { width, height } })
  await page.goto(`${afterBase}/thesis/`, { waitUntil: 'networkidle', timeout: 60000 })
  await page.waitForTimeout(1200)
  await page.screenshot({ path: `${outDir}/after-thesis-${width}-full.png`, fullPage: true })
  await page.close()
}

// --- Issue permalink 2026-w36, 1440, both builds (to prove no visible change)
for (const [label, base] of [['before', baselineBase], ['after', afterBase]]) {
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })
  await page.goto(`${base}/issues/2026-w36/`, { waitUntil: 'networkidle', timeout: 60000 })
  await page.waitForTimeout(1200)
  await page.screenshot({ path: `${outDir}/${label}-issue-w36-1440-full.png`, fullPage: true })
  await page.close()
}

await browser.close()

writeFileSync(`${outDir}/measurements.json`, JSON.stringify(measurements, null, 2))
console.log('Measurements written to measurements.json')
console.log('All captures complete.')
