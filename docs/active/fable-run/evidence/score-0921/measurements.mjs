// Measurements script for T7-7 live-site scoring.
// Records scrollHeight and element positions for the live production home page.
// Output: measurements.json with scrollHeight and bounding positions for each ID.

import { chromium } from '@playwright/test'
import { writeFileSync } from 'fs'

const prodBase = 'https://securitymarketpulse.com'

const urls = [
  { name: 'live-1440', url: prodBase, width: 1440, height: 900 },
  { name: 'live-390', url: prodBase, width: 390, height: 844 },
]

const elementIds = [
  'overview',
  'market',
  'we-think',
  'follow',
  'landscape',
  'platforms',
  'prints',
  'read',
  'hypotheses',
  'method',
  'next',
]

const measurements = {}

const browser = await chromium.launch()

for (const { name, url, width, height } of urls) {
  const page = await browser.newPage({ viewport: { width, height } })
  await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 })
  await page.waitForTimeout(2500)

  const data = await page.evaluate((ids) => {
    const scrollHeight = document.documentElement.scrollHeight
    const positions = {}

    for (const id of ids) {
      const elem = document.getElementById(id)
      if (elem) {
        const rect = elem.getBoundingClientRect()
        positions[id] = Math.round(rect.top + window.scrollY)
      } else {
        positions[id] = null
      }
    }

    return { scrollHeight, positions }
  }, elementIds)

  measurements[name] = {
    scrollHeight: data.scrollHeight,
    ...data.positions
  }

  console.log(`${name}: captured scrollHeight=${data.scrollHeight}`)
  await page.close()
}

await browser.close()

writeFileSync('measurements.json', JSON.stringify(measurements, null, 2))
console.log('Measurements written to measurements.json')
