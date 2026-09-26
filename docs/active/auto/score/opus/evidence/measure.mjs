// Scorer measurement script. Run in the OrbStack dev VM from ~/opus-score-tools.
import { chromium } from 'playwright'
import fs from 'node:fs'
import { createRequire } from 'node:module'
const require = createRequire(import.meta.url)
const axeSrc = fs.readFileSync(require.resolve('axe-core/axe.min.js'), 'utf8')

const BASE = process.argv[2]
const OUT = process.argv[3]
fs.mkdirSync(OUT, { recursive: true })
const browser = await chromium.launch()
const results = {}

async function measure(path, vp, tag, shots) {
  const page = await browser.newPage({ viewport: vp })
  await page.goto(BASE + path, { waitUntil: 'networkidle', timeout: 60000 })
  await page.waitForTimeout(2500)
  const r = {}
  if (shots) {
    await page.screenshot({ path: `${OUT}/${tag}-fold.png` })
    await page.screenshot({ path: `${OUT}/${tag}-full.png`, fullPage: true })
  }
  r.metrics = await page.evaluate(() => {
    const vh = innerHeight
    const de = document.documentElement
    const main = document.querySelector('main')
    const firstContent = main ? main.firstElementChild : null
    const rect = (el) => { const b = el.getBoundingClientRect(); return { top: Math.round(b.top + scrollY), h: Math.round(b.height), w: Math.round(b.width) } }
    // first-screen visible text
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT)
    const fold = []
    let minBody = 99, smallTexts = []
    const sizes = new Set()
    while (walker.nextNode()) {
      const n = walker.currentNode
      const t = n.textContent.trim()
      if (!t) continue
      const el = n.parentElement
      const cs = getComputedStyle(el)
      if (cs.visibility === 'hidden' || cs.display === 'none') continue
      const b = el.getBoundingClientRect()
      if (b.width === 0 || b.height === 0) continue
      const fs = parseFloat(cs.fontSize)
      sizes.add(fs)
      if (b.top + scrollY < vh) fold.push(t)
      if (t.length > 40 && fs < 14) smallTexts.push({ fs, t: t.slice(0, 60) })
    }
    // tap targets
    const small = []
    document.querySelectorAll('a, button, summary, input, select, [role=button], th[aria-sort] button').forEach((el) => {
      const b = el.getBoundingClientRect()
      if (b.width === 0 || b.height === 0) return
      if (getComputedStyle(el).visibility === 'hidden') return
      if (b.width < 24 || b.height < 24) small.push({ tag: el.tagName, t: (el.textContent || el.getAttribute('aria-label') || '').trim().slice(0, 30), w: Math.round(b.width), h: Math.round(b.height) })
    })
    // sections
    const secs = [...document.querySelectorAll('main section, main > div > section, main [id]')].map((s) => ({ id: s.id, cls: s.className, h2: (s.querySelector('h2,h3')?.textContent || '').trim().slice(0, 60), ...rect(s), visible: s.getBoundingClientRect().height > 0 }))
    const headings = [...document.querySelectorAll('h1,h2,h3')].map((h) => ({ tag: h.tagName, t: h.textContent.trim().slice(0, 70), top: Math.round(h.getBoundingClientRect().top + scrollY), visible: h.getBoundingClientRect().height > 0 }))
    const details = [...document.querySelectorAll('details')].map((d) => ({ open: d.open, summary: (d.querySelector('summary')?.textContent || '').trim().slice(0, 60), top: Math.round(d.getBoundingClientRect().top + scrollY) }))
    const tables = [...document.querySelectorAll('table')].map((t) => ({ cap: (t.caption?.textContent || '').trim().slice(0, 60), rows: t.tBodies[0]?.rows.length, ...rect(t), fontVariant: getComputedStyle(t).fontVariantNumeric }))
    const header = document.querySelector('header')
    return {
      scrollWidth: de.scrollWidth, clientWidth: de.clientWidth, pageHeight: de.scrollHeight,
      chromeTop: firstContent ? Math.round(firstContent.getBoundingClientRect().top + scrollY) : null,
      mainTop: main ? Math.round(main.getBoundingClientRect().top + scrollY) : null,
      headerH: header ? Math.round(header.getBoundingClientRect().height) : null,
      foldText: fold.join(' | ').slice(0, 3000),
      fontSizes: [...sizes].sort((a, b) => a - b), smallTexts: smallTexts.slice(0, 15), smallTargets: small.slice(0, 40), smallTargetCount: small.length,
      headings, details, tables, bodyFont: getComputedStyle(document.body).fontFamily, bodySize: getComputedStyle(document.body).fontSize,
    }
  })
  // axe
  await page.addScriptTag({ content: axeSrc })
  const axe = await page.evaluate(async () => {
    const r = await window.axe.run(document, { runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa', 'best-practice'] } })
    return r.violations.map((v) => ({ id: v.id, impact: v.impact, n: v.nodes.length, sample: v.nodes.slice(0, 3).map((n) => n.target.join(' ') + ' :: ' + (n.failureSummary || '').slice(0, 160)) }))
  })
  r.axe = axe
  // keyboard: first 25 tab stops
  if (shots) {
    await page.goto(BASE + path, { waitUntil: 'networkidle' })
    const stops = []
    for (let i = 0; i < 25; i++) {
      await page.keyboard.press('Tab')
      stops.push(await page.evaluate(() => {
        const a = document.activeElement
        if (!a) return null
        const cs = getComputedStyle(a)
        return { tag: a.tagName, t: (a.textContent || a.getAttribute('aria-label') || '').trim().slice(0, 40), href: a.getAttribute('href'), outline: cs.outlineStyle + ' ' + cs.outlineWidth + ' ' + cs.outlineColor, boxShadow: cs.boxShadow.slice(0, 40) }
      }))
    }
    r.tabStops = stops
    if (shots) await page.screenshot({ path: `${OUT}/${tag}-focus.png` })
  }
  await page.close()
  return r
}

for (const [tag, vp] of [['home-1440', { width: 1440, height: 900 }], ['home-390', { width: 390, height: 844 }], ['home-320', { width: 320, height: 800 }]]) {
  results[tag] = await measure('/', vp, tag, true)
}
for (const [tag, vp] of [['corr-1440', { width: 1440, height: 900 }], ['corr-390', { width: 390, height: 844 }]]) {
  results[tag] = await measure('/corrections/', vp, tag, true)
}
fs.writeFileSync(`${OUT}/measure.json`, JSON.stringify(results, null, 1))
await browser.close()
console.log('done')
