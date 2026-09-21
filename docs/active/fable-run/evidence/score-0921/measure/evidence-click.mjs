import { chromium } from '@playwright/test'
const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })
await page.goto('https://securitymarketpulse.com/', { waitUntil: 'networkidle', timeout: 60000 })
await page.waitForTimeout(1500)
const btn = await page.locator('button.evidence-link').first()
await btn.click()
await page.waitForTimeout(500)
const revealed = await page.evaluate(() => {
  // find any newly visible element with an href near the clicked button
  const btns = document.querySelectorAll('button.evidence-link')
  const first = btns[0]
  // search siblings/parent for a link
  let container = first.closest('li') || first.parentElement
  const links = container ? Array.from(container.querySelectorAll('a[href]')) : []
  return links.map(a => ({ href: a.href, text: a.textContent.trim().slice(0,80) }))
})
console.log(JSON.stringify(revealed, null, 2))
await browser.close()
