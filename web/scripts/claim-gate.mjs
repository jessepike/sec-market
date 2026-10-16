// The claim gate (D-85, D-100). Given a fixed contract of supplier x claim
// groups, a coverage receipt and per-claim proofs, it counts a claim as
// verified only when it carries a source URL, a content hash, a fresh check
// time and a structured-validation proof. Used by certify-sec.ts (digest) and
// certify-gate.ts (evaluateRefresh). A run is complete only at 100%.
import { createHash } from 'node:crypto'

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
