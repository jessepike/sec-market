import { buildStaleReport, buildStaleReportJson } from '../src/data/staleReport.ts'
import { securityDomains } from '../src/data/domains.ts'
import { evidenceById } from '../src/data/evidence.ts'
import { hypotheses } from '../src/data/hypotheses.ts'
import { allPressureRows } from '../src/data/platformPressure.ts'
import { vendorPrints } from '../src/data/prints.ts'
import { reconfirmations } from '../src/data/reconfirmations.ts'

// Prints the "Going stale" report (publish-path-spec.md §4.2) as Markdown to
// stdout by default, or `--json` as `{ asOf, staleClaimIds }` for a
// machine reader — scripts/reconfirmLogic.ts, via sign-issue.ts's
// `--reconfirm` path, is exactly that reader. The weekly gather job pastes
// the Markdown form under "Going stale" in the pull request body
// (docs/active/gather-brief.md). Report-building logic lives in
// ../src/data/staleReport.ts, pure and unit-tested directly in
// tests/stale-report.test.ts — this script only resolves the real data and
// today's date (or --as-of, for deterministic tests and reproducible runs).

function todayIso(): string {
  return new Date().toISOString().slice(0, 10)
}

function parseArgs(argv: string[]): { asOf: string; json: boolean } {
  const json = argv.includes('--json')
  const flagIndex = argv.indexOf('--as-of')
  if (flagIndex === -1) return { asOf: todayIso(), json }
  const value = argv[flagIndex + 1]
  if (!value || !/^\d{4}-\d{2}-\d{2}$/.test(value)) {
    console.error(`--as-of requires a value shaped YYYY-MM-DD, got: ${value ?? '(none)'}`)
    process.exit(1)
  }
  return { asOf: value, json }
}

const { asOf, json } = parseArgs(process.argv.slice(2))

const inputs = {
  domains: securityDomains,
  hypotheses,
  pressureRows: allPressureRows(),
  prints: vendorPrints,
  evidenceById,
  reconfirmations,
}

if (json) {
  console.log(JSON.stringify(buildStaleReportJson(asOf, inputs), null, 2))
} else {
  console.log(buildStaleReport(asOf, inputs))
}
