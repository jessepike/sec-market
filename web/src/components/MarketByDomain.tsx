import { useState } from 'react'
import {
  eventSummaryForSupplier,
  formatFiledDate,
  formatHeadlineCompact,
  formatOwnershipCompact,
  formatShortDate,
  formatShortQuarter,
  medianRevenueGrowthForDomain,
  parseGrowthPercent,
  shortSupplierName,
  suppliersForDomain,
} from '../data/tracker/derive'
import { trackerDomains } from '../data/tracker/domains'
import type { RevenuePeriod, RevenuePeriodLatest, TrackerSupplier } from '../data/tracker/suppliers'
import { EvidenceLink } from './EvidenceLink'

type SortKey = 'name' | 'growthLatest' | 'growthPrior' | 'headline' | 'capital' | 'events'
type SortDirection = 'asc' | 'desc'

interface SortState {
  key: SortKey
  direction: SortDirection
}

// Density pass (coordinator instruction after the step 5 build): shorter
// headers so a column fits its figure instead of wrapping onto three lines.
const COLUMNS: { key: SortKey; label: string }[] = [
  { key: 'name', label: 'Supplier' },
  { key: 'growthLatest', label: 'Rev. growth' },
  { key: 'growthPrior', label: 'Prior q' },
  { key: 'headline', label: 'Own metric' },
  { key: 'capital', label: 'Ownership or last round' },
  { key: 'events', label: 'Events, 12 mo.' },
]

function capitalDateFor(supplier: TrackerSupplier): string {
  return supplier.lastRound?.date ?? supplier.ownership?.closed ?? supplier.ownership?.announced ?? ''
}

function sortValue(supplier: TrackerSupplier, key: SortKey): string | number {
  switch (key) {
    case 'name':
      return supplier.name.toLowerCase()
    case 'growthLatest':
      return parseGrowthPercent(supplier.revenue?.latest.yoyGrowth) ?? Number.NEGATIVE_INFINITY
    case 'growthPrior':
      return parseGrowthPercent(supplier.revenue?.prior?.yoyGrowth) ?? Number.NEGATIVE_INFINITY
    case 'headline':
      return supplier.headlineMetric?.value ?? ''
    case 'capital':
      return capitalDateFor(supplier)
    case 'events':
      return eventSummaryForSupplier(supplier.id).count
  }
}

function sortSuppliers(suppliers: TrackerSupplier[], sort: SortState): TrackerSupplier[] {
  const sorted = suppliers.slice().sort((a, b) => {
    const av = sortValue(a, sort.key)
    const bv = sortValue(b, sort.key)
    if (typeof av === 'number' && typeof bv === 'number') return av - bv
    return String(av).localeCompare(String(bv))
  })
  if (sort.direction === 'desc') sorted.reverse()
  return sorted
}

/**
 * One growth figure ("+26%") with its muted mono period ("Q Jul 26") and a
 * compact source link — used for both the latest and the prior quarter
 * column. AUTO-001 fix pass 2, item 7: the latest-quarter figure also
 * carries the report's filing date ("Q Jul 26 · filed 26 Aug") — a blind
 * scorer cannot tell how stale a figure is without knowing when it was
 * actually filed, not just which quarter it describes. `prior` periods have
 * no `releaseDate` in the data (research only recorded the filing date for
 * the quarter actually reported on), so they show the period alone.
 */
function GrowthCell({ period, context }: { period: RevenuePeriod | undefined; context: string }) {
  if (!period) return <span className="tracker-figure--empty">{'–'}</span>
  // `prior` periods are plain `RevenuePeriod`, with no `releaseDate` field;
  // only `RevenuePeriodLatest` carries one. The cast is read-only — it never
  // fabricates a date, it just lets a `latest` period's real field through.
  const releaseDate = (period as Partial<RevenuePeriodLatest>).releaseDate
  return (
    <span className="tracker-figure">
      <span className="tracker-figure__value">{period.yoyGrowth}</span>{' '}
      <span className="tracker-figure__period">
        {formatShortQuarter(period.periodEnd)}
        {releaseDate ? <> {'·'} filed {formatFiledDate(releaseDate)}</> : null}
      </span>
      <EvidenceLink ids={period.evidenceIds} variant="compact" context={context} />
    </span>
  )
}

function CapitalCell({ supplier }: { supplier: TrackerSupplier }) {
  const text = formatOwnershipCompact(supplier)
  const evidenceIds = supplier.lastRound?.evidenceIds ?? supplier.ownership?.evidenceIds
  return (
    <span className="tracker-figure">
      <span className="tracker-figure__value">{text}</span>
      {evidenceIds && evidenceIds.length > 0 ? (
        <EvidenceLink ids={evidenceIds} variant="compact" context="Ownership" />
      ) : null}
    </span>
  )
}

function DomainTable({
  domainId,
  domainName,
  anchoredSupplierIds,
}: {
  domainId: string
  domainName: string
  /**
   * A handful of suppliers (Palo Alto Networks, CrowdStrike, Check Point's
   * SASE segment) carry more than one `domainId` and so render a row in more
   * than one domain's table. `id="s-<supplierId>"` (item 8) must stay a
   * document-unique id — two elements sharing one id is invalid HTML and
   * makes the *second* occurrence unreachable by anchor anyway, since the
   * browser jumps to the first match. This set is created once per page
   * render in `MarketByDomain` and threaded through every `DomainTable` in
   * `trackerDomains` order, so only the first table a given supplier appears
   * in claims the anchor; later occurrences render the row without one.
   */
  anchoredSupplierIds: Set<string>
}) {
  const [sort, setSort] = useState<SortState>({ key: 'name', direction: 'asc' })
  // Phone only (see the @media (max-width: 640px) block in index.css) — a
  // supplier row is collapsed to its name and one summary figure until this
  // set says otherwise. Empty by default so the server render and the
  // client's first render match. Harmless on desktop: the media query is
  // the only thing that ever hides a cell.
  const [expanded, setExpanded] = useState<ReadonlySet<string>>(() => new Set<string>())
  const suppliers = suppliersForDomain(domainId)
  const sorted = sortSuppliers(suppliers, sort)
  const median = medianRevenueGrowthForDomain(domainId)

  function toggleSort(key: SortKey) {
    setSort((current) =>
      current.key === key
        ? { key, direction: current.direction === 'asc' ? 'desc' : 'asc' }
        : { key, direction: 'asc' },
    )
  }

  function toggleExpanded(supplierId: string) {
    setExpanded((current) => {
      const next = new Set(current)
      if (next.has(supplierId)) next.delete(supplierId)
      else next.add(supplierId)
      return next
    })
  }

  return (
    <article id={`domain-${domainId}`} className="tracker-domain">
      <h3 className="tracker-domain__name">{domainName}</h3>
      <div className="table-scroll tracker-table-scroll">
        <table className="tracker-table" data-domain={domainId}>
          <caption className="visually-hidden">Tracked suppliers in {domainName}</caption>
          <thead>
            <tr>
              {COLUMNS.map((column) => (
                <th key={column.key} scope="col" aria-sort={sort.key === column.key ? (sort.direction === 'asc' ? 'ascending' : 'descending') : 'none'}>
                  <button type="button" className="tracker-table__sort" onClick={() => toggleSort(column.key)}>
                    {column.label}
                    <span aria-hidden="true" className="tracker-table__sort-glyph">
                      {sort.key === column.key ? (sort.direction === 'asc' ? '↑' : '↓') : ''}
                    </span>
                  </button>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sorted.map((supplier) => {
              const { count, latest } = eventSummaryForSupplier(supplier.id)
              const isExpanded = expanded.has(supplier.id)
              const shortName = shortSupplierName(supplier.name)
              // Phone's collapsed-row summary: latest revenue growth if the
              // company reports one, otherwise its ownership state.
              const rowSummary = supplier.revenue?.latest.yoyGrowth ?? formatOwnershipCompact(supplier)
              const claimsAnchor = !anchoredSupplierIds.has(supplier.id)
              if (claimsAnchor) anchoredSupplierIds.add(supplier.id)
              return (
                <tr
                  key={supplier.id}
                  id={claimsAnchor ? `s-${supplier.id}` : undefined}
                  className={isExpanded ? 'tracker-row--expanded' : undefined}
                >
                  <td data-label="Supplier">
                    <button
                      type="button"
                      className="tracker-row__toggle"
                      aria-expanded={isExpanded}
                      onClick={() => toggleExpanded(supplier.id)}
                    >
                      <span className="tracker-row__name" title={supplier.name}>
                        {shortName}
                      </span>
                      <span className="tracker-row__summary">{rowSummary}</span>
                      <span className="tracker-row__chevron" aria-hidden="true">
                        {isExpanded ? '−' : '+'}
                      </span>
                    </button>
                  </td>
                  <td data-label="Rev. growth" className="tracker-cell--numeric">
                    <GrowthCell period={supplier.revenue?.latest} context="Revenue growth, latest quarter" />
                  </td>
                  <td data-label="Prior q" className="tracker-cell--numeric">
                    <GrowthCell period={supplier.revenue?.prior} context="Revenue growth, prior quarter" />
                  </td>
                  <td data-label="Own metric">
                    {supplier.headlineMetric ? (
                      <span className="tracker-figure">
                        <span className="tracker-figure__value">{formatHeadlineCompact(supplier)}</span>
                        <EvidenceLink ids={supplier.headlineMetric.evidenceIds} variant="compact" context="Own headline metric" />
                      </span>
                    ) : (
                      <span className="tracker-figure--empty">{'–'}</span>
                    )}
                  </td>
                  <td data-label="Ownership or last round">
                    <CapitalCell supplier={supplier} />
                  </td>
                  <td data-label="Events, 12 mo.">
                    {count === 0 ? (
                      <span className="tracker-figure--empty">0</span>
                    ) : (
                      <span className="tracker-figure">
                        <span className="tracker-figure__value">
                          {count} {'·'} latest {latest!.type}, {formatShortDate(latest!.date)}
                        </span>
                        <EvidenceLink ids={latest!.evidenceIds} variant="compact" context="Latest event" />
                      </span>
                    )}
                  </td>
                </tr>
              )
            })}
          </tbody>
          {median !== null ? (
            <tfoot>
              <tr className="tracker-table__median">
                <td colSpan={COLUMNS.length}>
                  Median revenue growth of tracked public suppliers: {median >= 0 ? '+' : ''}
                  {median}%
                </td>
              </tr>
            </tfoot>
          ) : null}
        </table>
      </div>
    </article>
  )
}

/** A compact "jump to a domain" index — twelve links with supplier counts, at the top of the section so a reader does not have to scroll past every table to reach the one they want. */
function DomainIndex() {
  return (
    <nav className="tracker-domain-index" aria-label="Jump to a domain">
      <ul>
        {trackerDomains.map((domain) => (
          <li key={domain.id}>
            <a href={`#domain-${domain.id}`}>
              {domain.name}{' '}
              <span className="tracker-domain-index__count">({suppliersForDomain(domain.id).length})</span>
            </a>
          </li>
        ))}
      </ul>
    </nav>
  )
}

/**
 * "The market by domain" — autonomy-coverage-plan.md §3a. Twelve domains,
 * each a sortable table of its tracked suppliers, built from
 * data/tracker/{domains,suppliers,events}.ts. Default order is alphabetical
 * by supplier name; a reader can re-sort any column, the site does not pick
 * one for them.
 *
 * Density pass (coordinator instruction, after the initial step 5 build):
 * short supplier names with the legal name kept in the `title` attribute
 * and in evidence.ts, one-line compact cells with a "src" evidence link
 * instead of a name-carrying button, tighter column headers, a domain index
 * at the top, and a phone-width collapsed-row pattern — see index.css's
 * `@media (max-width: 640px)` block and DomainTable's `expanded` state
 * above.
 *
 * AUTO-001 fix pass 2, item 8: every supplier row carries a stable anchor,
 * `id="s-<supplierId>"`, so a single figure can be linked directly rather
 * than only "somewhere in this domain's table" — see index.css's
 * `tr[id] { scroll-margin-top: ... }` rule, which keeps the sticky header
 * from covering the row a link lands on. A few suppliers (Palo Alto
 * Networks, CrowdStrike, Check Point's SASE segment) sit in more than one
 * domain and so render more than one row; `anchoredSupplierIds` (created
 * fresh on every render, threaded through each `DomainTable` in
 * `trackerDomains` order) makes sure only the first such row claims the id,
 * keeping it a valid, document-unique anchor.
 */
export function MarketByDomain() {
  const anchoredSupplierIds = new Set<string>()
  return (
    <section id="market" className="tracker-market" aria-labelledby="market-heading">
      <div className="section-heading">
        <h2 id="market-heading">The market by domain</h2>
        <p>
          &ldquo;Revenue growth&rdquo; is the year-over-year change in a company&rsquo;s own reported
          GAAP revenue for the quarter named, taken from its SEC filings or its own press release.
          Figures are listed, not ranked; being listed is not a recommendation and being absent is not
          a criticism.
        </p>
      </div>
      <DomainIndex />
      <div className="tracker-domains">
        {trackerDomains.map((domain) => (
          <DomainTable
            key={domain.id}
            domainId={domain.id}
            domainName={domain.name}
            anchoredSupplierIds={anchoredSupplierIds}
          />
        ))}
      </div>
    </section>
  )
}
