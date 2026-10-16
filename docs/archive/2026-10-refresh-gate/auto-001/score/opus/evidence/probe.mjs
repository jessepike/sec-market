import { chromium } from 'playwright'
import fs from 'node:fs'
const BASE = process.argv[2]
const OUT = process.argv[3]
const browser = await chromium.launch()
const out = {}
for (const w of [390, 1440]) {
  const page = await browser.newPage({ viewport: { width: w, height: w === 390 ? 844 : 900 } })
  await page.goto(BASE + '/', { waitUntil: 'networkidle' })
  await page.waitForTimeout(2500)
  out[w] = await page.evaluate((w) => {
    const over = []
    document.querySelectorAll('body *').forEach((el) => {
      const b = el.getBoundingClientRect()
      if (b.right > w + 1 && b.width > 0) {
        // only report outermost
        const p = el.parentElement.getBoundingClientRect()
        if (p.right <= w + 1) over.push({ tag: el.tagName, cls: String(el.className).slice(0, 60), id: el.id, right: Math.round(b.right), top: Math.round(b.top + scrollY), txt: el.textContent.trim().slice(0, 60) })
      }
    })
    // section order with tops
    const secs = [...document.querySelectorAll('main > *, main > * > section, main section')].map((s) => ({ tag: s.tagName, id: s.id, cls: String(s.className).slice(0, 50), top: Math.round(s.getBoundingClientRect().top + scrollY), h: Math.round(s.getBoundingClientRect().height), head: (s.querySelector('h2,h3')?.textContent || '').trim().slice(0, 50) }))
    const tables = [...document.querySelectorAll('table')].map((t) => ({ top: Math.round(t.getBoundingClientRect().top + scrollY), h: Math.round(t.getBoundingClientRect().height), w: Math.round(t.getBoundingClientRect().width), rows: t.tBodies[0]?.rows.length, first: t.tBodies[0]?.rows[0]?.textContent.trim().slice(0, 40), wrapScroll: t.parentElement.scrollWidth > t.parentElement.clientWidth, wrapOverflow: getComputedStyle(t.parentElement).overflowX, fvn: getComputedStyle(t.querySelector('td') || t).fontVariantNumeric, tdFont: getComputedStyle(t.querySelector('td') || t).fontFamily.slice(0, 40), tdSize: getComputedStyle(t.querySelector('td') || t).fontSize }))
    const sortBtns = [...document.querySelectorAll('th button, th[aria-sort]')].map((b) => b.textContent.trim()).slice(0, 12)
    const ariaSort = [...document.querySelectorAll('th[aria-sort]')].length
    const nav = [...document.querySelectorAll('header a, nav a')].map((a) => [a.textContent.trim(), a.getAttribute('href')])
    const domainLinks = [...document.querySelectorAll('a[href^="#"]')].map((a) => [a.textContent.trim().slice(0, 40), a.getAttribute('href')]).slice(0, 40)
    const paraLens = [...document.querySelectorAll('main p')].slice(0, 12).map((p) => ({ w: Math.round(p.getBoundingClientRect().width), fs: getComputedStyle(p).fontSize, chars: Math.round(p.getBoundingClientRect().width / (parseFloat(getComputedStyle(p).fontSize) * 0.5)), t: p.textContent.trim().slice(0, 40) }))
    return { over: over.slice(0, 20), secs, tables, sortBtns, ariaSort, nav, domainLinks, paraLens }
  }, w)
  if (w === 390) {
    // screenshots of key regions
    const h = await page.evaluate(() => document.documentElement.scrollHeight)
    for (let y = 800; y < Math.min(h, 7000); y += 1600) {
      await page.screenshot({ path: `${OUT}/p390-${y}.png`, clip: { x: 0, y, width: 390, height: 1600 }, fullPage: true })
    }
  } else {
    const h = await page.evaluate(() => document.documentElement.scrollHeight)
    for (let y = 900; y < h; y += 1800) {
      await page.screenshot({ path: `${OUT}/p1440-${y}.png`, clip: { x: 0, y, width: 1440, height: 1800 }, fullPage: true })
    }
  }
  await page.close()
}
fs.writeFileSync(`${OUT}/probe.json`, JSON.stringify(out, null, 1))
await browser.close()
