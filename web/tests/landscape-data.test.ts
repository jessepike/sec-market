import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { describe, it } from 'node:test'
import { fileURLToPath } from 'node:url'
import { evidenceById } from '../src/data/evidence.ts'
import { landscapeDomains, trackedPrintEvidenceIds } from '../src/data/domains.ts'
import { hypotheses } from '../src/data/hypotheses.ts'
import { allPressureRows, platformPressure } from '../src/data/platformPressure.ts'
import type { Provenance } from '../src/data/types.ts'

const here = dirname(fileURLToPath(import.meta.url))

function evidenceIdsFrom(provenance: Provenance): string[] {
  return provenance.evidenceIds
}

function collectNewEvidenceIds(): string[] {
  const ids = new Set<string>()
  for (const row of allPressureRows()) {
    for (const id of evidenceIdsFrom(row.provenance.print)) ids.add(id)
    for (const id of evidenceIdsFrom(row.provenance.read)) ids.add(id)
  }
  for (const hypothesis of hypotheses) {
    for (const id of hypothesis.evidenceIds) ids.add(id)
    for (const id of hypothesis.provenance.evidenceIds) ids.add(id)
  }
  return [...ids]
}

describe('landscape data provenance', () => {
  it('resolves every evidence id used by the new datasets', () => {
    const ids = collectNewEvidenceIds()
    assert.ok(ids.length > 0, 'expected landscape data to reference evidence')
    const missing = ids.filter((id) => !evidenceById[id])
    assert.deepEqual(missing, [], `unresolved evidence ids: ${missing.join(', ')}`)
  })

  it('gives every tracked print claim a non-empty evidence tuple', () => {
    for (const row of allPressureRows()) {
      const print = row.provenance.print
      assert.equal(print.layer, 'tracked')
      if (print.layer === 'tracked') {
        assert.ok(print.evidenceIds.length > 0, `${row.id} tracked print has no evidence`)
      }
    }
  })

  it('keeps figures out of platformPressure.ts', () => {
    const source = readFileSync(resolve(here, '../src/data/platformPressure.ts'), 'utf8')
    assert.doesNotMatch(source, /%/)
    assert.doesNotMatch(source, /\$/)
  })

  it('labels landscape TRACKED chips from the prints on the card', () => {
    const cloud = landscapeDomains.find((domain) => domain.id === 'cloud-security')
    assert.ok(cloud)
    const ids = trackedPrintEvidenceIds(cloud)
    assert.ok(ids.includes('C13'), 'Falcon Cloud print is missing')
    assert.equal(
      ids.includes('D5a'),
      false,
      'Wiz/Alphabet close must not label the Cloud card prints',
    )
    for (const domain of landscapeDomains) {
      assert.ok(trackedPrintEvidenceIds(domain).length > 0, domain.id)
    }
  })

  it('derives one row per pressure group from sourced records', () => {
    assert.ok(platformPressure.holding.length > 0)
    assert.ok(platformPressure['buying-in'].length > 0)
    assert.ok(platformPressure.outrun.length > 0)
    assert.ok(platformPressure.challengers.length > 0)
  })
})
