// Computes Lighthouse medians (LCP, CLS, TBT, perf score) across 3 runs for a mobile/desktop prefix pair.
// node lh-medians.mjs <dir> <prefix>
import fs from 'node:fs'
import path from 'node:path'

const dir = process.argv[2]
const prefix = process.argv[3]

function stat(label) {
  const vals = [1, 2, 3].map((i) => JSON.parse(fs.readFileSync(path.join(dir, `${label}-${i}.json`), 'utf8')))
  const pick = (fn) => vals.map(fn).sort((a, b) => a - b)[1]
  const lcp = pick((v) => v.audits['largest-contentful-paint'].numericValue)
  const cls = pick((v) => v.audits['cumulative-layout-shift'].numericValue)
  const tbt = pick((v) => v.audits['total-blocking-time'].numericValue)
  const score = pick((v) => v.categories.performance.score)
  console.log(JSON.stringify({ label, lcpMs: lcp, cls, tbtMs: tbt, perfScore: score }))
}

stat(`${prefix}-mobile`)
stat(`${prefix}-desktop`)
