// Scorer capture script (Opus blind score, rubric v3.0). Run inside OrbStack dev VM:
//   cd /tmp/opusscore && node <this file> <outdir>
import { chromium } from '/tmp/opusscore/node_modules/playwright/index.mjs'
import fs from 'fs'
const axeSrc = fs.readFileSync('/tmp/opusscore/node_modules/axe-core/axe.min.js', 'utf8')
const BASE = 'https://security-market-pulse-git-preview-pikeholdings.vercel.app'
const out = process.argv[2]
const vps = [
  { width: 1440, height: 900 },
  { width: 390, height: 844 },
  { width: 320, height: 800 },
]
const routes = ['/', '/corrections/', '/issues/', '/thesis/', '/issues/2026-w36/']
const browser = await chromium.launch()
const summary = {}
for (const route of routes) {
  for (const vp of vps) {
    const page = await browser.newPage({ viewport: vp })
    await page.goto(BASE + route, { waitUntil: 'networkidle', timeout: 60000 })
    await page.waitForTimeout(1500)
    const tag = (route === '/' ? 'home' : route.replace(/\//g, '_').replace(/^_|_$/g, '')) + '-' + vp.width
    await page.screenshot({ path: `${out}/${tag}-fold.png` })
    await page.screenshot({ path: `${out}/${tag}-full.png`, fullPage: true })
    const m = await page.evaluate(() => {
      const main = document.querySelector('main') || document.body
      let first = main
      // first content element: first descendant element with text
      const walker = document.createTreeWalker(main, NodeFilter.SHOW_ELEMENT)
      let n
      while ((n = walker.nextNode())) {
        if (n.children.length === 0 && n.textContent.trim()) { first = n; break }
      }
      const r = first.getBoundingClientRect()
      // tap targets
      const small = []
      document.querySelectorAll('a,button,summary,input,select,[role=button],[tabindex]').forEach((e) => {
        const b = e.getBoundingClientRect()
        if (b.width === 0 && b.height === 0) return
        const cs = getComputedStyle(e)
        if (cs.visibility === 'hidden' || cs.display === 'none') return
        if (b.width < 24 || b.height < 24) small.push({ tag: e.tagName, text: (e.textContent || '').trim().slice(0, 40), w: Math.round(b.width), h: Math.round(b.height), inline: cs.display === 'inline' })
      })
      // font sizes of text nodes
      const sizes = {}
      const smallText = []
      document.querySelectorAll('body *').forEach((e) => {
        const own = [...e.childNodes].filter((c) => c.nodeType === 3 && c.textContent.trim()).map((c) => c.textContent.trim()).join(' ')
        if (!own) return
        const cs = getComputedStyle(e)
        if (cs.display === 'none' || cs.visibility === 'hidden') return
        const b = e.getBoundingClientRect(); if (b.width === 0) return
        const fs = cs.fontSize
        sizes[fs] = (sizes[fs] || 0) + 1
        if (parseFloat(fs) < 13 && own.length > 40) smallText.push({ fs, tag: e.tagName, text: own.slice(0, 80) })
      })
      const fams = new Set()
      document.querySelectorAll('body *').forEach((e) => fams.add(getComputedStyle(e).fontFamily))
      return {
        title: document.title,
        height: document.documentElement.scrollHeight,
        scrollWidth: document.documentElement.scrollWidth,
        clientWidth: document.documentElement.clientWidth,
        firstContent: { tag: first.tagName, text: first.textContent.trim().slice(0, 80), top: Math.round(r.top + scrollY) },
        smallTargets: small,
        fontSizes: sizes,
        smallText: smallText.slice(0, 20),
        fontFamilies: [...fams],
        details: [...document.querySelectorAll('details')].map((d) => ({ open: d.open, summary: (d.querySelector('summary')?.textContent || '').trim().slice(0, 60) })),
        timeEls: document.querySelectorAll('time').length,
        timeWithDt: document.querySelectorAll('time[datetime]').length,
        landmarks: [...document.querySelectorAll('header,nav,main,footer,aside,[role]')].map((e) => e.tagName + (e.getAttribute('role') ? '[' + e.getAttribute('role') + ']' : '')),
        emptyHeadings: [...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].filter((h) => !h.textContent.trim()).length,
        dupIds: (() => { const c = {}; document.querySelectorAll('[id]').forEach((e) => (c[e.id] = (c[e.id] || 0) + 1)); return Object.entries(c).filter(([, v]) => v > 1) })(),
      }
    })
    const text = await page.evaluate(() => document.body.innerText)
    fs.writeFileSync(`${out}/${tag}-text.txt`, text)
    // axe
    let axe = null
    if (route === '/' || route === '/corrections/') {
      if (vp.width !== 320) {
        await page.addScriptTag({ content: axeSrc })
        axe = await page.evaluate(async () => {
          const r = await window.axe.run(document, { runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa', 'best-practice'] } })
          return r.violations.map((v) => ({ id: v.id, impact: v.impact, help: v.help, nodes: v.nodes.length, sample: v.nodes.slice(0, 3).map((n) => n.target.join(' ') + ' :: ' + (n.failureSummary || '').slice(0, 200)) }))
        })
        fs.writeFileSync(`${out}/axe-${tag}.json`, JSON.stringify(axe, null, 2))
      }
    }
    summary[tag] = { ...m, axe: axe && axe.map((a) => `${a.impact} ${a.id} x${a.nodes}`) }
    await page.close()
  }
}
fs.writeFileSync(`${out}/measure.json`, JSON.stringify(summary, null, 2))
// keyboard pass on home at 1440 and 390
const kb = {}
for (const vp of vps.slice(0, 2)) {
  const page = await browser.newPage({ viewport: vp })
  await page.goto(BASE + '/', { waitUntil: 'networkidle' })
  const stops = []
  for (let i = 0; i < 40; i++) {
    await page.keyboard.press('Tab')
    const s = await page.evaluate(() => {
      const e = document.activeElement
      const cs = getComputedStyle(e)
      return { tag: e.tagName, text: (e.textContent || e.getAttribute('aria-label') || '').trim().slice(0, 50), href: e.getAttribute('href'), outline: cs.outlineStyle + ' ' + cs.outlineWidth + ' ' + cs.outlineColor, boxShadow: cs.boxShadow }
    })
    stops.push(s)
  }
  kb[vp.width] = stops
  await page.close()
}
fs.writeFileSync(`${out}/keyboard.json`, JSON.stringify(kb, null, 2))
await browser.close()
console.log('done')
