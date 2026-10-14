import raw from '../data/generated/refreshCoverage.json'
import type { RefreshCoverage as Coverage } from '../data/tracker/coverage'
import { trackerSuppliers } from '../data/tracker/suppliers'

const coverage = raw as Coverage
const failures = trackerSuppliers.map(supplier => ({ name: supplier.name,
  reasons: [...new Set(coverage.fields.filter(f => f.supplierId === supplier.id && (f.status === 'failed' || f.status === 'not-checked')).map(f => `${f.field.split('.')[0]}: ${f.reason}`))],
})).filter(supplier => supplier.reasons.length)
export function RefreshCoverage() {
  return <section id="refresh-coverage" className="refresh-coverage" aria-labelledby="refresh-coverage-heading">
    <h2 id="refresh-coverage-heading">Source-check coverage</h2>
    <p>Check attempted {coverage.checkedAt.slice(0, 10)}. {coverage.supplierChecksReceived} of {coverage.supplierCount} supplier receipts recorded.</p>
    <p>{coverage.summary.updated} field values updated; {coverage.summary['checked-no-change']} checked with no new disclosure; {coverage.summary.unavailable} not disclosed in checked sources; {coverage.summary.failed} failed checks; {coverage.summary['not-checked']} not verified. Retained facts keep their original reporting periods.</p>
    <p>{coverage.schedule.enabled ? 'Nightly refresh is scheduled for 02:00 Los Angeles time.' : 'Nightly hosted refresh is not enabled yet.'} <a href="/refresh-coverage.json">Full field and source-check report</a>.</p>
    <details><summary>Failed or unverified fields ({failures.length} suppliers)</summary><ul>{failures.map(supplier => <li key={supplier.name}><strong>{supplier.name}</strong><ul>{supplier.reasons.map(reason => <li key={reason}>{reason}</li>)}</ul></li>)}</ul></details>
  </section>
}
