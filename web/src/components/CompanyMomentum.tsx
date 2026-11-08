import { displayDomainIds } from '../data/tracker/domains'
import { isCertifiedSupplier } from '../data/tracker/certification'
import { domainMomentum, formatPercent, formatPoints, formatUsd, healthFacts, marketMedian } from '../data/tracker/momentum'
import { eventGroups, yearChanges } from '../data/tracker/presentation'
import { filingSeries } from '../data/tracker/presentation'
import { trackerSuppliers } from '../data/tracker/suppliers'
import { DomainCard } from './MomentumByDomain'

const domains = domainMomentum()
const yearItems = yearChanges().filter(item => item.type !== 'filing')

/** Year-over-year growth for each recent quarter that has the same quarter a year earlier in the SEC series. */
function quarterlyGrowth(edgarId: string) {
  const quarters = (filingSeries.find(s => s.id === edgarId)?.quarters ?? []).slice().sort((a, b) => a.periodEnd.localeCompare(b.periodEnd))
  return quarters.flatMap(q => {
    const end = Date.parse(q.periodEnd)
    const prior = quarters.find(p => Math.abs(Date.parse(p.periodEnd) - (end - 365 * 86_400_000)) <= 7 * 86_400_000)
    return prior ? [{ periodEnd: q.periodEnd, growth: Math.round((q.value / prior.value - 1) * 1000) / 10 }] : []
  })
}

/** The company's newest dated fact on file, for a page with no events: its last round, or its ownership change. */
function lastFact(s: (typeof trackerSuppliers)[number]): string | null {
  if (s.lastRound) return `${s.lastRound.stage}, ${s.lastRound.amount}${s.lastRound.lead ? `, led by ${s.lastRound.lead}` : ''} (${s.lastRound.date})`
  if (s.ownership) return `${s.ownership.status}${s.ownership.closed ? ` (${s.ownership.closed})` : s.ownership.announced ? ` (${s.ownership.announced})` : ''}`
  return null
}

function Stat({ label, value, detail, group }: { label: string; value: string; detail: string; group?: string }) {
  return <div className={`company-momentum__stat${group ? ` desk-count--${group}` : ''}`}><span>{label}</span><strong>{value}</strong><small>{detail}</small></div>
}

/**
 * Growth, health and peer standing at the top of a company page: the same certified figures and
 * domain comparison as the front page's momentum view, with this company highlighted.
 */
export function CompanyMomentum({ id }: { id: string }) {
  const supplier = trackerSuppliers.find(s => s.id === id)
  if (!supplier) return null
  const certified = isCertifiedSupplier(id) && !!supplier.revenue
  const own = domains.filter(d => displayDomainIds(supplier).includes(d.id))
  const health = healthFacts.suppliers[id]
  const series = certified && supplier.edgarId ? quarterlyGrowth(supplier.edgarId) : []
  const max = Math.max(10, ...series.map(s => Math.abs(s.growth)))
  const row = own.flatMap(d => d.rows).find(r => r.supplier.id === id)
  const events = yearItems.filter(i => i.supplierId === id)
  return <section className="company-momentum" aria-labelledby="company-momentum">
    <h2 id="company-momentum">{certified ? 'Growth and health' : 'Activity, last 12 months'}</h2>
    {certified && row ? <>
      <div className="company-momentum__stats">
        <Stat label="Revenue growth, year over year" value={formatPercent(row.latest)} detail={`Quarter ended ${supplier.revenue!.latest.periodEnd}`} />
        <Stat label="vs prior quarter" value={row.change === null ? '–' : `${row.change > 0 ? '▲' : row.change < 0 ? '▼' : '■'} ${formatPoints(row.change)}`} detail={supplier.revenue!.prior ? `Prior quarter ${supplier.revenue!.prior.yoyGrowth}` : 'No prior quarter on file'} />
        {health?.operatingMargin && <Stat label="Operating margin" value={formatPercent(health.operatingMargin.value)} detail={`Four quarters to ${health.operatingMargin.periodEnd}`} />}
        {health?.fcfMargin && <Stat label="Free cash flow margin" value={formatPercent(health.fcfMargin.value)} detail={`Four quarters to ${health.fcfMargin.periodEnd}`} />}
        {health?.balance && <Stat label="Cash and debt" value={`${formatUsd(health.balance.cash)} / ${formatUsd(health.balance.debt)}`} detail={`Cash and short-term investments / debt, ${health.balance.asOf}`} />}
        {marketMedian !== null && <Stat label="All SEC filers, median growth" value={formatPercent(marketMedian)} detail={`This company ${row.latest - marketMedian >= 0 ? '+' : '−'}${Math.abs(row.latest - marketMedian).toFixed(1)} pts`} />}
      </div>
      {series.length > 1 && <figure className="company-momentum__chart">
        <figcaption>Year-over-year revenue growth by quarter, from the SEC quarterly table below</figcaption>
        <ol>{series.map(s => <li key={s.periodEnd} aria-label={`Quarter ended ${s.periodEnd}: ${formatPercent(s.growth)}`}>
          <span className="company-momentum__value">{formatPercent(s.growth)}</span>
          <span className="company-momentum__col"><i style={{ height: `${Math.abs(s.growth) / max * 100}%` }} className={s.growth < 0 ? 'is-negative' : undefined} /></span>
          <time dateTime={s.periodEnd}>{s.periodEnd.slice(0, 7)}</time>
        </li>)}</ol>
      </figure>}
      <p className="coverage-page__note">Growth is re-derived from SEC filings. The margins{health?.balance ? ', cash and debt' : ''} come from the same filings but are not yet part of the certified check.{health?.balance ? ' Debt is carrying value at the quarter end.' : ' Debt is not shown yet.'}</p>
    </> : <>
      {events.length === 0 ? <p className="company-momentum__none">No sourced events in the last 12 months.{lastFact(supplier) && <> Latest on file: {lastFact(supplier)}.</>}</p>
      : <div className="company-momentum__stats">{eventGroups.map(g => {
        const items = events.filter(i => g.types.includes(i.type as never))
        return <Stat key={g.id} group={g.id} label={g.label} value={String(items.length)} detail={items[0] ? `Latest ${items[0].date}` : 'None in 12 months'} />
      })}</div>}
      <p className="coverage-page__note">{supplier.kind === 'public' ? 'This company does not file comparable quarterly revenue with the SEC.' : 'Private companies, segments and acquired companies have no comparable SEC financials.'} Counts are sourced events in the trailing 12 months; each is listed below. Its domain&rsquo;s SEC filers are shown for context.</p>
    </>}
    {own.filter(d => d.rows.length > 0).length > 0 && <>
      <h3 className="company-momentum__peers">{certified ? 'Against domain peers' : 'SEC filers in its domains'}</h3>
      <div className="momentum__grid company-momentum__grid">{own.filter(d => d.rows.length > 0).map(d => <DomainCard key={d.id} d={d} highlight={id} />)}</div>
    </>}
  </section>
}
