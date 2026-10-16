import { chromium } from '@playwright/test'
const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })
await page.goto('https://securitymarketpulse.com/', { waitUntil: 'networkidle', timeout: 60000 })
await page.waitForTimeout(1500)
const before = await page.evaluate(() => document.querySelectorAll('a[href]').length)
await page.locator('button.evidence-link').first().click()
await page.waitForTimeout(700)
const after = await page.evaluate(() => document.querySelectorAll('a[href]').length)
const dialog = await page.evaluate(() => {
  const dlg = document.querySelector('[role="dialog"], dialog, .evidence-panel, .evidence-modal, [aria-modal="true"]')
  if (!dlg) return null
  return { tag: dlg.tagName, className: dlg.className, html: dlg.outerHTML.slice(0, 2000) }
})
console.log('before links:', before, 'after links:', after)
console.log('dialog:', JSON.stringify(dialog, null, 2))
await browser.close()
