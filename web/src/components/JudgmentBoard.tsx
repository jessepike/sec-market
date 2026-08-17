import { marketCall } from '../data/market'
import { EvidenceLink } from './EvidenceLink'

export function JudgmentBoard() {
  return (
    <section id="read" className="judgment" aria-labelledby="judgment-heading">
      <div className="section-heading">
        <h2 id="judgment-heading">The read</h2>
        <p>{marketCall.confidenceNote}</p>
      </div>

      <div className="judgment__grid">
        <div className="judgment__card">
          <h3>What changed</h3>
          <ol className="judgment__list">
            {marketCall.whatChanged.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ol>
        </div>
        <div className="judgment__split">
          <div className="judgment__card">
            <h3>Do</h3>
            <ul className="judgment__list">
              {marketCall.actions.doItems.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
          <div className="judgment__card">
            <h3>Avoid</h3>
            <ul className="judgment__list judgment__list--avoid">
              {marketCall.actions.avoidItems.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
        </div>
        <div className="judgment__card">
          <h3>We will not call</h3>
          <ul className="judgment__list">
            {marketCall.noCallBoundaries.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
        <div className="judgment__card">
          <h3>What would change the call</h3>
          <ul className="judgment__list">
            {marketCall.changeTriggers.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      </div>
      <EvidenceLink ids={marketCall.evidenceIds} label="Sources" />
    </section>
  )
}
