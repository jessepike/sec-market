import { useState } from 'react'
import type { ReactNode } from 'react'
import { shortSupplierName } from '../data/tracker/names'
import { certifiedGrowth, domainMomentum, formatPercent, formatNetCash, formatPoints, formatUsd, healthFacts, marketMedian, signalAge } from '../data/tracker/momentum'
import { formatMonthYear } from '../data/tracker/derive'
import { shortUsd } from '../data/tracker/eventFacts'
import type { DomainMomentum, MomentumRow, OtherCompany } from '../data/tracker/momentum'
import { trackerDomains } from '../data/tracker/domains'
import { typeName } from '../data/tracker/typeNames'
import { companyPath } from '../data/companyPages'
import type { TrackerSupplier } from '../data/tracker/suppliers'

const domains = domainMomentum()
const withRows = domains.filter(d => d.rows.length > 0)
const shown = domains.filter(d => d.rows.length > 0 || d.others.length > 0)
const empty = domains.filter(d => d.rows.length === 0 && d.others.length === 0)
const all = certifiedGrowth.map(r => r.latest)
const lo = Math.min(0, Math.floor(Math.min(...all) / 10) * 10)
const hi = Math.max(10, Math.ceil(Math.max(...all) / 10) * 10)
const pos = (v: number) => `${((v - lo) / (hi - lo)) * 100}%`
const ticks = Array.from({ length: Math.floor((hi - lo) / 10) + 1 }, (_, i) => lo + i * 10).filter(v => v % 20 === 0)
/** Light axis labels under the bars, at the same scale as every row. */
function Axis() {
  return <li className="momentum__row momentum__axis" aria-hidden="true"><span />
    <div className="momentum__ticks">{ticks.map(v => <span key={v} style={{ left: pos(v) }}>{v}%</span>)}</div>
  </li>
}
const ends = certifiedGrowth.map(r => r.supplier.revenue!.latest.periodEnd).sort()
const hasHealth = Object.keys(healthFacts.suppliers).length > 0
const hasBalance = Object.values(healthFacts.suppliers).some(h => h?.balance)
const rowClass = `momentum__rows${hasHealth ? ' has-health' : ''}${hasBalance ? ' has-balance' : ''}`
const colClass = `momentum__cols${hasHealth ? ' has-health' : ''}${hasBalance ? ' has-balance' : ''}`

function Health({ row }: { row: MomentumRow }) {
  const h = row.health
  const cell = (kind: string, label: string, text: string | null, title?: string, href?: string, na = 'Not reported') => <span className={`momentum__metric momentum__metric--${kind}`} title={title}>
    <span className="momentum__metric-label">{label}</span>
    {text === null ? <span className="momentum__na">{na}</span> : href ? <a href={href} target="_blank" rel="noreferrer">{text}</a> : text}
  </span>
  if (!hasHealth) return null
  return <>
    {cell('op', 'Operating margin', h?.operatingMargin ? formatPercent(h.operatingMargin.value) : null, h?.operatingMargin ? `Four quarters to ${h.operatingMargin.periodEnd}` : undefined, h?.operatingMargin?.sourceUrl)}
    {cell('fcf', 'Free cash flow margin', h?.fcfMargin ? formatPercent(h.fcfMargin.value) : null, h?.fcfMargin ? `Four quarters to ${h.fcfMargin.periodEnd}` : undefined, h?.fcfMargin?.sourceUrl)}
    {hasBalance && cell('bal', 'Net cash', h?.balance && h.balance.debt !== null ? formatNetCash(h.balance.cash, h.balance.debt) : null, h?.balance ? `Cash and short-term investments ${formatUsd(h.balance.cash)}, ${h.balance.debt === null ? 'no borrowing tagged' : `debt ${formatUsd(h.balance.debt)}`}, at ${h.balance.asOf}` : undefined, h?.balance?.sourceUrl, h?.balance ? `${formatUsd(h.balance.cash)} cash` : 'Not reported')}
  </>
}

type Open = ((id: string) => void) | undefined

/** A company name: opens the supplier record on the front page, or links to the company page elsewhere. */
function Name({ supplier, open, className = '' }: { supplier: TrackerSupplier; open: Open; className?: string }) {
  // Only ranked rows carry a title; names in the collapsed list stay out of title lookups.
  const title = className ? supplier.name : undefined
  return <a className={`desk-supplier-link ${className}`} title={title} href={companyPath(supplier.id)} onClick={event => {
    if (!open || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button !== 0) return
    event.preventDefault(); open(supplier.id)
  }}>{shortSupplierName(supplier.name)}</a>
}

/**
 * The growth rate of each comparable quarter as a small line, oldest to newest. Every row uses one
 * vertical scale: the full height is 16 percentage points, widened only when a company moved more.
 */
function Spark({ trend }: { trend: MomentumRow['trend'] }) {
  if (trend.length < 2) return null
  const w = 40, h = 16, pad = 2.5
  const values = trend.map(t => t.growth)
  const min = Math.min(...values), max = Math.max(...values)
  const span = Math.max(16, max - min), mid = (min + max) / 2
  const x = (i: number) => pad + (i / (trend.length - 1)) * (w - pad * 2)
  const y = (v: number) => pad + ((mid + span / 2 - v) / span) * (h - pad * 2)
  return <svg className="momentum__spark" width={w} height={h} viewBox={`0 0 ${w} ${h}`} aria-hidden="true">
    <polyline points={values.map((v, i) => `${x(i).toFixed(1)},${y(v).toFixed(1)}`).join(' ')} fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" strokeLinecap="round" />
    <circle cx={x(values.length - 1)} cy={y(values.at(-1)!)} r="2.2" fill="#1f5fc8" />
  </svg>
}

function Row({ row, median, market, openSupplier, highlight }: { row: MomentumRow; median: number | null; market?: number | null; openSupplier: Open; highlight?: string }) {
  const { supplier, latest, change, trend } = row
  const rev = supplier.revenue!.latest
  const trendText = trend.map(t => `${formatPercent(t.growth)} for the quarter ended ${t.periodEnd}`).join(', ')
  return <li className={`momentum__row${highlight === supplier.id ? ' is-highlight' : ''}`} aria-current={highlight === supplier.id ? 'true' : undefined}>
    <span className="momentum__who"><Name supplier={supplier} open={openSupplier} className="momentum__name" />
      {row.revenue !== null && <span className="momentum__rev" title={`Revenue for the quarter ended ${rev.periodEnd}, from the SEC filing`}><span className="momentum__metric-label">Quarterly revenue </span>{shortUsd(row.revenue)}</span>}</span>
    <div className="momentum__bar" role="img" aria-label={`${supplier.name}: ${formatPercent(latest)} year-over-year revenue growth, quarter ended ${rev.periodEnd}${median !== null ? `; domain median ${formatPercent(median)}` : ''}${market != null ? `; all SEC filers median ${formatPercent(market)}` : ''}`}>
      <i className="momentum__zero" style={{ left: pos(0) }} />
      <i className="momentum__fill" style={{ left: pos(Math.min(0, latest)), width: `${(Math.abs(latest) / (hi - lo)) * 100}%` }} />
      {market != null && <i className="momentum__median momentum__median--all" style={{ left: pos(market) }} />}
      {median !== null && <i className="momentum__median" style={{ left: pos(median) }} />}
    </div>
    <span className="momentum__growth"><span className="momentum__metric-label">Revenue growth</span>{formatPercent(latest)}</span>
    <span className="momentum__change" role="img" aria-label={change === null ? 'No prior quarter on file' : `Growth by quarter: ${trendText}. Change from the prior quarter ${formatPoints(change)}`} title={change === null ? 'No prior quarter on file' : `Growth by quarter: ${trendText}`}>
      <span className="momentum__metric-label">Trend, change</span>
      {change === null ? '–' : <><Spark trend={trend} /> {formatPoints(change)}</>}
    </span>
    <Health row={row} />
  </li>
}

function headText(d: DomainMomentum): ReactNode {
  if (!d.revenueBars) return 'Listed by latest funding or deal'
  if (d.rows.length === 0) return 'No SEC filer'
  const all = marketMedian === null ? null : <>All SEC filers <strong>{formatPercent(marketMedian)}</strong></>
  if (d.median !== null) return <>Median <strong>{formatPercent(d.median)}</strong> across {d.rows.length} filers{all && <> · {all}</>}</>
  return <>{d.rows.length} SEC {d.rows.length === 1 ? 'filer' : 'filers'}; domain median shown from 3{all && <> · {all}</>}</>
}

function Other({ o, openSupplier, highlight }: { o: OtherCompany; openSupplier: Open; highlight?: string }) {
  return <li className={highlight === o.supplier.id ? 'is-highlight' : undefined}><Name supplier={o.supplier} open={openSupplier} />
    <span>{o.fact}</span>
    <span className="desk-note">{o.latestEvent ? <>{typeName(o.latestEvent.type)} <time dateTime={o.latestEvent.date}>{o.latestEvent.date}</time>{o.eventCount > 1 ? ` · ${o.eventCount} events in 12 months` : ''}</>
      : o.signalDate ? <>Newest dated fact <time dateTime={o.signalDate}>{formatMonthYear(o.signalDate)}</time> · {signalAge(o.signalDate)}</> : 'No dated fact on file'}</span></li>
}

export function DomainCard({ d, openSupplier, highlight }: { d: DomainMomentum; openSupplier?: (id: string) => void; highlight?: string }) {
  const domain = trackerDomains.find(t => t.id === d.id)
  return <article className="momentum__domain" id={`momentum-card-${d.id}`} aria-labelledby={`momentum-${d.id}`}>
    <div className="momentum__domain-head"><h3 id={`momentum-${d.id}`}>{d.name}</h3>
      <span>{headText(d)}</span></div>
    {domain?.subareas && <p className="desk-note momentum__scope">{domain.scope}</p>}
    {d.rows.length > 0 && <>
      <div className={colClass} aria-hidden="true"><span>Company, quarterly revenue</span><span>Revenue growth, year over year</span><span /><span>Trend, change vs prior quarter</span>
        {hasHealth && <><span>Operating margin</span><span>Free cash flow margin</span></>}{hasBalance && <span>Net cash</span>}</div>
      <ul className={rowClass}>{d.rows.map(row => <Row key={row.supplier.id} row={row} median={d.median} market={marketMedian} openSupplier={openSupplier} highlight={highlight} />)}<Axis /></ul>
    </>}
    {d.otherGroups.length > 0 && <div className="momentum__others">
      <div className="momentum__others-cols" aria-hidden="true"><span>{d.rows.length > 0 ? 'Private, acquired and other companies' : 'Company'}</span><span>Latest funding, ownership or deal</span><span>Newest event or dated fact</span></div>
      {d.otherGroups.map(g => <div key={g.id ?? 'all'} className="momentum__group">
        {g.name && <h4 className="momentum__group-name">{g.name}{g.scope && <span className="desk-note"> {g.scope}</span>}</h4>}
        <ul>{g.companies.map(o => <Other key={o.supplier.id} o={o} openSupplier={openSupplier} highlight={highlight} />)}</ul>
      </div>)}
    </div>}
  </article>
}

/**
 * Growth against cash generation: one labelled dot per SEC filer, revenue growth across and free
 * cash flow margin up, with the two medians drawn. A picture of the table below, with no labels
 * of its own beyond the numbers.
 */
function GrowthCashChart({ rows }: { rows: MomentumRow[] }) {
  const pts = rows.flatMap(r => r.health?.fcfMargin ? [{ id: r.supplier.id, name: shortSupplierName(r.supplier.name), g: r.latest, f: r.health.fcfMargin.value }] : [])
  if (pts.length < 3) return null
  const W = 760, H = 380, L = 52, R = 18, T = 18, B = 44
  const fs = pts.map(p => p.f).sort((a, b) => a - b)
  const fMed = fs.length % 2 ? fs[(fs.length - 1) / 2] : (fs[fs.length / 2 - 1] + fs[fs.length / 2]) / 2
  const fLo = Math.min(0, Math.floor(fs[0] / 10) * 10), fHi = Math.max(10, Math.ceil(fs.at(-1)! / 10) * 10)
  const x = (g: number) => L + ((g - lo) / (hi - lo)) * (W - L - R)
  const y = (f: number) => T + ((fHi - f) / (fHi - fLo)) * (H - T - B)
  const xTicks = Array.from({ length: (hi - lo) / 10 + 1 }, (_, i) => lo + i * 10)
  const yTicks = Array.from({ length: (fHi - fLo) / 10 + 1 }, (_, i) => fLo + i * 10)
  // Place each label beside its dot, trying right, left, above and below until it clears the others.
  const boxes: { x0: number; y0: number; x1: number; y1: number }[] = pts.map(p => ({ x0: x(p.g) - 6, y0: y(p.f) - 6, x1: x(p.g) + 6, y1: y(p.f) + 6 }))
  const hits = (b: { x0: number; y0: number; x1: number; y1: number }, skip: number) => b.x0 < L || b.x1 > W - 2 || b.y0 < 2 || b.y1 > H - B
    || boxes.some((o, i) => i !== skip && b.x0 < o.x1 && b.x1 > o.x0 && b.y0 < o.y1 && b.y1 > o.y0)
  const labels = pts.map((p, i) => {
    const w = p.name.length * 6.4 + 4, cx = x(p.g), cy = y(p.f)
    const tries = [{ x: cx + 9, y: cy + 4, a: 'start' }, { x: cx - 9, y: cy + 4, a: 'end' }, { x: cx, y: cy - 10, a: 'middle' }, { x: cx, y: cy + 18, a: 'middle' }, { x: cx + 9, y: cy - 8, a: 'start' }, { x: cx - 9, y: cy + 16, a: 'end' }]
    const box = (t: (typeof tries)[number]) => { const x0 = t.a === 'start' ? t.x : t.a === 'end' ? t.x - w : t.x - w / 2; return { x0, y0: t.y - 11, x1: x0 + w, y1: t.y + 3 } }
    const pick = tries.find(t => !hits(box(t), i)) ?? tries[0]
    boxes.push(box(pick))
    return pick
  })
  return <figure className="momentum__scatter">
    <figcaption><strong>Growth and cash generation.</strong> One dot per SEC filer. Across: year-over-year revenue growth, latest quarter. Up: free cash flow margin, last four quarters. Dashed lines are the medians of the {pts.length} filers.</figcaption>
    <div className="momentum__scatter-scroll" tabIndex={0} role="region" aria-label="Growth and cash generation chart, scroll sideways on a phone">
      <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={`Scatter chart of ${pts.length} SEC filers. ${pts.map(p => `${p.name}: growth ${formatPercent(p.g)}, free cash flow margin ${formatPercent(p.f)}`).join('; ')}.`}>
        {xTicks.map(t => <g key={`x${t}`}><line x1={x(t)} x2={x(t)} y1={T} y2={H - B} className={t === 0 ? 'is-zero' : undefined} /><text x={x(t)} y={H - B + 16} textAnchor="middle">{t}%</text></g>)}
        {yTicks.map(t => <g key={`y${t}`}><line x1={L} x2={W - R} y1={y(t)} y2={y(t)} className={t === 0 ? 'is-zero' : undefined} /><text x={L - 8} y={y(t) + 4} textAnchor="end">{t}%</text></g>)}
        <text x={(L + W - R) / 2} y={H - 6} textAnchor="middle" className="momentum__scatter-axis">Revenue growth, year over year</text>
        <text transform={`translate(13 ${(T + H - B) / 2}) rotate(-90)`} textAnchor="middle" className="momentum__scatter-axis">Free cash flow margin</text>
        {marketMedian !== null && <line x1={x(marketMedian)} x2={x(marketMedian)} y1={T} y2={H - B} className="is-median" />}
        <line x1={L} x2={W - R} y1={y(fMed)} y2={y(fMed)} className="is-median" />
        {pts.map((p, i) => <a key={p.id} href={companyPath(p.id)}><title>{`${p.name}: growth ${formatPercent(p.g)}, free cash flow margin ${formatPercent(p.f)}`}</title>
          <circle cx={x(p.g)} cy={y(p.f)} r="5" /><text x={labels[i].x} y={labels[i].y} textAnchor={labels[i].a as 'start' | 'end' | 'middle'} className="momentum__scatter-name">{p.name}</text></a>)}
      </svg>
    </div>
  </figure>
}

/** All certified filers once, ranked by latest growth, with the market median as the tick. */
function AllDomains({ openSupplier }: { openSupplier: (id: string) => void }) {
  const seen = new Set<string>()
  const rows = withRows.flatMap(d => d.rows).filter(r => !seen.has(r.supplier.id) && seen.add(r.supplier.id)).sort((a, b) => b.latest - a.latest || a.supplier.name.localeCompare(b.supplier.name))
  return <article className="momentum__domain momentum__all" aria-label="All SEC filers ranked">
    <GrowthCashChart rows={rows} />
    <div className="momentum__domain-head"><h3>All SEC filers</h3>{marketMedian !== null && <span>Median <strong>{formatPercent(marketMedian)}</strong></span>}</div>
    <div className={colClass} aria-hidden="true"><span>Company, quarterly revenue</span><span>Revenue growth, year over year</span><span /><span>Trend, change vs prior quarter</span>
      {hasHealth && <><span>Operating margin</span><span>Free cash flow margin</span></>}{hasBalance && <span>Net cash</span>}</div>
    <ul className={rowClass}>{rows.map(row => <Row key={row.supplier.id} row={{ ...row, vsMedian: null }} median={marketMedian} openSupplier={openSupplier} />)}<Axis /></ul>
  </article>
}

export function MomentumByDomain({ openSupplier }: { openSupplier: (id: string) => void }) {
  const [expanded, setExpanded] = useState(false)
  const [all, setAll] = useState(false)
  return <section id="momentum" className={`desk-panel momentum${expanded ? ' is-expanded' : ''}`} aria-labelledby="momentum-heading">
    <div className="desk-panel__head"><h2 id="momentum-heading">Company revenue growth</h2>
      <div className="momentum__toggle" role="group" aria-label="Group companies">
        <button type="button" aria-pressed={!all} onClick={() => setAll(false)}>By domain</button>
        <button type="button" aria-pressed={all} onClick={() => setAll(true)}>All domains</button>
      </div></div>
    <p className="desk-note">Whole-company revenue growth, year over year, for the latest quarter, re-derived from SEC filings. The small line is the growth rate of the last quarters on file, followed by the change from the prior quarter. The dark tick is the domain median; the light tick is the median of all SEC filers.</p>
    <details className="momentum__how"><summary>How to read this</summary><p className="desk-note">Quarters end {ends[0]} to {ends.at(-1)}; fiscal calendars differ. Growth is for the whole company, not for its business in one domain, so a company can appear in more than one domain card. A domain median is shown only with three or more filers. Every trend line uses one vertical scale: its full height is 16 percentage points, widened only when a company moved more. The SEC series holds eight quarters, so up to four growth rates can be compared.
      {hasHealth && <> Operating margin and free cash flow margin cover the four quarters to the same quarter end. They come from the same SEC filings but are not yet part of the certified check.{hasBalance ? ' Net cash is cash and short-term investments minus the carrying value of debt, at the same quarter end; where a filer tags no borrowing for that date, cash is shown alone.' : ' Debt is not shown yet.'}</>}
      {' '}Private companies, segments and non-SEC filers have no comparable financials here; they are listed under each domain with their latest funding, ownership or deal and their latest event. AI security shows no bars: no public company sells only AI security, so a whole-company growth rate would not describe it.</p></details>
    {all ? <div className="momentum__grid momentum__grid--one"><AllDomains openSupplier={openSupplier} /></div> : <>
      <div className="momentum__grid">{shown.map(d => <DomainCard key={d.id} d={d} openSupplier={openSupplier} />)}</div>
      <button type="button" className="momentum__mobile-toggle" aria-expanded={expanded} onClick={() => setExpanded(v => !v)}>{expanded ? 'Show fewer domains' : 'Show all domains'}</button>
      {empty.length > 0 && <p className="desk-note momentum__none">No companies tracked yet in {empty.map(d => d.name).join(', ')}.</p>}
    </>}
  </section>
}
