import { createHash } from 'node:crypto'
import { editions } from '../src/data/edition.ts'

/** Frozen append-only edition history — update only when appending a new edition. */
const EXPECTED_EDITIONS_SHA =
  'c3f8646e46d34588be5eb27d090873e81cfca29172b5cdf95d1f0dd7db1d3d1e'

const payload = JSON.stringify(editions)
const sha256 = createHash('sha256').update(payload).digest('hex')

if (process.argv.includes('--write')) {
  console.log('SHA-256:', sha256)
  console.log('Edition count:', editions.length)
  console.log('Update EXPECTED_EDITIONS_SHA in scripts/verify-edition.ts when appending editions.')
  process.exit(0)
}

if (EXPECTED_EDITIONS_SHA === 'PLACEHOLDER') {
  console.error('Edition integrity check FAILED: EXPECTED_EDITIONS_SHA is unset.')
  console.error('Run: npm run verify:edition -- --write')
  process.exit(1)
}

if (sha256 !== EXPECTED_EDITIONS_SHA) {
  console.error('Edition integrity check FAILED')
  console.error('Expected SHA-256:', EXPECTED_EDITIONS_SHA)
  console.error('Actual SHA-256:  ', sha256)
  process.exit(1)
}

console.log('Edition integrity check passed (SHA-256:', sha256, ')')
