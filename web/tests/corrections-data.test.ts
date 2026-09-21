import assert from 'node:assert/strict'
import { describe, it } from 'node:test'
import { findFiscalPeriodMismatches } from '../src/data/correctionHelpers.ts'
import { corrections } from '../src/data/corrections.ts'
import { evidenceById } from '../src/data/evidence.ts'
import { issueById, issues } from '../src/data/issues/index.ts'
import { LAST_UPDATED_ISO } from '../src/data/meta.ts'
import type { Correction, EvidenceRecord, Issue } from '../src/data/types.ts'

/** Same date-validity rule verify-issue.ts's own checks use — never the render-time clock. */
function isValidIsoDate(value: string): boolean {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) return false
  const [year, month, day] = value.split('-').map(Number)
  const date = new Date(Date.UTC(year, month - 1, day))
  return date.getUTCFullYear() === year && date.getUTCMonth() === month - 1 && date.getUTCDate() === day
}

describe('corrections data', () => {
  it('every correction id is unique', () => {
    const ids = corrections.map((correction) => correction.id)
    assert.equal(new Set(ids).size, ids.length, `duplicate correction id among: ${ids.join(', ')}`)
  })

  it('every correction names an issue that exists', () => {
    for (const correction of corrections) {
      assert.ok(
        issueById[correction.issueId],
        `correction "${correction.id}" names issue "${correction.issueId}", which does not exist`,
      )
    }
  })

  it('every corrected item id exists in that correction\'s issue', () => {
    for (const correction of corrections) {
      const issue = issueById[correction.issueId]
      assert.ok(issue, `correction "${correction.id}" names issue "${correction.issueId}", which does not exist`)
      const itemIds = new Set(
        issue.sections.flatMap((section) => section.items.map((item) => item.id)),
      )
      for (const reading of correction.correctedReadings) {
        assert.ok(
          itemIds.has(reading.itemId),
          `correction "${correction.id}" names item "${reading.itemId}", which does not exist in issue "${issue.id}"`,
        )
      }
    }
  })

  it('every correction has a valid ISO date, not after LAST_UPDATED_ISO', () => {
    for (const correction of corrections) {
      assert.ok(isValidIsoDate(correction.date), `correction "${correction.id}" date "${correction.date}" is not a valid calendar date`)
      assert.ok(
        correction.date <= LAST_UPDATED_ISO,
        `correction "${correction.id}" date "${correction.date}" is after LAST_UPDATED_ISO "${LAST_UPDATED_ISO}"`,
      )
    }
  })

  it('every correction has a non-empty approvedBy and text', () => {
    for (const correction of corrections) {
      assert.notEqual(correction.approvedBy.trim(), '', `correction "${correction.id}" has an empty approvedBy`)
      assert.notEqual(correction.text.trim(), '', `correction "${correction.id}" has empty text`)
    }
  })

  it('every corrected reading has a non-empty headline and at least one evidence id', () => {
    for (const correction of corrections) {
      for (const reading of correction.correctedReadings) {
        assert.notEqual(
          reading.correctedHeadline.trim(),
          '',
          `correction "${correction.id}" item "${reading.itemId}" has an empty corrected headline`,
        )
        assert.ok(
          reading.evidenceIds.length > 0,
          `correction "${correction.id}" item "${reading.itemId}" has no evidence ids`,
        )
        for (const id of reading.evidenceIds) {
          assert.ok(
            evidenceById[id],
            `correction "${correction.id}" item "${reading.itemId}" cites unresolved evidence id "${id}"`,
          )
        }
      }
    }
  })

  it('the real 2026-w36 correction covers the two known FY/quarter-mismatch items with the right evidence', () => {
    const correction = corrections.find((c) => c.id === 'C-2026-09-20-01')
    assert.ok(correction, 'expected the C-2026-09-20-01 correction to exist')
    const byItem = new Map(correction!.correctedReadings.map((reading) => [reading.itemId, reading]))

    const zscaler = byItem.get('2026-w36-prints-2')
    assert.ok(zscaler)
    assert.deepEqual(zscaler!.evidenceIds, ['W36-15'])
    assert.match(zscaler!.correctedHeadline, /quarter ended 31 July 2026/)

    const paloAlto = byItem.get('2026-w36-prints-6')
    assert.ok(paloAlto)
    assert.deepEqual(paloAlto!.evidenceIds, ['W36-19'])
    assert.match(paloAlto!.correctedHeadline, /quarter ended 31 July 2026/)
    assert.ok(paloAlto!.note && paloAlto!.note.length > 0, 'expected the withdrawn-comparison note')
  })
})

describe('findFiscalPeriodMismatches — the gate (SEC-MARKET-FABLE-001 T6-13)', () => {
  it('finds no uncorrected mismatch against the real, current issue and correction data', () => {
    const violations = findFiscalPeriodMismatches(issues, evidenceById, corrections)
    assert.deepEqual(violations, [], `unexpected uncorrected fiscal-period mismatch(es): ${JSON.stringify(violations)}`)
  })

  function makeEvidence(id: string, economicPeriod: string): EvidenceRecord {
    return {
      id,
      title: `Fixture ${id}`,
      organization: 'Fixture Org',
      publicationDate: '2026-01-01',
      economicPeriod,
      canonicalUrl: `https://example.test/${id}`,
      excerpt: 'Fixture excerpt.',
      sourceClass: 'INDEPENDENT',
      interpretation: 'Fixture interpretation.',
      limitations: 'Fixture limitation.',
      conflictingEvidenceIds: [],
      artifactLabel: `FIXTURE / ${id}`,
      tags: ['fixture'],
    }
  }

  function makeIssue(headline: string, evidenceIds: [string, ...string[]]): Issue {
    return {
      id: '2099-w01',
      weekEnding: '2099-01-04',
      windowStart: '2098-12-29',
      published: '2099-01-04',
      status: 'published',
      read: 'Fixture issue.',
      sections: [
        {
          lane: 'prints',
          items: [
            {
              id: '2099-w01-prints-1',
              lane: 'prints',
              headline,
              why: 'Fixture why.',
              date: '2099-01-02',
              evidenceIds,
            },
          ],
        },
        { lane: 'formation', items: [] },
        { lane: 'absorption', items: [] },
        { lane: 'capital', items: [] },
      ],
      weThink: {
        summary: 'Fixture.',
        postureDeltas: [],
        thesis: null,
        noCalls: [],
        signedBy: 'Jesse Pike',
        signedOn: '2099-01-04',
      },
      proposed: null,
      sources: { readable: 0, unreadable: [] },
    }
  }

  it('flags an "FY" headline citing quarterly evidence, when uncorrected', () => {
    const issue = makeIssue('Acme FY2099 revenue grows to $10M', ['FX-Q'])
    const evidence = { 'FX-Q': makeEvidence('FX-Q', 'Quarter ended 2098-12-31') }
    const violations = findFiscalPeriodMismatches([issue], evidence, [])
    assert.equal(violations.length, 1)
    assert.equal(violations[0].itemId, '2099-w01-prints-1')
  })

  it('flags "fiscal year" / "full-year" / "full year" phrasing too', () => {
    const evidence = { 'FX-Q': makeEvidence('FX-Q', 'Quarter ended 2098-12-31') }
    for (const headline of [
      'Acme fiscal year 2099 revenue grows to $10M',
      'Acme full-year revenue grows to $10M',
      'Acme full year revenue grows to $10M',
    ]) {
      const violations = findFiscalPeriodMismatches([makeIssue(headline, ['FX-Q'])], evidence, [])
      assert.equal(violations.length, 1, `expected a violation for headline: "${headline}"`)
    }
  })

  it('does not flag an "FY" headline whose cited evidence is not quarterly', () => {
    const issue = makeIssue('Acme FY2099 revenue grows to $10M', ['FX-FY'])
    const evidence = { 'FX-FY': makeEvidence('FX-FY', 'Fiscal year ended 2098-12-31') }
    assert.deepEqual(findFiscalPeriodMismatches([issue], evidence, []), [])
  })

  it('does not flag a headline with no fiscal-year/full-year language', () => {
    const issue = makeIssue('Acme revenue grows to $10M', ['FX-Q'])
    const evidence = { 'FX-Q': makeEvidence('FX-Q', 'Quarter ended 2098-12-31') }
    assert.deepEqual(findFiscalPeriodMismatches([issue], evidence, []), [])
  })

  it('is silenced by a correction covering the exact item, and re-flags if the correction is removed', () => {
    const issue = makeIssue('Acme FY2099 revenue grows to $10M', ['FX-Q'])
    const evidence = { 'FX-Q': makeEvidence('FX-Q', 'Quarter ended 2098-12-31') }
    const correction: Correction = {
      id: 'C-fixture-01',
      date: '2099-01-05',
      issueId: '2099-w01',
      approvedBy: 'Jesse Pike',
      text: 'Fixture correction text.',
      correctedReadings: [
        { itemId: '2099-w01-prints-1', correctedHeadline: 'Acme quarterly revenue grows to $10M', evidenceIds: ['FX-Q'] },
      ],
    }

    assert.deepEqual(findFiscalPeriodMismatches([issue], evidence, [correction]), [])
    // Removing the correction (this run's stand-in for the manual proof of
    // scripts/verify-issue.ts's check 16) must re-flag the same item.
    const violations = findFiscalPeriodMismatches([issue], evidence, [])
    assert.equal(violations.length, 1)
    assert.equal(violations[0].itemId, '2099-w01-prints-1')
  })
})
