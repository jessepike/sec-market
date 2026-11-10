/**
 * The front page feed and the names under each count tile.
 *
 * One entry per event, newest first. Entries that report one deal (an announcement, the buyer's
 * financing, a later merger proxy) are one entry that leads with the deal and names the latest
 * step. A quarterly result is an entry that states revenue and growth, not that a form was filed.
 * A filing notice that names no person, amount or deal stays in the company's activity ledger
 * and in /filings.csv, and is not counted on the tiles.
 */
import { eventFact, filingStep, isFilingNotice, parseAmount, shortUsd } from './eventFacts'
import type { EventFact } from './eventFacts'
import { shortSupplierName } from './names'
import { countedUnits, dealParent, eventGroups, quarterlyGrowth, recentChanges, yearChanges } from './presentation'
import type { ChangeItem } from './presentation'
import { trackerSuppliers } from './suppliers'

const supplierOf = (id: string) => trackerSuppliers.find(s => s.id === id)
const nameOf = (id: string) => shortSupplierName(supplierOf(id)?.name ?? id)
const signed = (n: number) => `${n > 0 ? '+' : n < 0 ? '−' : ''}${Math.abs(n).toFixed(1)}%`

/** A quarterly result or filing: the entries that state revenue and growth. */
export const isResultItem = (item: ChangeItem) => item.type === 'filing' || item.type === 'results'

/** The first dollar amount stated in an event's own text, in USD, or null. */
export const statedAmount = parseAmount

/**
 * A result as numbers: revenue for the quarter, year-over-year growth, and the growth rate of
 * the quarter before, all from the SEC series. Null when the quarter is not in that series.
 */
export function resultFact(item: ChangeItem): EventFact | null {
  const supplier = supplierOf(item.supplierId)
  const filing = item.filings[0]
  if (!supplier?.edgarId || !filing) return null
  const series = quarterlyGrowth(supplier.edgarId)
  const at = series.findIndex(q => q.periodEnd === filing.periodEnd)
  if (at < 0) return null
  const prior = series[at - 1]
  return { line: `Revenue ${shortUsd(series[at].value)}`, status: null,
    amount: { value: series[at].growth, text: signed(series[at].growth), label: 'year over year' },
    detail: `${prior ? `${signed(prior.growth)} the quarter before · ` : ''}quarter ended ${filing.periodEnd}` }
}

export interface FeedEntry {
  key: string
  /** The newest date among the entry's items. */
  date: string
  groupId: string
  /** The item whose fact leads the line. */
  primary: ChangeItem
  /** Every sourced item in the entry, newest first. */
  items: ChangeItem[]
  fact: EventFact
  /** The latest step, when a later filing adds to a deal already on file. */
  step: { label: string; date: string } | null
}

const yearItems = yearChanges()
const ownership = (item: ChangeItem) => item.type === 'acquisition' || item.type === 'divestiture'
const score = (item: ChangeItem) => { const f = eventFact(item); return (ownership(item) ? 4 : 0) + (f.amount ? 2 : 0) + (f.line.endsWith('…') ? 0 : 1) }

function entryFor(unit: { key: string; groupId: string; items: ChangeItem[] }): FeedEntry | null {
  const newest = unit.items.slice().sort((a, b) => b.date.localeCompare(a.date) || a.id.localeCompare(b.id))
  const base = { key: unit.key, date: newest[0].date, groupId: unit.groupId }
  if (isResultItem(newest[0])) return { ...base, primary: newest[0], items: newest, fact: resultFact(newest[0]) ?? eventFact(newest[0]), step: null }
  const stated = newest.filter(item => !isFilingNotice(item.text))
  const notice = newest.find(item => isFilingNotice(item.text))
  // A deal announced before this window: the notice still leads with that deal.
  const earlier = stated.length === 0 ? dealParent(newest[0], yearItems) : null
  const lead = stated.slice().sort((a, b) => score(b) - score(a) || b.date.localeCompare(a.date) || a.id.localeCompare(b.id))[0] ?? earlier
  if (!lead) return null
  return { ...base, primary: lead, items: earlier ? [...newest, earlier] : newest, fact: eventFact(lead),
    step: notice && ownership(notice) && notice.date > lead.date ? { label: filingStep(notice.text), date: notice.date } : null }
}

export const monthChanges = recentChanges()
const units = countedUnits(monthChanges)
export const feedEntries: FeedEntry[] = units.flatMap(unit => entryFor(unit) ?? [])
  .sort((a, b) => b.date.localeCompare(a.date) || a.key.localeCompare(b.key))
/** Filing notices with nothing to state, kept in the ledger: how many the feed leaves out. */
export const ledgerNoticeCount = units.length - feedEntries.length

export const entriesInGroup = (groupId: string) => feedEntries.filter(entry => entry.groupId === groupId)

/** "Proofpoint and Varonis Systems · Upwind": the companies behind a tile's count, newest first, then "+N more". */
export function tileSnapshot(groupId: string, limit = 2): string {
  const names = [...new Set(entriesInGroup(groupId).map(entry => [...new Set([entry.primary, ...entry.items].map(i => nameOf(i.supplierId)))].join(' and ')))]
  if (names.length === 0) return ''
  return names.slice(0, limit).join(' · ') + (names.length > limit ? ` · +${names.length - limit} more` : '')
}

export const tileSnapshots: Record<string, string> = Object.fromEntries(eventGroups.map(g => [g.id, tileSnapshot(g.id)]))

import { secFilingsInLastYear } from './presentation'

/** Every SEC quarterly filing for one supplier in the trailing 12 months, newest first. */
export function filingLedger(supplierId: string) {
  return secFilingsInLastYear().filter(f => f.supplierId === supplierId).sort((a, b) => b.filedDate.localeCompare(a.filedDate))
}
