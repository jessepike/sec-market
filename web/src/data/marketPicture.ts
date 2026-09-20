import { evidenceById as defaultEvidenceById } from './evidence'
import type { EvidenceRecord, VendorPrint } from './types'

/**
 * A security-domain id (domains.ts) mapped to the `group` string that holds
 * its vendor data in prints.ts. One domain, one group — every print's
 * primary `group` field belongs to exactly one domain here, which is what
 * keeps a vendor entry's id (see MarketPicture.tsx) from ever colliding
 * across domains without any extra bookkeeping.
 */
export const DOMAIN_PRINT_GROUP: Record<string, string> = {
  'network-sase': 'Network & edge',
  'data-ai-security': 'Data',
  'cloud-security': 'Cloud security',
  identity: 'Identity',
  secops: 'SecOps',
  'ai-runtime': 'AI runtime',
}

/**
 * Prints that report one product line or business segment, not the whole
 * company's figure — curated by id rather than inferred from `name` or
 * `metric` prose, which is free text and would be a fragile place to hang a
 * fact this load-bearing. design-spec v0.3 §3.3 names Palo Alto XSIAM as the
 * example; the coordinator's spec change for T6-2 (2026-09-20, after
 * external review) named CrowdStrike Falcon Cloud alongside it and asked for
 * the same "product line, not the whole company" tag on both.
 */
export const SEGMENT_PRINT_IDS: ReadonlySet<string> = new Set(['print-crwd-cloud', 'print-panw-xsiam'])

/** Above this many qualifying vendors, a domain shows the first six alphabetically plus a "show all" link. */
export const MAX_VISIBLE_VENDORS_PER_DOMAIN = 6

/**
 * A growth figure whose evidence predates the site's own build stamp by more
 * than this many days is marked "older figure". Compared against
 * `LAST_UPDATED_ISO` (a data constant in meta.ts), never against the
 * render-time clock — see the project rule against reading the clock during
 * render. Value set by the coordinator's spec change for T6-2 (2026-09-20),
 * superseding design-spec v0.3 §3.4's own "older than 45 days" rule for this
 * one surface.
 */
export const OLDER_FIGURE_THRESHOLD_DAYS = 120

export interface MarketPictureVendorEntry {
  print: VendorPrint
  /** ISO date of the evidence behind this figure — the newest publicationDate among its evidenceIds, or null if none resolve. */
  evidenceDate: string | null
  isOlderFigure: boolean
  isSegment: boolean
  previous: { value: string; period: string } | null
}

/** A real, comparable print — never a `coverage` record (a valuation, a raise, a close with no rate). */
function isRealComparablePrint(print: VendorPrint): boolean {
  return print.surface !== 'coverage'
}

/** A growth-rate figure carries a percent sign — what separates a rate from a dollar amount, a count, or a valuation. */
function hasGrowthFigure(print: VendorPrint): boolean {
  return print.value.includes('%')
}

function newestEvidenceDate(print: VendorPrint, evidenceByIdMap: Record<string, EvidenceRecord>): string | null {
  const dates = print.evidenceIds
    .map((id) => evidenceByIdMap[id]?.publicationDate)
    .filter((date): date is string => Boolean(date))
  if (dates.length === 0) return null
  return dates.slice().sort().at(-1) ?? null
}

function daysBetween(earlierIso: string, laterIso: string): number {
  const earlier = new Date(`${earlierIso}T00:00:00Z`).getTime()
  const later = new Date(`${laterIso}T00:00:00Z`).getTime()
  return Math.round((later - earlier) / 86_400_000)
}

/**
 * Every vendor entry a domain's market-picture row can honestly show, from a
 * set of `prints` already narrowed to one domain's group.
 *
 * Real comparable prints only (never `coverage`), and only those carrying a
 * growth-rate figure. Sorted alphabetically by vendor name — never by figure
 * size, which would read as a ranking the data cannot support across
 * differing metrics (coordinator spec change, T6-2, 2026-09-20, after
 * external review). No cut at three; callers apply
 * `MAX_VISIBLE_VENDORS_PER_DOMAIN` for display.
 *
 * A vendor/metric pair with more than one qualifying record collapses to a
 * single row: the newest becomes the entry, the next-newest becomes its
 * `previous` (value + period only — no direction arrow or word, since that
 * would need the two records to share more than a metric label to be
 * honest). Two records for the same vendor under *different* metric labels
 * are never merged — they are two different figures about two different
 * things and each stands as its own row.
 */
export function marketPictureVendorEntries(
  prints: VendorPrint[],
  todayIso: string,
  evidenceByIdMap: Record<string, EvidenceRecord> = defaultEvidenceById,
): MarketPictureVendorEntry[] {
  const qualifying = prints.filter((print) => isRealComparablePrint(print) && hasGrowthFigure(print))

  const byVendorMetric = new Map<string, VendorPrint[]>()
  for (const print of qualifying) {
    const key = `${print.name}\u0000${print.metric}`
    const list = byVendorMetric.get(key)
    if (list) {
      list.push(print)
    } else {
      byVendorMetric.set(key, [print])
    }
  }

  const entries: MarketPictureVendorEntry[] = []
  for (const list of byVendorMetric.values()) {
    const withDates = list
      .map((print) => ({ print, evidenceDate: newestEvidenceDate(print, evidenceByIdMap) }))
      // Newest evidence first; a print with no resolvable evidence date sorts
      // last so it never masquerades as the current figure over a dated one.
      .sort((a, b) => (b.evidenceDate ?? '').localeCompare(a.evidenceDate ?? ''))

    const [current, prior] = withDates
    const evidenceDate = current.evidenceDate
    const isOlderFigure = evidenceDate !== null && daysBetween(evidenceDate, todayIso) > OLDER_FIGURE_THRESHOLD_DAYS

    entries.push({
      print: current.print,
      evidenceDate,
      isOlderFigure,
      isSegment: SEGMENT_PRINT_IDS.has(current.print.id),
      previous: prior ? { value: prior.print.value, period: prior.print.period } : null,
    })
  }

  return entries.sort((a, b) => a.print.name.localeCompare(b.print.name))
}
