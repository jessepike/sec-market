import { formatShortDate } from '../data/dates'
import type { Issue, IssueItem, Lane } from '../data/types'
import { useVendorLens } from '../context/useVendorLens'
import { EvidenceLink } from './EvidenceLink'

/** Section id and display title per lane, in the fixed Lane order (types.ts). */
const LANE_META: Record<Lane, { id: string; title: string }> = {
  formation: { id: 'formation', title: 'Formation' },
  absorption: { id: 'absorption', title: 'Absorption' },
  prints: { id: 'prints-this-week', title: 'Prints' },
  capital: { id: 'capital', title: 'Capital and backdrop' },
}

function itemMatchesLens(item: IssueItem, activeSlugs: string[]): boolean {
  return (item.vendors ?? []).some((vendor) => activeSlugs.includes(vendor))
}

/**
 * Vendor lens (SEC-031): `useVendorLens()` returns its inactive fallback
 * (`activeSlugs: null`) whenever this renders outside a VendorLensProvider —
 * the issue permalink page, and scripts/verify-issue.ts's check 10 — so this
 * component's unfiltered render is byte-identical to before the lens existed
 * in both of those places.
 */
export function IssueLanes({ issue }: { issue: Issue }) {
  const { activeSlugs, clear } = useVendorLens()
  const isFiltered = activeSlugs !== null

  const totalItems = issue.sections.reduce((sum, section) => sum + section.items.length, 0)
  const shownItems = isFiltered
    ? issue.sections.reduce(
        (sum, section) => sum + section.items.filter((item) => itemMatchesLens(item, activeSlugs)).length,
        0,
      )
    : totalItems

  return (
    <>
      {isFiltered ? (
        <p className="issue-lane__filter-status" role="status">
          Vendor lens active · Showing {shownItems} of {totalItems} items ·{' '}
          <a
            href="#"
            onClick={(event) => {
              event.preventDefault()
              clear()
            }}
          >
            Clear
          </a>
        </p>
      ) : null}
      {issue.sections.map((section) => {
        const meta = LANE_META[section.lane]
        const items = isFiltered
          ? section.items.filter((item) => itemMatchesLens(item, activeSlugs))
          : section.items
        return (
          <section
            key={section.lane}
            id={meta.id}
            className="issue-lane"
            aria-labelledby={`${meta.id}-heading`}
          >
            <h2 id={`${meta.id}-heading`}>{meta.title}</h2>
            {section.intro ? <p className="issue-lane__intro">{section.intro}</p> : null}
            {items.length === 0 ? (
              <p className="issue-lane__empty">
                {isFiltered ? 'No items match the vendor lens.' : 'Nothing new this week.'}
              </p>
            ) : (
              <ul className="issue-lane__list">
                {items.map((item) => (
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
