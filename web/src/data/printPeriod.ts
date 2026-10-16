import type { EvidenceRecord } from './types'

/**
 * Parses the two period vocabularies this site actually uses — the compact
 * tag on a scorecard print (`prints.ts`'s `period` field: "JUN '26", "FY26",
 * "Q3 FY26", "2025", "Closed", "No series") and the free-text
 * `EvidenceRecord.economicPeriod` a print cites ("Quarter ended
 * 2026-06-30", "Fiscal year ended 2026-01-31", "FY2026 and quarter ended
 * 2026-07-25", "Series G close") — into a small set of comparable shapes.
 *
 * Both scripts/verify-prints.ts (does the card's period agree with its
 * evidence?) and, until 2026-10-16, the retired stale-report script (how old is this print's period?)
 * read through this module rather than parsing period strings themselves, so
 * the two cannot silently disagree about what a period string means.
 */

/** What a scorecard card's compact `period` tag says, mechanically. */
export type CardPeriodKind =
  | 'month-year' // "JUN '26" — a specific calendar month
  | 'fiscal-year' // "FY26" / "FY2026" — a bare fiscal year, no quarter marker
  | 'calendar-year' // "2025" — a bare four-digit year
  | 'quarter' // "Q3 FY26" — an explicit fiscal quarter
  | 'non-comparable' // "Closed" / "No series" — no period is being claimed
  | 'unknown' // does not match any pattern this parser recognises

export interface CardPeriodInfo {
  kind: CardPeriodKind
  /** 1–12, only for 'month-year'. */
  month?: number
  /** Four-digit year, when the tag names one directly. */
  year?: number
}

const MONTH_ABBREVIATIONS = [
  'JAN',
  'FEB',
  'MAR',
  'APR',
  'MAY',
  'JUN',
  'JUL',
  'AUG',
  'SEP',
  'OCT',
  'NOV',
  'DEC',
] as const

/** Matches "JUN '26", "JUN’26", "JUN 26" — a straight or curly apostrophe, optional space. */
const MONTH_YEAR_PATTERN = /^([A-Za-z]{3})\.?\s*['’]?\s*(\d{2})$/
const FISCAL_YEAR_PATTERN = /^FY\s?(\d{2}|\d{4})$/i
const CALENDAR_YEAR_PATTERN = /^(\d{4})$/
const QUARTER_FY_PATTERN = /^Q([1-4])\s*FY\s?(\d{2}|\d{4})$/i
const NON_COMPARABLE_VALUES = new Set(['closed', 'no series'])

/** "26" -> 2026, "2026" -> 2026. This site's cards only ever name years in the 2000s. */
function twoOrFourDigitYear(raw: string): number {
  return raw.length === 2 ? 2000 + Number(raw) : Number(raw)
}

export function classifyCardPeriod(period: string): CardPeriodInfo {
  const trimmed = period.trim()
  const lower = trimmed.toLowerCase()

  if (NON_COMPARABLE_VALUES.has(lower)) return { kind: 'non-comparable' }

  const monthYear = MONTH_YEAR_PATTERN.exec(trimmed)
  if (monthYear) {
    const monthIndex = MONTH_ABBREVIATIONS.indexOf(monthYear[1].toUpperCase() as (typeof MONTH_ABBREVIATIONS)[number])
    if (monthIndex !== -1) {
      return { kind: 'month-year', month: monthIndex + 1, year: twoOrFourDigitYear(monthYear[2]) }
    }
  }

  const quarterFy = QUARTER_FY_PATTERN.exec(trimmed)
  if (quarterFy) {
    return { kind: 'quarter', year: twoOrFourDigitYear(quarterFy[2]) }
  }

  const fiscalYear = FISCAL_YEAR_PATTERN.exec(trimmed)
  if (fiscalYear) {
    return { kind: 'fiscal-year', year: twoOrFourDigitYear(fiscalYear[1]) }
  }

  const calendarYear = CALENDAR_YEAR_PATTERN.exec(trimmed)
  if (calendarYear) {
    return { kind: 'calendar-year', year: Number(calendarYear[1]) }
  }

  return { kind: 'unknown' }
}

/** What one cited evidence record's `economicPeriod` free text says, mechanically. */
export type EvidencePeriodKind =
  | 'quarter' // "Quarter ended 2026-06-30" — a single fiscal quarter, nothing wider
  | 'fiscal-year' // "Fiscal year ended 2026-01-31" — a full fiscal year
  | 'calendar-year' // "Calendar year 2025"
  | 'combined' // "FY2026 and quarter ended 2026-07-25" — names both a year and a quarter
  | 'point' // a dated event: a close, a round, an agreement — not a reporting period
  | 'unknown' // free text this parser cannot place into a period shape

export interface EvidencePeriodInfo {
  kind: EvidencePeriodKind
  /** ISO end date, only when the text states one explicitly ("... ended YYYY-MM-DD"). */
  endDate?: string
  /** Four-digit year(s) findable anywhere in the economicPeriod text. */
  years: number[]
}

const QUARTER_ENDED_PATTERN = /quarter ended (\d{4}-\d{2}-\d{2})/i
const FISCAL_YEAR_ENDED_PATTERN = /fiscal year ended (\d{4}-\d{2}-\d{2})/i
const CALENDAR_YEAR_TEXT_PATTERN = /calendar year (\d{4})/i
const FY_TOKEN_PATTERN = /\bFY\s?(\d{2}|\d{4})\b/i
const POINT_EVENT_PATTERN =
  /\b(series|close|closed|clos(e|ing)|acqui\w*|agreement|round|transaction|deregistr\w*|strategic|valuation|raise)\b/i
const YEAR_TOKEN_PATTERN = /\b(19|20)\d{2}\b/g

function yearsIn(text: string): number[] {
  return [...text.matchAll(YEAR_TOKEN_PATTERN)].map((match) => Number(match[0]))
}

export function classifyEvidencePeriod(economicPeriod: string): EvidencePeriodInfo {
  const text = economicPeriod.trim()
  const years = yearsIn(text)
  const hasFyToken = FY_TOKEN_PATTERN.test(text)
  const quarterEnded = QUARTER_ENDED_PATTERN.exec(text)

  if (quarterEnded && hasFyToken) {
    return { kind: 'combined', endDate: quarterEnded[1], years }
  }
  if (quarterEnded) {
    return { kind: 'quarter', endDate: quarterEnded[1], years }
  }
  if (/^Q[1-4]\s*FY\s?\d{2,4}/i.test(text)) {
    return { kind: 'quarter', years }
  }

  const fiscalYearEnded = FISCAL_YEAR_ENDED_PATTERN.exec(text)
  if (fiscalYearEnded) {
    return { kind: 'fiscal-year', endDate: fiscalYearEnded[1], years }
  }

  const calendarYearText = CALENDAR_YEAR_TEXT_PATTERN.exec(text)
  if (calendarYearText) {
    return { kind: 'calendar-year', years: [Number(calendarYearText[1])] }
  }
  if (/^\d{4}$/.test(text)) {
    return { kind: 'calendar-year', years: [Number(text)] }
  }

  if (POINT_EVENT_PATTERN.test(text)) {
    return { kind: 'point', years }
  }

  return { kind: 'unknown', years }
}

export interface PeriodCheckResult {
  status: 'pass' | 'fail' | 'not-checkable'
  reason: string
}

/**
 * A month name (full, not abbreviated) and a four-digit year both appearing
 * somewhere in a piece of text — used only as a fallback corroboration for
 * point-in-time evidence whose structured `publicationDate` names an
 * announcement date rather than the later date (e.g. a deal's close) the
 * card's period tag actually names. Text presence, not inference: if the
 * excerpt says "closed on March 2, 2026" this finds "March" and "2026".
 */
const FULL_MONTH_NAMES = [
  'January',
  'February',
  'March',
  'April',
  'May',
  'June',
  'July',
  'August',
  'September',
  'October',
  'November',
  'December',
]

function textNamesMonthAndYear(text: string, month: number, year: number): boolean {
  const monthName = FULL_MONTH_NAMES[month - 1]
  return text.includes(monthName) && text.includes(String(year))
}

/**
 * Compares one print's card-period tag against the evidence it cites.
 * Returns 'fail' only for a mismatch this parser can state with confidence —
 * most notably a bare fiscal/calendar year label over evidence that names a
 * single quarter and nothing wider, the exact mistake SEC-043 corrected on
 * an issue headline. Everything the parser cannot place confidently comes
 * back 'not-checkable' rather than a guessed pass or fail.
 */
export function checkPrintPeriod(cardPeriod: string, evidence: EvidenceRecord[]): PeriodCheckResult {
  const card = classifyCardPeriod(cardPeriod)

  if (card.kind === 'non-comparable') {
    return { status: 'not-checkable', reason: `card period "${cardPeriod}" names no comparable span to check` }
  }
  if (evidence.length === 0) {
    return { status: 'not-checkable', reason: 'no cited evidence resolved' }
  }

  const evidenceInfos = evidence.map((record) => ({ record, info: classifyEvidencePeriod(record.economicPeriod) }))

  if (card.kind === 'fiscal-year' || card.kind === 'calendar-year') {
    // A card claiming a full year is checked against every citation; if ANY
    // citation is a bare quarter (no year marker at all), that is the
    // fiscal-year-over-a-quarter mistake and it fails outright regardless of
    // what the other citations say.
    const quarterOnly = evidenceInfos.find(({ info }) => info.kind === 'quarter')
    if (quarterOnly && !evidenceInfos.some(({ info }) => info.kind === 'fiscal-year' || info.kind === 'calendar-year' || info.kind === 'combined')) {
      return {
        status: 'fail',
        reason:
          `card period "${cardPeriod}" labels a full year, but its only period evidence ` +
          `("${quarterOnly.record.id}": economicPeriod "${quarterOnly.record.economicPeriod}") is a single quarter`,
      }
    }
    const yearMatch = evidenceInfos.find(
      ({ info }) => info.kind !== 'quarter' && info.kind !== 'unknown' && card.year !== undefined && info.years.includes(card.year),
    )
    if (yearMatch) return { status: 'pass', reason: `matches ${yearMatch.record.id}` }

    // Fallback for a bare year whose evidence is dated (funding rounds,
    // point events) rather than itself period-shaped: does any cited
    // record's economicPeriod text or publicationDate name that year at all?
    if (card.year !== undefined) {
      const anyYearMatch = evidence.find(
        (record) => yearsIn(record.economicPeriod).includes(card.year!) || record.publicationDate.startsWith(String(card.year)),
      )
      if (anyYearMatch) return { status: 'pass', reason: `matches ${anyYearMatch.id}` }
    }
    return {
      status: 'fail',
      reason: `card period "${cardPeriod}" names year ${card.year}, not found in any cited evidence's economicPeriod or publicationDate`,
    }
  }

  if (card.kind === 'quarter') {
    const quarterOrCombined = evidenceInfos.find(({ info }) => info.kind === 'quarter' || info.kind === 'combined')
    if (quarterOrCombined) {
      if (card.year !== undefined && quarterOrCombined.info.years.length > 0 && !quarterOrCombined.info.years.includes(card.year)) {
        return {
          status: 'fail',
          reason: `card period "${cardPeriod}" names FY${card.year}, but ${quarterOrCombined.record.id} names ${quarterOrCombined.info.years.join('/')}`,
        }
      }
      return { status: 'pass', reason: `matches ${quarterOrCombined.record.id}` }
    }
    return { status: 'not-checkable', reason: 'no cited evidence states a quarter or combined period to compare against' }
  }

  if (card.kind === 'month-year') {
    for (const { record, info } of evidenceInfos) {
      if (info.endDate) {
        const [, endMonth] = info.endDate.split('-')
        if (Number(endMonth) === card.month && info.endDate.startsWith(String(card.year))) {
          return { status: 'pass', reason: `matches ${record.id}'s economicPeriod end date ${info.endDate}` }
        }
      }
      if (info.kind === 'fiscal-year' || info.kind === 'calendar-year' || info.kind === 'combined') {
        if (card.year !== undefined && info.years.includes(card.year)) {
          return { status: 'pass', reason: `year matches ${record.id} (month not separately checkable within a year record)` }
        }
      }
      // Point-in-time evidence: try the record's own publicationDate month/year first.
      const [pubYear, pubMonth] = record.publicationDate.split('-')
      if (Number(pubMonth) === card.month && Number(pubYear) === card.year) {
        return { status: 'pass', reason: `matches ${record.id}'s publicationDate ${record.publicationDate}` }
      }
      // Fall back to a textual date named in the excerpt or title, for a
      // record whose publicationDate is an earlier stage (an intent or
      // announcement) than the date the card's period tag actually names
      // (e.g. a later close).
      if (card.month !== undefined && card.year !== undefined) {
        const combinedText = `${record.title} ${record.excerpt}`
        if (textNamesMonthAndYear(combinedText, card.month, card.year)) {
          return { status: 'pass', reason: `${record.id}'s title/excerpt names that month and year in text` }
        }
      }
    }
    return {
      status: 'fail',
      reason: `card period "${cardPeriod}" does not match any cited evidence's economicPeriod, publicationDate, or dated text`,
    }
  }

  return { status: 'not-checkable', reason: `card period "${cardPeriod}" does not match a recognised pattern` }
}

// --- Period end-date derivation (written for the retired stale-report script) ---------

const LAST_DAY_OF_MONTH = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

function isoDate(year: number, month: number, day: number): string {
  return `${String(year).padStart(4, '0')}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`
}

function isLeapYear(year: number): boolean {
  return (year % 4 === 0 && year % 100 !== 0) || year % 400 === 0
}

function lastDayOfMonthIso(year: number, month: number): string {
  const day = month === 2 && isLeapYear(year) ? 29 : LAST_DAY_OF_MONTH[month - 1]
  return isoDate(year, month, day)
}

/**
 * The best mechanically-derivable end date for a scorecard print's period,
 * for staleness measurement only (the retired stale-report script) — never used by
 * the figure-meaning check, which compares kinds and years rather than
 * needing one exact date.
 *
 * Priority: a month-year card tag ("JUN '26") or a bare year ("2025") names
 * its own end date directly, with no evidence needed. Every other shape —
 * "FY26", "Q3 FY26", "Closed", "No series" — carries no month in the card
 * text itself, so this falls back to the newest (latest) `publicationDate`
 * among the print's cited evidence, on the honest theory that the most
 * recently published document we hold about this print is the closest
 * anchor available. Returns null (unparseable) only when the card names no
 * date-shaped period AND no cited evidence resolves at all.
 */
export function derivePeriodEndDate(cardPeriod: string, evidence: EvidenceRecord[]): string | null {
  const card = classifyCardPeriod(cardPeriod)

  if (card.kind === 'month-year' && card.month !== undefined && card.year !== undefined) {
    return lastDayOfMonthIso(card.year, card.month)
  }
  if (card.kind === 'calendar-year' && card.year !== undefined) {
    return isoDate(card.year, 12, 31)
  }

  if (evidence.length === 0) return null
  const newest = evidence.reduce((latest, record) =>
    record.publicationDate > latest.publicationDate ? record : latest,
  )
  return newest.publicationDate
}

function isoDateToUtcMs(iso: string): number {
  const [year, month, day] = iso.split('-').map(Number)
  return Date.UTC(year, month - 1, day)
}

/** Whole calendar days between two ISO dates (`to` minus `from`), UTC. */
export function daysBetween(from: string, to: string): number {
  return Math.round((isoDateToUtcMs(to) - isoDateToUtcMs(from)) / 86_400_000)
}
