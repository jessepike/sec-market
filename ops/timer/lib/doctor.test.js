import { test } from 'node:test'
import assert from 'node:assert/strict'
import { diagnose, plan, doctor } from './doctor.js'

// Replays of the real Nov 10-12 2026 runs (times from the Actions run list).
// A run that finishes after the replay time is shown as still running.
const T = s => Date.parse(s)
const M = 'aa4b7d5'
const runs = {
  collect: [
    // [id, event, title, created, jobStarted, jobDone, conclusion]
    [10, 'workflow_dispatch', 'daily timer collection', '2026-11-10T05:17:38Z', '2026-11-10T05:18:30Z', '2026-11-10T05:50:00Z', 'success'],
    [11, 'workflow_dispatch', 'daily timer collection', '2026-11-11T05:17:38Z', '2026-11-11T05:18:30Z', '2026-11-11T06:03:30Z', 'cancelled'],
    [12, 'schedule', 'bounded subscription collector', '2026-11-11T12:44:56Z', '2026-11-11T12:45:40Z', '2026-11-11T13:20:40Z', 'success'],
    [13, 'workflow_dispatch', 'daily timer collection', '2026-11-12T05:17:38Z', '2026-11-12T05:18:30Z', '2026-11-12T06:04:10Z', 'cancelled'],
    [14, 'schedule', 'bounded subscription collector', '2026-11-12T13:47:52Z', '2026-11-12T13:48:30Z', '2026-11-12T14:26:40Z', 'success'],
  ],
  gate: [
    // [id, created, done, conclusion, sha]
    [20, '2026-11-10T05:54:28Z', '2026-11-10T06:51:18Z', 'success', '398b9db'],
    [21, '2026-11-11T13:26:25Z', '2026-11-11T13:47:01Z', 'failure', '1cca665'],
    [22, '2026-11-12T14:33:49Z', '2026-11-12T15:03:41Z', 'failure', '1cca665'],
    [23, '2026-11-12T17:56:56Z', '2026-11-12T18:14:08Z', 'failure', '038472c'],
  ],
  pub: [
    // [id, event, created, done, conclusion]
    [30, 'workflow_run', '2026-11-10T05:48:06Z', '2026-11-10T06:51:17Z', 'success'],
    [31, 'workflow_run', '2026-11-11T13:20:56Z', '2026-11-11T13:28:47Z', 'success'],
    [32, 'workflow_dispatch', '2026-11-11T13:50:50Z', '2026-11-11T13:55:44Z', 'failure'],
    [33, 'workflow_run', '2026-11-12T14:26:59Z', '2026-11-12T14:36:18Z', 'success'],
    [34, 'workflow_dispatch', '2026-11-12T15:10:51Z', '2026-11-12T15:19:22Z', 'failure'],
    [35, 'workflow_dispatch', '2026-11-12T17:50:50Z', '2026-11-12T17:59:29Z', 'success'],
    ...Array.from({ length: 9 }, (_, i) => [40 + i, 'workflow_dispatch', new Date(T('2026-11-12T20:00:50Z') + i * 600000).toISOString(),
      new Date(T('2026-11-12T20:08:50Z') + i * 600000).toISOString(), 'failure']),
  ],
}
const LIVE = '2026-11-10T05:18:30Z' // The Nov 10 collection stayed live through Nov 12.

function at(now, { live = LIVE, mainSha = '1cca665', loginExpired = false, extra = {} } = {}) {
  const n = T(now)
  const state = (created, done) => T(created) > n ? null : T(done) > n ? 'running' : 'done'
  const collections = runs.collect.concat(extra.collect || []).filter(r => state(r[3], r[5]))
    .map(([id, event, title, created, s, d, c]) => {
      const fin = T(d) <= n
      return { id, url: `run/${id}`, event, title, created, status: fin ? 'completed' : 'in_progress', conclusion: fin ? c : null,
        job: { status: fin ? 'completed' : 'in_progress', conclusion: fin ? c : null, started: s, completed: fin ? d : null } }
    }).reverse()
  const gates = runs.gate.filter(r => state(r[1], r[2])).map(([id, created, done, c, sha]) => {
    const fin = T(done) <= n
    return { id, url: `gate/${id}`, created, updated: fin ? done : created, status: fin ? 'completed' : 'in_progress', conclusion: fin ? c : null, sha }
  }).reverse()
  const pubs = runs.pub.concat(extra.pub || []).filter(r => state(r[2], r[3])).map(([id, event, created, done, c]) => {
    const fin = T(done) <= n
    return { id, url: `pub/${id}`, event, created, updated: fin ? done : created, status: fin ? 'completed' : 'in_progress', conclusion: fin ? c : null }
  }).reverse()
  return { now: n, liveAt: live && T(live), mainSha, collections, loginExpired, gates, pubs }
}
const codes = d => d.findings.map(f => f.code)

test('Nov 10 after the release: OK', () => {
  const d = diagnose(at('2026-11-10T08:00:00Z', { mainSha: '398b9db' }))
  assert.equal(d.code, 'OK')
  assert.deepEqual(codes(d), [])
})

test('Nov 11 06:10: the 05:17 collection timed out, so start one more collection', () => {
  const obs = at('2026-11-11T06:10:00Z', { live: LIVE })
  const d = diagnose(obs, { COLLECT_LIMIT_MINUTES: 45 })
  assert.deepEqual(codes(d), ['COLLECT_TIMEOUT'])
  const p = plan(d.findings[0], obs, { COLLECT_LIMIT_MINUTES: 45 })
  assert.equal(p.step, 'collect')
  assert.equal(p.escalate, 'none')
})

test('a second timeout the same day stops retrying and hands to repair', () => {
  const extra = { collect: [[15, 'workflow_dispatch', 'daily timer collection', '2026-11-11T06:10:30Z', '2026-11-11T06:11:00Z', '2026-11-11T06:56:00Z', 'cancelled']] }
  const obs = at('2026-11-11T07:00:00Z', { extra })
  const d = diagnose(obs, { COLLECT_LIMIT_MINUTES: 45 })
  assert.deepEqual(codes(d), ['COLLECT_TIMEOUT'])
  const p = plan(d.findings[0], obs, { COLLECT_LIMIT_MINUTES: 45 })
  assert.equal(p.step, 'none')
  assert.equal(p.escalate, 'repair')
})

test('Nov 11 14:00: the gate failed on unchanged code, so repair, not retry', () => {
  const d = diagnose(at('2026-11-11T14:00:00Z'))
  assert.deepEqual(codes(d), ['GATE_FAILED'])
  assert.equal(plan(d.findings[0], at('2026-11-11T14:00:00Z')).escalate, 'repair')
})

test('Nov 12 06:10: timed out again (retry and ask for a fix) and the gate failure still needs repair', () => {
  const obs = at('2026-11-12T06:10:00Z')
  const d = diagnose(obs, { COLLECT_LIMIT_MINUTES: 45 })
  assert.deepEqual(codes(d), ['COLLECT_TIMEOUT', 'GATE_FAILED'])
  const p = plan(d.findings[0], obs, { COLLECT_LIMIT_MINUTES: 45 })
  assert.equal(p.step, 'collect')
  assert.equal(p.escalate, 'repair', 'two timeouts in a row need a fix, not only a retry')
})

test('Nov 12 21:40: fix on main, gate budget used, publisher looping: wait for 00:05 and flag the loop', () => {
  const obs = at('2026-11-12T21:40:00Z', { mainSha: M })
  const d = diagnose(obs)
  assert.deepEqual(codes(d), ['PUBLISH_STORM', 'GATE_BUDGET_USED'])
  const wait = plan(d.findings[1], obs)
  assert.equal(wait.step, 'none')
  assert.match(wait.why, /2026-11-13T00:05:00Z/)
})

test('Nov 13 00:10: the budget has reset and main has the fix, so start the publisher once', () => {
  const obs = at('2026-11-13T00:10:00Z', { mainSha: M })
  obs.pubs = obs.pubs.filter(p => !/^4\d$/.test(String(p.id))) // the loop is fixed by then
  const d = diagnose(obs)
  assert.deepEqual(codes(d), ['GATE_BUDGET_USED'])
  assert.equal(plan(d.findings[0], obs).step, 'publish')
  // Once started, the next tick does not start it again.
  obs.pubs.unshift({ id: 99, event: 'workflow_dispatch', created: '2026-11-13T00:10:30Z', status: 'in_progress' })
  assert.equal(diagnose(obs).code, 'WAITING')
})

test('no collection by 06:00 UTC starts one', () => {
  const obs = at('2026-11-10T06:30:00Z', { mainSha: '398b9db' })
  obs.collections = obs.collections.filter(c => !c.created.startsWith('2026-11-10'))
  obs.gates = []; obs.pubs = []
  obs.liveAt = T('2026-11-09T05:30:00Z')
  const d = diagnose(obs)
  assert.deepEqual(codes(d), ['NO_COLLECTION'])
  assert.equal(plan(d.findings[0], obs).step, 'collect')
})

test('an expired login goes to the owner and is never retried', () => {
  const obs = at('2026-11-10T08:00:00Z', { mainSha: '398b9db', loginExpired: true })
  const d = diagnose(obs)
  assert.deepEqual(codes(d), ['LOGIN_EXPIRED'])
  assert.equal(plan(d.findings[0], obs).escalate, 'owner')
})

test('dry run reads but never dispatches', async () => {
  const obs = at('2026-11-11T06:10:00Z')
  const writes = []
  const gh = async (path, init = {}) => {
    if (init.method) { writes.push(path); return null }
    const key = path.split('?')[0]
    if (key.endsWith('/workflows/c.yml/runs')) return { workflow_runs: obs.collections.map(c => ({ id: c.id, html_url: c.url, event: c.event, display_title: c.title, created_at: c.created, status: c.status, conclusion: c.conclusion })) }
    const job = /runs\/(\d+)\/jobs/.exec(key)
    if (job) { const c = obs.collections.find(x => String(x.id) === job[1]); return { jobs: [{ id: c.id, name: 'collect-and-reconcile', status: c.job.status, conclusion: c.job.conclusion, started_at: c.job.started, completed_at: c.job.completed }] } }
    if (key.includes('/annotations')) return []
    if (key.includes('market-release-gate.yml')) return { workflow_runs: obs.gates.map(g => ({ ...g, html_url: g.url, created_at: g.created, updated_at: g.updated, head_sha: g.sha })) }
    if (key.includes('subscription-publisher.yml')) return { workflow_runs: obs.pubs.map(p => ({ ...p, html_url: p.url, created_at: p.created, updated_at: p.updated })) }
    if (key.includes('/check-runs')) return { check_runs: [{ head_sha: '1cca665' }] }
    throw new Error('unrouted ' + key)
  }
  const fetcher = async () => ({ ok: true, json: async () => ({ checkedAt: LIVE }) })
  const cfg = { GITHUB_REPO: 'o/r', WORKFLOW_FILE: 'c.yml', REF: 'main', DATA_URL: 'https://site.test/d.json', COLLECT_LIMIT_MINUTES: 45, DOCTOR_DRY_RUN: 'true' }
  const r = await doctor(cfg, gh, fetcher, T('2026-11-11T06:10:00Z'))
  assert.deepEqual(r.findings.map(f => f.code), ['COLLECT_TIMEOUT'])
  assert.equal(r.findings[0].plan.step, 'collect')
  assert.deepEqual(writes, [])
})
