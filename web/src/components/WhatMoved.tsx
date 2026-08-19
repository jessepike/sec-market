import { formatShortDate } from '../data/dates'
import { weekMoves } from '../data/whatMoved'
import { EvidenceLink } from './EvidenceLink'

export function WhatMoved() {
  return (
    <section id="moved" className="week-moved" aria-labelledby="moved-heading">
      <div className="week-moved__inner">
        <div className="week-moved__head">
          <h2 id="moved-heading">What moved this week</h2>
          <p className="stamp-label stamp-label--muted">WEEK OF {weekMoves.label}</p>
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
          <div className="week-moved__col week-moved__col--judged">
            <p className="stamp-label stamp-label--judged">
              JUDGED · a person signed this ·{' '}
              <time dateTime={weekMoves.asOf}>{formatShortDate(weekMoves.asOf)}</time>
            </p>
            <ul className="week-moved__list">
              {weekMoves.judged.map((item) => (
                <li key={item.kind}>
                  <span className={'week-moved__kind week-moved__kind--' + item.kind.toLowerCase()}>
                    {item.kind}
                  </span>
                  <p>{item.text}</p>
                </li>
              ))}
            </ul>
            <p className="week-moved__quiet">{weekMoves.quietNote}</p>
          </div>
        </div>
      </div>
    </section>
  )
}
