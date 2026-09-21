# T7-4 evidence: re-confirming a stance (SEC-MARKET-PUBLISH-001 §4.3)

Nothing visible changes on the site at merge: `dist/index.html`, `dist/thesis/index.html`
and `dist/issues/2026-w36/index.html`, built from `origin/preview` and from this branch and
compared with hashed asset filenames normalized, come out byte-for-byte identical.

## How that was actually confirmed, including a bug this evidence step caught

The first diff was not clean. `thesis/index.html` and `issues/2026-w36/index.html` matched
immediately, but `index.html` differed on 144 lines, all inside the JUDGED/RECONFIRMED stamps.
The four call sites (domain stances, market picture, hypotheses, Platform-pressure rows) had
written the same visible words as three different literal JSX structures before this build, and
React's server rendering inserts `<!-- -->` hydration boundary comments between adjacent
children in a way that depends on exactly how the source grouped them, not on what the page
shows. The shared `JudgedStamp` component read correctly by eye but changed those bytes on two
of the four call sites. It now ships as three exports: `JudgedStamp` (market picture),
`JudgedStampSpaced` (domain stances), `JudgedStampStacked` (hypotheses and Platform-pressure,
both occurrences), each reproducing its call site's original shape exactly, verified by
rebuilding both branches and diffing the real `dist/` output down to zero lines, not by reading
the JSX. The component-level unit test asserts the same three exact strings, but against
`renderToString` (what the real `src/entry-server.tsx` uses), not `renderToStaticMarkup` (which
never emits these comments and could not have caught the mismatch — that was the original test's
blind spot). This cost an extra round: fixing the wrong shape, discovering `origin/preview` had
moved on with unrelated commits before this could be diffed against it (confirmed those commits
never touched `web/`), and then finding a second, different mismatch after the first fix looked
clean, because two of the four call sites had structurally distinct originals that happened to
render the same visible text.

## Stamp appearance with a reconfirmation

A temporary fixture reconfirmation (never committed) was added locally, the site rebuilt, and
the stamp captured at 1440 and 390px for one domain-board card and one Platform-pressure row
(mobile stack), then the fixture was removed and the build re-run clean. `git status --short`
after cleanup shows only this evidence folder as new.

At 1440px the stamp reads on one line: `JUDGED 16 AUG 2026 · RECONFIRMED 19 SEP 2026 · JESSE
PIKE`. At 390px the longer, reconfirmed form wraps: the domain-board stamp breaks onto two
lines, and the denser Platform-pressure stamp (smaller column width, monospace type) wraps onto
three. In both cases the wrap is a plain, ordinary line break — no clipping, no horizontal
overflow, no overlapping text — it just takes visibly more vertical space than the single-line,
never-reconfirmed stamp. Screenshots: `domain-board-stamp-1440.png`, `domain-board-stamp-390.png`,
`platform-pressure-stamp-390.png`.

## Claim id scheme

`${kind}:${id}` reusing each claim type's own existing stable id — `domain:network-sase`,
`hypothesis:<id>`, `platform-pressure:<id>` — never a new id space. Documented in
`web/src/data/reconfirmationHelpers.ts` and in the "As built" note added to
`docs/active/publish-path-spec.md` §4.3.

## Test counts

- `web/tests/reconfirmations.test.ts`: 33 tests, all passing (helpers, staleness, validation,
  `computeReconfirmations` — all 5 required scenarios plus 2 extra — module regeneration, and
  three `JudgedStamp` byte-identical checks).
- `npm run test:data` (all data test files): 187 tests, 0 failures.
- `npm run lint`: 0 warnings, 0 errors.
- `npm run build` (full chain, including new `verify:issue` check 17
  `reconfirmations-valid`): passes.
- `npm run test:e2e`: 37 passed, 1 skipped, matching the pre-existing baseline exactly — no
  e2e test needed to change for this feature.
- `npm test` (lint + test:data + build + test:e2e) run end to end: passes.

## Dry-run results, both flag values

Run against `origin/issue/2026-w37` in a disposable scratch clone (a bare repo outside both
checkouts, `preview` seeded from this branch's tip to stand in for "already merged," `main` and
the issue branch seeded from their real content), `DRY_RUN=1`, no pushes, nothing committed to
any real ref. Scratch directories were removed afterward.

- `RECONFIRM=false`, signed 2026-09-19: guard and build phases both pass; the local commit
  touches only `issues/2026-w37.ts` and `issues.lock.json`; `reconfirmations.ts` is untouched
  (still `[]`); `sign-issue` prints `reconfirmed: 0`; full `npm test` passes (37 passed, 1
  skipped).
- `RECONFIRM=true`, signed 2026-11-02 (far enough ahead that every judged claim is stale):
  guard and build both pass; the local commit touches `issues/2026-w37.ts`,
  `issues.lock.json`, and `reconfirmations.ts`; `sign-issue` prints `reconfirmed: 24`
  (6 domain stances, 4 hypotheses, 14 Platform-pressure rows — every currently judged claim,
  since this draft set no `challengedClaimIds`), `challenged-left-stale:` empty; `verify:issue`
  check 17 passes on the new entries; full `npm test` passes (187 data tests, 37 e2e passed, 1
  skipped).

## What cannot be verified without GitHub

The approval-word gate itself (an approving review or a `publish reconfirm` comment actually
resolving `RECONFIRM=true` in the live workflow) is `.github/workflows/publish-issue.yml`
plumbing that only runs on a real pull request; the dry run above starts from `RECONFIRM`
already resolved, matching how `scripts/test-publish-issue.sh`'s existing guard-logic tests treat
it. Live promotion to `main` and the fifteen-minute site poll (step 8) are also unverifiable
outside GitHub and were not exercised (`DRY_RUN=1` skips all pushes and the poll by design).

## What was noticed and left alone

The build phase currently reconfirms every stale, unchallenged claim in one pass with no cap;
for a project with many more judged claims than this one has today, a single `reconfirm` could
re-date a large number of stances at once. That is what §4.3 specifies and it is correct today.
Also noticed: `JudgedStamp`'s three-shape split is the kind of divergence that will bite a future
change unless the next person to touch this file reads the header comment, which says plainly to
verify any new shape against a real `dist/` diff, not against this test file.
