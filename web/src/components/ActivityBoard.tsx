import { activityItems } from '../data/activity'
import type { ActivityItem } from '../data/types'
import { formatIsoDate } from '../utils/formatDate'
import { EvidenceLink } from './EvidenceLink'

function byDateDesc(a: ActivityItem, b: ActivityItem) {
  return b.date.localeCompare(a.date)
}

function ActivityRows({ items }: { items: ActivityItem[] }) {
  return (
    <div className="activity-list">
      {items.map((item) => (
        <details key={item.id} className="activity-row">
          <summary>
            <span className="activity-row__headline">{item.headline}</span>
            <span className="activity-row__value">{item.value}</span>
            <time dateTime={item.date}>{formatIsoDate(item.date)}</time>
          </summary>
          <div className="activity-row__body">
            <p className="activity-row__meta">
              {item.actor} · {item.domain}
            </p>
            <p>{item.note}</p>
            <EvidenceLink ids={item.evidenceIds} />
          </div>
        </details>
      ))}
    </div>
  )
}

export function ActivityBoard() {
  const lead = activityItems
    .filter((item) => item.surface === 'lead')
    .sort((a, b) => (a.leadOrder ?? 99) - (b.leadOrder ?? 99))
  const more = activityItems.filter((item) => item.surface === 'more').sort(byDateDesc)
  const background = activityItems.filter((item) => item.surface === 'background').sort(byDateDesc)

  return (
    <section id="activity" className="activity-board" aria-labelledby="activity-heading">
      <div className="section-heading">
        <h2 id="activity-heading">M&A and startups</h2>
      </div>
      <ActivityRows items={lead} />
      {more.length > 0 ? (
        <details className="depth activity-more">
          <summary>More in this window ({more.length})</summary>
          <ActivityRows items={more} />
        </details>
      ) : null}
      {background.length > 0 ? (
        <details className="depth activity-more">
          <summary>Background — last disclosed raises ({background.length})</summary>
          <ActivityRows items={background} />
        </details>
      ) : null}
    </section>
  )
}
