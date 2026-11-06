// One readable health summary for a pipeline site (outside GitHub Actions).
// Every hour it measures the live site, the daily clock, collection, publishing,
// alerts, disk and Actions minutes, then rewrites one GitHub issue whose title
// says the overall state ("Site health: OK", "Site health: 1 failing").
// Editing the issue is silent; a comment (which notifies the owner) is posted
// only when a check newly goes bad, and once when everything recovers.
import { TIMER_TITLE, LOGIN_ANNOTATION, ISSUE_TITLE } from './core.js'

export const HEALTH_PREFIX = 'Site health:'
export const DISK_ANNOTATION = 'evidence-disk'
const HOUR = 3600000
const GB = 1e9
const STATE_RE = /<!-- health-state (\{.*?\}) -->/

export function healthConfig(cfg) {
  return {
    site: new URL(cfg.DATA_URL).origin,
    publisher: cfg.PUBLISHER_FILE ?? 'subscription-publisher.yml',
    funding: cfg.FUNDING_FILE ?? 'funding-weekly.yml',
    observer: cfg.OBSERVER_FILE ?? 'freshness.yml',
    livePaths: (cfg.LIVE_PATHS ?? '/coverage/,/data/,/funding/,/llms.txt,/tracker.json,/events.json,/og.png,/favicon.svg')
      .split(',').map(s => s.trim()).filter(s => s.startsWith('/')),
    requestUrl: cfg.REQUEST_URL ?? 'https://market-pipeline-timer.vercel.app/api/request',
    jobLimitMinutes: Number(cfg.COLLECT_LIMIT_MINUTES || 35),
    minutesLimit: Number(cfg.ACTIONS_MINUTES_LIMIT || 3000),
    usdPerMinute: Number(cfg.ACTIONS_USD_PER_MINUTE || 0.008),
    budgetUsd: Number(cfg.ACTIONS_BUDGET_USD || 5),
  }
}

const fmtTime = ms => new Date(ms).toISOString().slice(0, 16).replace('T', ' ') + ' UTC'
const ago = (now, ms) => {
  const h = (now - ms) / HOUR
  return h < 1 ? `${Math.max(0, Math.round(h * 60))} min ago` : h < 48 ? `${h.toFixed(1)} h ago` : `${(h / 24).toFixed(1)} days ago`
}
const minutes = (a, b) => (Date.parse(b) - Date.parse(a)) / 60000

async function getJson(fetcher, url) {
  try {
    const r = await fetcher(url, { signal: AbortSignal.timeout(20000), headers: { 'cache-control': 'no-cache' } })
    return r.ok ? await r.json() : null
  } catch { return null }
}

async function getStatus(fetcher, url) {
  try {
    const r = await fetcher(url, { signal: AbortSignal.timeout(20000) })
    return r.status
  } catch { return 0 }
}

// Newest run of a workflow whose named job actually ran (skipped no-op runs are passed over).
async function latestJob(gh, repo, file, jobName, { branch, keep = () => true, limit = 15 } = {}) {
  const q = `per_page=${limit}` + (branch ? `&branch=${branch}` : '')
  const { workflow_runs: runs = [] } = await gh(`/repos/${repo}/actions/workflows/${file}/runs?${q}`)
  for (const run of runs.filter(keep)) {
    const { jobs = [] } = await gh(`/repos/${repo}/actions/runs/${run.id}/jobs?per_page=20`)
    const job = jobs.find(j => j.name === jobName)
    if (!job || job.conclusion === 'skipped') continue
    return { run, job, runs }
  }
  return { run: null, job: null, runs }
}

const trusted = run => run.event === 'schedule' || (run.event === 'workflow_dispatch' && run.display_title === TIMER_TITLE)

export function parseDisk(message) {
  const archive = /archive=(\d+)/.exec(message || '')
  const free = /free=(\d+)/.exec(message || '')
  return archive && free ? { archive: Number(archive[1]), free: Number(free[1]) } : null
}

// Rough Actions minutes for this repository this calendar month, from run times.
async function monthMinutes(gh, repo, now) {
  const d = new Date(now)
  const start = Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), 1)
  const days = new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth() + 1, 0)).getUTCDate()
  let used = 0, count = 0
  for (let page = 1; page <= 10; page++) {
    const { workflow_runs: runs = [] } = await gh(`/repos/${repo}/actions/runs?created=%3E%3D${new Date(start).toISOString().slice(0, 10)}&per_page=100&page=${page}`)
    for (const r of runs) {
      if (!r.run_started_at || r.status !== 'completed') continue
      used += Math.max(1, Math.ceil(minutes(r.run_started_at, r.updated_at)))
      count++
    }
    if (runs.length < 100) break
  }
  const elapsed = (now - start) / (24 * HOUR)
  const projected = elapsed >= 1 ? Math.round(used / elapsed * days) : null
  return { used, count, projected }
}

export async function assess(cfg, gh, fetcher = fetch, now = Date.now()) {
  const h = healthConfig(cfg)
  const repo = cfg.GITHUB_REPO
  const checks = []
  const add = (id, label, status, detail, how) => checks.push({ id, label, status, detail, how })
  const guard = async (id, label, how, fn) => {
    try { await fn() } catch (e) { add(id, label, 'fail', `Could not measure: ${String(e.message || e).slice(0, 120)}`, how) }
  }

  // 1. Live site answers.
  await guard('site', 'Live site answers', 'GET the home page; it must return HTTP 200.', async () => {
    const code = await getStatus(fetcher, h.site + '/')
    add('site', 'Live site answers', code === 200 ? 'ok' : 'fail', code === 200 ? 'HTTP 200' : `HTTP ${code || 'no answer'}`,
      'GET the home page; it must return HTTP 200.')
  })

  // 2. Published data is fresh.
  const coverage = await getJson(fetcher, cfg.DATA_URL)
  const liveAt = Date.parse(coverage?.checkedAt)
  {
    const how = `Read checkedAt in ${new URL(cfg.DATA_URL).pathname} on the live site. Warn past 26 h, fail past ${cfg.MAX_AGE_HOURS} h (collection is daily).`
    if (!Number.isFinite(liveAt)) add('data', 'Live data is fresh', 'fail', 'Live coverage file is missing or unreadable', how)
    else {
      const age = (now - liveAt) / HOUR
      const intake = Number.isInteger(coverage.successfulTasks) && Number.isInteger(coverage.requiredTasks)
        ? `; ${coverage.successfulTasks} of ${coverage.requiredTasks} source checks succeeded` : ''
      add('data', 'Live data is fresh', age > cfg.MAX_AGE_HOURS || age < -1 ? 'fail' : age > 26 ? 'warn' : 'ok',
        `Data from ${fmtTime(liveAt)}, ${ago(now, liveAt)}${intake}`, how)
    }
  }

  // 3. The daily clock fired.
  let collectorRuns = []
  await guard('timer', 'Daily clock fired', 'Newest collector run started by the outside timer must be under 25 h old.', async () => {
    const { workflow_runs: runs = [] } = await gh(`/repos/${repo}/actions/workflows/${cfg.WORKFLOW_FILE}/runs?branch=${cfg.REF}&per_page=20`)
    collectorRuns = runs
    const timer = runs.find(r => r.event === 'workflow_dispatch' && r.display_title === TIMER_TITLE)
    const backup = runs.find(r => r.event === 'schedule')
    const t = timer && Date.parse(timer.created_at)
    add('timer', 'Daily clock fired', t && now - t <= 25 * HOUR ? 'ok' : 'fail',
      (timer ? `Timer start ${fmtTime(t)} (${ago(now, t)})` : 'No timer start found') +
      (backup ? `; GitHub backup ${ago(now, Date.parse(backup.created_at))}` : ''),
      'Newest collector run started by the outside timer must be under 25 h old.')
  })

  // 4. Collection succeeded inside its time limit. 5. ChatGPT login. 6. Disk.
  let lastGoodCollection = null
  await guard('collect', 'Collection succeeded', 'Newest daily run that collected', async () => {
    const how = `Newest daily collector run that really collected. Fail if it failed, was cancelled or is over ${cfg.MAX_AGE_HOURS} h old; warn when it used over 85% of the ${h.jobLimitMinutes}-minute limit.`
    const { run, job, runs } = await latestJob(gh, repo, cfg.WORKFLOW_FILE, 'collect-and-reconcile', { branch: cfg.REF, keep: trusted })
    for (const r of runs.filter(trusted)) {
      if (r.conclusion !== 'success') continue
      const { jobs = [] } = r.id === run?.id ? { jobs: [job] } : await gh(`/repos/${repo}/actions/runs/${r.id}/jobs?per_page=20`)
      const j = jobs.find(x => x?.name === 'collect-and-reconcile')
      if (j?.conclusion === 'success') { lastGoodCollection = { run: r, job: j }; break }
    }
    if (!job) { add('collect', 'Collection succeeded', 'fail', 'No collection run found', how); return }
    const started = Date.parse(job.started_at || run.created_at)
    const link = `[run](${run.html_url})`
    if (job.status !== 'completed') {
      add('collect', 'Collection succeeded', 'ok', `Running now, ${Math.round((now - started) / 60000)} of ${h.jobLimitMinutes} min used (${link})`, how)
    } else {
      const used = minutes(job.started_at, job.completed_at)
      const share = `${Math.round(used)} of ${h.jobLimitMinutes} min`
      const old = now - started > cfg.MAX_AGE_HOURS * HOUR
      const status = job.conclusion !== 'success' || old ? 'fail' : used > h.jobLimitMinutes * 0.85 ? 'warn' : 'ok'
      add('collect', 'Collection succeeded', status,
        `${job.conclusion === 'success' ? 'Succeeded' : job.conclusion === 'cancelled' ? 'Cancelled (time limit or stop)' : 'Failed'} ${ago(now, started)}, ${share} (${link})`, how)
    }
    let notes = []
    if (job.status === 'completed') notes = await gh(`/repos/${repo}/check-runs/${job.id}/annotations?per_page=50`)
    const expired = notes.some(n => n.title === LOGIN_ANNOTATION)
    add('login', 'ChatGPT login works', expired ? 'fail' : 'ok', expired ? 'The last collection reported the login expired' : 'No expired-login flag on the last collection',
      'The collector writes a chatgpt-login annotation when the model step reports the login expired.')
    const disk = parseDisk(notes.find(n => n.title === DISK_ANNOTATION)?.message)
    const diskHow = 'The collector writes an evidence-disk annotation with the restored evidence size and the runner free space at the end of collection. Warn under 6 GB free, fail under 3 GB.'
    if (!disk) add('disk', 'Runner disk has room', 'none', 'Not measured yet; the next collection records it', diskHow)
    else add('disk', 'Runner disk has room', disk.free < 3 * GB ? 'fail' : disk.free < 6 * GB ? 'warn' : 'ok',
      `Evidence ${(disk.archive / GB).toFixed(2)} GB; ${(disk.free / GB).toFixed(1)} GB free on the runner`, diskHow)
  })

  // 7. Publisher released.
  await guard('publish', 'Publisher released', 'Newest publisher run that really published', async () => {
    const how = 'Newest publisher run whose publish job ran (callbacks that skip are passed over). Fail if it failed or refused.'
    const { run, job } = await latestJob(gh, repo, h.publisher, 'publish', { branch: cfg.REF })
    if (!job) { add('publish', 'Publisher released', 'fail', 'No publish run found', how); return }
    const at = Date.parse(job.started_at || run.created_at)
    const status = job.status !== 'completed' ? 'ok' : job.conclusion === 'success' ? 'ok' : 'fail'
    const word = job.status !== 'completed' ? 'Running now' : job.conclusion === 'success' ? 'Released' : 'Failed or refused'
    add('publish', 'Publisher released', status, `${word} ${ago(now, at)} ([run](${run.html_url}))`, how)
  })

  // 8. The last good collection reached the live site.
  {
    const how = 'The live checkedAt must be no older than the start of the newest successful collection, once 3 h have passed since it finished.'
    if (!lastGoodCollection) add('delivered', 'Latest collection is live', 'none', 'No successful collection to compare', how)
    else {
      const startedAt = Date.parse(lastGoodCollection.job.started_at)
      const doneAt = Date.parse(lastGoodCollection.job.completed_at)
      const live = Number.isFinite(liveAt) && liveAt >= startedAt - 10 * 60000
      const status = live ? 'ok' : now - doneAt > 3 * HOUR ? 'fail' : 'warn'
      add('delivered', 'Latest collection is live', status,
        live ? `Collection of ${fmtTime(startedAt)} is on the site` : `Collected ${ago(now, doneAt)}, site still shows ${Number.isFinite(liveAt) ? fmtTime(liveAt) : 'nothing'}`, how)
    }
  }

  // 9. GitHub-side observer still runs (catches Actions being stopped, for example by billing).
  await guard('observer', 'GitHub Actions is running', 'GitHub-side watchdog run age', async () => {
    const { workflow_runs: runs = [] } = await gh(`/repos/${repo}/actions/workflows/${h.observer}/runs?per_page=1`)
    const r = runs[0]
    const at = r && Date.parse(r.created_at)
    add('observer', 'GitHub Actions is running', at && now - at <= 9 * HOUR ? 'ok' : at && now - at <= 14 * HOUR ? 'warn' : 'fail',
      r ? `GitHub-side watchdog ran ${ago(now, at)}` : 'GitHub-side watchdog never ran',
      'The GitHub-side watchdog is scheduled every 6 h, and GitHub often starts schedules hours late. Warn past 9 h, fail past 14 h: Actions is then stopped or blocked (for example by billing).')
  })

  // 10. Weekly funding job.
  if (h.funding) await guard('funding', 'Weekly funding update ran', 'Newest weekly funding run', async () => {
    const how = 'Newest weekly funding run (Mondays 07:41 UTC) must have succeeded and be under 8 days old.'
    const { workflow_runs: runs = [] } = await gh(`/repos/${repo}/actions/workflows/${h.funding}/runs?per_page=5`)
    const r = runs.find(x => x.status === 'completed')
    if (!r) { add('funding', 'Weekly funding update ran', 'none', 'Has not run yet; first run is the next Monday 07:41 UTC', how); return }
    const at = Date.parse(r.created_at)
    add('funding', 'Weekly funding update ran', r.conclusion !== 'success' || now - at > 8 * 24 * HOUR ? 'fail' : 'ok',
      `${r.conclusion === 'success' ? 'Succeeded' : 'Failed'} ${ago(now, at)} ([run](${r.html_url}))`, how)
  })

  // 11. Open alerts.
  let openIssues = []
  await guard('alerts', 'No open pipeline alerts', 'Open alert issues', async () => {
    openIssues = await gh(`/repos/${repo}/issues?state=open&per_page=100`)
    const alerts = openIssues.filter(i => !i.pull_request && i.user?.type === 'Bot' && !i.title.startsWith(HEALTH_PREFIX) && !/^Company requests/.test(i.title))
    add('alerts', 'No open pipeline alerts', alerts.length ? 'warn' : 'ok',
      alerts.length ? alerts.map(i => `[#${i.number}](${i.html_url}) ${i.title}`).join('; ') : 'None open',
      'Open issues opened by the pipeline bots (each failing job opens one and closes it on recovery).')
  })

  // 12. Actions minutes against the budget.
  await guard('minutes', 'Actions minutes on budget', 'Run times this month', async () => {
    const m = await monthMinutes(gh, repo, now)
    const hardLimit = h.minutesLimit + h.budgetUsd / h.usdPerMinute
    const basis = m.projected ?? m.used
    const status = basis > hardLimit ? 'fail' : basis > h.minutesLimit * 0.8 ? 'warn' : 'ok'
    add('minutes', 'Actions minutes on budget', status,
      `About ${m.used} min used this month over ${m.count} runs` + (m.projected !== null ? `, on pace for about ${m.projected}` : '') +
      `. Included ${h.minutesLimit} + $${h.budgetUsd} budget. Other sites on the account are not counted`,
      'Sums the run times of this repository\'s completed Actions runs this month (a low estimate: GitHub rounds each job up). Warn when on pace past 80% of the included minutes, fail past included plus the budget. The exact bill is at github.com/settings/billing/usage.')
  })

  // 13. The code on main is what the live site runs.
  await guard('release', 'Live site runs current main', 'Compare live appRevision with main', async () => {
    const how = 'Compares appRevision in the live /app-release.json with the commit main ran at in its newest Actions run (the GitHub-side watchdog runs on main every 6 h). A main push publishes at the next daily release, so this warns first and fails once that commit has waited over 30 h.'
    const { workflow_runs: runs = [] } = await gh(`/repos/${repo}/actions/runs?branch=${cfg.REF}&per_page=100`)
    const head = runs[0]?.head_sha
    const firstSeen = Math.min(...runs.filter(r => r.head_sha === head).map(r => Date.parse(r.created_at)))
    const release = await getJson(fetcher, h.site + '/app-release.json')
    const live = release?.appRevision
    if (!head || !live) { add('release', 'Live site runs current main', 'warn', !live ? 'Live app-release.json has no revision' : 'No Actions run on main found', how); return }
    if (live === head) add('release', 'Live site runs current main', 'ok', `Live and main both at ${live.slice(0, 7)}`, how)
    else add('release', 'Live site runs current main', now - firstSeen > 30 * HOUR ? 'fail' : 'warn',
      `Live ${live.slice(0, 7)}, main ${head.slice(0, 7)} since ${ago(now, firstSeen)}; goes live at the next release`, how)
  })

  // 14. Shipped pages and files answer on the live site.
  if (h.livePaths.length) {
    const how = `GET each of ${h.livePaths.join(', ')} on the live site; each must return HTTP 200.`
    const codes = await Promise.all(h.livePaths.map(async p => [p, await getStatus(fetcher, h.site + p)]))
    const missing = codes.filter(([, c]) => c !== 200)
    add('pages', 'Shipped pages are live', missing.length ? 'warn' : 'ok',
      missing.length ? `Not live: ${missing.map(([p, c]) => `${p} (${c || 'no answer'})`).join(', ')}` : `All ${codes.length} answer`, how)
  }

  // 15. The company request box endpoint is deployed and configured.
  if (h.requestUrl) {
    const how = 'Sends a CORS preflight (OPTIONS, no data written) from the site origin to the request endpoint; it must answer 204.'
    let code = 0
    try { code = (await fetcher(h.requestUrl, { method: 'OPTIONS', headers: { origin: h.site }, signal: AbortSignal.timeout(20000) })).status } catch { code = 0 }
    add('request', 'Company request box answers', code === 204 ? 'ok' : 'fail', code === 204 ? 'Endpoint answers' : `Endpoint returned ${code || 'no answer'}`, how)
  }

  // 16. Coverage counts (information).
  {
    const tracker = await getJson(fetcher, h.site + '/tracker.json')
    const n = Array.isArray(tracker?.suppliers) ? tracker.suppliers.length : null
    add('coverage', 'Suppliers tracked live', 'none', n === null ? 'tracker.json is not published on the live site yet' : `${n} suppliers in /tracker.json`,
      'Counts suppliers in the live /tracker.json. Information only.')
  }

  return { checks, openIssues }
}

export function overall(checks) {
  const fail = checks.filter(c => c.status === 'fail').length
  const warn = checks.filter(c => c.status === 'warn').length
  const title = fail ? `${HEALTH_PREFIX} ${fail} failing` + (warn ? `, ${warn} warning` : '') : warn ? `${HEALTH_PREFIX} ${warn} warning` : `${HEALTH_PREFIX} OK`
  return { fail, warn, title }
}

const ICON = { ok: '🟢 OK', warn: '🟡 Warn', fail: '🔴 Fail', none: '⚪ Info' }
const cell = s => String(s).replace(/\|/g, '\\|').replace(/\n/g, ' ')

export function render(checks, now, state) {
  const { title } = overall(checks)
  const rows = checks.map(c => `| ${cell(c.label)} | ${ICON[c.status]} | ${cell(c.detail)} |`).join('\n')
  const how = checks.map(c => `- **${c.label}:** ${c.how}`).join('\n')
  return `**${title.slice(HEALTH_PREFIX.length).trim()}** as of ${fmtTime(now)}. Refreshed every hour from Vercel, outside GitHub Actions. ` +
    `This issue stays open as the status page; it comments (and notifies) only when a check newly goes bad or everything recovers.\n\n` +
    `| Check | Status | Detail |\n|---|---|---|\n${rows}\n\n<details><summary>How each check is measured</summary>\n\n${how}\n\n</details>\n\n` +
    `<!-- health-state ${JSON.stringify(state)} -->\n`
}

export function readState(body) {
  try { return JSON.parse(STATE_RE.exec(body || '')?.[1] || '{}') } catch { return {} }
}

export async function publishHealth(cfg, gh, assessed, now = Date.now()) {
  const { checks, openIssues } = assessed
  const bad = checks.filter(c => c.status === 'fail' || c.status === 'warn').map(c => `${c.id}:${c.status}`)
  const { title } = overall(checks)
  const body = render(checks, now, { bad })
  const base = `/repos/${cfg.GITHUB_REPO}/issues`
  const existing = (openIssues.length ? openIssues : await gh(`${base}?state=open&per_page=100`))
    .find(i => !i.pull_request && i.title.startsWith(HEALTH_PREFIX))
  if (!existing) {
    const made = await gh(base, { method: 'POST', body: JSON.stringify({ title, body, assignees: [cfg.ASSIGNEE] }) })
    return { action: 'opened', number: made?.number, title }
  }
  const before = new Set(readState(existing.body).bad || [])
  const fresh = bad.filter(b => !before.has(b))
  await gh(`${base}/${existing.number}`, { method: 'PATCH', body: JSON.stringify({ title, body }) })
  let comment = null
  if (fresh.length) {
    const names = fresh.map(b => { const [id, s] = b.split(':'); const c = checks.find(x => x.id === id); return `- ${ICON[s]} **${c.label}:** ${c.detail}` })
    comment = `Newly bad:\n${names.join('\n')}`
  } else if (before.size && !bad.length) comment = 'All checks pass again.'
  if (comment) await gh(`${base}/${existing.number}/comments`, { method: 'POST', body: JSON.stringify({ body: comment }) })
  return { action: comment ? 'updated+commented' : 'updated', number: existing.number, title }
}

export async function health(cfg, gh, fetcher = fetch, now = Date.now()) {
  const assessed = await assess(cfg, gh, fetcher, now)
  const published = await publishHealth(cfg, gh, assessed, now)
  return { ...published, checks: assessed.checks }
}

export { ISSUE_TITLE }
