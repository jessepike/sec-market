import { useState } from 'react'
import { shortSupplierName } from '../data/tracker/names'
import { certifiedGrowth, domainMomentum, formatPercent, formatPoints, healthFacts, marketMedian } from '../data/tracker/momentum'
import type { DomainMomentum, MomentumRow } from '../data/tracker/momentum'
import { typeName } from '../data/tracker/typeNames'
import { companyPath } from '../data/companyPages'
import type { TrackerSupplier } from '../data/tracker/suppliers'

const domains = domainMomentum()
const withRows = domains.filter(d => d.rows.length > 0)
const withoutRows = domains.filter(d => d.rows.length === 0)
const all = certifiedGrowth.map(r => r.latest)
const lo = Math.min(0, Math.floor(Math.min(...all) / 10) * 10)
const hi = Math.max(10, Math.ceil(Math.max(...all) / 10) * 10)
const pos = (v: number) => `${((v - lo) / (hi - lo)) * 100}%`
const ends = certifiedGrowth.map(r => r.supplier.revenue!.latest.periodEnd).sort()
const hasHealth = Object.keys(healthFacts.suppliers).length > 0

function Health({ row }: { row: MomentumRow }) {
  const h = row.health
  const cell = (label: string, text: string | null, title?: string, href?: string) => <span className="momentum__metric" title={title}>
    <span className="momentum__metric-label">{label}</span>
    {text === null ? <span className="momentum__na">Not reported</span> : href ? <a href={href} target="_blank" rel="noreferrer">{text}</a> : text}
  </span>
  if (!hasHealth) return null
  return <>
    {cell('Operating margin', h?.operatingMargin ? formatPercent(h.operatingMargin.value) : null, h?.operatingMargin ? `Four quarters to ${h.operatingMargin.periodEnd}` : undefined, h?.operatingMargin?.sourceUrl)}
    {cell('Free cash flow margin', h?.fcfMargin ? formatPercent(h.fcfMargin.value) : null, h?.fcfMargin ? `Four quarters to ${h.fcfMargin.periodEnd}` : undefined, h?.fcfMargin?.sourceUrl)}
  </>
}

type Open = ((id: string) => void) | undefined

/** A company name: opens the supplier record on the front page, or links to the company page elsewhere. */
function Name({ supplier, open, className = '' }: { supplier: TrackerSupplier; open: Open; className?: string }) {
  // Only ranked rows carry a title; names in the collapsed list stay out of title lookups.
  const title = className ? supplier.name : undefined
  return open
    ? <button type="button" className={`desk-supplier-link ${className}`} title={title} onClick={() => open(supplier.id)}>{shortSupplierName(supplier.name)}</button>
    : <a className={`desk-supplier-link ${className}`} title={title} href={companyPath(supplier.id)}>{shortSupplierName(supplier.name)}</a>
}

function Row({ row, median, openSupplier, highlight }: { row: MomentumRow; median: number | null; openSupplier: Open; highlight?: string }) {
  const { supplier, latest, change } = row
  const rev = supplier.revenue!.latest
  return <li className={`momentum__row${highlight === supplier.id ? ' is-highlight' : ''}`} aria-current={highlight === supplier.id ? 'true' : undefined}>
    <Name supplier={supplier} open={openSupplier} className="momentum__name" />
    <div className="momentum__bar" role="img" aria-label={`${supplier.name}: ${formatPercent(latest)} year-over-year revenue growth, quarter ended ${rev.periodEnd}${median !== null ? `; domain median ${formatPercent(median)}` : ''}`}>
      <i className="momentum__zero" style={{ left: pos(0) }} />
      <i className="momentum__fill" style={{ left: pos(Math.min(0, latest)), width: `${(Math.abs(latest) / (hi - lo)) * 100}%` }} />
      {median !== null && <i className="momentum__median" style={{ left: pos(median) }} />}
    </div>
    <span className="momentum__growth">{formatPercent(latest)}</span>
    <span className="momentum__change" title={change === null ? 'No prior quarter on file' : `Prior quarter ${supplier.revenue!.prior!.yoyGrowth}, quarter ended ${supplier.revenue!.prior!.periodEnd}`}>
      {change === null ? '–' : <><span aria-hidden="true">{change > 0 ? '▲' : change < 0 ? '▼' : '■'}</span> {formatPoints(change)}</>}
    </span>
    <Health row={row} />
  </li>
}

export function DomainCard({ d, openSupplier, highlight }: { d: DomainMomentum; openSupplier?: (id: string) => void; highlight?: string }) {
  return <article className="momentum__domain" aria-labelledby={`momentum-${d.id}`}>
    <div className="momentum__domain-head"><h3 id={`momentum-${d.id}`}>{d.name}</h3>
      <span>{d.median !== null ? <>Median <strong>{formatPercent(d.median)}</strong> across {d.rows.length} filers</> : '1 SEC filer, no median'}</span></div>
    <div className={`momentum__cols${hasHealth ? ' has-health' : ''}`} aria-hidden="true"><span>Company</span><span>Revenue growth, year over year</span><span /><span>vs prior quarter</span>
      {hasHealth && <><span>Operating margin</span><span>Free cash flow margin</span></>}</div>
    <ul className={`momentum__rows${hasHealth ? ' has-health' : ''}`}>{d.rows.map(row => <Row key={row.supplier.id} row={row} median={d.median} openSupplier={openSupplier} highlight={highlight} />)}</ul>
    {d.others.length > 0 && <details className="momentum__others" open={d.others.some(o => o.supplier.id === highlight) || undefined}><summary>{d.others.length} more {d.others.length === 1 ? 'company' : 'companies'} without SEC financials</summary>
      <ul>{d.others.map(o => <li key={o.supplier.id} className={highlight === o.supplier.id ? 'is-highlight' : undefined}><Name supplier={o.supplier} open={openSupplier} />
        <span>{o.fact}</span>
        <span className="desk-note">{o.latestEvent ? <>{typeName(o.latestEvent.type)} <time dateTime={o.latestEvent.date}>{o.latestEvent.date}</time>{o.eventCount > 1 ? ` · ${o.eventCount} events in 12 months` : ''}</> : 'No events in 12 months'}</span></li>)}</ul>
    </details>}
  </article>
}

export function MomentumByDomain({ openSupplier }: { openSupplier: (id: string) => void }) {
  const [expanded, setExpanded] = useState(false)
  return <section id="momentum" className={`desk-panel momentum${expanded ? ' is-expanded' : ''}`} aria-labelledby="momentum-heading">
    <div className="desk-panel__head"><h2 id="momentum-heading">Revenue momentum by domain</h2>
      <span>{marketMedian !== null && <>All {certifiedGrowth.length} SEC filers: median {formatPercent(marketMedian)}</>}</span></div>
    <p className="desk-note">Year-over-year revenue growth for the latest quarter, highest first, re-derived from SEC filings. Quarters end {ends[0]} to {ends.at(-1)}; fiscal calendars differ. The arrow shows the change from the prior quarter&rsquo;s growth rate, in percentage points. The tick on each bar is the domain median. A company can appear in more than one domain.
      {hasHealth && <> Operating margin and free cash flow margin cover the four quarters to the same quarter end. They are computed from the same SEC filings but are not yet part of the certified check. Debt is not shown yet: SEC tags for it are not consistent enough across these 16 filers.</>}
      {' '}Private companies, segments and non-SEC filers have no comparable financials here; their events are listed under each domain.</p>
    <div className="momentum__grid">{withRows.map(d => <DomainCard key={d.id} d={d} openSupplier={openSupplier} />)}</div>
    <button type="button" className="momentum__mobile-toggle" aria-expanded={expanded} onClick={() => setExpanded(v => !v)}>{expanded ? 'Show fewer domains' : `Show all ${withRows.length} domains`}</button>
    {withoutRows.length > 0 && <p className="desk-note momentum__none">No SEC filer in {withoutRows.map(d => d.name).join(', ')}. Their companies are in the domain list below.</p>}
  </section>
}
