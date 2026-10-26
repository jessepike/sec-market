# Historical Q4 test fixture repair

Root authorized this test-only repair after the dormant PR Newswire integration passed. The base
is finish commit `5a4df6e954e50564007e768b77a5d596de5a924c`. No runtime, gate, pipeline, policy,
workflow, generated source data, status, backlog, commit, push or dispatch change is authorized.
Independent review is required before a second scarce gate is spent.

## Failure and intended behavior

Publisher 40266519925 reached independent gate 40266928448. Its authenticated test log records the
historical H-to-J baseline test failing because it reads the newly prepared dailyMarket.json as
its historical migration fixture. A fresh J collection and the old zero-credit prospective J
baseline have different purposes and contents. The production verifier correctly rejects that
substitution. Its assertions and runtime behavior must remain unchanged.

The historical test will read a frozen copy of the already accepted prospective H-to-J snapshot.
Freeze its exact bytes from immutable Git blob 3794b800ffc9d691604d77ed1d06a3a8daebf517 at the base
commit, not from a mutable generated file. Raw SHA-256 is
`7120790449e8a4427446e2a62d69889cf651692153e6624359c50daa0379197f`,7,696,749 bytes.
The existing verifier independently authenticates its underlying H baseline using registry pin
`e1945874cb3f2cb661bf67671ec2bd760ae363761e21f85e3ea8d044afd91384`,5,108,696 bytes,
plus original policy, seal and exact transition. No fixture will be reconstructed from a fresh
snapshot or by reimplementing the verifier's projection.

## Owned change

Add a gzip-compressed test fixture under web/tests/fixtures with deterministic compression and
both compressed/raw byte/hash pins. Update only the historical test's snapshot input; keep every
existing policy, date, zero-credit and mutation assertion. Add a focused regression test that runs
the historical test under an injected fresh generated-snapshot read and proves it never consumes
that mutable input. The fresh overlay must not become an accepted historical migration fixture.
Runtime scripts, historical proof assets and source policies stay byte-exact.

## Verification and actual-input replay

Retain the authenticated original failure log and a local unrepaired counterexample. Verify the
frozen snapshot with the unchanged historical verifier before changing the test. Run both repaired
historical tests and the fresh-overlay independence counterexample. Then run full npm test in an
isolated exact current candidate with the auditor's nine prepared generated files applied.

The actual failed gate did not export its prepared snapshot. The auditor's sealed prepare_data
replay uses exact actual gate input 96d66bde96d333223557bdd78ef8df821b8e67a9, manifest
`4c00a5cc5c2cf162b6d1d7816236fd2561faf894f5adede334e6f3f33e3a6da3`,56,262 entries,
and an explicitly fixed local clock. Its resulting nine-file overlay is derived offline evidence,
not an export or rerun of the failed gate. Reproduce prepare_data against the current candidate
where possible, authenticate overlay/source/state before and after, and preserve all eight actual
admissions, old six public rows/dates and original source expiry. Use archived-only source input
with no network fallback or model/gate calls.

Pass criteria are unchanged historical assertions, a meaningful red-to-green overlay
counterexample, full actual-input-overlay npm test including all 80 SEC claims and browser checks,
and sealed source/state integrity. Passing the local replay gives no remote gate or publication
credit. Root owns any later main promotion, gate dispatch and live verification.

## Execution base update

Root accepted this specification and then committed only actual audit documents as 05ee1292,
above the pinned 5a4df6e9 candidate. The actual-overlay build will use that current commit with
only the owned test/fixture/regression patch. The frozen prospective baseline remains the exact
immutable 5a4df6e9 blob and retains its original hash. No runtime delta is introduced by this base
update.
