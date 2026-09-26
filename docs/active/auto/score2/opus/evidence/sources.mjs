// Click every evidence "src" control on the front page and record what it reveals.
import { chromium } from '/tmp/opusscore/node_modules/playwright/index.mjs'
import fs from 'fs'
const BASE = 'https://security-market-pulse-git-preview-pikeholdings.vercel.app'
const out = process.argv[2]
const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })
await page.goto(BASE + '/', { waitUntil: 'networkidle' })
await page.waitForTimeout(1000)
const n = await page.locator('button.evidence-link').count()
const rows = []
for (let i = 0; i < n; i++) {
  const b = page.locator('button.evidence-link').nth(i)
  const label = await b.getAttribute('aria-label')
  const ctx = await b.evaluate((el) => {
    const tr = el.closest('tr'); const li = el.closest('li')
    const sec = el.closest('section')
    return {
      supplier: tr ? (tr.querySelector('.tracker-row__name')?.textContent || '') : '',
      cell: (el.closest('td,li,p,div')?.innerText || '').replace(/\s+/g, ' ').slice(0, 200),
      section: sec ? (sec.querySelector('h2,h3')?.textContent || '') : '',
    }
  })
  await b.scrollIntoViewIfNeeded()
  await b.click()
  await page.waitForTimeout(150)
  const pop = await page.evaluate(() => {
    const cands = [...document.querySelectorAll('[role=dialog],[role=tooltip],.evidence-popover,[class*=popover],[class*=evidence-card],[class*=evidence__panel]')]
      .filter((e) => e.offsetParent !== null)
    const e = cands[cands.length - 1]
    if (!e) return null
    return { text: e.innerText.replace(/\s+/g, ' ').slice(0, 400), hrefs: [...e.querySelectorAll('a')].map((a) => a.href) }
  })
  rows.push({ i, label, ...ctx, pop })
  await page.keyboard.press('Escape')
  await page.waitForTimeout(50)
}
fs.writeFileSync(`${out}/sources.json`, JSON.stringify(rows, null, 2))
// expand one row to see the row detail
const t = page.locator('button.tracker-row__toggle').first()
await t.click()
await page.waitForTimeout(300)
const detail = await page.evaluate(() => {
  const tr = document.querySelector('button.tracker-row__toggle[aria-expanded=true]')?.closest('tr')
  const nx = tr?.nextElementSibling
  return { row: tr?.innerText, next: nx?.innerText, nextHtml: nx?.outerHTML?.slice(0, 3000) }
})
fs.writeFileSync(`${out}/row-expand.json`, JSON.stringify(detail, null, 2))
await page.screenshot({ path: `${out}/home-1440-rowexpanded.png` })
console.log(n, 'buttons')
await browser.close()
