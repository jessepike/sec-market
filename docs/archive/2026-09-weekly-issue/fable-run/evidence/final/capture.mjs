// Adapted capture script for T6-15 fable-run final evidence collection.
// Captures screenshots at 1440x900 and 390x844 viewports for:
// - preview home, corrections page, and issue 2026-w36
// - both full-page and viewport-only screenshots
// - special captures: #market element and first CORRECTED item at 1440
// Also collects measurements for measurements.json
// Files saved to docs/archive/2026-09-weekly-issue/fable-run/evidence/final/

import { chromium } from '@playwright/test'
import { writeFileSync } from 'fs'
import { resolve } from 'path'

const previewBase = 'https://security-market-pulse-git-preview-pikeholdings.vercel.app'

const pages = [
  { path: '/', filePrefix: 'final-home' },
  { path: '/corrections/', filePrefix: 'final-corrections' },
  { path: '/issues/2026-w36/', filePrefix: 'final-issue-w36' },
]

const viewports = [
  { width: 1440, height: 900 },
  { width: 390, height: 844 },
]

const browser = await chromium.launch()
const measurements = {}

for (const { path, filePrefix } of pages) {
  const url = `${previewBase}${path}`

  for (const { width, height } of viewports) {
    const page = await browser.newPage({ viewport: { width, height } })
    await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 })
    // Charts load through a dynamic import after mount; give them time to paint.
    await page.waitForTimeout(2500)

    // Viewport-only screenshot
    const viewportOut = `${filePrefix}-${width}-viewport.png`
    await page.screenshot({ path: viewportOut, fullPage: false })
    console.log(`${url} @ ${width}px -> ${viewportOut} (viewport)`)

    // Full-page screenshot
    const fullOut = `${filePrefix}-${width}-full.png`
    await page.screenshot({ path: fullOut, fullPage: true })
    console.log(`${url} @ ${width}px -> ${fullOut} (full page)`)

    // Collect measurements from home page
    if (path === '/') {
      const measurement = await page.evaluate(() => {
        const pageHeight = document.documentElement.scrollHeight
        const result = { pageHeight }

        // Measure each section
        const ids = ['overview', 'market', 'we-think', 'follow', 'landscape', 'platforms', 'prints', 'read', 'hypotheses', 'method', 'next']
        for (const id of ids) {
          const el = document.getElementById(id)
          if (el) {
            const rect = el.getBoundingClientRect()
            result[id] = Math.round(rect.top + window.scrollY)
          } else {
            result[id] = null
          }
        }

        // Also measure market bottom
        const marketEl = document.getElementById('market')
        if (marketEl) {
          const rect = marketEl.getBoundingClientRect()
          result['market-bottom'] = Math.round(rect.bottom + window.scrollY)
        }

        return result
      })

      measurements[`${width}px`] = measurement
    }

    // Special captures at 1440 for home page
    if (path === '/' && width === 1440) {
      // Capture #market element clipped
      const marketElement = await page.$('#market')
      if (marketElement) {
        const marketOut = 'final-market-1440.png'
        await marketElement.screenshot({ path: marketOut })
        console.log(`${url} -> ${marketOut} (#market element)`)
      }

      // Capture first element containing "CORRECTED"
      // Try to find and screenshot it, skip if not found
      try {
        const correctedElement = await page.locator(':has-text("CORRECTED")').first()
        if (await correctedElement.count() > 0) {
          // Walk up to find a meaningful container
          const correctedOut = 'final-corrected-item-1440.png'
          await correctedElement.screenshot({ path: correctedOut })
          console.log(`${url} -> ${correctedOut} (first CORRECTED item)`)
        } else {
          console.log(`${url} -> final-corrected-item-1440.png (skipped: no CORRECTED text found)`)
        }
      } catch (e) {
        console.log(`${url} -> final-corrected-item-1440.png (skipped: ${e.message})`)
      }
    }

    await page.close()
  }
}

await browser.close()

// Write measurements to JSON
writeFileSync('measurements.json', JSON.stringify(measurements, null, 2))
console.log('Measurements saved to measurements.json')
console.log('All captures complete.')
