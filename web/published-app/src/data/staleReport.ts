import { daysBetween, derivePeriodEndDate } from './printPeriod'
import {
  type ClaimKind,
  collectJudgedClaimRefs,
  effectiveDate,
  effectiveJudgment,
} from './reconfirmationHelpers'
import type { EvidenceRecord, Hypothesis, PressureRow, Reconfirmation, SecurityDomain, VendorPrint } from './types'

/**
 * Builds the "Going stale" report (publish-path-spec.md §4.2): every judged
 * claim (a domain stance, a Platform-pressure row, a tracked hypothesis)
 * whose EFFECTIVE judged date — the newest reconfirmation, if any, else the
 * original judgment (SEC-MARKET-PUBLISH-001 §4.3) — is older than 45 days,
 * and every scorecard print whose period ended more than 150 days ago,
 * oldest first. Pure and side-effect free so it can be unit-tested directly
 * (tests/stale-report.test.ts); scripts/stale-report.ts is the thin CLI
 * wrapper that calls this with the real data and today's date (or
 * `--as-of`), in either Markdown (default) or `--json`.
 */

const JUDGED_STALE_AFTER_DAYS = 45
const PRINT_STALE_AFTER_DAYS = 150

interface JudgedClaim {
  kind: ClaimKind
  id: string
  claimId: string
  text: string
  judgedOn: string
  reconfirmedOn: string | null
  ageDays: number
}

interface StalePrint {
  id: string
  text: string
  periodEnd: string
  ageDays: number
}

interface UnparseablePrint {
  id: string
  text: string
  period: string
}

export interface StaleReportInputs {
  domains: SecurityDomain[]
  hypotheses: Hypothesis[]
  pressureRows: PressureRow[]
  prints: VendorPrint[]
  evidenceById: Record<string, EvidenceRecord>
  /** Defaults to the real, on-disk reconfirmations. Overridable for tests. */
  reconfirmations?: Reconfirmation[]
}

function collectJudgedClaims(inputs: StaleReportInputs, asOf: string): JudgedClaim[] {
  const reconfirmations = inputs.reconfirmations ?? []
  return collectJudgedClaimRefs(inputs).map((ref) => {
    const effective = effectiveJudgment(ref.claimId, ref.judgedOn, reconfirmations)
    const asOfDate = effectiveDate(effective)
    return {
      kind: ref.kind,
      id: ref.id,
      claimId: ref.claimId,
      text: ref.text,
      judgedOn: ref.judgedOn,
      reconfirmedOn: effective.reconfirmedOn,
      ageDays: daysBetween(asOfDate, asOf),
    }
  })
}

function collectScorecardAges(
  inputs: StaleReportInputs,
  asOf: string,
): { stale: StalePrint[]; unparseable: UnparseablePrint[] } {
  const stale: StalePrint[] = []
  const unparseable: UnparseablePrint[] = []

  for (const print of inputs.prints) {
    const evidence = print.evidenceIds.map((id) => inputs.evidenceById[id]).filter((r): r is EvidenceRecord => Boolean(r))
    const periodEnd = derivePeriodEndDate(print.period, evidence)
    if (periodEnd === null) {
      unparseable.push({ id: print.id, text: `${print.name} — ${print.metric} (${print.value})`, period: print.period })
      continue
    }
    const ageDays = daysBetween(periodEnd, asOf)
    if (ageDays > PRINT_STALE_AFTER_DAYS) {
      stale.push({ id: print.id, text: `${print.name} — ${print.metric} (${print.value})`, periodEnd, ageDays })
    }
  }

  return { stale, unparseable }
}

export function buildStaleReport(asOf: string, inputs: StaleReportInputs): string {
  const judgedClaims = collectJudgedClaims(inputs, asOf)
    .filter((claim) => claim.ageDays > JUDGED_STALE_AFTER_DAYS)
    .sort((a, b) => b.ageDays - a.ageDays)

  const { stale: staleScorecard, unparseable } = collectScorecardAges(inputs, asOf)
  staleScorecard.sort((a, b) => b.ageDays - a.ageDays)

  const lines: string[] = []
  lines.push('# Going stale')
  lines.push('')
  lines.push(
    `As of ${asOf}: ${judgedClaims.length} judged claim(s) older than ${JUDGED_STALE_AFTER_DAYS} days, ` +
      `${staleScorecard.length} scorecard print(s) whose period ended more than ${PRINT_STALE_AFTER_DAYS} days ago, ` +
      `${unparseable.length} print(s) with a period not understood.`,
  )
  lines.push('')

  lines.push('## Judged claims older than 45 days')
  lines.push('')
  if (judgedClaims.length === 0) {
    lines.push('None found.')
  } else {
    for (const claim of judgedClaims) {
      const reconfirmedNote = claim.reconfirmedOn ? `, reconfirmed ${claim.reconfirmedOn}` : ''
      lines.push(
        `- \`${claim.id}\` (${claim.kind}) — ${claim.text} — judged ${claim.judgedOn}${reconfirmedNote}, ${claim.ageDays} days ago`,
      )
    }
  }
  lines.push('')

  lines.push('## Scorecard periods more than 150 days old')
  lines.push('')
  if (staleScorecard.length === 0) {
    lines.push('None found.')
  } else {
    for (const print of staleScorecard) {
      lines.push(`- \`${print.id}\` — ${print.text} — period ended ${print.periodEnd}, ${print.ageDays} days ago`)
    }
  }
  if (unparseable.length > 0) {
    lines.push('')
    lines.push('### Period not understood')
    lines.push('')
    for (const print of unparseable) {
      lines.push(`- \`${print.id}\` — ${print.text} — period "${print.period}" not understood by the parser`)
    }
  }
  lines.push('')

  return lines.join('\n')
}

export interface StaleReportJson {
  asOf: string
  staleClaimIds: string[]
}

/**
 * The machine-readable form of the same "older than 45 days by effective
 * date" judgment the Markdown report renders (publish-path-spec.md §4.3):
 * just the claim ids, in `${kind}:${id}` form, so the sign step's
 * `reconfirm` logic (scripts/reconfirmLogic.ts) can consume it without
 * re-implementing the staleness rule or scraping Markdown. `scripts/
 * stale-report.ts --json` prints this to stdout.
 */
export function buildStaleReportJson(asOf: string, inputs: StaleReportInputs): StaleReportJson {
  const staleClaimIds = collectJudgedClaims(inputs, asOf)
    .filter((claim) => claim.ageDays > JUDGED_STALE_AFTER_DAYS)
    .map((claim) => claim.claimId)
  return { asOf, staleClaimIds }
}
