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
    const payload = await (await page.request.get(`${base}/corrections.json`)).json()
    const role = payload.find(entry => entry.reviewScope === 'publisher_disclosure_only')
    if (role) {
      assert.equal(role.targets.length, 1)
      assert.equal(role.targets[0].targetId, 'evidence:TR-xage-1')
      assert.equal(role.targets[0].original.sourceClass, 'INDEPENDENT')
      assert.equal(role.targets[0].proposedValue.sourceClass, 'OFFICIAL')
      assert.equal(role.targets[0].original.excerpt, role.targets[0].proposedValue.excerpt)
      const roleRow = page.locator(`#${role.id}`)
      assert.match(await roleRow.innerText(), /Publisher disclosure correction/)
      assert.match(await roleRow.innerText(), /Source class: INDEPENDENT/)
      assert.match(await roleRow.innerText(), /Source class: OFFICIAL/)
      assert.doesNotMatch(await roleRow.innerText(), /Source-verified factual correction/)
      await roleRow.screenshot({ path: `${screenshots}-role-history-${width}.png`, animations: 'disabled' })
    }
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
    if (role) {
      await page.locator('#research summary').click()
      await page.getByPlaceholder('Search by title, organization, excerpt, or tag…').fill('Xage Security hits record growth')
      const library = page.locator('.evidence-library__item').filter({ hasText: 'Xage Security hits record growth' })
      assert.equal(await library.count(), 1)
      assert.equal(await library.locator('.evidence-library__class').innerText(), 'OFFICIAL')
      await library.click()
      const record = page.locator('.evidence-drawer .evidence-record').filter({ hasText: 'Xage Security hits record growth' })
      assert.equal(await record.locator('dt').filter({ hasText: 'Source class' }).locator('..').locator('dd').innerText(), 'OFFICIAL')
      assert.equal(await record.locator('blockquote').innerText(), role.targets[0].original.excerpt)
      assert.match(await record.innerText(), /Yahoo Finance/)
      assert.match(await record.innerText(), /paid press release/)
      assert.match(await record.innerText(), /does not independently verify/)
      const drawer = page.locator('.evidence-drawer')
      await drawer.evaluate(element => Promise.all(element.getAnimations().map(animation => animation.finished)))
      const box = await drawer.boundingBox()
      assert.ok(box && box.x >= 0 && box.x + box.width <= width + 1)
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth), width)
      await page.screenshot({ path: `${screenshots}-xage-${width}.png`, fullPage: false, animations: 'disabled' })
      await page.getByRole('button', { name: 'Close evidence panel' }).click()
      readings.Xage = { sourceClass: 'OFFICIAL', originalExcerptPreserved: true, scopedHistory: true }
    }
    receipts.push({ width, groups: 5 + (role ? 1 : 0), horizontalOverflow: false, readings })
    await page.close()
  }
} finally { await browser.close() }
writeFileSync(output, JSON.stringify({ kind: 'synthetic_non_admitting_visual_replay', semanticAdmission: false, publishable: false, sourceRequests: 0, modelCalls: 0, receipts }, null, 2) + '\n')
console.log(JSON.stringify({ widths: receipts.map(receipt => receipt.width), groups: receipts[0]?.groups, semanticAdmission: false }))
