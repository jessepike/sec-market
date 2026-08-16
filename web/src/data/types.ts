export type SourceClass =
  | 'FILING'
  | 'IR'
  | 'TRANSCRIPT'
  | 'OFFICIAL'
  | 'INDEPENDENT'
  | 'VENDOR-SURVEY'
  | 'VENDOR-RESEARCH'

export type ConfidenceLevel = 'high' | 'medium' | 'low'
export type Posture = 'PREPARE' | 'INVESTIGATE' | 'NO-CALL'
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
  momentum: Momentum
  evidenceStrength: ConfidenceLevel
  summary: string
  watchItems: string[]
  supportingEvidenceIds: string[]
  counterEvidenceIds: string[]
}

export interface MarketSignal {
  id: string
  date: string
  category: 'financial' | 'investment' | 'buyer' | 'regulation' | 'operating' | 'incident'
  headline: string
  detail: string
  evidenceIds: string[]
}
