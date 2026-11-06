import { test } from 'node:test'
import assert from 'node:assert/strict'
import { addRequest, cleanName, handle, readQueue, writeQueue, QUEUE_LABEL, QUEUE_TITLE, LIMITS } from './requests.js'

const env = { CRON_SECRET: 's', GITHUB_TOKEN: 't', GITHUB_REPO: 'jessepike/sec-market', ASSIGNEE: 'jessepike' }
const NOW = Date.parse('2026-11-06T12:00:00Z')
const ORIGIN = 'https://securitymarketpulse.com'
const res = (body, status = 200) => ({ ok: status < 300, status, json: async () => body })
const post = (body, origin = ORIGIN) => new Request('https://t.example/api/request', { method: 'POST',
  headers: { origin, 'content-type': 'application/json' }, body: typeof body === 'string' ? body : JSON.stringify(body) })

function fakeGitHub(issues = []) {
  const calls = []
  const fetcher = async (url, init = {}) => {
    const method = init.method || 'GET'
    calls.push({ method, url, body: init.body && JSON.parse(init.body) })
    if (method === 'GET') return res(issues)
    return res({ number: 7 }, 201)
  }
  return { calls, fetcher }
}

test('names: plain company names pass, links, markup and junk do not', () => {
  for (const ok of ['Cyera', '7AI', 'F5', 'Check Point', 'AT&T Cybersecurity', "O'Brien Labs", 'Trend Micro Inc.', 'Société Générale'])
    assert.ok(cleanName(ok), ok)
  assert.equal(cleanName('  rubrik   inc '), 'rubrik inc')
  for (const bad of ['', 'a', '123', 'x'.repeat(LIMITS.maxChars + 1), 'buy now http', 'cheap.ru', 'www shop', '<script>', 'a|b', 'me@x', null, 5])
    assert.equal(cleanName(bad), null, String(bad))
})

test('queue round-trips through the issue body and counts repeats case-insensitively', () => {
  let { list, added } = addRequest([], 'Cyera', '2026-11-06')
  assert.equal(added, true)
  ;({ list, added } = addRequest(readQueue(writeQueue(list)), 'cyera', '2026-11-07'))
  assert.equal(added, false)
  assert.deepEqual(list, [{ name: 'Cyera', count: 2, first: '2026-11-06', last: '2026-11-07' }])
  assert.match(writeQueue(list), /\| Cyera \| 2 \| 2026-11-06 \| 2026-11-07 \|/)
  assert.deepEqual(readQueue('no marker'), [])
})

test('new names are capped per day; repeats still count', () => {
  let list = []
  for (let i = 0; i < LIMITS.newPerDay; i++) list = addRequest(list, `Company ${String.fromCharCode(65 + i)}`, '2026-11-06').list
  assert.equal(addRequest(list, 'One More', '2026-11-06').dropped, true)
  assert.equal(addRequest(list, 'company a', '2026-11-06').list[0].count, 2)
  assert.equal(addRequest(list, 'One More', '2026-11-07').added, true)
})

test('endpoint refuses other origins and answers the preflight', async () => {
  const { fetcher, calls } = fakeGitHub()
  assert.equal((await handle(post({ name: 'Cyera', elapsed: 5000 }, 'https://evil.example'), env, fetcher, NOW)).status, 403)
  const pre = await handle(new Request('https://t.example/api/request', { method: 'OPTIONS', headers: { origin: ORIGIN } }), env, fetcher, NOW)
  assert.equal(pre.status, 204)
  assert.equal(pre.headers.get('access-control-allow-origin'), ORIGIN)
  assert.equal(calls.length, 0)
})

test('honeypot and instant submits look accepted but write nothing; bad input is 400', async () => {
  const { fetcher, calls } = fakeGitHub()
  for (const body of [{ name: 'Cyera', elapsed: 5000, website: 'x' }, { name: 'Cyera', elapsed: 100 }, { name: 'Cyera' }]) {
    const r = await handle(post(body), env, fetcher, NOW)
    assert.equal(r.status, 200)
    assert.deepEqual(await r.json(), { ok: true })
  }
  assert.equal(calls.length, 0)
  assert.equal((await handle(post({ name: 'http spam', elapsed: 5000 }), env, fetcher, NOW)).status, 400)
  assert.equal((await handle(post('not json'), env, fetcher, NOW)).status, 400)
  assert.equal((await handle(post('x'.repeat(2000)), env, fetcher, NOW)).status, 413)
  assert.equal(calls.length, 0)
})

test('first request opens one assigned, labelled issue', async () => {
  const { fetcher, calls } = fakeGitHub([])
  const r = await handle(post({ name: 'Cyera', elapsed: 5000 }), env, fetcher, NOW)
  assert.equal(r.status, 200)
  const create = calls.find(c => c.method === 'POST')
  assert.equal(create.url, 'https://api.github.com/repos/jessepike/sec-market/issues')
  assert.equal(create.body.title, QUEUE_TITLE)
  assert.deepEqual(create.body.labels, [QUEUE_LABEL])
  assert.deepEqual(create.body.assignees, ['jessepike'])
  assert.deepEqual(readQueue(create.body.body), [{ name: 'Cyera', count: 1, first: '2026-11-06', last: '2026-11-06' }])
})

test('a new name edits the list and comments once; a repeat only edits', async () => {
  const issue = { number: 7, title: QUEUE_TITLE, body: writeQueue([{ name: 'Cyera', count: 1, first: '2026-11-05', last: '2026-11-05' }]) }
  let gh = fakeGitHub([issue])
  await handle(post({ name: 'Straiker', elapsed: 5000 }), env, gh.fetcher, NOW)
  assert.deepEqual(gh.calls.map(c => c.method), ['GET', 'PATCH', 'POST'])
  assert.equal(gh.calls[2].body.body, 'New company request: Straiker')
  gh = fakeGitHub([issue])
  await handle(post({ name: 'CYERA', elapsed: 5000 }), env, gh.fetcher, NOW)
  assert.deepEqual(gh.calls.map(c => c.method), ['GET', 'PATCH'])
  assert.equal(readQueue(gh.calls[1].body.body)[0].count, 2)
})

test('GitHub failure is a 503 the box can show', async () => {
  const fetcher = async () => res({}, 500)
  assert.equal((await handle(post({ name: 'Cyera', elapsed: 5000 }), env, fetcher, NOW)).status, 503)
})

test('the app token it asks for can touch issues only', async () => {
  const { generateKeyPairSync } = await import('node:crypto')
  const { privateKey } = generateKeyPairSync('rsa', { modulusLength: 2048 })
  const pem = privateKey.export({ type: 'pkcs1', format: 'pem' })
  let asked
  const fetcher = async (url, init = {}) => {
    if (url.endsWith('/installation')) return res({ id: 9 })
    if (url.endsWith('/access_tokens')) { asked = JSON.parse(init.body); return res({ token: 'inst' }, 201) }
    return (init.method || 'GET') === 'GET' ? res([]) : res({ number: 1 }, 201)
  }
  const appEnv = { ...env, GITHUB_TOKEN: '', GITHUB_APP_ID: '1', GITHUB_APP_PRIVATE_KEY: pem }
  assert.equal((await handle(post({ name: 'Cyera', elapsed: 5000 }), appEnv, fetcher, NOW)).status, 200)
  assert.deepEqual(asked, { repositories: ['sec-market'], permissions: { issues: 'write', metadata: 'read' } })
})
