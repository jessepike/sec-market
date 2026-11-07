import { formatShortDate } from '../data/tracker/derive'
import {
  formatUsd,
  fundingUpdatedAt,
  heldRoundCount,
  isTracked,
  portfolioAdditions,
  portfolioSummary,
  roundsByWeek,
  sourceLabel,
} from '../data/funding/feed'

/**
 * `/funding/`: security funding rounds by week, and companies newly listed on
 * cyber-specialist investors' portfolio pages. Written weekly by
 * ops/funding/collect.py. Facts only: no ranking and no labels.
 */
export function FundingRounds() {
  const weeks = roundsByWeek()
  const additions = portfolioAdditions()
  const portfolios = portfolioSummary()
  const baselineDates = portfolios.map((p) => p.baselineAt).filter((d): d is string => Boolean(d)).sort()
  const roundCount = weeks.reduce((n, w) => n + w.rounds.length, 0)
  return (
    <section id="funding" className="coverage-page funding-page" aria-labelledby="funding-heading">
      <h1 id="funding-heading">Venture rounds</h1>
      <p className="coverage-page__scope">All announced security rounds, including companies not tracked here.</p>
      <p className="coverage-page__lede">
        Venture rounds and other financings announced by security companies, week by week, including companies
        the site does not track. Each round comes from the weekly Return on Security funding list. It is shown
        only when the source that list links to (the company, an investor, a news report or an SEC Form D)
        names the company and states the same dollar amount. Rounds without an amount are not shown.
      </p>
      {fundingUpdatedAt ? (
        <p className="coverage-page__note">
          Last new data {formatShortDate(fundingUpdatedAt)}. The list is read every Monday. {roundCount} rounds
          shown from the latest {weeks.length} weeks.
          {heldRoundCount > 0 ? ` ${heldRoundCount} more are not shown because their source did not confirm the company and amount.` : ''}
        </p>
      ) : null}

      <h2 id="funding-weeks">Rounds by week</h2>
      {weeks.length === 0 ? <p>No confirmed rounds yet.</p> : null}
      {weeks.map((week) => (
        <section key={week.weekOf} id={`funding-week-${week.weekOf}`} className="coverage-list" aria-labelledby={`funding-week-${week.weekOf}-heading`}>
          <h3 id={`funding-week-${week.weekOf}-heading`}>
            Week of {formatShortDate(week.weekOf)} ({week.rounds.length})
          </h3>
          <table className="coverage-table funding-table">
            <thead>
              <tr>
                <th scope="col">Company</th>
                <th scope="col">Round</th>
                <th scope="col">Amount</th>
                <th scope="col">Lead investor</th>
                <th scope="col">Source</th>
              </tr>
            </thead>
            <tbody>
              {week.rounds.map((round) => (
                <tr key={round.id}>
                  <th scope="row" data-label="Company">
                    <span className="coverage-table__name">
                      <a href={round.companyUrl} rel="nofollow noopener">{round.company}</a>
                    </span>
                    <span className="coverage-table__domains">
                      {round.country}
                      {isTracked(round.company) ? ' · tracked supplier' : ''}
                    </span>
                  </th>
                  <td data-label="Round">{round.stage}</td>
                  <td data-label="Amount">{formatUsd(round.amountUsd)}</td>
                  <td data-label="Lead investor">{round.lead ?? 'Not disclosed'}</td>
                  <td data-label="Source">
                    <a href={round.sourceUrl} rel="nofollow noopener">
                      {sourceLabel(round)}
                    </a>
                    <span className="coverage-table__domains">
                      Found via <a href={round.foundVia.url} rel="nofollow noopener">{round.foundVia.name} #{round.foundVia.issue}</a>
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      ))}

      <h2 id="funding-portfolios">New on investor portfolio pages</h2>
      <p className="coverage-page__lede">
        Companies that appeared on a cyber-specialist investor&rsquo;s public portfolio page since the site first
        read it. A listing shows the investor added the company. It does not say when or how much they
        invested.
      </p>
      {additions.length === 0 ? (
        <p>
          None yet.{' '}
          {baselineDates.length
            ? `The pages were first read on ${formatShortDate(baselineDates[0])}. Companies added after that date will appear here.`
            : 'The pages have not been read yet.'}
        </p>
      ) : (
        <table className="coverage-table funding-table">
          <thead>
            <tr>
              <th scope="col">Company</th>
              <th scope="col">Investor</th>
              <th scope="col">First seen</th>
            </tr>
          </thead>
          <tbody>
            {additions.map((a) => (
              <tr key={`${a.investor}:${a.company}`}>
                <th scope="row" data-label="Company"><span className="coverage-table__name">{a.company}</span></th>
                <td data-label="Investor"><a href={a.investorUrl} rel="nofollow noopener">{a.investor}</a></td>
                <td data-label="First seen">{formatShortDate(a.firstSeen)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      <p className="coverage-page__note">
        Portfolio pages read each week:{' '}
        {portfolios.map((p, i) => (
          <span key={p.name}>
            {i > 0 ? ', ' : ''}
            <a href={p.url} rel="nofollow noopener">{p.name}</a> ({p.count} companies)
          </span>
        ))}
        . Funding lists come from{' '}
        <a href="https://www.returnonsecurity.com/" rel="nofollow noopener">Return on Security</a>. A company here is
        not added to the tracked suppliers unless the owner approves it.
      </p>
      <p className="coverage-page__back"><a href="/">Back to the front page</a></p>
    </section>
  )
}
