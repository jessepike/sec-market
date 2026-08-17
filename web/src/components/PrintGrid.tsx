import { printGroups, vendorPrints } from '../data/prints'
import { EvidenceLink } from './EvidenceLink'

export function PrintGrid() {
  return (
    <section id="prints" className="print-grid" aria-labelledby="prints-heading">
      <div className="section-heading">
        <h2 id="prints-heading">This period</h2>
        <p>Public prints first. Private names stay on the board as capital or “no series” — not invented ARR.</p>
      </div>
      {printGroups.map((group) => {
        const prints = vendorPrints.filter((print) => print.group === group)
        if (prints.length === 0) return null
        const comparable = prints.filter((print) => print.surface !== 'coverage').length
        return (
          <div key={group} className="print-group">
            <div className="grouphdr">
              <span className="grouphdr__title">{group}</span>
              <span className="grouphdr__count">
                {comparable} print{comparable === 1 ? '' : 's'} · {prints.length} covered
              </span>
            </div>
            <div className="print-cards">
              {prints.map((print) => (
                <article
                  key={print.id}
                  className={
                    print.surface === 'coverage' ? 'print-card print-card--coverage' : 'print-card'
                  }
                >
                  <header className="print-card__top">
                    <h3>{print.name}</h3>
                    <span>{print.period}</span>
                  </header>
                  <p className={`print-card__value print-card__value--${print.tone}`}>{print.value}</p>
                  <p className="print-card__metric">{print.metric}</p>
                  <div className="print-card__spark" aria-hidden="true">
                    <span className="print-card__spark-empty">— no series yet —</span>
                  </div>
                  <p className="print-card__note">{print.note}</p>
                  <EvidenceLink ids={print.evidenceIds} />
                </article>
              ))}
            </div>
          </div>
        )
      })}
    </section>
  )
}
