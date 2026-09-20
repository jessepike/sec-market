// THROWAWAY script: open the first chart's "More actions" (...) menu on Radar's
// overview page and dump the resulting menu item text, to see exactly what
// per-chart actions the product exposes (share / embed / download / API).
// No login, no form submission, no data entry.
import { chromium } from '@playwright/test'
import fs from 'node:fs'

const UA =
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'

const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, userAgent: UA })
await page.goto('https://radar.cloudflare.com/', { waitUntil: 'networkidle', timeout: 60000 })
await page.waitForTimeout(2000)

const out = []

// Click the first "More actions..." button
const moreButtons = await page.getByRole('button', { name: /more actions/i }).all()
out.push(`found ${moreButtons.length} "more actions" buttons`)
if (moreButtons.length > 0) {
  await moreButtons[0].click()
  await page.waitForTimeout(1000)
  const menuText = await page.evaluate(() => {
    const menu = document.querySelector('[role="menu"], [role="listbox"], [data-radix-popper-content-wrapper]')
    return menu ? menu.innerText : '(no menu element found)'
  })
  out.push('=== MORE ACTIONS MENU TEXT ===')
  out.push(menuText)
  await page.screenshot({
    path: '/mnt/mac/Users/jessepike/code/projects/sec-market/docs/active/fable-run/evidence/reference/radar-more-actions-menu.png',
    fullPage: false,
  })
}

fs.writeFileSync(
  '/mnt/mac/Users/jessepike/code/projects/sec-market/docs/active/fable-run/evidence/reference/radar-menu.txt',
  out.join('\n'),
  'utf8'
)
console.log('done')

await browser.close()
