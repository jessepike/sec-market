/**
 * The front page feed and the one-line snapshot under each count tile.
 *
 * Routine SEC filings (a 10-Q or 10-K with no other news) and results
 * announcements leave the front feed: the growth they carry is shown in the
 * momentum view, and every filing stays in the activity ledger on the
 * company page and in /filings.csv. Funding, acquisitions, restructuring,
 * debt and leadership stay, ordered by the dollar amount the source states,
 * then by date. That order is a sort on a stated number, not a ranking.
 */
import { shortSupplierName } from './names'
import { countedUnits, eventGroups, recentChanges, secFilingsInLastYear } from './presentation'
import type { ChangeItem, CountedUnit } from './presentation'
import { trackerSuppliers } from './suppliers'

const nameOf = (id: string) => shortSupplierName(trackerSuppliers.find(s => s.id === id)?.name ?? id)

/** Routine items that belong in the activity ledger, not the front feed. */
export const isLedgerItem = (item: ChangeItem) => item.type === 'filing' || item.type === 'results'

/**
 * The first dollar amount stated in an event's own text, in USD, or null.
 * "$N million", "$N billion" and full figures of $1,000,000 or more count; per-share prices do not.
 */
export function statedAmount(text: string): number | null {
  const m = text.match(/\$\s?(\d[\d,]*(?:\.\d+)?)\s*(million|billion)\b/i)
  if (m) return Number(m[1].replaceAll(',', '')) * (m[2].toLowerCase() === 'billion' ? 1e9 : 1e6)
  // A full figure such as "$1,250,000,000" counts from $1 million up.
  const full = text.match(/\$(\d{1,3}(?:,\d{3}){2,})(?!\.\d|\d)/)
  return full ? Number(full[1].replaceAll(',', '')) : null
}

const unitAmount = (unit: CountedUnit) => Math.max(...unit.items.map(i => statedAmount(i.text) ?? 0))

/** Largest stated amount first, then newest, then id; items with no amount follow by date. */
export function byStatedAmount(a: ChangeItem, b: ChangeItem): number {
  return (statedAmount(b.text) ?? 0) - (statedAmount(a.text) ?? 0) || b.date.localeCompare(a.date) || a.id.localeCompare(b.id)
}

export const monthChanges = recentChanges()
export const feedChanges = monthChanges.filter(item => !isLedgerItem(item)).sort(byStatedAmount)
export const ledgerChanges = monthChanges.filter(isLedgerItem)
export const monthUnits = countedUnits(monthChanges)

function shortAmount(n: number): string {
  return n >= 1e9 ? `$${(n / 1e9).toFixed(n >= 1e10 ? 0 : 1)}B` : `$${Math.round(n / 1e6)}M`
}

/**
 * "Varonis $6.3B · Upwind" — the companies behind a tile's count, largest stated amount first,
 * at most `limit` names, then "+N more". Empty when the tile counts nothing.
 */
export function tileSnapshot(groupId: string, limit = 3): string {
  const units = monthUnits.filter(u => u.groupId === groupId)
    .sort((a, b) => unitAmount(b) - unitAmount(a) || b.date.localeCompare(a.date) || a.key.localeCompare(b.key))
  const parts = units.map(unit => {
    const names = [...new Set(unit.items.map(i => nameOf(i.supplierId)))].join(' and ')
    const amount = unitAmount(unit)
    return amount > 0 ? `${names} ${shortAmount(amount)}` : names
  })
  const shown = [...new Set(parts)]
  if (shown.length === 0) return ''
  return shown.slice(0, limit).join(' · ') + (shown.length > limit ? ` · +${shown.length - limit} more` : '')
}

export const tileSnapshots: Record<string, string> = Object.fromEntries(eventGroups.map(g => [g.id, tileSnapshot(g.id)]))

/** Every SEC quarterly filing for one supplier in the trailing 12 months, newest first. */
export function filingLedger(supplierId: string) {
  return secFilingsInLastYear().filter(f => f.supplierId === supplierId).sort((a, b) => b.filedDate.localeCompare(a.filedDate))
}
