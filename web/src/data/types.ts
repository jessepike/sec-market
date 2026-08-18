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
  evidenceIds: string[]
}

export interface ContextStat {
  value: string
  label: string
  tone: 'up' | 'down' | 'hold'
  evidenceIds: string[]
}

export interface MarketSignal {
  id: string
  date: string
  category: 'financial' | 'investment' | 'buyer' | 'regulation' | 'operating' | 'incident'
  freshness: 'current' | 'background'
  headline: string
  detail: string
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
