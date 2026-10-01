// Scorer interaction probe (Opus, rubric v3.0): src drawer, row expand, sort, deep links.
// Note: supplier row ids (s-*) exist in the served HTML but are gone after hydration, so rows are
// located by supplier name here.
import { chromium } from 'playwright'
import fs from 'node:fs'
const BASE = 'https://security-market-pulse-git-preview-pikeholdings.vercel.app'
const out = process.argv[2]
const browser = await chromium.launch()
const r = {}
const row = (page, dom, name) => page.locator(`#${dom} tbody tr`).filter({ has: page.locator('.tracker-row__name', { hasText: new RegExp('^' + name + '$') }) }).first()
const drawer = (page) => page.evaluate(() => { const d = document.querySelector('.evidence-drawer-backdrop'); return d ? { text: d.innerText.slice(0, 1500), hrefs: [...d.querySelectorAll('a[href]')].map(a => a.href) } : null })

for (const [w, h] of [[1440, 900], [390, 844]]) {
  const page = await browser.newPage({ viewport: { width: w, height: h } })
  await page.goto(BASE + '/', { waitUntil: 'networkidle' }); await page.waitForTimeout(1000)
  const crwd = row(page, 'domain-endpoint-xdr', 'CrowdStrike')
  r[`crwd-src-visible-${w}`] = await crwd.locator('td[data-label="Rev. growth"] button.evidence-link').isVisible()
  r[`crwd-cells-visible-${w}`] = await crwd.locator('td').evaluateAll(tds => tds.map(t => t.dataset.label + ':' + (t.getBoundingClientRect().height > 0 && getComputedStyle(t).display !== 'none')))
  const y = await crwd.evaluate(e => e.getBoundingClientRect().top + scrollY - 120)
  await page.evaluate((y) => scrollTo(0, y), y); await page.waitForTimeout(200)
  await page.screenshot({ path: `${out}/table-first-${w}.png` })
  await crwd.locator('button.tracker-row__toggle').evaluate(e => e.click()); await page.waitForTimeout(500)
  r[`crwd-expanded-${w}`] = await crwd.evaluate(tr => ({ cls: tr.className, text: tr.innerText, cells: [...tr.cells].map(t => t.dataset.label + ':' + (t.getBoundingClientRect().height > 0 && getComputedStyle(t).display !== 'none')) }))
  await page.screenshot({ path: `${out}/row-expanded-${w}.png` })
  const before = await page.$$eval('#domain-network-sase tbody tr', t => t.map(x => x.querySelector('.tracker-row__name').innerText))
  await page.locator('#domain-network-sase th button', { hasText: 'Rev. growth' }).evaluate(e => e.click()); await page.waitForTimeout(300)
  const after1 = await page.$$eval('#domain-network-sase tbody tr', t => t.map(x => x.querySelector('.tracker-row__name').innerText + ':' + (x.querySelector('td[data-label="Rev. growth"] .tracker-figure__value')?.innerText || '–')))
  const aria = await page.$$eval('#domain-network-sase th', t => t.map(x => x.getAttribute('aria-sort')))
  await page.locator('#domain-network-sase th button', { hasText: 'Rev. growth' }).evaluate(e => e.click()); await page.waitForTimeout(300)
  const after2 = await page.$$eval('#domain-network-sase tbody tr', t => t.map(x => x.querySelector('.tracker-row__name').innerText))
  r[`sort-${w}`] = { before, after1, aria, after2 }
  await page.close()
}
for (const hash of ['#s-snyk', '#s-zscaler', '#domain-identity']) {
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })
  await page.goto(BASE + '/' + hash, { waitUntil: 'networkidle' }); await page.waitForTimeout(1500)
  r['deeplink' + hash] = await page.evaluate((h) => { const e = document.querySelector(h); return { existsAfterHydration: !!e, top: e ? Math.round(e.getBoundingClientRect().top) : null, scrollY } }, hash)
  await page.screenshot({ path: `${out}/deeplink-${hash.slice(1)}.png` })
  await page.close()
}
{
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })
  await page.goto(BASE + '/', { waitUntil: 'networkidle' }); await page.waitForTimeout(800)
  const pops = {}
  const probes = [
    ['domain-network-sase', 'Fortinet', 'Rev. growth'], ['domain-network-sase', 'Fortinet', 'Own metric'],
    ['domain-appsec', 'Snyk', 'Ownership or last round'], ['domain-network-sase', 'Cato Networks', 'Own metric'], ['domain-network-sase', 'Cato Networks', 'Events, 12 mo.'],
    ['domain-endpoint-xdr', 'Trend Micro', 'Own metric'], ['domain-endpoint-xdr', 'Palo Alto Networks', 'Rev. growth'], ['domain-appsec', 'JFrog', 'Rev. growth'],
    ['domain-data', 'Varonis Systems', 'Prior q'], ['domain-data', 'Varonis Systems', 'Rev. growth'], ['domain-identity', 'Okta', 'Rev. growth'], ['domain-identity', 'SailPoint', 'Own metric'],
    ['domain-email', 'Abnormal Security', 'Own metric'], ['domain-identity', 'Ping Identity', 'Own metric'], ['domain-exposure', 'Axonius', 'Own metric'],
    ['domain-network-sase', 'Check Point', 'Rev. growth'], ['domain-network-sase', 'Cloudflare', 'Rev. growth'], ['domain-network-sase', 'Netskope', 'Rev. growth'], ['domain-network-sase', 'Zscaler', 'Rev. growth'],
    ['domain-endpoint-xdr', 'SentinelOne', 'Rev. growth'], ['domain-data', 'Rubrik', 'Rev. growth'], ['domain-data', 'Commvault Systems', 'Rev. growth'], ['domain-exposure', 'Rapid7', 'Rev. growth'],
    ['domain-exposure', 'Tenable', 'Rev. growth'], ['domain-exposure', 'Qualys', 'Rev. growth'], ['domain-identity', 'SailPoint', 'Rev. growth'], ['domain-identity', 'SailPoint', 'Prior q'],
    ['domain-secops', 'Torq', 'Events, 12 mo.'], ['domain-data', 'Cyera', 'Events, 12 mo.'], ['domain-identity', 'Delinea', 'Events, 12 mo.'], ['domain-data', 'Veeam', 'Events, 12 mo.'], ['domain-managed-security', 'Optiv Security', 'Events, 12 mo.'], ['domain-endpoint-xdr', 'Sophos', 'Events, 12 mo.'], ['domain-cloud', 'Upwind', 'Events, 12 mo.'],
    ['domain-network-sase', 'Zscaler', 'Events, 12 mo.'], ['domain-managed-security', 'Arctic Wolf Networks', 'Events, 12 mo.'], ['domain-endpoint-xdr', 'Sophos', 'Ownership or last round'], ['domain-ot-iot', 'Dragos', 'Ownership or last round'],
    ['domain-cloud', 'Wiz', 'Ownership or last round'], ['domain-ai-security', 'Zenity', 'Own metric'], ['domain-network-sase', 'Cato Networks', 'Ownership or last round'],
  ]
  for (const [dom, name, col] of probes) {
    const k = `${name} | ${col}`
    try {
      await row(page, dom, name).locator(`td[data-label="${col}"] button.evidence-link`).first().evaluate(e => e.click()); await page.waitForTimeout(350)
      pops[k] = await drawer(page)
      await page.keyboard.press('Escape'); await page.waitForTimeout(200)
    } catch (e) { pops[k] = 'ERR ' + e.message.slice(0, 120) }
  }
  r.pops = pops
  await page.close()
}
fs.writeFileSync(`${out}/interact.json`, JSON.stringify(r, null, 2))
await browser.close()
console.log('ok')
