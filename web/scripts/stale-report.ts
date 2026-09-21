import { buildStaleReport } from '../src/data/staleReport.ts'
import { securityDomains } from '../src/data/domains.ts'
import { evidenceById } from '../src/data/evidence.ts'
import { hypotheses } from '../src/data/hypotheses.ts'
import { allPressureRows } from '../src/data/platformPressure.ts'
import { vendorPrints } from '../src/data/prints.ts'

// Prints the "Going stale" report (publish-path-spec.md §4.2) as Markdown to
// stdout. The weekly gather job pastes this output under "Going stale" in
// the pull request body (docs/active/gather-brief.md). Report-building logic
// lives in ../src/data/staleReport.ts, pure and unit-tested directly in
// tests/stale-report.test.ts — this script only resolves the real data and
// today's date (or --as-of, for deterministic tests and reproducible runs).

function todayIso(): string {
  return new Date().toISOString().slice(0, 10)
}

function parseAsOf(argv: string[]): string {
  const flagIndex = argv.indexOf('--as-of')
  if (flagIndex === -1) return todayIso()
  const value = argv[flagIndex + 1]
  if (!value || !/^\d{4}-\d{2}-\d{2}$/.test(value)) {
    console.error(`--as-of requires a value shaped YYYY-MM-DD, got: ${value ?? '(none)'}`)
    process.exit(1)
  }
  return value
}

const asOf = parseAsOf(process.argv.slice(2))

const report = buildStaleReport(asOf, {
  domains: securityDomains,
  hypotheses,
  pressureRows: allPressureRows(),
  prints: vendorPrints,
  evidenceById,
})

console.log(report)
