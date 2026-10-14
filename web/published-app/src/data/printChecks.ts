import { extractNumericTokens } from './issueHelpers'
import { checkPrintPeriod, type PeriodCheckResult } from './printPeriod'
import type { EvidenceRecord, VendorPrint } from './types'

/**
 * The figure-meaning check (SEC-044/SEC-045, publish-path-spec.md §4.1): for
 * every scorecard print, compare it with the evidence it cites on company or
 * segment, metric, reporting period, and units, and confirm the value shown
 * appears in that evidence. `EvidenceRecord` carries no structured metric
 * field — only free text (`excerpt`, `interpretation`) — so the metric
 * dimension is always reported 'not-checkable' rather than guessed from
 * keyword matching. Company, period, and value+units are each backed by a
 * structured or reliably-extractable field and are checked for real.
 *
 * scripts/verify-prints.ts is the only caller that turns this into a build
 * gate; this module has no side effects and no knowledge of the unverified
 * list, so it can be unit-tested with synthetic prints and evidence.
 */

export type CheckStatus = 'pass' | 'fail' | 'not-checkable'

export interface DimensionResult {
  status: CheckStatus
  reason: string
}

export interface PrintVerification {
  printId: string
  company: DimensionResult
  metric: DimensionResult
  period: DimensionResult
  value: DimensionResult
  units: DimensionResult
  /** 'fail' if any dimension failed; otherwise 'pass' (a not-checkable dimension never blocks a pass). */
  overall: 'pass' | 'fail'
}

const STOPWORDS = new Set(['the', 'inc', 'corp', 'corporation', 'llc', 'ltd', 'co', 'group', 'holdings', 'and'])

/** Lower-cased, punctuation-stripped, stopword-filtered word tokens, 3+ letters. */
function significantTokens(text: string): Set<string> {
  const words = text
    .toLowerCase()
    .split(/[^a-z0-9]+/)
    .filter((word) => word.length >= 3 && !STOPWORDS.has(word))
  return new Set(words)
}

function tokensOverlap(a: Set<string>, b: Set<string>): boolean {
  for (const token of a) {
    if (b.has(token)) return true
  }
  return false
}

/**
 * Whether the print's name (or, for a multi-name card like "Entra / Ping /
 * PE PAM", any one of its slash-separated parts) is corroborated by ANY of
 * the cited evidence's organization field, title, or excerpt. Organization
 * alone is not enough — a small acquired company's evidence is very often
 * published under the acquirer's name (see print-veza / evidence C23,
 * bylined "ServiceNow"), so title and excerpt are checked too. "Any part,
 * any evidence" is deliberately lenient: this catches a fabricated company
 * name, not a mis-split multi-vendor placeholder card.
 */
export function checkPrintCompany(print: VendorPrint, evidence: EvidenceRecord[]): DimensionResult {
  if (evidence.length === 0) {
    return { status: 'not-checkable', reason: 'no cited evidence resolved' }
  }
  const nameParts = print.name.split('/').map((part) => part.trim())
  for (const part of nameParts) {
    const partTokens = significantTokens(part)
    if (partTokens.size === 0) continue
    for (const record of evidence) {
      const evidenceText = `${record.organization} ${record.title} ${record.excerpt}`
      if (tokensOverlap(partTokens, significantTokens(evidenceText))) {
        return { status: 'pass', reason: `"${part}" corroborated by ${record.id}` }
      }
    }
  }
  return {
    status: 'fail',
    reason: `no cited evidence (organization, title, or excerpt) names "${print.name}"`,
  }
}

/** Always not-checkable: EvidenceRecord has no structured metric field to compare against. */
export function checkPrintMetric(_print: VendorPrint): DimensionResult {
  return {
    status: 'not-checkable',
    reason: 'EvidenceRecord carries no structured metric field — only free text — so the metric a print names cannot be mechanically confirmed without guessing',
  }
}

interface ParsedToken {
  raw: string
  number: number
  unit: 'PCT' | 'USD_B' | 'USD_M' | 'USD_K' | 'COUNT'
}

function parseToken(token: string): ParsedToken | null {
  const match = /^(\d[\d.]*)(B|M|K|%)?$/.exec(token)
  if (!match) return null
  const number = Number(match[1])
  if (!Number.isFinite(number)) return null
  const suffix = match[2]
  const unit: ParsedToken['unit'] = suffix === '%' ? 'PCT' : suffix === 'B' ? 'USD_B' : suffix === 'M' ? 'USD_M' : suffix === 'K' ? 'USD_K' : 'COUNT'
  return { raw: token, number, unit }
}

/** "$1.725 billion" / "300 million" / "37.7 percent" -> "$1.725B" / "300M" / "37.7%", so extractNumericTokens can find them. */
function normalizeSpelledOutMagnitudes(text: string): string {
  return text
    .replace(/([\d,.]+)\s*billion\b/gi, '$1B')
    .replace(/([\d,.]+)\s*million\b/gi, '$1M')
    .replace(/([\d,.]+)\s*thousand\b/gi, '$1K')
    .replace(/(\d[\d,.]*)\s*percent\b/gi, '$1%')
}

/** Absolute tolerance for two figures of the same unit to still count as "the same value shown". */
function withinTolerance(cardNumber: number, evidenceNumber: number, unit: ParsedToken['unit']): boolean {
  if (unit === 'PCT') return Math.abs(cardNumber - evidenceNumber) <= 1.0
  if (unit === 'COUNT') return cardNumber === evidenceNumber
  // Currency: allow the rounding a press release and a scorecard card commonly disagree by.
  const relative = Math.abs(cardNumber - evidenceNumber) / Math.max(Math.abs(evidenceNumber), 1e-9)
  return relative <= 0.02
}

/**
 * The value+units dimensions together: extracts the numeric token(s) from
 * the card's compact `value` string ("+52%", "$12B", "300+"), extracts the
 * same from every cited evidence excerpt (after expanding spelled-out
 * magnitude words so "$12 billion" is comparable to "$12B"), and looks for
 * an evidence token of the SAME unit whose magnitude matches exactly or
 * within a small, documented rounding tolerance. A card value with no
 * digits at all ("Closed", "Seed", "Split", "—") is not a numeric claim, so
 * both dimensions come back not-checkable rather than failed.
 */
export function checkPrintValueAndUnits(
  print: VendorPrint,
  evidence: EvidenceRecord[],
): { value: DimensionResult; units: DimensionResult } {
  const cardTokens = extractNumericTokens(print.value).map(parseToken).filter((t): t is ParsedToken => t !== null)
  if (cardTokens.length === 0) {
    return {
      value: { status: 'not-checkable', reason: `card value "${print.value}" contains no numeric figure to check` },
      units: { status: 'not-checkable', reason: `card value "${print.value}" contains no numeric figure to check` },
    }
  }
  if (evidence.length === 0) {
    return {
      value: { status: 'not-checkable', reason: 'no cited evidence resolved' },
      units: { status: 'not-checkable', reason: 'no cited evidence resolved' },
    }
  }

  const evidenceTokensByRecord = evidence.map((record) => ({
    record,
    tokens: extractNumericTokens(normalizeSpelledOutMagnitudes(record.excerpt))
      .map(parseToken)
      .filter((t): t is ParsedToken => t !== null),
  }))

  for (const cardToken of cardTokens) {
    for (const { record, tokens } of evidenceTokensByRecord) {
      const sameUnitMatch = tokens.find((t) => t.unit === cardToken.unit && withinTolerance(cardToken.number, t.number, t.unit))
      if (sameUnitMatch) {
        const exact = sameUnitMatch.number === cardToken.number
        return {
          value: {
            status: 'pass',
            reason: exact
              ? `"${cardToken.raw}" appears verbatim in ${record.id}`
              : `"${cardToken.raw}" matches ${record.id}'s "${sameUnitMatch.raw}" within rounding tolerance`,
          },
          units: { status: 'pass', reason: `unit ${cardToken.unit} confirmed by ${record.id}` },
        }
      }
    }
  }

  // Units mismatch, distinct from value mismatch: the magnitude appears but
  // tagged with a different unit than the card uses.
  for (const cardToken of cardTokens) {
    for (const { record, tokens } of evidenceTokensByRecord) {
      const differentUnitMatch = tokens.find((t) => t.unit !== cardToken.unit && t.number === cardToken.number)
      if (differentUnitMatch) {
        return {
          value: { status: 'fail', reason: `card value "${print.value}" not found in any cited evidence excerpt` },
          units: {
            status: 'fail',
            reason: `${record.id} states ${differentUnitMatch.raw} (unit ${differentUnitMatch.unit}), not ${cardToken.unit} as the card does`,
          },
        }
      }
    }
  }

  return {
    value: { status: 'fail', reason: `card value "${print.value}" not found in any cited evidence excerpt` },
    units: { status: 'not-checkable', reason: 'value itself did not resolve, so a unit comparison is not meaningful' },
  }
}

/** Runs all five dimensions for one print against its resolved cited evidence. */
export function verifyPrint(print: VendorPrint, evidenceById: Record<string, EvidenceRecord>): PrintVerification {
  const evidence = print.evidenceIds.map((id) => evidenceById[id]).filter((record): record is EvidenceRecord => Boolean(record))

  const company = checkPrintCompany(print, evidence)
  const metric = checkPrintMetric(print)
  const period: PeriodCheckResult = checkPrintPeriod(print.period, evidence)
  const { value, units } = checkPrintValueAndUnits(print, evidence)

  const overall: PrintVerification['overall'] = [company, metric, period, value, units].some(
    (dimension) => dimension.status === 'fail',
  )
    ? 'fail'
    : 'pass'

  return { printId: print.id, company, metric, period, value, units, overall }
}

export function verifyAllPrints(prints: VendorPrint[], evidenceById: Record<string, EvidenceRecord>): PrintVerification[] {
  return prints.map((print) => verifyPrint(print, evidenceById))
}
