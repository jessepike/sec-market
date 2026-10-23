import assert from 'node:assert/strict'
import { test } from 'node:test'
import { evidenceById } from '../src/data/evidence.ts'
import { trackerEvents } from '../src/data/tracker/events.ts'
import { trackerSuppliers } from '../src/data/tracker/suppliers.ts'

test('Varonis acquisition agreement remains an announced transaction with its primary dated source', () => {
  const event = trackerEvents.find(event => event.id === 'EV-varonis-proofpoint-agreement')!
  assert.ok(event)
  assert.equal(event.date, '2026-10-15')
  assert.equal(event.type, 'acquisition')
  assert.match(event.text, /definitive agreement/)
  assert.match(event.text, /\$6\.3 billion/)
  assert.match(event.text, /\$49\.75 per share/)
  assert.match(event.text, /subject to shareholder and regulatory approvals/)
  assert.match(event.text, /separate companies until closing/)
  assert.doesNotMatch(event.text, /completed|has acquired/)
  const evidence = evidenceById[event.evidenceIds[0]]
  assert.equal(evidence.publicationDate, event.date)
  assert.equal(new URL(evidence.canonicalUrl).hostname, 'www.proofpoint.com')
  assert.match(evidence.retrieval!.sha256, /^[a-f0-9]{64}$/)
  const supplier = trackerSuppliers.find(supplier => supplier.id === 'varonis')!
  assert.equal(supplier.kind, 'public')
  assert.equal(supplier.ownership!.announced, event.date)
  assert.equal(supplier.ownership!.closed, undefined)
  assert.ok(supplier.ownership!.evidenceIds.includes(evidence.id))
})
