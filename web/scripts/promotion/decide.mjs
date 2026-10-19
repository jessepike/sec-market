// Automatic promotion decision (D-103). Decides whether `main` may fast-forward
// to a `preview` commit with no human step. Pure Git inspection, no network.
//
//   promote  the oldest commits on preview pass every rule; `sha` is the newest of them
//   wait     the oldest waiting commit has not soaked yet
//   hold     the oldest waiting commit is a major change (see PROTECTED and TRAILER)
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

/** Paths whose change always needs the owner: governance, deploy safety, CI, dependencies and the certification chain. */
export const PROTECTED = [
  /^intent\.md$/,
  /^AGENTS\.md$/,
  /^CLAUDE\.md$/,
  /^\.claude\//,
  /^\.githooks\//,
  /^\.github\//,
  /^web\/vercel\.json$/,
  /^web\/package(-lock)?\.json$/,
  /^web\/scripts\/promotion\//,
  /^web\/scripts\/(app-release|claim-gate|certify-[a-z-]+)\.(mjs|ts)$/,
  /^web\/scripts\/sec-verify\/independent\.mjs$/,
]

/** Hours a commit must age, from its own date, before it may go live. */
export const SOAK_HOURS = { data: 6, other: 24 }

const TRAILER = /^Owner-Review:\s*required\b/im
const SECRET = /\bsecrets\s*[.[]|toJSON\(\s*secrets\s*\)/

function git(repo, args) {
  return execFileSync('git', args, { cwd: repo, encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'], maxBuffer: 64 * 1024 * 1024 }).trim()
}

function isAncestor(repo, a, b) {
  try { execFileSync('git', ['merge-base', '--is-ancestor', a, b], { cwd: repo, stdio: 'ignore' }); return true } catch { return false }
}

const lines = s => s.split('\n').filter(Boolean)

/** One commit: whether it is a bot data commit, why it is major (if it is), and its age. */
function inspect(repo, sha, now) {
  const subject = git(repo, ['log', '-1', '--format=%s', sha])
  const message = git(repo, ['log', '-1', '--format=%B', sha])
  const files = lines(git(repo, ['diff-tree', '--no-commit-id', '--no-renames', '--name-only', '-r', sha]))
  const data = /^data\(auto\):/.test(subject) && files.length > 0 && files.every(f => DATA_FILES.includes(f))
  const major = []
  const tag = `${sha.slice(0, 7)} (${subject})`
  if (TRAILER.test(message)) major.push(`${tag} is marked Owner-Review: required`)
  for (const f of files) if (PROTECTED.some(p => p.test(f))) major.push(`${tag} changes protected path ${f}`)
  const workflowDiff = git(repo, ['show', '--no-renames', '-U0', '--format=', sha, '--', '.github'])
  if (workflowDiff.split('\n').some(l => l.startsWith('+') && SECRET.test(l))) major.push(`${tag} makes a workflow use a repository secret`)
  const ageHours = (now - Number(git(repo, ['log', '-1', '--format=%ct', sha])) * 1000) / 3600000
  return { sha, subject, data, major, ageHours, soak: data ? SOAK_HOURS.data : SOAK_HOURS.other }
}

/**
 * Picks the newest commit on preview that may go live. Commits are taken oldest first; the
 * candidate is the last one before the first commit that is major or has not soaked. So a held
 * or unsoaked commit stops only itself and what follows it, never the work already ripe before it.
 */
export function decide(repo, { base = 'origin/main', head = 'HEAD', now = Date.now() } = {}) {
  const headSha = git(repo, ['rev-parse', head])
  if (!isAncestor(repo, base, head)) return { action: 'fail', sha: headSha, reasons: [`${base} is not an ancestor of ${head}; a fast-forward is impossible`] }
  const range = lines(git(repo, ['rev-list', '--reverse', `${base}..${head}`]))
  if (!range.length) return { action: 'none', sha: headSha, reasons: ['main already matches preview'] }

  const merges = lines(git(repo, ['rev-list', '--merges', `${base}..${head}`]))
  if (merges.length) return { action: 'hold', sha: headSha, reasons: merges.map(m => `${m.slice(0, 7)} is a merge commit; preview is kept linear, so the owner must look`), commits: range.length, waiting: range.length }

  let candidate = null, dataOnly = true, stop = null
  for (const sha of range) {
    const c = inspect(repo, sha, now)
    if (c.major.length) { stop = { action: 'hold', reasons: c.major }; break }
    if (c.ageHours < c.soak) { stop = { action: 'wait', reasons: [`${sha.slice(0, 7)} (${c.subject}) is ${Math.round(c.ageHours * 10) / 10} h old; ${c.soak} h soak required`] }; break }
    candidate = sha
    dataOnly &&= c.data
  }
  const waiting = range.length - (candidate ? range.indexOf(candidate) + 1 : 0)
  if (!candidate) return { action: stop.action, sha: headSha, reasons: stop.reasons, commits: range.length, waiting }
  const reasons = [`${range.indexOf(candidate) + 1} of ${range.length} commits ready${dataOnly ? ' (certified data only)' : ''}`]
  if (stop) reasons.push(`still waiting: ${stop.reasons.join('; ')}`)
  return { action: 'promote', sha: candidate, dataOnly, reasons, commits: range.length, waiting, heldBehind: stop?.action ?? null }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const result = decide(process.cwd())
  console.log(JSON.stringify(result, null, 2))
  if (process.env.GITHUB_OUTPUT) {
    appendFileSync(process.env.GITHUB_OUTPUT, `action=${result.action}\nsha=${result.sha}\ndata_only=${result.dataOnly ?? false}\nheld_behind=${result.heldBehind ?? ''}\n`)
    appendFileSync(process.env.GITHUB_OUTPUT, `reasons<<EOF\n${result.reasons.map(r => `- ${r}`).join('\n')}\nEOF\n`)
  }
}
