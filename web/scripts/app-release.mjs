// Production build entry point (`npm run build`, run by Vercel).
//
// The site publishes in one mode: the certified tracker (AUTO-002 Phase 2,
// D-101). Before anything is built, certify-gate re-derives every certified
// SEC claim from the committed build inputs and must report 100% with no
// drift. If it does not, the build fails and Vercel keeps serving the last
// good deployment. `--verify` runs the gate without building.
import { readFileSync, writeFileSync, cpSync } from 'node:fs'
import { resolve, dirname } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'
import { spawnSync } from 'node:child_process'
import { verifyDaily } from './verify-daily.mjs'
import { verifyFactualCorrections } from './verify-factual-corrections.mjs'

/** Runs the certified gate; throws unless every certified claim passes. */
export function verifyAppRelease(repo) {
  verifyDaily(resolve(repo, 'web'))
  verifyFactualCorrections(resolve(repo, 'web'))
  const factualViews = spawnSync(process.execPath, ['--import', 'tsx', 'scripts/verify-current-facts.ts'], { cwd: resolve(repo, 'web'), stdio: 'inherit', env: process.env })
  if (factualViews.status !== 0) throw new Error('Exported facts differ from the reviewed projection; the tracker is not published.')
  const publication = JSON.parse(readFileSync(resolve(repo, 'web/src/data/generated/refreshPublication.json'), 'utf8'))
  if (publication.snapshotMode !== 'certified') throw new Error(`Unknown release mode "${publication.snapshotMode}"; only "certified" is supported.`)
  const r = spawnSync('npx', ['tsx', '--tsconfig', 'tsconfig.app.json', 'scripts/certify-gate.ts', '--at-certification'], { cwd: resolve(repo, 'web'), stdio: 'inherit', env: process.env })
  if (r.status !== 0) throw new Error('Certified tier failed its gate; the tracker is not published.')
  const coverage = JSON.parse(readFileSync(resolve(repo, 'web/src/data/generated/certifiedCoverage.json'), 'utf8'))
  return { allowed: true, releaseKind: 'certified', dataUpdated: true, certifiedAt: coverage.checkedAt, contractVersion: coverage.contractVersion }
}

/** Preserve legacy receipt fields; v2 makes the three independent measures explicit. */
export function dailyReleaseMetadata(daily) {
  if (!daily.enabled) return {}
  const metadata = { dailyRunId: daily.runId, dailySnapshotSha256: daily.fileSha256, dailyContractSha256: daily.contractSha256, dailyCoverageComplete: daily.coverageComplete }
  if (daily.coverageMeasure === 'daily_source_intake_v2') Object.assign(metadata, {
    dailyCoverageMeasure: daily.coverageMeasure,
    dailyIntakeComplete: daily.intakeComplete,
    dailyProcessingComplete: daily.processingComplete,
    dailyHistoricalReviewComplete: daily.historicalReviewComplete,
  })
  return metadata
}

/** Gate, then build, then publish the certification receipt and release record beside the site. */
export function buildRelease(repo) {
  const decision = verifyAppRelease(repo)
  const web = resolve(repo, 'web'), dist = resolve(web, 'dist')
  const r = spawnSync('npm', ['run', 'build:certified'], { cwd: web, stdio: 'inherit', env: process.env })
  if (r.status !== 0) throw new Error(`Release command failed (${r.status}): npm run build:certified`)
  cpSync(resolve(web, 'src/data/generated/certifiedCoverage.json'), resolve(dist, 'certified-coverage.json'))
  const release = { ...decision, rootView: 'tracker', appRevision: process.env.VERCEL_GIT_COMMIT_SHA ?? null, appBuiltAt: new Date().toISOString() }
  const daily = verifyDaily(web)
  Object.assign(release, dailyReleaseMetadata(daily))
  const factual = verifyFactualCorrections(web)
  if (factual.enabled) release.factualCorrections = factual
  writeFileSync(resolve(dist, 'app-release.json'), JSON.stringify(release, null, 2) + '\n')
  return release
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  try { const repo = resolve(dirname(fileURLToPath(import.meta.url)), '../..'); console.log(JSON.stringify(process.argv.includes('--verify') ? verifyAppRelease(repo) : buildRelease(repo))) }
  catch (error) { console.error(`App release refused: ${error.message}`); process.exitCode = 2 }
}
