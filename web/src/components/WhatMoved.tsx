import { weekMoves } from '../data/whatMoved'
import { EvidenceLink } from './EvidenceLink'

/**
 * D-76/autonomy-coverage-plan.md §3, step 1: this used to carry a second,
 * JUDGED column (posture HELD/MOVED and a method-rule "WHY" line, signed and
 * dated by a person). The site publishes sourced facts only now, so only the
 * TRACKED column — public prints, no judgment applied — survives here.
 */
export function WhatMoved() {
  return (
    <section id="moved" className="week-moved" aria-labelledby="moved-heading">
      <div className="week-moved__inner">
        <div className="week-moved__head">
          <h2 id="moved-heading">What moved</h2>
          <p className="stamp-label stamp-label--muted">WINDOW · {weekMoves.label}</p>
        </div>
        <div className="week-moved__grid">
          <div className="week-moved__col week-moved__col--tracked">
            <p className="stamp-label stamp-label--tracked">TRACKED · public prints, no judgment applied</p>
            <ul className="week-moved__list">
              {weekMoves.tracked.map((item) => (
                <li key={item.kind}>
                  <span className="week-moved__kind">{item.kind}</span>
                  <div>
                    <p>{item.text}</p>
                    {item.evidenceIds.length > 0 ? <EvidenceLink ids={item.evidenceIds} /> : null}
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </section>
  )
}
