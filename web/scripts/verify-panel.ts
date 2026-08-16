import { createHash } from 'node:crypto'
import { exportCanonicalDerivedPayload } from '../src/data/panelIntegrity.ts'

const write = process.argv.includes('--write')
const payload = exportCanonicalDerivedPayload()
const sha256 = createHash('sha256').update(payload).digest('hex')

if (write) {
  console.log('SHA-256:', sha256)
  console.log('Canonical payload length:', payload.length)
  console.log('Update EXPECTED_DERIVED_PANEL_JSON in panelIntegrity.ts if values changed.')
  process.exit(0)
}

// Import expected by re-reading module is circular; verify length and hash match known good
const EXPECTED_SHA = 'cd7070458d4511b95f6ca433ad34cdb8488d44c67b6c8eb61a982fb760e0d1f2'

if (sha256 !== EXPECTED_SHA) {
  console.error('Panel integrity check FAILED')
  console.error('Expected SHA-256:', EXPECTED_SHA)
  console.error('Actual SHA-256:  ', sha256)
  process.exit(1)
}

console.log('Panel integrity check passed (SHA-256:', sha256, ')')
