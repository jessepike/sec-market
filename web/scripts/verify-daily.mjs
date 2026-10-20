import { readFileSync, existsSync } from 'node:fs'
import { createHash } from 'node:crypto'
import { resolve } from 'node:path'

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
  const canonical = x => Array.isArray(x) ? '[' + x.map(canonical).join(',') + ']' : x && typeof x === 'object' ? '{' + Object.keys(x).sort().map(k => JSON.stringify(k) + ':' + canonical(x[k])).join(',') + '}' : JSON.stringify(x)
  const contract = JSON.parse(readFileSync(resolve(web, '../contracts/market.json'), 'utf8'))
  if (createHash('sha256').update(canonical(contract)).digest('hex') !== data.contractSha256) throw new Error('Daily coverage contract changed')
  const ids = new Set(contract.suppliers.map(s => s.id))
  const coverage = data.coverage
  const rows = coverage?.sources
  const required = contract.sources.filter(s => s.required).length + contract.suppliers.reduce((total, supplier) => {
    const bound = new Set(contract.sources.filter(s => s.supplierId === supplier.id && s.required).map(s => s.family))
    return total + supplier.requiredFamilies.filter(f => !bound.has(f)).length
  }, 0)
  if (!coverage || coverage.runId !== data.runId || coverage.contractSha256 !== data.contractSha256 || coverage.supplierCount !== ids.size || coverage.requiredTasks !== required || !Array.isArray(rows)) throw new Error('Daily coverage denominator or provenance differs')
  const successes = rows.filter(r => r.required && ['updated', 'checked_no_change'].includes(r.outcome))
  if (new Set(rows.map(r => r.taskId)).size !== rows.length || successes.some(r => r.registration !== 'verified') || successes.length !== coverage.successfulTasks || coverage.gapTaskIds.length !== required - successes.length || coverage.complete !== (required > 0 && successes.length === required)) throw new Error('Daily coverage completion differs from its source receipts')
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
  return { enabled: true, runId: data.runId, fileSha256, snapshotSha256: data.snapshotSha256, contractSha256: data.contractSha256, coverageComplete: data.coverage.complete }
}

if (process.argv[1]?.endsWith('/verify-daily.mjs')) {
  try { console.log(JSON.stringify(verifyDaily(process.cwd()))) }
  catch (error) { console.error(error.message); process.exitCode = 2 }
}
