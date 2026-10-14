import { readFileSync, writeFileSync, mkdirSync, cpSync, rmSync, readdirSync } from 'node:fs'
import { resolve, dirname, relative } from 'node:path'
import { createHash } from 'node:crypto'
import { fileURLToPath, pathToFileURL } from 'node:url'
import { spawnSync } from 'node:child_process'
import { runGate } from './refresh-publication-gate.mjs'

const sha = bytes => createHash('sha256').update(bytes).digest('hex')
export function verifyFrozenData(root, manifest) {
  const seen = []
  function walk(path) { for (const entry of readdirSync(path, { withFileTypes: true })) { const p = resolve(path, entry.name); if (entry.isDirectory()) walk(p); else seen.push(relative(root, p)) } }
  walk(resolve(root, 'src/data'))
  if (seen.length !== Object.keys(manifest.dataFiles).length || seen.some(path => !Object.hasOwn(manifest.dataFiles, path))) throw new Error('Published data inventory changed.')
  for (const [path, expected] of Object.entries(manifest.dataFiles)) if (sha(readFileSync(resolve(root, path))) !== expected) throw new Error(`Published data changed: ${path}`)
  return { unchanged: true, sourceRevision: manifest.sourceRevision, dataFileCount: seen.length, lastCompleteRefreshAt: manifest.lastCompleteRefreshAt }
}

export function appOnlyDecision(snapshot, publication) {
  if (!snapshot.unchanged || publication.lastCompleteRefreshAt !== snapshot.lastCompleteRefreshAt || publication.publishedSourceRevision !== snapshot.sourceRevision) throw new Error('App-only release cannot change published data or its complete-refresh date.')
  return { allowed: true, releaseKind: 'app-only', dataUpdated: false, snapshotRevision: snapshot.sourceRevision, lastCompleteRefreshAt: snapshot.lastCompleteRefreshAt }
}

export function diagnosticPreview(env) {
  return env.VERCEL_ENV === 'preview' || (!env.VERCEL_ENV && !env.VERCEL && env.SMP_APP_PREVIEW === '1')
}

export function publicAttempt(coverage, publication) {
  return { schemaVersion: 1, lastAttemptAt: publication.lastAttemptAt, state: publication.lastAttemptState, published: false,
    lastCompleteRefreshAt: publication.lastCompleteRefreshAt, publishedSnapshotRevision: publication.publishedSourceRevision,
    suppliersAttempted: coverage.supplierChecksReceived, supplierCount: coverage.supplierCount, attemptCounts: coverage.summary,
    failedSupplierIds: [...new Set(coverage.fields.filter(f => ['failed', 'not-checked'].includes(f.status)).map(f => f.supplierId))],
    notice: 'This is a held attempt receipt, not a published refreshed snapshot. Candidate financial values are omitted. Complete refresh requires independent substantive verification under the fixed contract.' }
}

export function verifyAppRelease(repo) {
  const published = resolve(repo, 'web/published-app')
  const manifest = JSON.parse(readFileSync(resolve(published, 'snapshot-manifest.json'), 'utf8'))
  const publication = JSON.parse(readFileSync(resolve(repo, 'web/src/data/generated/refreshPublication.json'), 'utf8'))
  if (process.env.SMP_RELEASE_KIND === 'refresh' || publication.snapshotMode === 'tracker') {
    const result = runGate(repo)
    if (!result.allowed || !result.complete) throw new Error('Refreshed snapshot publication requires 100% certified required checks.')
    return { allowed: true, releaseKind: 'refresh', dataUpdated: true }
  }
  return appOnlyDecision(verifyFrozenData(published, manifest), publication)
}

function command(cwd, args) { const r = spawnSync('npm', args, { cwd, stdio: 'inherit', env: process.env }); if (r.status !== 0) throw new Error(`Release command failed (${r.status}): npm ${args.join(' ')}`) }

export function buildRelease(repo) {
  const decision = verifyAppRelease(repo)
  const web = resolve(repo, 'web'), published = resolve(web, 'published-app')
  const coverage = JSON.parse(readFileSync(resolve(web, 'src/data/generated/refreshCoverage.json'), 'utf8'))
  const publication = JSON.parse(readFileSync(resolve(web, 'src/data/generated/refreshPublication.json'), 'utf8'))
  if (decision.releaseKind === 'refresh') { command(web, ['run', 'build:tracker']); return decision }
  const status = { ...publicAttempt(coverage, publication), appRevision: process.env.VERCEL_GIT_COMMIT_SHA ?? null, appBuiltAt: new Date().toISOString(), appDeployedAt: null }
  writeFileSync(resolve(published, 'src/release-status.json'), JSON.stringify(status, null, 2) + '\n')
  command(published, ['run', 'build'])
  // Default/production artifacts contain only the immutable published app/data.
  // Preview additionally retains the explicit diagnostic candidate as its root.
  const preview = diagnosticPreview(process.env)
  if (preview) {
    command(web, ['run', 'build:diagnostic'])
    cpSync(resolve(published, 'dist'), resolve(web, 'dist/published-preview'), { recursive: true })
    // Assets remain absolute /assets on both renderers; names are content hashed.
    cpSync(resolve(published, 'dist/assets'), resolve(web, 'dist/assets'), { recursive: true, force: false })
  } else {
    rmSync(resolve(web, 'dist'), { recursive: true, force: true })
    cpSync(resolve(published, 'dist'), resolve(web, 'dist'), { recursive: true })
  }
  const dist = resolve(web, 'dist')
  mkdirSync(dist, { recursive: true })
  writeFileSync(resolve(dist, 'refresh-attempt.json'), JSON.stringify(status, null, 2) + '\n')
  writeFileSync(resolve(dist, 'app-release.json'), JSON.stringify({ ...decision, rootView: preview ? 'diagnostic' : 'published', previewIncludesDiagnostic: preview, appRevision: status.appRevision, appBuiltAt: status.appBuiltAt, dataHashes: JSON.parse(readFileSync(resolve(published, 'snapshot-manifest.json'), 'utf8')).dataFiles }, null, 2) + '\n')
  verifyAppRelease(repo)
  console.log(JSON.stringify({ ...decision, previewIncludesDiagnostic: preview }))
  return decision
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  try { const repo = resolve(dirname(fileURLToPath(import.meta.url)), '../..'); console.log(JSON.stringify(process.argv.includes('--verify') ? verifyAppRelease(repo) : buildRelease(repo))) }
  catch (error) { console.error(`App release refused: ${error.message}`); process.exitCode = 2 }
}
