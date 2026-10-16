// Dump every evidence drawer on the front page tracker (Opus scorer, rubric v3.0).
import { chromium } from 'playwright'
import fs from 'node:fs'
const out = process.argv[2]
const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })
await page.goto('https://security-market-pulse-git-preview-pikeholdings.vercel.app/', { waitUntil: 'networkidle' })
await page.waitForTimeout(800)
const rows = []
const doms = await page.$$eval('article.tracker-domain', a => a.map(x => x.id))
for (const dom of doms) {
  const n = await page.locator(`#${dom} tbody tr`).count()
  for (let i = 0; i < n; i++) {
    const tr = page.locator(`#${dom} tbody tr`).nth(i)
    const name = await tr.locator('.tracker-row__name').innerText()
    const cells = await tr.locator('td').evaluateAll(tds => tds.map(t => ({ label: t.dataset.label, text: t.innerText.replace(/\s+/g, ' ').replace(/ src/g, '').trim() })))
    const btns = tr.locator('button.evidence-link')
    const nb = await btns.count()
    const drawers = []
    for (let j = 0; j < nb; j++) {
      const label = await btns.nth(j).getAttribute('aria-label')
      await btns.nth(j).evaluate(e => e.click()); await page.waitForTimeout(250)
      const d = await page.evaluate(() => { const d = document.querySelector('.evidence-drawer-backdrop'); return d ? { text: d.innerText.replace(/\n+/g, ' | ').slice(0, 2500), hrefs: [...d.querySelectorAll('a[href]')].map(a => a.href) } : null })
      drawers.push({ label, ...d })
      await page.keyboard.press('Escape'); await page.waitForTimeout(120)
    }
    rows.push({ dom, name, cells, drawers })
  }
}
fs.writeFileSync(`${out}/drawers.json`, JSON.stringify(rows, null, 1))
await browser.close()
console.log(rows.length)
