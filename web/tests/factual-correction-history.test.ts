import assert from 'node:assert/strict'
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { describe, it } from 'node:test'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { Corrections } from '../src/components/Corrections.tsx'
import { corrections } from '../src/data/corrections.ts'
import { correctionsJsonPayload } from '../src/data/correctionHelpers.ts'
import { factualCorrectionFeedText, factualCorrectionHistory, publicCorrectionsJsonPayload } from '../src/data/factualCorrectionHelpers.ts'
import { SITE_URL } from '../src/data/meta.ts'
import type { EvidenceRecord } from '../src/data/types.ts'
import type { FactualCorrectionBundle, FactualCorrectionGroup } from '../src/data/tracker/factualCorrections.ts'
import { projectEvents } from '../src/data/tracker/factualCorrections.ts'
import type { TrackerEvent } from '../src/data/tracker/events.ts'
import type { TrackerSupplier } from '../src/data/tracker/suppliers.ts'
import { buildFeedXml, writeCorrectionsJson, writeFactualCorrectionsJson, writeFeedXml } from '../scripts/generate-feed.ts'
import { checkCorrectionsJsonExists, checkFactualCorrectionsJsonExists, checkFeedXmlExistsAndParses, report } from '../scripts/verify-dist.ts'

// Synthetic responses exercise presentation mechanics; they confer no semantic admission.
const evidence: EvidenceRecord = {
  id: 'SYN-1', title: 'Source <title> & "report"', organization: 'Fixture',
  publicationDate: '2026-10-20', economicPeriod: '2026', canonicalUrl: 'https://example.test/report?a=1&b=2',
  excerpt: 'A source excerpt.', sourceClass: 'OFFICIAL', interpretation: '', limitations: '',
  conflictingEvidenceIds: [], artifactLabel: 'Synthetic', tags: [],
}
const event: TrackerEvent = { id: 'EV-fixture', supplierId: 'fixture', type: 'funding', date: '2026-10-20', text: 'Old <value> & "amount"', evidenceIds: [evidence.id], rung: 1 }
const suppliers: TrackerSupplier[] = [{ id: 'fixture', name: 'Fixture & Company', kind: 'private', domainIds: ['fixture'] }]
const sources = { evidence: { [evidence.id]: evidence }, suppliers }
const admission = { candidateSha256: 'b'.repeat(64), evidenceSetSha256: 'c'.repeat(64), policySha256: 'a'.repeat(64), admittedAt: '2026-10-23T01:00:00Z', reviewSha256: 'd'.repeat(64), result: 'accepted' as const }
const globalInventoryPolicy = 'f'.repeat(64)
const replacement: FactualCorrectionGroup = {
  id: 'synthetic-replacement', supplierId: 'fixture', reasonCode: 'source-date', date: '2026-10-23',
  note: 'Synthetic correction <note> & "quoted".', admission,
  targets: [{ targetId: 'event:EV-fixture', operation: 'replace', original: event, originalSha256: 'e'.repeat(64), proposedValue: { ...event, date: '2026-10-19', text: 'Corrected <value> & "amount"' } }],
}
const withdrawal: FactualCorrectionGroup = {
  ...replacement, id: 'synthetic-withdrawal', reasonCode: 'duplicate-event',
  targets: [{ targetId: 'event:EV-fixture', operation: 'withdraw', original: event, originalSha256: 'e'.repeat(64), proposedValue: null }],
}
const bundle = (groups: FactualCorrectionGroup[]): FactualCorrectionBundle => ({ schemaVersion: 1, enabled: true, policySha256: globalInventoryPolicy, checkedAt: '2026-10-23T02:00:00Z', groups })
const disabled: FactualCorrectionBundle = { schemaVersion: 1, enabled: false, policySha256: null, checkedAt: null, groups: [] }

function temporary(fn: (dir: string) => void) {
  const dir = mkdtempSync(join(tmpdir(), 'factual-history-'))
  try { fn(dir) } finally { rmSync(dir, { recursive: true, force: true }) }
}

describe('factual correction history (synthetic, non-admitting)', () => {
  it('requires all eleven dist checks and reports a factual correction check failure', (context) => {
    context.mock.method(console, 'log', () => {})
    context.mock.method(console, 'error', () => {})
    const results = Array.from({ length: 10 }, (_, index) => ({ name: `existing-${index}`, pass: true }))
    const correctionCheck = { name: '11k factual-corrections-json-exists', pass: true }
    assert.throws(() => report(results), /expected 11 check results, got 10/)
    assert.equal(report([...results, correctionCheck]), false)
    assert.equal(report([...results, { ...correctionCheck, pass: false }]), true)
  })

  it('preserves legacy attribution, shape and default feed/JSON bytes when disabled', () => temporary((dir) => {
    const before = JSON.stringify(corrections)
    const payload = publicCorrectionsJsonPayload(corrections, disabled.groups, sources, SITE_URL)
    assert.deepEqual(payload, correctionsJsonPayload(corrections, SITE_URL))
    writeCorrectionsJson(corrections, dir, disabled.groups, sources)
    assert.equal(readFileSync(join(dir, 'corrections.json'), 'utf8'), JSON.stringify(correctionsJsonPayload(corrections, SITE_URL), null, 2))
    assert.equal(buildFeedXml([], corrections, disabled.groups, sources), buildFeedXml([], corrections))
    const html = renderToStaticMarkup(createElement(Corrections, { groups: [], sources }))
    assert.equal((html.match(/Approved by Jesse Pike/g) ?? []).length, corrections.length)
    assert.doesNotMatch(html, /Source-verified factual correction/)
    assert.equal(JSON.stringify(corrections), before)
  }))

  it('publishes named source notes, before/after links and hashes without owner attribution', () => {
    const before = JSON.stringify(corrections)
    const entries = factualCorrectionHistory([replacement], sources, SITE_URL)
    assert.equal(entries[0].supplierName, 'Fixture & Company')
    assert.equal(entries[0].sources[0].url, evidence.canonicalUrl)
    assert.match(entries[0].changes[0].before, /2026-10-20: Old/)
    assert.match(entries[0].changes[0].after, /2026-10-19: Corrected/)
    const html = renderToStaticMarkup(createElement(Corrections, { groups: [replacement], sources }))
    assert.match(html, /Fixture &amp; Company/)
    assert.match(html, /Before: 2026-10-20/)
    assert.match(html, /After: 2026-10-19/)
    assert.match(html, /href="https:\/\/example.test\/report\?a=1&amp;b=2"/)
    assert.match(html, new RegExp(admission.reviewSha256))
    assert.doesNotMatch(html, /<note>|<value>/)
    const factualHtml = html.slice(html.indexOf('id="synthetic-replacement"'), html.indexOf('id="C-'))
    assert.doesNotMatch(factualHtml, /Approved by/)
    const payload = publicCorrectionsJsonPayload(corrections, [replacement], sources, SITE_URL)
    assert.deepEqual(payload.filter((entry) => !('kind' in entry)), correctionsJsonPayload(corrections, SITE_URL))
    assert.equal(JSON.stringify(corrections), before)
  })

  it('shows withdrawal while projection retains the original event identity only once', () => {
    const retained = { ...event, id: 'EV-original', text: 'Original transaction.' }
    const projected = projectEvents({ events: [event, retained], suppliers, evidence: [evidence] }, bundle([withdrawal]), globalInventoryPolicy, { [withdrawal.id]: admission.policySha256 })
    assert.deepEqual(projected, [retained])
    assert.equal(event.text, 'Old <value> & "amount"')
    const entry = factualCorrectionHistory([withdrawal], sources, SITE_URL)[0]
    assert.equal(entry.changes[0].after, 'Withdrawn from the standing reference.')
    assert.equal(entry.sources[0].url, evidence.canonicalUrl)
  })

  it('links evidence metadata corrections directly and includes both event evidence sets', () => {
    const nextEvidence = { ...evidence, id: 'SYN-2', canonicalUrl: 'https://example.test/new' }
    const changed = structuredClone(replacement)
    const target = changed.targets[0]
    assert.equal(target.operation, 'replace')
    if (target.operation === 'replace' && 'evidenceIds' in target.proposedValue) target.proposedValue.evidenceIds = [nextEvidence.id]
    changed.targets.push({ targetId: 'evidence:SYN-1', operation: 'replace', original: evidence, originalSha256: 'f'.repeat(64), proposedValue: { ...evidence, publicationDate: '2026-10-19' } })
    const entry = factualCorrectionHistory([changed], { evidence: { ...sources.evidence, [nextEvidence.id]: nextEvidence }, suppliers }, SITE_URL)[0]
    assert.deepEqual(new Set(entry.sources.map((source) => source.url)), new Set([evidence.canonicalUrl, nextEvidence.canonicalUrl]))
    assert.match(entry.changes[1].before, /Publication date: 2026-10-20/)
    assert.match(entry.changes[1].after, /Publication date: 2026-10-19/)
    assert.throws(() => factualCorrectionHistory([replacement], { evidence: {}, suppliers }, SITE_URL), /unresolved source/)
  })

  it('publishes every bound primary source even when targets do not cite it', () => temporary((dir) => {
    const extras = [
      { ...evidence, id: 'TR-checkpoint-5', title: 'Synthetic original offering', canonicalUrl: 'https://example.test/original-offering' },
      { ...evidence, id: 'TR-zscaler-6', title: 'Synthetic second announcement', canonicalUrl: 'https://example.test/second-announcement' },
    ]
    const boundSources = {
      evidence: { ...sources.evidence, ...Object.fromEntries(extras.map((record) => [record.id, record])) },
      suppliers,
      groupEvidenceIds: { [replacement.id]: [evidence.id, ...extras.map((record) => record.id)] },
    }
    const entry = factualCorrectionHistory([replacement], boundSources, SITE_URL)[0]
    assert.deepEqual(new Set(entry.sources.map((record) => record.id)), new Set([evidence.id, ...extras.map((record) => record.id)]))
    const html = renderToStaticMarkup(createElement(Corrections, { groups: [replacement], sources: boundSources }))
    writeCorrectionsJson(corrections, dir, [replacement], boundSources)
    writeFeedXml([], corrections, dir, [replacement], boundSources)
    const json = JSON.parse(readFileSync(join(dir, 'corrections.json'), 'utf8'))
    const published = json.find((record: { id: string }) => record.id === replacement.id)
    const feed = readFileSync(join(dir, 'feed.xml'), 'utf8')
    for (const extra of extras) {
      assert.ok(html.includes(`href="${extra.canonicalUrl}"`))
      assert.ok(published.sources.some((source: { url: string }) => source.url === extra.canonicalUrl))
      assert.ok(feed.includes(extra.canonicalUrl))
      assert.ok(!replacement.targets.some((target) => JSON.stringify(target).includes(extra.id)))
    }
    assert.ok(checkCorrectionsJsonExists(dir, corrections, [replacement], boundSources).pass)
    assert.ok(checkFeedXmlExistsAndParses(dir, [], corrections, [replacement], boundSources).pass)
    assert.equal(checkCorrectionsJsonExists(dir, corrections, [replacement], sources).pass, false)
    assert.equal(checkFeedXmlExistsAndParses(dir, [], corrections, [replacement], sources).pass, false)
    assert.throws(() => factualCorrectionHistory([replacement], { ...boundSources, evidence: sources.evidence }, SITE_URL), /unresolved bound source TR-checkpoint-5/)
  }))

  it('writes consistent JSON and escaped feed, and rejects altered public bytes', () => temporary((dir) => {
    const groups = [replacement]
    const emitted = bundle(groups)
    writeCorrectionsJson(corrections, dir, groups, sources)
    writeFactualCorrectionsJson(emitted, dir)
    const detached = JSON.parse(readFileSync(join(dir, 'factual-corrections.json'), 'utf8'))
    assert.equal(detached.policySha256, globalInventoryPolicy)
    assert.equal(detached.groups[0].admission.policySha256, admission.policySha256)
    assert.notEqual(detached.policySha256, detached.groups[0].admission.policySha256)
    const feedResult = writeFeedXml([], corrections, dir, groups, sources)
    assert.equal(feedResult.itemCount, corrections.length + 1)
    assert.ok(checkCorrectionsJsonExists(dir, corrections, groups, sources).pass)
    assert.ok(checkFactualCorrectionsJsonExists(dir, emitted).pass)
    const feedCheck = checkFeedXmlExistsAndParses(dir, [], corrections, groups, sources)
    assert.ok(feedCheck.pass, feedCheck.detail)
    const xml = readFileSync(join(dir, 'feed.xml'), 'utf8')
    assert.match(xml, /&lt;note&gt; &amp; &quot;quoted&quot;/)
    assert.match(xml, /report\?a=1&amp;b=2/)
    assert.doesNotMatch(xml, /<note>|<value>/)
    const publicEntry = JSON.parse(readFileSync(join(dir, 'corrections.json'), 'utf8')).find((entry: { id: string }) => entry.id === replacement.id)
    assert.equal(publicEntry.kind, 'source_verified_factual_correction')
    assert.equal(publicEntry.approvedBy, undefined)
    assert.equal(publicEntry.note, groups[0].note)
    assert.equal(factualCorrectionFeedText(publicEntry), factualCorrectionFeedText(factualCorrectionHistory(groups, sources, SITE_URL)[0]))
    writeFileSync(join(dir, 'feed.xml'), xml.replace('Synthetic correction', 'Altered correction'))
    assert.equal(checkFeedXmlExistsAndParses(dir, [], corrections, groups, sources).pass, false)
    writeFileSync(join(dir, 'corrections.json'), '[]')
    assert.equal(checkCorrectionsJsonExists(dir, corrections, groups, sources).pass, false)
    writeFileSync(join(dir, 'factual-corrections.json'), JSON.stringify(disabled))
    assert.equal(checkFactualCorrectionsJsonExists(dir, emitted).pass, false)
  }))
})
