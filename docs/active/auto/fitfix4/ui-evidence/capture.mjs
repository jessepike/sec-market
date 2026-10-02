// Fix pass 4 evidence capture — adapted from docs/active/auto/score3/opus/evidence/capture.mjs.
// Run in the OrbStack dev VM against a local production build (vite preview on :4173).
// node capture.mjs <outdir> <label>
import { chromium } from 'playwright'
import fs from 'node:fs'
import { createRequire } from 'node:module'
const require = createRequire(import.meta.url)
const axeSrc = fs.readFileSync(require.resolve('axe-core/axe.min.js'), 'utf8')

const BASE = process.env.CAPTURE_BASE || 'http://localhost:4173'
const out = process.argv[2]
const label = process.argv[3] || 'capture'
fs.mkdirSync(out, { recursive: true })
const browser = await chromium.launch()
const result = {}

async function open(path, w, h) {
  const page = await browser.newPage({ viewport: { width: w, height: h } })
  await page.goto(BASE + path, { waitUntil: 'networkidle', timeout: 60000 })
  await page.waitForTimeout(1200)
  return page
}

for (const [w, h] of [[1440, 900], [390, 844], [320, 800]]) {
  const page = await open('/', w, h)
  const tag = `${label}-home-${w}`
  await page.screenshot({ path: `${out}/${tag}-fold.png` })
  await page.screenshot({ path: `${out}/${tag}-full.png`, fullPage: true })
  const m = await page.evaluate(() => {
    const de = document.documentElement
    const main = document.querySelector('main') || document.body
    let first = null
    for (const el of main.querySelectorAll('*')) {
      const r = el.getBoundingClientRect()
      if (r.height > 0 && el.children.length === 0 && el.textContent.trim()) { first = el; break }
    }
    const firstTop = first ? first.getBoundingClientRect().top + scrollY : null
    // Supplier-row probe: top of the first tracker row in the first domain table.
    const firstRow = document.querySelector('#market .tracker-table tbody tr')
    const firstRowTop = firstRow ? firstRow.getBoundingClientRect().top + scrollY : null
    const runStatusLine = document.querySelector('.run-status__line')
    const runStatusBottom = runStatusLine ? runStatusLine.getBoundingClientRect().bottom + scrollY : null
    const small = []
    const targets = []
    for (const el of document.querySelectorAll('a,button,summary,input,select,[role=button],[tabindex]')) {
      const r = el.getBoundingClientRect()
      if (r.width === 0 && r.height === 0) continue
      const cs = getComputedStyle(el)
      if (cs.visibility === 'hidden' || cs.display === 'none') continue
      if (r.width < 24 || r.height < 24) targets.push({ tag: el.tagName, cls: el.className, text: el.textContent.trim().slice(0, 50), w: Math.round(r.width), h: Math.round(r.height) })
    }
    const sizes = {}
    const fams = {}
    for (const el of document.querySelectorAll('body *')) {
      if (!el.childNodes.length) continue
      const hasText = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())
      if (!hasText) continue
      const r = el.getBoundingClientRect(); if (!r.height) continue
      const cs = getComputedStyle(el)
      sizes[cs.fontSize] = (sizes[cs.fontSize] || 0) + 1
      fams[cs.fontFamily.split(',')[0]] = (fams[cs.fontFamily.split(',')[0]] || 0) + 1
      if (parseFloat(cs.fontSize) < 12 && el.textContent.trim().length > 20) small.push({ fs: cs.fontSize, t: el.textContent.trim().slice(0, 80) })
    }
    const ids = [...document.querySelectorAll('[id]')].map(e => e.id)
    const dup = ids.filter((x, i) => ids.indexOf(x) !== i)
    const emptyH = [...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].filter(h => !h.textContent.trim()).length
    return {
      scrollW: de.scrollWidth, clientW: de.clientWidth, height: de.scrollHeight,
      firstContent: first ? { tag: first.tagName, text: first.textContent.trim().slice(0, 80), top: firstTop } : null,
      firstRowTop, runStatusBottom,
      smallTargets: targets, fontSizes: sizes, fontFamilies: fams, smallLongText: small.slice(0, 20),
      dupIds: [...new Set(dup)], emptyHeadings: emptyH,
      times: document.querySelectorAll('time[datetime]').length,
      tableDates: document.querySelectorAll('.tracker-figure__period').length,
      tableDatesAsTime: document.querySelectorAll('.tracker-table time[datetime]').length,
    }
  })
  result[tag] = m
  if (w !== 320) {
    await page.addScriptTag({ content: axeSrc })
    const ax = await page.evaluate(async () => {
      const r = await axe.run(document, { runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'] } })
      return r.violations.map(v => ({ id: v.id, impact: v.impact, n: v.nodes.length, sample: v.nodes.slice(0, 3).map(n => n.target.join(' ') + ' :: ' + (n.failureSummary || '').slice(0, 200)) }))
    })
    result[`axe-${label}-home-${w}`] = ax
  }
  if (w !== 320) {
    const stops = []
    await page.evaluate(() => window.scrollTo(0, 0))
    for (let i = 0; i < 40; i++) {
      await page.keyboard.press('Tab')
      stops.push(await page.evaluate(() => {
        const e = document.activeElement
        const r = e.getBoundingClientRect()
        return { tag: e.tagName, text: (e.textContent || '').trim().slice(0, 50), x: Math.round(r.x), y: Math.round(r.y), visible: r.width > 0 && r.height > 0, inHiddenThead: !!e.closest('thead') && getComputedStyle(e.closest('thead')).display === 'none' }
      }))
    }
    result[`kbd-${label}-home-${w}`] = stops.map((s, i) => ({ ...s, i: i + 1 }))
  }
  await page.close()
}

for (const [w, h] of [[1440, 900], [390, 844]]) {
  const page = await open('/corrections/', w, h)
  await page.screenshot({ path: `${out}/${label}-corrections-${w}-full.png`, fullPage: true })
  await page.addScriptTag({ content: axeSrc })
  result[`axe-${label}-corrections-${w}`] = await page.evaluate(async () => {
    const r = await axe.run(document, { runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'] } })
    return r.violations.map(v => ({ id: v.id, impact: v.impact, n: v.nodes.length, sample: v.nodes.slice(0, 3).map(n => n.target.join(' ')) }))
  })
  await page.close()
}

fs.writeFileSync(`${out}/${label}-capture.json`, JSON.stringify(result, null, 2))
await browser.close()
console.log('done:', label)
