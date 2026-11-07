import { companyPath } from '../data/companyPages'
import { formatShortDate } from '../data/tracker/derive'
import { coverageRows, coverageTiers, rowsForTier, typeTierCounts } from '../data/tracker/coverage'
import { onboardingRows, showOnboarding } from '../data/tracker/onboarding'
import { CoverageStatement } from './CoverageStatement'

/**
 * `/coverage/`: every tracked supplier, its company type, and how much the
 * site can say about it. Tiers come from src/data/tracker/coverage.ts and are
 * derived from each supplier's data, not set by hand.
 */
export function SupplierCoverage() {
  const grid = typeTierCounts()
  return (
    <section id="coverage" className="coverage-page" aria-labelledby="coverage-heading">
      <h1 id="coverage-heading">Companies</h1>
      <p className="coverage-page__lede">
        This site tracks {coverageRows.length} security suppliers. How much it can show for each one depends on
        what that company makes public. A US-listed company files its revenue with the SEC every quarter. A
        venture-backed startup announces funding rounds and sometimes its own growth figures. A company owned by
        private equity, or a product line inside a larger company, usually publishes no financials of its own, so
        the site can only record ownership and dated events.
      </p>

      <CoverageStatement />

      <h2 id="coverage-tiers">What each tier includes</h2>
      <div className="coverage-page__tiers">
        {coverageTiers.map((tier) => (
          <article key={tier.id} className={`coverage-tier coverage-tier--${tier.id}`}>
            <p className="coverage-tier__label">Tier {tier.number} · {rowsForTier(tier.id).length} suppliers</p>
            <h3>{tier.name}</h3>
            <p className="coverage-tier__who">{tier.who}</p>
            <ul>
              {tier.includes.map((line) => <li key={line}>{line}</li>)}
            </ul>
            <p className="coverage-tier__fresh"><strong>How current:</strong> {tier.freshness}</p>
          </article>
        ))}
      </div>

      <div className="table-scroll">
        <table className="coverage-grid">
          <caption>Suppliers by company type and coverage tier</caption>
          <thead>
            <tr>
              <th scope="col">Company type</th>
              {coverageTiers.map((tier) => <th scope="col" key={tier.id}>Tier {tier.number}</th>)}
              <th scope="col">Total</th>
            </tr>
          </thead>
          <tbody>
            {grid.map((row) => (
              <tr key={row.kind}>
                <th scope="row">{row.label}</th>
                {coverageTiers.map((tier) => <td key={tier.id}>{row.counts[tier.id] || '·'}</td>)}
                <td>{row.total}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <h2 id="coverage-suppliers">Every supplier, by tier</h2>
      {coverageTiers.map((tier) => {
        const rows = rowsForTier(tier.id)
        return (
          <section key={tier.id} id={`coverage-${tier.id}`} className="coverage-list" aria-labelledby={`coverage-${tier.id}-heading`}>
            <h3 id={`coverage-${tier.id}-heading`}>Tier {tier.number}: {tier.name} ({rows.length})</h3>
            <table className="coverage-table">
              <thead>
                <tr>
                  <th scope="col">Supplier</th>
                  <th scope="col">Company type</th>
                  <th scope="col">What the site has</th>
                  <th scope="col">Newest dated fact</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row) => (
                  <tr key={row.supplier.id}>
                    <th scope="row" data-label="Supplier">
                      <a className="coverage-table__name" title={row.supplier.name} href={companyPath(row.supplier.id)}>{row.displayName}</a>
                      {row.supplier.ticker ? <span className="coverage-table__ticker"> {row.supplier.ticker}</span> : null}
                      <span className="coverage-table__domains">{row.domains.join(' · ')}</span>
                    </th>
                    <td data-label="Company type">{row.typeLabel}</td>
                    <td data-label="What the site has">{row.holdings.join('; ')}</td>
                    <td data-label="Newest dated fact">{row.latestFact ? formatShortDate(row.latestFact) : 'None on record'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        )
      })}

      {showOnboarding && onboardingRows.length > 0 ? (
        <section id="coverage-onboarding" className="coverage-list coverage-onboarding" aria-labelledby="coverage-onboarding-heading">
          <h3 id="coverage-onboarding-heading">Being onboarded ({onboardingRows.length}, preview only)</h3>
          <p className="coverage-page__note">
            These suppliers have a sourced seed record but are not yet collected by the daily pipeline. They appear on
            the live site only after the pipeline has collected and checked them for three clean days in a row.
          </p>
          <table className="coverage-table">
            <thead>
              <tr>
                <th scope="col">Supplier</th>
                <th scope="col">Company type</th>
                <th scope="col">Seed record</th>
                <th scope="col">Target tier</th>
              </tr>
            </thead>
            <tbody>
              {onboardingRows.map((row) => (
                <tr key={row.supplier.id}>
                  <th scope="row" data-label="Supplier">
                    <span className="coverage-table__name" title={row.supplier.name}>{row.displayName}</span>
                    {row.supplier.ticker ? <span className="coverage-table__ticker"> {row.supplier.ticker}</span> : null}
                    <span className="coverage-table__domains">{row.domains.join(' · ')}</span>
                  </th>
                  <td data-label="Company type">{row.typeLabel}</td>
                  <td data-label="Seed record">
                    {row.facts.join('; ')}
                    {row.sources.map((source) => (
                      <span key={source.url}> <a href={source.url} rel="noopener noreferrer">Source: {source.label}</a></span>
                    ))}
                  </td>
                  <td data-label="Target tier">Tier {row.targetTier}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      ) : null}

      <p className="coverage-page__note">
        A supplier moves tier on its own when its data changes, for example when a private company goes public
        and starts filing with the SEC. &ldquo;Newest dated fact&rdquo; is the most recent date among the
        supplier&rsquo;s results, funding rounds and events on this site. Figures are re-derived from SEC
        filings only in tier 1.
      </p>
      <p className="coverage-page__back"><a href="/">Back to the front page</a></p>
    </section>
  )
}
