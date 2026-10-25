# Cross-day public source inventory repair: independent review

Verdict: clean within the one-line repair. Use the original plan's `scheduledAt` to reconstruct its public source rows. Keep the current `now` for receipt reconciliation and freshness checks. No runtime change beyond that call-site correction is needed for this defect.

## Cause and correction

`contracts.plan_run` includes the UTC collection day in run and task identities. `reporting.inventory` regenerates that inventory and joins receipts by task ID. Passing the publication clock after midnight created another day's task IDs, leaving all 557 rows unchecked despite the aggregate's 264 successful checks. `snapshot.py:364` now passes `plan["scheduledAt"]`. `build_snapshot` still reconciles raw receipts against the current clock at line 231 and checks coverage age immediately afterward. Original source observations and expiry dates are not renewed.

The downloaded gate log at `/var/tmp/smp-gate-diagnostics-40148005688/extracted/test.log:2757` contains the reported refusal: `Daily v2 coverage completion differs from its source receipts`. This review inspected that extracted log; external artifact authentication is the root agent's separately retained evidence.

## Independent checks

All five new portable Python-to-JavaScript tests passed in OrbStack with a fresh Python cache. They exercise the real `build_snapshot` and unchanged `web/scripts/verify-daily.mjs`, including an honestly resealed former-failure snapshot, inconsistent gap/checked/review rows, preserved original timestamps, and expired evidence rejection.

Additional independent checks also passed:

- Reconstructed the old function in memory and compared the entire same-day snapshot with the repaired function. They are exactly equal, including hash `eef9600c0929c615afc6147b36f2a35de30a69f6695abeef1ebc038633a439c8` in the fictional fixture.
- Changed each of `sourceId`, `supplierId`, `registration`, and `family` in a checked source row, resealed each snapshot, and confirmed the actual JavaScript verifier rejected all four.
- Independently executed the actual JavaScript verifier against both complete archived replay outputs. The old projection failed with the exact gate error; the repaired projection passed.
- Recomputed the actual 557 required rows, 264 checked rows, 293 exact gap IDs, source/supplier/family/registration/required joins, four ordinary fact references, and 33 review queue entries. Every non-source-row payload field is exactly equal between the old and repaired projections; only source rows and their resulting snapshot seal differ.

The actual replay uses collection run `2c57fb25697bfc4b40df574890334adfa1d6d0df610837e12aa3a71e22515523`, original scheduled time `2026-10-24T18:28:54.713214Z`, and publication check time `2026-10-25T00:23:00Z`. It preserves last collection time `2026-10-24T18:32:51.588317Z` and valid-until `2026-10-26T00:29:16.957017+00:00`. Processing and historical review remain incomplete, with their original summaries and dates. The repaired actual snapshot hash is `8ae128c6f731631b2036a844745b2776ee0d146d3c1290f39bf0aad4b4bf3d00`.

## Evidence and pins

The implementation's actual replay receipt is [cross-day-public-source-inventory-fix-handoff-2026-10-25.json](/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/cross-day-public-source-inventory-fix-handoff-2026-10-25.json), raw SHA-256 `12dfc63318bd2135a0353ea2b519e07db5382be9901e3b4cbd335190a6a0e653`. Its full before/after payload `/tmp/smp-cross-day-snapshot-actual-full.json` in the VM hashes to `78a07679b64b2b94a26442800d7971fe0585e0d93d41f3d85653999453f275b3`; this review independently read that payload, verified its joins and differences, and ran both projections through JavaScript.

The implementation replay authenticates all 41,245 manifest entries of archive `ac0260ed95c3bf5090b236e42b3a7090a70c3861`, manifest `895213b31bb9f75814acc9484cad9aabd3719e07ddd72c621275a9b2568a1e5c`. Its before/after seals match for all 41,249 files and 1,909 directories, with zero write/network guard attempts. This review inspected the replay script and its sealed result rather than duplicating that full archive scan. The independent JavaScript checks used temporary fixtures only.

| Reviewed file | SHA-256 |
|---|---|
| `web/scripts/pipeline/snapshot.py` | `10b07fad6a1abbaa662ee141c43cd2ebfb6c40b890f35f8f412659fe1fc98b05` |
| `ops/ci/test_cross_day_snapshot_inventory.py` | `d473133a3f7097428a5d7316556e6ebe45f5b42d43f79b00c003a39517ae5bb6` |
| Unchanged `web/scripts/verify-daily.mjs` | `553a53b78118ddb593779c505ea3c57638948e59b29180f37a854eefcf284276` |
| Unchanged `contracts/market.json` | `24221c946781559c0ff3626e4e479c4647da915d0f2d7559ea88046982532c3c` |
| Exact disabled `contracts/source-qualification-probes.json` | `ad1c5cc234fe4fa69cbceb5370ac74825a37dc80b08528ca908d14b1352e53b4` |
| Unchanged `web/scripts/pipeline/source_qualification_origin.py` | `955ddadd22585672f677b533a6478034cb8048a0ec71faea37af0bfa74469bc6` |
| Unchanged `ops/ci/html_qualification_seed.py` | `68c66beda7c00e65361c90e7bc30efffc2e19a41804ae76ebffd40914d9236e4` |

Host and VM source/test hashes agree. Current canonical H remains `8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db`. The tracked runtime diff is exactly one changed line in `snapshot.py`; verifier, contract, origin and seed files have no diff.

## Acceptance boundary

This is offline repair evidence, not a successful external gate or publication. Root owns the isolated full-gate rehearsal, reviewed promotion, and re-enabling publisher workflow `393693283`, which was temporarily disabled to protect the remaining October 25 gate attempt. This review made no source/model requests, archive/state changes, budget changes, dispatches, Git operations or release mutations.
