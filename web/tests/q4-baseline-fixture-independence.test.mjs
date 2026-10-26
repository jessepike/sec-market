import test from 'node:test'
import assert from 'node:assert/strict'
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { spawnSync } from 'node:child_process'

// Reproduce the gate's fresh generated-data substitution without changing any source file.
// The historical test must pass while an attempted read returns a fresh J counterexample.
test('historical Q4 assertions ignore a fresh generated snapshot overlay', () => {
  const directory = mkdtempSync(join(tmpdir(), 'q4-fresh-overlay-'))
  try {
    const trace = join(directory, 'generated-reads.txt')
    const hook = join(directory, 'fresh-overlay.mjs')
    const generated = fileURLToPath(new URL('../src/data/generated/dailyMarket.json', import.meta.url))
    const historical = fileURLToPath(new URL('./q4-baseline-migration.test.mjs', import.meta.url))
    writeFileSync(trace, '')
    const fresh = JSON.stringify({
      schemaVersion: 1,
      contractSha256: '47b9f22636f0e6ea79cf830ae90aab844d8f554d44110a5bb08f29f00266593a',
      runId: 'SYNTHETIC_FRESH_J_OVERLAY',
      coverage: { intake: { evaluated: true }, successfulTasks: 265, requiredTasks: 557 },
    })
    writeFileSync(hook, `
      import fs from 'node:fs'
      import { fileURLToPath } from 'node:url'
      import { syncBuiltinESMExports } from 'node:module'
      const original = fs.readFileSync
      fs.readFileSync = function (path, ...args) {
        const name = path instanceof URL ? fileURLToPath(path) : String(path)
        if (name === ${JSON.stringify(generated)}) {
          fs.appendFileSync(${JSON.stringify(trace)}, String(process.pid))
          return Buffer.from(${JSON.stringify(fresh)})
        }
        return original.call(this, path, ...args)
      }
      syncBuiltinESMExports()
    `)
    const env = { ...process.env }
    delete env.NODE_TEST_CONTEXT
    const result = spawnSync(process.execPath, ['--import', hook, '--test', historical], {
      encoding: 'utf8', timeout: 45000, env,
    })
    assert.equal(result.error, undefined)
    assert.equal(result.status, 0, result.stdout + result.stderr)
    assert.match(result.stdout, /# tests 2\b/, 'the child must execute both historical tests')
    assert.match(result.stdout, /# pass 2\b/)
    assert.equal(readFileSync(trace, 'utf8'), '', 'the historical assertion consumed mutable generated data')
  } finally {
    rmSync(directory, { recursive: true, force: true })
  }
})
