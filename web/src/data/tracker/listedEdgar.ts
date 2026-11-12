import edgarFactsRaw from '../generated/edgarFacts.json' with { type: 'json' }
import { trackerSuppliers } from './suppliers'

/**
 * The EDGAR collection covers every company in edgarRegistry, including companies still in
 * onboarding (D-138), so the release check can validate them before they are listed. The page
 * shows only the filers it lists: public tracker suppliers with an edgarId.
 */
const listedIds = new Set(trackerSuppliers.filter(s => s.kind === 'public' && s.edgarId).map(s => s.edgarId as string))

export const listedEdgarFacts = {
  ...edgarFactsRaw,
  suppliers: edgarFactsRaw.suppliers.filter(s => listedIds.has(s.id)),
  failures: (edgarFactsRaw.failures as { id: string }[]).filter(f => listedIds.has(f.id)),
} as typeof edgarFactsRaw
