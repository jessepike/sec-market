# Scheduled source freshness implementation

October 25, 2026. Future preview repair under
`/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/scheduled-source-freshness-cycle-spec-2026-10-25.md`.

The existing `force_refresh` flag now suppresses both successful receipt reuse and saved
run-download replay. It also leaves earlier immutable replay pointers intact instead of trying
to replace them with the forced cycle's new observation. New observations, source heads and task
receipts retain their normal persistence. Ordinary retries still reuse successful receipts and
saved downloads with their original clocks.

The collector selects forced refresh only when all five existing environment fields match:
GitHub Actions `true`, repository `jessepike/sec-market`, event `schedule`, ref `refs/heads/main`
and schedule `17 5 * * *`. Source probes return through their existing earlier path. Manual runs,
other branches/events and temporary acceptance crons keep their preceding selection behavior.
No workflow or trigger was added.

## Files and SHA-256

| File under `/Users/jessepike/code/projects/sec-market-finish-20261022/` | SHA-256 |
|---|---|
| `web/scripts/pipeline/engine.py` | `e471f18006a4899406510cdede42829476ba1945b58c420c61f6edce767a7e19` |
| `ops/ci/collect.py` | `d27a676d6adc50faa7004f109a5507fa2d441627f4709b65ba8de855b4f5a7d5` |
| `ops/ci/test_scheduled_source_freshness.py` | `84c7fe20666cbaa173173d7dbc98ac5e5a3072eef71a86f6fc31955a45147523` |

This handback is the fourth changed file. No other implementation surface was edited.

## Offline verification

All tests, builds and screenshot tools ran in OrbStack `dev`. No packages were installed.

| Check | Result |
|---|---|
| Focused scheduled-cycle regressions | 12 passed. |
| Full operational suite | 840 passed. |
| Full `npm test` | Lint, 377 data tests, 115 pipeline tests, gated build and 42 browser tests passed; one existing fixture-dependent browser test skipped. |
| Whitespace check | `git diff --check` passed. |

The focused tests cover an early manual cycle followed by a later same-day forced cycle,
ordinary receipt reuse, isolated saved-download replay, immutable pointer preservation, exact
schedule selection/exclusions and its actual `execute` wiring. An offline opener exercises the
real `Fetcher` HTTP 304 handler, including ETag/Last-Modified request headers, the later actual
request clock and original body/observation provenance. The responses are synthetic test evidence.

They also verify exhausted capacity, cancellation and execution deadlines before transport;
current-invocation full-response sharing; immutable SEC document retention with a genuinely
new index anchor; and unchanged-body semantic review reuse without additional model calls.
The full suite includes the read-only actual-archive tests that retain all six old correction
admissions and verify selected archive hashes, sizes and modification times. No frozen archive
was initialized with LocalStore or written. Synthetic tests use separate temporary stores.

When a forced cycle has no successful reusable receipt and has never written an ordinary replay
pointer, a later ordinary retry may need another bounded conditional request. No pointer is
overwritten and no allowance is refunded. This repair does not introduce a separate cycle ID.

## Render evidence

`web/scripts/shot.mjs` captured the actual production page and current local build at 1440 and
390 pixels. Local used its own port 18815. Both new local images exactly match the S1 local images:
zero changed pixels at 1440×8379 and 390×7749. Nothing visible changed.

Evidence is under
`/Users/jessepike/Documents/Codex/2026-10-22/security-market-pulse/renewal-20261024/`:

* `scheduled-freshness-production-1440.png` and `scheduled-freshness-production-390.png`.
* `scheduled-freshness-local-1440.png` and `scheduled-freshness-local-390.png`.
* `scheduled-freshness-visual-comparison.json` records pixel results and screenshot hashes.
* `scheduled-freshness-file-seals.json` records changed-file hashes and protected input checks.
* `scheduled-freshness-ops-tests.log` and `scheduled-freshness-web-tests.log` retain full output.

## Actual validation and release limit

Main remains `6d5e87feba4ffbc75e50f35cb564cb8fd91708ca`. The market contract, correction contract
and correction stamp still match their committed bytes. Source policy H, admissions, source
allowances and workflows were not edited. No commit, push, source intake, model/account request,
dispatch or production promotion occurred. Browser captures made ordinary requests to the public
site. Running recovery `40169973257` was not touched.

There is no implementation blocker. The repaired revision has not run on the genuine daily
timer, so it earns no actual collection or publication credit. I recommend keeping it on future
preview until current H scheduled/public acceptance is complete, independent review passes and
a code-bound release gate is available. Real validation still requires that repaired revision's
scheduled source receipts to prove the new transport clocks and provenance.

## Retained local validation evidence

The complete operational and web output, original pixel-comparison record and original implementation-file seals are now retained under
`/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/receipts/scheduled-source-freshness-cycle-2026-10-25/`. The manifest verifies raw and compressed log hashes, source file pins, screenshot bytes and dimensions, and the current reviewed code. The 840-test operational output is the complete standard unittest progress/summary log; it was not rerun in verbose mode for this retention pass. The complete web log records 377 data tests, 115 pipeline tests, the build and 42 passing browser tests with one existing skip.

`/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/receipts/scheduled-source-freshness-cycle-2026-10-25/manifest.json` is the retained entry point. `file-seals.json` pins this amended handback; `source-file-seals.json` preserves the earlier handback seal as historical evidence. All referenced source screenshots and logs remained unchanged. This retention pass made no source/model request, test rerun, archive write, admission, dispatch, commit, push or production change. It supplies no real-timer or publication credit.

### Cold forced retry limit, as independently reviewed

A cold forced cycle deliberately writes no run-download pointer. If its transport succeeds but semantic work is pending, a later ordinary retry can need additional conditional transport. The independent two-URL fixture spent two additional fetch reservations and completed, without an immutable-object collision or invented source time. Successful tasks in a cold partial cycle were reused while the failed task alone retried. This bounded cost is consistent with the explicit read/write suppression; it does not promise zero-fetch resumption or extend the existing last-good policy.
