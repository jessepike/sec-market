import type { printGroups } from './prints'

export type SourceClass =
  | 'FILING'
  | 'IR'
  | 'TRANSCRIPT'
  | 'OFFICIAL'
  | 'INDEPENDENT'
  | 'OWN_ANALYSIS'
  | 'VENDOR-SURVEY'
  | 'VENDOR-RESEARCH'

export type ConfidenceLevel = 'high' | 'medium' | 'low'
export type Posture = 'PREPARE' | 'INVESTIGATE' | 'NO-CALL'
/** No RUN. Episode 002 caps Network/SASE at PREPARE; PRIORITIZE needs a separate decision episode. */
export type TempoTag = 'PREPARE' | 'WATCH'
/** Decision window the posture is meant to govern. Not a freshness stamp. */
export type DecisionHorizon =
  | 'This quarter'
  | 'This planning cycle'
  | 'Next 1–4 quarters'
  | 'Next 4–8 quarters'
  | 'Beyond 8 quarters'
export type EditionChangeKind = 'held' | 'revised' | 'new'
export type CoverageResult = 'PASS' | 'PASS_WITH_LIMITATION' | 'INSUFFICIENT_COVERAGE' | 'NO-CALL'
export type Momentum = 'accelerating' | 'stable-positive' | 'stable-to-decelerating' | 'mixed-positive' | 'weak'

/**
 * Who is accountable for a claim.
 * 'tracked'  — mechanically refreshed from a public source. No judgment applied.
 * 'judged'   — a person set this, on a date, at a stated confidence.
 */
export type ProvenanceLayer = 'tracked' | 'judged'

export interface TrackedClaim {
  layer: 'tracked'
  evidenceIds: [string, ...string[]]
  observedOn: string
}

export interface JudgedClaim {
  layer: 'judged'
  judgedOn: string
  confidence: ConfidenceLevel
  evidenceIds: string[]
}

export type Provenance = TrackedClaim | JudgedClaim

export type VendorPosition = 'platform' | 'incumbent' | 'challenger' | 'early' | 'absorbed'

export type PressureGroup = 'holding' | 'buying-in' | 'outrun' | 'challengers'

export interface PressureRow {
  id: string
  vendors: string[]
  position: VendorPosition
  print: string
  read: string
  provenance: { print: Provenance; read: Provenance }
}

export type HypothesisState = 'NO-CALL' | 'TRACKING' | 'SUPPORTED' | 'FALSIFIED'

export interface Hypothesis {
  id: string
  claim: string
  state: HypothesisState
  note: string
  firstTest: string | null
  evidenceIds: string[]
  provenance: JudgedClaim
}

// A tracked claim without evidence must not compile. Uncomment to prove it:
// const _invalidTracked: TrackedClaim = {
//   layer: 'tracked',
//   evidenceIds: [],
//   observedOn: '2026-08-17',
// }

export interface SourceAttribution {
  organization: string
  publicationDate: string
  economicPeriod: string
  canonicalUrl?: string
}

export interface EvidenceRecord {
  id: string
  title: string
  organization: string
  publicationDate: string
  economicPeriod: string
  canonicalUrl: string
  excerpt: string
  sourceClass: SourceClass
  interpretation: string
  limitations: string
  conflictingEvidenceIds: string[]
  artifactLabel: string
  tags: string[]
  /** Per-source dates when one record combines multiple organizations */
  sourceAttributions?: SourceAttribution[]
  /** ISO date the underlying source was retrieved, when it differs from publicationDate. */
  retrievedAt?: string
  /** Machine-readable retrieval receipt for the underlying source, when captured. */
  retrieval?: { finalUrl: string; sha256: string; fetchedAt: string; locator?: string }
}

export interface SecurityDomain {
  id: string
  name: string
  coverage: CoverageResult
  posture: Posture
  tag: TempoTag
  /** ISO date the published posture was set. */
  asOf: string
  horizon: DecisionHorizon
  momentum: Momentum
  evidenceStrength: ConfidenceLevel
  print: string
  why: string
  summary: string
  watchItems: string[]
  /** Evidence that produced this posture. */
  supportingEvidenceIds: string[]
  counterEvidenceIds: string[]
}

export interface EditionSurfaceChange {
  id: string
  label: string
  kind: EditionChangeKind
  detail: string
}

/** What a single edition published for one domain. Frozen once the edition ships. */
export interface PostureSnapshot {
  domainId: string
  posture: Posture
  tag: TempoTag
  /** null when that edition published no horizon for the domain. Never backfilled. */
  horizon: DecisionHorizon | null
}

/** One entry in the append-only edition history. */
export interface EditionRecord {
  id: string
  date: string
  dateDisplay: string
  summary: string
  surfaces: EditionSurfaceChange[]
  postures: PostureSnapshot[]
  /** Human judgment about a posture, keyed by domain id. Optional per domain. */
  notes: Record<string, string>
}

/** Derived view of the current edition. Prior identity comes from the history. */
export interface Edition {
  id: string
  date: string
  dateDisplay: string
  priorId: string | null
  priorDateDisplay: string | null
  summary: string
  surfaces: EditionSurfaceChange[]
}

export interface VendorPrint {
  id: string
  group: string
  name: string
  period: string
  value: string
  metric: string
  note: string
  tone: 'up' | 'down' | 'flat'
  /** Default print. Coverage names have no comparable series this window. */
  surface?: 'print' | 'coverage'
  position?: VendorPosition
  evidenceIds: string[]
  /**
   * Optional second domain this print is also counted under. Must differ from
   * `group` and be one of `printGroups`. The eyebrow's distinct-print total is
   * unaffected — this only makes the print's card also render, with a
   * primary-group label, inside the secondary group's section. See
   * PrintGrid.tsx and scripts/verify-integrity.ts.
   */
  secondaryGroup?: (typeof printGroups)[number]
  /** Lower-case, hyphenated vendor slug for the vendor lens. Populated in a later task. */
  vendorSlug?: string
}

export interface ContextStat {
  value: string
  label: string
  tone: 'up' | 'down' | 'hold'
  evidenceIds: string[]
}

export interface WatchItem {
  id: string
  window: string
  item: string
  why: string
}

export type ActivitySurface = 'lead' | 'more' | 'background'

export interface ActivityItem {
  id: string
  kind: 'ma' | 'funding'
  date: string
  actor: string
  target: string
  value: string
  domain: string
  headline: string
  note: string
  surface: ActivitySurface
  /** Sort key for lead headlines. Lower is higher on the page. */
  leadOrder?: number
  evidenceIds: string[]
}

// --- Weekly issue (SEC-MARKET-ISSUE-001 §3) ---

export type Lane = 'formation' | 'absorption' | 'prints' | 'capital'
export type IssueStatus = 'draft' | 'published'

export interface IssueItem {
  id: string // `${issueId}-${lane}-${n}`
  lane: Lane
  headline: string // ≤ 110 chars, states the fact
  why: string // one sentence, why it matters, may be empty on a draft
  date: string // ISO date of the event or filing
  evidenceIds: [string, ...string[]]
  vendors?: string[] // vendor slugs, for the lens
  domainId?: SecurityDomain['id']
  background?: true // dated before the window; must say so on the page
}

export interface PostureDelta {
  domainId: SecurityDomain['id']
  from: Posture
  to: Posture
  basis: string
  confidence: ConfidenceLevel
  evidenceIds: [string, ...string[]]
}

export interface ThesisScore {
  thesis: 'episode-002'
  verdict: 'holds' | 'strengthens' | 'weakens' | 'no-call'
  basis: string
  confidence: ConfidenceLevel
  evidenceIds: string[]
}

/**
 * What the gather proposes. Visible on a draft, labelled as a machine
 * proposal; must be null once published.
 *
 * `thesis` is optional (SEC-MARKET-PUBLISH-001 §3, D-72/D-73): the founding
 * thesis is a standing analysis at `/thesis/`, not a weekly verdict, so the
 * gather no longer proposes one and the sign step ignores it if present. An
 * older draft that still carries a `thesis` continues to type-check.
 */
export interface MachineProposal {
  read: string
  thesis?: ThesisScore
  noCalls: string[]
  postureDeltas: string // prose only; the signer converts what they accept into PostureDelta records
  summary: string
  /**
   * Judged-claim ids (see ClaimKind/claimId in reconfirmationHelpers.ts) that
   * this week's evidence cuts against (SEC-MARKET-PUBLISH-001 §4.3, gather-
   * brief.md "Going stale"). The gather may name a stance as challenged; it
   * never reconfirms one and never writes to reconfirmations.ts. A claim
   * listed here is excluded from automatic re-dating even if it is stale and
   * `reconfirm` is signed — it needs a human look, not a rubber stamp.
   */
  challengedClaimIds?: string[]
}

// --- Corrections (SEC-MARKET-FABLE-001 T6-13) ---

/** One item's corrected reading, carried alongside the original in the record. */
export interface CorrectedReading {
  itemId: IssueItem['id']
  correctedHeadline: string
  evidenceIds: string[]
  /** Set when a claim beyond the headline (e.g. a "why it matters" comparison) is withdrawn. */
  note?: string
}

/**
 * An owner-approved, append-only correction to a published issue. Never
 * edits the issue itself — see web/src/data/issues/issues.lock.json, the
 * append-only publication manifest the issue data is hashed into. A
 * correction is a dated note that travels beside the affected item(s) and
 * is also listed on its own page at /corrections/.
 */
export interface Correction {
  id: string // `C-<published-date>-<sequence>`, e.g. `C-2026-09-20-01`
  date: string // ISO date the correction was approved and published
  issueId: Issue['id']
  text: string // the full owner-approved correction text, verbatim
  approvedBy: string // must equal AUTHOR_NAME in meta.ts
  correctedReadings: CorrectedReading[]
}

// --- Reconfirmations (SEC-MARKET-PUBLISH-001 §4.3) ---

/**
 * An owner-approved, append-only re-dating of a judged claim (a domain
 * stance, a Platform-pressure row, or a tracked hypothesis — see ClaimKind
 * in reconfirmationHelpers.ts). Never edits the claim's own `judgedOn` date;
 * the effective date a reader sees is computed from the original judgment
 * plus the newest reconfirmation, if any (`effectiveJudgment`). Written only
 * by the sign step, and only when the owner's approval carried the word
 * `reconfirm` (docs/active/publish-path-spec.md §4.3).
 */
export interface Reconfirmation {
  /** `${ClaimKind}:${id}` — see claimId() in reconfirmationHelpers.ts. */
  claimId: string
  reconfirmedOn: string // ISO date
  by: string // must equal AUTHOR_NAME in meta.ts
  via: Issue['id'] // the published issue whose approval carried the reconfirmation
}

export interface Issue {
  id: string // ISO week, `2026-w36`
  weekEnding: string // ISO date, the Sunday
  windowStart: string // ISO date; normally weekEnding − 6, longer only for the opening issue
  published: string | null // ISO date; null while draft
  status: IssueStatus
  read: string // one line, ≤ 140 chars, the h1
  quiet?: true // a quiet week says so
  sections: Array<{ lane: Lane; intro?: string; items: IssueItem[] }> // exactly four, in Lane order
  weThink: {
    summary: string
    postureDeltas: PostureDelta[]
    thesis: ThesisScore | null // null on a draft; the signer sets it
    noCalls: string[]
    signedBy: string | null // must equal AUTHOR_NAME in meta.ts when set
    signedOn: string | null
  }
  proposed: MachineProposal | null // set by the gather on a draft; null once published
  sources: { readable: number; unreadable: string[] }
}
