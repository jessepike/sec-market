# Independent review of the prospective v2 baseline migration

Verdict: no actionable finding in the reviewed inactive unit. The production authority list is empty. This review does not authorize an actual source activation, select a future whole-policy hash or certify a production collection.

## Reviewed files

| File | Raw SHA-256 |
| --- | --- |
| `web/scripts/pipeline/daily_baseline_migration.mjs` | `bee841bd212173aa727d2d3569fafe19d11c55dd2c55e5e91329747635a1d0eb` |
| `web/scripts/verify-daily.mjs` | `553a53b78118ddb593779c505ea3c57638948e59b29180f37a854eefcf284276` |
| `web/tests/daily-migration.test.mjs` | `7a3751129512c6a86d18000d30cb761e667956eb9a8c95ab7dfa4ca3a9d20953` |

The review inspected the pure validator, packaged original byte pins, production wrapper, synthetic dependency boundary and its placement inside the existing daily verifier. No reviewed implementation or asset was edited.

## What the guard proves

The build-facing function supplies only fixed packaged original bytes, their fixed pins and the source-controlled authority array. Caller-supplied synthetic dependencies enter a separate fixture function; `verifyDaily` does not call it. The synthetic complete-origin marker in the tests is fixture evidence only and is not installed as production authority.

The guard requires exactly one static authority selecting the complete current contract hash. That authority pins the original contract, full original public fixture, exact raw fixture length/hash, seal and transition pointer. Exact current-contract selection is the positive trust boundary for the proposed three source rows; this browser/build helper does not independently fetch or replay qualification evidence. The backend origin authority, complete original proof replay and external run/archive review remain separate prerequisites.

The original and current policies must preserve source identity/order and every field outside the three exact Ping/Delinea/Sonatype rows. Only their candidate-to-verified shape is permitted here; the fixed approved resulting whole-policy hash prevents an unreviewed alternate adapter from becoming eligible. Both policies retain the same required denominator, fixed at 557 for this migration.

The full superseded wrapper has a closed shape and must equal the packaged original policy, original snapshot and seal. Equality includes the entire nested superseded chain. Every other original top-level public field is preserved, including SEC records, dates, queue/provenance fields and historical projections. The new baseline must retain the old run and check dates, have zero successful tasks, all obligations uncollected, and zero unevaluated processing/history totals at aggregate and per-source grain. It cannot borrow success from the previous policy.

## Existing path compatibility

The new call is confined to an uncollected v2 snapshot whose superseded snapshot also has v2 coverage. The collected v2 branch still performs the existing source/measure/partition checks. The existing v1 path and v1-to-v2 prospective path retain their previous checks. Returning from the narrow migration branch does not skip the enclosing `verifyDaily` seal, current-contract, snapshot-address, timestamp, event/evidence or supplier-value checks, which run after `verifyV2` returns.

This is a public build baseline rule. It does not alter the normal collector, private execution, budget controls, semantic admissions or runtime canary. A seeded object archive with old-policy coverage still cannot pass the strict current-contract canary until a genuine new-policy collection exists.

## VM verification

The following command completed with 16 passed, zero failed and zero skipped tests in OrbStack:

```text
cd /mnt/mac/Users/jessepike/code/projects/sec-market-finish-20261022/web
node --test tests/daily-migration.test.mjs tests/daily-release.test.mjs tests/daily-app-metadata.test.mjs
```

The five migration cases include exact original byte pins, an explicitly fictional positive dependency, rejection through the real build verifier with an empty production authority, changed original raw bytes/seal/nested history/transition and altered dates, SEC projection, nonzero intake, evaluated history, nonzero source processing and an extra policy source edit. The existing release cases independently retain legacy metadata, quiet-source behavior, full denominator, exact seals, verbatim citations and collected-v2 intake distinct from unfinished processing/history. Existing prospective tests reject changed original dates/facts and invented reviewed history.

## Activation boundary

Before any future authority is populated, independently verify the actual V5 external run/artifact/archive, exact complete qualification origins, closed final contract/transition, original packaged assets, six correction group projections, all 80 existing SEC claims and current facts. The root's final build, rendered preview and actual post-activation collector/canary receipts are still required. This bounded review does not claim those later steps passed.
