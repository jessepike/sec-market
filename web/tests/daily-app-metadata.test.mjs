import test from 'node:test'
import assert from 'node:assert/strict'
import { dailyReleaseMetadata } from '../scripts/app-release.mjs'

const daily = { enabled: true, runId: 'run', fileSha256: 'snapshot', contractSha256: 'contract', coverageComplete: true }
const legacy = { dailyRunId: 'run', dailySnapshotSha256: 'snapshot', dailyContractSha256: 'contract', dailyCoverageComplete: true }

test('legacy daily release metadata remains identical', () => {
  assert.deepEqual(dailyReleaseMetadata(daily), legacy)
  assert.deepEqual(dailyReleaseMetadata({ enabled: false }), {})
})

test('v2 release metadata keeps intake completion separate from pending review', () => {
  assert.deepEqual(dailyReleaseMetadata({ ...daily, coverageMeasure: 'daily_source_intake_v2', intakeComplete: true, processingComplete: false, historicalReviewComplete: false }), {
    ...legacy,
    dailyCoverageMeasure: 'daily_source_intake_v2',
    dailyIntakeComplete: true,
    dailyProcessingComplete: false,
    dailyHistoricalReviewComplete: false,
  })
})
