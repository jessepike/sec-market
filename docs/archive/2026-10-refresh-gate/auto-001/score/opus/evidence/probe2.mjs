import { chromium } from 'playwright'
import fs from 'node:fs'
import { createRequire } from 'node:module'
const require = createRequire(import.meta.url)
const axeSrc = fs.readFileSync(require.resolve('axe-core/axe.min.js'), 'utf8')
const BASE = process.argv[2]
const OUT = process.argv[3]
const browser = await chromium.launch()
const res = {}
// 1440: click first src button in the table, and the landscape card button
{
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })
  await page.goto(BASE + '/', { waitUntil: 'networkidle' })
  await page.waitForTimeout(2000)
  await page.addScriptTag({ content: axeSrc })
  res.axeCheck = await page.evaluate(async () => { const r = await window.axe.run(document); return { v: r.violations.map((x) => [x.id, x.impact, x.nodes.length]), passes: r.passes.length, incomplete: r.incomplete.map((x) => [x.id, x.nodes.length]) } })
  const btn = page.locator('#domain-endpoint-xdr table tbody tr').first().locator('button:has-text("src")').first()
  await btn.scrollIntoViewIfNeeded()
  const y0 = await page.evaluate(() => scrollY)
  await btn.click()
  await page.waitForTimeout(600)
  res.srcPopover1440 = await page.evaluate(() => {
    const d = document.querySelector('[role=dialog], .evidence-popover, .src-popover, [data-state=open], dialog[open]')
    return d ? { cls: d.className, txt: d.textContent.trim().slice(0, 800), hrefs: [...d.querySelectorAll('a')].map((a) => a.href) } : null
  })
  res.scrollAfterClick = [y0, await page.evaluate(() => scrollY)]
  await page.screenshot({ path: `${OUT}/src-popover-1440.png` })
  await page.keyboard.press('Escape')
  // row expand at 1440 (the + chevron)
  const row = page.locator('#domain-network-sase table tbody tr').nth(3)
  await row.locator('button').first().click()
  await page.waitForTimeout(500)
  await row.scrollIntoViewIfNeeded()
  await page.screenshot({ path: `${OUT}/row-expand-1440.png` })
  res.expanded1440 = await page.evaluate(() => { const e = document.querySelector('#domain-network-sase tr[aria-expanded=true], #domain-network-sase .tracker-row--open, #domain-network-sase [data-open=true]'); const all = document.querySelector('#domain-network-sase'); return all.innerText.slice(0, 3000) })
  // landscape card button
  const lbtn = page.locator('#landscape button').first()
  await lbtn.scrollIntoViewIfNeeded()
  await lbtn.click()
  await page.waitForTimeout(600)
  res.landscapePopover = await page.evaluate(() => { const d = document.querySelector('[role=dialog], dialog[open]'); return d ? d.innerText.slice(0, 2000) + ' || ' + [...d.querySelectorAll('a')].map((a) => a.href).join(' ') : document.activeElement.outerHTML.slice(0, 300) })
  await page.screenshot({ path: `${OUT}/landscape-popover-1440.png` })
  await page.keyboard.press('Escape')
  // sort by Rev. growth
  const sb = page.locator('#domain-network-sase th button:has-text("Rev. growth")')
  await sb.scrollIntoViewIfNeeded(); await sb.click(); await page.waitForTimeout(400)
  res.sorted = await page.evaluate(() => [...document.querySelectorAll('#domain-network-sase table tbody tr')].map((r) => r.cells[0]?.innerText.split('\n')[0]).join(', '))
  await page.close()
}
// 390: horizontal scroll check, row expand
{
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } })
  await page.goto(BASE + '/', { waitUntil: 'networkidle' })
  await page.waitForTimeout(2000)
  res.hscroll390 = await page.evaluate(() => { window.scrollTo(300, 0); return { x: scrollX, htmlOx: getComputedStyle(document.documentElement).overflowX, bodyOx: getComputedStyle(document.body).overflowX, sw: document.documentElement.scrollWidth } })
  await page.screenshot({ path: `${OUT}/hscroll-390.png` })
  await page.evaluate(() => window.scrollTo(0, 0))
  const row = page.locator('#domain-network-sase table tbody tr').nth(3)
  await row.scrollIntoViewIfNeeded()
  const bx = await row.locator('button').first().boundingBox()
  await row.locator('button').first().click()
  await page.waitForTimeout(500)
  await page.screenshot({ path: `${OUT}/row-expand-390.png` })
  res.rowBtn390 = bx
  res.expanded390 = await page.evaluate(() => document.querySelector('#domain-network-sase').innerText.slice(0, 1500))
  await page.close()
}
{
  const page = await browser.newPage({ viewport: { width: 320, height: 800 } })
  await page.goto(BASE + '/', { waitUntil: 'networkidle' })
  await page.waitForTimeout(1500)
  res.hscroll320 = await page.evaluate(() => { window.scrollTo(300, 0); return { x: scrollX, sw: document.documentElement.scrollWidth } })
  await page.close()
}
fs.writeFileSync(`${OUT}/probe2.json`, JSON.stringify(res, null, 1))
await browser.close()
