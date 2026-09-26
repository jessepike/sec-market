import { EPISODE_ID, EPISODE_VERSION, LAST_UPDATED_DISPLAY } from '../data/meta'
import { reasoningSteps, signalFamilies, sourcingLadder } from '../data/method'

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
        independent print — we do not rewrite them into the buyer. Tracked figures are updated as
        companies report; the run status near the top of the page says whether the latest run was
        complete.
      </p>

      <h3 className="method__subhead">Signals behind the standing thesis (archived analysis)</h3>
      <p className="method-copy">
        The table below documents how the site&rsquo;s one standing analysis (&ldquo;does security
        spending lag infrastructure spending&rdquo;, kept at <a href="/thesis/">/thesis/</a>) was
        reasoned about while it was an active judgment. It describes that archived record, not the
        live tracker above, which publishes no calls.
      </p>
      <div className="table-scroll">
        <table className="tempo-table method-table">
          <caption className="visually-hidden">
            Signal families used in this analysis, with examples and how each is treated
          </caption>
          <thead>
            <tr>
              <th scope="col">Signal</th>
              <th scope="col">Examples</th>
              <th scope="col">We treat it as</th>
            </tr>
          </thead>
          {signalFamilies.map((family) => (
            <tbody key={family.name}>
              <tr>
                <th scope="row">{family.name}</th>
                <td>{family.examples}</td>
                <td>{family.weTreatAs}</td>
              </tr>
              <tr className="method-table__guard">
                <td colSpan={3}>
                  <strong>We do not.</strong> {family.weDoNot}
                </td>
              </tr>
            </tbody>
          ))}
        </table>
      </div>

      <h3 className="method__subhead">How that archived call was reasoned (thesis only)</h3>
      <ol className="method-steps">
        {reasoningSteps.map((item, index) => (
          <li key={item.step} className="method-step">
            <p className="method-step__n">{index + 1}</p>
            <div>
              <h4>{item.step}</h4>
              <p>{item.rule}</p>
            </div>
          </li>
        ))}
      </ol>
    </section>
  )
}
