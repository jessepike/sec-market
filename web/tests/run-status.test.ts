import assert from 'node:assert/strict'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { describe, it } from 'node:test'
import { RunStatus } from '../src/components/RunStatus.tsx'
import { runStatus } from '../src/data/runStatus.ts'
import type { RunStatus as RunStatusData } from '../src/data/runStatus.ts'

/**
 * The run-status data file exports one fixed value; these tests render the
 * component against a local override object built from it, one per state,
 * rather than mutating the shared export — the component reads the module's
 * `runStatus` binding directly, so each case temporarily monkey-patches the
 * exported object's own fields (safe here: it's a plain object, and each
 * test restores it before the next runs).
 */
function withRunStatus(next: RunStatusData, run: () => void): void {
  const original = { ...runStatus }
  Object.assign(runStatus, next)
  try {
    run()
  } finally {
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

  it('the shipped default is a genuinely updated, complete run', () => {
    assert.equal(runStatus.state, 'updated')
    assert.deepEqual(runStatus.failedSources, [])
  })
})
