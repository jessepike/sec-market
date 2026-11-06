import { useEffect, useRef, useState } from 'react'
import { evidenceById } from '../data/evidence'
import { runStatus } from '../data/runStatus'
import { certifiedCount, isCertifiedEvent, isCertifiedSupplier } from '../data/tracker/certification'
import { eventsForSupplier, formatOwnershipCompact, shortSupplierName, suppliersForDomain } from '../data/tracker/derive'
import { trackerDomains } from '../data/tracker/domains'
import { trackerSuppliers } from '../data/tracker/suppliers'
import type { TrackerSupplier } from '../data/tracker/suppliers'
import { countedUnits, currencyName, eventGroups, filingSeries, recentChanges, revenueGrowthRows, yearChanges } from '../data/tracker/presentation'
import type { ChangeItem } from '../data/tracker/presentation'
import { SiteMasthead } from './SiteMasthead'
import { CompanySearch } from './CompanySearch'
import { companyPath } from '../data/companyPages'
import './market-desk.css'

const changes = recentChanges()
const yearItems = yearChanges()
const yearUnits = countedUnits(yearItems)
const monthUnits = countedUnits(changes)
const unitsInGroup = (units: typeof yearUnits, groupId: string) => units.filter(u => u.groupId === groupId)
const plural = (n: number, word: string) => `${n} ${word}${n === 1 ? '' : 's'}`
function eventSummaryForSupplier(id: string) {
  const own = yearItems.filter(item => item.supplierId === id)
  return { count: own.length, latest: own[0] ?? null }
}
const nonSecGrowth = revenueGrowthRows().filter(r => !isCertifiedSupplier(r.supplier.id)).map(r => shortSupplierName(r.supplier.name))
const nonSecGrowthNote = nonSecGrowth.length ? `${nonSecGrowth.join(' and ')} ${nonSecGrowth.length > 1 ? 'figures come' : 'figure comes'} from company releases and ${nonSecGrowth.length > 1 ? 'are' : 'is'} not re-checked automatically; the rest are re-derived from SEC filings.` : 'All figures are re-derived from SEC filings.'
const growthRows = revenueGrowthRows()
const supplierById = Object.fromEntries(trackerSuppliers.map(s => [s.id, s]))
const typeName = (type: string) => ({ 'exec-change': 'Leadership', 'going-concern': 'Going concern', layoff: 'Layoffs', filing: 'SEC filing', 'late-filing': 'Late filing' })[type] ?? type.replaceAll('-', ' ')

function Sources({ ids }: { ids: string[] }) {
  return <span className="desk-sources">{ids.map(id => {
    const source = evidenceById[id]
    if (!source) return null
    return <a key={id} href={source.canonicalUrl} target="_blank" rel="noreferrer" title={source.title}>
      {source.organization} <time dateTime={source.publicationDate}>{source.publicationDate}</time><span aria-hidden="true"> ↗</span>
    </a>
  })}</span>
}

function Fact({ label, value, period, ids }: { label: string; value: string; period?: string; ids: string[] }) {
  return <div className="desk-fact"><span className="desk-fact__label">{label}</span><strong>{value}</strong>
    {period && <span className="desk-fact__period">{period}</span>}<Sources ids={ids} /></div>
}

function SupplierFacts({ supplier }: { supplier: TrackerSupplier }) {
  const { revenue, headlineMetric: metric, lastRound: round, ownership } = supplier
  return <div className="desk-facts">
    {revenue ? <>
      <Fact label={supplier.kind === 'segment' ? 'Reported segment revenue' : 'Reported quarterly revenue'} value={revenue.latest.value} period={`${revenue.latest.period} · ${supplier.edgarId ? 'filed' : 'reported'} ${revenue.latest.releaseDate}`} ids={revenue.latest.evidenceIds} />
      <Fact label="Year-over-year revenue growth" value={revenue.latest.yoyGrowth} period={revenue.latest.period} ids={revenue.latest.evidenceIds} />
      {revenue.latest.growthBasis && <Fact label="Growth reporting basis" value={revenue.latest.growthBasis} period={revenue.latest.period} ids={revenue.latest.evidenceIds} />}
      {revenue.prior && <Fact label="Prior quarter, year-over-year growth" value={revenue.prior.yoyGrowth} period={revenue.prior.period} ids={revenue.prior.evidenceIds} />}
    </> : <p className="desk-gap">{supplier.kind === 'segment' ? 'No separately reported quarterly revenue in this tracker.' : 'No comparable quarterly revenue in this tracker.'}</p>}
    {metric && <Fact label={metric.label} value={metric.value} period={metric.period} ids={metric.evidenceIds} />}
    {round && <Fact label={`Last reported funding · ${round.stage}`} value={round.amount} period={`${round.date}${round.lead ? ` · led by ${round.lead}` : ''}${round.valuation ? ` · valuation ${round.valuation}` : ''}`} ids={round.evidenceIds} />}
    {ownership && <Fact label="Ownership" value={ownership.status} period={[ownership.announced ? `Announced ${ownership.announced}` : '', ownership.closed ? `Closed ${ownership.closed}` : ''].filter(Boolean).join(' · ')} ids={ownership.evidenceIds} />}
  </div>
}

function SupplierDialog({ supplier, close }: { supplier: TrackerSupplier | null; close: () => void }) {
  const ref = useRef<HTMLDialogElement>(null)
  useEffect(() => {
    const dialog = ref.current
    if (supplier && dialog && !dialog.open) dialog.showModal()
    if (!supplier && dialog?.open) dialog.close()
  }, [supplier])
  const quarters = supplier ? filingSeries.find(s => s.id === supplier.edgarId)?.quarters ?? [] : []
  return <dialog ref={ref} className="desk-dialog" aria-labelledby="desk-supplier-title" onClose={close} onCancel={close}>
    {supplier && <>
      <div className="desk-dialog__head"><div><span className="desk-kicker">Supplier record</span><h2 id="desk-supplier-title">{supplier.name}</h2></div><button type="button" onClick={close} aria-label="Close supplier record">Close</button></div>
      <p>{supplier.domainIds.map(id => trackerDomains.find(d => d.id === id)?.name).join(' · ')} · <a href={companyPath(supplier.id)}>Company page</a></p>
      <p className="desk-note desk-cert-note">{isCertifiedSupplier(supplier.id)
        ? 'Certified: name and ticker, quarterly revenue, year-over-year growth, the quarterly table, and the filing and date of SEC-filed events, all re-derived from SEC filings. Other facts here keep their own source and date and are not re-checked automatically.'
        : 'Not certified. Each fact keeps its own source and date and is not re-checked automatically.'}</p>
      <SupplierFacts supplier={supplier} />
      {quarters.length > 0 && <section><h3>SEC quarterly revenue</h3><p className="desk-note">Exact dollars from filings. Derived quarters are labelled; comparative figures may be restated in a later filing.</p>
        <div className="desk-quarter-table"><table><thead><tr><th>Quarter ended</th><th>Revenue, USD</th><th>Filed</th><th>Source</th></tr></thead><tbody>{quarters.map(q => <tr key={q.periodEnd}><td>{q.periodEnd}</td><td>${q.value.toLocaleString('en-US')}{q.derived ? ' (derived)' : ''}</td><td>{q.filedDate}</td><td><a href={q.sourceUrl} target="_blank" rel="noreferrer">{q.form}</a></td></tr>)}</tbody></table></div>
      </section>}
      <section><h3>Dated events</h3><ul className="desk-dialog__events">{eventsForSupplier(supplier.id).map(event => <li key={event.id}><time dateTime={event.date}>{event.date}</time> <span className="desk-type">{typeName(event.type)}</span>{isCertifiedEvent(event) && <span className="desk-cert">SEC filing, date checked</span>}<p>{event.text}</p><Sources ids={event.evidenceIds} /></li>)}</ul>
        {eventsForSupplier(supplier.id).length === 0 && <p>No sourced events in this tracker.</p>}</section>
    </>}
  </dialog>
}

function ChangeRow({ item, openSupplier }: { item: ChangeItem; openSupplier: (id: string) => void }) {
  return <li className="desk-change"><time dateTime={item.date}>{item.date}</time><div>
    <button type="button" className="desk-supplier-link" onClick={() => openSupplier(item.supplierId)}>{shortSupplierName(supplierById[item.supplierId]?.name ?? item.supplierId)}</button>
    <span className="desk-type">{typeName(item.type)}</span>{item.type !== 'filing' && isCertifiedEvent(item) && <span className="desk-cert">SEC filing, date checked</span>}<p>{item.text}</p><Sources ids={item.evidenceIds} />
    {item.filings.map(f => <a className="desk-filing" key={`${f.supplierId}-${f.periodEnd}`} href={f.sourceUrl} target="_blank" rel="noreferrer">SEC {f.form} · quarter ended {f.periodEnd} · filed {f.filedDate} ↗</a>)}
  </div></li>
}

function GrowthChart({ openSupplier }: { openSupplier: (id: string) => void }) {
  const [byValue, setByValue] = useState(false)
  const [expanded, setExpanded] = useState(false)
  const rows = byValue ? growthRows.slice().sort((a, b) => b.latest - a.latest || a.supplier.name.localeCompare(b.supplier.name)) : growthRows
  const all = rows.flatMap(r => [r.latest, ...(r.prior === null ? [] : [r.prior])])
  const min = Math.floor(Math.min(0, ...all) / 10) * 10
  const max = Math.ceil(Math.max(...all) / 10) * 10
  const position = (value: number) => `${(value - min) / (max - min) * 100}%`
  const ticks = Array.from({ length: (max - min) / 10 + 1 }, (_, i) => min + i * 10)
  const ends = growthRows.map(r => r.supplier.revenue!.latest.periodEnd).sort()
  return <section id="reported-growth" className={`desk-panel desk-growth${expanded ? ' is-expanded' : ''}`} aria-labelledby="desk-growth-heading">
    <div className="desk-panel__head"><h2 id="desk-growth-heading">Reported revenue growth</h2><button type="button" aria-pressed={byValue} onClick={() => setByValue(v => !v)}>{byValue ? 'Sort A–Z' : 'Sort by value'}</button></div>
    <p className="desk-note">{rows.length} public suppliers. Latest quarters end {ends[0]} to {ends.at(-1)}. Year-over-year revenue growth in each company's reporting currency; different fiscal periods. Company totals, excluding segments and ARR. {nonSecGrowthNote}</p>
    <div className="desk-growth__scale" aria-hidden="true"><span /><div>{ticks.map(t => <span key={t} style={{ left: position(t) }}>{t}%</span>)}</div><span /></div>
    <ul className="desk-growth__rows">{rows.map(({ supplier, latest, prior, currency }) => <li key={supplier.id}>
      <button type="button" className="desk-supplier-link" onClick={() => openSupplier(supplier.id)}>{shortSupplierName(supplier.name)}</button>
      <div className="desk-growth__plot" role="img" aria-label={`${supplier.name}: latest ${supplier.revenue!.latest.yoyGrowth}${currency ? ` growth in ${currencyName(currency)}` : ''}, quarter ended ${supplier.revenue!.latest.periodEnd}${prior !== null ? `; prior ${supplier.revenue!.prior!.yoyGrowth}, quarter ended ${supplier.revenue!.prior!.periodEnd}` : '; prior quarter unavailable'}`}>
        {ticks.map(t => <i className="desk-growth__grid" key={t} style={{ left: position(t) }} />)}
        {prior !== null && <><i className="desk-growth__join" style={{ left: position(Math.min(latest, prior)), width: `${Math.abs(latest - prior) / (max - min) * 100}%` }} /><i className="desk-growth__dot desk-growth__dot--prior" style={{ left: position(prior) }} /></>}
        <i className="desk-growth__dot" style={{ left: position(latest) }} />
      </div>
      <a className="desk-growth__value" href={evidenceById[supplier.revenue!.latest.evidenceIds[0]].canonicalUrl} target="_blank" rel="noreferrer" title={`${supplier.revenue!.latest.period} · ${supplier.edgarId ? 'filed' : 'reported'} ${supplier.revenue!.latest.releaseDate} · ${supplier.revenue!.latest.growthBasis ?? 'Company reporting currency'} · ${evidenceById[supplier.revenue!.latest.evidenceIds[0]].organization}`} aria-label={`${supplier.name} ${supplier.revenue!.latest.yoyGrowth}${currency ? ` in ${currencyName(currency)}` : ''}, ${supplier.revenue!.latest.period}, source`}>{supplier.revenue!.latest.yoyGrowth}{currency && <abbr className="desk-growth__currency" title={`Growth in ${currencyName(currency)}`}>{currency}</abbr>}</a>
    </li>)}</ul>
    <button type="button" className="desk-growth__mobile-toggle" aria-expanded={expanded} onClick={() => setExpanded(v => !v)}>{expanded ? 'Show fewer suppliers' : `Compare all ${rows.length} suppliers`}</button>
    <p className="desk-note desk-growth__legend"><span>● Latest reported quarter</span><span>○ Quarter before</span></p>
    <p className="desk-note">Select a supplier for both exact figures, periods and sources. A missing prior dot means no comparable prior figure is recorded.</p>
  </section>
}

function Timeline({ openSupplier }: { openSupplier: (id: string) => void }) {
  const [selected, setSelected] = useState<string | null>(null)
  const [showAll, setShowAll] = useState(false)
  const start = new Date(Date.parse(runStatus.lastChecked) - 365 * 86_400_000)
  const months: string[] = []
  const date = new Date(Date.UTC(start.getUTCFullYear(), start.getUTCMonth(), 1))
  while (date.toISOString().slice(0, 7) <= runStatus.lastChecked.slice(0, 7)) {
    months.push(date.toISOString().slice(0, 7)); date.setUTCMonth(date.getUTCMonth() + 1)
  }
  const chosen = selected ? yearUnits.filter(u => `${u.groupId}:${u.date.slice(0, 7)}` === selected).flatMap(u => u.items) : []
  return <section id="event-timeline" className="desk-panel desk-timeline" aria-labelledby="desk-timeline-heading">
    <div className="desk-panel__head"><h2 id="desk-timeline-heading">Twelve months of tracked events</h2><span>{plural(yearUnits.length, 'event')}</span></div>
    <p className="desk-note">{start.toISOString().slice(0, 10)} to {runStatus.lastChecked}. Monthly groups; endpoint months are partial. Darker cells hold more events. Select a count to read every event and its source.</p>
    <div className="desk-timeline__scroll" tabIndex={0} role="region" aria-label="Monthly event timeline, scroll horizontally on a phone">
      <div className="desk-timeline__grid"><span />{months.map(month => <span className="desk-timeline__month" key={month}>{new Date(`${month}-01T00:00:00Z`).toLocaleDateString('en-US', { month: 'short', year: '2-digit', timeZone: 'UTC' })}</span>)}
        {eventGroups.map(group => <div className="desk-timeline__lane" key={group.id}><span>{group.label}</span>{months.map(month => {
          const count = unitsInGroup(yearUnits, group.id).filter(u => u.date.startsWith(month)).length
          const key = `${group.id}:${month}`
          return <div className="desk-timeline__cell" key={month}>{count > 0 ? <button type="button" data-level={count >= 6 ? 4 : count >= 4 ? 3 : count >= 2 ? 2 : 1} aria-label={`${group.label}, ${month}, ${plural(count, 'event')}`} aria-pressed={selected === key} aria-controls="desk-timeline-events" onClick={() => { setSelected(key); setShowAll(false) }}>{count}</button> : <span aria-label="No events">·</span>}</div>
        })}</div>)}
      </div>
    </div>
    <div id="desk-timeline-events" aria-live="polite">{selected && <><h3>{eventGroups.find(g => g.id === selected.split(':')[0])?.label} · {selected.split(':')[1]}</h3><ul className="desk-changes">{chosen.map(item => <ChangeRow key={item.id} item={item} openSupplier={openSupplier} />)}</ul></>}</div>
    <details open={showAll} onToggle={event => setShowAll(event.currentTarget.open)}><summary>Read all {yearItems.length} entries as a dated list</summary>
      <ul className="desk-changes">{yearItems.map(item => <ChangeRow key={item.id} item={item} openSupplier={openSupplier} />)}</ul>
    </details>
  </section>
}

function PublicSuppliers({ openSupplier }: { openSupplier: (id: string) => void }) {
  return <section className="desk-public" aria-labelledby="desk-public-heading"><h2 id="desk-public-heading">Public suppliers, latest reported quarter</h2>
    <p className="desk-note">Alphabetical. Select any supplier for the SEC quarterly series, exact dollar values and all dated events.</p>
    <div className="desk-public__rows">{trackerSuppliers.filter(s => s.kind === 'public').slice().sort((a, b) => a.name.localeCompare(b.name)).map(supplier => <details key={supplier.id} id={`s-${supplier.id}`}>
      <summary><span>{shortSupplierName(supplier.name)}</span><span>{supplier.revenue?.latest.yoyGrowth ?? 'No quarterly revenue figure'}</span>{supplier.revenue ? <span className="desk-public__period">Quarter ended <time dateTime={supplier.revenue.latest.periodEnd}>{supplier.revenue.latest.periodEnd}</time></span> : <span />}</summary>
      <SupplierFacts supplier={supplier} /><button type="button" onClick={() => openSupplier(supplier.id)}>Full supplier record</button>
    </details>)}</div></section>
}

function DomainBrowser({ openSupplier }: { openSupplier: (id: string) => void }) {
  const [domainId, setDomainId] = useState(trackerDomains[0].id)
  const [search, setSearch] = useState('')
  useEffect(() => {
    const selectHashDomain = () => {
      const id = window.location.hash.replace('#domain-', '')
      if (trackerDomains.some(d => d.id === id)) setDomainId(id)
    }
    selectHashDomain(); window.addEventListener('hashchange', selectHashDomain)
    return () => window.removeEventListener('hashchange', selectHashDomain)
  }, [])
  return <section id="market" className="desk-domains" aria-labelledby="market-heading">
    <div className="desk-section-head"><div><h2 id="market-heading">The market by domain</h2><p className="desk-note">Every tracked supplier, alphabetical. Company metrics measure different things; their labels and dates stay with them.</p></div>
      <label className="desk-search">Find a supplier<input type="search" value={search} onChange={e => setSearch(e.target.value)} placeholder="Name or ticker" /></label></div>
    <label className="desk-domain-select">Security domain<select value={domainId} onChange={e => setDomainId(e.target.value)}>{trackerDomains.map(d => <option value={d.id} key={d.id}>{d.name} ({suppliersForDomain(d.id).length})</option>)}</select></label>
    <div className="desk-domains__grid">{trackerDomains.map(domain => <article id={`domain-${domain.id}`} className={`tracker-domain desk-domain${search && !suppliersForDomain(domain.id).some(s => `${s.name} ${s.ticker ?? ''}`.toLowerCase().includes(search.toLowerCase())) ? ' is-search-empty' : ''}${domainId === domain.id || search ? ' is-selected' : ''}`} key={domain.id}>
      <h3>{domain.name}</h3><p className="desk-note">{domain.scope}</p><ul>{suppliersForDomain(domain.id).filter(s => `${s.name} ${s.ticker ?? ''}`.toLowerCase().includes(search.toLowerCase())).map(supplier => {
        const summary = eventSummaryForSupplier(supplier.id)
        return <li key={supplier.id}><button type="button" className="desk-supplier-link" title={supplier.name} onClick={() => openSupplier(supplier.id)}>{shortSupplierName(supplier.name)}</button>
          <span className="desk-domain__fact">{supplier.revenue ? `${supplier.revenue.latest.yoyGrowth} revenue growth · quarter ended ${supplier.revenue.latest.periodEnd}` : supplier.headlineMetric ? `${supplier.headlineMetric.label}: ${supplier.headlineMetric.value} · ${supplier.headlineMetric.period}` : formatOwnershipCompact(supplier)}</span>
          <span className="desk-note">{plural(summary.count, 'event')} in 12 months{summary.latest ? ` · last ${summary.latest.date}` : ''}</span>
        </li>
      })}</ul></article>)}</div>
  </section>
}

export function MarketDesk() {
  const [supplierId, setSupplierId] = useState<string | null>(null)
  const [groupId, setGroupId] = useState<string | null>(null)
  const [allChanges, setAllChanges] = useState(false)
  const group = eventGroups.find(g => g.id === groupId)
  const filtered = group ? unitsInGroup(monthUnits, group.id).flatMap(u => u.items).sort((a, b) => b.date.localeCompare(a.date) || a.id.localeCompare(b.id)) : changes
  return <div className="market-desk">
    <div className="desk-hero"><p className="desk-kicker">{trackerSuppliers.length} suppliers · {trackerDomains.length} domains · {certifiedCount} SEC filers certified</p><SiteMasthead />
      <CompanySearch openSupplier={setSupplierId} />
    </div>
    <div className="desk-counts" aria-label="Event counts in the last 30 days, with trailing twelve-month totals">{eventGroups.map(g => {
      const annual = unitsInGroup(yearUnits, g.id); const recent = unitsInGroup(monthUnits, g.id)
      return <button type="button" key={g.id} aria-pressed={groupId === g.id} onClick={() => { setGroupId(current => current === g.id ? null : g.id); setAllChanges(false) }}><span>{g.label}</span><strong>{recent.length}</strong><small>{annual.length} in 12 months</small></button>
    })}</div><p className="desk-note desk-counts-note">Last 30 days to {runStatus.lastChecked}, with the trailing 12-month total below each count. Counts of sourced events, one per deal, not a market ranking. Select a type to filter the change log.</p>
    <div className="desk-opening"><section id="tracker-changed" className={`desk-panel desk-changelog${allChanges ? ' is-expanded' : ''}`} aria-labelledby="tracker-changed-heading">
      <div className="desk-panel__head"><h2 id="tracker-changed-heading">What changed in the last 30 days</h2><span>{filtered.length} entries</span></div>
      <p className="desk-note">Window ends {runStatus.lastChecked}. Results and their matching SEC filing share an entry.</p>
      {group && <button type="button" onClick={() => setGroupId(null)}>Clear {group.label.toLowerCase()} filter</button>}
      <ul className="desk-changes">{(allChanges ? filtered : filtered.slice(0, 8)).map(item => <ChangeRow key={item.id} item={item} openSupplier={setSupplierId} />)}</ul>
      {filtered.length === 0 && <p className="desk-empty">No events of this type in this window.</p>}
      {filtered.length > 4 && <button type="button" className="desk-show-all" aria-expanded={allChanges} onClick={() => setAllChanges(v => !v)}>{allChanges ? 'Show fewer entries' : `Show all ${filtered.length} entries`}</button>}
    </section><GrowthChart openSupplier={setSupplierId} /></div>
    <Timeline openSupplier={setSupplierId} /><PublicSuppliers openSupplier={setSupplierId} /><DomainBrowser openSupplier={setSupplierId} />
    <SupplierDialog supplier={supplierId ? supplierById[supplierId] : null} close={() => setSupplierId(null)} />
  </div>
}
