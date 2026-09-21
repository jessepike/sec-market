import type { Issue, MachineProposal } from '../src/data/types.ts'

/**
 * True iff `value` matches `^\d{4}-\d{2}-\d{2}$` and names a real calendar
 * date. Duplicated from verify-issue.ts's private copy rather than imported
 * from it: that module runs its whole check suite as a side effect of being
 * loaded, so importing it just for this one pure function would run the
 * wrong program.
 */
export function isValidIsoDate(value: string): boolean {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) return false
  const [year, month, day] = value.split('-').map(Number)
  const date = new Date(Date.UTC(year, month - 1, day))
  return (
    date.getUTCFullYear() === year && date.getUTCMonth() === month - 1 && date.getUTCDate() === day
  )
}

/** A proposal with no substantive read or summary is refused rather than signed. */
export function isProposedEmpty(proposed: MachineProposal | null): boolean {
  return !proposed || proposed.read.trim() === '' || proposed.summary.trim() === ''
}

/**
 * Thrown by `findDraftToSign` specifically when `--id` names an issue that
 * exists but is already published (SEC-MARKET-PUBLISH-001, coordinator
 * review point L, 2026-09-21). This is not a broken state — it means the
 * approval arrived for an issue someone (or some earlier, retried run)
 * already signed — so the CLI shell treats it as a distinct, benign outcome
 * (exit code 2) rather than the generic failure every other refusal here is.
 */
export class AlreadyPublishedError extends Error {}

/**
 * Picks the one draft issue to sign, refusing on every unsafe state
 * (SEC-MARKET-PUBLISH-001 §2.2):
 * - `id` given but no issue carries it
 * - `id` given but that issue is not a draft (already signed/published) —
 *   throws `AlreadyPublishedError`, handled as a benign no-op by the CLI
 * - no draft issue at all
 * - more than one draft issue, even if `id` would otherwise disambiguate —
 *   more than one draft existing at all means the trunk is in a state
 *   `verify:issue` check 6 should already have refused, so this refuses too
 *   rather than guessing which one the approval was for
 * - `id` given but does not match the one draft found
 * - the draft is inconsistently marked (carries signed fields despite
 *   `status: 'draft'`)
 * - the draft's `proposed` is null or has no substantive content
 */
export function findDraftToSign(issues: Issue[], id: string | null): Issue {
  if (id !== null) {
    const target = issues.find((issue) => issue.id === id)
    if (!target) {
      throw new Error(`sign-issue: no issue with id "${id}" found`)
    }
    if (target.status !== 'draft') {
      throw new AlreadyPublishedError(`sign-issue: issue "${id}" is already signed (status "${target.status}")`)
    }
  }

  const drafts = issues.filter((issue) => issue.status === 'draft')
  if (drafts.length === 0) {
    throw new Error('sign-issue: no draft issue found to sign')
  }
  if (drafts.length > 1) {
    throw new Error(
      `sign-issue: ${drafts.length} draft issues found (${drafts.map((d) => d.id).join(', ')}) — refusing; there must be exactly one`,
    )
  }

  const draft = drafts[0]
  if (id !== null && id !== draft.id) {
    throw new Error(`sign-issue: --id "${id}" does not match the one draft issue "${draft.id}"`)
  }

  if (draft.published !== null || draft.weThink.signedBy !== null || draft.weThink.signedOn !== null) {
    throw new Error(
      `sign-issue: issue "${draft.id}" is marked draft but already carries signed fields — refusing`,
    )
  }

  if (isProposedEmpty(draft.proposed)) {
    throw new Error(
      `sign-issue: issue "${draft.id}" has no proposed content to sign (proposed is null or empty)`,
    )
  }

  return draft
}

/**
 * How many proposed stance notes `computeSignedIssue` silently drops by
 * always signing with `postureDeltas: []` (coordinator review of
 * SEC-MARKET-PUBLISH-001 build 1, 2026-09-21). `MachineProposal.postureDeltas`
 * is one prose string, not a list, so there is no reliable way to count
 * individual notes inside it — this counts the field itself: 0 when it is
 * blank or exactly the gather-brief.md convention for "nothing to propose"
 * ("none proposed", case-insensitive, optional trailing period), 1 for
 * anything else, including a draft that leads with "none proposed" but then
 * goes on to flag something (the real 2026-w37 draft does exactly this: "None
 * proposed, with one flagged for a human look..."). If a future draft's prose
 * ever needs to be split into more than one tracked note, this undercounts —
 * a known, stated limitation, not a silent one.
 */
export function postureDeltasDroppedCount(proposed: MachineProposal): number {
  const text = proposed.postureDeltas.trim()
  if (text === '') return 0
  if (/^none proposed\.?$/i.test(text)) return 0
  return 1
}

export interface SignIssueOptions {
  signedOn: string
  authorName: string
}

/**
 * Pure transform: draft -> published (SEC-MARKET-PUBLISH-001 §2.2, §3).
 *
 * - `weThink.summary` and `weThink.noCalls` come from `proposed`.
 * - `weThink.thesis` is always `null`. The founding thesis left the weekly
 *   issue for its own standing page at `/thesis/` (build 3, D-72/D-73); an
 *   older draft's `proposed.thesis`, if still present, is ignored rather than
 *   carried forward.
 * - `weThink.postureDeltas` is always `[]`. `proposed.postureDeltas` is prose
 *   only — `MachineProposal.postureDeltas` is a `string`, while
 *   `weThink.postureDeltas` is a `PostureDelta[]`, a structured record that
 *   `verify:issue` check 9 cross-checks against `securityDomains` and the
 *   edition history. There is no safe, mechanical way to turn prose into one
 *   of those records, so this automated signer always signs with none rather
 *   than guess at one. Converting an accepted posture move into a real
 *   PostureDelta stays a separate, more deliberate step (spec §4.3, not yet
 *   built) — his approval of an issue's read is not approval of a posture
 *   change.
 * - `signedBy` is `authorName`; `published` and `signedOn` are `signedOn`.
 * - The top-level `read` is taken explicitly from `proposed.read`
 *   (SEC-MARKET-PUBLISH-001 §2.2; coordinator review point C, 2026-09-21).
 *   An earlier version left `issue.read` untouched on the assumption that the
 *   gather always writes the same text to both fields — true today, but an
 *   assumption a future draft could quietly violate, and the spec says to
 *   take it from `proposed` explicitly rather than lean on that coincidence.
 * - `proposed` becomes `null`.
 *
 * Callers are expected to have already validated preconditions with
 * `findDraftToSign` — this function re-checks only that `proposed` exists, so
 * it fails loudly rather than silently if ever called out of order.
 */
export function computeSignedIssue(issue: Issue, options: SignIssueOptions): Issue {
  if (!issue.proposed) {
    throw new Error(`sign-issue: issue "${issue.id}" has no proposed content to sign`)
  }
  const { signedOn, authorName } = options
  return {
    ...issue,
    read: issue.proposed.read,
    published: signedOn,
    status: 'published',
    weThink: {
      summary: issue.proposed.summary,
      postureDeltas: [],
      thesis: null,
      noCalls: issue.proposed.noCalls,
      signedBy: authorName,
      signedOn,
    },
    proposed: null,
  }
}
