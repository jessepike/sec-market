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
export type DecisionHorizon = 'This quarter' | 'This planning cycle' | 'Next 1–4 quarters'
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
