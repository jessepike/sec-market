# Historical Q4 test fixture repair

The test-only repair passes the full actual-input overlay suite and independent review. Root accepted the exact change and viewed all four new screenshots. The candidate is ready for root's commit and preview checks.

## Change and immutable evidence

The historical migration test now loads its accepted prospective H-to-J baseline from a pinned gzip fixture. Every original test body and assertion remains byte-exact. A new regression injects a fresh generated snapshot and proves the historical tests never read that mutable input. The original test fails on the actual derived overlay; the corrected regression fails against the original test; the repaired pair passes all three tests independently.

The fixture comes from immutable commit `5a4df6e954e50564007e768b77a5d596de5a924c`, Git blob `3794b800ffc9d691604d77ed1d06a3a8daebf517`. Its raw SHA-256 is `7120790449e8a4427446e2a62d69889cf651692153e6624359c50daa0379197f` (7,696,749 bytes). Deterministic gzip SHA-256 is `643cfc12299d2841d37ca7589fe76de56b9ba40266b1643c7e67d3213e71c051` (555,404 bytes). It was never derived from the fresh actual snapshot. The existing verifier still checks the original H proof, policy, transition and seal unchanged.

The repair is based on current commit `05ee1292e70ead4d54c0cdc8566c1a5101349866`. Only the historical test, its fixture, the new regression and repair documents/receipts are owned here. Independent review sealed 298 unchanged runtime, policy, workflow and script files. Finish generated data and all source/state/disabled-plan/requests/stamp files remain unchanged by this repair. Status and backlog belong to the actual audit worker.

## Actual-input replay and full suite

The failed gate did not export its prepared generated snapshot. This evidence is an explicitly derived, offline replay of the authenticated actual gate input. Archive `96d66bde96d333223557bdd78ef8df821b8e67a9` and manifest `4c00a5cc5c2cf162b6d1d7816236fd2561faf894f5adede334e6f3f33e3a6da3` authenticate 56,262 entries. The fixed local clock is `2026-10-26T04:15:20.629309Z`.

Current-candidate prepare_data independently reproduces the auditor's snapshot: raw SHA-256 `74cec6e38ca699353205b83d198de5141b0cf93486b8293890b60290791e96e4`, internal hash `4d5bf5bfa52f2d246bdea71b3a49704cd5f45aacf264038011df863fb18ceb81`. All eight actual admissions, the old six published rows/dates and original source expiry `2026-10-27T09:26:58.065250+00:00` are preserved. All 27,795 consumed state files remain unchanged and were rehashed independently after testing. All nine generated overlay files also remain byte-exact after testing/build. The read-only adapter's eight put calls only assert existing immutable objects; no state write occurred. Source/model requests, reservations and dispatches were zero.

The full `npm test` exits 0 in the isolated current candidate with that nine-file actual overlay: 380 data tests, 115 pipeline tests, all 80 SEC claims, build and 43 browser tests pass, with no skips. The exact command and working directory are in the JSON report. The earlier 1,015-operation PRN integration pass remains sealed; root explicitly excluded a repeat for this test-only repair.

## Retained failures and independent review

The original authenticated gate failure and all four gate diagnostic logs are retained losslessly. The first local regression harness inherited NODE_TEST_CONTEXT and returned success without running nested tests. Its log is retained as an invalid initial harness result. The corrected harness clears that variable, requires two child tests and two passes, fails against the original and passes against the repair. The first prepare_data adapter omitted put and failed before projection. Its failure note and corrected assertion-only adapter are retained.

Independent review is PASS at `docs/active/daily-pipeline/accuracy/receipts/q4-historical-test-fixture-repair-2026-10-26/independent/review.md`. It separately authenticates the frozen blob, runs the three green tests and both red counterexamples, checks unchanged assertions and 298 protected files, reviews the full suite, and rehashes state/overlay inputs. The copied independent receipt index SHA-256 is `ebbb61dec17ea1ee7ff4cbdb58e577ba45b4e20016658aceb73479c3ba8c9513`.

## Render comparison and release boundary

The finished build supplied all four new full-page renders at 1440 and 390 pixels; no rebuild occurred. Worker and root viewed all four. Layout and dimensions are unchanged. The derived private eight-group candidate shows 265/557 intake versus public 264/557, 52/11,185 documents reviewed versus 38/10,655, an October 26 rolling window versus October 25, nine restructurings versus ten, and updated qualified S1 text. These are data changes; no UI improvement is claimed. Production still serves the prior fc8 release. Absolute host image paths and hashes are in the JSON report and render receipt.

The local repair/replay supplies no remote gate or publication credit. Root owns commit, preview checks, main selection, the remaining native gate and live verification. No commit, push, source request, main change or gate dispatch was performed by this worker.
