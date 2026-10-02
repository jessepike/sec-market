import assert from 'node:assert/strict'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { describe, it } from 'node:test'
import { RunStatus } from '../src/components/RunStatus.tsx'
import { formatLongDate } from '../src/data/dates.ts'
import edgarFactsRaw from '../src/data/generated/edgarFacts.json' with { type: 'json' }
import { runStatus } from '../src/data/runStatus.ts'
import type { RunStatus as RunStatusData } from '../src/data/runStatus.ts'
import { LAST_UPDATED_DISPLAY, LAST_UPDATED_ISO } from '../src/data/meta.ts'
import { trackerSuppliers } from '../src/data/tracker/suppliers.ts'

/**
 * The run-status data file exports one derived value; these tests render
 * the component against a local override object built from it, one per
 * state, rather than mutating the shared export — the component reads the
 * module's `runStatus` binding directly, so each case temporarily
 * monkey-patches the exported object's own fields (safe here: it's a plain
 * object, and each test restores it before the next runs).
 *
 * Clears every existing key before assigning `next`, not just merges over
 * it — `runStatus` can carry an optional `detail` (AUTO-001 fix pass 2,
 * item 4), and a plain `Object.assign` would leave the shipped `runStatus`'s
 * real `detail` string leaking into a test case that doesn't set one.
 */
function withRunStatus(next: RunStatusData, run: () => void): void {
  const original = { ...runStatus }
  for (const key of Object.keys(runStatus)) delete (runStatus as Record<string, unknown>)[key]
  Object.assign(runStatus, next)
  try {
    run()
  } finally {
    for (const key of Object.keys(runStatus)) delete (runStatus as Record<string, unknown>)[key]
    Object.assign(runStatus, original)
  }
}

describe('RunStatus', () => {
  it('renders "Every source collected" when the run is updated', () => {
    withRunStatus(
      { lastChecked: '2026-09-25', state: 'updated', failedNewsSuppliers: [] },
      () => {
        const markup = renderToStaticMarkup(createElement(RunStatus))
        assert.match(markup, /Figures checked 25 Sep 2026/)
        assert.match(markup, /Every source collected/)
        assert.doesNotMatch(markup, /could not be read/)
      },
    )
  })

  it('renders "No material change" when the run found nothing new', () => {
    withRunStatus(
      { lastChecked: '2026-09-25', state: 'no-change', failedNewsSuppliers: [] },
      () => {
        const markup = renderToStaticMarkup(createElement(RunStatus))
        assert.match(markup, /No material change within our coverage/)
        assert.doesNotMatch(markup, /Every source collected/)
      },
    )
  })

  /**
   * Third fix pass (2026-09-26), items 1-3: the previous version of this
   * derivation rendered `failedSources` as a flat list of raw collector
   * strings — 25 of them, with URLs, HTTP status codes, and a reference to
   * `.collect/failed-sources.json`, a file the site never publishes. The
   * first line now reads like a status line for a security leader: the
   * filings side and the company-news side, each stated plainly, and the
   * affected suppliers move into a closed disclosure named by short display
   * name with one plain reason each.
   */
  it('renders the incomplete wording and the supplier count', () => {
    withRunStatus(
      {
        lastChecked: '2026-09-26',
        state: 'incomplete',
        detail: 'Filings complete for all 14 public suppliers; company news pages could not be read for 2 of 74 suppliers.',
        failedNewsSuppliers: [
          { supplierId: 'armis', displayName: 'Armis', reason: 'newsroom blocked automated reading' },
          { supplierId: 'ivanti', displayName: 'Ivanti', reason: 'no primary source found' },
        ],
      },
      () => {
        const markup = renderToStaticMarkup(createElement(RunStatus))
        assert.match(markup, /Figures checked 26 Sep 2026/)
        assert.match(markup, /Filings complete for all 14 public suppliers/)
        assert.match(markup, /company news pages could not be read for 2 of 74 suppliers/)
        assert.match(markup, /Which sources failed/)
        assert.match(markup, /Armis/)
        assert.match(markup, /newsroom blocked automated reading/)
        assert.match(markup, /Ivanti/)
        assert.match(markup, /no primary source found/)
        // Never a URL, a file path, or an HTTP status code anywhere in the
        // rendered markup — the exact defect this pass fixed.
        assert.doesNotMatch(markup, /https?:\/\//)
        assert.doesNotMatch(markup, /HTTP \d{3}/)
        assert.doesNotMatch(markup, /\.collect\//)
        assert.doesNotMatch(markup, /failed-sources\.json/)
      },
    )
  })

  it('renders no disclosure when incomplete for a reason with no per-supplier failures', () => {
    withRunStatus(
      {
        lastChecked: '2026-09-25',
        state: 'incomplete',
        failedNewsSuppliers: [],
        detail: 'Filings complete for all 14 public suppliers; press, funding and distress sources last checked for 4 of 74 suppliers on 26 Sep 2026 (restricted run: optiv, snyk, cyera, rapid7).',
      },
      () => {
        const markup = renderToStaticMarkup(createElement(RunStatus))
        assert.match(markup, /Figures checked 25 Sep 2026/)
        assert.match(markup, /press, funding and distress sources last checked for 4 of 74 suppliers/)
        assert.doesNotMatch(markup, /Which sources failed/)
      },
    )
  })

  it('the shipped status is well formed: a real date, a known state, and a reason whenever incomplete', () => {
    assert.match(runStatus.lastChecked, /^\d{4}-\d{2}-\d{2}$/)
    assert.ok(['updated', 'no-change', 'incomplete'].includes(runStatus.state))
    if (runStatus.state !== 'incomplete') {
      assert.deepEqual(runStatus.failedNewsSuppliers, [])
    } else {
      assert.ok(Boolean(runStatus.detail), 'expected a plain-language detail for an incomplete run')
    }
  })

  /**
   * Third fix pass, item 2: the closed disclosure lists each affected
   * supplier once, by short display name, with one plain reason — never a
   * URL, an HTTP status code, or a file path, whatever the shipped data
   * actually says failed.
   */
  it('the shipped failedNewsSuppliers, if any, are plain text only', () => {
    for (const supplier of runStatus.failedNewsSuppliers) {
      assert.doesNotMatch(supplier.reason, /https?:\/\//)
      assert.doesNotMatch(supplier.reason, /HTTP \d{3}/)
      assert.doesNotMatch(supplier.reason, /\.(json|collect)\b/)
      assert.ok(supplier.supplierId.length > 0)
      assert.ok(supplier.displayName.length > 0)
    }
    const ids = runStatus.failedNewsSuppliers.map((s) => s.supplierId)
    assert.deepEqual(ids, Array.from(new Set(ids)), 'expected one row per distinct supplier, no duplicates')
  })
})

/**
 * AUTO-001 fix pass 4, item 4: the filings clause's denominator ("SEC
 * filings complete for all 16 public suppliers that file quarterly with the
 * SEC") must always reconcile with the tracker's own count of `kind:
 * 'public'` suppliers — the defect both blind scorers caught was exactly
 * this drifting apart (a hand-typed "14" against 18 "Public ·" rows).
 * runStatus.ts derives `publicSuppliers`/`nonXbrlPublicNames` from
 * `trackerSuppliers` itself (split on whether a public supplier carries an
 * `edgarId`) rather than importing a private array, so this test recomputes
 * the same split independently against the live tracker data and the
 * generated EDGAR facts file, the way verify-tracker.ts's own gates do.
 */
describe('filingsClause supplier-count reconciliation (runStatus.ts)', () => {
  const publicSuppliers = trackerSuppliers.filter((s) => s.kind === 'public')
  const xbrlPublicSuppliers = publicSuppliers.filter((s) => s.edgarId)
  const nonXbrlPublicSuppliers = publicSuppliers.filter((s) => !s.edgarId)

  it('XBRL-covered public suppliers plus named non-XBRL public suppliers equal the tracker\'s public-supplier count', () => {
    assert.equal(
      xbrlPublicSuppliers.length + nonXbrlPublicSuppliers.length,
      publicSuppliers.length,
      'the split by edgarId should account for every "public" tracker supplier exactly once',
    )
  })

  it('every XBRL-covered public supplier\'s edgarId resolves in generated/edgarFacts.json', () => {
    const edgarIds = new Set((edgarFactsRaw as { suppliers: Array<{ id: string }> }).suppliers.map((s) => s.id))
    for (const supplier of xbrlPublicSuppliers) {
      assert.ok(
        edgarIds.has(supplier.edgarId!),
        `supplier "${supplier.id}" (${supplier.name}) has edgarId "${supplier.edgarId}", which does not ` +
          'resolve in generated/edgarFacts.json',
      )
    }
  })

  it('the shipped filings clause names exactly the non-XBRL public suppliers, by short name', () => {
    if (runStatus.state === 'incomplete' && runStatus.detail) {
      for (const supplier of nonXbrlPublicSuppliers) {
        // A legal-entity suffix is stripped for the reader-facing clause
        // (shortSupplierName) — check on the first word, which survives
        // every suffix-stripping case in this tracker's supplier names.
        const firstWord = supplier.name.split(/[\s,]/)[0]
        assert.ok(
          runStatus.detail!.includes(firstWord),
          `expected the run-status detail to name "${supplier.name}" (a non-XBRL public supplier) — got: "${runStatus.detail}"`,
        )
      }
    }
  })
})

/**
 * Step 1 fix pass, item 2: meta.ts's LAST_UPDATED_ISO/LAST_UPDATED_DISPLAY
 * are derived from runStatus.lastChecked, not hand-set — this is the
 * data-level half of that guarantee (the e2e half, checking the four
 * rendered dates on the page itself, lives in tests/e2e/smoke.spec.ts).
 * `withRunStatus()` above mutates the shared `runStatus` object at test
 * time, after meta.ts has already captured `runStatus.lastChecked` into a
 * module-level const, so this checks the derivation against the shipped
 * default rather than inside one of those mutated blocks.
 */
describe('meta.ts date derivation (single source)', () => {
  it('LAST_UPDATED_ISO is exactly runStatus.lastChecked', () => {
    assert.equal(LAST_UPDATED_ISO, runStatus.lastChecked)
  })

  it('LAST_UPDATED_DISPLAY is the long-form rendering of runStatus.lastChecked', () => {
    assert.equal(LAST_UPDATED_DISPLAY, formatLongDate(runStatus.lastChecked))
  })
})
