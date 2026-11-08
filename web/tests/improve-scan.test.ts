import assert from 'node:assert/strict'
import { test } from 'node:test'
import { scan } from '../scripts/improve/scan'

const queue = (names: string[]) =>
  `<!-- company-requests:${JSON.stringify(names.map(name => ({ name, count: 1, first: '2026-11-06' })))}-->`

test('the scorecard lists gaps with a question, a fix class and their items', () => {
  const { gaps } = scan()
  assert.ok(gaps.length > 0)
  for (const g of gaps) {
    assert.ok(['growth', 'peers', 'health', 'freshness', 'coverage'].includes(g.question), g.id)
    assert.ok(['data', 'coverage', 'feature'].includes(g.fix), g.id)
    assert.equal(g.count, g.items.length, g.id)
    assert.ok(g.count > 0, g.id)
  }
})

test('company requests drop names the site already tracks and keep new ones', () => {
  const { requests } = scan(queue(['Cyera', 'Some New Company']))
  assert.deepEqual(requests.map(r => r.name), ['Some New Company'])
})

test('a queue without the marker yields no requests', () => {
  assert.deepEqual(scan('no marker here').requests, [])
})
