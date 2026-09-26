import { chromium } from 'playwright'
import fs from 'node:fs'
const BASE = process.argv[2]
const OUT = process.argv[3]
const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })
await page.goto(BASE + '/', { waitUntil: 'networkidle' })
await page.waitForTimeout(1500)
const res = {}
async function drawer(rowSel, supplier, idx) {
  const row = page.locator(`${rowSel} table tbody tr`, { hasText: supplier }).first()
  const btns = row.locator('button:has-text("src"), a:has-text("src")')
  const n = await btns.count()
  const b = btns.nth(Math.min(idx, n - 1))
  await b.scrollIntoViewIfNeeded()
  await b.click()
  await page.waitForTimeout(500)
  const t = await page.evaluate(() => { const d = document.querySelector('.evidence-drawer'); return d ? d.innerText.slice(0, 1200) + ' || ' + [...d.querySelectorAll('a')].map((a) => a.href).join(' ') : 'no drawer' })
  await page.keyboard.press('Escape'); await page.waitForTimeout(300)
  return `[${n} src] ` + t
}
res.entraGrowth = await drawer('#domain-identity', 'Microsoft Entra', 0)
res.oktaEvent = await drawer('#domain-identity', 'Okta', 9)
res.catoMetric = await drawer('#domain-network-sase', 'Cato', 0)
res.snyk = await drawer('#domain-appsec', 'Snyk', 0)
res.nozomi = await page.evaluate(() => [...document.querySelectorAll('#domain-ot-iot tbody tr')].map((r) => r.innerText.replace(/\s+/g, ' ')).join(' ## '))
// what changed: any link to report error? footer links
res.reportLinks = await page.evaluate(() => [...document.querySelectorAll('a[href^="mailto:"]')].map((a) => a.textContent.trim() + ' ' + a.getAttribute('href') + ' @' + Math.round(a.getBoundingClientRect().top + scrollY)))
res.footer = await page.evaluate(() => (document.querySelector('body > footer, footer.site-footer, footer:last-of-type')?.innerText || '').slice(0, 1500))
res.nextSection = await page.evaluate(() => (document.querySelector('#next')?.innerText || '').slice(0, 2500))
res.coverageNav = await page.evaluate(() => (document.querySelector('#tracker-coverage')?.innerText || '').slice(0, 300))
fs.writeFileSync(`${OUT}/probe3.json`, JSON.stringify(res, null, 1))
await browser.close()
