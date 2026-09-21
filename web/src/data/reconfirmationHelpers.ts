import { daysBetween } from './printPeriod'
import type { Hypothesis, Issue, PressureRow, Reconfirmation, SecurityDomain } from './types'

/**
 * The three kinds of judged claim a reconfirmation can re-date
 * (SEC-MARKET-PUBLISH-001 §4.2/§4.3): a domain stance, a tracked hypothesis,
 * or a Platform-pressure row's judged read. Matches staleReport.ts's own
 * notion of "judged claim" exactly — both modules read through
 * `collectJudgedClaimRefs` below so they cannot drift on what counts as one.
 */
export type ClaimKind = 'domain' | 'hypothesis' | 'platform-pressure'

/**
 * A judged claim's id, for reconfirmations.ts and the stale report:
 * `${kind}:${id}`, where `id` is the claim's own existing stable id
 * (`SecurityDomain.id`, `Hypothesis.id`, or `PressureRow.id` — all three
 * already carry one, used elsewhere as a React key and in the edition
 * delta). The `kind` prefix guards against an accidental collision across
 * those three id spaces, which does not happen today but is not guaranteed
 * by construction (a domain id and a hypothesis id are free-form strings
 * from two different arrays).
 */
export function claimId(kind: ClaimKind, id: string): string {
  return `${kind}:${id}`
}

export interface JudgedClaimRef {
  kind: ClaimKind
  id: string
  claimId: string
  text: string
  judgedOn: string
}

export interface ClaimSources {
  domains: SecurityDomain[]
  hypotheses: Hypothesis[]
  pressureRows: PressureRow[]
}

/**
 * Every judged claim on the site today, each with its own original judged
 * date. A Platform-pressure row whose `read` provenance is `'tracked'`
 * (there is no such row today, but the type allows it) carries no judgment
 * to reconfirm and is excluded, exactly as staleReport.ts already excluded
 * it.
 */
export function collectJudgedClaimRefs(inputs: ClaimSources): JudgedClaimRef[] {
  const claims: JudgedClaimRef[] = []

  for (const domain of inputs.domains) {
    claims.push({
      kind: 'domain',
      id: domain.id,
      claimId: claimId('domain', domain.id),
      text: `${domain.name}: ${domain.why}`,
      judgedOn: domain.asOf,
    })
  }

  for (const hypothesis of inputs.hypotheses) {
    claims.push({
      kind: 'hypothesis',
      id: hypothesis.id,
      claimId: claimId('hypothesis', hypothesis.id),
      text: hypothesis.claim,
      judgedOn: hypothesis.provenance.judgedOn,
    })
  }

  for (const row of inputs.pressureRows) {
    if (row.provenance.read.layer !== 'judged') continue
    claims.push({
      kind: 'platform-pressure',
      id: row.id,
      claimId: claimId('platform-pressure', row.id),
      text: row.read,
      judgedOn: row.provenance.read.judgedOn,
    })
  }

  return claims
}

export interface EffectiveJudgment {
  /** The claim's original judged date. Never changed by a reconfirmation. */
  judgedOn: string
  /** The newest reconfirmation's date, or null if the claim has never been reconfirmed. */
  reconfirmedOn: string | null
  reconfirmedBy: string | null
  reconfirmedVia: string | null
}

/**
 * A claim's original judgment plus the newest reconfirmation for it, if any.
 * Pure — takes the reconfirmations list explicitly rather than importing the
 * singleton, so callers (the sign step, tests) can pass a candidate list
 * that has not been written to disk yet.
 */
export function effectiveJudgment(
  claimIdValue: string,
  judgedOn: string,
  reconfirmations: Reconfirmation[],
): EffectiveJudgment {
  const matches = reconfirmations.filter((entry) => entry.claimId === claimIdValue)
  if (matches.length === 0) {
    return { judgedOn, reconfirmedOn: null, reconfirmedBy: null, reconfirmedVia: null }
  }
  const latest = matches.reduce((a, b) => (b.reconfirmedOn > a.reconfirmedOn ? b : a))
  return { judgedOn, reconfirmedOn: latest.reconfirmedOn, reconfirmedBy: latest.by, reconfirmedVia: latest.via }
}

/** The date staleness and display should treat as "last judged": the newest reconfirmation, or the original judged date. */
export function effectiveDate(effective: EffectiveJudgment): string {
  return effective.reconfirmedOn ?? effective.judgedOn
}

/** True when a claim's effective date is more than `staleAfterDays` before `asOf`. Mirrors staleReport.ts's own threshold (45 days). */
export function isStaleAsOf(effective: EffectiveJudgment, asOf: string, staleAfterDays: number): boolean {
  return daysBetween(effectiveDate(effective), asOf) > staleAfterDays
}

export interface ReconfirmationViolation {
  index: number
  claimId: string
  reason: string
}

/**
 * Checks every entry in `reconfirmations` against the rules
 * SEC-MARKET-PUBLISH-001 §4.3 sets for re-dating a judgment under the
 * owner's name (used by scripts/verify-issue.ts's reconfirmations check):
 *
 * - `claimId` names a real judged claim
 * - `by` equals `authorName`
 * - `reconfirmedOn` is a valid calendar date, not earlier than the claim's
 *   own original `judgedOn`, and not later than `newestPublishedSignedOn`
 *   plus one day (there is no published issue yet to have carried a later
 *   approval)
 * - `via` names a published issue
 *
 * Pure and side-effect free so it can be unit-tested directly
 * (tests/reconfirmations.test.ts) without importing the real data module.
 */
export function validateReconfirmations(
  reconfirmations: Reconfirmation[],
  claims: JudgedClaimRef[],
  authorName: string,
  publishedIssueIds: Set<string>,
  newestPublishedSignedOn: string | null,
): ReconfirmationViolation[] {
  const claimById = new Map(claims.map((claim) => [claim.claimId, claim]))
  const violations: ReconfirmationViolation[] = []
  const isoDatePattern = /^\d{4}-\d{2}-\d{2}$/

  reconfirmations.forEach((entry, index) => {
    const claim = claimById.get(entry.claimId)
    if (!claim) {
      violations.push({ index, claimId: entry.claimId, reason: `no judged claim has id "${entry.claimId}"` })
      return
    }
    if (entry.by !== authorName) {
      violations.push({
        index,
        claimId: entry.claimId,
        reason: `"by" is "${entry.by}", not AUTHOR_NAME "${authorName}"`,
      })
    }
    if (!isoDatePattern.test(entry.reconfirmedOn)) {
      violations.push({
        index,
        claimId: entry.claimId,
        reason: `"reconfirmedOn" "${entry.reconfirmedOn}" is not a ^\\d{4}-\\d{2}-\\d{2}$ date`,
      })
    } else {
      if (entry.reconfirmedOn < claim.judgedOn) {
        violations.push({
          index,
          claimId: entry.claimId,
          reason: `"reconfirmedOn" ${entry.reconfirmedOn} is earlier than the claim's judgedOn ${claim.judgedOn}`,
        })
      }
      if (newestPublishedSignedOn === null) {
        violations.push({
          index,
          claimId: entry.claimId,
          reason: 'no published issue exists yet, so no reconfirmedOn can be valid',
        })
      } else {
        const latestAllowed = daysBetween(newestPublishedSignedOn, entry.reconfirmedOn)
        if (latestAllowed > 1) {
          violations.push({
            index,
            claimId: entry.claimId,
            reason: `"reconfirmedOn" ${entry.reconfirmedOn} is more than one day after the newest published issue's signedOn ${newestPublishedSignedOn}`,
          })
        }
      }
    }
    if (!publishedIssueIds.has(entry.via)) {
      violations.push({
        index,
        claimId: entry.claimId,
        reason: `"via" "${entry.via}" is not a published issue id`,
      })
    }
  })

  return violations
}

/** Every id in `ids` that does not name a real judged claim — used to validate `MachineProposal.challengedClaimIds` on a draft. */
export function unknownClaimIds(ids: string[], claims: JudgedClaimRef[]): string[] {
  const known = new Set(claims.map((claim) => claim.claimId))
  return ids.filter((id) => !known.has(id))
}

/** Convenience for verify-issue.ts: the newest `signedOn` among published issues, or null if there are none. */
export function newestPublishedSignedOn(issues: Issue[]): string | null {
  let newest: string | null = null
  for (const issue of issues) {
    if (issue.status !== 'published' || !issue.weThink.signedOn) continue
    if (newest === null || issue.weThink.signedOn > newest) newest = issue.weThink.signedOn
  }
  return newest
}
