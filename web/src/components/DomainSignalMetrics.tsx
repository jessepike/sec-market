import type { ConfidenceLevel, Momentum } from '../data/types'

interface DomainSignalMetricsProps {
  momentum: Momentum
  evidenceStrength: ConfidenceLevel
}

const momentumLabels: Record<Momentum, string> = {
  accelerating: 'Accelerating',
  'stable-positive': 'Stable positive',
  'stable-to-decelerating': 'Stable to decelerating',
  'mixed-positive': 'Mixed positive',
  weak: 'Weak',
}

const strengthLabels: Record<ConfidenceLevel, string> = {
  high: 'High',
  medium: 'Medium',
  low: 'Low',
}

export function DomainSignalMetrics({ momentum, evidenceStrength }: DomainSignalMetricsProps) {
  return (
    <dl className="domain-signals" aria-label="Momentum and signal strength">
      <div className="domain-signal">
        <dt className="domain-signal__label">Momentum</dt>
        <dd className="domain-signal__value">
          <span className={`metric-pill metric-pill--momentum-${momentum}`}>
            {momentumLabels[momentum]}
          </span>
        </dd>
      </div>
      <div className="domain-signal">
        <dt className="domain-signal__label">Signal strength</dt>
        <dd className="domain-signal__value">
          <span className={`metric-pill metric-pill--strength-${evidenceStrength}`}>
            {strengthLabels[evidenceStrength]}
          </span>
        </dd>
      </div>
    </dl>
  )
}
