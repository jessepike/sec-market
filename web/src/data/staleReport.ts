import { daysBetween, derivePeriodEndDate } from './printPeriod'
import type { EvidenceRecord, Hypothesis, PressureRow, SecurityDomain, VendorPrint } from './types'

/**
 * Builds the "Going stale" report (publish-path-spec.md §4.2): every judged
 * claim (a domain stance, a Platform-pressure row, a tracked hypothesis)
 * whose judged date is older than 45 days, and every scorecard print whose
 * period ended more than 150 days ago, oldest first. Pure and side-effect
 * free so it can be unit-tested directly (tests/stale-report.test.ts);
 * scripts/stale-report.ts is the thin CLI wrapper that calls this with the
 * real data and today's date (or `--as-of`).
 */

const JUDGED_STALE_AFTER_DAYS = 45
const PRINT_STALE_AFTER_DAYS = 150

interface JudgedClaim {
  kind: 'domain' | 'hypothesis' | 'platform-pressure'
  id: string
  text: string
  judgedOn: string
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
}

function collectJudgedClaims(inputs: StaleReportInputs, asOf: string): JudgedClaim[] {
  const claims: JudgedClaim[] = []

  for (const domain of inputs.domains) {
    claims.push({
      kind: 'domain',
      id: domain.id,
      text: `${domain.name}: ${domain.why}`,
      judgedOn: domain.asOf,
      ageDays: daysBetween(domain.asOf, asOf),
    })
  }

  for (const hypothesis of inputs.hypotheses) {
    claims.push({
      kind: 'hypothesis',
      id: hypothesis.id,
      text: hypothesis.claim,
      judgedOn: hypothesis.provenance.judgedOn,
      ageDays: daysBetween(hypothesis.provenance.judgedOn, asOf),
    })
  }

  for (const row of inputs.pressureRows) {
    if (row.provenance.read.layer !== 'judged') continue
    claims.push({
      kind: 'platform-pressure',
      id: row.id,
      text: row.read,
      judgedOn: row.provenance.read.judgedOn,
      ageDays: daysBetween(row.provenance.read.judgedOn, asOf),
    })
  }

  return claims
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
      lines.push(`- \`${claim.id}\` (${claim.kind}) — ${claim.text} — judged ${claim.judgedOn}, ${claim.ageDays} days ago`)
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
