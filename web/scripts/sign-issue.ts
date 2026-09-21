/**
 * Signs the one draft issue on the trunk, turning a machine proposal into a
 * published judgment (SEC-MARKET-PUBLISH-001 §2.2). Run from `web/`:
 *
 *   npm run sign:issue -- --signed-on 2026-09-20 [--id 2026-w37] [--reconfirm]
 *
 * `--signed-on` is required and must be `YYYY-MM-DD`, a real calendar date,
 * in the owner's timezone (America/Los_Angeles) — the caller (normally
 * `scripts/publish-issue.sh`) computes that date from the approval event, not
 * from when this script happens to run. `--id` is an optional safety check:
 * when given, it must name the one draft found, or the script refuses.
 *
 * `--reconfirm` (SEC-MARKET-PUBLISH-001 §4.3): only present when the owner's
 * own approval contained the word `reconfirm`. When set, every judged claim
 * that is stale as of `--signed-on` (by effective date) and not named in the
 * draft's own `proposed.challengedClaimIds` gets one new entry in
 * `web/src/data/reconfirmations.ts`, dated `--signed-on`, credited to
 * `AUTHOR_NAME`, `via` this issue. Omitted (the default), nothing is
 * reconfirmed — re-dating a judgment under his name must be something he
 * said, never a side effect of signing.
 *
 * Pure logic lives in `signIssueLogic.ts`, `signIssueRender.ts`,
 * `reconfirmLogic.ts` and `reconfirmRender.ts`; this file is the thin CLI
 * shell — argument parsing and the file writes.
 */
import { existsSync, writeFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { securityDomains } from '../src/data/domains.ts'
import { evidenceById } from '../src/data/evidence.ts'
import { hypotheses } from '../src/data/hypotheses.ts'
import { issues } from '../src/data/issues/index.ts'
import { AUTHOR_NAME } from '../src/data/meta.ts'
import { allPressureRows } from '../src/data/platformPressure.ts'
import { vendorPrints } from '../src/data/prints.ts'
import { reconfirmations as existingReconfirmations } from '../src/data/reconfirmations.ts'
import { buildStaleReportJson } from '../src/data/staleReport.ts'
import {
  AlreadyPublishedError,
  computeSignedIssue,
  findDraftToSign,
  isValidIsoDate,
  postureDeltasDroppedCount,
} from './signIssueLogic.ts'
import { computeReconfirmations } from './reconfirmLogic.ts'
import { renderReconfirmationsModule } from './reconfirmRender.ts'
import { renderIssueModule } from './signIssueRender.ts'

const __dirname = dirname(fileURLToPath(import.meta.url))
const ISSUES_DIR = resolve(__dirname, '../src/data/issues')
const RECONFIRMATIONS_PATH = resolve(__dirname, '../src/data/reconfirmations.ts')

function parseArgs(argv: string[]): { signedOn: string; id: string | null; reconfirm: boolean } {
  let signedOn: string | null = null
  let id: string | null = null
  let reconfirm = false
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--signed-on') {
      signedOn = argv[i + 1] ?? null
      i++
    } else if (argv[i] === '--id') {
      id = argv[i + 1] ?? null
      i++
    } else if (argv[i] === '--reconfirm') {
      reconfirm = true
    }
  }
  if (signedOn === null) {
    throw new Error('sign-issue: --signed-on YYYY-MM-DD is required')
  }
  return { signedOn, id, reconfirm }
}

function main(): void {
  const { signedOn, id, reconfirm } = parseArgs(process.argv.slice(2))

  if (!isValidIsoDate(signedOn)) {
    throw new Error(`sign-issue: --signed-on "${signedOn}" is not a valid YYYY-MM-DD calendar date`)
  }

  const draft = findDraftToSign(issues, id)
  // Read before signing: computeSignedIssue below does not mutate `draft`,
  // but the published issue it returns carries `proposed: null` — this is
  // the only chance to see what the gather flagged as challenged.
  const challengedClaimIds = draft.proposed!.challengedClaimIds ?? []
  const signed = computeSignedIssue(draft, { signedOn, authorName: AUTHOR_NAME })

  const modulePath = resolve(ISSUES_DIR, `${signed.id}.ts`)
  if (!existsSync(modulePath)) {
    throw new Error(`sign-issue: expected issue module at ${modulePath}, not found`)
  }

  writeFileSync(modulePath, renderIssueModule(signed, AUTHOR_NAME))

  console.log(`sign-issue: signed "${signed.id}" as ${AUTHOR_NAME} on ${signedOn}`)
  console.log(`sign-issue: wrote ${modulePath}`)
  console.log('sign-issue: next, run "npm run verify:issue -- --write" to append the lock manifest.')
  // Grepped by scripts/publish-issue.sh so the pull request comment can say
  // when a proposed posture note was signed away unapplied. draft.proposed is
  // non-null here — computeSignedIssue above already throws otherwise.
  console.log(`sign-issue: posture-deltas-dropped: ${postureDeltasDroppedCount(draft.proposed!)}`)

  // Reconfirmation (SEC-MARKET-PUBLISH-001 §4.3). Computed against the
  // *pre-existing* reconfirmations (this signed issue is not published yet
  // at this point in the process, so it is not itself a valid `via` for
  // anything staleness-related — the staleness snapshot below is unaffected
  // by it either way).
  const staleReport = buildStaleReportJson(signedOn, {
    domains: securityDomains,
    hypotheses,
    pressureRows: allPressureRows(),
    prints: vendorPrints,
    evidenceById,
    reconfirmations: existingReconfirmations,
  })
  const { reconfirmations, added, challengedLeftStale } = computeReconfirmations({
    reconfirm,
    signedOn,
    issueId: signed.id,
    authorName: AUTHOR_NAME,
    challengedClaimIds,
    staleClaimIds: staleReport.staleClaimIds,
    existingReconfirmations,
  })
  if (added.length > 0) {
    writeFileSync(RECONFIRMATIONS_PATH, renderReconfirmationsModule(reconfirmations))
    console.log(`sign-issue: wrote ${RECONFIRMATIONS_PATH}`)
  }
  // Grepped by scripts/publish-issue.sh for the release comment. Printed
  // whether or not --reconfirm was given, so "reconfirmed: 0" is the
  // ordinary, expected line on every non-reconfirm publish.
  console.log(`sign-issue: reconfirmed: ${added.length}`)
  console.log(`sign-issue: challenged-left-stale: ${challengedLeftStale.join(',')}`)
}

try {
  main()
} catch (error) {
  console.error(error instanceof Error ? error.message : String(error))
  // Exit code 2 is a distinct, benign signal that scripts/publish-issue.sh
  // (coordinator review point L, 2026-09-21) checks for specifically: the
  // named issue is already published, so there was never anything to sign.
  // Every other failure keeps exit code 1.
  process.exit(error instanceof AlreadyPublishedError ? 2 : 1)
}
