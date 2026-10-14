import { status, completeRefreshLabel, format } from './appStatus'

export function RefreshStatus() {
  return <section className="refresh-status" aria-labelledby="refresh-status-heading">
    <h2 id="refresh-status-heading">Data refresh status</h2>
    <p><strong>Last complete data refresh: {completeRefreshLabel}.</strong></p>
    <p>Latest attempt: {format(status.lastAttemptAt)} — incomplete and held. Published figures and their reporting periods are unchanged.</p>
    <p>{status.suppliersAttempted} of {status.supplierCount} suppliers attempted; {status.failedSupplierIds.length} have failed or unverified checks. A data update is published only when every required applicable check passes.</p>
    <p>App deployment revision: {status.appRevision?.slice(0, 7) ?? 'local review'}. This status update does not refresh the data. <a href="/refresh-attempt.json">Latest attempt receipt</a>.</p>
  </section>
}
