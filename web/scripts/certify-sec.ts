// Certified-tier runner (SEC-MARKET-AUTO-002-P0). Builds the candidate claims
// the site would display for each SEC filer, fetches primary SEC sources, asks
// the independent verifier (sec-verify/independent.mjs) to prove each claim,
// and writes coverage plus proofs in the exact shape evaluateRefresh checks.
// A claim that fails verification gets no proof, so the gate holds the run.
//
// Run: npm run certify:sec   (then npm run certify:gate)
import { createHash } from 'node:crypto'
import { existsSync, readFileSync, writeFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { edgarRegistry } from '../src/data/edgarRegistry'
import { trackerSuppliers } from '../src/data/tracker/suppliers'
import { retainedTrackerEvents } from '../src/data/tracker/events'
import { evidenceById } from '../src/data/evidence'
import { digest } from './refresh-publication-gate.mjs'
import { accessionFromUrl, verifyIdentity, verifyNotStale, verifyRevenuePeriod, verifySecEvents } from './sec-verify/independent.mjs'

const USER_AGENT = process.env.SMP_SEC_USER_AGENT ?? 'SecurityMarketPulse research jesse@keatingpike.com'
const INTERVAL_MS = 250
const generated = (name: string) => resolve('src/data/generated', name)
const contract = JSON.parse(readFileSync(resolve('src/data/tracker/certifiedContract.json'), 'utf8'))

/** The certified set is derived, never hand-set: tracker suppliers with structured SEC revenue. */
export function derivedCertifiedIds(): string[] {
  const registry = new Set(edgarRegistry.map(r => r.id))
  return trackerSuppliers.filter(s => s.edgarId && registry.has(s.edgarId)).map(s => s.id).sort()
}

interface Fetched { url: string; checkedAt: string; status: 'ok' | 'failed'; sha256?: string; body?: unknown; reason?: string }
const sleep = (ms: number) => new Promise(r => setTimeout(r, ms))
async function fetchJson(url: string): Promise<Fetched> {
  let reason = ''
  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      const res = await fetch(url, { headers: { 'User-Agent': USER_AGENT, Accept: 'application/json' }, signal: AbortSignal.timeout(30000) })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const text = await res.text()
      return { url, checkedAt: new Date().toISOString(), status: 'ok', sha256: createHash('sha256').update(text).digest('hex'), body: JSON.parse(text) }
    } catch (error) { reason = error instanceof Error ? error.message : String(error); await sleep(1000) }
  }
  return { url, checkedAt: new Date().toISOString(), status: 'failed', reason }
}

type Leaf = [string, unknown]
const leaves = (group: string, value: unknown): Leaf[] => value && typeof value === 'object' && !Array.isArray(value)
  ? Object.entries(value as Record<string, unknown>).filter(([k]) => k !== 'evidenceIds').map(([k, v]) => [`${group}.${k}`, v] as Leaf)
  : [[group, value]]

async function main() {
  const ids = derivedCertifiedIds()
  if (JSON.stringify(ids) !== JSON.stringify([...contract.supplierIds].sort())) throw new Error(`Certified contract supplier set differs from the derived set: ${ids.join(',')}`)
  const previousPath = generated('certifiedCoverage.json')
  const previous = existsSync(previousPath) ? JSON.parse(readFileSync(previousPath, 'utf8')) : { fields: [] }
  const filingRun = JSON.parse(readFileSync(generated('filingRun.json'), 'utf8')) as { windowEnd: string }
  const windowEnd = filingRun.windowEnd
  const windowStart = new Date(Date.parse(windowEnd + 'T00:00:00Z') - 365 * 86400000).toISOString().slice(0, 10)
  const today = new Date().toISOString().slice(0, 10)
  // Certified SEC events use the SEC filing run's own window, not the site's
  // collector-bounded window (runStatus.lastChecked). Phase 2 renders this window.
  const inWindow = retainedTrackerEvents.filter(e => e.date >= windowStart && e.date <= windowEnd)

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

    const secEventsFor = inWindow.filter(e => e.supplierId === id).map(e => ({ e, urls: e.evidenceIds.map(x => evidenceById[x]?.canonicalUrl ?? '') }))
      .filter(({ urls }) => urls.some(u => u.includes('sec.gov')))
    const candidate: Record<string, unknown> = {
      identity: { name: supplier.name, ticker: supplier.ticker ?? null, kind: supplier.kind },
      'revenue.latest': supplier.revenue?.latest ?? null,
      'revenue.prior': supplier.revenue?.prior ?? null,
      secEvents: secEventsFor.map(({ e, urls }) => ({ date: e.date, type: e.type, accessions: urls.filter(u => u.includes('sec.gov')).map(accessionFromUrl) }))
        .sort((a, b) => (a.date + a.accessions.join()).localeCompare(b.date + b.accessions.join())),
    }

    for (const group of Object.keys(contract.groups)) {
      const value = candidate[group]
      const groupLeaves = leaves(group, value)
      let result: { ok: boolean; reason?: string; locator?: string; excerpt?: string }
      let evidenceSource: Fetched[] = []
      if (facts.status !== 'ok' || subs.status !== 'ok') result = { ok: false, reason: `SEC source failed: ${facts.reason ?? ''} ${subs.reason ?? ''}`.trim() }
      else if (group === 'identity') { result = verifyIdentity(subs.body, candidate.identity); evidenceSource = [subs] }
      else if (group === 'secEvents') {
        const allDates = inWindow.filter(e => e.supplierId === id).map(e => e.date)
        const events = value as Array<{ date: string; accessions: (string | null)[] }>
        const unreadable = events.find(v => v.accessions.some(a => !a))
        result = unreadable ? { ok: false, reason: `event ${unreadable.date} has an sec.gov source with no readable accession` }
          : verifySecEvents(subs.body, events as Array<{ date: string; accessions: string[] }>, allDates, windowStart, windowEnd, today)
        evidenceSource = [subs]
      } else {
        const isLatest = group === 'revenue.latest'
        result = verifyRevenuePeriod(facts.body, reg.revenueConcepts, value, { requireReleaseDate: isLatest })
        if (result.ok && isLatest) {
          const fresh = verifyNotStale(facts.body, subs.body, reg.revenueConcepts, value as { periodEnd: string; releaseDate: string })
          if (!fresh.ok) result = fresh
        }
        evidenceSource = [facts, subs]
      }
      const checkedAt = new Date().toISOString()
      for (const [field, leaf] of groupLeaves) {
        const prior = previous.fields.find((f: { supplierId: string; field: string }) => f.supplierId === id && f.field === field)
        const status = !result.ok ? 'failed' : prior && JSON.stringify(prior.value) === JSON.stringify(leaf) ? 'checked-no-change' : 'updated'
        fields.push({ supplierId: id, field, status, checkedAt, sourceUrls: [facts.url, subs.url], value: leaf, reason: result.ok ? 'Independently re-derived from primary SEC data.' : result.reason!, retained: !result.ok })
      }
      if (!result.ok) { console.log(`HOLD  ${id}.${group}: ${result.reason}`); continue }
      const values = groupLeaves.slice().sort(([a], [b]) => a.localeCompare(b))
      proofs.push({ key: `${id}.${group}`, verifiedAt: checkedAt, valueSha256: digest(values), result: 'verified-value',
        discovery: { url: subs.url, sha256: subs.sha256, checkedAt: subs.checkedAt, coveredThrough: subs.checkedAt, scope: 'company-or-parent' },
        evidence: evidenceSource.map(s => ({ url: s.url, sha256: s.sha256, checkedAt: s.checkedAt, method: 'structured-validation', locator: result.locator ?? 'SEC submissions index', excerpt: result.excerpt ?? 'Checked.' })) })
      console.log(`OK    ${id}.${group}`)
    }
  }

  const summary = Object.fromEntries(['updated', 'checked-no-change', 'failed'].map(s => [s, fields.filter(f => f.status === s).length]))
  const coverage = { contractVersion: contract.version, checkedAt: new Date().toISOString(), state: summary.failed === 0 ? 'complete' : 'incomplete',
    allSuppliersAttempted: true, supplierCount: ids.length, supplierChecksReceived: received, sourceChecks, fields, summary }
  writeFileSync(previousPath, JSON.stringify(coverage, null, 2) + '\n')
  writeFileSync(generated('certifiedVerification.json'), JSON.stringify({ contractVersion: contract.version, verifiedClaims: proofs }, null, 2) + '\n')
  console.log(JSON.stringify({ suppliers: ids.length, sourcesReceived: received, proofs: proofs.length, ...summary }))
}

main().catch(error => { console.error(error); process.exit(1) })
