import raw from '../data/generated/refreshCoverage.json'
import type { RefreshCoverage as Coverage } from '../data/tracker/coverage'
import { trackerSuppliers } from '../data/tracker/suppliers'
import { completeRefreshDisplay, lastAttemptAt, appDeployment } from '../data/refreshPublication'

const coverage = raw as Coverage
const failures = trackerSuppliers.map(supplier => ({ name: supplier.name,
  reasons: [...new Set(coverage.fields.filter(f => f.supplierId === supplier.id && (f.status === 'failed' || f.status === 'not-checked')).map(f => `${f.field.split('.')[0]}: ${f.reason}`))],
})).filter(supplier => supplier.reasons.length)
export function RefreshCoverage() {
  return <section id="refresh-coverage" className="refresh-coverage" aria-labelledby="refresh-coverage-heading">
    <h2 id="refresh-coverage-heading">Source-check coverage</h2>
    <p>Last complete data refresh: {completeRefreshDisplay}. The data-updated date advances only when every required check passes.</p>
    <p>Latest attempt: {lastAttemptAt} ({coverage.state}). {coverage.supplierChecksReceived} of {coverage.supplierCount} supplier receipts recorded. An incomplete candidate is held from publication.</p>
    <p>{coverage.summary.updated} candidate field values changed; {coverage.summary['checked-no-change']} checked unchanged; {coverage.summary.unavailable} undisclosed answers requiring explicit policy; {coverage.summary.failed} failed checks; {coverage.summary['not-checked']} not verified. These attempt counts do not certify a complete refresh. Reporting periods remain separate.</p>
    <p>App deployment: {appDeployment.deployedAt ?? 'not recorded in this receipt'}. App deployment does not refresh data.</p>
    <p>{coverage.schedule.enabled ? 'Nightly refresh is scheduled for 02:00 Los Angeles time.' : 'Nightly hosted refresh is not enabled yet.'} <a href="/refresh-coverage.json">Full field and source-check report</a>.</p>
    <details><summary>Failed or unverified fields ({failures.length} suppliers)</summary><ul>{failures.map(supplier => <li key={supplier.name}><strong>{supplier.name}</strong><ul>{supplier.reasons.map(reason => <li key={reason}>{reason}</li>)}</ul></li>)}</ul></details>
  </section>
}
