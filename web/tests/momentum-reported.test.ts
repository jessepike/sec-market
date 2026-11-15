import assert from 'node:assert/strict'
import { test } from 'node:test'
import { domainMomentum, parseGrowth, parseUsd } from '../src/data/tracker/momentum'
import { isCertifiedSupplier } from '../src/data/tracker/certification'

test('company-reported growth and revenue text parse, and anything else is refused', () => {
  assert.equal(parseGrowth('+6.4%'), 6.4)
  assert.equal(parseGrowth('-1.1%'), -1.1)
  assert.equal(parseGrowth('+13%'), 13)
  assert.equal(parseGrowth('about 10%'), null)
  assert.equal(parseUsd('$1,122.0 million'), 1_122_000_000)
  assert.equal(parseUsd('$2.1 billion'), 2_100_000_000)
  assert.equal(parseUsd('¥74.6 billion'), null)
})

test('company-reported rows are public, never certified, never in a median, and never listed twice', () => {
  for (const d of domainMomentum()) {
    for (const r of d.reported) {
      assert.equal(r.supplier.kind, 'public', r.supplier.id)
      assert.equal(isCertifiedSupplier(r.supplier.id), false, r.supplier.id)
      assert.ok(d.rows.length > 0 && d.revenueBars, `${d.id} draws reported rows only beside SEC filers`)
      assert.ok(!d.others.some(o => o.supplier.id === r.supplier.id), `${r.supplier.id} also listed as text in ${d.id}`)
    }
    const values = d.rows.map(r => r.latest).sort((a, b) => a - b)
    if (d.median !== null && values.length % 2) assert.equal(d.median, values[(values.length - 1) / 2], `${d.id} median uses SEC filers only`)
  }
  assert.ok(domainMomentum().some(d => d.reported.length > 0), 'at least one domain shows company-reported growth')
})
