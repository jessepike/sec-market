// Interaction checks: jump link, sort, row expand at 390, source reveal at 390.
import { chromium } from '/tmp/opusscore/node_modules/playwright/index.mjs'
import fs from 'fs'
const BASE = 'https://security-market-pulse-git-preview-pikeholdings.vercel.app'
const out = process.argv[2]
const browser = await chromium.launch()
const res = {}
for (const vp of [{ width: 1440, height: 900 }, { width: 390, height: 844 }]) {
  const page = await browser.newPage({ viewport: vp })
  await page.goto(BASE + '/', { waitUntil: 'networkidle' })
  // jump link
  await page.locator('a[href="#domain-identity"]').first().click()
  await page.waitForTimeout(600)
  await page.screenshot({ path: `${out}/jump-identity-${vp.width}.png` })
  const tbl = page.locator('#domain-identity table, #domain-identity').first()
  const names = async () => page.$$eval('#domain-identity .tracker-row__name', (e) => e.map((x) => x.textContent))
  const before = await names()
  // sort by Rev. growth
  const sortBtn = page.locator('#domain-identity button.tracker-table__sort', { hasText: 'Rev. growth' })
  let after = null, after2 = null
  if (await sortBtn.count()) {
    const sortVisible = await sortBtn.first().isVisible(); res['sortVisible'+vp.width]=sortVisible
    await sortBtn.first().focus(); await page.keyboard.press('Enter'); await page.waitForTimeout(200); after = await names()
    await page.keyboard.press('Enter'); await page.waitForTimeout(200); after2 = await names()
  }
  // row expand
  const toggle = page.locator('#domain-identity button.tracker-row__toggle', { hasText: 'Okta' }).first()
  await toggle.scrollIntoViewIfNeeded()
  const visBefore = await page.evaluate(() => {
    const b = [...document.querySelectorAll('#domain-identity button.tracker-row__toggle')].find((x) => x.textContent.includes('Okta'))
    const tr = b.closest('tr')
    return [...tr.querySelectorAll('td')].map((td) => ({ label: td.dataset.label, visible: getComputedStyle(td).display !== 'none' && td.getBoundingClientRect().height > 0, text: td.innerText.replace(/\s+/g, ' ').slice(0, 60) }))
  })
  await toggle.focus(); await page.keyboard.press('Enter'); await page.waitForTimeout(300)
  const visAfter = await page.evaluate(() => {
    const b = [...document.querySelectorAll('#domain-identity button.tracker-row__toggle')].find((x) => x.textContent.includes('Okta'))
    const tr = b.closest('tr')
    return { expanded: b.getAttribute('aria-expanded'), cells: [...tr.querySelectorAll('td')].map((td) => ({ label: td.dataset.label, visible: getComputedStyle(td).display !== 'none' && td.getBoundingClientRect().height > 0 })) }
  })
  await page.screenshot({ path: `${out}/okta-expanded-${vp.width}.png` })
  // open a source at this width
  const src = page.locator('#domain-identity tr', { hasText: 'Okta' }).locator('button.evidence-link').first()
  let pop = null
  if (await src.isVisible()) {
    await src.focus(); await page.keyboard.press('Enter'); await page.waitForTimeout(300)
    await page.screenshot({ path: `${out}/okta-src-${vp.width}.png` })
    pop = await page.evaluate(() => { const d = [...document.querySelectorAll('[role=dialog]')].filter((e) => e.offsetParent !== null).pop(); return d ? d.innerText.slice(0, 600) : null })
    await page.keyboard.press('Escape')
  }
  res[vp.width] = { before, after, after2, visBefore, visAfter, pop, scrollY: await page.evaluate(() => scrollY) }
  await page.close()
}
fs.writeFileSync(`${out}/interact.json`, JSON.stringify(res, null, 2))
await browser.close()
console.log(JSON.stringify(res, null, 1).slice(0, 4000))
