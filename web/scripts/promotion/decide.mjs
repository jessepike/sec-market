// Automatic promotion decision (D-103). Decides whether `main` may fast-forward
// to a `preview` commit with no human step. Pure Git inspection, no network.
//
//   promote  every rule below passes
//   wait     a rule needs time: the newest commit has not soaked yet
//   hold     a major change is waiting for the owner (see MAJOR below)
//   none     nothing to promote: main already equals preview
//   fail     main is not an ancestor of preview, so a fast-forward is impossible
//
// The workflow (.github/workflows/promote.yml) adds the checks that need a
// build: tests green, a fresh certification that reproduces the committed
// data, and the page-structure guard.
import { execFileSync } from 'node:child_process'
import { appendFileSync } from 'node:fs'
import { pathToFileURL } from 'node:url'

/** Files the scheduled certified refresh writes. A change touching only these is data-only. */
export const DATA_FILES = [
  'web/src/data/generated/edgarFacts.json',
  'web/src/data/generated/filingEvents.json',
  'web/src/data/generated/filingEvidence.json',
  'web/src/data/generated/filingRun.json',
  'web/src/data/generated/certifiedCoverage.json',
  'web/src/data/generated/certifiedVerification.json',
]

/** Paths whose change always needs the owner: governance, deploy safety and the promotion rules themselves. */
export const PROTECTED = [
  /^intent\.md$/,
  /^\.claude\//,
  /^\.githooks\//,
  /^web\/vercel\.json$/,
  /^\.github\/workflows\/promote\.yml$/,
  /^web\/scripts\/promotion\//,
]

/** Hours the newest commit must age before promotion. */
export const SOAK_HOURS = { data: 6, other: 24 }

const TRAILER = /^Owner-Review:\s*required\s*$/im

function git(repo, args) {
  return execFileSync('git', args, { cwd: repo, encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] }).trim()
}

function isAncestor(repo, a, b) {
  try { execFileSync('git', ['merge-base', '--is-ancestor', a, b], { cwd: repo, stdio: 'ignore' }); return true } catch { return false }
}

export function decide(repo, { base = 'origin/main', head = 'HEAD', now = Date.now() } = {}) {
  const headSha = git(repo, ['rev-parse', head])
  if (!isAncestor(repo, base, head)) return { action: 'fail', sha: headSha, reasons: [`${base} is not an ancestor of ${head}; a fast-forward is impossible`] }
  const commits = git(repo, ['rev-list', `${base}..${head}`]).split('\n').filter(Boolean)
  if (!commits.length) return { action: 'none', sha: headSha, reasons: ['main already matches preview'] }

  const files = git(repo, ['diff', '--no-renames', '--name-only', base, head]).split('\n').filter(Boolean)
  const dataOnly = files.every(f => DATA_FILES.includes(f))
  const major = []
  for (const sha of commits) {
    const message = git(repo, ['log', '-1', '--format=%B', sha])
    if (TRAILER.test(message)) major.push(`${sha.slice(0, 7)} is marked Owner-Review: required (${message.split('\n')[0]})`)
  }
  for (const f of files) if (PROTECTED.some(p => p.test(f))) major.push(`${f} is a protected path`)
  const workflowDiff = git(repo, ['diff', '--no-renames', '-U0', base, head, '--', '.github/workflows'])
  if (/^\+.*\$\{\{\s*secrets\./m.test(workflowDiff)) major.push('a workflow starts using a repository secret')

  const newest = Number(git(repo, ['log', '-1', '--format=%ct', head])) * 1000
  const ageHours = (now - newest) / 3600000
  const soak = dataOnly ? SOAK_HOURS.data : SOAK_HOURS.other
  const summary = { sha: headSha, commits: commits.length, files, dataOnly, ageHours: Math.round(ageHours * 10) / 10, soakHours: soak }

  if (major.length) return { action: 'hold', ...summary, reasons: major }
  if (ageHours < soak) return { action: 'wait', ...summary, reasons: [`newest commit is ${summary.ageHours} h old; ${soak} h soak required`] }
  return { action: 'promote', ...summary, reasons: [dataOnly ? 'data-only change, soaked' : 'change soaked; no major-change markers'] }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const result = decide(process.cwd())
  console.log(JSON.stringify(result, null, 2))
  if (process.env.GITHUB_OUTPUT) {
    appendFileSync(process.env.GITHUB_OUTPUT, `action=${result.action}\nsha=${result.sha}\ndata_only=${result.dataOnly ?? false}\n`)
    appendFileSync(process.env.GITHUB_OUTPUT, `reasons<<EOF\n${result.reasons.map(r => `- ${r}`).join('\n')}\nEOF\n`)
  }
}
