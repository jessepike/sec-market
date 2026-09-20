// THROWAWAY script for item 3 (keyboard walk) and the disclosure-toggle check.
// Copy of baseline/measure/keyboard-walk.mjs, target changed to preview, OUT changed to
// evidence/after/measure. Sticky-overlap check extended per task instructions: instead of
// checking only the single tallest top-pinned fixed/sticky element (the baseline's
// "header" heuristic), every stop is checked against EVERY position:sticky / position:fixed
// element on the page, and a stop counts as hidden if its bounding box is covered by any of
// them. All sticky/fixed elements found are also listed with computed position, top and height.
import { chromium } from '@playwright/test'
import fs from 'node:fs'

const OUT = '/mnt/mac/Users/jessepike/code/projects/sec-market/docs/active/fable-run/evidence/after/measure'
const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })
await page.goto('https://security-market-pulse-git-preview-pikeholdings.vercel.app/', { waitUntil: 'networkidle', timeout: 60000 })
await page.waitForTimeout(1000)

// Enumerate every sticky/fixed element on the page (not just a top-pinned "header" heuristic).
function cssSelectorForSticky(el) {
  if (!(el instanceof Element)) return ''
  const path = []
  let node = el
  while (node && node.nodeType === Node.ELEMENT_NODE && path.length < 5) {
    let sel = node.nodeName.toLowerCase()
    if (node.id) { sel += '#' + node.id; path.unshift(sel); break }
    if (node.className && typeof node.className === 'string') {
      const cls = node.className.trim().split(/\s+/).slice(0, 2).join('.')
      if (cls) sel += '.' + cls
    }
    path.unshift(sel)
    node = node.parentElement
  }
  return path.join(' > ')
}

const stickyElements = await page.evaluate((selectorFnSrc) => {
  // eslint-disable-next-line no-eval
  const cssSelector = eval(`(${selectorFnSrc})`)
  const all = Array.from(document.querySelectorAll('body *'))
  const found = []
  for (const el of all) {
    const cs = getComputedStyle(el)
    if (cs.position === 'sticky' || cs.position === 'fixed') {
      const r = el.getBoundingClientRect()
      if (r.width === 0 && r.height === 0) continue
      found.push({
        selector: cssSelector(el),
        tag: el.tagName,
        position: cs.position,
        top: cs.top,
        computedRectTop: Math.round(r.top),
        height: Math.round(r.height),
      })
    }
  }
  return found
}, cssSelectorForSticky.toString())

// header height for the legacy "pinned to top" check, kept for comparability with baseline.
const headerInfo = await page.evaluate(() => {
  const candidates = Array.from(document.querySelectorAll('body *')).filter(el => {
    const cs = getComputedStyle(el)
    return (cs.position === 'fixed' || cs.position === 'sticky') && el.getBoundingClientRect().top <= 5
  })
  if (!candidates.length) return { height: 0 }
  const el = candidates.sort((a, b) => b.getBoundingClientRect().height - a.getBoundingClientRect().height)[0]
  const r = el.getBoundingClientRect()
  return { height: r.height, tag: el.tagName, className: el.className }
})

const stops = []
const MAX = 80
let signedByPressCount = null

for (let i = 1; i <= MAX; i++) {
  await page.keyboard.press('Tab')
  await page.waitForTimeout(80)
  const info = await page.evaluate(() => {
    function accessibleName(el) {
      if (!el) return null
      if (el.getAttribute('aria-label')) return el.getAttribute('aria-label')
      const labelledby = el.getAttribute('aria-labelledby')
      if (labelledby) {
        const t = labelledby.split(/\s+/).map(id => document.getElementById(id)?.textContent?.trim()).filter(Boolean).join(' ')
        if (t) return t
      }
      if (el.tagName === 'IMG' && el.alt) return el.alt
      if (el.title) return el.title
      const text = (el.textContent || '').trim().replace(/\s+/g, ' ')
      if (text) return text.slice(0, 80)
      if (el.value) return String(el.value)
      return '(no accessible name)'
    }
    function cssSelector(el) {
      if (!(el instanceof Element)) return ''
      const path = []
      let node = el
      while (node && node.nodeType === Node.ELEMENT_NODE && path.length < 5) {
        let sel = node.nodeName.toLowerCase()
        if (node.id) { sel += '#' + node.id; path.unshift(sel); break }
        if (node.className && typeof node.className === 'string') {
          const cls = node.className.trim().split(/\s+/).slice(0, 2).join('.')
          if (cls) sel += '.' + cls
        }
        path.unshift(sel)
        node = node.parentElement
      }
      return path.join(' > ')
    }
    const el = document.activeElement
    if (!el || el === document.body) return null
    const rect = el.getBoundingClientRect()
    const absoluteTop = Math.round(rect.top + window.scrollY)
    return {
      tag: el.tagName,
      name: accessibleName(el),
      selector: cssSelector(el),
      rectTop: Math.round(rect.top),
      rectBottom: Math.round(rect.bottom),
      rectLeft: Math.round(rect.left),
      rectRight: Math.round(rect.right),
      absoluteTop,
      isSkipLink: /skip to|skip navigation|skip content/i.test(el.textContent || '') || /skip/i.test(el.className || ''),
      containsSignedBy: (el.textContent || '').includes('Signed by'),
    }
  })
  if (!info) { stops.push({ press: i, note: 'focus left document / body focused' }); continue }

  // focus-indicator check: compare focused vs. blurred computed style for this element
  const styleCompare = await page.evaluate(() => {
    const el = document.activeElement
    function styleOf() {
      const cs = getComputedStyle(el)
      return { outlineStyle: cs.outlineStyle, outlineWidth: cs.outlineWidth, outlineColor: cs.outlineColor, boxShadow: cs.boxShadow, borderColor: cs.borderColor, borderWidth: cs.borderWidth }
    }
    const focused = styleOf()
    el.blur()
    const blurred = styleOf()
    el.focus()
    const changed = JSON.stringify(focused) !== JSON.stringify(blurred)
    const hasVisibleOutline = focused.outlineStyle !== 'none' && parseFloat(focused.outlineWidth) > 0
    const hasBoxShadow = focused.boxShadow !== 'none' && focused.boxShadow !== blurred.boxShadow
    return { changed, hasVisibleOutline, hasBoxShadow, focused, blurred }
  })

  // Full sticky/fixed overlap check: is the focused element's box covered by ANY
  // position:sticky/fixed element (excluding the focused element's own ancestors, since an
  // element cannot hide itself)?
  const stickyOverlap = await page.evaluate(() => {
    const el = document.activeElement
    if (!el) return { hidden: false, coveringSelectors: [] }
    const rect = el.getBoundingClientRect()
    if (rect.width === 0 && rect.height === 0) return { hidden: false, coveringSelectors: [] }
    function cssSelector(node) {
      const path = []
      while (node && node.nodeType === Node.ELEMENT_NODE && path.length < 5) {
        let sel = node.nodeName.toLowerCase()
        if (node.id) { sel += '#' + node.id; path.unshift(sel); break }
        if (node.className && typeof node.className === 'string') {
          const cls = node.className.trim().split(/\s+/).slice(0, 2).join('.')
          if (cls) sel += '.' + cls
        }
        path.unshift(sel)
        node = node.parentElement
      }
      return path.join(' > ')
    }
    let ancestor = el
    const ancestors = new Set()
    while (ancestor) { ancestors.add(ancestor); ancestor = ancestor.parentElement }
    const all = Array.from(document.querySelectorAll('body *'))
    const stickyFixed = []
    for (const cand of all) {
      if (ancestors.has(cand)) continue // an element's own ancestor can't "hide" it
      const cs = getComputedStyle(cand)
      if (cs.position !== 'sticky' && cs.position !== 'fixed') continue
      const cr = cand.getBoundingClientRect()
      if (cr.width === 0 || cr.height === 0) continue
      if (cs.visibility === 'hidden' || cs.display === 'none' || parseFloat(cs.opacity) === 0) continue
      const overlaps = !(rect.right <= cr.left || rect.left >= cr.right || rect.bottom <= cr.top || rect.top >= cr.bottom)
      if (overlaps) stickyFixed.push({ el: cand, selector: cssSelector(cand), position: cs.position, top: cs.top, zIndex: cs.zIndex })
    }
    if (stickyFixed.length === 0) return { hidden: false, coveringSelectors: [], method: 'no-bbox-overlap' }
    // Bounding-box overlap alone over-reports (a skip link deliberately sits at the same
    // coordinates as the header until focused, then paints above it). Confirm true visual
    // occlusion with elementFromPoint: sample points inside the focused element's box,
    // clamped to the viewport, and check whether the topmost painted element there is the
    // focused element (or one of its descendants) rather than the sticky/fixed candidate.
    const vw = window.innerWidth, vh = window.innerHeight
    const clampedRect = {
      left: Math.max(0, rect.left), right: Math.min(vw, rect.right),
      top: Math.max(0, rect.top), bottom: Math.min(vh, rect.bottom),
    }
    const points = []
    if (clampedRect.right > clampedRect.left && clampedRect.bottom > clampedRect.top) {
      const cx = (clampedRect.left + clampedRect.right) / 2
      const cy = (clampedRect.top + clampedRect.bottom) / 2
      points.push([cx, cy])
      points.push([clampedRect.left + 2, clampedRect.top + 2])
    }
    let occludedBy = null
    for (const [x, y] of points) {
      const top = document.elementFromPoint(x, y)
      if (!top) continue
      const isFocusedOrDescendant = top === el || el.contains(top) || top.contains(el)
      if (isFocusedOrDescendant) continue
      const coveringCandidate = stickyFixed.find(sf => sf.el === top || sf.el.contains(top))
      if (coveringCandidate) { occludedBy = coveringCandidate; break }
    }
    const covering = occludedBy
      ? [{ selector: occludedBy.selector, position: occludedBy.position, top: occludedBy.top, zIndex: occludedBy.zIndex }]
      : []
    return { hidden: covering.length > 0, coveringSelectors: covering, method: 'elementFromPoint', bboxOverlapOnly: stickyFixed.map(s => s.selector) }
  })

  const hiddenBehindHeader = headerInfo.height > 0 && info.rectTop < headerInfo.height && info.rectBottom > 0

  stops.push({
    press: i,
    tag: info.tag,
    name: info.name,
    selector: info.selector,
    isSkipLink: info.isSkipLink,
    hasVisibleFocusIndicator: styleCompare.changed,
    hiddenBehindStickyHeader: hiddenBehindHeader,
    hiddenBehindAnySticky: stickyOverlap.hidden,
    coveringStickyElements: stickyOverlap.coveringSelectors,
    bboxOverlapOnly: stickyOverlap.bboxOverlapOnly || [],
  })

  if (info.containsSignedBy && signedByPressCount === null) signedByPressCount = i
}

// details/summary reachability + Enter/Space toggle check
const disclosureCheck = await page.evaluate(() => {
  const d = document.querySelector('details')
  const s = d ? d.querySelector('summary') : null
  return { hasDetails: !!d, hasSummary: !!s, summaryTabIndex: s ? s.tabIndex : null, initiallyOpen: d ? d.open : null }
})
let enterToggle = null, spaceToggle = null
try {
  const summarySelector = 'details summary'
  await page.locator(summarySelector).first().focus()
  const before = await page.evaluate(() => document.querySelector('details').open)
  await page.keyboard.press('Enter')
  await page.waitForTimeout(150)
  const afterEnter = await page.evaluate(() => document.querySelector('details').open)
  enterToggle = { before, afterEnter, toggled: before !== afterEnter }
  await page.keyboard.press('Enter') // close it back with Enter
  await page.waitForTimeout(150)
  const beforeSpace = await page.evaluate(() => document.querySelector('details').open)
  await page.keyboard.press(' ')
  await page.waitForTimeout(150)
  const afterSpace = await page.evaluate(() => document.querySelector('details').open)
  spaceToggle = { beforeSpace, afterSpace, toggled: beforeSpace !== afterSpace }
} catch (e) {
  enterToggle = { error: String(e) }
}

const result = {
  stickyElementsOnPage: stickyElements,
  headerInfo,
  firstStopIsSkipLink: stops[0] ? stops[0].isSkipLink : null,
  first25Stops: stops.slice(0, 25),
  allStopsFocusIndicatorSummary: {
    total: stops.filter(s => s.tag).length,
    withVisibleIndicator: stops.filter(s => s.hasVisibleFocusIndicator).length,
    withoutVisibleIndicator: stops.filter(s => s.tag && !s.hasVisibleFocusIndicator).map(s => ({ press: s.press, tag: s.tag, selector: s.selector })),
  },
  stopsHiddenBehindHeader: stops.filter(s => s.hiddenBehindStickyHeader).map(s => ({ press: s.press, tag: s.tag, selector: s.selector })),
  stopsHiddenBehindAnySticky: stops.filter(s => s.hiddenBehindAnySticky).map(s => ({ press: s.press, tag: s.tag, selector: s.selector, coveringStickyElements: s.coveringStickyElements })),
  signedByPressCount,
  disclosureCheck,
  enterToggle,
  spaceToggle,
}

fs.writeFileSync(`${OUT}/keyboard-walk-results.json`, JSON.stringify(result, null, 2))
console.log(JSON.stringify({
  stickyElementsOnPageCount: stickyElements.length,
  stickyElementsOnPage: stickyElements,
  firstStopIsSkipLink: result.firstStopIsSkipLink,
  signedByPressCount,
  totalStopsCaptured: stops.length,
  withVisibleIndicator: result.allStopsFocusIndicatorSummary.withVisibleIndicator,
  withoutVisibleIndicator: result.allStopsFocusIndicatorSummary.withoutVisibleIndicator.length,
  hiddenBehindHeaderCount: result.stopsHiddenBehindHeader.length,
  hiddenBehindAnyStickyCount: result.stopsHiddenBehindAnySticky.length,
  disclosureCheck,
  enterToggle,
  spaceToggle,
}, null, 2))
await browser.close()
