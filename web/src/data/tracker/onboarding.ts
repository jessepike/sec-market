/**
 * Suppliers being onboarded (D-138). Each has a sourced seed record in
 * onboarding.json. They are shown on preview builds only, in their own
 * section on /coverage/, and never join trackerSuppliers, the certified
 * cohort, search or any count. A supplier leaves this file and joins the
 * tracker only after the contract change adds it to the daily pipeline and it
 * passes three clean daily runs.
 */
import { displayDomainIds } from './domains'
import onboarding from './onboarding.json' with { type: 'json' }
import { coverageTierFor, coverageTiers, supplierKindLabel } from './coverage'
import { trackerDomains } from './domains'
import { shortSupplierName } from './derive'
import type { EvidenceRecordLike } from './onboardingTypes'
import type { TrackerSupplier } from './suppliers'

declare const __SMP_SHOW_ONBOARDING__: boolean | undefined

/**
 * True only on a Vercel preview build. vite.config.ts sets the constant for the
 * client bundle; Node scripts (prerender) read the same environment variable.
 * The publisher's production build runs in GitHub Actions, where VERCEL_ENV is
 * not "preview", so production never renders this section.
 */
export const showOnboarding: boolean =
  typeof __SMP_SHOW_ONBOARDING__ !== 'undefined'
    ? __SMP_SHOW_ONBOARDING__ === true
    : (globalThis as { process?: { env?: Record<string, string | undefined> } }).process?.env?.VERCEL_ENV === 'preview'

export const onboardingSuppliers = onboarding.suppliers as TrackerSupplier[]
export const onboardingEvidence = onboarding.evidence as EvidenceRecordLike[]

const evidenceById = new Map(onboardingEvidence.map((record) => [record.id, record]))
const domainName = new Map(trackerDomains.map((d) => [d.id, d.name]))

export interface OnboardingRow {
  supplier: TrackerSupplier
  displayName: string
  typeLabel: string
  domains: string[]
  /** Tier it is expected to land in once live. F5 and Akamai are SEC filers, so they target tier 1. */
  targetTier: number
  facts: string[]
  sources: { label: string; url: string }[]
}

function factsFor(supplier: TrackerSupplier): string[] {
  const out: string[] = []
  if (supplier.revenue) {
    const latest = supplier.revenue.latest
    out.push(`Revenue ${latest.value}, ${latest.yoyGrowth} year over year (${latest.period})`)
  }
  if (supplier.headlineMetric) out.push(`${supplier.headlineMetric.label} ${supplier.headlineMetric.value} (${supplier.headlineMetric.period})`)
  if (supplier.lastRound) {
    const r = supplier.lastRound
    out.push(`${r.stage}, ${r.amount}${r.valuation ? ` at ${r.valuation}` : ''}${r.lead ? `, led by ${r.lead}` : ''} (${r.date})`)
  }
  if (!supplier.revenue && !supplier.lastRound && supplier.ownership) out.push(supplier.ownership.status)
  return out
}

function sourcesFor(supplier: TrackerSupplier): { label: string; url: string }[] {
  const ids = new Set<string>([
    ...(supplier.revenue?.latest.evidenceIds ?? []),
    ...(supplier.headlineMetric?.evidenceIds ?? []),
    ...(supplier.lastRound?.evidenceIds ?? []),
    ...(supplier.ownership?.evidenceIds ?? []),
  ])
  return [...ids].flatMap((id) => {
    const record = evidenceById.get(id)
    return record ? [{ label: record.organization, url: record.canonicalUrl }] : []
  })
}

export const onboardingRows: OnboardingRow[] = onboardingSuppliers
  .map((supplier) => ({
    supplier,
    displayName: shortSupplierName(supplier.name),
    typeLabel: supplierKindLabel[supplier.kind],
    domains: displayDomainIds(supplier).map((id) => domainName.get(id) ?? id),
    targetTier: supplier.cik ? 1 : (coverageTiers.find((t) => t.id === coverageTierFor(supplier))?.number ?? 4),
    facts: factsFor(supplier),
    sources: sourcesFor(supplier),
  }))
  .sort((a, b) => a.targetTier - b.targetTier || a.displayName.localeCompare(b.displayName))
