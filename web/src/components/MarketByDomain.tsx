import { useState } from 'react'
import {
  eventSummaryForSupplier,
  medianRevenueGrowthForDomain,
  parseGrowthPercent,
  suppliersForDomain,
} from '../data/tracker/derive'
import { trackerDomains } from '../data/tracker/domains'
import type { TrackerSupplier } from '../data/tracker/suppliers'
import { formatIsoDate } from '../utils/formatDate'
import { EvidenceLink } from './EvidenceLink'

type SortKey = 'name' | 'growthLatest' | 'growthPrior' | 'headline' | 'capital' | 'events'
type SortDirection = 'asc' | 'desc'

interface SortState {
  key: SortKey
  direction: SortDirection
}

const COLUMNS: { key: SortKey; label: string }[] = [
  { key: 'name', label: 'Supplier' },
  { key: 'growthLatest', label: 'Revenue growth, latest quarter' },
  { key: 'growthPrior', label: 'Revenue growth, prior quarter' },
  { key: 'headline', label: "Company's own headline metric" },
  { key: 'capital', label: 'Last funding round or ownership' },
  { key: 'events', label: 'Events, last 12 months' },
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
      return parseGrowthPercent(supplier.revenue?.prior.yoyGrowth) ?? Number.NEGATIVE_INFINITY
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

function CapitalCell({ supplier }: { supplier: TrackerSupplier }) {
  if (supplier.lastRound) {
    const round = supplier.lastRound
    return (
      <span data-label="Last funding round or ownership">
        {round.stage} {round.amount} · {formatIsoDate(round.date)}
        {round.lead ? ` · ${round.lead}` : ''}
        <EvidenceLink ids={round.evidenceIds} />
      </span>
    )
  }
  if (supplier.ownership) {
    const own = supplier.ownership
    return (
      <span data-label="Last funding round or ownership">
        {own.status}
        {own.closed ? ` (closed ${formatIsoDate(own.closed)})` : ''}
        <EvidenceLink ids={own.evidenceIds} />
      </span>
    )
  }
  return <span data-label="Last funding round or ownership">Not disclosed</span>
}

function DomainTable({ domainId, domainName }: { domainId: string; domainName: string }) {
  const [sort, setSort] = useState<SortState>({ key: 'name', direction: 'asc' })
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
              return (
                <tr key={supplier.id}>
                  <td data-label="Supplier">{supplier.name}</td>
                  <td data-label="Revenue growth, latest quarter">
                    {supplier.revenue ? (
                      <>
                        {supplier.revenue.latest.yoyGrowth} ({supplier.revenue.latest.periodEnd})
                        <EvidenceLink ids={supplier.revenue.latest.evidenceIds} />
                      </>
                    ) : (
                      'No comparable figure'
                    )}
                  </td>
                  <td data-label="Revenue growth, prior quarter">
                    {supplier.revenue ? (
                      <>
                        {supplier.revenue.prior.yoyGrowth} ({supplier.revenue.prior.periodEnd})
                        <EvidenceLink ids={supplier.revenue.prior.evidenceIds} />
                      </>
                    ) : (
                      'No comparable figure'
                    )}
                  </td>
                  <td data-label="Company's own headline metric">
                    {supplier.headlineMetric ? (
                      <>
                        {supplier.headlineMetric.label}: {supplier.headlineMetric.value} (
                        {supplier.headlineMetric.period})
                        <EvidenceLink ids={supplier.headlineMetric.evidenceIds} />
                      </>
                    ) : (
                      'Not disclosed'
                    )}
                  </td>
                  <td data-label="Last funding round or ownership">
                    <CapitalCell supplier={supplier} />
                  </td>
                  <td data-label="Events, last 12 months">
                    {count === 0
                      ? 'None found'
                      : `${count} · latest ${latest!.type}, ${formatIsoDate(latest!.date)}`}
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

/**
 * "The market by domain" — autonomy-coverage-plan.md §3a. Twelve domains,
 * each a sortable table of its tracked suppliers, built from
 * data/tracker/{domains,suppliers,events}.ts. Default order is alphabetical
 * by supplier name; a reader can re-sort any column, the site does not pick
 * one for them.
 */
export function MarketByDomain() {
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
      <div className="tracker-domains">
        {trackerDomains.map((domain) => (
          <DomainTable key={domain.id} domainId={domain.id} domainName={domain.name} />
        ))}
      </div>
    </section>
  )
}
