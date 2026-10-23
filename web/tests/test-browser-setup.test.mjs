import test from 'node:test'
import assert from 'node:assert/strict'
import { ensureBrowser } from '../scripts/ensure-test-browser.mjs'

const browser = { close: async () => {} }

test('usable Chromium launches without an installation or OS upgrade', async () => {
  await ensureBrowser({ launch: async () => browser, install: () => assert.fail('unnecessary install') })
})

test('missing executable downloads browser and installs OS packages only after a missing-library launch', async () => {
  const attempts = [new Error("Executable doesn't exist"), new Error('error while loading shared libraries: libnss3.so'), browser]
  const installs = []
  await ensureBrowser({ launch: async () => { const result = attempts.shift(); if (result instanceof Error) throw result; return result }, install: args => installs.push(args) })
  assert.deepEqual(installs, [['install', 'chromium'], ['install-deps', 'chromium']])
  assert.equal(attempts.length, 0)
})

test('unrelated launch failures stay failed without an apt retry', async () => {
  await assert.rejects(ensureBrowser({ launch: async () => { throw new Error('sandbox denied') }, install: () => assert.fail('unnecessary install') }), /sandbox denied/)
})

test('failed dependency installation prevents successful setup', async () => {
  await assert.rejects(ensureBrowser({ launch: async () => { throw new Error('Host system is missing dependencies') }, install: () => { throw new Error('setup timed out') } }), /setup timed out/)
})
