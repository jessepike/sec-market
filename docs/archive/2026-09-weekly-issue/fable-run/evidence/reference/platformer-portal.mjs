// THROWAWAY script: Platformer's pricing lives behind a Ghost "portal" overlay
// triggered by clicking Subscribe (href="#/portal/signup"), not on a static
// page. Clicking to reveal the pricing tiers is not a form submission and no
// email is entered — the script clicks only, then reads the resulting DOM
// text and closes without submitting anything.
import { chromium } from '@playwright/test'
import fs from 'node:fs'

const UA =
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'

const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, userAgent: UA })
await page.goto('https://www.platformer.news/', { waitUntil: 'networkidle', timeout: 60000 })
await page.waitForTimeout(1500)

try {
  await page.click('text=Become a paid subscriber', { timeout: 10000 })
} catch (e) {
  console.log('click by text failed, trying Subscribe link:', e.message)
  await page.click('a[href="#/portal/signup"]', { timeout: 10000 }).catch((e2) => console.log('fallback click failed too:', e2.message))
}

await page.waitForTimeout(3000)
const bodyText = await page.evaluate(() => document.body.innerText).catch(() => '(could not read body text)')
fs.writeFileSync(
  '/mnt/mac/Users/jessepike/code/projects/sec-market/docs/active/fable-run/evidence/reference/platformer-portal.txt',
  `URL: https://www.platformer.news/ (after clicking Subscribe, portal overlay)\n\n${bodyText}`,
  'utf8'
)
console.log('wrote platformer-portal.txt')

await browser.close()
