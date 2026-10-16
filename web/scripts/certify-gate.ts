// Gate for the certified tier (SEC-MARKET-AUTO-002-P0). Before evaluating
// proofs it re-derives every certified claim from the build inputs
// (trackerSuppliers, events, evidence, edgarFacts) and refuses if any value
// differs from what was certified: a value changed after certification never
// passes (audit fix 1). It also refuses placeholder locators or excerpts.
// Exits 0 only when every required claim passed.
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs'
import { resolve } from 'node:path'
import { evaluateRefresh } from './refresh-publication-gate.mjs'
import { allCandidateLeaves, derivedCertifiedIds } from './sec-verify/candidates'

const read = (path: string) => JSON.parse(readFileSync(resolve(path), 'utf8'))
const contract = read('src/data/tracker/certifiedContract.json')
const coverage = read('src/data/generated/certifiedCoverage.json')
const verification = read('src/data/generated/certifiedVerification.json')
const drift: string[] = []

if (JSON.stringify(derivedCertifiedIds()) !== JSON.stringify([...contract.supplierIds].sort())) drift.push('certified supplier set differs from the derived set')
const built = allCandidateLeaves(Object.keys(contract.groups), coverage.windowEnd)
const certified = new Map((coverage.fields as Array<{ supplierId: string; field: string; value: unknown }>).map(f => [`${f.supplierId}|${f.field}`, JSON.stringify(f.value)]))
for (const leaf of built) {
  const key = `${leaf.supplierId}|${leaf.field}`
  const now = JSON.stringify(JSON.parse(JSON.stringify(leaf.value ?? null)))
  if (!certified.has(key)) drift.push(`${key}: displayed but never certified`)
  else if (certified.get(key) !== now) drift.push(`${key}: build value differs from certified value`)
}
for (const key of certified.keys()) if (!built.some(l => `${l.supplierId}|${l.field}` === key)) drift.push(`${key}: certified but no longer displayed`)
const placeholders = new Set(['', 'checked.', 'sec submissions index'])
for (const p of verification.verifiedClaims as Array<{ key: string; evidence: Array<{ locator?: string; excerpt?: string }> }>)
  if (p.evidence.some(e => placeholders.has((e.locator ?? '').trim().toLowerCase()) || placeholders.has((e.excerpt ?? '').trim().toLowerCase()))) drift.push(`${p.key}: placeholder locator or excerpt`)

const result = evaluateRefresh(contract, coverage, verification)
const complete = result.complete && drift.length === 0
const receipt = { schemaVersion: 1, contractVersion: contract.version, attemptedAt: coverage.checkedAt, evaluatedAt: new Date().toISOString(), ...result, complete, drift }
mkdirSync(resolve('..', '.collect'), { recursive: true })
writeFileSync(resolve('..', '.collect/certified-attempt.json'), JSON.stringify(receipt, null, 2) + '\n')
console.log(JSON.stringify({ complete, required: result.required, verified: result.verified, blockers: result.failures.length, drift: drift.length }))
for (const f of [...drift, ...result.failures].slice(0, 40)) console.log('  ' + f)
process.exitCode = complete ? 0 : 2
