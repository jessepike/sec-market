// Compares the certified claim values in a new certifiedCoverage.json with a
// baseline copy (the one committed on preview). Timestamps, hashes and proof
// dates always change between runs; only claim values decide whether a commit
// is worth making (D-96: publish only when something changed).
//
// Usage: node scripts/certify-changed.mjs <baseline.json> <current.json>
// Prints `changed=true|false` (for $GITHUB_OUTPUT) and one line per change.
import { readFileSync, existsSync } from 'node:fs'

export function changedClaims(baseline, current) {
  const key = f => `${f.supplierId}|${f.field}`
  const before = new Map((baseline?.fields ?? []).map(f => [key(f), JSON.stringify(f.value)]))
  const after = new Map((current?.fields ?? []).map(f => [key(f), JSON.stringify(f.value)]))
  const changes = []
  for (const [k, v] of after) if (before.get(k) !== v) changes.push(`${before.has(k) ? 'changed' : 'added'} ${k}`)
  for (const k of before.keys()) if (!after.has(k)) changes.push(`removed ${k}`)
  return changes
}

if (process.argv[1] && import.meta.url.endsWith(process.argv[1].split('/').pop())) {
  const [baselinePath, currentPath] = process.argv.slice(2)
  const baseline = existsSync(baselinePath) ? JSON.parse(readFileSync(baselinePath, 'utf8')) : null
  const current = JSON.parse(readFileSync(currentPath, 'utf8'))
  const changes = changedClaims(baseline, current)
  console.log(`changed=${changes.length > 0}`)
  for (const c of changes) console.error(c)
}
