// Non-text contrast sample (D10 level-5 test 6): sample computed colours of control
// borders, focus indicators, and chart marks against their backgrounds. WCAG 1.4.11
// requires 3:1 for these.
import { chromium } from '@playwright/test'
import fs from 'node:fs'

const OUT = '/mnt/mac/Users/jessepike/code/projects/sec-market/docs/active/fable-run/evidence/score-0921/measure'
const base = 'https://securitymarketpulse.com'

function parseColor(str) {
  const m = str.match(/rgba?\(([^)]+)\)/)
  if (!m) return null
  const parts = m[1].split(',').map(s => parseFloat(s.trim()))
  return { r: parts[0], g: parts[1], b: parts[2], a: parts.length > 3 ? parts[3] : 1 }
}
function relLum({ r, g, b }) {
  const chan = c => { c = c / 255; return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4) }
  return 0.2126 * chan(r) + 0.7152 * chan(g) + 0.0722 * chan(b)
}
function contrastRatio(fg, bg) {
  const l1 = relLum(fg) + 0.05, l2 = relLum(bg) + 0.05
  return l1 > l2 ? l1 / l2 : l2 / l1
}

const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })
await page.goto(base + '/', { waitUntil: 'networkidle', timeout: 60000 })
await page.waitForTimeout(3000) // let charts paint

const result = await page.evaluate(() => {
  function parseColorIn(str) {
    const m = str.match(/rgba?\(([^)]+)\)/)
    if (!m) return null
    const parts = m[1].split(',').map(s => parseFloat(s.trim()))
    return { r: parts[0], g: parts[1], b: parts[2], a: parts.length > 3 ? parts[3] : 1 }
  }
  function effectiveBg(el) {
    let node = el
    while (node) {
      const cs = getComputedStyle(node)
      const c = parseColorIn(cs.backgroundColor)
      if (c && c.a > 0.999) return c
      node = node.parentElement
    }
    return { r: 255, g: 255, b: 255 }
  }
  const samples = []
  // 1. control borders: buttons and .tag pills and inputs
  const controls = Array.from(document.querySelectorAll('button, .tag, summary, a.chart-table-details, details.chart-table-details summary'))
  for (const el of controls.slice(0, 40)) {
    const cs = getComputedStyle(el)
    const borderColor = cs.borderColor
    const borderWidth = parseFloat(cs.borderWidth || cs.borderTopWidth)
    if (!borderWidth || borderWidth < 1) continue
    const c = parseColorIn(borderColor)
    if (!c || c.a < 0.2) continue
    const bg = effectiveBg(el.parentElement || el)
    samples.push({ kind: 'control-border', selector: el.tagName + (el.className ? '.' + String(el.className).split(' ')[0] : ''), border: borderColor, bg: `rgb(${bg.r},${bg.g},${bg.b})`, fg: c })
  }
  // 2. focus indicator: focus first button, read outline color
  const firstButton = document.querySelector('button')
  let focusSample = null
  if (firstButton) {
    firstButton.focus()
    const cs = getComputedStyle(firstButton)
    const outlineColor = cs.outlineColor
    const bg = effectiveBg(firstButton.parentElement || firstButton)
    focusSample = { outlineColor, outlineWidth: cs.outlineWidth, bg: `rgb(${bg.r},${bg.g},${bg.b})` }
    firstButton.blur()
  }
  // 3. chart marks: svg path/line/rect stroke or fill colors within a chart-section svg
  const chartSvgs = Array.from(document.querySelectorAll('.chart-section svg, [class*="chart"] svg'))
  const chartMarks = []
  for (const svg of chartSvgs.slice(0, 3)) {
    const paths = Array.from(svg.querySelectorAll('path, line, rect, circle')).slice(0, 10)
    for (const p of paths) {
      const cs = getComputedStyle(p)
      const stroke = p.getAttribute('stroke') || cs.stroke
      const fill = p.getAttribute('fill') || cs.fill
      chartMarks.push({ tag: p.tagName, stroke, fill })
    }
  }
  return { samples, focusSample, chartSvgCount: chartSvgs.length, chartMarks }
})

// compute ratios for control borders where colors are parseable rgb()
const out = { raw: result, computed: [] }
for (const s of result.samples) {
  const bgMatch = s.bg.match(/rgb\(([^)]+)\)/)
  if (!bgMatch) continue
  const bgParts = bgMatch[1].split(',').map(Number)
  const bg = { r: bgParts[0], g: bgParts[1], b: bgParts[2] }
  const ratio = contrastRatio(s.fg, bg)
  out.computed.push({ ...s, ratio: Math.round(ratio * 100) / 100 })
}

fs.writeFileSync(`${OUT}/nontext-contrast.json`, JSON.stringify(out, null, 2))
console.log(JSON.stringify({ sampleCount: result.samples.length, focusSample: result.focusSample, chartSvgCount: result.chartSvgCount, chartMarkCount: result.chartMarks.length, computedSample: out.computed.slice(0, 10) }, null, 2))
await browser.close()
