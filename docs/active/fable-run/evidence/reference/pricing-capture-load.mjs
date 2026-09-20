// THROWAWAY variant of pricing-capture.mjs for pages whose trackers/ads never
// let networkidle fire. Waits for "load" instead, then a longer settle period
// (networkidle would time out and the page never captures otherwise). Same
// rules apply: no login, no form submission, no email entry, no CAPTCHA solving.
//
// Usage:
//   node pricing-capture-load.mjs <url> <out-file>
import { chromium } from '@playwright/test'
import fs from 'node:fs'

const [, , url, outFile] = process.argv
if (!url || !outFile) {
  console.error('usage: node pricing-capture-load.mjs <url> <out-file>')
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
  const resp = await page.goto(url, { waitUntil: 'load', timeout: 60000 })
  status = resp ? `HTTP ${resp.status()}` : 'no response object'
} catch (e) {
  status = `NAV ERROR: ${e.message}`
}
await page.waitForTimeout(4000)

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
