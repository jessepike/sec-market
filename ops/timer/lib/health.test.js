import { test } from 'node:test'
import assert from 'node:assert/strict'
import { assess, finishGate, publishHealth, overall, parseDisk, readState, HEALTH_PREFIX } from './health.js'

const NOW = Date.parse('2026-11-06T12:00:00Z')
const MAIN = 'a'.repeat(40)
const iso = h => new Date(NOW - h * 3600000).toISOString()
const cfg = { GITHUB_REPO: 'o/r', WORKFLOW_FILE: 'c.yml', DATA_URL: 'https://site.test/daily-coverage.json', MAX_AGE_HOURS: 30,
              REF: 'main', ASSIGNEE: 'owner', ACTIONS_MINUTES_LIMIT: '2000', REQUEST_URL: 'https://timer.test/api/request',
              LIVE_PATHS: '/data/,/llms.txt' }

function world(over = {}) {
  const w = {
    collectConclusion: 'success', collectMinutes: 20, dataAge: 6, publish: 'success', annotations: [
      { title: 'evidence-disk', message: 'archive=2600000000 free=9000000000' }],
    issues: [], live: MAIN, pages: 200, request: 204, ...over,
  }
  const collectRun = { id: 1, event: 'workflow_dispatch', display_title: 'daily timer collection', status: 'completed',
    conclusion: w.collectConclusion, created_at: iso(7), html_url: 'https://gh/run/1' }
  const skipped = { id: 2, event: 'workflow_dispatch', display_title: 'daily timer collection', status: 'completed', conclusion: 'success', created_at: iso(1), html_url: 'https://gh/run/2' }
  const routes = {
    '/repos/o/r/actions/workflows/c.yml/runs': { workflow_runs: [skipped, collectRun] },
    '/repos/o/r/actions/runs/2/jobs': { jobs: [{ id: 20, name: 'collect-and-reconcile', conclusion: 'skipped', status: 'completed' }] },
    '/repos/o/r/actions/runs/1/jobs': { jobs: [{ id: 10, name: 'collect-and-reconcile', status: 'completed', conclusion: w.collectConclusion,
      started_at: iso(7), completed_at: new Date(Date.parse(iso(7)) + w.collectMinutes * 60000).toISOString() }] },
    '/repos/o/r/check-runs/10/annotations': w.annotations,
    '/repos/o/r/actions/workflows/subscription-publisher.yml/runs': { workflow_runs: [{ id: 3, created_at: iso(2), html_url: 'https://gh/run/3' }, { id: 4, created_at: iso(6), html_url: 'https://gh/run/4' }] },
    '/repos/o/r/actions/runs/3/jobs': { jobs: [{ name: 'publish', conclusion: 'skipped', status: 'completed' }] },
    '/repos/o/r/actions/runs/4/jobs': { jobs: [{ name: 'publish', status: 'completed', conclusion: w.publish, started_at: iso(6) }] },
    '/repos/o/r/actions/workflows/freshness.yml/runs': { workflow_runs: [{ id: 5, created_at: iso(3), html_url: 'https://gh/run/5' }] },
    '/repos/o/r/actions/runs/5/jobs': { jobs: [{ id: 50, name: 'daily-pipeline', conclusion: 'success' }, { id: 51, name: 'observer-alert', conclusion: 'success' }, { id: 52, name: 'probe', conclusion: 'skipped' }] },
    '/repos/o/r/check-runs/50/annotations': w.watchdog ?? [],
    '/repos/o/r/check-runs/51/annotations': [{ title: 'pipeline-observer', annotation_level: 'notice', message: 'completed' }],
    '/repos/o/r/actions/workflows/funding-weekly.yml/runs': { workflow_runs: [] },
    '/repos/o/r': { private: w.public ? false : true },
    '/repos/o/r/issues': w.issues,
    '/repos/o/r/actions/runs': { workflow_runs: w.runs ?? [{ status: 'completed', run_started_at: iso(5), updated_at: iso(4.9), head_sha: MAIN, created_at: iso(5), name: 'web' }] },
  }
  const writes = []
  const gh = async (path, init = {}) => {
    if (init.method) { writes.push({ path, method: init.method, body: JSON.parse(init.body) }); return { number: 99 } }
    const key = path.split('?')[0]
    if (!(key in routes)) throw new Error('unrouted ' + key)
    return routes[key]
  }
  const fetcher = async (url, init = {}) => {
    const u = new URL(url)
    if (u.host === 'timer.test') return { status: w.request, ok: w.request < 300 }
    if (u.pathname === '/daily-coverage.json') return { ok: true, status: 200, json: async () => ({ checkedAt: iso(w.dataAge), successfulTasks: 300, requiredTasks: 557 }) }
    if (u.pathname === '/app-release.json') return { ok: true, status: 200, json: async () => ({ appRevision: w.live }) }
    if (u.pathname === '/tracker.json') return { ok: true, status: 200, json: async () => ({ suppliers: new Array(74).fill({}) }) }
    if (u.pathname === '/') return { ok: true, status: 200 }
    return { ok: w.pages === 200, status: w.pages }
  }
  return { gh, fetcher, writes }
}

const byId = checks => Object.fromEntries(checks.map(c => [c.id, c]))

test('a watchdog failure annotation raises the alerts check; notices do not', async () => {
  const { gh, fetcher } = world({ watchdog: [{ title: 'pipeline-watchdog', annotation_level: 'failure', message: 'needs attention; reasons: X' }] })
  const alerts = byId((await assess(cfg, gh, fetcher, NOW)).checks).alerts
  assert.equal(alerts.status, 'warn')
  assert.match(alerts.detail, /needs attention; reasons: X/)
  const quiet = world({ watchdog: [{ title: 'pipeline-watchdog', annotation_level: 'notice', message: 'healthy' }] })
  assert.equal(byId((await assess(cfg, quiet.gh, quiet.fetcher, NOW)).checks).alerts.status, 'ok')
})

test('alert issues are read from ISSUES_REPO', async () => {
  const { gh, fetcher } = world()
  const seen = []
  const spy = async (path, init) => { seen.push(path); return path.startsWith('/repos/o/private/issues') ? [] : gh(path, init) }
  await assess({ ...cfg, ISSUES_REPO: 'o/private' }, spy, fetcher, NOW)
  assert.ok(seen.some(p => p.startsWith('/repos/o/private/issues')))
  assert.ok(!seen.some(p => p.startsWith('/repos/o/r/issues')))
})

test('a healthy pipeline is all green, skipped runs are passed over', async () => {
  const { gh, fetcher } = world()
  const { checks } = await assess(cfg, gh, fetcher, NOW)
  const c = byId(checks)
  for (const id of ['site', 'data', 'timer', 'collect', 'login', 'disk', 'publish', 'delivered', 'observer', 'alerts', 'minutes', 'release', 'pages', 'request'])
    assert.equal(c[id].status, 'ok', `${id}: ${c[id].detail}`)
  assert.match(c.collect.detail, /20 of 90 min/)
  assert.match(c.publish.detail, /run\/4/)
  assert.equal(c.funding.status, 'none')
  assert.match(c.coverage.detail, /74 suppliers/)
  assert.equal(overall(checks).title, `${HEALTH_PREFIX} OK`)
})

test('failed collection, refused publish, stale data and low disk fail', async () => {
  const { gh, fetcher } = world({ collectConclusion: 'cancelled', publish: 'failure', dataAge: 40,
    annotations: [{ title: 'evidence-disk', message: 'archive=5000000000 free=2000000000' }, { title: 'chatgpt-login', message: 'CHATGPT_SIGN_IN_AGAIN' }] })
  const c = byId((await assess(cfg, gh, fetcher, NOW)).checks)
  for (const id of ['collect', 'publish', 'data', 'disk', 'login']) assert.equal(c[id].status, 'fail', id)
  assert.match(c.collect.detail, /Cancelled/)
})

test('a slow collection near the job limit warns', async () => {
  const { gh, fetcher } = world({ collectMinutes: 80 })
  assert.equal(byId((await assess(cfg, gh, fetcher, NOW)).checks).collect.status, 'warn')
})

test('open bot alerts, a lagging release and missing pages warn; the request box failing fails', async () => {
  const { gh, fetcher } = world({ live: 'b'.repeat(40), pages: 404, request: 500,
    issues: [{ number: 21, title: 'Daily market publisher needs attention', html_url: 'u21', user: { type: 'Bot' } },
             { number: 5, title: 'Company requests from the site', html_url: 'u5', user: { type: 'Bot' } },
             { number: 6, title: 'A human issue', html_url: 'u6', user: { type: 'User' } }] })
  const c = byId((await assess(cfg, gh, fetcher, NOW)).checks)
  assert.equal(c.alerts.status, 'warn')
  assert.match(c.alerts.detail, /#21/)
  assert.doesNotMatch(c.alerts.detail, /#5|#6/)
  assert.equal(c.release.status, 'warn')
  assert.equal(c.pages.status, 'warn')
  assert.equal(c.request.status, 'fail')
})

test('the health issue is created once, then edited silently, commenting only on new problems and recovery', async () => {
  let w = world()
  let assessed = await assess(cfg, w.gh, w.fetcher, NOW)
  let r = await publishHealth(cfg, w.gh, assessed, NOW)
  assert.equal(r.action, 'opened')
  assert.equal(w.writes[0].body.title, `${HEALTH_PREFIX} OK`)
  assert.deepEqual(w.writes[0].body.assignees, ['owner'])
  const okBody = w.writes[0].body.body

  w = world({ collectConclusion: 'failure', issues: [{ number: 30, title: `${HEALTH_PREFIX} OK`, body: okBody, user: { type: 'Bot' } }] })
  assessed = await assess(cfg, w.gh, w.fetcher, NOW)
  r = await publishHealth(cfg, w.gh, assessed, NOW)
  assert.equal(r.action, 'updated+commented')
  assert.match(w.writes[0].body.title, /1 failing/)
  assert.match(w.writes[1].body.body, /Collection succeeded/)
  const badBody = w.writes[0].body.body
  assert.deepEqual(readState(badBody).bad, ['collect:fail'])

  w = world({ collectConclusion: 'failure', issues: [{ number: 30, title: `${HEALTH_PREFIX} 1 failing`, body: badBody, user: { type: 'Bot' } }] })
  r = await publishHealth(cfg, w.gh, await assess(cfg, w.gh, w.fetcher, NOW), NOW)
  assert.equal(r.action, 'updated')
  assert.equal(w.writes.length, 1)

  w = world({ issues: [{ number: 30, title: `${HEALTH_PREFIX} 1 failing`, body: badBody, user: { type: 'Bot' } }] })
  r = await publishHealth(cfg, w.gh, await assess(cfg, w.gh, w.fetcher, NOW), NOW)
  assert.equal(w.writes[1].body.body, 'All checks pass again.')
})

test('a measurement error fails that check instead of the whole report', async () => {
  const { fetcher } = world()
  const gh = async () => { throw new Error('GITHUB_GET_500') }
  const { checks } = await assess(cfg, gh, fetcher, NOW)
  assert.equal(byId(checks).timer.status, 'fail')
  assert.match(byId(checks).timer.detail, /GITHUB_GET_500/)
  assert.equal(byId(checks).site.status, 'ok')
})

test('disk annotation parsing', () => {
  assert.deepEqual(parseDisk('archive=1 free=2'), { archive: 1, free: 2 })
  assert.equal(parseDisk('nope'), null)
})

test('Actions counts as stopped only when no workflow at all has started a run for 26 h', async () => {
  const { fetcher } = world()
  const base = world().gh
  const gh = (age) => async (path, init) => path.startsWith('/repos/o/r/actions/runs?')
    ? { workflow_runs: [{ status: 'completed', run_started_at: iso(age), updated_at: iso(age), head_sha: MAIN, created_at: iso(age), name: 'x' }] }
    : base(path, init)
  const status = async age => byId((await assess(cfg, gh(age), fetcher, NOW)).checks).observer.status
  assert.equal(await status(12), 'ok')
  assert.equal(await status(20), 'warn')
  assert.equal(await status(30), 'fail')
})

test('a fix reaching main after a failed gate starts the publisher once', async () => {
  const run = async ({ conclusion = 'failure', sha = 'new', commitAge = 0.5, pubAge = 1, pubSha = 'old', checkAge = commitAge } = {}) => {
    const writes = []
    const gh = async (path, init = {}) => {
      if (init.method) { writes.push({ path, body: JSON.parse(init.body) }); return null }
      if (path.includes('market-release-gate.yml/runs')) return { workflow_runs: [{ id: 7, status: 'completed', conclusion, head_sha: 'old', updated_at: iso(2) }] }
      if (path.includes('subscription-publisher.yml/runs')) return { workflow_runs: [{ created_at: iso(pubAge), head_sha: pubSha }] }
      if (path === '/repos/o/r/commits/main/check-runs?per_page=100') return { check_runs: [{ head_sha: sha, completed_at: iso(commitAge + 0.1) }, { head_sha: sha, completed_at: iso(checkAge) }] }
      throw new Error('unrouted ' + path)
    }
    return { r: await finishGate(cfg, gh, NOW), writes }
  }
  const fixed = await run()
  assert.equal(fixed.r.nudged, true)
  assert.deepEqual(fixed.writes, [{ path: '/repos/o/r/actions/workflows/subscription-publisher.yml/dispatches', body: { ref: 'main' } }])
  for (const [opts, why] of [[{ conclusion: 'success' }, 'gate passed'], [{ sha: 'old' }, 'main unchanged'],
    [{ commitAge: 3 }, 'main CI finished before the failure'], [{ pubAge: 0.2, pubSha: 'new' }, 'publisher already ran for this commit'],
    [{ pubAge: 0.2, pubSha: 'new', checkAge: 0.05 }, 'the publisher run itself added newer check runs to the commit']])
    assert.equal((await run(opts)).writes.length, 0, why)
})

test('a finished gate with no publisher run after it gets one started, once', async () => {
  const gate = (age, status = 'completed') => ({ id: 7, status, updated_at: iso(age) })
  const run = async (g, pubAge) => {
    const writes = []
    const gh = async (path, init = {}) => {
      if (init.method) { writes.push({ path, body: JSON.parse(init.body) }); return null }
      if (path.includes('market-release-gate.yml/runs')) return { workflow_runs: g ? [g] : [] }
      if (path.includes('subscription-publisher.yml/runs')) return { workflow_runs: pubAge == null ? [] : [{ created_at: iso(pubAge) }] }
      throw new Error('unrouted ' + path)
    }
    return { r: await finishGate(cfg, gh, NOW), writes }
  }
  const missed = await run(gate(1), 2)
  assert.equal(missed.r.nudged, true)
  assert.deepEqual(missed.writes, [{ path: '/repos/o/r/actions/workflows/subscription-publisher.yml/dispatches', body: { ref: 'main' } }])
  for (const [g, pub, why] of [[gate(1), 0.5, 'callback already ran'], [gate(0.02), 2, 'gate artifact may still be settling'],
    [gate(1, 'in_progress'), 2, 'gate still running'], [gate(30), 40, 'too old'], [null, 2, 'no gate']])
    assert.equal((await run(g, pub)).writes.length, 0, why)
})

test('a public repository passes the minutes check without counting runs', async () => {
  const { gh, fetcher } = world({ public: true })
  const c = byId((await assess(cfg, gh, fetcher, NOW)).checks).minutes
  assert.equal(c.status, 'ok')
  assert.match(c.detail, /Public repository/)
})

test('a run whose logs were deleted later counts at most six hours', async () => {
  const runs = [{ status: 'completed', run_started_at: iso(100), updated_at: iso(0), head_sha: MAIN, created_at: iso(100), name: 'web' }]
  const { gh, fetcher } = world({ runs })
  const c = byId((await assess(cfg, gh, fetcher, NOW)).checks).minutes
  assert.match(c.detail, /About 360 min used/)
})
