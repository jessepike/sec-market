import { formatShortDate } from '../data/dates'
import type { Issue, Lane } from '../data/types'
import { EvidenceLink } from './EvidenceLink'

/** Section id and display title per lane, in the fixed Lane order (types.ts). */
const LANE_META: Record<Lane, { id: string; title: string }> = {
  formation: { id: 'formation', title: 'Formation' },
  absorption: { id: 'absorption', title: 'Absorption' },
  prints: { id: 'prints-this-week', title: 'Prints' },
  capital: { id: 'capital', title: 'Capital and backdrop' },
}

export function IssueLanes({ issue }: { issue: Issue }) {
  return (
    <>
      {issue.sections.map((section) => {
        const meta = LANE_META[section.lane]
        return (
          <section
            key={section.lane}
            id={meta.id}
            className="issue-lane"
            aria-labelledby={`${meta.id}-heading`}
          >
            <h2 id={`${meta.id}-heading`}>{meta.title}</h2>
            {section.intro ? <p className="issue-lane__intro">{section.intro}</p> : null}
            {section.items.length === 0 ? (
              <p className="issue-lane__empty">Nothing new this week.</p>
            ) : (
              <ul className="issue-lane__list">
                {section.items.map((item) => (
                  <li key={item.id} className="issue-lane__item">
                    <p className="issue-lane__headline">
                      {item.headline}
                      {item.background ? (
                        <span className="issue-lane__background"> · background</span>
                      ) : null}
                    </p>
                    <p className="issue-lane__meta">
                      <time dateTime={item.date}>{formatShortDate(item.date)}</time>
                    </p>
                    {item.why ? <p className="issue-lane__why">{item.why}</p> : null}
                    <EvidenceLink ids={item.evidenceIds} />
                  </li>
                ))}
              </ul>
            )}
          </section>
        )
      })}
    </>
  )
}
