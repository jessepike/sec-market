import type { IntakeDailyCoverage } from '../../src/data/tracker/daily'

// Fictional counts exercise the approved reporting schema, not live collection credit.
export const intakeReviewFixture: IntakeDailyCoverage = {
  schemaVersion: 2, measure: 'daily_source_intake_v2', checkedAt: '2026-10-24T04:00:00Z',
  lastCollectionAt: '2026-10-24T03:58:00Z', validUntil: '2026-10-25T09:58:00Z',
  overdueHours: 30, automationEnabled: true,
  successfulTasks: 557, requiredTasks: 557, gapTaskIds: [], complete: true,
  intake: { measure: 'daily_source_intake_v2', evaluated: true, status: 'collected',
    successfulTasks: 557, requiredTasks: 557, gapTaskIds: [], complete: true },
  processing: { complete: false, inventoryDocuments: 100, reviewedDocuments: 20, pendingDocuments: 80,
    heldDocuments: 3, changedDocuments: 6, unknownDateDocuments: 4 },
  historicalReview: { complete: false, inventoryDocuments: 9900, reviewedDocuments: 200,
    pendingDocuments: 9700, heldDocuments: 12 },
}
