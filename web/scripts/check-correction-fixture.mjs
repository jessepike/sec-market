// Browser verification for an isolated synthetic fixture. This never admits a
// correction or contacts a production/source URL. See visual_corrections.py.
import assert from 'node:assert/strict'
import { writeFileSync } from 'node:fs'
import { chromium } from '@playwright/test'

const [base, screenshots, output] = process.argv.slice(2)
if (!base || !screenshots || !output || new URL(base).hostname !== '127.0.0.1') throw new Error('Provide the local synthetic fixture URL, screenshot prefix and receipt path')
const browser = await chromium.launch()
const receipts = []
try {
  for (const width of [1440, 390]) {
    const page = await browser.newPage({ viewport: { width, height: 900 } })
    await page.goto(`${base}/corrections/`)
    await page.locator('#FC-20261023-checkpoint-sase details summary').click()
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth), width)
    assert.equal(await page.locator('.corrections-page__item[id^=FC-]').count(), 5)
    const links = await page.locator('.corrections-page__item[id^=FC-] a').evaluateAll(nodes => nodes.map(node => node.href))
    assert.ok(links.includes('https://www.sec.gov/Archives/edgar/data/1015922/000117891325004030/zk2534094.htm'))
    assert.ok(links.includes('https://www.sec.gov/Archives/edgar/data/1713683/000171368326000082/zs-20260415.htm'))
    await page.screenshot({ path: `${screenshots}-proof-${width}.png`, fullPage: true })
    await page.goto(`${base}/`)
    const readings = {}
    for (const [query, title] of [['Expel', 'Expel, Inc.'], ['Optiv', 'Optiv Security Inc.'], ['Check Point', 'Check Point'], ['Splunk', 'Splunk'], ['Zscaler', 'Zscaler']]) {
      await page.getByPlaceholder('Name or ticker').fill(query)
      await page.getByTitle(title, { exact: true }).first().click()
      const dialog = page.locator('.desk-dialog')
      readings[query] = await dialog.innerText()
      if (query === 'Expel') {
        assert.match(readings[query], /171\.3 million/)
        assert.doesNotMatch(readings[query], /additional \$171\.3M/)
        await page.screenshot({ path: `${screenshots}-expel-${width}.png` })
      }
      if (query === 'Optiv') {
        assert.match(readings[query], /2026-03-16/)
        assert.match(readings[query], /upon closing/i)
      }
      if (query === 'Check Point') assert.doesNotMatch(readings[query], /notes issued during Q2 2026/)
      if (query === 'Splunk') assert.doesNotMatch(readings[query], /\$1 billion.*Splunk integration/)
      if (query === 'Zscaler') {
        const transition = await dialog.locator('.desk-dialog__events li').filter({ hasText: 'Mike Rich' }).innerText()
        assert.doesNotMatch(transition, /April 16/)
      }
      await page.keyboard.press('Escape')
    }
    receipts.push({ width, groups: 5, horizontalOverflow: false, readings })
    await page.close()
  }
} finally { await browser.close() }
writeFileSync(output, JSON.stringify({ kind: 'synthetic_non_admitting_visual_replay', semanticAdmission: false, publishable: false, sourceRequests: 0, modelCalls: 0, receipts }, null, 2) + '\n')
console.log(JSON.stringify({ widths: receipts.map(receipt => receipt.width), groups: 5, semanticAdmission: false }))
