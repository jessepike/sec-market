import { readFileSync, writeFileSync } from 'node:fs'
import { resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import { runGate } from './refresh-publication-gate.mjs'

const repo = resolve(dirname(fileURLToPath(import.meta.url)), '../..')
const result = runGate(repo)
if (!result.complete) throw new Error('100% substantive verification required; public complete-refresh date retained.')
const path = resolve(repo, 'web/src/data/generated/refreshPublication.json')
const previous = JSON.parse(readFileSync(path, 'utf8'))
const next = { ...previous, lastCompleteRefreshAt: result.attemptedAt, lastAttemptAt: result.attemptedAt, lastAttemptState: 'complete',
  verificationContract: result.contractVersion, coverage: { required: result.required, verified: result.verified, excluded: result.excluded },
  note: 'Every required logical claim passed the contract. App deployment is recorded separately after release.' }
writeFileSync(path, JSON.stringify(next, null, 2) + '\n')
