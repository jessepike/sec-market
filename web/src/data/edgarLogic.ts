/**
 * Pure extraction and validation logic for the SEC EDGAR revenue runner
 * (step 2 of docs/active/autonomy-coverage-plan.md §5). No network calls
 * live here — `web/scripts/edgar-refresh.ts` fetches each supplier's
 * `companyfacts` JSON and hands it to `buildSupplierRecord` below. Kept
 * network-free on purpose so `tests/edgar-logic.test.ts` can run against
 * saved fixture JSON with no network access, the same pattern already used
 * by `staleReport.ts` / `stale-report.test.ts`.
 *
 * The shape being parsed is SEC's XBRL "companyfacts" API:
 * https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json — an
 * `us-gaap` concept (e.g. `Revenues`) maps to a `units.USD` array of facts,
 * each `{ start, end, val, accn, fy, fp, form, filed, frame? }`.
 */

export interface XbrlFact {
  start?: string
  end: string
  val: number
  accn: string
  fy?: number
  fp?: string
  form: string
  filed: string
  frame?: string
}

export interface CompanyFactsConcept {
  label?: string
  description?: string
  units?: {
    USD?: XbrlFact[]
    [unit: string]: XbrlFact[] | undefined
  }
}

export interface CompanyFacts {
  cik?: number
  entityName?: string
  facts?: {
    'us-gaap'?: Record<string, CompanyFactsConcept>
    [taxonomy: string]: Record<string, CompanyFactsConcept> | undefined
  }
}

export interface QuarterFact {
  periodStart: string
  periodEnd: string
  value: number
  form: string
  accessionNumber: string
  filedDate: string
  sourceUrl: string
  derived: boolean
  fiscalYear: number | null
  fiscalQuarter: 'Q1' | 'Q2' | 'Q3' | 'Q4' | null
}

export interface YoyFigure {
  quarter: QuarterFact
  priorYearQuarter: QuarterFact | null
  growth: number | null
  flags: string[]
}

export interface SupplierRecord {
  id: string
  name: string
  cik: string
  concept: string
  quarters: QuarterFact[]
  latest: YoyFigure | null
  prior: YoyFigure | null
  notes: string[]
}

export interface SupplierFailure {
  id: string
  name: string
  reason: string
}

const QUARTER_MIN_DAYS = 80
const QUARTER_MAX_DAYS = 100
const ANNUAL_MIN_DAYS = 340
const ANNUAL_MAX_DAYS = 386
/** Same-quarter-prior-year window: 350–380 days, centered on 365. */
const PRIOR_YEAR_MIN_DAYS = 350
const PRIOR_YEAR_MAX_DAYS = 380
const GROWTH_BAND = 0.8

export function daysBetween(startIso: string, endIso: string): number {
  const start = Date.parse(`${startIso}T00:00:00Z`)
  const end = Date.parse(`${endIso}T00:00:00Z`)
  return Math.round((end - start) / (1000 * 60 * 60 * 24))
}

/**
 * The calendar day after `dateIso`. XBRL fiscal periods are contiguous —
 * a quarter's period never overlaps or gaps the next one, so Q2 starts the
 * day after Q1 ends (e.g. Q1 ending 2024-03-31 is followed by Q2 starting
 * 2024-04-01, not another 2024-03-31). Used to chain Q1→Q2→Q3 and to place
 * a derived Q4's start right after Q3's end.
 */
function nextDay(dateIso: string): string {
  const date = new Date(`${dateIso}T00:00:00Z`)
  date.setUTCDate(date.getUTCDate() + 1)
  return date.toISOString().slice(0, 10)
}

export function isQuarterlyDuration(days: number): boolean {
  return days >= QUARTER_MIN_DAYS && days <= QUARTER_MAX_DAYS
}

export function isAnnualDuration(days: number): boolean {
  return days >= ANNUAL_MIN_DAYS && days <= ANNUAL_MAX_DAYS
}

/**
 * The filing index page for one accession, e.g.
 * https://www.sec.gov/Archives/edgar/data/1535527/000153552726000123/0001535527-26-000123-index.htm
 */
export function buildFilingIndexUrl(cikNumeric: number, accn: string): string {
  const noDashes = accn.replace(/-/g, '')
  return `https://www.sec.gov/Archives/edgar/data/${cikNumeric}/${noDashes}/${accn}-index.htm`
}

/**
 * Picks the first concept (in priority order) that has at least one
 * 10-Q/10-K USD fact. Returns null if none of the candidate concepts exist
 * or none has usable data — the caller records that as a failure rather
 * than guessing at a different tag.
 */
export function selectRevenueFacts(
  companyFacts: CompanyFacts,
  concepts: string[],
): { concept: string; facts: XbrlFact[] } | null {
  const gaap = companyFacts.facts?.['us-gaap']
  if (!gaap) return null
  for (const concept of concepts) {
    const usd = gaap[concept]?.units?.USD
    if (!usd || usd.length === 0) continue
    const filingFacts = usd.filter((f) => f.form === '10-Q' || f.form === '10-K')
    if (filingFacts.length === 0) continue
    return { concept, facts: filingFacts }
  }
  return null
}

/**
 * De-duplicates facts that share a period end date — a restated figure for
 * a quarter already reported (e.g. shown again as a comparative in a later
 * filing) — by keeping the one with the latest `filed` date. A tie on
 * `filed` keeps the fact with the lexicographically greatest accession
 * number, which for EDGAR accession numbers is also the later filing.
 */
function dedupeByPeriodEnd(facts: XbrlFact[]): Map<string, XbrlFact> {
  const byEnd = new Map<string, XbrlFact>()
  for (const fact of facts) {
    const existing = byEnd.get(fact.end)
    if (!existing) {
      byEnd.set(fact.end, fact)
      continue
    }
    if (fact.filed > existing.filed || (fact.filed === existing.filed && fact.accn > existing.accn)) {
      byEnd.set(fact.end, fact)
    }
  }
  return byEnd
}

function toQuarterFact(fact: XbrlFact, cikNumeric: number, derived: boolean): QuarterFact {
  const fiscalQuarter =
    fact.fp === 'Q1' || fact.fp === 'Q2' || fact.fp === 'Q3' || fact.fp === 'Q4' ? fact.fp : null
  return {
    periodStart: fact.start ?? '',
    periodEnd: fact.end,
    value: fact.val,
    form: fact.form,
    accessionNumber: fact.accn,
    filedDate: fact.filed,
    sourceUrl: buildFilingIndexUrl(cikNumeric, fact.accn),
    derived,
    fiscalYear: fact.fy ?? null,
    fiscalQuarter,
  }
}

/**
 * Builds the deduped, Q4-derived quarterly series from raw 10-Q/10-K USD
 * facts for one revenue concept. Quarterly facts (80–100 day duration) are
 * used directly. A fiscal Q4 usually has no discrete 10-Q tag — annual
 * facts (340–386 days, from a 10-K) are matched to the three preceding
 * quarters by date (Q1's start equals the annual period's start, each
 * quarter's end equals the next quarter's start, and the third quarter's
 * end sits one quarter before the annual period's end); Q4 is then the
 * annual total minus that sum, marked `derived: true`. Where an annual
 * period's end date already has a directly reported quarterly fact (some
 * filers do tag Q4 separately), the reported figure is kept and nothing is
 * derived for that year.
 */
export function buildQuarterSeries(
  facts: XbrlFact[],
  cikNumeric: number,
): { quarters: QuarterFact[]; notes: string[] } {
  const notes: string[] = []
  const quarterlyRaw = facts.filter((f) => f.start && isQuarterlyDuration(daysBetween(f.start, f.end)))
  const annualRaw = facts.filter(
    (f) => f.form === '10-K' && f.start && isAnnualDuration(daysBetween(f.start, f.end)),
  )

  const quarterlyByEnd = dedupeByPeriodEnd(quarterlyRaw)
  const annualByEnd = dedupeByPeriodEnd(annualRaw)

  const quarters: QuarterFact[] = []
  for (const fact of quarterlyByEnd.values()) {
    quarters.push(toQuarterFact(fact, cikNumeric, false))
  }

  for (const annual of annualByEnd.values()) {
    if (quarterlyByEnd.has(annual.end)) {
      // Some filers do tag Q4 directly; nothing to derive.
      continue
    }
    if (!annual.start) continue

    const q1 = [...quarterlyByEnd.values()].find((q) => q.start === annual.start)
    const q2 = q1 ? [...quarterlyByEnd.values()].find((q) => q.start === nextDay(q1.end)) : undefined
    const q3 = q2 ? [...quarterlyByEnd.values()].find((q) => q.start === nextDay(q2.end)) : undefined

    if (!q1 || !q2 || !q3) {
      notes.push(
        `${annual.end}: annual fact present but could not find all three preceding quarters to derive Q4 (fy ${annual.fy ?? 'unknown'}).`,
      )
      continue
    }
    const q4Start = nextDay(q3.end)
    const gapDays = daysBetween(q4Start, annual.end)
    if (!isQuarterlyDuration(gapDays)) {
      notes.push(
        `${annual.end}: implied Q4 (${q4Start} to ${annual.end}) is ${gapDays} days, outside the 80–100 day quarterly window — skipped Q4 derivation.`,
      )
      continue
    }

    const derivedValue = annual.val - (q1.val + q2.val + q3.val)
    quarters.push({
      periodStart: q4Start,
      periodEnd: annual.end,
      value: derivedValue,
      form: `${annual.form} (derived)`,
      accessionNumber: annual.accn,
      filedDate: annual.filed,
      sourceUrl: buildFilingIndexUrl(cikNumeric, annual.accn),
      derived: true,
      fiscalYear: annual.fy ?? null,
      fiscalQuarter: 'Q4',
    })
  }

  quarters.sort((a, b) => (a.periodEnd < b.periodEnd ? 1 : a.periodEnd > b.periodEnd ? -1 : 0))
  return { quarters, notes }
}

/**
 * Finds the same-fiscal-quarter prior-year figure for `quarter` within
 * `quarters`: the entry whose period end is 350–380 days earlier. Prefers
 * an exact `fiscalQuarter` label match when both have one; otherwise falls
 * back to the closest end date in that window.
 */
export function findPriorYearQuarter(quarter: QuarterFact, quarters: QuarterFact[]): QuarterFact | null {
  const candidates = quarters.filter((q) => {
    if (q === quarter) return false
    const gap = daysBetween(q.periodEnd, quarter.periodEnd)
    return gap >= PRIOR_YEAR_MIN_DAYS && gap <= PRIOR_YEAR_MAX_DAYS
  })
  if (candidates.length === 0) return null
  const labeled = candidates.filter((q) => q.fiscalQuarter && q.fiscalQuarter === quarter.fiscalQuarter)
  const pool = labeled.length > 0 ? labeled : candidates
  return pool.reduce((closest, q) => {
    const closestGap = Math.abs(daysBetween(closest.periodEnd, quarter.periodEnd) - 365)
    const qGap = Math.abs(daysBetween(q.periodEnd, quarter.periodEnd) - 365)
    return qGap < closestGap ? q : closest
  })
}

/**
 * Computes YoY growth for one quarter against its same-quarter-prior-year
 * figure, plus validation flags. Never drops the figure for being out of
 * band — it flags it instead, per the runner's brief.
 */
export function computeYoy(quarter: QuarterFact, quarters: QuarterFact[]): YoyFigure {
  const priorYearQuarter = findPriorYearQuarter(quarter, quarters)
  const flags: string[] = []

  if (!isQuarterlyDuration(daysBetween(quarter.periodStart, quarter.periodEnd))) {
    flags.push('unexpected-duration')
  }
  if (!priorYearQuarter) {
    flags.push('no-prior-year-match')
  }
  if (priorYearQuarter && quarter.fiscalQuarter && priorYearQuarter.fiscalQuarter) {
    if (quarter.fiscalQuarter !== priorYearQuarter.fiscalQuarter) {
      flags.push('fiscal-period-mismatch')
    }
  }

  let growth: number | null = null
  if (priorYearQuarter && priorYearQuarter.value !== 0) {
    growth = (quarter.value - priorYearQuarter.value) / priorYearQuarter.value
    if (Math.abs(growth) > GROWTH_BAND) {
      flags.push('growth-out-of-band')
    }
  } else if (priorYearQuarter) {
    flags.push('prior-year-value-zero')
  }

  return { quarter, priorYearQuarter, growth, flags }
}

/**
 * The fiscal quarter and fiscal year a `periodEnd` falls in, given a
 * filer's fiscal year end (`edgarRegistry.ts`'s `fiscalYearEnd`, "MMDD").
 * AUTO-001 fix pass (2026-09-26), item 2: written for `verify-tracker.ts`'s
 * period-label gate, after two blind scorers caught SailPoint's and Okta's
 * `revenue.latest.period`/`revenue.prior.period` hand-typed as "Q4 FY2027"/
 * "Q3 FY2027" for a periodEnd (2026-07-31 / 2026-04-30) that is actually
 * each filer's Q2/Q1 FY2027 under its own 0131 fiscal year end.
 *
 * A filer's fiscal year end recurs on the same MM-DD every year; the
 * quarter a `periodEnd` sits in is the nearest fiscal-year-end date at or
 * after it, minus how many ~91-day quarters separate them. Throws if no
 * candidate fiscal year end (the prior, current, or next calendar year's)
 * lands within 366 days at or after `periodEnd` — a sign the input dates
 * are not actually a quarter-end for this filer.
 */
export function expectedFiscalQuarter(
  periodEnd: string,
  fiscalYearEndMMDD: string,
): { quarter: 1 | 2 | 3 | 4; fiscalYear: number } {
  const mm = fiscalYearEndMMDD.slice(0, 2)
  const dd = fiscalYearEndMMDD.slice(2, 4)
  const periodYear = Number(periodEnd.slice(0, 4))

  let best: { fyEnd: string; days: number } | null = null
  for (const year of [periodYear - 1, periodYear, periodYear + 1]) {
    const fyEnd = `${year}-${mm}-${dd}`
    const days = daysBetween(periodEnd, fyEnd)
    if (days < 0 || days > 366) continue
    if (!best || days < best.days) best = { fyEnd, days }
  }
  if (!best) {
    throw new Error(
      `expectedFiscalQuarter: no fiscal year end within 366 days at or after ${periodEnd} for FYE ${fiscalYearEndMMDD}`,
    )
  }

  const quartersBeforeEnd = Math.round(best.days / 91)
  const quarter = 4 - quartersBeforeEnd
  if (quarter < 1 || quarter > 4) {
    throw new Error(
      `expectedFiscalQuarter: computed out-of-range quarter ${quarter} for ${periodEnd}, FYE ${fiscalYearEndMMDD}`,
    )
  }
  return { quarter: quarter as 1 | 2 | 3 | 4, fiscalYear: Number(best.fyEnd.slice(0, 4)) }
}

/**
 * Builds one supplier's full record: the deduped/derived quarterly series
 * (most recent 8 quarters), plus YoY for the latest quarter and the one
 * before it. Throws only for a genuinely unusable input (no concept found,
 * or no quarters at all) — the caller (the refresh script) catches that and
 * records it in `failures` rather than letting one bad supplier stop the
 * run.
 */
export function buildSupplierRecord(
  id: string,
  name: string,
  cik: string,
  companyFacts: CompanyFacts,
  revenueConcepts: string[],
): SupplierRecord {
  const selected = selectRevenueFacts(companyFacts, revenueConcepts)
  if (!selected) {
    throw new Error(`no usable revenue concept found among: ${revenueConcepts.join(', ')}`)
  }
  const cikNumeric = Number.parseInt(cik, 10)
  const { quarters: allQuarters, notes } = buildQuarterSeries(selected.facts, cikNumeric)
  if (allQuarters.length === 0) {
    throw new Error(`concept ${selected.concept} present but yielded zero usable quarters`)
  }

  const last8 = allQuarters.slice(0, 8)
  const latest = last8[0] ? computeYoy(last8[0], allQuarters) : null
  const prior = last8[1] ? computeYoy(last8[1], allQuarters) : null

  return {
    id,
    name,
    cik,
    concept: selected.concept,
    quarters: last8,
    latest,
    prior,
    notes,
  }
}
