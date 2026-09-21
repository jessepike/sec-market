import type { Reconfirmation } from '../src/data/types.ts'

/**
 * Decides which stale, unchallenged claims get re-dated under the owner's
 * name when he signs `reconfirm` (SEC-MARKET-PUBLISH-001 §4.3, coordinator
 * task T7-4). Pure: takes the stale-claim-id list `scripts/stale-report.ts
 * --json` already computed (which already accounts for a prior
 * reconfirmation through `effectiveJudgment` — a claim reconfirmed inside
 * the last 45 days is not in that list at all) and the current issue's
 * `proposed.challengedClaimIds`, and decides, per claim, whether it gets a
 * new entry. Never inspects `judgedOn` or ages anything itself — that
 * computation lives once, in `src/data/staleReport.ts`, so this module and
 * the "Going stale" report can never disagree about what counts as stale.
 */

export interface ComputeReconfirmationsOptions {
  /** Whether the owner's approval carried the word `reconfirm`. False does nothing at all. */
  reconfirm: boolean
  /** The approval's date, in `YYYY-MM-DD` — same value passed to sign-issue.ts's `--signed-on`. */
  signedOn: string
  /** The issue whose approval carries the reconfirmation (`Reconfirmation.via`). */
  issueId: string
  /** Must equal AUTHOR_NAME in meta.ts. */
  authorName: string
  /** `MachineProposal.challengedClaimIds` from the draft being signed, read before `proposed` is nulled. */
  challengedClaimIds: string[]
  /** `buildStaleReportJson(signedOn, ...).staleClaimIds` — every claim stale as of the signing date, by effective date. */
  staleClaimIds: string[]
  /** The reconfirmations already on record; never mutated, never removed from. */
  existingReconfirmations: Reconfirmation[]
}

export interface ComputeReconfirmationsResult {
  /** `existingReconfirmations` plus `added`, append-only, in that order. Write this to reconfirmations.ts. */
  reconfirmations: Reconfirmation[]
  /** The new entries this run adds, if any. */
  added: Reconfirmation[]
  /** Stale claim ids left un-reconfirmed because this week's evidence challenges them — needs a human session. */
  challengedLeftStale: string[]
}

export function computeReconfirmations(options: ComputeReconfirmationsOptions): ComputeReconfirmationsResult {
  if (!options.reconfirm) {
    return { reconfirmations: options.existingReconfirmations, added: [], challengedLeftStale: [] }
  }

  const challenged = new Set(options.challengedClaimIds)
  const added: Reconfirmation[] = []
  const challengedLeftStale: string[] = []

  for (const claimId of options.staleClaimIds) {
    if (challenged.has(claimId)) {
      challengedLeftStale.push(claimId)
      continue
    }
    added.push({ claimId, reconfirmedOn: options.signedOn, by: options.authorName, via: options.issueId })
  }

  return { reconfirmations: [...options.existingReconfirmations, ...added], added, challengedLeftStale }
}
