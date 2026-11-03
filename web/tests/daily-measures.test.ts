import assert from 'node:assert/strict'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { test } from 'node:test'
import { DailyCollectionStatus } from '../src/components/RunStatus'
import { readDailyCoverage, dailyOverdue, type DailyCoverage } from '../src/data/tracker/daily'
import { intakeReviewFixture } from './fixtures/daily-coverage-v2'

function render(coverage: DailyCoverage) {
  return renderToStaticMarkup(createElement(DailyCollectionStatus, { coverage }))
}

test('complete intake cannot hide pending processing, held claims or historical work', () => {
  const coverage = readDailyCoverage(structuredClone(intakeReviewFixture))!
  const html = render(coverage)
  assert.match(html, /Daily source intake: 557 of 557 checked; complete/)
  assert.match(html, /Document processing \(incomplete\): 20 of 100 reviewed; 80 pending, 3 held/)
  assert.match(html, /6 changed, 4 dates unknown/)
  assert.match(html, /Historical review \(incomplete\): 200 of 9900 reviewed; 9700 pending, 12 held/)
  assert.match(html, /Document processing \(incomplete\)/)
  assert.match(html, /Historical review \(incomplete\)/)
  assert.match(html, /Source intake does not mean every current event or historical claim has been reviewed/)
  assert.match(html, /run-status__line--incomplete/)
  assert.doesNotMatch(html, /run-status__line--updated/)
})

test('intake freshness still uses the original source deadline independently of review counts', () => {
  assert.equal(dailyOverdue(intakeReviewFixture, Date.parse('2026-10-25T09:00:00Z')), false)
  assert.equal(dailyOverdue(intakeReviewFixture, Date.parse('2026-10-25T10:00:00Z')), true)
})

test('legacy coverage keeps its combined meaning and existing reader wording', () => {
  const { schemaVersion: _schema, measure: _measure, intake: _intake, processing: _processing,
    historicalReview: _history, ...legacy } = intakeReviewFixture
  const html = render(readDailyCoverage({ ...legacy, complete: false, successfulTasks: 244 })!)
  assert.match(html, /Latest recorded collection/)
  assert.match(html, /244 of 557 required source checks completed/)
  assert.match(html, /Coverage is incomplete/)
  assert.doesNotMatch(html, /Daily source intake:|Document processing:|Historical review:/)
})

test('v2 rejects missing measures, inconsistent aliases, impossible progress and downgrade fallback', () => {
  const mutations: Array<(value: Record<string, any>) => void> = [
    value => { delete value.processing }, value => { delete value.historicalReview },
    value => { delete value.intake }, value => { value.measure = 'unknown' },
    value => { value.schemaVersion = 3 }, value => { value.schemaVersion = 1 },
    value => { value.intake.successfulTasks = 244 }, value => { value.intake.measure = 'legacy' },
    value => { value.processing.complete = true }, value => { value.processing.pendingDocuments = 79 },
    value => { value.processing.heldDocuments = 21 }, value => { value.processing.unknownDateDocuments = -1 },
    value => { value.processing.changedDocuments = true }, value => { value.historicalReview.complete = true },
    value => { value.complete = false }, value => { value.intake.evaluated = false; value.intake.status = 'uncollected' },
  ]
  for (const mutate of mutations) {
    const value = structuredClone(intakeReviewFixture)
    mutate(value)
    assert.throws(() => readDailyCoverage(value), /Daily coverage schema or measure/)
  }
})

test('reviewed historical holds stay visible even when its inventory review is complete', () => {
  const value = structuredClone(intakeReviewFixture)
  value.processing = { ...value.processing, complete: true, pendingDocuments: 0, reviewedDocuments: 100, heldDocuments: 0 }
  value.historicalReview = { ...value.historicalReview, complete: true, pendingDocuments: 0, reviewedDocuments: 9900 }
  const html = render(readDailyCoverage(value)!)
  assert.match(html, /Historical review \(complete\): 9900 of 9900 reviewed; 0 pending, 12 held/)
  assert.match(html, /run-status__line--incomplete/)
})

test('schema 2 without a measure cannot fall back to legacy labels', () => {
  const value: Record<string, unknown> = { ...intakeReviewFixture }
  delete value.measure
  assert.throws(() => readDailyCoverage(value), /Daily coverage schema or measure/)
})

test('duplicate top-level gaps cannot silently replace an unmatched intake gap', () => {
  const value = structuredClone(intakeReviewFixture)
  value.successfulTasks = value.intake.successfulTasks = 555
  value.complete = value.intake.complete = false
  value.intake.gapTaskIds = ['missing-a', 'missing-b']
  value.gapTaskIds = ['missing-a', 'missing-a']
  assert.throws(() => readDailyCoverage(value), /Daily coverage schema or measure/)
})

test('uncollected new-policy data never presents zero of zero as reviewed or renews an old collection time', () => {
  const value = structuredClone(intakeReviewFixture)
  value.complete = value.intake.complete = false
  value.successfulTasks = value.intake.successfulTasks = 0
  value.gapTaskIds = value.intake.gapTaskIds = Array.from({ length: 557 }, (_, i) => `uncollected-${i}`)
  value.intake.evaluated = false
  value.intake.status = 'uncollected'
  value.validUntil = null
  value.processing = { complete: false, evaluated: false, status: 'uncollected', inventoryDocuments: 0,
    reviewedDocuments: 0, pendingDocuments: 0, heldDocuments: 0, changedDocuments: 0, unknownDateDocuments: 0 }
  value.historicalReview = { complete: false, evaluated: false, status: 'uncollected', inventoryDocuments: 0,
    reviewedDocuments: 0, pendingDocuments: 0, heldDocuments: 0 }
  const html = render(readDailyCoverage(value)!)
  assert.match(html, /Source intake has not yet been collected under this policy. Earlier recorded collection:/)
  assert.match(html, /Daily source intake: not yet collected \(0 of 557\)/)
  assert.match(html, /Document processing: not evaluated; pending, held and unknown-date counts unmeasured/)
  assert.match(html, /Historical review: not evaluated; pending and held counts unmeasured/)
  assert.doesNotMatch(html, /0 of 0|Latest recorded source intake:/)
})

test('collected empty inventory does not imply zero of zero documents reviewed', () => {
  const value = structuredClone(intakeReviewFixture)
  value.processing = { complete: true, inventoryDocuments: 0, reviewedDocuments: 0, pendingDocuments: 0,
    heldDocuments: 0, changedDocuments: 0, unknownDateDocuments: 0 }
  value.historicalReview = { complete: true, inventoryDocuments: 0, reviewedDocuments: 0, pendingDocuments: 0, heldDocuments: 0 }
  const html = render(readDailyCoverage(value)!)
  assert.match(html, /Document processing \(complete\): no documents observed/)
  assert.match(html, /Historical review \(complete\): no documents observed/)
  assert.doesNotMatch(html, /0 of 0 reviewed/)
})

test('archive counters are accepted, validated and add no wording to the processing line', () => {
  const plain = render(readDailyCoverage(structuredClone(intakeReviewFixture))!)
  const value = structuredClone(intakeReviewFixture)
  value.processing = { ...value.processing, archivedDocuments: 11000, notAboutSupplierDocuments: 2 }
  assert.equal(render(readDailyCoverage(value)!), plain)
  for (const mutate of [
    (v: Record<string, any>) => { v.processing.archivedDocuments = -1 },
    (v: Record<string, any>) => { v.processing.notAboutSupplierDocuments = 21 },
    (v: Record<string, any>) => { v.processing.archivedDocuments = '5' },
  ]) {
    const bad = structuredClone(intakeReviewFixture) as Record<string, any>
    bad.processing = { ...bad.processing, archivedDocuments: 1, notAboutSupplierDocuments: 1 }
    mutate(bad)
    assert.throws(() => readDailyCoverage(bad), /Daily coverage schema or measure/)
  }
})
