import assert from 'node:assert/strict'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { describe, it } from 'node:test'
import { RunStatus } from '../src/components/RunStatus.tsx'
import { formatLongDate } from '../src/data/dates.ts'
import { LAST_UPDATED_DISPLAY, LAST_UPDATED_ISO } from '../src/data/meta.ts'
import { runStatus } from '../src/data/runStatus.ts'
import type { RunStatus as RunStatusData } from '../src/data/runStatus.ts'

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
  it('renders "every source collected" when the run is updated', () => {
    withRunStatus(
      { lastChecked: '2026-09-25', state: 'updated', failedSources: [] },
      () => {
        const markup = renderToStaticMarkup(createElement(RunStatus))
        assert.match(markup, /Figures checked 25 Sep 2026/)
        assert.match(markup, /every source collected/)
        assert.doesNotMatch(markup, /collection incomplete/)
      },
    )
  })

  it('renders "no material change" when the run found nothing new', () => {
    withRunStatus(
      { lastChecked: '2026-09-25', state: 'no-change', failedSources: [] },
      () => {
        const markup = renderToStaticMarkup(createElement(RunStatus))
        assert.match(markup, /no material change within our coverage/)
        assert.doesNotMatch(markup, /every source collected/)
      },
    )
  })

  it('renders the failure count and names the failed sources when incomplete', () => {
    withRunStatus(
      { lastChecked: '2026-09-24', state: 'incomplete', failedSources: ['SEC EDGAR', 'WARN notices'] },
      () => {
        const markup = renderToStaticMarkup(createElement(RunStatus))
        assert.match(markup, /Figures checked 24 Sep 2026/)
        assert.match(markup, /collection incomplete: 2 sources failed/)
        assert.match(markup, /SEC EDGAR, WARN notices/)
      },
    )
  })

  /**
   * AUTO-001 fix pass 2, item 4: a scope-restricted collect run can leave
   * failedSources empty — nothing failed, but not everything was checked
   * either — so runStatus.ts sets `detail` instead, and RunStatus.tsx must
   * prefer it over the generic "N sources failed" line.
   */
  it('renders the plain-language detail when incomplete with no failed sources', () => {
    withRunStatus(
      {
        lastChecked: '2026-09-25',
        state: 'incomplete',
        failedSources: [],
        detail: 'Press, funding and distress sources last checked for 4 of 74 suppliers on 26 Sep 2026 (restricted run: optiv, snyk, cyera, rapid7).',
      },
      () => {
        const markup = renderToStaticMarkup(createElement(RunStatus))
        assert.match(markup, /Figures checked 25 Sep 2026/)
        assert.match(markup, /Press, funding and distress sources last checked for 4 of 74 suppliers/)
        assert.doesNotMatch(markup, /collection incomplete: 0 sources failed/)
      },
    )
  })

  it('the shipped status is well formed: a real date, a known state, and a reason whenever incomplete', () => {
    assert.match(runStatus.lastChecked, /^\d{4}-\d{2}-\d{2}$/)
    assert.ok(['updated', 'no-change', 'incomplete'].includes(runStatus.state))
    if (runStatus.state !== 'incomplete') {
      assert.deepEqual(runStatus.failedSources, [])
    } else {
      // A scope-restricted run can leave failedSources empty; `detail` is
      // the plain-language reason in that case, so at least one must be set.
      assert.ok(runStatus.failedSources.length > 0 || Boolean(runStatus.detail))
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
