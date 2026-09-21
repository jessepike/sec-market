/**
 * Signs the one draft issue on the trunk, turning a machine proposal into a
 * published judgment (SEC-MARKET-PUBLISH-001 §2.2). Run from `web/`:
 *
 *   npm run sign:issue -- --signed-on 2026-09-20 [--id 2026-w37]
 *
 * `--signed-on` is required and must be `YYYY-MM-DD`, a real calendar date,
 * in the owner's timezone (America/Los_Angeles) — the caller (normally
 * `scripts/publish-issue.sh`) computes that date from the approval event, not
 * from when this script happens to run. `--id` is an optional safety check:
 * when given, it must name the one draft found, or the script refuses.
 *
 * Pure logic lives in `signIssueLogic.ts` and `signIssueRender.ts`; this file
 * is the thin CLI shell — argument parsing and the one file write.
 */
import { existsSync, writeFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { issues } from '../src/data/issues/index.ts'
import { AUTHOR_NAME } from '../src/data/meta.ts'
import {
  AlreadyPublishedError,
  computeSignedIssue,
  findDraftToSign,
  isValidIsoDate,
  postureDeltasDroppedCount,
} from './signIssueLogic.ts'
import { renderIssueModule } from './signIssueRender.ts'

const __dirname = dirname(fileURLToPath(import.meta.url))
const ISSUES_DIR = resolve(__dirname, '../src/data/issues')

function parseArgs(argv: string[]): { signedOn: string; id: string | null } {
  let signedOn: string | null = null
  let id: string | null = null
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--signed-on') {
      signedOn = argv[i + 1] ?? null
      i++
    } else if (argv[i] === '--id') {
      id = argv[i + 1] ?? null
      i++
    }
  }
  if (signedOn === null) {
    throw new Error('sign-issue: --signed-on YYYY-MM-DD is required')
  }
  return { signedOn, id }
}

function main(): void {
  const { signedOn, id } = parseArgs(process.argv.slice(2))

  if (!isValidIsoDate(signedOn)) {
    throw new Error(`sign-issue: --signed-on "${signedOn}" is not a valid YYYY-MM-DD calendar date`)
  }

  const draft = findDraftToSign(issues, id)
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
