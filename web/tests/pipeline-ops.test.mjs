import { test } from 'node:test'
import assert from 'node:assert/strict'
import { createHash, webcrypto } from 'node:crypto'
import { handle } from '../../ops/archive/worker.mjs'
import { check, inspect, inspectDeployment } from '../../ops/watchdog/worker.mjs'

globalThis.crypto ??= webcrypto
class Bucket {
  values = new Map()
  generation = 0
  async get(key) {
    const v = this.values.get(key)
    return v ? { ...v, body: v.bytes, text: async () => new TextDecoder().decode(v.bytes), json: async () => JSON.parse(new TextDecoder().decode(v.bytes)) } : null
  }
  async head(key) { return this.get(key) }
  async put(key, value, options = {}) {
    const old = this.values.get(key)
    if (options.onlyIf?.etagDoesNotMatch === '*' && old) return null
    if (options.onlyIf?.etagMatches && options.onlyIf.etagMatches !== old?.etag) return null
    const bytes = typeof value === 'string' ? new TextEncoder().encode(value) : new Uint8Array(value)
    const v = { bytes, etag: String(++this.generation), customMetadata: options.customMetadata, size: bytes.length }
    this.values.set(key, v)
    return v
  }
  async list() { return { objects: [...this.values].map(([key, v]) => ({ key, ...v })), truncated: false } }
}
function environment() { return { ARCHIVE: new Bucket(), READ_TOKEN: 'reader', COLLECT_TOKEN: 'collector', VERIFY_TOKEN: 'verifier', PUBLISH_TOKEN: 'publisher' } }
function request(path, role = 'collector', body, method = 'PUT') {
  const bytes = body === undefined ? undefined : typeof body === 'string' ? body : JSON.stringify(body)
  return new Request('https://archive.invalid' + path, { method, body: bytes, headers: { authorization: 'Bearer ' + role, ...(bytes ? { 'x-smp-sha256': createHash('sha256').update(bytes).digest('hex') } : {}) } })
}
test('archive denies missing configuration, unauthenticated requests and all deletion', async () => {
  assert.equal((await handle(request('/v1/records/objects/a'), {})).status, 503)
  const env = environment()
  assert.equal((await handle(request('/v1/records/objects/a', 'wrong'), env)).status, 401)
  assert.equal((await handle(request('/v1/records/objects/a', 'publisher', undefined, 'DELETE'), env)).status, 405)
})
test('archive enforces role permissions and content addresses', async () => {
  const env = environment()
  assert.equal((await handle(request('/v1/records/releases/a', 'collector', 'x'), env)).status, 403)
  assert.equal((await handle(request('/v1/records/objects/wrong', 'collector', 'x'), env)).status, 400)
  assert.equal((await handle(request('/v1/records/facts/a', 'verifier', 'x'), env)).status, 201)
  assert.equal((await handle(request('/v1/records/facts/a', 'publisher', 'x'), env)).status, 403)
})
test('archive retries are idempotent and cannot overwrite an immutable receipt', async () => {
  const env = environment()
  assert.equal((await handle(request('/v1/records/runs/a', 'collector', 'original'), env)).status, 201)
  assert.equal((await handle(request('/v1/records/runs/a', 'collector', 'original'), env)).status, 200)
  assert.equal((await handle(request('/v1/records/runs/a', 'collector', 'changed'), env)).status, 409)
})
test('production head requires publisher and CAS; record route cannot bypass it', async () => {
  const env = environment()
  assert.equal((await handle(request('/v1/records/heads/production.json', 'publisher', '{}'), env)).status, 400)
  assert.equal((await handle(request('/v1/heads/production', 'collector', { expected: null, value: { sequence: 1 } }), env)).status, 403)
  assert.equal((await handle(request('/v1/heads/production', 'publisher', { expected: null, value: { sequence: 1 } }), env)).status, 200)
  assert.equal((await handle(request('/v1/heads/production', 'publisher', { expected: null, value: { sequence: 2 } }), env)).status, 409)
  const r = await handle(request('/v1/heads/production', 'reader', undefined, 'GET'), env)
  assert.deepEqual(await r.json(), { sequence: 1 })
  assert.equal(r.headers.get('x-smp-writer-role'), 'publish')
})
test('competing CAS attempts cannot both advance the same head', async () => {
  const env = environment()
  await handle(request('/v1/heads/production', 'publisher', { expected: null, value: 0 }), env)
  const results = await Promise.all([1, 2].map(value => handle(request('/v1/heads/production', 'publisher', { expected: 0, value }), env)))
  assert.deepEqual(results.map(r => r.status).sort(), [200, 409])
})
test('archive listing requires read role and exposes integrity hashes', async () => {
  const env = environment()
  await handle(request('/v1/records/runs/a', 'collector', 'original'), env)
  assert.equal((await handle(request('/v1/list', 'collector', undefined, 'GET'), env)).status, 403)
  const r = await handle(request('/v1/list', 'reader', undefined, 'GET'), env)
  assert.equal((await r.json()).keys[0].sha256, createHash('sha256').update('original').digest('hex'))
})
const now = Date.parse('2026-10-20T12:00:00Z')
const expected = { contractSha256: 'a'.repeat(64), supplierCount: 74, requiredTasks: 557, overdueHours: 30 }
const complete = { ...expected, checkedAt: '2026-10-20T11:00:00Z', successfulTasks: 557, gapTaskIds: [], complete: true, runId: 'run-1' }
const deployed = {ready:true,appRevision:'b'.repeat(40),dataReleaseId:'release-1',snapshotSha256:'c'.repeat(64),artifactSha256:'d'.repeat(64),contractSha256:expected.contractSha256}
function watchdogEnv() { return { COVERAGE_URL: 'https://site.invalid/coverage.json', RELEASE_EXPECTATION_URL:'https://authority.invalid/expected-release.json',LIVE_RECEIPT_URL:'https://site.invalid/release.json', EXPECTED_CONTRACT_SHA256: expected.contractSha256, EXPECTED_SUPPLIERS: '74', EXPECTED_REQUIRED_TASKS: '557', ALERT_WEBHOOK: 'https://alerts.invalid/hook', ALERT_STATE: new Bucket() } }
function monitored(fetcher,env){return (url,options)=>[env.RELEASE_EXPECTATION_URL,env.LIVE_RECEIPT_URL].includes(url)?Response.json(deployed):fetcher(url,options)}
test('watchdog refuses missing, stale, future or reduced coverage', () => {
  assert.equal(inspect(complete, expected, now).healthy, true)
  for (const r of [null, { ...complete, checkedAt: '2026-10-18T11:00:00Z' }, { ...complete, checkedAt: '2026-10-21T11:00:00Z' }, { ...complete, requiredTasks: 16 }, { ...complete, gapTaskIds: ['missing'] }, { ...complete, gapTaskIds: undefined }]) {
    assert.equal(inspect(r, expected, now).healthy, false)
  }
})
test('HTTP 200 with incomplete coverage still alerts; repeated checks are deduplicated', async () => {
  const env = watchdogEnv(), sent = []
  const fetcher = monitored(async (url, options) => url === env.COVERAGE_URL ? Response.json({ ...complete, complete: false }) : (sent.push(options.body), new Response('ok')),env)
  assert.equal((await check(env, fetcher, now)).healthy, false)
  await check(env, fetcher, now + 3600000)
  assert.equal(sent.length, 1)
  await check(env, fetcher, now + 25 * 3600000)
  assert.equal(sent.length, 2)
})
test('failed alert delivery is retried and is never recorded as delivered', async () => {
  const env = watchdogEnv()
  const fetcher = monitored(async url => url === env.COVERAGE_URL ? new Response('unavailable', { status: 503 }) : new Response('failed', { status: 500 }),env)
  await assert.rejects(() => check(env, fetcher, now), /ALERT_DELIVERY_FAILED/)
  assert.equal(env.ALERT_STATE.values.size, 0)
})
test('watchdog reports recovery and requires explicit configuration', async () => {
  await assert.rejects(() => check({}, null, now), /WATCHDOG_NOT_CONFIGURED/)
  const env = watchdogEnv(), sent = []
  let receipt = null
  const fetcher = monitored(async (url, options) => url === env.COVERAGE_URL ? Response.json(receipt) : (sent.push(JSON.parse(options.body).text), new Response('ok')),env)
  await check(env, fetcher, now)
  receipt = complete
  await check(env, fetcher, now)
  assert.equal(sent.length, 2)
  assert.match(sent[1], /recovered/)
})
test('fresh collection cannot hide stale deployed data or application code', async () => {
  assert.equal(inspectDeployment(deployed,deployed),true)
  assert.equal(inspectDeployment(deployed,{...deployed,dataReleaseId:'old'}),false)
  const env=watchdogEnv(),sent=[]
  const fetcher=async (url,options)=>{
    if(url===env.COVERAGE_URL)return Response.json(complete)
    if(url===env.RELEASE_EXPECTATION_URL)return Response.json(deployed)
    if(url===env.LIVE_RECEIPT_URL)return Response.json({...deployed,appRevision:'wrong'})
    sent.push(options.body);return new Response('ok')
  }
  const result=await check(env,fetcher,now)
  assert.equal(result.healthy,false);assert.match(sent[0],/PRODUCTION_RELEASE_NOT_ACKNOWLEDGED/)
})
