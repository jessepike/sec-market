import { test } from 'node:test'
import assert from 'node:assert/strict'
import { dailyOverdue, type DailyCoverage } from '../src/data/tracker/daily'

const coverage: DailyCoverage = { checkedAt: '2026-10-20T18:00:00Z', lastCollectionAt: '2026-10-20T12:00:00Z',
  validUntil: '2026-10-21T18:00:00Z', overdueHours: 30, requiredTasks: 557, successfulTasks: 557, complete: true, automationEnabled: true }

test('a later governance check does not extend the oldest source deadline', () => {
  assert.equal(dailyOverdue(coverage, Date.parse('2026-10-21T17:00:00Z')), false)
  assert.equal(dailyOverdue(coverage, Date.parse('2026-10-21T19:00:00Z')), true)
})
test('missing or future coverage cannot look current', () => {
  assert.equal(dailyOverdue({ ...coverage, validUntil: null }, Date.parse('2026-10-20T19:00:00Z')), true)
  assert.equal(dailyOverdue(coverage, Date.parse('2026-10-19T19:00:00Z')), true)
})
