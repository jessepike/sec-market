import type { CoverageResult, Posture } from '../data/types'

interface StatusBadgeProps {
  kind: 'no-call' | 'insufficient' | CoverageResult | Posture | string
}

const labels: Record<string, string> = {
  'no-call': 'NO-CALL',
  insufficient: 'INSUFFICIENT COVERAGE',
  INSUFFICIENT_COVERAGE: 'INSUFFICIENT COVERAGE',
  'NO-CALL': 'NO-CALL',
  PASS: 'Coverage: Pass',
  PASS_WITH_LIMITATION: 'Coverage: Pass (limited)',
  PREPARE: 'PREPARE',
  INVESTIGATE: 'INVESTIGATE',
}

export function StatusBadge({ kind }: StatusBadgeProps) {
  const normalized = kind.toLowerCase().replace(/_/g, '-')
  const isAlert = normalized.includes('no-call') || normalized.includes('insufficient')

  return (
    <span className={`status-badge ${isAlert ? 'status-badge--alert' : ''} status-badge--${normalized}`}>
      {labels[kind] ?? kind}
    </span>
  )
}
