// Scorer capture script (Opus, rubric v3.0). Run in the OrbStack dev VM from /tmp/opus-score.
// node capture.mjs <outdir>
import { chromium } from 'playwright'
import fs from 'node:fs'
import { createRequire } from 'node:module'
const require = createRequire(import.meta.url)
const axeSrc = fs.readFileSync(require.resolve('axe-core/axe.min.js'), 'utf8')

const BASE = 'https://security-market-pulse-git-preview-pikeholdings.vercel.app'
const out = process.argv[2]
fs.mkdirSync(out, { recursive: true })
const browser = await chromium.launch()
const result = {}

async function open(path, w, h) {
  const page = await browser.newPage({ viewport: { width: w, height: h } })
  await page.goto(BASE + path, { waitUntil: 'networkidle', timeout: 60000 })
  await page.waitForTimeout(1500)
  return page
}

for (const [w, h] of [[1440, 900], [390, 844], [320, 800]]) {
  const page = await open('/', w, h)
  const tag = `home-${w}`
  await page.screenshot({ path: `${out}/${tag}-fold.png` })
  await page.screenshot({ path: `${out}/${tag}-full.png`, fullPage: true })
  const m = await page.evaluate(() => {
    const de = document.documentElement
    const main = document.querySelector('main') || document.body
    // first content element: first descendant of main with visible text
    let first = null
    for (const el of main.querySelectorAll('*')) {
      const r = el.getBoundingClientRect()
      if (r.height > 0 && el.children.length === 0 && el.textContent.trim()) { first = el; break }
    }
    const firstTop = first ? first.getBoundingClientRect().top + scrollY : null
    const small = []
    const targets = []
    for (const el of document.querySelectorAll('a,button,summary,input,select,[role=button],[tabindex]')) {
      const r = el.getBoundingClientRect()
      if (r.width === 0 && r.height === 0) continue
      const cs = getComputedStyle(el)
      if (cs.visibility === 'hidden' || cs.display === 'none') continue
      if (r.width < 24 || r.height < 24) targets.push({ tag: el.tagName, text: el.textContent.trim().slice(0, 50), w: Math.round(r.width), h: Math.round(r.height), inline: cs.display === 'inline' })
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
      if (parseFloat(cs.fontSize) < 13 && el.textContent.trim().length > 60) small.push({ fs: cs.fontSize, t: el.textContent.trim().slice(0, 80) })
    }
    const ids = [...document.querySelectorAll('[id]')].map(e => e.id)
    const dup = ids.filter((x, i) => ids.indexOf(x) !== i)
    const emptyH = [...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].filter(h => !h.textContent.trim()).length
    return {
      scrollW: de.scrollWidth, clientW: de.clientWidth, height: de.scrollHeight,
      firstContent: first ? { tag: first.tagName, text: first.textContent.trim().slice(0, 80), top: firstTop } : null,
      smallTargets: targets, fontSizes: sizes, fontFamilies: fams, smallLongText: small.slice(0, 20),
      dupIds: [...new Set(dup)], emptyHeadings: emptyH,
      headings: [...document.querySelectorAll('h1,h2,h3')].map(h => ({ l: h.tagName, t: h.textContent.trim().slice(0, 90), top: Math.round(h.getBoundingClientRect().top + scrollY), id: h.id || h.closest('[id]')?.id })),
      details: document.querySelectorAll('details').length, detailsOpen: document.querySelectorAll('details[open]').length,
      times: document.querySelectorAll('time[datetime]').length,
      landmarks: [...document.querySelectorAll('header,nav,main,footer,aside,[role]')].map(e => e.tagName + (e.getAttribute('role') ? '[' + e.getAttribute('role') + ']' : '')),
      tables: [...document.querySelectorAll('table')].map(t => ({ id: t.id || t.closest('[id]')?.id, rows: t.tBodies[0]?.rows.length, top: Math.round(t.getBoundingClientRect().top + scrollY), h: Math.round(t.getBoundingClientRect().height) })),
    }
  })
  result[tag] = m
  fs.writeFileSync(`${out}/${tag}-text.txt`, await page.evaluate(() => document.body.innerText))
  if (w !== 320) {
    await page.addScriptTag({ content: axeSrc })
    const ax = await page.evaluate(async () => {
      const r = await axe.run(document, { runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa', 'best-practice'] } })
      return r.violations.map(v => ({ id: v.id, impact: v.impact, n: v.nodes.length, sample: v.nodes.slice(0, 3).map(n => n.target.join(' ') + ' :: ' + (n.failureSummary || '').slice(0, 200)) }))
    })
    result[`axe-home-${w}`] = ax
  }
  // keyboard pass
  if (w !== 320) {
    const stops = []
    await page.evaluate(() => window.scrollTo(0, 0))
    for (let i = 0; i < 40; i++) {
      await page.keyboard.press('Tab')
      stops.push(await page.evaluate(() => {
        const e = document.activeElement
        const cs = getComputedStyle(e)
        return { i: 0, tag: e.tagName, text: (e.textContent || '').trim().slice(0, 50), href: e.getAttribute('href'), outline: cs.outlineStyle + ' ' + cs.outlineWidth + ' ' + cs.outlineColor, boxShadow: cs.boxShadow !== 'none', inTable: !!e.closest('table'), section: e.closest('section[id]')?.id }
      }))
    }
    result[`kbd-home-${w}`] = stops.map((s, i) => ({ ...s, i: i + 1 }))
    await page.evaluate(() => window.scrollTo(0, 0))
    await page.keyboard.press('Tab')
    await page.screenshot({ path: `${out}/${tag}-focus1.png` })
  }
  await page.close()
}

for (const [w, h] of [[1440, 900], [390, 844], [320, 800]]) {
  const page = await open('/corrections/', w, h)
  await page.screenshot({ path: `${out}/corrections-${w}-full.png`, fullPage: true })
  result[`corr-${w}`] = await page.evaluate(() => ({ scrollW: document.documentElement.scrollWidth, clientW: document.documentElement.clientWidth }))
  fs.writeFileSync(`${out}/corrections-${w}-text.txt`, await page.evaluate(() => document.body.innerText))
  if (w !== 320) {
    await page.addScriptTag({ content: axeSrc })
    result[`axe-corr-${w}`] = await page.evaluate(async () => {
      const r = await axe.run(document, { runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa', 'best-practice'] } })
      return r.violations.map(v => ({ id: v.id, impact: v.impact, n: v.nodes.length, sample: v.nodes.slice(0, 3).map(n => n.target.join(' ')) }))
    })
  }
  await page.close()
}
fs.writeFileSync(`${out}/capture.json`, JSON.stringify(result, null, 2))
await browser.close()
console.log('done')
