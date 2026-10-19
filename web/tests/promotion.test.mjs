import { test } from 'node:test'
import assert from 'node:assert/strict'
import { execFileSync } from 'node:child_process'
import { mkdtempSync, mkdirSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join } from 'node:path'
import { decide, SOAK_HOURS } from '../scripts/promotion/decide.mjs'

const HOUR = 3600000
const T0 = Date.parse('2026-10-18T00:00:00Z')

function repo() {
  const dir = mkdtempSync(join(tmpdir(), 'promo-'))
  const g = (args, env = {}) => execFileSync('git', args, { cwd: dir, env: { ...process.env, ...env }, stdio: 'pipe' }).toString().trim()
  g(['init', '-q', '-b', 'main'])
  g(['config', 'user.email', 't@example.com']); g(['config', 'user.name', 'T']); g(['config', 'commit.gpgsign', 'false'])
  const commit = (path, body, message, at) => {
    mkdirSync(join(dir, dirname(path)), { recursive: true })
    writeFileSync(join(dir, path), body)
    g(['add', '-A'])
    const date = new Date(at).toISOString()
    g(['commit', '-q', '-m', message], { GIT_AUTHOR_DATE: date, GIT_COMMITTER_DATE: date })
  }
  commit('README.md', 'x', 'init', T0)
  g(['branch', 'base'])
  return { dir, g, commit }
}

const DATA = 'web/src/data/generated/filingEvents.json'

test('nothing to promote when main equals preview', () => {
  const r = repo()
  assert.equal(decide(r.dir, { base: 'base', now: T0 }).action, 'none')
})

test('a data-only change promotes after the data soak, not before', () => {
  const r = repo()
  r.commit(DATA, '[1]', 'data(auto): refresh', T0)
  assert.equal(decide(r.dir, { base: 'base', now: T0 + (SOAK_HOURS.data - 1) * HOUR }).action, 'wait')
  const ok = decide(r.dir, { base: 'base', now: T0 + SOAK_HOURS.data * HOUR })
  assert.equal(ok.action, 'promote'); assert.equal(ok.dataOnly, true)
})

test('a code or docs change needs the longer soak', () => {
  const r = repo()
  r.commit('docs/x.md', 'y', 'docs: note', T0)
  assert.equal(decide(r.dir, { base: 'base', now: T0 + SOAK_HOURS.data * HOUR }).action, 'wait')
  assert.equal(decide(r.dir, { base: 'base', now: T0 + SOAK_HOURS.other * HOUR }).action, 'promote')
})

test('an Owner-Review trailer anywhere in the range holds the whole promotion', () => {
  const r = repo()
  r.commit('web/src/a.ts', '1', 'feat(site): new section\n\nOwner-Review: required', T0)
  r.commit(DATA, '[2]', 'data(auto): refresh', T0 + HOUR)
  const d = decide(r.dir, { base: 'base', now: T0 + 100 * HOUR })
  assert.equal(d.action, 'hold'); assert.match(d.reasons[0], /Owner-Review/)
})

test('protected paths hold: intent, rules, hooks, headers and the promotion rules', () => {
  for (const path of ['intent.md', '.claude/rules/constraints.md', '.githooks/pre-push', 'web/vercel.json', '.github/workflows/promote.yml', 'web/scripts/promotion/decide.mjs']) {
    const r = repo()
    r.commit(path, 'z', 'chore: edit', T0)
    assert.equal(decide(r.dir, { base: 'base', now: T0 + 100 * HOUR }).action, 'hold', path)
  }
})

test('a workflow that starts using a secret holds', () => {
  const r = repo()
  r.commit('.github/workflows/digest.yml', 'env:\n  KEY: ${{ secrets.BUTTONDOWN_API_KEY }}\n', 'ci: digest', T0)
  assert.equal(decide(r.dir, { base: 'base', now: T0 + 100 * HOUR }).action, 'hold')
})

test('a diverged main fails rather than promoting', () => {
  const r = repo()
  r.g(['checkout', '-q', '-b', 'prod', 'base']); r.commit('x.txt', 'a', 'hotfix on main', T0)
  r.g(['checkout', '-q', 'main']); r.commit('y.txt', 'b', 'work', T0)
  assert.equal(decide(r.dir, { base: 'prod', now: T0 + 100 * HOUR }).action, 'fail')
})

test('page-structure guard ignores data and flags new sections, headings and pages', async () => {
  const { skeleton, compare } = await import('../scripts/promotion/structure.mjs')
  const site = (body, extra = {}) => {
    const d = mkdtempSync(join(tmpdir(), 'dist-'))
    writeFileSync(join(d, 'index.html'), `<nav><a href="#a">A</a></nav><h1>Title</h1><section id="changes"><h2>What changed</h2>${body}</section>`)
    for (const [p, h] of Object.entries(extra)) { mkdirSync(join(d, dirname(p)), { recursive: true }); writeFileSync(join(d, p), h) }
    return skeleton(d)
  }
  assert.deepEqual(compare(site('<p>Revenue $1</p>'), site('<p>Revenue $2</p><h3>New supplier</h3>')), [])
  assert.match(compare(site(''), site('<section id="new"><h2>Promo</h2></section>')).join(' '), /added #new/)
  assert.match(compare(site(''), site('', { 'about/index.html': '<h1>About</h1>' })).join(' '), /new page/)
})
