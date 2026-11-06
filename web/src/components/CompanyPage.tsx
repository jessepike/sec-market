import { companyView, eventWindow } from '../data/companyPages'

/**
 * `/companies/<id>/` (D-139): every figure and dated event the site holds for
 * one supplier, each with its period, source and certified flag. Built from
 * src/data/companyPages.ts, the same view the page's Markdown and JSON copies
 * use. Reuses the coverage page's styles; no new CSS.
 */
export function CompanyPage({ id }: { id: string }) {
  const view = companyView(id)
  if (!view) return null
  return (
    <section id="company" className="coverage-page" aria-labelledby="company-heading">
      <h1 id="company-heading">
        {view.displayName}
      </h1>
      <p className="coverage-page__lede">
        {[view.ticker, view.name !== view.displayName ? view.name.replace(/\.+$/, '') : null, view.typeLabel, ...view.domains].filter(Boolean).join(' · ')}.
        Coverage tier {view.tierNumber}: {view.tierName}.
        Every figure keeps the period it is true for and the source it is cited to.
      </p>

      <h2 id="company-figures">Figures</h2>
      {view.figures.length === 0 ? (
        <p className="coverage-page__note">No figures on record for this company.</p>
      ) : (
        <table className="coverage-table">
          <thead>
            <tr>
              <th scope="col">Figure</th>
              <th scope="col">Value</th>
              <th scope="col">Period</th>
              <th scope="col">Source</th>
            </tr>
          </thead>
          <tbody>
            {view.figures.map((f) => (
              <tr key={f.id}>
                <th scope="row" data-label="Figure">{f.label}</th>
                <td data-label="Value">
                  {f.value}
                  {f.certified ? <span className="coverage-table__domains">Re-derived from SEC filings</span> : null}
                </td>
                <td data-label="Period">{f.period || 'Not stated'}</td>
                <td data-label="Source">
                  {f.sourceUrls.length === 0
                    ? 'None listed'
                    : f.sourceUrls.map((url, i) => (
                        <span key={url}>
                          {i > 0 ? ', ' : null}
                          <a href={url} rel="noopener">{f.sourceDates[i] || 'Source'}</a>
                        </span>
                      ))}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {view.secQuarters.length > 0 && (
        <>
          <h2 id="company-sec-revenue">Quarterly revenue from SEC filings</h2>
          <p className="coverage-page__note">Exact dollars from filings. Derived quarters are labelled; a later filing may restate a comparative figure.</p>
          <table className="coverage-table">
            <thead>
              <tr>
                <th scope="col">Quarter ended</th>
                <th scope="col">Revenue, USD</th>
                <th scope="col">Filed</th>
                <th scope="col">Source</th>
              </tr>
            </thead>
            <tbody>
              {view.secQuarters.map((q) => (
                <tr key={q.periodEnd}>
                  <th scope="row" data-label="Quarter ended">{q.periodEnd}</th>
                  <td data-label="Revenue, USD">${q.revenueUsd.toLocaleString('en-US')}{q.derived ? ' (derived)' : ''}</td>
                  <td data-label="Filed">{q.filedDate}</td>
                  <td data-label="Source"><a href={q.sourceUrl} rel="noopener">{q.form}</a></td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}

      {view.filings.length > 0 && (
        <>
          <h2 id="company-filings">Activity ledger: SEC filings</h2>
          <p className="coverage-page__note">Every quarterly and annual report filed in the last 12 months. These routine filings no longer appear in the front page change log.</p>
          <table className="coverage-table">
            <thead>
              <tr>
                <th scope="col">Filed</th>
                <th scope="col">Form</th>
                <th scope="col">Latest quarter reported</th>
              </tr>
            </thead>
            <tbody>
              {view.filings.map((f) => (
                <tr key={f.sourceUrl}>
                  <th scope="row" data-label="Filed">{f.filedDate}</th>
                  <td data-label="Form"><a href={f.sourceUrl} rel="noopener">{f.form}</a></td>
                  <td data-label="Latest quarter reported">{f.periodEnd}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}

      <h2 id="company-events">Events, {eventWindow.from} to {eventWindow.to}</h2>
      {view.events.length === 0 ? (
        <p className="coverage-page__note">No dated events on record in this window.</p>
      ) : (
        <table className="coverage-table">
          <thead>
            <tr>
              <th scope="col">Date</th>
              <th scope="col">Type</th>
              <th scope="col">Event</th>
              <th scope="col">Source</th>
            </tr>
          </thead>
          <tbody>
            {view.events.map((e) => (
              <tr key={e.id}>
                <th scope="row" data-label="Date">{e.date}</th>
                <td data-label="Type">{e.type}</td>
                <td data-label="Event">{e.text}</td>
                <td data-label="Source">
                  {e.sourceUrls.map((url, i) => (
                    <span key={url}>
                      {i > 0 ? ', ' : null}
                      <a href={url} rel="noopener">{e.sourceDates[i] || 'Source'}</a>
                    </span>
                  ))}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <p className="coverage-page__note">
        This page is also published as <a href={`${view.path}index.md`}>Markdown</a> and{' '}
        <a href={`${view.path}data.json`}>JSON</a> for programs and AI agents.
      </p>
      <p className="coverage-page__back">
        <a href="/coverage/">All tracked companies</a> · <a href="/">Back to the front page</a>
      </p>
    </section>
  )
}
