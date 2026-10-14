import { existsSync, readFileSync, writeFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { trackerSuppliers } from '../src/data/tracker/suppliers'
import { trackerEvents } from '../src/data/tracker/events'
import { evidenceById } from '../src/data/evidence'
import edgarFacts from '../src/data/generated/edgarFacts.json' with { type: 'json' }
import { supportedFieldStatus, requiredFieldGroups, validateSupplierChecks, verifyClaimSources } from '../src/data/tracker/coverage'
import type { FieldCheck, FieldStatus, RefreshCoverage, SourceCheck, SupplierCheck } from '../src/data/tracker/coverage'
import { evaluateRefresh } from './refresh-publication-gate.mjs'

const repo = resolve('..')
const checksPath = resolve(repo, '.collect/supplier-checks.json')
const checks: SupplierCheck[] = existsSync(checksPath) ? JSON.parse(readFileSync(checksPath, 'utf8')) : []
validateSupplierChecks(checks, trackerSuppliers.map(s => s.id))
const sourceFile = process.env.SMP_SOURCE_CHECKS ?? resolve(repo, '.collect/source-bodies/source-checks.json')
const sourceChecks: SourceCheck[] = existsSync(sourceFile) ? JSON.parse(readFileSync(sourceFile, 'utf8')) : []
const edgar = edgarFacts as unknown as { checks?: Array<{ supplierId: string; checkedAt: string; url: string; status: string; sha256?: string; reason?: string }> }
const fields: FieldCheck[] = []
const unsafeChangedGroups: string[] = []
const baselinePath = resolve(repo, '.collect/baseline-suppliers.json')
const baseline = existsSync(baselinePath) ? JSON.parse(readFileSync(baselinePath, 'utf8')) as typeof trackerSuppliers : []
const allSources = [...sourceChecks, ...checks.flatMap(c => c.sourceChecks), ...(edgar.checks ?? []).map(c => ({ ...c, status: c.status === 'checked' ? 'ok' as const : 'failed' as const }))]

for (const supplier of trackerSuppliers) {
  const receipt = checks.find(c => c.supplierId === supplier.id)
  for (const field of requiredFieldGroups) {
    const value = field === 'identity' ? { name: supplier.name, ticker: supplier.ticker ?? null, kind: supplier.kind }
      : field === 'events' ? trackerEvents.filter(e => e.supplierId === supplier.id)
      : field === 'revenue.latest' ? supplier.revenue?.latest ?? null : field === 'revenue.prior' ? supplier.revenue?.prior ?? null
      : supplier[field as 'headlineMetric' | 'lastRound' | 'ownership'] ?? null
    const observed = receipt?.fields.find(f => f.field === field)
    const sec = field.startsWith('revenue.') && supplier.edgarId ? edgar.checks?.find(c => c.supplierId === supplier.edgarId) : undefined
    let status = supportedFieldStatus(observed, receipt?.sourceChecks ?? [])
    let urls = observed?.sourceUrls ?? []
    let at: string | null = receipt?.checkedAt ?? null
    let reason = observed?.reason ?? 'No per-field source-check receipt. Retained value is not claimed current.'
    const evidenceIds = value && typeof value === 'object' && 'evidenceIds' in value ? (value.evidenceIds as string[]) : []
    const supporting = evidenceIds.map(id => evidenceById[id]?.canonicalUrl).filter(Boolean)
    const missingProof = verifyClaimSources(observed, receipt?.sourceChecks ?? [], supporting)
    if (!sec && missingProof) { status = 'not-checked'; reason = missingProof }
    if (sec) {
      status = sec.status === 'checked' ? value === null ? 'unavailable' : 'checked-no-change' : 'failed'
      urls = [sec.url]; at = sec.checkedAt; reason = sec.status === 'checked' ? 'Structured SEC facts checked; exact filed period and comparable growth feed the displayed field.' : sec.reason ?? 'SEC source failed; previous claim retained.'
      const structured = edgarFacts.suppliers.find(s => s.id === supplier.edgarId)
      if (sec.status === 'checked' && field === 'revenue.latest' && !structured?.latest && value !== null) {
        status = 'failed'; reason = 'SEC source was retrieved but no validated latest quarter could replace the retained claim.'
      }
    }
    if (status === 'not-applicable' && value !== null && !sec) {
      status = 'not-checked'; reason = 'A populated live field cannot be excluded from verification; previous claim retained.'
    }
    const previous = baseline.find(s => s.id === supplier.id)
    const old = field === 'identity' ? previous ? { name: previous.name, ticker: previous.ticker ?? null, kind: previous.kind } : null
        : field === 'revenue.latest' ? previous?.revenue?.latest ?? null : field === 'revenue.prior' ? previous?.revenue?.prior ?? null
        : previous?.[field as 'headlineMetric' | 'lastRound' | 'ownership'] ?? null
    const factual = (v: unknown): string => JSON.stringify(v && typeof v === 'object' && !Array.isArray(v) ? Object.fromEntries(Object.entries(v).filter(([key]) => key !== 'evidenceIds').sort(([a], [b]) => a.localeCompare(b))) : v)
    if (previous && field !== 'events' && ['failed', 'not-checked'].includes(status) && factual(old) !== factual(value)) unsafeChangedGroups.push(`${supplier.id}.${field}`)
    // Include each atomic displayed/contract property under its independently checked field group.
    const leaves = value && typeof value === 'object' && !Array.isArray(value) ? Object.entries(value).filter(([key]) => key !== 'evidenceIds').map(([key, v]) => [field + '.' + key, v] as const) : [[field, value] as const]
    for (const [name, leaf] of leaves) {
      let leafStatus = status
      if (previous && field !== 'events' && ['updated', 'checked-no-change'].includes(status)) {
        const priorLeaf = old && typeof old === 'object' && !Array.isArray(old) ? (old as Record<string, unknown>)[name.slice(field.length + 1)] : old
        leafStatus = factual(priorLeaf) === factual(leaf) ? 'checked-no-change' : 'updated'
      }
      fields.push({ supplierId: supplier.id, field: name, status: leafStatus, checkedAt: at,
      sourceUrls: [...new Set([...urls, ...(observed?.discoverySourceUrls ?? []), ...supporting])], value: leaf, period: value && typeof value === 'object' && 'period' in value ? String(value.period) : undefined,
      reason, retained: status === 'failed' || status === 'not-checked' })
    }

  }
  fields.push({ supplierId: supplier.id, field: 'configured.domainIds', status: 'configured', checkedAt: null, sourceUrls: [], value: supplier.domainIds, reason: 'Declared editorial coverage; not a refreshed supplier disclosure.', retained: true })
}
const statuses: FieldStatus[] = ['updated', 'checked-no-change', 'unavailable', 'failed', 'not-checked', 'not-applicable', 'configured']
const summary = Object.fromEntries(statuses.map(status => [status, fields.filter(f => f.status === status).length])) as Record<FieldStatus, number>
const allSuppliersAttempted = trackerSuppliers.every(s => checks.some(c => c.supplierId === s.id))
const coverage: RefreshCoverage = { checkedAt: new Date().toISOString(), state: allSuppliersAttempted && summary.failed === 0 && summary['not-checked'] === 0 ? 'complete' : 'incomplete',
  allSuppliersAttempted, supplierCount: trackerSuppliers.length, supplierChecksReceived: checks.length, sourceChecks: allSources, fields, summary,
  schedule: { enabled: process.env.SMP_NIGHTLY_ENABLED === '1', timezone: 'America/Los_Angeles', time: '02:00', blocker: process.env.SMP_NIGHTLY_ENABLED === '1' ? null : 'Workflow installation, safe production-deployment skip and a dedicated hosted collector credential require owner action.' } }
const contract = JSON.parse(readFileSync(resolve('src/data/tracker/refreshContract.json'), 'utf8'))
const verification = JSON.parse(readFileSync(resolve('src/data/generated/refreshVerification.json'), 'utf8'))
const logical = evaluateRefresh(contract, coverage, verification)
coverage.state = logical.complete ? 'complete' : 'incomplete'
writeFileSync(resolve('src/data/generated/refreshCoverage.json'), JSON.stringify(coverage, null, 2) + '\n')
console.log(JSON.stringify({ ...summary, supplierChecksReceived: checks.length, expectedSuppliers: trackerSuppliers.length, allSuppliersAttempted }))
if (process.env.SMP_REQUIRE_ALL_ATTEMPTS === '1' && (!allSuppliersAttempted || summary['not-checked'] > 0)) process.exitCode = 2
if (process.env.SMP_REQUIRE_COMPLETE === '1' && !logical.complete) {
  console.error(`Complete refresh required: ${logical.verified}/${logical.required} logical claims certified; incomplete candidate held.`)
  process.exitCode = 2
}
if (unsafeChangedGroups.length) {
  console.error(`Unverified factual changes refused: ${unsafeChangedGroups.join(', ')}`)
  process.exitCode = 3
}
