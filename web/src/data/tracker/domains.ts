/**
 * Twelve-domain coverage model — step 5 of the autonomy plan
 * (docs/active/autonomy-coverage-plan.md §4, D-76/D-77). Replaces the old
 * four-domain landscape as the site's declared coverage: a fixed list of
 * domains, each with the suppliers tracked inside it (see suppliers.ts) and
 * one factual line describing what the domain covers. No stance, ranking, or
 * forecast appears in this file — see web/scripts/verify-tracker.ts, which
 * fails the build on a banned word anywhere in a domain's scope line.
 *
 * Order here is fixed and matches docs/active/autonomy-coverage-plan.md §4's
 * table. Adding or dropping a domain is a data edit to this file plus
 * suppliers.ts, not a code change.
 */

export interface TrackerDomain {
  id: string
  /** Short display name, e.g. "Endpoint and XDR". */
  name: string
  /** One factual sentence: what this domain covers. No judgment words. */
  scope: string
}

export const trackerDomains: TrackerDomain[] = [
  {
    id: 'endpoint-xdr',
    name: 'Endpoint and XDR',
    scope: 'Endpoint detection and response and extended detection and response platforms.',
  },
  {
    id: 'secops',
    name: 'Security operations (SIEM/SOAR)',
    scope:
      'Security information and event management, and security orchestration, automation and response.',
  },
  {
    id: 'managed-security',
    name: 'Managed security and MDR',
    scope: 'Managed detection and response and outsourced security operations.',
  },
  {
    id: 'network-sase',
    name: 'Network and SASE',
    scope: 'Network security, secure access service edge, and secure service edge.',
  },
  {
    id: 'cloud',
    name: 'Cloud security',
    scope: 'Cloud-native application protection platforms and cloud security posture management.',
  },
  {
    id: 'identity',
    name: 'Identity',
    scope: 'Identity and access management, privileged access management, and identity governance.',
  },
  {
    id: 'data',
    name: 'Data security',
    scope: 'Data security posture management, data loss prevention, and backup and resilience treated as security.',
  },
  {
    id: 'exposure',
    name: 'Vulnerability and exposure management',
    scope: 'Vulnerability scanning, exposure management, and attack-surface management.',
  },
  {
    id: 'appsec',
    name: 'Application security',
    scope: 'Application security testing and software-supply-chain security.',
  },
  {
    id: 'email',
    name: 'Email security',
    scope: 'Email security and business email compromise protection.',
  },
  {
    id: 'ot-iot',
    name: 'OT and IoT security',
    scope: 'Operational-technology and industrial IoT security.',
  },
  {
    id: 'ai-security',
    name: 'AI security',
    scope:
      'Security products for AI systems, covered as a market — who is buying whom and what is reported as revenue, not as news.',
  },
]

export const trackerDomainIds = trackerDomains.map((domain) => domain.id)

/**
 * What the site does not cover, stated plainly (product-core.md §4,
 * intent.md v1.4 scope amendment). Shown on the front page's "What this
 * site covers" section (autonomy-coverage-plan.md §3d).
 */
export const notCoveredByTracker: string[] = [
  'Daily security news, vulnerabilities, and breaches as events',
  'Product reviews and technical evaluations',
  'Investment advice',
  'Physical security, guarding and access-control hardware as a market',
  'Governance, risk and compliance platforms that are not themselves a security-domain product',
  'Insurance and cyber-insurance underwriting',
  'Security domains outside the twelve listed above',
]
