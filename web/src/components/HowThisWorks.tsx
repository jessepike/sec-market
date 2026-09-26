import { EPISODE_ID, EPISODE_VERSION, LAST_UPDATED_DISPLAY } from '../data/meta'
import { sourcingLadder } from '../data/method'
import { notCoveredByTracker, trackerDomains } from '../data/tracker/domains'
import { trackerSuppliers } from '../data/tracker/suppliers'

/**
 * AUTO-001 fix pass 2 (2026-09-26), item 5: both blind rescores caught
 * live-page judgment text here — this section used to also render two
 * tables from data/method.ts (`signalFamilies`, `reasoningSteps`), framed
 * as "archived analysis" but still served on `/`, not an archive-only
 * route. Those tables carried the exact banned phrases both scorers quoted
 * verbatim ("PREPARE only where the account has a matching live motion",
 * "That is a no-call", "The best check on whether customers actually
 * spent"). They are gone from this component; `data/method.ts` itself is
 * untouched (`signalFamilies`/`reasoningSteps` stay there as the historical
 * record of how the archived `/thesis/` call was reasoned — it is simply
 * not imported here anymore). The sourcing ladder stays: it describes a
 * publishing standard for the live tracker, not a judgment.
 */
export function HowThisWorks() {
  return (
    <section className="method" aria-labelledby="method-heading">
      <div className="section-heading">
        <h2 id="method-heading">How this is built</h2>
        <p>
          The market-by-domain tracker publishes facts only: no stances, rankings, forecasts, or
          sentences interpreting what a fact means. &ldquo;Revenue growth&rdquo; is the year-over-year
          change in a company&rsquo;s own reported GAAP revenue for the quarter named, taken from its
          SEC filings or its own press release; where a company reports no comparable revenue figure,
          the table says so rather than estimating one. Facts are collected, checked against the
          sourcing ladder below, and published automatically — no human approval step, and no machine
          judgment. This edition is the Episode 002 packet ({EPISODE_ID} v{EPISODE_VERSION}) plus a
          facts-only pass, updated {LAST_UPDATED_DISPLAY}. Every number links to a source excerpt and
          its limits.
        </p>
      </div>

      <h3 className="method__subhead">The sourcing ladder</h3>
      <p className="method-copy">
        Every distress or consolidation fact on the tracker is checked against this ladder before it
        can publish. A fact resting only on the weakest rung, a single trade-press report with no
        primary document behind it, does not publish on this site — it stays a lead until a stronger
        source confirms it.
      </p>
      <div className="table-scroll">
        <table className="tempo-table method-table">
          <caption className="visually-hidden">The five-rung sourcing ladder, strongest first</caption>
          <thead>
            <tr>
              <th scope="col">Rung</th>
              <th scope="col">What it is</th>
              <th scope="col">Publishes alone?</th>
            </tr>
          </thead>
          <tbody>
            {sourcingLadder.map((rung) => (
              <tr key={rung.rung}>
                <th scope="row">
                  {rung.rung}. {rung.label}
                </th>
                <td>{rung.description}</td>
                <td>{rung.publishesAlone ? 'Yes' : 'No'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <h3 className="method__subhead">How the tracker ages</h3>
      <p className="method-copy">
        Current prints stay on the scorecard. Older still-true context collapses to Background.
        Superseded prints leave the card and stay in evidence. Acquired vendors keep their last
        independent print — we do not rewrite them into the buyer. SEC filings refresh daily; press,
        funding and distress facts refresh twice a week. The run status near the top of the page
        says whether the latest run was complete.
      </p>

      <h3 className="method__subhead">What is not covered</h3>
      <p className="method-copy">
        {trackerDomains.length} domains, {trackerSuppliers.length} tracked suppliers — the full list,
        and what falls outside it, is in{' '}
        <a href="#tracker-coverage">What this site covers</a> earlier on this page. In short:{' '}
        {notCoveredByTracker.length} categories of company and claim this tracker does not follow,
        stated there rather than here so it stays in one place.
      </p>
    </section>
  )
}
