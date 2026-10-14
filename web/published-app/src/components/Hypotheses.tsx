import { hypotheses } from '../data/hypotheses'
import { claimId, effectiveJudgment } from '../data/reconfirmationHelpers'
import { reconfirmations } from '../data/reconfirmations'
import { EvidenceLink } from './EvidenceLink'
import { JudgedStampStacked } from './JudgedStamp'

export function Hypotheses() {
  return (
    <section id="hypotheses" className="hypotheses" aria-labelledby="hypotheses-heading">
      <div className="hypotheses__head">
        <h2 id="hypotheses-heading">Tracked hypotheses</h2>
        <p className="stamp-label">Stated in advance · scored against evidence, not opinion</p>
      </div>
      <ul className="hypotheses__list">
        {hypotheses.map((item) => (
          <li key={item.id} className={'hypotheses__row hypotheses__row--' + item.state.toLowerCase()}>
            <span className={'chip chip--' + (item.state === 'NO-CALL' ? 'watch' : 'prepare')}>
              {item.state}
            </span>
            <p className="hypotheses__claim">{item.claim}</p>
            <p className="hypotheses__note">{item.note}</p>
            <div className="hypotheses__meta">
              {item.provenance.layer === 'judged' ? (
                <JudgedStampStacked
                  judgedOn={item.provenance.judgedOn}
                  reconfirmedOn={
                    effectiveJudgment(claimId('hypothesis', item.id), item.provenance.judgedOn, reconfirmations)
                      .reconfirmedOn
                  }
                />
              ) : null}
              {item.evidenceIds.length > 0 ? <EvidenceLink ids={item.evidenceIds} /> : null}
            </div>
          </li>
        ))}
      </ul>
    </section>
  )
}
