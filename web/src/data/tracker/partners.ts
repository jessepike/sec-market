/**
 * Vendor partner tags for security solution providers (D-153, vendor pairing v1). Display only.
 *
 * Each tag is a dated public statement by a vendor already on the site that names the provider:
 * an award or partner program status, cited to the vendor's own page. Tags live on the provider's
 * seed record in onboarding.json (`partners`). No tag is rated, ranked or inferred, and none comes
 * from ePlus's own partner data (D-153). They show on Vercel preview builds only, in the onboarding
 * rows on /coverage/ and on company pages, until the owner approves them for production.
 */
import onboarding from './onboarding.json' with { type: 'json' }
import { shortSupplierName } from './names'
import { trackerSuppliers } from './suppliers'
import type { EvidenceRecordLike } from './onboardingTypes'

export interface VendorPartner {
  /** A supplier on the site, e.g. "splunk", "zscaler", "crwd". */
  vendorId: string
  /** The vendor's own words for the award or program, with its year and region. */
  program: string
  /** Date of the vendor's statement, YYYY-MM-DD. */
  date: string
  evidenceIds: string[]
}

export interface PartnerLine {
  /** "Named partner of: Splunk (2026 Services Partner of the Year, AMER)". */
  text: string
  sources: { label: string; url: string }[]
}

const records = onboarding.suppliers as Array<{ id: string; partners?: VendorPartner[] }>
const evidenceById = new Map((onboarding.evidence as EvidenceRecordLike[]).map((e) => [e.id, e]))

/** Every live supplier on the site, by id. A partner vendor must be one of them. */
export const knownVendorNames: ReadonlyMap<string, string> = new Map(
  trackerSuppliers.map((s) => [s.id, shortSupplierName(s.name)] as const),
)

export function partnersFor(supplierId: string): VendorPartner[] {
  return records.find((r) => r.id === supplierId)?.partners ?? []
}

export function partnerLine(supplierId: string): PartnerLine | null {
  const partners = partnersFor(supplierId)
  if (partners.length === 0) return null
  const parts = partners.map((p) => `${knownVendorNames.get(p.vendorId) ?? p.vendorId} (${p.program})`)
  const sources = partners.flatMap((p) => p.evidenceIds.flatMap((id) => {
    const record = evidenceById.get(id)
    return record ? [{ label: record.organization, url: record.canonicalUrl }] : []
  }))
  return { text: `Named partner of: ${parts.join('; ')}`, sources: [...new Map(sources.map((s) => [s.url, s])).values()] }
}
