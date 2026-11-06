/**
 * The front page feed and the names under each count tile.
 *
 * Routine SEC filings (a 10-Q or 10-K with no other news) and results announcements leave the
 * front feed: the growth they carry is in the revenue growth view, and every filing stays in the
 * activity ledger on the company page and in /filings.csv. Funding, acquisitions, restructuring,
 * debt and leadership stay, newest first.
 */
import { parseAmount } from './eventFacts'
import { shortSupplierName } from './names'
import { countedUnits, eventGroups, recentChanges, secFilingsInLastYear } from './presentation'
import type { ChangeItem } from './presentation'
import { trackerSuppliers } from './suppliers'

const nameOf = (id: string) => shortSupplierName(trackerSuppliers.find(s => s.id === id)?.name ?? id)

/** Routine items that belong in the activity ledger, not the front feed. */
export const isLedgerItem = (item: ChangeItem) => item.type === 'filing' || item.type === 'results'

/** The first dollar amount stated in an event's own text, in USD, or null. */
export const statedAmount = parseAmount

export const byNewest = (a: ChangeItem, b: ChangeItem) => b.date.localeCompare(a.date) || a.id.localeCompare(b.id)

export const monthChanges = recentChanges()
export const feedChanges = monthChanges.filter(item => !isLedgerItem(item)).sort(byNewest)
export const monthUnits = countedUnits(monthChanges)

/** "Varonis Systems · Upwind": the companies behind a tile's count, newest first, then "+N more". */
export function tileSnapshot(groupId: string, limit = 2): string {
  const units = monthUnits.filter(u => u.groupId === groupId).sort((a, b) => b.date.localeCompare(a.date) || a.key.localeCompare(b.key))
  const names = [...new Set(units.map(unit => [...new Set(unit.items.map(i => nameOf(i.supplierId)))].join(' and ')))]
  if (names.length === 0) return ''
  return names.slice(0, limit).join(' · ') + (names.length > limit ? ` · +${names.length - limit} more` : '')
}

export const tileSnapshots: Record<string, string> = Object.fromEntries(eventGroups.map(g => [g.id, tileSnapshot(g.id)]))

/** Every SEC quarterly filing for one supplier in the trailing 12 months, newest first. */
export function filingLedger(supplierId: string) {
  return secFilingsInLastYear().filter(f => f.supplierId === supplierId).sort((a, b) => b.filedDate.localeCompare(a.filedDate))
}
