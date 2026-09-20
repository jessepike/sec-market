// THROWAWAY script for item 3 (keyboard walk) and the disclosure-toggle check.
import { chromium } from '@playwright/test'
import fs from 'node:fs'

const OUT = '/mnt/mac/Users/jessepike/code/projects/sec-market/docs/active/fable-run/evidence/baseline/measure'
const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })
await page.goto('https://securitymarketpulse.com/', { waitUntil: 'networkidle', timeout: 60000 })
await page.waitForTimeout(1000)

// header height for sticky-overlap check
const headerInfo = await page.evaluate(() => {
  const candidates = Array.from(document.querySelectorAll('body *')).filter(el => {
    const cs = getComputedStyle(el)
    return (cs.position === 'fixed' || cs.position === 'sticky') && el.getBoundingClientRect().top <= 5
  })
  if (!candidates.length) return { height: 0 }
  // pick the tallest/topmost sticky/fixed element
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

  const hiddenBehindHeader = headerInfo.height > 0 && info.rectTop < headerInfo.height && info.rectBottom > 0

  stops.push({
    press: i,
    tag: info.tag,
    name: info.name,
    selector: info.selector,
    isSkipLink: info.isSkipLink,
    hasVisibleFocusIndicator: styleCompare.changed,
    hiddenBehindStickyHeader: hiddenBehindHeader,
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
  headerInfo,
  firstStopIsSkipLink: stops[0] ? stops[0].isSkipLink : null,
  first25Stops: stops.slice(0, 25),
  allStopsFocusIndicatorSummary: {
    total: stops.filter(s => s.tag).length,
    withVisibleIndicator: stops.filter(s => s.hasVisibleFocusIndicator).length,
    withoutVisibleIndicator: stops.filter(s => s.tag && !s.hasVisibleFocusIndicator).map(s => ({ press: s.press, tag: s.tag, selector: s.selector })),
  },
  stopsHiddenBehindHeader: stops.filter(s => s.hiddenBehindStickyHeader).map(s => ({ press: s.press, tag: s.tag, selector: s.selector })),
  signedByPressCount,
  disclosureCheck,
  enterToggle,
  spaceToggle,
}

fs.writeFileSync(`${OUT}/keyboard-walk-results.json`, JSON.stringify(result, null, 2))
console.log(JSON.stringify({
  firstStopIsSkipLink: result.firstStopIsSkipLink,
  signedByPressCount,
  totalStopsCaptured: stops.length,
  withVisibleIndicator: result.allStopsFocusIndicatorSummary.withVisibleIndicator,
  withoutVisibleIndicator: result.allStopsFocusIndicatorSummary.withoutVisibleIndicator.length,
  hiddenBehindHeaderCount: result.stopsHiddenBehindHeader.length,
  disclosureCheck,
  enterToggle,
  spaceToggle,
}, null, 2))
await browser.close()
