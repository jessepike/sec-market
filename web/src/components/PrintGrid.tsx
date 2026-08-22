import { printGroups, vendorPrints } from '../data/prints'
import { EvidenceLink } from './EvidenceLink'

const COUNT_WORDS = [
  'zero',
  'one',
  'two',
  'three',
  'four',
  'five',
  'six',
  'seven',
  'eight',
  'nine',
  'ten',
] as const

function countWord(n: number): string {
  if (n >= 1 && n <= 10) return COUNT_WORDS[n]
  return String(n)
}

export function PrintGrid() {
  const printCount = vendorPrints.length
  const domainCount = printGroups.filter((group) =>
    vendorPrints.some((print) => print.group === group),
  ).length

  return (
    <section id="prints" className="print-grid" aria-labelledby="prints-heading">
      <div className="section-heading">
        <p className="eyebrow">
          The full scorecard · {countWord(printCount)} prints across {countWord(domainCount)}{' '}
          domains
        </p>
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
