import assert from 'node:assert/strict'
import { mkdtempSync, readFileSync, readdirSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { describe, it } from 'node:test'
import { buildReleaseRecord, parseResultsRelease, type ReleaseQuarter } from '../src/data/sixKLogic.ts'
import { refreshReleases } from '../scripts/release-refresh.ts'

// Raw Check Point 6-K results releases saved from EDGAR on 2026-11-06
// (tests/fixtures/sec-6k). No network: fetch is replaced with these bytes.
const dir = join(dirname(fileURLToPath(import.meta.url)), 'fixtures/sec-6k')
const doc = (accession: string) => readFileSync(join(dir, readdirSync(dir).find(f => f.startsWith(accession) && f.endsWith('.htm'))!), 'latin1')

const M = 1_000_000
const expected: Record<string, [string, number, number]> = {
  '0001178913-25-003565': ['2025-09-30', 677.5 * M, 635.1 * M],
  '0001178913-26-000437': ['2025-12-31', 744.9 * M, 703.7 * M],
  '0001178913-26-002310': ['2026-03-31', 668.4 * M, 637.8 * M],
  '0001178913-26-003696': ['2026-06-30', 673.6 * M, 665.2 * M],
  '0001178913-26-004953': ['2026-09-30', 669.8 * M, 677.5 * M],
}

describe('6-K results release parser', () => {
  for (const [accession, [periodEnd, value, priorYearValue]] of Object.entries(expected)) {
    it(`reads Total revenues from ${accession}`, () => {
      assert.deepEqual(parseResultsRelease(doc(accession)), { periodEnd, value, priorYearValue })
    })
  }

  it('refuses a document with no income statement', () => {
    assert.throws(() => parseResultsRelease('<html><body><p>Notice of annual general meeting</p></body></html>'))
  })

  it('refuses a statement not stated in millions', () => {
    const html = doc('0001178913-26-004953').replace(/in millions/gi, 'in thousands')
    assert.throws(() => parseResultsRelease(html), /in millions/)
  })

  it('refuses a malformed revenue cell', () => {
    const html = doc('0001178913-26-004953').replace('669.8', '669.8x')
    assert.throws(() => parseResultsRelease(html))
  })
})

const q = (periodEnd: string, value: number, priorYearValue: number, filedDate: string): ReleaseQuarter => ({ periodEnd, value, priorYearValue,
  scale: 'USD millions', form: '6-K', accessionNumber: `0000000000-26-${filedDate.replaceAll('-', '').slice(2)}`, filedDate, sourceUrl: 'https://www.sec.gov/x', sha256: 'x', checkedAt: '2026-11-06T00:00:00Z' })

describe('6-K release record', () => {
  it('picks the latest quarter and the quarter before it', () => {
    const r = buildReleaseRecord('c', 'C', '1', [q('2026-06-30', 2, 1, '2026-07-30')], [q('2026-09-30', 3, 2, '2026-11-02')])
    assert.equal(r.latest?.periodEnd, '2026-09-30')
    assert.equal(r.prior?.periodEnd, '2026-06-30')
  })

  it('refuses two releases that disagree on one quarter', () => {
    assert.throws(() => buildReleaseRecord('c', 'C', '1', [q('2026-06-30', 2, 1, '2026-07-30')], [q('2026-06-30', 5, 1, '2026-07-31')]), /Conflicting/)
  })

  it('refuses a prior-year column that differs from the earlier release', () => {
    assert.throws(() => buildReleaseRecord('c', 'C', '1', [q('2025-09-30', 677.5 * M, 1, '2025-10-28')], [q('2026-09-30', 669.8 * M, 600 * M, '2026-11-02')]), /Prior-year/)
  })
})

describe('6-K refresh', () => {
  const realFetch = globalThis.fetch
  const stub = (missing = new Set<string>()) => {
    globalThis.fetch = (async (input: string | URL | Request) => {
      const url = String(input instanceof Request ? input.url : input)
      if (missing.has(url)) throw new Error('Unarchived SEC request held by release gate')
      if (url === 'https://data.sec.gov/submissions/CIK0001015922.json') return new Response(readFileSync(join(dir, 'submissions-CIK0001015922.json')))
      const m = /\/1015922\/(\d{10})(\d{2})(\d{6})\/([^/]+)$/.exec(url)
      const file = m && `${m[1]}-${m[2]}-${m[3]}-${m[4]}`
      if (file && readdirSync(dir).includes(file)) return new Response(readFileSync(join(dir, file)))
      return new Response('<html><body>Other 6-K</body></html>')
    }) as typeof fetch
  }
  const now = new Date('2026-11-06T12:00:00Z')

  it('builds Check Point through the quarter ended 2026-09-30', async () => {
    stub()
    try {
      const out = join(mkdtempSync(join(tmpdir(), 'r6k-')), 'out.json')
      const result = await refreshReleases(now, out)
      const cp = result.suppliers.find(s => s.id === 'checkpoint')!
      assert.equal(result.failures.length, 0)
      assert.equal(cp.latest?.periodEnd, '2026-09-30')
      assert.equal(cp.latest?.value, 669.8 * M)
      assert.equal(cp.prior?.periodEnd, '2026-06-30')
      assert.equal(cp.quarters.length, 5)
    } finally { globalThis.fetch = realFetch }
  })

  it('keeps the last good record when the index is unavailable', async () => {
    stub(new Set(['https://data.sec.gov/submissions/CIK0001015922.json']))
    try {
      const out = join(mkdtempSync(join(tmpdir(), 'r6k-')), 'out.json')
      const retained = { generatedAt: '', failures: [], checks: [], suppliers: [{ id: 'checkpoint', name: 'C', cik: '0001015922',
        quarters: [q('2026-06-30', 2, 1, '2026-07-30')], latest: q('2026-06-30', 2, 1, '2026-07-30'), prior: null }] }
      writeFileSync(out, JSON.stringify(retained))
      const result = await refreshReleases(now, out)
      assert.equal(result.failures.length, 1)
      assert.equal(result.suppliers[0].latest?.periodEnd, '2026-06-30')
    } finally { globalThis.fetch = realFetch }
  })
})
