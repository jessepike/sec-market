import { PRODUCT_TITLE } from '../data/meta'
import { certifiedDateDisplay } from '../data/tracker/certification'

/**
 * D-76/autonomy-coverage-plan.md §3, step 1: this rail used to carry a
 * TRACKED/JUDGED legend, because live pages carried both kinds of claim. The
 * site now publishes sourced facts only and no judgments, so the legend is
 * replaced with one plain statement rather than a two-state key with nothing
 * for one of its states to point at on a live page.
 */
export function ProvenanceRail() {
  return (
    <div className="rail" role="region" aria-label="Provenance">
      <div className="rail__inner">
        <p className="rail__brand">{PRODUCT_TITLE}</p>
        <span className="rail__rule" aria-hidden="true" />
        <p className="rail__asof">
          SEC figures certified {certifiedDateDisplay}
        </p>
        <p className="rail__statement">Sourced facts, published automatically. No stances, rankings or forecasts.</p>
      </div>
    </div>
  )
}
