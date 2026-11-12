// Pipeline doctor: the deterministic half of the repair loop.
//
// Every 10 minutes it reads the day's collector, gate and publisher runs and the
// live data, sorts the day into one known case, and takes at most one safe,
// bounded step. Anything it cannot fix safely is handed to the repair step
// (a Claude scheduled task, docs/reference/repair-loop.md), which runs the same
// diagnosis through doctor-cli.mjs, reads the logs and fixes the cause.
//
// It keeps no state of its own. Every limit is counted from GitHub's run list,
// so a crashed or repeated call can never act twice: a step it took is visible
// as a run the next time it looks.
import { TIMER_TITLE, LOGIN_ANNOTATION, dispatch } from './core.js'

const HOUR = 3600000
const MIN = 60000

export const CASES = {
  OK: 'Today\'s collection is live.',
  WAITING: 'A step is running or still inside its normal window.',
  COLLECT_TIMEOUT: 'The collection hit its time limit and saved nothing.',
  COLLECT_FAILED: 'The collection failed before it finished.',
  NO_COLLECTION: 'No collection has started today.',
  LOGIN_EXPIRED: 'The ChatGPT login used by the AI step has expired.',
  GATE_FAILED: 'The release gate refused the release (a check failed).',
  GATE_BUDGET_USED: 'Both of today\'s gate attempts are used; a collection is waiting to publish.',
  RELEASE_NOT_STARTED: 'A collection finished but no release has started.',
  PUBLISH_STORM: 'The publisher keeps starting and being refused.',
  STALE_UNEXPLAINED: 'The live data is stale and no known case explains it.',
}

// What the doctor itself may do, and what it hands on.
//   act: a bounded step the doctor takes now
//   repair: the repair step (Claude) must find and fix the cause
//   owner: only Jess can do it (for example sign in again)
export const HANDLING = {
  COLLECT_TIMEOUT: 'act', COLLECT_FAILED: 'act', NO_COLLECTION: 'act', GATE_BUDGET_USED: 'act', RELEASE_NOT_STARTED: 'act',
  LOGIN_EXPIRED: 'owner', GATE_FAILED: 'repair', PUBLISH_STORM: 'repair', STALE_UNEXPLAINED: 'repair',
  OK: 'none', WAITING: 'none',
}

export function doctorConfig(cfg) {
  return {
    publisher: cfg.PUBLISHER_FILE ?? 'subscription-publisher.yml',
    gate: cfg.GATE_FILE ?? 'market-release-gate.yml',
    collectLimit: Number(cfg.COLLECT_LIMIT_MINUTES || 90),
    gatesPerDay: Number(cfg.GATES_PER_DAY || 2),
    // One extra collection a day at most, on top of the 05:17 timer start.
    collectRetries: Number(cfg.COLLECT_RETRIES_PER_DAY || 1),
    // First minute of the UTC day the doctor expects a collection to have started.
    collectBy: Number(cfg.COLLECT_BY_MINUTE || 6 * 60),
    dryRun: cfg.DOCTOR_DRY_RUN === 'true' || cfg.DOCTOR_DRY_RUN === true,
  }
}

const day = ms => new Date(ms).toISOString().slice(0, 10)
const at = s => Date.parse(s)
const trusted = run => run.event === 'schedule' || (run.event === 'workflow_dispatch' && run.display_title === TIMER_TITLE)

// Read everything the diagnosis needs. Read-only.
export async function observe(cfg, gh, fetcher = fetch, now = Date.now()) {
  const d = doctorConfig(cfg)
  const repo = cfg.GITHUB_REPO
  let liveAt = null
  try {
    const r = await fetcher(cfg.DATA_URL, { signal: AbortSignal.timeout(20000), headers: { 'cache-control': 'no-cache' } })
    if (r.ok) liveAt = at((await r.json())?.checkedAt)
  } catch { /* unreadable live data counts as stale */ }
  if (!Number.isFinite(liveAt)) liveAt = null

  const { workflow_runs: runs = [] } = await gh(`/repos/${repo}/actions/workflows/${cfg.WORKFLOW_FILE}/runs?branch=${cfg.REF}&per_page=20`)
  const collections = []
  for (const run of runs.filter(trusted)) {
    if (now - at(run.created_at) > 48 * HOUR) break
    const { jobs = [] } = await gh(`/repos/${repo}/actions/runs/${run.id}/jobs?per_page=20`)
    const job = jobs.find(j => j.name === 'collect-and-reconcile') || null
    collections.push({ id: run.id, url: run.html_url, event: run.event, title: run.display_title, created: run.created_at,
      status: run.status, conclusion: run.conclusion, job: job && { id: job.id, status: job.status, conclusion: job.conclusion,
        started: job.started_at, completed: job.completed_at } })
  }
  const newestDone = collections.find(c => c.job?.status === 'completed' && c.job.conclusion !== 'skipped')
  let loginExpired = false
  if (newestDone) {
    const notes = await gh(`/repos/${repo}/check-runs/${newestDone.job.id}/annotations?per_page=50`)
    loginExpired = notes.some(n => n.title === LOGIN_ANNOTATION)
  }
  const { workflow_runs: gateRuns = [] } = await gh(`/repos/${repo}/actions/workflows/${d.gate}/runs?branch=${cfg.REF}&event=workflow_dispatch&per_page=10`)
  const { workflow_runs: pubRuns = [] } = await gh(`/repos/${repo}/actions/workflows/${d.publisher}/runs?per_page=30`)
  // Main's commit, from its check runs (the access the timer already has).
  const { check_runs: checks = [] } = await gh(`/repos/${repo}/commits/${cfg.REF}/check-runs?per_page=1`)
  const slim = r => ({ id: r.id, url: r.html_url, event: r.event, created: r.created_at, updated: r.updated_at, status: r.status, conclusion: r.conclusion, sha: r.head_sha })
  return { now, liveAt, mainSha: checks[0]?.head_sha ?? null, collections, loginExpired, gates: gateRuns.map(slim), pubs: pubRuns.map(slim) }
}

// Pure: sort one observation into findings, each with its handling. Two tracks
// run side by side: today's collection, and the release of the newest good
// collection. Tested against replays of real days (doctor.test.js).
export function diagnose(obs, cfg = {}) {
  const d = doctorConfig(cfg)
  const { now, liveAt } = obs
  const today = day(now)
  const minuteOfDay = (now - at(today + 'T00:00:00Z')) / MIN
  const facts = []
  const findings = []
  const find = (code, extra = {}) => findings.push({ code, handling: HANDLING[code], summary: CASES[code], ...extra })

  const lastGood = obs.collections.find(c => c.job?.conclusion === 'success') || null
  const liveCurrent = !!lastGood && liveAt !== null && liveAt >= at(lastGood.job.started) - 10 * MIN
  const realToday = obs.collections.filter(c => day(at(c.created)) === today && c.job && c.job.conclusion !== 'skipped')
  const collecting = obs.collections.find(c => c.status !== 'completed')
  const gatesToday = obs.gates.filter(g => day(at(g.created)) === today)
  // The gate allows gatesPerDay attempts per code revision and twice that in
  // total each UTC day (release.py gate_budget_check, owner 2026-11-12).
  const onMain = gatesToday.filter(g => obs.mainSha && g.sha === obs.mainSha).length
  const budgetUsed = gatesToday.length >= 2 * d.gatesPerDay || onMain >= d.gatesPerDay
  const gateRunning = obs.gates.find(g => g.status !== 'completed')
  const pubRunning = obs.pubs.find(p => p.status !== 'completed')
  const newestGate = obs.gates[0] || null

  facts.push(liveAt !== null ? `Live data from ${new Date(liveAt).toISOString()}` : 'Live data unreadable')
  if (lastGood) facts.push(`Newest good collection started ${lastGood.job.started}${liveCurrent ? ' and is live' : ', not live'} (${lastGood.url})`)
  facts.push(`Gate runs today: ${gatesToday.length} of ${2 * d.gatesPerDay}, ${onMain} of ${d.gatesPerDay} on main's code`)
  if (collecting) facts.push(`Collector running (${collecting.url})`)
  if (gateRunning) facts.push(`Gate running (${gateRunning.url})`)
  if (pubRunning) facts.push(`Publisher running (${pubRunning.url})`)

  // Brake: a publisher that keeps starting and being refused is a fault itself.
  const refused = obs.pubs.filter(p => now - at(p.created) <= 2 * HOUR && p.status === 'completed' && p.conclusion === 'failure')
  if (refused.length >= 3 && !obs.gates.some(g => now - at(g.created) <= 2 * HOUR)) {
    facts.push(`${refused.length} publisher runs refused in the last 2 h with no gate run`)
    find('PUBLISH_STORM')
  }
  if (obs.loginExpired) find('LOGIN_EXPIRED')

  // Track 1: today's collection.
  const okToday = realToday.some(c => c.job.conclusion === 'success')
  const lastToday = realToday[0]
  if (!collecting && !okToday) {
    if (lastToday?.job.status === 'completed') {
      const used = (at(lastToday.job.completed) - at(lastToday.job.started)) / MIN
      facts.push(`Collection ${lastToday.url} ${lastToday.job.conclusion} after ${Math.round(used)} of ${d.collectLimit} min`)
      const timedOut = lastToday.job.conclusion === 'cancelled' && used >= d.collectLimit * 0.95
      find(timedOut ? 'COLLECT_TIMEOUT' : 'COLLECT_FAILED', { minutes: Math.round(used), run: lastToday.url })
    } else if (!realToday.length && minuteOfDay >= d.collectBy) find('NO_COLLECTION')
  }

  // Track 2: the newest good collection reaches the site.
  if (lastGood && !liveCurrent && !gateRunning && !pubRunning) {
    const doneAt = at(lastGood.job.completed)
    const gateAfter = newestGate && at(newestGate.created) >= doneAt ? newestGate : null
    const fixedSince = gateAfter && obs.mainSha && obs.mainSha !== gateAfter.sha
    if (gateAfter?.conclusion === 'failure') {
      facts.push(`Gate ${gateAfter.url} failed at ${gateAfter.updated} on ${String(gateAfter.sha).slice(0, 7)}; main is ${String(obs.mainSha).slice(0, 7)}`)
      // Same code would fail the same way: that needs a fix. New code on main
      // gets one more attempt, today if the budget allows, else after 00:00 UTC.
      if (!fixedSince) find('GATE_FAILED', { gate: gateAfter.url })
      else if (budgetUsed) find('GATE_BUDGET_USED', { gate: gateAfter.url, waitUntil: day(now + 24 * HOUR) + 'T00:05:00Z' })
      else find('GATE_BUDGET_USED', { gate: gateAfter.url, retryReady: true })
    } else if (budgetUsed) {
      find('GATE_BUDGET_USED', { waitUntil: day(now + 24 * HOUR) + 'T00:05:00Z' })
    } else if (!gateAfter && now - doneAt >= 30 * MIN) {
      facts.push(`Collection finished ${lastGood.job.completed}; no gate run since`)
      find('RELEASE_NOT_STARTED')
    }
  }

  const stale = liveAt === null || now - liveAt > 30 * HOUR
  if (!findings.length && stale && !collecting && !gateRunning && !pubRunning) find('STALE_UNEXPLAINED')
  const busy = collecting || gateRunning || pubRunning || (lastGood && !liveCurrent)
  const code = findings[0]?.code ?? (busy ? 'WAITING' : 'OK')
  return { code, handling: HANDLING[code], summary: CASES[code], findings, facts }
}

// The step for each finding, with its limit counted from GitHub's own runs.
export function plan(finding, obs, cfg = {}) {
  const d = doctorConfig(cfg)
  const today = day(obs.now)
  const minuteOfDay = (obs.now - at(today + 'T00:00:00Z')) / MIN
  switch (finding.code) {
    case 'COLLECT_TIMEOUT':
    case 'COLLECT_FAILED':
    case 'NO_COLLECTION': {
      // The 05:17 timer start is the first; the doctor may add collectRetries more.
      const starts = obs.collections.filter(c => c.event === 'workflow_dispatch' && c.title === TIMER_TITLE && day(at(c.created)) === today)
      const allowed = 1 + d.collectRetries
      if (obs.loginExpired) return { step: 'none', why: 'A collection cannot succeed until the owner signs in again', escalate: 'owner' }
      if (starts.length >= allowed) return { step: 'none', why: `${starts.length} timer collections already started today; the repair step takes over`, escalate: 'repair' }
      // A retry that would run into the next day's 05:17 start is pointless.
      if (minuteOfDay > 22 * 60) return { step: 'none', why: 'Too late in the UTC day to retry; tomorrow\'s timer start runs', escalate: 'repair' }
      // A repeat of yesterday's timeout means the limit or the work is wrong: retry, and ask for a fix too.
      const repeat = finding.code === 'COLLECT_TIMEOUT' && obs.collections.some(c => day(at(c.created)) === day(obs.now - 24 * HOUR) &&
        c.job?.conclusion === 'cancelled' && (at(c.job.completed) - at(c.job.started)) / MIN >= d.collectLimit * 0.95)
      return { step: 'collect', why: `Start one more collection (${starts.length + 1} of ${allowed} today)`, escalate: repeat ? 'repair' : 'none' }
    }
    case 'RELEASE_NOT_STARTED':
    case 'GATE_BUDGET_USED': {
      if (finding.waitUntil) return { step: 'none', why: `Wait for the gate budget to reset at ${finding.waitUntil}`, escalate: 'none' }
      // At most one doctor start an hour and three a day; each start is visible as a run.
      const dispatched = obs.pubs.filter(p => p.event === 'workflow_dispatch' && day(at(p.created)) === today)
      if (obs.pubs.some(p => obs.now - at(p.created) < 60 * MIN)) return { step: 'none', why: 'A publisher run started in the last hour', escalate: 'none' }
      if (dispatched.length >= 3) return { step: 'none', why: 'Publisher already started 3 times today', escalate: 'repair' }
      return { step: 'publish', why: 'Start the publisher once to release the waiting collection' }
    }
    case 'LOGIN_EXPIRED': return { step: 'none', why: 'Only the owner can sign in again', escalate: 'owner' }
    case 'GATE_FAILED': case 'PUBLISH_STORM': case 'STALE_UNEXPLAINED':
      return { step: 'none', why: 'Needs a diagnosis and a code fix', escalate: 'repair' }
    default: return { step: 'none', why: 'Nothing to do', escalate: 'none' }
  }
}

export async function doctor(cfg, gh, fetcher = fetch, now = Date.now()) {
  const d = doctorConfig(cfg)
  const obs = await observe(cfg, gh, fetcher, now)
  const diagnosis = diagnose(obs, cfg)
  const steps = []
  for (const f of diagnosis.findings) {
    const p = plan(f, obs, cfg)
    f.plan = p
    if (d.dryRun || steps.includes(p.step)) continue
    if (p.step === 'collect') { const r = await dispatch(cfg, fetcher, now); f.done = r; steps.push('collect') }
    if (p.step === 'publish') {
      await gh(`/repos/${cfg.GITHUB_REPO}/actions/workflows/${d.publisher}/dispatches`, { method: 'POST', body: JSON.stringify({ ref: cfg.REF }) })
      f.done = { ok: true }; steps.push('publish')
    }
  }
  const escalate = [...new Set(diagnosis.findings.map(f => f.plan.escalate).filter(e => e && e !== 'none'))]
  return { at: new Date(now).toISOString(), ...diagnosis, escalate, dryRun: d.dryRun }
}
