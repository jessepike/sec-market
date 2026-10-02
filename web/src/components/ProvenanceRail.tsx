import { formatShortDate } from '../data/dates'
import { LAST_UPDATED_ISO, PRODUCT_TITLE } from '../data/meta'

/**
 * D-76/autonomy-coverage-plan.md §3, step 1: this rail used to carry a
 * TRACKED/JUDGED legend, because live pages carried both kinds of claim. The
 * site now publishes sourced facts only and no judgments, so the legend is
 * replaced with one plain statement rather than a two-state key with nothing
 * for one of its states to point at on a live page.
 *
 * Fix pass 4, item 11: the rail renders on every route (AppShell mounts it
 * once, above the per-route content), including the three kept as dated
 * records — the issue archive, an issue permalink, and /thesis/. On the
 * week-36 issue permalink this statement ("published automatically, with no
 * stances...") sat directly above that page's own old signed judgments,
 * reading as a live claim about content the page itself says is a dated
 * record. `archive` suppresses the statement line there; the brand and the
 * "AS OF" date stay on every route, and the archive notice each of those
 * three pages already carries (App.tsx's `ArchiveNotice`) is what actually
 * says the page is a dated record.
 */
export function ProvenanceRail({ archive = false }: { archive?: boolean }) {
  return (
    <div className="rail" role="region" aria-label="Provenance">
      <div className="rail__inner">
        <p className="rail__brand">{PRODUCT_TITLE}</p>
        <span className="rail__rule" aria-hidden="true" />
        <p className="rail__asof">
          AS OF <time dateTime={LAST_UPDATED_ISO}>{formatShortDate(LAST_UPDATED_ISO)}</time>
        </p>
        {archive ? null : (
          <p className="rail__statement">
            Sourced facts, checked and published automatically. No stances, rankings or forecasts.
          </p>
        )}
      </div>
    </div>
  )
}
