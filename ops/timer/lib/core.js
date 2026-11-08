// Outside daily clock and watchdog for a static-site pipeline (D-126).
// Shared by any pipeline site (Security Market Pulse, Security Threat Pulse).
// Each site deploys its own Vercel project from this folder with its own
// environment variables: no credentials or data are shared between sites.
import { createSign } from 'node:crypto'

const API = 'https://api.github.com'
export const TIMER_TITLE = 'daily timer collection'
export const ISSUE_TITLE = 'Daily pipeline needs attention (outside watchdog)'
export const LOGIN_ANNOTATION = 'chatgpt-login'
const LOGIN_REASONS = new Set(['CHATGPT_SUBSCRIPTION_LOGIN_REQUIRED', 'CHATGPT_SIGN_IN_AGAIN'])
export const PROBLEMS = {
  DATA_STALE: 'The published data is older than the limit, or could not be read.',
  RUN_FAILED: 'The latest daily collector run failed.',
  NO_RECENT_RUN: 'No daily collector run has started within the limit.',
  CHATGPT_LOGIN_EXPIRED: 'The ChatGPT login used for AI extraction has expired. Sign in again with the "dedicated subscription account setup" workflow (ops/ci/bootstrap.py).',
}

export function config(env) {
  const need = ['CRON_SECRET', 'GITHUB_REPO', 'WORKFLOW_FILE', 'DATA_URL']
  const missing = need.filter(k => !env[k])
  const app = env.GITHUB_APP_ID && env.GITHUB_APP_PRIVATE_KEY
  if (!app && !env.GITHUB_TOKEN) missing.push('GITHUB_APP_ID + GITHUB_APP_PRIVATE_KEY (or GITHUB_TOKEN)')
  if (missing.length) throw new Error('TIMER_NOT_CONFIGURED: ' + missing.join(', '))
  if (!/^[\w.-]+\/[\w.-]+$/.test(env.GITHUB_REPO)) throw new Error('GITHUB_REPO_INVALID')
  // Issues (alerts, health, company requests) can live in a private repo of the
  // same owner while the pipeline repo is public. Defaults to GITHUB_REPO.
  const issuesRepo = env.ISSUES_REPO || env.GITHUB_REPO
  if (!/^[\w.-]+\/[\w.-]+$/.test(issuesRepo) || issuesRepo.split('/')[0] !== env.GITHUB_REPO.split('/')[0])
    throw new Error('ISSUES_REPO_INVALID')
  if (new URL(env.DATA_URL).protocol !== 'https:') throw new Error('DATA_URL_MUST_BE_HTTPS')
  return { ...env, ISSUES_REPO: issuesRepo, MAX_AGE_HOURS: Number(env.MAX_AGE_HOURS || 30), REF: env.WORKFLOW_REF || 'main',
           ASSIGNEE: env.ALERT_ASSIGNEE || env.GITHUB_REPO.split('/')[0] }
}

// Vercel Cron sends "Authorization: Bearer <CRON_SECRET>". Reject anything else.
export function authorized(request, secret) {
  return request.headers.get('authorization') === `Bearer ${secret}`
}

const b64url = value => Buffer.from(value).toString('base64url')

export function appJwt(appId, privateKey, now = Date.now()) {
  const iat = Math.floor(now / 1000) - 60
  const body = `${b64url(JSON.stringify({ alg: 'RS256', typ: 'JWT' }))}.${b64url(JSON.stringify({ iat, exp: iat + 540, iss: String(appId) }))}`
  const signature = createSign('RSA-SHA256').update(body).sign(privateKey.replace(/\\n/g, '\n'), 'base64url')
  return `${body}.${signature}`
}

function headers(token) {
  return { authorization: `Bearer ${token}`, accept: 'application/vnd.github+json',
           'x-github-api-version': '2022-11-28', 'user-agent': 'pipeline-timer' }
}

// A GitHub App's installation token (preferred: its issues notify the owner)
// or a fine-grained token (GitHub never notifies you of your own token's issues).
// Pass permissions to narrow the token below the app's grant (the public
// request endpoint asks for issues only).
export async function githubToken(cfg, fetcher = fetch, now = Date.now(), permissions) {
  if (!(cfg.GITHUB_APP_ID && cfg.GITHUB_APP_PRIVATE_KEY)) return cfg.GITHUB_TOKEN
  const jwt = headers(appJwt(cfg.GITHUB_APP_ID, cfg.GITHUB_APP_PRIVATE_KEY, now))
  const found = await fetcher(`${API}/repos/${cfg.GITHUB_REPO}/installation`, { headers: jwt, signal: AbortSignal.timeout(20000) })
  if (!found.ok) throw new Error('APP_NOT_INSTALLED_' + found.status)
  const { id } = await found.json()
  const issued = await fetcher(`${API}/app/installations/${id}/access_tokens`, { method: 'POST', headers: jwt, signal: AbortSignal.timeout(20000),
    body: JSON.stringify({ repositories: [...new Set([cfg.GITHUB_REPO, cfg.ISSUES_REPO || cfg.GITHUB_REPO].map(r => r.split('/')[1]))],
      ...(permissions && { permissions }) }) })
  if (!issued.ok) throw new Error('APP_TOKEN_FAILED_' + issued.status)
  return (await issued.json()).token
}

export function client(token, fetcher) {
  return async (path, init = {}) => {
    const r = await fetcher(path.startsWith('http') ? path : API + path,
      { ...init, headers: headers(token), signal: AbortSignal.timeout(20000) })
    if (!r.ok) throw new Error(`GITHUB_${init.method || 'GET'}_${r.status}`)
    return r.status === 204 ? null : r.json()
  }
}

export async function dispatch(cfg, fetcher = fetch, now = Date.now()) {
  const token = await githubToken(cfg, fetcher, now)
  const url = `${API}/repos/${cfg.GITHUB_REPO}/actions/workflows/${cfg.WORKFLOW_FILE}/dispatches`
  const r = await fetcher(url, { method: 'POST', headers: headers(token),
    body: JSON.stringify({ ref: cfg.REF, inputs: { timer: 'true' } }), signal: AbortSignal.timeout(20000) })
  return { ok: r.status === 204 || r.status === 200, status: r.status }
}

// Age in hours of the published data, from its checkedAt field. null = unreadable.
export function dataAgeHours(body, now = Date.now()) {
  const at = Date.parse(body?.checkedAt)
  return Number.isFinite(at) ? (now - at) / 3600000 : null
}

const trusted = run => run.event === 'schedule' || (run.event === 'workflow_dispatch' && run.display_title === TIMER_TITLE)
const collectJob = jobs => jobs.find(j => j.name === 'collect-and-reconcile')

// Newest daily-timer run that actually collected (backups that skipped because
// the day already ran are passed over), with its collection job.
async function latestCollection(cfg, gh) {
  const { workflow_runs: runs } = await gh(`/repos/${cfg.GITHUB_REPO}/actions/workflows/${cfg.WORKFLOW_FILE}/runs?branch=${cfg.REF}&per_page=20`)
  for (const run of runs.filter(trusted)) {
    const { jobs } = await gh(`/repos/${cfg.GITHUB_REPO}/actions/runs/${run.id}/jobs?per_page=20`)
    const job = collectJob(jobs)
    if (run.status === 'completed' && run.conclusion === 'success' && job?.conclusion === 'skipped') continue
    return { run, job }
  }
  return null
}

export async function inspect(cfg, gh, fetcher = fetch, now = Date.now()) {
  const problems = []
  let age = null
  try {
    const r = await fetcher(cfg.DATA_URL, { signal: AbortSignal.timeout(20000), headers: { 'cache-control': 'no-cache' } })
    if (r.ok) age = dataAgeHours(await r.json(), now)
  } catch { /* unreachable or unreadable data is stale, never healthy */ }
  if (age === null || age < 0 || age > cfg.MAX_AGE_HOURS) problems.push('DATA_STALE')
  const latest = await latestCollection(cfg, gh)
  const started = latest && Date.parse(latest.run.created_at)
  if (!latest || !(now - started <= cfg.MAX_AGE_HOURS * 3600000)) problems.push('NO_RECENT_RUN')
  if (latest?.run.status === 'completed' && latest.run.conclusion !== 'success') problems.push('RUN_FAILED')
  if (latest?.job && latest.job.status === 'completed') {
    const notes = await gh(`/repos/${cfg.GITHUB_REPO}/check-runs/${latest.job.id}/annotations?per_page=50`)
    if (notes.some(n => n.title === LOGIN_ANNOTATION && LOGIN_REASONS.has(String(n.message).trim()))) problems.push('CHATGPT_LOGIN_EXPIRED')
  }
  return { problems, age, runUrl: latest?.run.html_url ?? null }
}

export async function watch(cfg, fetcher = fetch, now = Date.now()) {
  const gh = client(await githubToken(cfg, fetcher, now), fetcher)
  const found = await inspect(cfg, gh, fetcher, now)
  const base = `/repos/${cfg.ISSUES_REPO || cfg.GITHUB_REPO}/issues`
  const open = (await gh(`${base}?state=open&per_page=100`)).find(i => i.title === ISSUE_TITLE && !i.pull_request)
  const lines = found.problems.map(p => `- ${PROBLEMS[p]}`)
  const facts = `Data age: ${found.age === null ? 'unreadable' : found.age.toFixed(1) + ' hours'} (limit ${cfg.MAX_AGE_HOURS}). ` +
    `Latest run: ${found.runUrl ?? 'none found'}. Checked ${new Date(now).toISOString()} from Vercel, outside GitHub Actions.`
  if (found.problems.length) {
    const body = `${lines.join('\n')}\n\n${facts}\n\nThis issue closes itself once everything is healthy.`
    if (open) await gh(`${base}/${open.number}`, { method: 'PATCH', body: JSON.stringify({ body }) })
    else await gh(base, { method: 'POST', body: JSON.stringify({ title: ISSUE_TITLE, body, assignees: [cfg.ASSIGNEE] }) })
    return { ...found, action: open ? 'updated' : 'opened' }
  }
  if (open) {
    await gh(`${base}/${open.number}/comments`, { method: 'POST', body: JSON.stringify({ body: 'Recovered. ' + facts }) })
    await gh(`${base}/${open.number}`, { method: 'PATCH', body: JSON.stringify({ state: 'closed', state_reason: 'completed' }) })
    return { ...found, action: 'closed' }
  }
  return { ...found, action: 'none' }
}
