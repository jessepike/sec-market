// THROWAWAY capture + DOM-extraction script for the browser-followup research task.
// Mirrors docs/archive/2026-09-weekly-issue/fable-run/evidence/baseline/capture.mjs (chromium.launch(), no
// channel, since only Playwright's own chromium build exists in the OrbStack dev VM).
// Additionally dumps visible text and specific DOM signals (chart action labels,
// "last updated" / licence lines) to a sibling .txt file for manual reading.
//
// Usage:
//   node radar-capture.mjs <url> <out-prefix>
import { chromium } from '@playwright/test'
import fs from 'node:fs'

const [, , url, prefix] = process.argv
if (!url || !prefix) {
  console.error('usage: node radar-capture.mjs <url> <out-prefix>')
  process.exit(1)
}

const UA =
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'

const configs = [
  { width: 1440, height: 900 },
  { width: 390, height: 844 },
]

const browser = await chromium.launch()

for (const { width, height } of configs) {
  const page = await browser.newPage({
    viewport: { width, height },
    userAgent: UA,
  })
  await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 })
  await page.waitForTimeout(2000)

  const viewportOut = `${prefix}-${width}-viewport.png`
  await page.screenshot({ path: viewportOut, fullPage: false })
  console.log(`${url} @ ${width}px -> ${viewportOut} (first viewport, ${width}x${height})`)

  if (width === 1440) {
    const fullOut = `${prefix}-${width}-full.png`
    await page.screenshot({ path: fullOut, fullPage: true })
    console.log(`${url} @ ${width}px -> ${fullOut} (full page)`)

    // Extract DOM signals for manual reading: visible text, button/aria-label
    // text (per-chart action menus), and anything mentioning "updated" or a
    // licence/attribution string.
    const bodyText = await page.evaluate(() => document.body.innerText)

    const actionLabels = await page.evaluate(() => {
      const nodes = Array.from(
        document.querySelectorAll('button, a[role="button"], [aria-label], [title]')
      )
      const out = new Set()
      for (const n of nodes) {
        const label = n.getAttribute('aria-label') || n.getAttribute('title') || n.textContent
        const trimmed = (label || '').trim().replace(/\s+/g, ' ')
        if (trimmed && trimmed.length < 80) out.add(trimmed)
      }
      return Array.from(out)
    })

    const updatedLines = bodyText
      .split('\n')
      .map((l) => l.trim())
      .filter(
        (l) =>
          l &&
          /updated|last refresh|licen[cs]e|source:|data source|attribution|©/i.test(l)
      )

    const dump = [
      `URL: ${url}`,
      '',
      '=== VISIBLE TEXT (document.body.innerText) ===',
      bodyText,
      '',
      '=== BUTTON / ARIA-LABEL / TITLE STRINGS ===',
      ...actionLabels,
      '',
      '=== LINES MENTIONING updated/license/source/attribution ===',
      ...updatedLines,
    ].join('\n')

    fs.writeFileSync(`${prefix}-dom.txt`, dump, 'utf8')
    console.log(`${url} -> ${prefix}-dom.txt (DOM text dump)`)
  }

  await page.close()
}

await browser.close()
