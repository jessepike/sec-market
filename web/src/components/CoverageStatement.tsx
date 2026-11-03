import { notCoveredByTracker, trackerDomains } from '../data/tracker/domains'
import { trackerSuppliers } from '../data/tracker/suppliers'

/**
 * "What this site covers" — autonomy-coverage-plan.md §3c. States the
 * twelve declared domains, the supplier count, and what is explicitly not
 * covered, per product-core.md §4 and intent.md v1.4.
 */
export function CoverageStatement() {
  return (
    <section id="tracker-coverage" className="tracker-coverage" aria-labelledby="tracker-coverage-heading">
      <div className="section-heading">
        <h2 id="tracker-coverage-heading">What this site covers</h2>
        <p>
          {trackerDomains.length} domains, {trackerSuppliers.length} tracked suppliers. Adding or
          dropping a domain or a supplier is a data change, not a promise about who belongs in the
          market. <a href="/coverage/">See every supplier and how much is covered for each</a>.
        </p>
      </div>
      <ul className="tracker-coverage__domains">
        {trackerDomains.map((domain) => (
          <li key={domain.id}>
            <a href={`#domain-${domain.id}`}>{domain.name}</a> — {domain.scope}
          </li>
        ))}
      </ul>
      <h3 className="tracker-coverage__subhead">Not covered</h3>
      <ul className="tracker-coverage__not-covered">
        {notCoveredByTracker.map((line) => (
          <li key={line}>{line}</li>
        ))}
      </ul>
    </section>
  )
}
