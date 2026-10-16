import { chromium } from '@playwright/test'
const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })
await page.goto('https://security-market-pulse-git-preview-pikeholdings.vercel.app/', { waitUntil: 'networkidle', timeout: 60000 })
await page.waitForTimeout(1500)
const scriptResult = await page.addScriptTag({ url: 'https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.10.2/axe.min.js' }).then(() => 'loaded').catch(e => 'error:' + e.message)
console.log('script tag result:', scriptResult)
const check = await page.evaluate(() => {
  return { hasAxe: typeof window.axe, version: window.axe ? window.axe.version : null }
})
console.log('axe check:', JSON.stringify(check))
const full = await page.evaluate(async () => {
  const r = await window.axe.run(document, { resultTypes: ['violations', 'passes', 'incomplete', 'inapplicable'] })
  return { violations: r.violations.length, passes: r.passes.length, incomplete: r.incomplete.length, inapplicable: r.inapplicable.length }
})
console.log('full run:', JSON.stringify(full))
await browser.close()
