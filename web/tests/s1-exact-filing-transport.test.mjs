import assert from 'node:assert/strict'
import { test } from 'node:test'
import { readFileSync, writeFileSync, mkdirSync, mkdtempSync, rmSync } from 'node:fs'
import { execFileSync } from 'node:child_process'
import { tmpdir } from 'node:os'
import { resolve } from 'node:path'
import { createHash } from 'node:crypto'
import { reviewPolicy, verifyFactualCorrections } from '../scripts/verify-factual-corrections.mjs'

const root = resolve(import.meta.dirname, '../..')
const read = path => JSON.parse(readFileSync(resolve(root, path)))
const canonical = value => Array.isArray(value) ? '[' + value.map(canonical).join(',') + ']' : value && typeof value === 'object' ? '{' + Object.keys(value).sort().map(key => JSON.stringify(key) + ':' + canonical(value[key])).join(',') + '}' : JSON.stringify(value)
const digest = value => createHash('sha256').update(Buffer.isBuffer(value) ? value : canonical(value)).digest('hex')
const group = read('ops/ci/fixtures/s1-exact-filing-transport.json')
const market = read('contracts/market.json')
const requests = read('contracts/factual-corrections.json')
const baseline = requests.baseline.sha256
const copy = value => structuredClone(value)

function fixture(t) {
  const directory = mkdtempSync(resolve(tmpdir(), 'smp-s1-closed-transport-'))
  t.after(() => rmSync(directory, { recursive: true, force: true }))
  const write = (path, value) => {
    const file = resolve(directory, path)
    mkdirSync(resolve(file, '..'), { recursive: true })
    writeFileSync(file, JSON.stringify(value, null, 2) + '\n')
  }
  for (const path of ['contracts/market.json', 'contracts/factual-corrections.json', 'contracts/factual-baseline.json', 'web/src/data/tracker/originals.json']) {
    const file = resolve(directory, path)
    mkdirSync(resolve(file, '..'), { recursive: true })
    writeFileSync(file, readFileSync(resolve(root, path)))
  }
  const current = copy(requests)
  current.groups.push(copy(group))
  const actualMarket = copy(market)
  const originals = read('web/src/data/tracker/originals.json')
  function stamp() {
    const policy = {
      schemaVersion: 1,
      policySha256: digest({ marketSha256: digest(actualMarket), requestsSha256: digest(current), baselineSha256: current.baseline.sha256 }),
      groupIds: current.groups.map(row => row.id), targetIds: current.groups.flatMap(row => row.targets.map(target => target.targetId)),
      sourceEvidenceIds: Object.fromEntries(current.groups.map(row => [row.id, row.sources.map(source => source.evidenceId)])),
      reviewPolicySha256ByGroup: Object.fromEntries(current.groups.map(row => [row.id, reviewPolicy(row, actualMarket, current.baseline.sha256)])),
    }
    write('contracts/factual-corrections.json', current)
    write('contracts/market.json', actualMarket)
    write('web/src/data/tracker/factualCorrectionPolicy.json', policy)
    write('web/src/data/tracker/originals.json', originals)
    write('web/src/data/generated/factualCorrections.json', { schemaVersion: 1, enabled: false, policySha256: null, checkedAt: null, groups: [] })
    return policy
  }
  stamp()
  return { directory, current, actualMarket, originals, stamp, write, verify: () => verifyFactualCorrections(resolve(directory, 'web')) }
}

test('optional transport builds only with its exact pinned source and keeps six old policies', t => {
  const f = fixture(t)
  const policy = f.stamp(), old = read('web/src/data/tracker/factualCorrectionPolicy.json')
  assert.equal(f.verify().enabled, false)
  assert.equal(Object.keys(old.reviewPolicySha256ByGroup).length, 6)
  for (const [id, hash] of Object.entries(old.reviewPolicySha256ByGroup)) assert.equal(policy.reviewPolicySha256ByGroup[id], hash)
  const bare = copy(group)
  delete bare.sources[0].transportAttestation
  assert.notEqual(reviewPolicy(group, market, baseline), reviewPolicy(bare, market, baseline))
})

test('Python and JavaScript independently agree on valid and rejected exact transport policies', () => {
  const cases = requests.groups.map(row => ({ group: row, market, baseline }))
  cases.push({ group, market, baseline })
  const add = mutate => {
    const row = { group: copy(group), market: copy(market), baseline }
    mutate(row.group, row.market, row)
    cases.push(row)
  }
  add(row => { delete row.sources[0].transportAttestation })
  for (const key of Object.keys(group.sources[0].transportAttestation)) {
    add(row => { delete row.sources[0].transportAttestation[key] })
    add(row => { row.sources[0].transportAttestation[key] = 'changed' })
  }
  for (const value of [null, [], {}, { ...group.sources[0].transportAttestation, extra: true }, { ...group.sources[0].transportAttestation, schemaVersion: true }]) {
    add(row => { row.sources[0].transportAttestation = value })
  }
  for (const key of ['requestedUrl', 'canonicalUrl', 'finalUrl']) {
    const url = group.sources[0].transportAttestation[key]
    for (const changed of [url.replace('https:', 'http:'), url.replace('www.sec.gov', 'sec.gov'), url.replace('www.sec.gov', 'www.sec.gov:443'),
      url.replace('www.sec.gov', 'www.sec.gov.evil.invalid'), url.replace('/data/', '/data/../data/'), url.replace('1583708/', '1583709/'),
      url.replace('26000039/', '26000040/'), url.replace('s-20260528.htm', 's-20260529.htm'), url + '?x=1', url + '#filing', url.replace('s-20260528', '%73-20260528')]) {
      add(row => { row.sources[0].transportAttestation[key] = changed })
    }
  }
  for (const [key, value] of [['sourceId', 'another'], ['evidenceId', 'another'], ['url', group.sources[0].transportAttestation.finalUrl], ['extra', true],
    ['observationId', false], ['fetchedAt', '2026-10-24'], ['body', { ...group.sources[0].body, bytes: 49403 }],
    ['body', { ...group.sources[0].body, extra: true }], ['body', { ...group.sources[0].body, bytes: '49404' }]]) {
    add(row => { row.sources[0][key] = value })
  }
  add(row => { row.supplierId = 'netskope' })
  add((row, configuration) => { configuration.sources.find(source => source.id === row.sources[0].sourceId).required = false })
  add((row, configuration, testcase) => { testcase.baseline = 'wrong' })
  const python = `import json,sys\nsys.path.insert(0,sys.argv[1])\nfrom corrections import group_review_policy\nresults=[]\nfor case in json.load(sys.stdin):\n try: results.append(group_review_policy(case['group'],case['market'],case['baseline']))\n except (ValueError,TypeError,KeyError): results.append('rejected')\nprint(json.dumps(results))`
  const expected = JSON.parse(execFileSync('python3', ['-B', '-c', python, resolve(root, 'web/scripts/pipeline')], { input: JSON.stringify(cases), maxBuffer: 4 * 1024 * 1024 }).toString())
  const actual = cases.map(row => { try { return reviewPolicy(row.group, row.market, row.baseline) } catch { return 'rejected' } })
  assert.deepEqual(actual, expected)
  assert.equal(actual.filter(value => value !== 'rejected').length, 8) // Six old groups, exact optional group, ordinary group without attestation.
})

test('build rejects changed immutable evidence despite a recomputed ordinary baseline', t => {
  const f = fixture(t)
  f.originals.evidence.find(row => row.id === 'TR-s1-3').organization += ' changed'
  const originalBaseline = read('contracts/factual-baseline.json')
  originalBaseline.inventories.evidence['TR-s1-3'] = digest(f.originals.evidence.find(row => row.id === 'TR-s1-3'))
  const bytes = Buffer.from(JSON.stringify(originalBaseline, null, 2) + '\n')
  f.write('contracts/factual-baseline.json', originalBaseline)
  f.current.baseline.sha256 = digest(bytes)
  f.stamp()
  assert.throws(f.verify, /transport immutable evidence differs/)
})

test('build rejects an extra attested group field before accepting a fresh stamp', t => {
  const f = fixture(t)
  f.current.groups.at(-1).extra = true
  f.stamp()
  assert.throws(f.verify, /transport group schema differs/)
})
