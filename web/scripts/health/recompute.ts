/**
 * Recomputes healthFacts.json from SEC companyfacts, anchored on the revenue
 * quarters already in edgarFacts.json, without touching revenue. The daily
 * refresh (`npm run refresh:edgar`) does the same as part of its run; this is
 * for a one-off refresh where data.sec.gov is reachable:
 *
 *   npx tsx --tsconfig tsconfig.app.json scripts/health/recompute.ts
 *
 * Supersedes pull.py plus compute.py (kept for the 2026-11-06 record).
 */
import { readFile, writeFile } from 'node:fs/promises'
import edgar from '../../src/data/generated/edgarFacts.json' with { type: 'json' }
import contract from '../../src/data/tracker/certifiedContract.json' with { type: 'json' }
import { computeHealth, healthMethod, type HealthFile } from '../../src/data/healthLogic.ts'
import type { CompanyFacts, QuarterFact } from '../../src/data/edgarLogic.ts'

const OUT = new URL('../../src/data/generated/healthFacts.json', import.meta.url)
const certified = new Set(contract.supplierIds)
const previous = JSON.parse(await readFile(OUT, 'utf8')) as HealthFile
const out: HealthFile = { generatedAt: edgar.generatedAt, method: healthMethod, suppliers: {}, gaps: {} }
for (const s of edgar.suppliers as { id: string; cik: string; quarters: QuarterFact[] }[]) {
  if (!certified.has(s.id)) continue
  const res = await fetch(`https://data.sec.gov/api/xbrl/companyfacts/CIK${s.cik}.json`, { headers: { 'User-Agent': 'SecurityMarketPulse research jesse@keatingpike.com', Accept: 'application/json' } })
  if (!res.ok) { console.error(`keep ${s.id}: HTTP ${res.status}`); if (previous.suppliers[s.id]) out.suppliers[s.id] = previous.suppliers[s.id]; continue }
  const { health, gaps, notes } = computeHealth(s.cik, s.quarters, await res.json() as CompanyFacts)
  out.suppliers[s.id] = health
  if (gaps.length) out.gaps[s.id] = gaps
  if (notes.length) (out.notes ??= {})[s.id] = notes
  console.log(`${s.id.padEnd(11)} op ${health.operatingMargin?.value ?? '-'} fcf ${health.fcfMargin?.value ?? '-'} cash ${health.balance?.cash ?? '-'} debt ${health.balance?.debt ?? '-'} ${gaps.join('; ')}`)
  await new Promise(r => setTimeout(r, 250))
}
await writeFile(OUT, `${JSON.stringify(out, null, 1)}\n`)
