/**
 * Pure helpers over the tracker data (domains.ts, suppliers.ts, events.ts).
 * Kept separate from the components so the logic can be unit-tested without
 * rendering React — see tests/tracker-data.test.ts.
 */
import { runStatus } from '../runStatus'
import { trackerEvents } from './events'
import { trackerSuppliers } from './suppliers'
import type { TrackerEvent } from './events'
import type { TrackerSupplier } from './suppliers'

/** Suppliers assigned to a domain, alphabetical by name — the front page's default order. */
export function suppliersForDomain(domainId: string): TrackerSupplier[] {
  return trackerSuppliers
    .filter((supplier) => supplier.domainIds.includes(domainId))
    .slice()
    .sort((a, b) => a.name.localeCompare(b.name))
}

/** Parses a leading "+26%" / "-5.2%" / "26%" style string into a signed number, or null if unparseable. */
export function parseGrowthPercent(value: string | undefined): number | null {
  if (!value) return null
  const match = value.match(/(-?\+?\d+(\.\d+)?)\s*%/)
  if (!match) return null
  const num = Number(match[1].replace('+', ''))
  return Number.isFinite(num) ? num : null
}

/**
 * Density pass (coordinator instruction, following the step 5 build) — a
 * reader-facing short name, stripping the legal-entity suffix a filing or
 * press release carries ("CrowdStrike Holdings, Inc." -> "CrowdStrike") but
 * leaving genuine brand words alone ("Palo Alto Networks", "Cato Networks",
 * "Microsoft Defender for Endpoint" are untouched). The full legal name
 * stays wherever a name is sourced as a fact — evidence.ts, and the `title`
 * attribute anywhere this is used. A trailing parenthetical alternate name
 * ("Sophos Group (Sophos Ltd)") is dropped in favor of the leading name.
 */
const LEGAL_SUFFIX = /,?\s+(Incorporated|Corporation|Corp\.?|Holdings|Technologies|Software|Group|Inc\.?|LLC|Ltd\.?|Limited)$/i

export function shortSupplierName(name: string): string {
  let short = name.trim().replace(/\s*\([^)]*\)\s*$/, '')
  let previous: string
  do {
    previous = short
    short = short.replace(LEGAL_SUFFIX, '').trim()
  } while (short !== previous && short.length > 0)
  return short || name
}

const MONTHS_SHORT = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

function monthPart(dateStr: string): { month: string; year2: string; year4: string } | null {
  const [y, m] = dateStr.split('-')
  const yearNum = Number(y)
  const monthIndex = Number(m) - 1
  if (!Number.isFinite(yearNum) || monthIndex < 0 || monthIndex > 11) return null
  return { month: MONTHS_SHORT[monthIndex], year2: String(yearNum).slice(-2), year4: String(yearNum) }
}

/** "2026-07-31" -> "Q Jul 26" — the muted mono period label next to a growth figure. */
export function formatShortQuarter(dateStr: string | undefined): string {
  if (!dateStr) return ''
  const parts = monthPart(dateStr)
  return parts ? `Q ${parts.month} ${parts.year2}` : dateStr
}

/** "2026-08-12" -> "12 Aug 26" — a compact event date. */
export function formatShortDate(dateStr: string | undefined): string {
  if (!dateStr) return ''
  const [, , d] = dateStr.split('-')
  const parts = monthPart(dateStr)
  if (!parts) return dateStr
  const day = Number(d)
  return Number.isFinite(day) ? `${day} ${parts.month} ${parts.year2}` : `${parts.month} ${parts.year2}`
}

/** "2026-04-20" or "2026-04" -> "Apr 2026" — for an ownership or funding date. */
export function formatMonthYear(dateStr: string | undefined): string {
  if (!dateStr) return ''
  const parts = monthPart(dateStr)
  return parts ? `${parts.month} ${parts.year4}` : dateStr
}

/** "2020-03-01" -> "2020" — for a PE-ownership year. */
export function formatYear(dateStr: string | undefined): string {
  if (!dateStr) return ''
  return dateStr.slice(0, 4)
}

/**
 * "$5.84 billion" -> "$5.84B", "$651.4 million" -> "$651.4M", preserving any
 * leading qualifier (">$1.7 billion" -> ">$1.7B"). Text with no
 * billion/million unit passes through unchanged.
 */
export function abbreviateDollar(text: string | undefined): string {
  if (!text) return ''
  return text
    .replace(/([\d.,]+)\s*billion/gi, '$1B')
    .replace(/([\d.,]+)\s*million/gi, '$1M')
}

/** Pulls "2026-07-31" out of a period string like "Q2 FY2027, ended 2026-07-31". */
function endedDate(period: string): string | undefined {
  const match = period.match(/(\d{4}-\d{2}-\d{2})/)
  return match?.[1]
}

/** "ARR $5.84B · Q Jul 26" — the company's own headline metric, compacted. */
export function formatHeadlineCompact(supplier: TrackerSupplier): string {
  const metric = supplier.headlineMetric
  if (!metric) return ''
  const value = abbreviateDollar(metric.value)
  const ended = endedDate(metric.period)
  const quarter = ended ? formatShortQuarter(ended) : ''
  return [`${metric.label} ${value}`.trim(), quarter].filter(Boolean).join(' · ')
}

/** Pulls a parent-company name out of "Segment of X Corporation (publicly traded...)." */
function segmentParentFromStatus(status: string): string {
  const match = status.match(/Segment of ([^.(]+)/i)
  return match ? shortSupplierName(match[1].trim()) : ''
}

/**
 * "Public · CRWD", "Segment of Microsoft", "PE-owned · Thoma Bravo (2022)",
 * "Acquired by ServiceNow · Apr 2026", or "Series D $300M · Sep 2026" for a
 * private company's last funding round — one compact fact for the
 * ownership-or-last-round column. Falls back to the raw ownership sentence
 * for a shape this pass did not anticipate, and to an em-free en dash when
 * there is nothing to show at all.
 */
export function formatOwnershipCompact(supplier: TrackerSupplier): string {
  if (supplier.lastRound) {
    const round = supplier.lastRound
    const amount = abbreviateDollar(round.amount)
    const when = formatMonthYear(round.date)
    return [`${round.stage} ${amount}`.trim(), when].filter(Boolean).join(' · ')
  }
  const ownership = supplier.ownership
  if (!ownership) return '–'

  switch (supplier.kind) {
    case 'public':
      return supplier.ticker ? `Public · ${supplier.ticker}` : 'Public'
    case 'segment': {
      const parent = ownership.acquirer ? shortSupplierName(ownership.acquirer) : segmentParentFromStatus(ownership.status)
      return parent ? `Segment of ${parent}` : 'Segment'
    }
    case 'pe-owned': {
      const who = ownership.acquirer ? shortSupplierName(ownership.acquirer) : ''
      const year = formatYear(ownership.announced ?? ownership.closed)
      const detail = [who, year ? `(${year})` : ''].filter(Boolean).join(' ')
      return detail ? `PE-owned · ${detail}` : 'PE-owned'
    }
    case 'acquired': {
      const who = ownership.acquirer ? shortSupplierName(ownership.acquirer) : ''
      const when = formatMonthYear(ownership.closed ?? ownership.announced)
      if (!who) return 'Acquired'
      return when ? `Acquired by ${who} · ${when}` : `Acquired by ${who}`
    }
    default:
      return ownership.status
  }
}

/** Median of the latest reported YoY revenue growth across a domain's public suppliers, or null with fewer than 2. */
export function medianRevenueGrowthForDomain(domainId: string): number | null {
  const values = suppliersForDomain(domainId)
    .filter((supplier) => supplier.kind === 'public' || supplier.kind === 'segment')
    .map((supplier) => parseGrowthPercent(supplier.revenue?.latest.yoyGrowth))
    .filter((value): value is number => value !== null)
  if (values.length < 2) return null
  const sorted = values.slice().sort((a, b) => a - b)
  const mid = Math.floor(sorted.length / 2)
  return sorted.length % 2 === 0 ? (sorted[mid - 1] + sorted[mid]) / 2 : sorted[mid]
}

/** Events for one supplier, newest first. */
export function eventsForSupplier(supplierId: string): TrackerEvent[] {
  return trackerEvents
    .filter((event) => event.supplierId === supplierId)
    .slice()
    .sort((a, b) => (a.date < b.date ? 1 : a.date > b.date ? -1 : 0))
}

/** Count of events in the 12 months ending on the last checked date for one supplier, and the newest one if any. */
export function eventSummaryForSupplier(supplierId: string): { count: number; latest: TrackerEvent | null } {
  const events = eventsForSupplier(supplierId).filter((event) => {
    const age = daysBetween(event.date, runStatus.lastChecked)
    return age >= 0 && age <= 365
  })
  return { count: events.length, latest: events[0] ?? null }
}

function daysBetween(earlier: string, later: string): number {
  const [ey, em, ed] = earlier.split('-').map(Number)
  const [ly, lm, ld] = later.split('-').map(Number)
  const earlierMs = Date.UTC(ey, em - 1, ed)
  const laterMs = Date.UTC(ly, lm - 1, ld)
  return Math.round((laterMs - earlierMs) / 86_400_000)
}

/** Tracker events dated within the 30 days ending on `today` (inclusive), newest first. */
export function eventsInLast30Days(today: string): TrackerEvent[] {
  return trackerEvents
    .filter((event) => {
      const age = daysBetween(event.date, today)
      return age >= 0 && age <= 30
    })
    .slice()
    .sort((a, b) => (a.date < b.date ? 1 : a.date > b.date ? -1 : 0))
}

export interface EdgarFiling {
  supplierId: string
  periodEnd: string
  filedDate: string
  form: string
  value: number
  sourceUrl: string
}

interface EdgarFactsFile {
  generatedAt: string
  suppliers: Array<{
    id: string
    name: string
    cik: string
    quarters: Array<{
      periodEnd: string
      filedDate: string
      form: string
      value: number
      sourceUrl: string
    }>
  }>
}

/**
 * EDGAR-filed quarters (from generated/edgarFacts.json) with a filing date
 * within 30 days of `today` — restricted to each supplier's single latest
 * (most recent `periodEnd`) quarter.
 *
 * A 10-Q/10-K also carries the same-quarter-prior-year figure as a
 * comparative, and `edgarLogic.ts`'s `dedupeByPeriodEnd` keeps whichever
 * fact for a given `periodEnd` was filed most recently — so a prior-year
 * quarter's stored `filedDate` is the date of the NEWEST filing that
 * restated it, not the date it was first reported. Scanning every quarter
 * in `supplier.quarters` (as this function used to) treated that restated
 * comparative as a fresh filing and produced entries like "filed its 10-Q
 * for the quarter ended 2025-07-31" alongside the real, current filing for
 * 2026-07-31 filed on the same day. Only a supplier's chronologically
 * latest quarter (its true newest filing) is eligible to appear here.
 */
export function edgarFilingsInLast30Days(today: string, facts: EdgarFactsFile): EdgarFiling[] {
  const out: EdgarFiling[] = []
  for (const supplier of facts.suppliers) {
    if (supplier.quarters.length === 0) continue
    const latest = supplier.quarters.reduce((newest, quarter) =>
      quarter.periodEnd > newest.periodEnd ? quarter : newest,
    )
    const age = daysBetween(latest.filedDate, today)
    if (age >= 0 && age <= 30) {
      out.push({
        supplierId: supplier.id,
        periodEnd: latest.periodEnd,
        filedDate: latest.filedDate,
        form: latest.form,
        value: latest.value,
        sourceUrl: latest.sourceUrl,
      })
    }
  }
  return out.sort((a, b) => (a.filedDate < b.filedDate ? 1 : a.filedDate > b.filedDate ? -1 : 0))
}
