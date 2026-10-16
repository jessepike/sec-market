// THROWAWAY script for items 4,5,6,7,8,9,10.
// Run with working directory = web/ so bare imports resolve from web/node_modules.
import { chromium } from '@playwright/test'
import fs from 'node:fs'

const base = 'https://securitymarketpulse.com'
const OUT = '/mnt/mac/Users/jessepike/code/projects/sec-market/docs/active/fable-run/evidence/baseline/measure'

const browser = await chromium.launch()
const out = {}

// ---------- shared in-page helper library ----------
const pageFns = () => {
  function cssSelector(el) {
    if (!(el instanceof Element)) return ''
    const path = []
    while (el && el.nodeType === Node.ELEMENT_NODE && path.length < 6) {
      let sel = el.nodeName.toLowerCase()
      if (el.id) { sel += '#' + el.id; path.unshift(sel); break }
      if (el.className && typeof el.className === 'string') {
        const cls = el.className.trim().split(/\s+/).slice(0, 2).join('.')
        if (cls) sel += '.' + cls
      }
      let sib = el, nth = 1
      while ((sib = sib.previousElementSibling)) nth++
      sel += `:nth-child(${nth})`
      path.unshift(sel)
      el = el.parentElement
    }
    return path.join(' > ')
  }
  window.__cssSelector = cssSelector
}

// ================= ITEM 9: disclosure count =================
{
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })
  await page.goto(base + '/', { waitUntil: 'networkidle', timeout: 60000 })
  await page.waitForTimeout(1000)
  const disclosures = await page.evaluate(() => {
    const all = Array.from(document.querySelectorAll('details'))
    return { total: all.length, open: all.filter(d => d.open).length }
  })
  out.disclosures = disclosures
  console.log('item9 disclosures:', JSON.stringify(disclosures))
  await page.close()
}

// ================= ITEM 10: word counts =================
{
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })
  await page.goto(base + '/', { waitUntil: 'networkidle', timeout: 60000 })
  await page.waitForTimeout(1000)
  const words = await page.evaluate(() => {
    function countWords(s) {
      return (s || '').trim().split(/\s+/).filter(Boolean).length
    }
    const visible = countWords(document.body.innerText)
    // total including closed disclosures: clone body, strip script/style, use textContent
    const clone = document.body.cloneNode(true)
    clone.querySelectorAll('script, style, noscript').forEach(n => n.remove())
    const total = countWords(clone.textContent)
    return { visibleWordCount: visible, totalWordCountIncludingClosedDisclosures: total }
  })
  out.words = words
  console.log('item10 words:', JSON.stringify(words))
  await page.close()
}

// ================= ITEM 7: headings =================
{
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })
  await page.goto(base + '/', { waitUntil: 'networkidle', timeout: 60000 })
  await page.waitForTimeout(1000)
  await page.evaluate(pageFns)
  const headings = await page.evaluate(() => {
    const hs = Array.from(document.querySelectorAll('h1,h2,h3,h4,h5,h6'))
    const empties = hs
      .filter(h => !h.textContent.replace(/\s+/g, ' ').trim())
      .map(h => ({ tag: h.tagName, selector: window.__cssSelector(h) }))
    const levels = hs.map(h => parseInt(h.tagName[1]))
    let skips = []
    for (let i = 1; i < levels.length; i++) {
      if (levels[i] > levels[i - 1] + 1) {
        skips.push(`h${levels[i - 1]} -> h${levels[i]} at index ${i} (${hs[i].textContent.trim().slice(0, 40)})`)
      }
    }
    return { totalHeadings: hs.length, emptyHeadings: empties, levelSkips: skips }
  })
  out.headings = headings
  console.log('item7 headings:', JSON.stringify(headings))
  await page.close()
}

// ================= ITEM 4: target size at 390 =================
{
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } })
  await page.goto(base + '/', { waitUntil: 'networkidle', timeout: 60000 })
  await page.waitForTimeout(1000)
  await page.evaluate(pageFns)
  const targets = await page.evaluate(() => {
    const els = Array.from(document.querySelectorAll('a, button, summary'))
    const results = []
    for (const el of els) {
      const rect = el.getBoundingClientRect()
      if (rect.width === 0 && rect.height === 0) continue
      // heuristic: inline link inside a sentence => display:inline AND has non-whitespace
      // text sibling (before or after) within the same parent block.
      const cs = getComputedStyle(el)
      let inlineInSentence = false
      if (el.tagName === 'A' && (cs.display === 'inline' || cs.display === 'inline-block')) {
        const parent = el.parentElement
        if (parent) {
          const siblings = Array.from(parent.childNodes)
          const idx = siblings.indexOf(el)
          const before = siblings.slice(0, idx).some(n => n.nodeType === 3 && n.textContent.trim().length > 0)
          const after = siblings.slice(idx + 1).some(n => n.nodeType === 3 && n.textContent.trim().length > 0)
          if (before || after) inlineInSentence = true
        }
      }
      results.push({
        tag: el.tagName,
        selector: window.__cssSelector(el),
        width: Math.round(rect.width * 10) / 10,
        height: Math.round(rect.height * 10) / 10,
        inlineInSentence,
        text: (el.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 50),
      })
    }
    return results
  })
  const eligible = targets.filter(t => !t.inlineInSentence)
  const small = eligible.filter(t => t.width < 24 || t.height < 24)
  small.sort((a, b) => (a.width * a.height) - (b.width * b.height))
  out.targetSize = {
    totalElements: targets.length,
    eligibleElements: eligible.length,
    excludedInlineInSentence: targets.length - eligible.length,
    smallCount: small.length,
    tenSmallest: small.slice(0, 10),
  }
  console.log('item4 targetSize summary:', out.targetSize.totalElements, out.targetSize.eligibleElements, out.targetSize.smallCount)
  await page.close()
}

// ================= ITEM 5: reflow at 320x640 =================
{
  const page = await browser.newPage({ viewport: { width: 320, height: 640 } })
  await page.goto(base + '/', { waitUntil: 'networkidle', timeout: 60000 })
  await page.waitForTimeout(1000)
  await page.evaluate(pageFns)
  const reflow = await page.evaluate(() => {
    const scrollWidth = document.documentElement.scrollWidth
    const clientWidth = document.documentElement.clientWidth
    const overflowing = []
    const all = document.querySelectorAll('body *')
    for (const el of all) {
      const rect = el.getBoundingClientRect()
      if (rect.width === 0) continue
      if (Math.round(rect.right) > clientWidth + 1 || Math.round(rect.left) < -1) {
        overflowing.push({
          selector: window.__cssSelector(el),
          tag: el.tagName,
          left: Math.round(rect.left),
          right: Math.round(rect.right),
          width: Math.round(rect.width),
        })
      }
      if (overflowing.length >= 40) break
    }
    return { scrollWidth, clientWidth, horizontalScroll: scrollWidth > clientWidth, overflowingCount: overflowing.length, overflowingSample: overflowing.slice(0, 10) }
  })
  out.reflow = reflow
  console.log('item5 reflow:', JSON.stringify({ scrollWidth: reflow.scrollWidth, clientWidth: reflow.clientWidth, horizontalScroll: reflow.horizontalScroll, overflowingCount: reflow.overflowingCount }))
  await page.close()
}

// ================= ITEM 6: contrast on small text =================
{
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })
  await page.goto(base + '/', { waitUntil: 'networkidle', timeout: 60000 })
  await page.waitForTimeout(1000)
  await page.evaluate(pageFns)
  const contrast = await page.evaluate(() => {
    function parseColor(str) {
      const m = str.match(/rgba?\(([^)]+)\)/)
      if (!m) return null
      const parts = m[1].split(',').map(s => parseFloat(s.trim()))
      return { r: parts[0], g: parts[1], b: parts[2], a: parts.length > 3 ? parts[3] : 1 }
    }
    function relLum({ r, g, b }) {
      const chan = c => {
        c = c / 255
        return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4)
      }
      return 0.2126 * chan(r) + 0.7152 * chan(g) + 0.0722 * chan(b)
    }
    function contrastRatio(fg, bg) {
      const l1 = relLum(fg) + 0.05
      const l2 = relLum(bg) + 0.05
      return l1 > l2 ? l1 / l2 : l2 / l1
    }
    function effectiveBg(el) {
      let node = el
      while (node) {
        const cs = getComputedStyle(node)
        const c = parseColor(cs.backgroundColor)
        if (c && c.a > 0) {
          if (c.a >= 0.999) return c
          // approximate blend against white if translucent and no further parent resolves
          const parentBg = node.parentElement ? effectiveBg(node.parentElement) : { r: 255, g: 255, b: 255 }
          return {
            r: c.r * c.a + parentBg.r * (1 - c.a),
            g: c.g * c.a + parentBg.g * (1 - c.a),
            b: c.b * c.a + parentBg.b * (1 - c.a),
          }
        }
        node = node.parentElement
      }
      return { r: 255, g: 255, b: 255 }
    }

    const results = []
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
      acceptNode(n) {
        if (!n.textContent || !n.textContent.trim()) return NodeFilter.FILTER_REJECT
        const p = n.parentElement
        if (!p) return NodeFilter.FILTER_REJECT
        const cs = getComputedStyle(p)
        if (cs.display === 'none' || cs.visibility === 'hidden') return NodeFilter.FILTER_REJECT
        return NodeFilter.FILTER_ACCEPT
      },
    })
    const seen = new Set()
    let node
    while ((node = walker.nextNode())) {
      const p = node.parentElement
      if (seen.has(p)) continue
      seen.add(p)
      const cs = getComputedStyle(p)
      const fontPx = parseFloat(cs.fontSize)
      if (!(fontPx < 14)) continue
      const fg = parseColor(cs.color)
      if (!fg) continue
      const bg = effectiveBg(p)
      const ratio = contrastRatio(fg, bg)
      const rect = p.getBoundingClientRect()
      results.push({
        selector: window.__cssSelector(p),
        text: node.textContent.trim().slice(0, 40),
        fontSize: fontPx,
        color: cs.color,
        effectiveBackground: `rgb(${Math.round(bg.r)}, ${Math.round(bg.g)}, ${Math.round(bg.b)})`,
        ratio: Math.round(ratio * 100) / 100,
        inTopBar: rect.top < 60 && rect.top >= -5,
      })
    }
    return results
  })
  const failing = contrast.filter(c => c.ratio < 4.5)
  const failingNonTopBar = failing.filter(c => !c.inTopBar)
  const failingTopBar = failing.filter(c => c.inTopBar)
  failingNonTopBar.sort((a, b) => a.ratio - b.ratio)
  failingTopBar.sort((a, b) => a.ratio - b.ratio)
  out.contrast = {
    totalSmallTextNodes: contrast.length,
    failingCount: failing.length,
    failingNonTopBarCount: failingNonTopBar.length,
    failingTopBarCount: failingTopBar.length,
    fiveWorstNonTopBar: failingNonTopBar.slice(0, 5),
    topBarSample: failingTopBar.slice(0, 5),
  }
  console.log('item6 contrast:', JSON.stringify({ total: contrast.length, failing: failing.length, topBarFailing: failingTopBar.length }))
  await page.close()
}

// ================= ITEM 8: position measurements =================
for (const [label, width, height] of [['1440x900', 1440, 900], ['390x844', 390, 844]]) {
  const page = await browser.newPage({ viewport: { width, height } })
  await page.goto(base + '/', { waitUntil: 'networkidle', timeout: 60000 })
  await page.waitForTimeout(1000)
  const data = await page.evaluate(({ vpHeight }) => {
    function findTextEl(needle) {
      const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT)
      let node
      while ((node = walker.nextNode())) {
        if (node.textContent.includes(needle)) return node.parentElement
      }
      return null
    }
    const docHeight = document.documentElement.scrollHeight
    function offsetOf(el) {
      if (!el) return null
      const rect = el.getBoundingClientRect()
      return Math.round(rect.top + window.scrollY)
    }
    const signedEl = document.querySelector('.we-think__signature') || findTextEl('Signed by')
    const whatWeThinkEl = document.getElementById('we-think-heading') || findTextEl('What we now think')
    const infraEl = findTextEl('Infrastructure is running ahead')

    const signedOffset = offsetOf(signedEl)
    const whatWeThinkOffset = offsetOf(whatWeThinkEl)
    const infraOffset = offsetOf(infraEl)

    // lane items: .issue-lane__item across the 4 lanes (Formation/Absorption/Prints/Capital)
    const laneItems = Array.from(document.querySelectorAll('.issue-lane__item'))
    const totalLaneItems = laneItems.length
    const fullyVisibleInFirstViewport = laneItems.filter(el => {
      const r = el.getBoundingClientRect()
      return r.top >= 0 && r.bottom <= vpHeight
    }).length

    return {
      docHeight,
      signedOffset,
      whatWeThinkOffset,
      infraOffset,
      totalLaneItems,
      fullyVisibleInFirstViewport,
    }
  }, { vpHeight: height })

  data.signedPct = data.signedOffset != null ? Math.round((data.signedOffset / data.docHeight) * 1000) / 10 : null
  data.whatWeThinkPct = data.whatWeThinkOffset != null ? Math.round((data.whatWeThinkOffset / data.docHeight) * 1000) / 10 : null
  data.infraPct = data.infraOffset != null ? Math.round((data.infraOffset / data.docHeight) * 1000) / 10 : null
  data.signedViewportHeights = data.signedOffset != null ? Math.round((data.signedOffset / height) * 100) / 100 : null
  data.whatWeThinkViewportHeights = data.whatWeThinkOffset != null ? Math.round((data.whatWeThinkOffset / height) * 100) / 100 : null
  data.infraViewportHeights = data.infraOffset != null ? Math.round((data.infraOffset / height) * 100) / 100 : null

  out[`position_${label}`] = data
  console.log(`item8 position @${label}:`, JSON.stringify(data))
  await page.close()
}

fs.writeFileSync(`${OUT}/main-measure-results.json`, JSON.stringify(out, null, 2))
await browser.close()
console.log('ALL DONE')
