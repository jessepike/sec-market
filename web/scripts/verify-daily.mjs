import { readFileSync, existsSync } from 'node:fs'
import { createHash } from 'node:crypto'
import { resolve } from 'node:path'
import { verifyProspectiveV2Migration } from './pipeline/daily_baseline_migration.mjs'
import { Q4_J, verifyQ4BaselineMigration } from './pipeline/daily_q4_baseline_migration.mjs'
import { rosterBaseFor } from './pipeline/roster_transition.mjs'

const canonical = x => Array.isArray(x) ? '[' + x.map(canonical).join(',') + ']' : x && typeof x === 'object' ? '{' + Object.keys(x).sort().map(k => JSON.stringify(k) + ':' + canonical(x[k])).join(',') + '}' : JSON.stringify(x)
const hash = x => createHash('sha256').update(canonical(x)).digest('hex')
const measure = 'daily_source_intake_v2'
const count = x => Number.isSafeInteger(x) && x >= 0
const object = x => x !== null && typeof x === 'object' && !Array.isArray(x)
const sameIds = (a, b) => Array.isArray(a) && Array.isArray(b) &&
  a.every(id => typeof id === 'string') && b.every(id => typeof id === 'string') &&
  new Set(a).size === a.length && new Set(b).size === b.length && a.length === b.length && a.every(id => b.includes(id))
const requireV2 = (condition, message) => { if (!condition) throw new Error('Daily v2 coverage ' + message) }

function verifySummary(summary, processing, uncollected) {
  const fields = ['inventoryDocuments', 'reviewedDocuments', 'pendingDocuments', 'heldDocuments',
    ...(processing ? ['changedDocuments', 'unknownDateDocuments'] : [])]
  requireV2(object(summary) && typeof summary.complete === 'boolean' && fields.every(k => count(summary[k])), 'review summary is invalid')
  requireV2(summary.reviewedDocuments + summary.pendingDocuments === summary.inventoryDocuments &&
    summary.heldDocuments <= summary.reviewedDocuments &&
    (!summary.complete || (summary.pendingDocuments === 0 && (!processing || summary.heldDocuments === 0))), 'review partitions differ')
  if (processing) requireV2(summary.changedDocuments + summary.unknownDateDocuments <= summary.inventoryDocuments, 'review classifications differ')
  // Present only under a history window; archived documents sit outside this inventory.
  if (processing) requireV2(['archivedDocuments', 'notAboutSupplierDocuments'].every(k => summary[k] === undefined || count(summary[k])) &&
    (summary.notAboutSupplierDocuments ?? 0) <= summary.reviewedDocuments, 'archive or exclusion counters are invalid')
  if (uncollected) requireV2(summary.evaluated === false && summary.status === 'uncollected' &&
    summary.complete === false && fields.every(k => summary[k] === 0), 'uncollected review claims measured work')
  else requireV2(summary.evaluated !== false && summary.status !== 'uncollected', 'collected review is marked uncollected')
  return fields
}

function verifyV2(contract, data, coverage, rows, required) {
  requireV2(contract.version === 'market-daily-v2' && contract.collection?.mode === 'daily_intake_with_separate_history' &&
    coverage.schemaVersion === 2 && coverage.measure === measure && object(coverage.intake), 'policy or measure differs')
  const intake = coverage.intake
  requireV2(typeof intake.evaluated === 'boolean' && typeof intake.complete === 'boolean' &&
    intake.measure === measure && count(coverage.successfulTasks) && count(coverage.requiredTasks) &&
    intake.successfulTasks === coverage.successfulTasks && intake.requiredTasks === required &&
    intake.complete === coverage.complete && sameIds(intake.gapTaskIds, coverage.gapTaskIds), 'intake aliases differ')
  const uncollected = intake.evaluated === false
  requireV2(intake.status === (uncollected ? 'uncollected' : 'collected'), 'intake evaluation status differs')
  const sourceMap = new Map(contract.sources.map(s => [s.id, s]))
  for (const row of rows) {
    const source = sourceMap.get(row.sourceId)
    requireV2(row.measure === measure && row.outcome === row.intakeOutcome && typeof row.required === 'boolean' &&
      typeof row.taskId === 'string' && row.taskId.length > 0 &&
      (source ? row.supplierId === source.supplierId && row.family === source.family &&
        row.required === source.required && row.registration === source.registration :
        row.sourceId === '' && row.registration === 'missing' && row.required === true &&
        contract.suppliers.some(s => s.id === row.supplierId && s.requiredFamilies.includes(row.family))), 'source identity or intake outcome differs')
    requireV2(['checked', 'not_checked', 'blocked', 'failed'].includes(row.outcome), 'unknown intake outcome')
  }
  const successes = rows.filter(r => r.required && r.outcome === 'checked')
  const gaps = rows.filter(r => r.required && r.outcome !== 'checked').map(r => r.taskId)
  requireV2(rows.filter(r => r.required).length === required && new Set(rows.map(r => r.taskId)).size === rows.length &&
    successes.every(r => r.registration === 'verified') && successes.length === coverage.successfulTasks &&
    sameIds(gaps, intake.gapTaskIds) && coverage.complete === (required > 0 && successes.length === required), 'completion differs from its source receipts')
  for (const kind of ['processing', 'historicalReview']) {
    const fields = verifySummary(coverage[kind], kind === 'processing', uncollected)
    for (const row of rows) verifySummary(row[kind], kind === 'processing', uncollected)
    requireV2(fields.every(field => coverage[kind][field] === rows.reduce((sum, row) => sum + row[kind][field], 0)) &&
      coverage[kind].complete === rows.every(row => row[kind].complete), 'aggregate review differs from sources')
  }
  if (uncollected) {
    const old = data.supersededPolicy
    if (old?.snapshot?.coverage?.schemaVersion === 2) {
      if (hash(contract) === Q4_J) verifyQ4BaselineMigration(data, contract, required)
      else verifyProspectiveV2Migration(data, contract, required)
      return
    }
    requireV2(coverage.successfulTasks === 0 && coverage.complete === false && coverage.validUntil === null &&
      rows.every(r => r.outcome === 'not_checked'), 'uncollected intake claims a check')
    requireV2(object(old) && object(old.contract) && object(old.snapshot) &&
      hash(old.contract) === old.contractSha256 && old.snapshot.contractSha256 === old.contractSha256 &&
      old.snapshot.snapshotSha256 === old.snapshotSha256, 'superseded policy or snapshot binding differs')
    const unsigned = { ...old.snapshot }; delete unsigned.snapshotSha256
    requireV2(hash(unsigned) === old.snapshotSha256 && old.snapshot.coverage?.schemaVersion !== 2 &&
      ['events', 'evidence', 'supplierUpdates'].every(field => canonical(data[field]) === canonical(old.snapshot[field])) &&
      data.checkedAt === old.snapshot.checkedAt && coverage.checkedAt === old.snapshot.coverage.checkedAt &&
      coverage.lastCollectionAt === old.snapshot.coverage.lastCollectionAt, 'uncollected migration changed historical facts or times')
  }
}

export function verifyDaily(web) {
  const path = resolve(web, 'src/data/generated/dailyMarket.json')
  if (!existsSync(path)) return { enabled: false } // Legacy release fixtures have no daily data module.
  const bytes = readFileSync(path), data = JSON.parse(bytes)
  if (data.schemaVersion !== 1 || typeof data.enabled !== 'boolean') throw new Error('Unsupported daily snapshot')
  if (!data.enabled) {
    if (data.events.length || data.evidence.length || Object.keys(data.supplierUpdates).length) throw new Error('Disabled daily snapshot contains changes')
    return { enabled: false }
  }
  const sealPath = path.replace(/\.json$/, '.seal.json')
  if (!existsSync(sealPath)) throw new Error('Daily snapshot seal missing')
  const seal = JSON.parse(readFileSync(sealPath, 'utf8'))
  const fileSha256 = createHash('sha256').update(bytes).digest('hex')
  if (seal.fileSha256 !== fileSha256 || seal.runId !== data.runId || seal.contractSha256 !== data.contractSha256) throw new Error('Daily snapshot differs from its validated seal')
  let contract = JSON.parse(readFileSync(resolve(web, '../contracts/market.json'), 'utf8'))
  // A snapshot from the base contract stays valid under its reviewed additive roster successor (D-138).
  if (hash(contract) !== data.contractSha256) contract = rosterBaseFor(web, contract, data.contractSha256) ?? contract
  if (createHash('sha256').update(canonical(contract)).digest('hex') !== data.contractSha256) throw new Error('Daily coverage contract changed')
  const ids = new Set(contract.suppliers.map(s => s.id))
  const coverage = data.coverage
  const rows = coverage?.sources
  const required = contract.sources.filter(s => s.required).length + contract.suppliers.reduce((total, supplier) => {
    const bound = new Set(contract.sources.filter(s => s.supplierId === supplier.id && s.required).map(s => s.family))
    return total + supplier.requiredFamilies.filter(f => !bound.has(f)).length
  }, 0)
  if (!coverage || coverage.runId !== data.runId || coverage.contractSha256 !== data.contractSha256 || coverage.supplierCount !== ids.size || coverage.requiredTasks !== required || !Array.isArray(rows)) throw new Error('Daily coverage denominator or provenance differs')
  if (contract.version === 'market-daily-v2' || contract.collection?.mode === 'daily_intake_with_separate_history' || coverage.schemaVersion === 2 || coverage.measure === measure) {
    verifyV2(contract, data, coverage, rows, required)
  } else {
    if (coverage.intake !== undefined || coverage.processing !== undefined || coverage.historicalReview !== undefined ||
      (coverage.schemaVersion !== undefined && coverage.schemaVersion !== 1)) throw new Error('Unsupported daily coverage measure')
    const successes = rows.filter(r => r.required && ['updated', 'checked_no_change'].includes(r.outcome))
    if (new Set(rows.map(r => r.taskId)).size !== rows.length || successes.some(r => r.registration !== 'verified') || successes.length !== coverage.successfulTasks || coverage.gapTaskIds.length !== required - successes.length || coverage.complete !== (required > 0 && successes.length === required)) throw new Error('Daily coverage completion differs from its source receipts')
  }
  if (!Number.isFinite(Date.parse(coverage.checkedAt)) || !Number.isFinite(Date.parse(coverage.lastCollectionAt)) || coverage.overdueHours !== contract.schedule.overdueHours) throw new Error('Daily coverage timestamps or freshness policy differ')
  const unsigned = { ...data }; delete unsigned.snapshotSha256
  if (createHash('sha256').update(canonical(unsigned)).digest('hex') !== data.snapshotSha256) throw new Error('Daily snapshot content address differs')
  const evidence = new Map(data.evidence.map(e => [e.id, e]))
  if (evidence.size !== data.evidence.length || new Set(data.events.map(e => e.id)).size !== data.events.length) throw new Error('Duplicate daily record identity')
  for (const event of data.events) {
    if (!ids.has(event.supplierId) || ![1, 2, 3, 4].includes(event.rung) || !event.evidenceIds.length || event.evidenceIds.some(id => !evidence.has(id))) throw new Error('Daily event has unsupported provenance')
    for (const id of event.evidenceIds) if (!evidence.get(id).excerpt.includes(event.text)) throw new Error('Daily statement differs from supported source excerpt')
  }
  for (const [id, patch] of Object.entries(data.supplierUpdates)) {
    if (!ids.has(id) || Object.keys(patch).some(k => k !== 'headlineMetric' && k !== 'lastRound')) throw new Error('Unsupported daily supplier patch')
    for (const field of Object.values(patch)) if (!field.evidenceIds.length || field.evidenceIds.some(id => !evidence.has(id))) throw new Error('Daily supplier value lacks evidence')
  }
  return { enabled: true, runId: data.runId, fileSha256, snapshotSha256: data.snapshotSha256, contractSha256: data.contractSha256, coverageComplete: data.coverage.complete,
    ...(coverage.schemaVersion === 2 ? { coverageMeasure: measure, intakeComplete: coverage.intake.complete,
      processingComplete: coverage.processing.complete, historicalReviewComplete: coverage.historicalReview.complete } : {}) }
}

if (process.argv[1]?.endsWith('/verify-daily.mjs')) {
  try { console.log(JSON.stringify(verifyDaily(process.cwd()))) }
  catch (error) { console.error(error.message); process.exitCode = 2 }
}
