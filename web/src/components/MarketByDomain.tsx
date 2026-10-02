import { useState } from 'react'
import {
  eventSummaryForSupplier,
  formatFiledDate,
  formatHeadlineCompact,
  formatMonthYear,
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

/**
 * Fix pass 4, item 5: every growth figure signed, one rendering path for
 * "+34%", "36%", "1%", "-1.5%" and "11.2%" alike — the data carries whatever
 * precision each company's own report gives (do not invent a decimal here;
 * only the sign and the glyph are normalised). A true minus sign (U+2212)
 * reads more deliberately than a hyphen in a column of numbers; the
 * underlying number is unchanged, so `parseGrowthPercent` (sorting) and the
 * raw data are untouched.
 */
function signedGrowth(raw: string | undefined): string {
  if (!raw) return ''
  const match = raw.match(/^(-)?\+?(\d+(?:\.\d+)?)%$/)
  if (!match) return raw
  const [, negative, digits] = match
  if (negative) return `−${digits}%`
  if (Number(digits) === 0) return `${digits}%`
  return `+${digits}%`
}

/**
 * Fix pass 4, item 9: the ownership/last-round cell's trailing date ("Series
 * D $300M · Sep 2026", "Acquired by ServiceNow · Apr 2026") as a real
 * `<time datetime>` element instead of plain text, mirroring
 * `formatOwnershipCompact`'s own branches (derive.ts) rather than parsing its
 * output — this file does not own data/**, so the one small duplication
 * stays here instead of changing that shared formatter's return shape.
 */
function capitalParts(supplier: TrackerSupplier): { prefix: string; date: string; dateText: string } {
  const isoDate = capitalDateFor(supplier)
  const full = formatOwnershipCompact(supplier)
  if (!isoDate) return { prefix: full, date: '', dateText: '' }
  const dateText =
    supplier.lastRound
      ? formatMonthYear(supplier.lastRound.date)
      : formatMonthYear(supplier.ownership?.closed ?? supplier.ownership?.announced)
  if (!dateText || !full.endsWith(dateText)) return { prefix: full, date: '', dateText: '' }
  return { prefix: full.slice(0, full.length - dateText.length).replace(/\s*·\s*$/, '').trimEnd(), date: isoDate, dateText }
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
      <span className="tracker-figure__value">{signedGrowth(period.yoyGrowth)}</span>{' '}
      <span className="tracker-figure__period">
        <time dateTime={period.periodEnd}>{formatShortQuarter(period.periodEnd)}</time>
        {releaseDate ? (
          <>
            {' '}
            {'·'} filed <time dateTime={releaseDate}>{formatFiledDate(releaseDate)}</time>
          </>
        ) : null}
      </span>
      <EvidenceLink ids={period.evidenceIds} variant="compact" context={context} />
    </span>
  )
}

function CapitalCell({ supplier }: { supplier: TrackerSupplier }) {
  const { prefix, date, dateText } = capitalParts(supplier)
  const evidenceIds = supplier.lastRound?.evidenceIds ?? supplier.ownership?.evidenceIds
  return (
    <span className="tracker-figure">
      <span className="tracker-figure__value">
        {prefix}
        {date ? (
          <>
            {' '}
            {'·'} <time dateTime={date}>{dateText}</time>
          </>
        ) : null}
      </span>
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
  const suppliers = suppliersForDomain(domainId)
  const sorted = sortSuppliers(suppliers, sort)
  const median = medianRevenueGrowthForDomain(domainId)
  // Fix pass 4, item 6: every domain needs a reference point, not just the
  // six that happened to have two or more public suppliers already.
  // `medianRevenueGrowthForDomain` returns null below that count; this
  // counts how many public (or publicly-reporting segment) suppliers the
  // domain actually has, so the footer line can say which case it is
  // rather than showing nothing.
  const publicSupplierCount = suppliers.filter(
    (supplier) => supplier.kind === 'public' || supplier.kind === 'segment',
  ).length

  function toggleSort(key: SortKey) {
    setSort((current) =>
      current.key === key
        ? { key, direction: current.direction === 'asc' ? 'desc' : 'asc' }
        : { key, direction: 'asc' },
    )
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
              const shortName = shortSupplierName(supplier.name)
              const claimsAnchor = !anchoredSupplierIds.has(supplier.id)
              if (claimsAnchor) anchoredSupplierIds.add(supplier.id)
              return (
                <tr key={supplier.id} id={claimsAnchor ? `s-${supplier.id}` : undefined}>
                  {/* Fix pass 4, item 3: this used to be a tap-to-expand
                      button hiding every other cell until pressed (see
                      index.css's @media (max-width: 640px) block for the
                      replacement) — every cell now renders unconditionally,
                      so the supplier cell is plain text, not a control. */}
                  <td data-label="Supplier">
                    <span className="tracker-row__name" title={supplier.name}>
                      {shortName}
                    </span>
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
                          {count} {'·'} latest {latest!.type},{' '}
                          <time dateTime={latest!.date}>{formatShortDate(latest!.date)}</time>
                        </span>
                        <EvidenceLink ids={latest!.evidenceIds} variant="compact" context="Latest event" />
                      </span>
                    )}
                  </td>
                </tr>
              )
            })}
          </tbody>
          {/* Fix pass 4, item 6: every domain gets a reference-point row —
              the median where there are two or more public suppliers to
              take a median of, and a plain count otherwise, rather than
              nothing. Six domains (security operations, email,
              application security and AI security among them) used to show
              neither. */}
          <tfoot>
            <tr className="tracker-table__median">
              <td colSpan={COLUMNS.length}>
                {median !== null
                  ? `Median revenue growth of tracked public suppliers: ${signedGrowth(`${median}%`)}`
                  : publicSupplierCount === 1
                    ? 'One public supplier in this domain; no median shown.'
                    : 'No public suppliers in this domain; no median shown.'}
              </td>
            </tr>
          </tfoot>
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
 * instead of a name-carrying button, tighter column headers, and a domain
 * index at the top. Fix pass 4, item 3: a phone-width row used to collapse
 * to one figure behind a tap; every cell now renders unconditionally, and
 * index.css's `@media (max-width: 640px)` block only changes where each
 * cell is drawn (a two-column, three-line card), not whether it renders.
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
        {/* Coordinator follow-up, same first-screen fix as SiteMasthead.tsx:
            this paragraph was another ~105px sitting above the first table
            at 390px. Same <details> pattern — forced open with no visible
            summary above 640px, so desktop is unchanged and the words never
            leave the page, just the initial phone view. */}
        <details className="market-definition">
          <summary>What &ldquo;revenue growth&rdquo; means here</summary>
          <p>
            &ldquo;Revenue growth&rdquo; is the year-over-year change in a company&rsquo;s own reported
            GAAP revenue for the quarter named, taken from its SEC filings or its own press release.
            Figures are listed, not ranked; being listed is not a recommendation and being absent is not
            a criticism.
          </p>
        </details>
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
