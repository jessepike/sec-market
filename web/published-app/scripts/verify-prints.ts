import { existsSync, readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { evidenceById } from '../src/data/evidence.ts'
import { verifyAllPrints } from '../src/data/printChecks.ts'
import { printsUnverified } from '../src/data/printsUnverified.ts'
import { vendorPrints } from '../src/data/prints.ts'

// The figure-meaning check (publish-path-spec.md §4.1, SEC-044/SEC-045).
// Compares every scorecard print against the evidence it cites on company,
// metric, period, and units, and confirms its value appears in that
// evidence. Comparison logic lives in ../src/data/printChecks.ts and
// ../src/data/printPeriod.ts, both pure and unit-tested directly in
// tests/print-checks.test.ts — this script is only the CLI wrapper, the
// unverified-list gate, and the exit code.

const __dirname = dirname(fileURLToPath(import.meta.url))
const BASELINE_PATH = resolve(__dirname, 'prints-unverified-baseline.json')

/**
 * The maximum set of print ids `printsUnverified.ts` may ever list, as a
 * sorted JSON array committed alongside this script. `printsUnverified.ts`
 * may hold fewer ids than this (an id is removed once its print is
 * corrected) but never an id absent from this file — adding to the
 * unverified list is a decision that needs the owner's word, made by
 * editing THIS file in a reviewed commit, not by the weekly gather job.
 */
function readBaseline(): string[] {
  if (!existsSync(BASELINE_PATH)) return []
  const raw = readFileSync(BASELINE_PATH, 'utf8').trim()
  return raw === '' ? [] : (JSON.parse(raw) as string[])
}

function main(): void {
  const baseline = new Set(readBaseline())
  const unverifiedIds = new Set(printsUnverified.map((entry) => entry.id))

  const baselineViolations = [...unverifiedIds].filter((id) => !baseline.has(id))
  if (baselineViolations.length > 0) {
    console.error(
      `FAIL  shrink-only baseline — printsUnverified.ts lists id(s) not in the committed baseline ` +
        `(scripts/prints-unverified-baseline.json): ${baselineViolations.join(', ')}. Adding to the ` +
        `unverified list needs the owner's word, recorded by adding the id to the baseline file first.`,
    )
    process.exit(1)
  }

  const unknownPrintIds = printsUnverified
    .map((entry) => entry.id)
    .filter((id) => !vendorPrints.some((print) => print.id === id))
  if (unknownPrintIds.length > 0) {
    console.error(`FAIL  printsUnverified.ts names id(s) not present in prints.ts: ${unknownPrintIds.join(', ')}`)
    process.exit(1)
  }

  const results = verifyAllPrints(vendorPrints, evidenceById)

  let passCount = 0
  let warnCount = 0
  let failCount = 0
  const failures: string[] = []
  const notCheckableCounts: Record<string, number> = {}

  for (const result of results) {
    for (const [dimension, outcome] of [
      ['company', result.company],
      ['metric', result.metric],
      ['period', result.period],
      ['value', result.value],
      ['units', result.units],
    ] as const) {
      if (outcome.status === 'not-checkable') {
        notCheckableCounts[dimension] = (notCheckableCounts[dimension] ?? 0) + 1
      }
    }

    if (unverifiedIds.has(result.printId)) {
      warnCount++
      if (result.overall === 'fail') {
        const failingDims = (['company', 'metric', 'period', 'value', 'units'] as const).filter(
          (dim) => result[dim].status === 'fail',
        )
        console.log(
          `WARN  ${result.printId} — on the unverified list; fails ${failingDims.join(', ')} ` +
            `(${failingDims.map((dim) => result[dim].reason).join('; ')})`,
        )
      } else {
        console.log(`WARN  ${result.printId} — on the unverified list; the mechanical check itself now passes`)
      }
      continue
    }

    if (result.overall === 'fail') {
      failCount++
      const failingDims = (['company', 'metric', 'period', 'value', 'units'] as const).filter(
        (dim) => result[dim].status === 'fail',
      )
      failures.push(
        `${result.printId}: fails ${failingDims.join(', ')} — ${failingDims.map((dim) => result[dim].reason).join('; ')}`,
      )
    } else {
      passCount++
    }
  }

  console.log('')
  console.log(
    `verify:prints — ${passCount} pass, ${warnCount} on the unverified list, ${failCount} fail ` +
      `(${vendorPrints.length} prints total)`,
  )
  console.log(
    `not-checkable by dimension: ${Object.entries(notCheckableCounts)
      .map(([dim, count]) => `${dim}=${count}`)
      .join(', ')}`,
  )

  if (failCount > 0) {
    console.error('')
    console.error('FAIL  verify:prints — prints below fail a checkable dimension and are not on the unverified list:')
    for (const failure of failures) console.error(`  - ${failure}`)
    console.error(
      'Either the figure is wrong (record it in printsUnverified.ts and add its id to the baseline, with the owner\'s word) or the check has a bug.',
    )
    process.exit(1)
  }

  console.log('verify:prints passed')
}

main()
