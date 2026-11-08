import { test } from 'node:test'
import assert from 'node:assert/strict'
import { generateKeyPairSync, createVerify } from 'node:crypto'
import { appJwt, authorized, config, dataAgeHours, dispatch, githubToken, watch, ISSUE_TITLE, TIMER_TITLE, LOGIN_ANNOTATION } from './core.js'

const env = { CRON_SECRET: 's', GITHUB_TOKEN: 't', GITHUB_REPO: 'jessepike/sec-market',
              WORKFLOW_FILE: 'subscription-collector.yml', DATA_URL: 'https://securitymarketpulse.com/daily-coverage.json' }
const NOW = Date.parse('2026-11-04T12:00:00Z')
const res = (body, status = 200) => ({ ok: status < 300, status, json: async () => body })

test('config refuses missing settings, bad repo and plain http; app or token required', () => {
  assert.throws(() => config({}), /TIMER_NOT_CONFIGURED/)
  assert.throws(() => config({ ...env, GITHUB_TOKEN: '' }), /GITHUB_APP_ID/)
  assert.throws(() => config({ ...env, GITHUB_REPO: 'x' }), /GITHUB_REPO_INVALID/)
  assert.throws(() => config({ ...env, DATA_URL: 'http://a.b/x' }), /HTTPS/)
  const cfg = config(env)
  assert.equal(cfg.MAX_AGE_HOURS, 30)
  assert.equal(cfg.ASSIGNEE, 'jessepike')
})

test('only the cron secret is accepted', () => {
  const req = v => ({ headers: new Headers(v ? { authorization: v } : {}) })
  assert.equal(authorized(req('Bearer s'), 's'), true)
  for (const v of [null, 'Bearer x', 's', 'bearer s']) assert.equal(authorized(req(v), 's'), false)
})

test('GitHub App JWT verifies and installation token is scoped to the one repo', async () => {
  const { privateKey, publicKey } = generateKeyPairSync('rsa', { modulusLength: 2048 })
  const pem = privateKey.export({ type: 'pkcs1', format: 'pem' }).replace(/\n/g, '\\n')
  const jwt = appJwt(123, pem, NOW)
  const [h, p, sig] = jwt.split('.')
  assert.ok(createVerify('RSA-SHA256').update(`${h}.${p}`).verify(publicKey, sig, 'base64url'))
  assert.equal(JSON.parse(Buffer.from(p, 'base64url')).iss, '123')
  const calls = []
  const fetcher = async (url, init = {}) => {
    calls.push({ url, body: init.body && JSON.parse(init.body) })
    return url.endsWith('/installation') ? res({ id: 9 }) : res({ token: 'inst' }, 201)
  }
  const token = await githubToken(config({ ...env, GITHUB_TOKEN: '', GITHUB_APP_ID: '123', GITHUB_APP_PRIVATE_KEY: pem }), fetcher, NOW)
  assert.equal(token, 'inst')
  assert.deepEqual(calls[1].body, { repositories: ['sec-market'] })
  calls.length = 0
  await githubToken(config({ ...env, GITHUB_TOKEN: '', GITHUB_APP_ID: '123', GITHUB_APP_PRIVATE_KEY: pem,
    ISSUES_REPO: 'jessepike/sec-market-private' }), fetcher, NOW)
  assert.deepEqual(calls[1].body, { repositories: ['sec-market', 'sec-market-private'] })
})

test('config keeps issues in GITHUB_REPO unless ISSUES_REPO names a repo of the same owner', () => {
  assert.equal(config(env).ISSUES_REPO, 'jessepike/sec-market')
  assert.equal(config({ ...env, ISSUES_REPO: 'jessepike/sec-market-private' }).ISSUES_REPO, 'jessepike/sec-market-private')
  assert.throws(() => config({ ...env, ISSUES_REPO: 'someone/else' }), /ISSUES_REPO_INVALID/)
})

test('watch writes its alert issue to ISSUES_REPO', async () => {
  const urls = []
  const fetcher = async (url, init = {}) => {
    urls.push(url)
    if (url.includes('/actions/workflows/')) return res({ workflow_runs: [] })
    if (url.includes('daily-coverage')) return res({ checkedAt: new Date(NOW).toISOString() })
    if (url.endsWith('/issues?state=open&per_page=100')) return res([])
    return res({ number: 1 }, 201)
  }
  await watch(config({ ...env, ISSUES_REPO: 'jessepike/sec-market-private' }), fetcher, NOW)
  const issueCalls = urls.filter(u => u.includes('/issues'))
  assert.ok(issueCalls.length > 0)
  assert.ok(issueCalls.every(u => u.includes('/repos/jessepike/sec-market-private/issues')))
})

test('dispatch posts timer=true on main to the collector workflow', async () => {
  let call
  const r = await dispatch(config(env), async (url, init) => { call = { url, init }; return { status: 204 } })
  assert.equal(r.ok, true)
  assert.equal(call.url, 'https://api.github.com/repos/jessepike/sec-market/actions/workflows/subscription-collector.yml/dispatches')
  assert.deepEqual(JSON.parse(call.init.body), { ref: 'main', inputs: { timer: 'true' } })
  assert.equal((await dispatch(config(env), async () => ({ status: 403 }))).ok, false)
})

test('data age comes from checkedAt; unreadable is null', () => {
  assert.equal(dataAgeHours({ checkedAt: '2026-11-04T06:00:00Z' }, NOW), 6)
  assert.equal(dataAgeHours({}, NOW), null)
})

const FRESH = { checkedAt: '2026-11-04T05:40:00Z' }
const run = (id, extra = {}) => ({ id, event: 'workflow_dispatch', display_title: TIMER_TITLE, status: 'completed',
  conclusion: 'success', created_at: '2026-11-04T05:17:30Z', html_url: `https://github.com/r/${id}`, ...extra })
const job = (id, extra = {}) => ({ jobs: [{ id: id * 10, name: 'collect-and-reconcile', status: 'completed', conclusion: 'success', ...extra }] })

function fakeGitHub({ data = FRESH, runs = [run(1)], jobs = { 1: job(1) }, annotations = {}, openIssues = [] }) {
  const calls = []
  const fetcher = async (url, init = {}) => {
    calls.push({ url, method: init.method || 'GET', body: init.body && JSON.parse(init.body) })
    if (url === env.DATA_URL) { if (data instanceof Error) throw data; return res(data) }
    if (url.includes('/workflows/') && url.includes('/runs?')) return res({ workflow_runs: runs })
    const j = url.match(/\/actions\/runs\/(\d+)\/jobs/); if (j) return res(jobs[j[1]] || { jobs: [] })
    const a = url.match(/\/check-runs\/(\d+)\/annotations/); if (a) return res(annotations[a[1]] || [])
    if (url.includes('/issues?state=open')) return res(openIssues)
    return res({ number: 5 }, 201)
  }
  return { fetcher, calls, writes: () => calls.filter(c => c.method !== 'GET') }
}

test('healthy: fresh data, successful timer run, no login problem, nothing written', async () => {
  const gh = fakeGitHub({})
  const r = await watch(config(env), gh.fetcher, NOW)
  assert.deepEqual(r.problems, [])
  assert.equal(gh.writes().length, 0)
})

test('stale or unreachable data opens one issue assigned to the owner', async () => {
  for (const data of [{ checkedAt: '2026-11-02T00:00:00Z' }, {}, new Error('down')]) {
    const gh = fakeGitHub({ data })
    const r = await watch(config(env), gh.fetcher, NOW)
    assert.deepEqual(r.problems, ['DATA_STALE'])
    const [created] = gh.writes()
    assert.equal(created.body.title, ISSUE_TITLE)
    assert.deepEqual(created.body.assignees, ['jessepike'])
  }
})

test('failed run, missing run and plain manual dispatches are detected', async () => {
  assert.ok((await watch(config(env), fakeGitHub({ runs: [run(1, { conclusion: 'failure' })] }).fetcher, NOW)).problems.includes('RUN_FAILED'))
  assert.ok((await watch(config(env), fakeGitHub({ runs: [] }).fetcher, NOW)).problems.includes('NO_RECENT_RUN'))
  const manual = fakeGitHub({ runs: [run(1, { display_title: 'bounded subscription collector' })] })
  assert.ok((await watch(config(env), manual.fetcher, NOW)).problems.includes('NO_RECENT_RUN'))
  const old = fakeGitHub({ runs: [run(1, { created_at: '2026-11-02T05:17:00Z' })] })
  assert.ok((await watch(config(env), old.fetcher, NOW)).problems.includes('NO_RECENT_RUN'))
})

test('a skipped backup start is passed over for the run that collected', async () => {
  const gh = fakeGitHub({ runs: [run(2, { event: 'schedule', display_title: 'bounded subscription collector' }), run(1, { conclusion: 'failure' })],
                          jobs: { 2: job(2, { conclusion: 'skipped' }), 1: job(1, { conclusion: 'failure' }) } })
  assert.ok((await watch(config(env), gh.fetcher, NOW)).problems.includes('RUN_FAILED'))
})

test('ChatGPT login expiry is read from the collection job annotation', async () => {
  const gh = fakeGitHub({ annotations: { 10: [{ title: LOGIN_ANNOTATION, message: 'CHATGPT_SIGN_IN_AGAIN' }] } })
  const r = await watch(config(env), gh.fetcher, NOW)
  assert.deepEqual(r.problems, ['CHATGPT_LOGIN_EXPIRED'])
  assert.match(gh.writes()[0].body.body, /dedicated subscription account setup/)
  const other = fakeGitHub({ annotations: { 10: [{ title: LOGIN_ANNOTATION, message: 'SUBSCRIPTION_LIMIT_REACHED' }] } })
  assert.deepEqual((await watch(config(env), other.fetcher, NOW)).problems, [])
})

test('an open alert is updated while unhealthy and closed on recovery', async () => {
  const open = [{ number: 7, title: ISSUE_TITLE }, { number: 8, title: 'other' }]
  const still = fakeGitHub({ data: {}, openIssues: open })
  assert.equal((await watch(config(env), still.fetcher, NOW)).action, 'updated')
  assert.ok(still.writes().every(c => c.url.endsWith('/issues/7')))
  const ok = fakeGitHub({ openIssues: open })
  assert.equal((await watch(config(env), ok.fetcher, NOW)).action, 'closed')
  assert.ok(ok.writes().some(c => c.method === 'PATCH' && c.url.endsWith('/issues/7') && c.body.state === 'closed'))
})
