import { chromium } from '@playwright/test'
const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })
await page.goto('https://security-market-pulse-git-preview-pikeholdings.vercel.app/', { waitUntil: 'networkidle', timeout: 60000 })
await page.waitForTimeout(1500)
const openOnes = await page.evaluate(() => {
  return Array.from(document.querySelectorAll('details[open]')).map(d => {
    const s = d.querySelector('summary')
    return (s ? s.textContent.trim().slice(0,60) : d.className)
  })
})
console.log(JSON.stringify(openOnes, null, 2))
await browser.close()
