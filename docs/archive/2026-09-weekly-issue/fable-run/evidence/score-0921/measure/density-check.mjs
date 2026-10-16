// Density check for D6: item heights and how many items of one lane fit in a single
// 1440x900 / 390x844 screen without scrolling, at various scroll offsets.
import { chromium } from '@playwright/test'
import fs from 'node:fs'
const OUT = '/mnt/mac/Users/jessepike/code/projects/sec-market/docs/active/fable-run/evidence/score-0921/measure'
const base = 'https://securitymarketpulse.com'

const browser = await chromium.launch()
const results = {}

for (const [label, width, height] of [['1440x900', 1440, 900], ['390x844', 390, 844]]) {
  const page = await browser.newPage({ viewport: { width, height } })
  await page.goto(base + '/', { waitUntil: 'networkidle', timeout: 60000 })
  await page.waitForTimeout(2000)
  const data = await page.evaluate(() => {
    const items = Array.from(document.querySelectorAll('.issue-lane__item'))
    const rects = items.map(el => {
      const r = el.getBoundingClientRect()
      return { top: Math.round(r.top + window.scrollY), height: Math.round(r.height) }
    })
    // group by lane (nearest ancestor section)
    const bySections = []
    document.querySelectorAll('section').forEach(sec => {
      const secItems = Array.from(sec.querySelectorAll('.issue-lane__item'))
      if (secItems.length) {
        const heading = sec.querySelector('h2')
        bySections.push({
          heading: heading ? heading.textContent.trim() : sec.id,
          count: secItems.length,
          heights: secItems.map(el => Math.round(el.getBoundingClientRect().height)),
        })
      }
    })
    // best window: for each possible scroll position (top of each item), count how many
    // item TOPS fall within [scrollY, scrollY+viewportHeight] i.e. fully visible items
    return { itemRects: rects, bySections }
  })
  // compute max items with tops+heights fully inside some window of `height` px
  const rects = data.itemRects.sort((a, b) => a.top - b.top)
  let maxFit = 0
  for (const r of rects) {
    const windowTop = r.top
    const windowBottom = windowTop + height
    const fit = rects.filter(x => x.top >= windowTop && (x.top + x.height) <= windowBottom).length
    if (fit > maxFit) maxFit = fit
  }
  results[label] = { maxFitInOneScreen: maxFit, bySections: data.bySections }
  console.log(label, 'maxFitInOneScreen:', maxFit)
  console.log(label, 'bySections:', JSON.stringify(data.bySections.map(s => ({ heading: s.heading, count: s.count, avgHeight: Math.round(s.heights.reduce((a,b)=>a+b,0)/s.heights.length) }))))
  await page.close()
}

fs.writeFileSync(`${OUT}/density-check.json`, JSON.stringify(results, null, 2))
await browser.close()
