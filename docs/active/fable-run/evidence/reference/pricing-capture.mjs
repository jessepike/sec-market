// THROWAWAY text-extraction script for the browser-followup research task (Part B).
// Loads a public pricing/subscribe page with a real Chrome UA and Playwright's
// bundled chromium (no channel — see radar-capture.mjs for why), waits for
// network idle plus a settle period, then dumps the rendered visible text to a
// .txt file for manual reading. Does not log in, submit any form, or enter an
// email address.
//
// Usage:
//   node pricing-capture.mjs <url> <out-file>
import { chromium } from '@playwright/test'
import fs from 'node:fs'

const [, , url, outFile] = process.argv
if (!url || !outFile) {
  console.error('usage: node pricing-capture.mjs <url> <out-file>')
  process.exit(1)
}

const UA =
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'

const browser = await chromium.launch()
const page = await browser.newPage({
  viewport: { width: 1440, height: 900 },
  userAgent: UA,
})

let status = 'ok'
try {
  const resp = await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 })
  status = resp ? `HTTP ${resp.status()}` : 'no response object'
} catch (e) {
  status = `NAV ERROR: ${e.message}`
}
await page.waitForTimeout(2000)

const bodyText = await page.evaluate(() => document.body.innerText).catch(() => '(could not read body text)')
const title = await page.title().catch(() => '(no title)')
const links = await page
  .evaluate(() => {
    const out = new Set()
    for (const a of Array.from(document.querySelectorAll('a[href]'))) {
      const text = (a.textContent || '').trim().replace(/\s+/g, ' ')
      const href = a.getAttribute('href')
      if (href) out.add(`${text || '(no text)'} -> ${href}`)
    }
    return Array.from(out)
  })
  .catch(() => ['(could not read links)'])

const dump = [
  `URL: ${url}`,
  `Nav status: ${status}`,
  `Page title: ${title}`,
  '',
  '=== VISIBLE TEXT (document.body.innerText) ===',
  bodyText,
  '',
  '=== LINKS (text -> href) ===',
  ...links,
].join('\n')

fs.writeFileSync(outFile, dump, 'utf8')
console.log(`${url} -> ${outFile} (status: ${status})`)

await page.close()
await browser.close()
