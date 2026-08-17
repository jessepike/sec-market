import { EPISODE_ID, EPISODE_VERSION, LAST_UPDATED_DISPLAY } from '../data/meta'
import { reasoningSteps, signalFamilies } from '../data/method'

export function HowThisWorks() {
  return (
    <section className="method" aria-labelledby="method-heading">
      <div className="section-heading">
        <h2 id="method-heading">How this is built</h2>
        <p>
          Public sources only. This edition is the Episode 002 packet ({EPISODE_ID} v{EPISODE_VERSION})
          plus an August 2026 surface refresh — SentinelOne, SailPoint, identity coverage names, and
          2026 capital events — updated {LAST_UPDATED_DISPLAY}. Each domain posture is dated, with a
          horizon and the evidence that produced it. This edition shows what held or moved versus the
          one before. Not a live feed. Every number links to a source excerpt and its limits.
        </p>
      </div>

      <h3 className="method__subhead">How editions age</h3>
      <p className="method-copy">
        Current prints stay on the scorecard. Older still-true context collapses to Background.
        Superseded prints leave the card and stay in evidence. Acquired vendors keep their last
        independent print — we do not rewrite them into the buyer. Domain postures keep the date
        they were set; the next edition shows what held or moved. Refresh is manual: earnings
        clusters, material closes or raises, and Watch-next falsifiers. Not a weekly news cycle.
      </p>

      <h3 className="method__subhead">Signals we use</h3>
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

      <h3 className="method__subhead">How we turn that into a call</h3>
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
