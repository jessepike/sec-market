import type { SecurityDomain } from './types'

export const securityDomains: SecurityDomain[] = [
  {
    id: 'network-sase',
    name: 'Network / SASE',
    coverage: 'PASS_WITH_LIMITATION',
    posture: 'PREPARE',
    momentum: 'accelerating',
    evidenceStrength: 'medium',
    summary:
      'Fortinet, Cisco firewall orders, Zscaler, and Cloudflare show realized to improving momentum. Treat as current refresh and displacement motion — not proof that AI capex caused a broad security wave.',
    watchItems: [
      'Organic momentum after refresh, pricing, and M&A adjustments',
      'Check Point weakness vs. Fortinet/Cisco improvement',
      'Whether networking demand is infrastructure spend vs. incremental cybersecurity',
    ],
    supportingEvidenceIds: ['C3', 'C4', 'C5', 'A2'],
    counterEvidenceIds: ['C6'],
  },
  {
    id: 'cloud-security',
    name: 'Cloud Security',
    coverage: 'INSUFFICIENT_COVERAGE',
    posture: 'INVESTIGATE',
    momentum: 'mixed-positive',
    evidenceStrength: 'low',
    summary:
      'Cloud and AI-capacity investment continues; Alphabet announced a ~$32B Wiz acquisition. Cloud incidents expose posture gaps. No clean three-company domain-specific financial series exists.',
    watchItems: [
      'Workload migration and AI-capacity activation milestones',
      'Native cloud controls vs. residual specialist gaps',
      'CNAPP consolidation and platform absorption',
    ],
    supportingEvidenceIds: ['D5a', 'D7'],
    counterEvidenceIds: ['D1'],
  },
  {
    id: 'identity',
    name: 'Identity / Machine Identity',
    coverage: 'INSUFFICIENT_COVERAGE',
    posture: 'INVESTIGATE',
    momentum: 'stable-to-decelerating',
    evidenceStrength: 'low',
    summary:
      'Identity is a recurring requirement; CyberArk transaction signals platform capital. Okta cRPO growth decelerated to 12%; agent-identity product revenue remains early.',
    watchItems: [
      'Consequential machine identities or delegated access introduction',
      'MFA, credential, and delegated-access gaps from incidents',
      'Hygiene bundling vs. specialist spend',
    ],
    supportingEvidenceIds: ['D5b', 'D7', 'D6'],
    counterEvidenceIds: ['C7'],
  },
  {
    id: 'data-ai-security',
    name: 'Data / AI Security',
    coverage: 'PASS_WITH_LIMITATION',
    posture: 'PREPARE',
    momentum: 'accelerating',
    evidenceStrength: 'medium',
    summary:
      'Rubrik (+32% subscription ARR) and Varonis (~+25% SaaS ARR ex-conversions) show selected acceleration. Planned AI-protection spend has not become a broad realized series.',
    watchItems: [
      'Sensitive data entering new AI workloads',
      'DSPM absorption into CNAPP or platform controls',
      'Conversion-distorted headline metrics',
    ],
    supportingEvidenceIds: ['C8a', 'C8b', 'D2', 'D7'],
    counterEvidenceIds: ['D1'],
  },
  {
    id: 'secops',
    name: 'Security Operations',
    coverage: 'INSUFFICIENT_COVERAGE',
    posture: 'INVESTIGATE',
    momentum: 'mixed-positive',
    evidenceStrength: 'low',
    summary:
      'Splunk, Red Canary, and Chronosphere acquisitions break financial comparability. CrowdStrike re-accelerated but platformization and share shift dominate over a new broad SecOps demand cycle.',
    watchItems: [
      'Automation priority vs. constrained hiring (ISC2)',
      'Platform consolidation redistributing spend',
      'Organic bridges after major acquisitions',
    ],
    supportingEvidenceIds: ['C1', 'C2', 'D4'],
    counterEvidenceIds: ['C6'],
  },
  {
    id: 'ai-runtime',
    name: 'AI Runtime Security',
    coverage: 'INSUFFICIENT_COVERAGE',
    posture: 'INVESTIGATE',
    momentum: 'stable-positive',
    evidenceStrength: 'low',
    summary:
      'Product formation and buyer intent are strong (59% plan GenAI protection increases; 32% already spending on AI-security tools). Independent customer outcomes and realized specialist spend remain limited.',
    watchItems: [
      'Pilot-to-production workload scaling',
      'Native platform security absorption',
      'Realized specialist bookings vs. intent surveys',
    ],
    supportingEvidenceIds: ['D2', 'D3'],
    counterEvidenceIds: ['D1'],
  },
]
