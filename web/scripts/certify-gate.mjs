// Gate for the certified tier (SEC-MARKET-AUTO-002-P0). Same evaluateRefresh
// as the v1 path, given the certified contract, coverage and proofs.
// Exits 0 only when every required claim passed.
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs'
import { resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import { evaluateRefresh } from './refresh-publication-gate.mjs'

const repo = resolve(dirname(fileURLToPath(import.meta.url)), '../..')
const read = path => JSON.parse(readFileSync(resolve(repo, path), 'utf8'))
const contract = read('web/src/data/tracker/certifiedContract.json')
const coverage = read('web/src/data/generated/certifiedCoverage.json')
const verification = read('web/src/data/generated/certifiedVerification.json')
const result = evaluateRefresh(contract, coverage, verification)
const receipt = { schemaVersion: 1, contractVersion: contract.version, attemptedAt: coverage.checkedAt, evaluatedAt: new Date().toISOString(), ...result }
mkdirSync(resolve(repo, '.collect'), { recursive: true })
writeFileSync(resolve(repo, '.collect/certified-attempt.json'), JSON.stringify(receipt, null, 2) + '\n')
console.log(JSON.stringify({ complete: result.complete, required: result.required, verified: result.verified, blockers: result.failures.length }))
for (const f of result.failures.slice(0, 40)) console.log('  ' + f)
process.exitCode = result.complete ? 0 : 2
