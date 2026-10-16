import { chromium } from '@playwright/test'
const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })
await page.goto('https://securitymarketpulse.com/', { waitUntil: 'networkidle', timeout: 60000 })
await page.waitForTimeout(1500)
await page.locator('button.evidence-link').first().click()
await page.waitForTimeout(700)
const full = await page.evaluate(() => {
  const dlg = document.querySelector('.evidence-drawer')
  return dlg ? dlg.outerHTML : null
})
console.log(full)
await browser.close()
