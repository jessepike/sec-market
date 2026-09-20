// THROWAWAY measurement script for T6-2 (wave 1 build evidence), following
// the pattern in docs/active/fable-run/evidence/baseline/measure/*.mjs
// (read-only reference, not modified). Run against the local preview server
// with cwd = worktree web/ so bare imports resolve from its node_modules.
import { chromium } from '@playwright/test'

const base = process.argv[2] ?? 'http://localhost:4173'
const widths = [1440, 390]
const out = {}

const browser = await chromium.launch()

for (const width of widths) {
  const page = await browser.newPage({ viewport: { width, height: 900 } })
  await page.goto(base + '/', { waitUntil: 'networkidle', timeout: 60000 })
  await page.waitForTimeout(1500)

  const measurements = await page.evaluate(() => {
    function top(id) {
      const el = document.getElementById(id)
      return el ? Math.round(el.getBoundingClientRect().top + window.scrollY) : null
    }
    // Everything above the first content element at narrow widths: the
    // header, plus anything before #overview's first child.
    const header = document.querySelector('.site-header')
    const overview = document.getElementById('overview')
    const firstContentTop = overview ? overview.getBoundingClientRect().top + window.scrollY : null
    const headerHeight = header ? header.getBoundingClientRect().height : null

    // The "signature line" inside #we-think.
    const signature = document.querySelector('#we-think .we-think__signature')
    const signatureTop = signature ? Math.round(signature.getBoundingClientRect().top + window.scrollY) : null

    return {
      marketTop: top('market'),
      followTop: top('follow'),
      readTop: top('read'),
      weThinkTop: top('we-think'),
      signatureTop,
      headerHeight,
      firstContentTop: firstContentTop !== null ? Math.round(firstContentTop) : null,
      pageHeight: document.body.scrollHeight,
    }
  })

  out[width] = measurements
  console.log(`${width}px:`, JSON.stringify(measurements))
  await page.close()
}

await browser.close()

const fs = await import('node:fs')
fs.writeFileSync(
  '/mnt/mac/Users/jessepike/code/projects/sec-market/docs/active/fable-run/evidence/wave1/measurements.json',
  JSON.stringify(out, null, 2),
)
console.log('done')
