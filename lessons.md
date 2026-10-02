# Lessons

Hot buffer. One line per insight, newest date first. Keep the last ~15; promote
cross-project patterns to the knowledge base and drop them from here.

## 2026-10-02

- [withheld:2026-10-02] A backgrounded tool call wrapping a command that ALSO backgrounds itself with a trailing `&` produces an orphaned, unreliable process — the wrapper returns immediately while the real work's survival across turns (especially across a session interruption) is uncertain. Pass the long-running command directly to the backgrounding mechanism without an internal `&`; that is the form that gives a trustworthy completion notification.
- [withheld:2026-10-02] After any session-rate-limit or similar interruption, a "completed exit code 0" notification for a background task is not proof it ran — check ground truth (a result file's timestamp/content, `ps aux`) before trusting it. One batch of this session's 74-supplier collector run silently never executed despite reporting success; only a timestamp check caught it.
- [withheld:2026-10-02] A script whose receipt file is overwritten by each invocation (by design, to reflect only that invocation's own findings) cannot be trusted as-is after running it multiple times in sequence for one combined result — `scripts/collect.sh`'s `collectorRun` block in `collectState.json` needed hand-merging across 7 batched runs so the site's reported failed-supplier count reflected the whole 74-supplier run instead of just the last batch.
- [withheld:2026-10-02] A supplier's own news counting as "unreadable" is only honest after a real fallback chain, not after one fetch failing — RSS/Atom, sitemap, an IR subdomain, a wire-service copy (GlobeNewswire/PR Newswire/Business Wire), and an EDGAR full-text search, in that order, with the failure detail naming which routes were tried.

## 2026-09-21

- [withheld:2026-09-21] `web/scripts/shot.mjs` needs Google Chrome and fails in the OrbStack VM. `docs/active/fable-run/evidence/baseline/capture.mjs` uses plain chromium and works there; copy it rather than modifying `shot.mjs`.
- [withheld:2026-09-21] A build-time meaning gate (fiscal period vs. source, `verify-issue.ts`/`verify-prints.ts`) can't be satisfied by editing a locked, hashed issue or a corrected-in-place standing table. The escape hatch is an explicit, dated exemption list read by the check (`corrections.ts`, `printsUnverified.ts`), not an edit to the checked data.

## 2026-09-20

- [promoted:kb:ea7ad6ea:2026-09-20] A syntax check on the machine that writes the script is not a syntax check on the machine that runs it. `scripts/gather.sh` passed `bash -n` on the laptop (bash 5) and failed to parse at all on macbook2014 (bash 3.2), because bash 3.2 cannot read a here-document nested inside command substitution and took the apostrophes in the prompt prose as opening quotes. The launchd job could never have run past its own first line. Check syntax on the target host, and keep here-documents at the top level.
- [promoted:kb:b481fe6f:2026-09-20] A guard that only ever runs on the cheap path proves nothing about the expensive one. Every gather run so far exited early on "nothing due" and wrote a clean receipt, which made the job look healthy while the line right after the model call was a parse error and the receipt's JSON broke on any multi-line error text. Force the long path with an override before believing a scheduled job works.
- [promoted:kb:0503a431:2026-09-20] Check the expensive precondition before spending the hour. macbook2014's Claude subscription login expired in May and returns 401 on the first call, which would have reached the receipt as a failed gather rather than as a host needing a person at a browser. The job now probes its own login for one token and reports `blocked-auth` by name.

## 2026-09-19

- [promoted:kb:d2c72b34:2026-09-19] A unit test that asserts against the live data array instead of a fixture is a time bomb, not a test. `thesisRunningScore` had a case named "is empty when there are no published issues" that read the real issues array, so it passed only while every issue was a draft and failed the moment the first one was signed. The test was wrong, not the code. Assert behaviour against fixtures; use live data only for invariants that must hold for every row.
- [withheld:2026-09-19] Page composition accepted on a spec is not page composition anyone has seen. The weekly-issue front page passed three external review rounds, a full e2e suite and five build gates, and still nobody had looked at it at full page height until the promotion render: it opens with a chronological list of funding rounds down to a $60.0K pre-seed, with the judgment below four lanes. Render the whole page at both widths at the point the composition changes, not at the point it ships.
- [promoted:kb:d4734a32:2026-09-19] A 12-day silent gap between build-review turns let a locally-committed change (`d2cae33`, an inbox intake) sit unpushed and undiscovered until session-wrap's own `git log`/`git status` pass caught it. Re-check `git status`, unpushed-commit count, and the D-65-style owner-action list at the start of any session that resumes after a long gap, not just at wrap.

## 2026-09-05


## 2026-09-04


## 2026-09-03


## 2026-08-28


## 2026-08-27

- [withheld:2026-08-27] A purchase price allocation says what an acquirer thinks it bought. Two AI security deals put almost the whole price in goodwill and assigned nothing to customer relationships, while an adjacent deal in the same filing put $464M of $476M into customer relationships. That contrast is stronger evidence than any figure either company would state directly.

## 2026-08-22


## 2026-08-20


## 2026-08-19

- [withheld:2026-08-19] A figure in a record's `note` field is not interchangeable with one in its `value` field. Falcon Cloud at $800M is an absolute amount; every other row in that table is a growth rate. The delegate caught this and was right.

