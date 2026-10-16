import { chromium } from 'playwright'
import fs from 'node:fs'
const BASE = process.argv[2]
const OUT = process.argv[3]
const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })
await page.goto(BASE + '/', { waitUntil: 'networkidle' })
await page.waitForTimeout(1500)
const res = await page.evaluate(() => {
  const parse = (c) => { const m = c.match(/rgba?\(([^)]+)\)/); if (!m) return null; const p = m[1].split(',').map(Number); return { r: p[0], g: p[1], b: p[2], a: p[3] ?? 1 } }
  const lum = ({ r, g, b }) => { const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4) }; return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b) }
  const bg = (el) => { while (el) { const c = parse(getComputedStyle(el).backgroundColor); if (c && c.a > 0.9) return c; el = el.parentElement } return { r: 255, g: 255, b: 255 } }
  const out = {}
  const walker = document.createTreeWalker(document.querySelector('main') || document.body, NodeFilter.SHOW_TEXT)
  while (walker.nextNode()) {
    const el = walker.currentNode.parentElement
    const t = walker.currentNode.textContent.trim(); if (!t) continue
    const b = el.getBoundingClientRect(); if (!b.width) continue
    const cs = getComputedStyle(el)
    const fg = parse(cs.color); const bgc = bg(el)
    const L1 = lum(fg), L2 = lum(bgc)
    const ratio = (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05)
    const key = cs.color + ' on ' + `rgb(${bgc.r},${bgc.g},${bgc.b})` + ' ' + cs.fontSize
    if (!out[key]) out[key] = { ratio: +ratio.toFixed(2), sample: t.slice(0, 40), n: 0 }
    out[key].n++
  }
  // topbar too
  const tb = document.querySelector('header')
  return Object.entries(out).sort((a, b) => a[1].ratio - b[1].ratio).slice(0, 12)
})
fs.writeFileSync(`${OUT}/contrast.json`, JSON.stringify(res, null, 1))
await browser.close()
