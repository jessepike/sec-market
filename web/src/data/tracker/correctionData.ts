import originals from './originals.json' with { type: 'json' }
import policy from './factualCorrectionPolicy.json' with { type: 'json' }
import bundle from '../generated/factualCorrections.json' with { type: 'json' }
import { projectEvents, projectSuppliers, projectEvidence, validateBundle } from './factualCorrections'
import type { FactualCorrectionInventories } from './factualCorrections'

// The fixed originals contain no imports. All three projections validate this same
// complete context, avoiding a cycle through the public supplier/event/evidence views.
export const factualCorrectionOriginals = originals as unknown as FactualCorrectionInventories
const validated: unknown = bundle
validateBundle(validated, policy.policySha256, factualCorrectionOriginals)
export const factualCorrectionBundle = validated
export const factualCorrectionGroups = factualCorrectionBundle.groups
export const factualCorrectionSourceEvidenceIds = policy.sourceEvidenceIds
export const originalHandCollectedEvents = factualCorrectionOriginals.events.slice()
export const originalManualTrackerSuppliers = factualCorrectionOriginals.suppliers.slice()
export const originalHandWrittenEvidenceRecords = factualCorrectionOriginals.evidence.slice()
export const effectiveHandCollectedEvents = projectEvents(factualCorrectionOriginals, bundle, policy.policySha256)
export const effectiveManualTrackerSuppliers = projectSuppliers(factualCorrectionOriginals, bundle, policy.policySha256)
export const effectiveHandWrittenEvidenceRecords = projectEvidence(factualCorrectionOriginals, bundle, policy.policySha256)
