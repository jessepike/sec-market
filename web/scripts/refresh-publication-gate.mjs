import { createHash } from 'node:crypto'
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs'
import { resolve, dirname } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

export const digest = value => createHash('sha256').update(typeof value === 'string' ? value : JSON.stringify(value)).digest('hex')
const validTime = (time, now, hours) => Number.isFinite(Date.parse(time)) && Date.parse(time) <= now + 300000 && now - Date.parse(time) <= hours * 3600000
const sourceProof = (proof, now, hours) => proof && /^https?:\/\//.test(proof.url ?? '') && /^[a-f0-9]{64}$/.test(proof.sha256 ?? '') && validTime(proof.checkedAt, now, hours)

/** Fixed supplier/group inventory. Attempt timestamps and HTTP retrieval alone never pass. */
export function evaluateRefresh(contract, coverage, verification, now = Date.now()) {
  const failures = []
  const expected = contract.supplierIds.flatMap(id => Object.keys(contract.groups).map(group => ({ id, group, key: `${id}.${group}` })))
  const proofs = verification?.verifiedClaims ?? []
  if (verification?.contractVersion !== contract.version) failures.push('Verification contract version does not match.')
  if (!coverage?.allSuppliersAttempted || coverage.supplierCount !== contract.supplierIds.length || coverage.supplierChecksReceived !== contract.supplierIds.length) failures.push('Supplier attempt inventory is incomplete or changed.')
  let verified = 0, excluded = 0
  for (const { id, group, key } of expected) {
    const exclusion = contract.exclusions[key]
    if (exclusion && exclusion.reason && exclusion.reviewedAt) { excluded++; continue }
    const fields = (coverage?.fields ?? []).filter(f => f.supplierId === id && (f.field === group || f.field.startsWith(group + '.')))
    const matches = proofs.filter(p => p.key === key)
    const hours = contract.groups[group]
    const allowedUndisclosed = Boolean(contract.undisclosedAnswers[key]?.reason && contract.undisclosedAnswers[key]?.reviewedAt)
    const acceptedStatuses = allowedUndisclosed ? ['updated', 'checked-no-change', 'unavailable'] : ['updated', 'checked-no-change']
    const requiredFields = [...(contract.components?.[group] ?? []).map(component => `${group}.${component}`), ...(contract.pinnedFields?.[key] ?? [])]
    const wholeGroupUndisclosed = allowedUndisclosed && fields.length === 1 && fields[0].field === group && fields[0].status === 'unavailable'
    let reason
    if (!fields.length || fields.some(f => !acceptedStatuses.includes(f.status) || !Object.hasOwn(f, 'value'))) reason = 'missing, failed, undisclosed or unresolved required claim'
    else if (new Set(fields.map(f => f.field)).size !== fields.length || (!wholeGroupUndisclosed && requiredFields.some(name => !fields.some(f => f.field === name)))) reason = 'required claim component missing or duplicated; denominator cannot shrink'
    else if (matches.length !== 1) reason = 'one substantive verification proof is required'
    else {
      const proof = matches[0]
      const values = fields.map(f => [f.field, f.value]).sort(([a], [b]) => a.localeCompare(b))
      if (!validTime(proof.verifiedAt, now, hours) || proof.valueSha256 !== digest(values)) reason = 'verification is stale or does not cover the exact candidate values'
      else if (!sourceProof(proof.discovery, now, hours) || !validTime(proof.discovery.coveredThrough, now, hours) || proof.discovery.scope !== 'company-or-parent') reason = 'current discovery coverage is missing or stale'
      else if (!Array.isArray(proof.evidence) || !proof.evidence.length || proof.evidence.some(e => !sourceProof(e, now, hours) || !['primary-content-match', 'structured-validation'].includes(e.method) || !e.locator?.trim() || !e.excerpt?.trim())) reason = 'substantive primary evidence and locator are missing'
      else if (proof.result !== (fields.some(f => f.status === 'unavailable') ? 'verified-undisclosed' : 'verified-value')) reason = 'verification result does not answer the required claim'
    }
    if (reason) failures.push(`${key}: ${reason}`)
    else verified++
  }
  const required = expected.length - excluded
  return { contractVersion: contract.version, complete: required > 0 && verified === required && failures.length === 0, required, verified, excluded, failures }
}

export function publicationDecision(baseline, currentFiles, result) {
  const unchanged = Object.entries(baseline.files).every(([path, sha]) => currentFiles[path] === sha)
  return { allowed: unchanged || result.complete, refreshed: !unchanged && result.complete, baselineRetained: unchanged, lastCompleteRefreshAt: baseline.lastCompleteRefreshAt, reason: unchanged ? 'Legacy published snapshot retained; no new refresh claimed.' : result.complete ? 'Every required logical claim passed.' : 'Incomplete candidate held; published data and complete-refresh date must remain unchanged.' }
}

export function runGate(repo) {
  const read = path => JSON.parse(readFileSync(resolve(repo, path), 'utf8'))
  const contract = read('web/src/data/tracker/refreshContract.json')
  const baseline = read('web/src/data/tracker/publishedSnapshot.json')
  const coverage = read('web/src/data/generated/refreshCoverage.json')
  const verification = read('web/src/data/generated/refreshVerification.json')
  const result = evaluateRefresh(contract, coverage, verification)
  const publication = read('web/src/data/generated/refreshPublication.json')
  const currentFiles = Object.fromEntries(Object.keys(baseline.files).map(path => [path, existsSync(resolve(repo, path)) ? digest(readFileSync(resolve(repo, path), 'utf8')) : null]))
  const decision = publicationDecision(baseline, currentFiles, result)
  if (decision.refreshed && publication.lastCompleteRefreshAt !== coverage.checkedAt) {
    decision.allowed = false
    decision.reason = 'Complete candidate lacks its matching public data-refresh date; prepare the publication receipt first.'
  }
  if (publication.lastCompleteRefreshAt !== null && (!result.complete || publication.lastCompleteRefreshAt !== coverage.checkedAt)) {
    decision.allowed = false
    decision.refreshed = false
    decision.reason = 'Complete-refresh date lacks the matching 100% verification receipt.'
  }
  const changedFiles = Object.keys(baseline.files).filter(path => currentFiles[path] !== baseline.files[path])
  const receipt = { schemaVersion: 1, attemptedAt: coverage.checkedAt, evaluatedAt: new Date().toISOString(), ...result, ...decision, changedFiles,
    notification: { id: digest({ attempt: coverage.checkedAt, candidate: currentFiles }), kind: decision.refreshed ? 'data-updated' : decision.allowed ? 'no-data-update' : 'refresh-blocked', date: coverage.checkedAt, completeRefreshAt: decision.refreshed ? coverage.checkedAt : baseline.lastCompleteRefreshAt,
      deliveryState: 'pending-parent-delivery', confirmation: 'A prepared candidate is not a deployment. Deliver data-updated only after the exact candidate is Ready and its public receipt matches.',
      details: { changedFiles, candidateChanges: (coverage.fields ?? []).filter(f => f.status === 'updated').map(f => ({ supplierId: f.supplierId, field: f.field, value: f.value, reportingPeriod: f.period ?? null, reason: f.reason, sourceUrls: f.sourceUrls })), required: result.required, verified: result.verified, excluded: result.excluded, blockers: result.failures } },
    candidateFileHashes: currentFiles, previousPublishedRevision: baseline.sourceRevision }
  mkdirSync(resolve(repo, '.collect'), { recursive: true })
  writeFileSync(resolve(repo, '.collect/refresh-attempt.json'), JSON.stringify(receipt, null, 2) + '\n')
  console.log(JSON.stringify({ allowed: decision.allowed, refreshed: decision.refreshed, required: result.required, verified: result.verified, excluded: result.excluded, blockerCount: result.failures.length, reason: decision.reason }))
  return receipt
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  try { process.exitCode = runGate(resolve(dirname(fileURLToPath(import.meta.url)), '../..')).allowed ? 0 : 2 }
  catch (error) { console.error(`Refresh publication refused: ${error.message}`); process.exitCode = 2 }
}
