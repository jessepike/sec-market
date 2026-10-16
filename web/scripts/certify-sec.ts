// Certified-tier runner (SEC-MARKET-AUTO-002-P0). Builds the candidate claims
// the site would display for each SEC filer (sec-verify/candidates.ts), fetches
// primary SEC sources, asks the verifier (sec-verify/independent.mjs) to
// re-derive each claim, and writes coverage plus proofs in the exact shape
// evaluateRefresh checks. A claim that fails gets no proof, so the gate holds.
// Raw SEC responses are archived by hash under .collect/sec-archive/ so any
// proof can be re-checked later.
//
// Run: npm run certify:sec   (then npm run certify:gate)
import { createHash } from 'node:crypto'
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { edgarRegistry } from '../src/data/edgarRegistry'
import { trackerSuppliers } from '../src/data/tracker/suppliers'
import { digest } from './refresh-publication-gate.mjs'
import { candidateFor, derivedCertifiedIds, eventWindow, leaves, windowEvents } from './sec-verify/candidates'
import { verifyHistory, verifyIdentity, verifyNotStale, verifyPriorAdjacent, verifyRevenuePeriod, verifySecEvents } from './sec-verify/independent.mjs'

const USER_AGENT = process.env.SMP_SEC_USER_AGENT ?? 'SecurityMarketPulse research jesse@keatingpike.com'
const INTERVAL_MS = 250
const generated = (name: string) => resolve('src/data/generated', name)
const archiveDir = resolve('..', '.collect/sec-archive')
const contract = JSON.parse(readFileSync(resolve('src/data/tracker/certifiedContract.json'), 'utf8'))

interface Fetched { url: string; checkedAt: string; status: 'ok' | 'failed'; sha256?: string; body?: unknown; reason?: string }
interface Result { ok: boolean; reason?: string; locator?: string; excerpt?: string }
const sleep = (ms: number) => new Promise(r => setTimeout(r, ms))
async function fetchJson(url: string): Promise<Fetched> {
  let reason = ''
  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      const res = await fetch(url, { headers: { 'User-Agent': USER_AGENT, Accept: 'application/json' }, signal: AbortSignal.timeout(30000) })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const text = await res.text()
      const sha256 = createHash('sha256').update(text).digest('hex')
      writeFileSync(resolve(archiveDir, `${sha256}.json`), text)
      return { url, checkedAt: new Date().toISOString(), status: 'ok', sha256, body: JSON.parse(text) }
    } catch (error) { reason = error instanceof Error ? error.message : String(error); await sleep(1000) }
  }
  return { url, checkedAt: new Date().toISOString(), status: 'failed', reason }
}

async function main() {
  mkdirSync(archiveDir, { recursive: true })
  const ids = derivedCertifiedIds()
  if (JSON.stringify(ids) !== JSON.stringify([...contract.supplierIds].sort())) throw new Error(`Certified contract supplier set differs from the derived set: ${ids.join(',')}`)
  const previousPath = generated('certifiedCoverage.json')
  const previous = existsSync(previousPath) ? JSON.parse(readFileSync(previousPath, 'utf8')) : { fields: [] }
  const { windowEnd } = JSON.parse(readFileSync(generated('filingRun.json'), 'utf8')) as { windowEnd: string }
  const { windowStart } = eventWindow(windowEnd)
  const today = new Date().toISOString().slice(0, 10)

  const sourceChecks: Omit<Fetched, 'body'>[] = []
  const fields: Array<{ supplierId: string; field: string; status: string; checkedAt: string; sourceUrls: string[]; value: unknown; reason: string; retained: boolean }> = []
  const proofs: unknown[] = []
  let received = 0

  for (const [index, id] of ids.entries()) {
    if (index > 0) await sleep(INTERVAL_MS)
    const supplier = trackerSuppliers.find(s => s.id === id)!
    const reg = edgarRegistry.find(r => r.id === supplier.edgarId)!
    const facts = await fetchJson(`https://data.sec.gov/api/xbrl/companyfacts/CIK${reg.cik}.json`)
    await sleep(INTERVAL_MS)
    const subs = await fetchJson(`https://data.sec.gov/submissions/CIK${reg.cik}.json`)
    for (const f of [facts, subs]) { const { body: _body, ...rest } = f; sourceChecks.push(rest) }
    if (facts.status === 'ok' && subs.status === 'ok') received++
    const candidate = candidateFor(id, windowStart, windowEnd)
    const latest = candidate['revenue.latest'] as { periodEnd: string; releaseDate: string } | null
    const prior = candidate['revenue.prior'] as { periodEnd: string } | null

    for (const group of Object.keys(contract.groups)) {
      const value = candidate[group]
      const groupLeaves = leaves(group, value)
      let result: Result
      let sources: Fetched[] = [subs]
      if (facts.status !== 'ok' || subs.status !== 'ok') result = { ok: false, reason: `SEC source failed: ${facts.reason ?? ''} ${subs.reason ?? ''}`.trim() }
      else if (group === 'identity') result = verifyIdentity(subs.body, candidate.identity)
      else if (group === 'secEvents') {
        const events = value as Array<{ id: string; date: string; type: string; accessions: (string | null)[]; evidenceDates: (string | null)[] }>
        const unreadable = events.find(v => v.accessions.some(a => !a))
        const allEvents = windowEvents(id, windowStart, windowEnd).map(x => ({ date: x.e.date, type: x.e.type, accessions: x.accessions.filter(Boolean) }))
        result = unreadable ? { ok: false, reason: `${unreadable.id}: sec.gov source with no readable accession` }
          : verifySecEvents(subs.body, events, allEvents, windowStart, windowEnd, today)
      } else if (group === 'revenue.history') {
        result = verifyHistory(facts.body, reg.revenueConcepts, value); sources = [facts]
      } else {
        const isLatest = group === 'revenue.latest'
        result = verifyRevenuePeriod(facts.body, reg.revenueConcepts, value, { requireReleaseDate: isLatest })
        if (result.ok && isLatest && latest) { const r = verifyNotStale(facts.body, subs.body, reg.revenueConcepts, latest); if (!r.ok) result = r }
        if (result.ok && !isLatest && latest && prior) { const r = verifyPriorAdjacent(facts.body, reg.revenueConcepts, latest.periodEnd, prior.periodEnd); if (!r.ok) result = r }
        sources = [facts, subs]
      }
      if (result.ok && (!result.locator?.trim() || !result.excerpt?.trim())) result = { ok: false, reason: 'verifier returned no locator or excerpt' }
      const checkedAt = new Date().toISOString()
      for (const [field, leaf] of groupLeaves) {
        const prev = previous.fields.find((f: { supplierId: string; field: string }) => f.supplierId === id && f.field === field)
        const status = !result.ok ? 'failed' : prev && JSON.stringify(prev.value) === JSON.stringify(leaf) ? 'checked-no-change' : 'updated'
        fields.push({ supplierId: id, field, status, checkedAt, sourceUrls: [facts.url, subs.url], value: leaf, reason: result.ok ? 'Re-derived from primary SEC data.' : result.reason!, retained: !result.ok })
      }
      if (!result.ok) { console.log(`HOLD  ${id}.${group}: ${result.reason}`); continue }
      const values = groupLeaves.slice().sort(([a], [b]) => a.localeCompare(b))
      proofs.push({ key: `${id}.${group}`, verifiedAt: checkedAt, valueSha256: digest(values), result: 'verified-value',
        discovery: { url: subs.url, sha256: subs.sha256, checkedAt: subs.checkedAt, coveredThrough: subs.checkedAt, scope: 'company-or-parent' },
        evidence: sources.map(s => ({ url: s.url, sha256: s.sha256, checkedAt: s.checkedAt, method: 'structured-validation', locator: result.locator, excerpt: result.excerpt })) })
      console.log(`OK    ${id}.${group}`)
    }
  }

  const summary = Object.fromEntries(['updated', 'checked-no-change', 'failed'].map(s => [s, fields.filter(f => f.status === s).length]))
  const coverage = { contractVersion: contract.version, checkedAt: new Date().toISOString(), windowEnd, state: summary.failed === 0 ? 'complete' : 'incomplete',
    allSuppliersAttempted: true, supplierCount: ids.length, supplierChecksReceived: received, sourceChecks, fields, summary }
  writeFileSync(previousPath, JSON.stringify(coverage, null, 2) + '\n')
  writeFileSync(generated('certifiedVerification.json'), JSON.stringify({ contractVersion: contract.version, verifiedClaims: proofs }, null, 2) + '\n')
  console.log(JSON.stringify({ suppliers: ids.length, sourcesReceived: received, proofs: proofs.length, ...summary }))
}

main().catch(error => { console.error(error); process.exit(1) })
