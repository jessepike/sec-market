/**
 * Pending domains (D-153). Kept apart from domains.ts so graduation.ts can read them without a
 * circular import.
 */
import type { TrackerDomain } from './domains'

/** verify-tracker needs at least this many live companies in a domain. */
export const PENDING_DOMAIN_MIN_LIVE = 3

/**
 * Domains whose companies are all still onboarding (D-153, 2026-11-20). Their companies show only
 * in the preview-only onboarding section, so the domain does too. A pending domain joins
 * `trackerDomains` on its own once three of its companies have graduated (verify-tracker needs at
 * least three live companies per domain), so the production page does not change before then.
 */
export const pendingDomains: TrackerDomain[] = [
  {
    id: 'solution-providers',
    name: 'Security solution providers and services',
    scope: "Resellers, integrators and security service firms that sell, deploy and run the vendors' products.",
    revenueBars: false,
    subareas: [
      {
        id: 'large-solution-providers',
        name: 'Large solution providers',
        scope: 'National and global resellers and integrators with security practices.',
        supplierIds: ['cdw', 'insight', 'eplus', 'presidio', 'wwt', 'guidepoint', 'trace3'],
      },
      {
        id: 'specialist-boutiques',
        name: 'Specialist boutiques',
        scope: 'Smaller service firms that focus on a few vendors or one security domain.',
        supplierIds: ['xalient', 'tekstream', 'bitsio'],
      },
    ],
  },
]
