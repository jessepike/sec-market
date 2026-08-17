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

export interface SummaryCard {
  id: string
  label: string
  headline: string
  detail: string
  disposition: string
  evidenceIds: string[]
}

export interface SecurityDomain {
  id: string
  name: string
  coverage: CoverageResult
  posture: Posture
  tag: TempoTag
  momentum: Momentum
  evidenceStrength: ConfidenceLevel
  print: string
  tempo: string
  why: string
  summary: string
  watchItems: string[]
  supportingEvidenceIds: string[]
  counterEvidenceIds: string[]
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
