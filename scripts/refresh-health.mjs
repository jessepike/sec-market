import { pathToFileURL } from 'node:url'
import { readFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'

export function assessCoverage(coverage, now = new Date(), maxAgeHours = 36) {
  const age = (now.getTime() - Date.parse(coverage.checkedAt)) / 3600000
  if (!Number.isFinite(age) || age < -.1) return { healthy: false, reason: 'Invalid source-check timestamp.' }
  if (age > maxAgeHours) return { healthy: false, reason: `Source-check receipt is ${Math.floor(age)} hours old; nightly refresh is overdue.` }
  if (!coverage.allSuppliersAttempted) return { healthy: false, reason: `Only ${coverage.supplierChecksReceived} of ${coverage.supplierCount} supplier coverage receipts exist.` }
  if (coverage.state !== 'complete') return { healthy: false, reason: `${coverage.summary.failed} field checks failed; ${coverage.summary['not-checked']} remain unverified. Retained values are not claimed fresh.` }
  return { healthy: true, reason: 'All supplier field checks completed within the nightly freshness window.' }
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) {
  let result
  try {
    const coverage = process.env.COVERAGE_FILE ? JSON.parse(readFileSync(process.env.COVERAGE_FILE, 'utf8'))
      : await (await fetch(`${process.env.SMP_SITE ?? 'https://security-market-pulse-git-preview-pikeholdings.vercel.app'}/refresh-coverage.json`, { signal: AbortSignal.timeout(20000) })).json()
    result = assessCoverage(coverage)
  } catch (error) { result = { healthy: false, reason: `Coverage endpoint could not be read: ${String(error.message)}` } }
  console.log(JSON.stringify(result))
  if (process.env.SMP_ALERT_WRITE === '1') {
    if (!process.env.GH_REPO) throw new Error('GH_REPO must explicitly identify the alert repository.')
    const title = process.env.SMP_ALERT_TITLE ?? 'Security Market Pulse source refresh'
    const list = spawnSync('gh', ['issue', 'list', '--repo', process.env.GH_REPO, '--state', 'open', '--search', title, '--json', 'number,title'], { encoding: 'utf8' })
    if (list.status !== 0) throw new Error(list.stderr)
    const existing = JSON.parse(list.stdout).find(issue => issue.title === title)
    if (result.healthy && existing) {
      const closed = spawnSync('gh', ['issue', 'close', String(existing.number), '--repo', process.env.GH_REPO, '--comment', `Recovered: ${result.reason}`], { encoding: 'utf8' })
      if (closed.status !== 0) throw new Error(closed.stderr)
    } else if (!result.healthy && !existing) {
      const created = spawnSync('gh', ['issue', 'create', '--repo', process.env.GH_REPO, '--title', title, '--body', `${result.reason}\n\nCheck the nightly workflow and /refresh-coverage.json. This monitor checks source/field receipts, not discontinued weekly issues.`], { encoding: 'utf8' })
      if (created.status !== 0) throw new Error(created.stderr)
      console.log(created.stdout.trim())
    }
  }
  process.exitCode = result.healthy ? 0 : 2
}
