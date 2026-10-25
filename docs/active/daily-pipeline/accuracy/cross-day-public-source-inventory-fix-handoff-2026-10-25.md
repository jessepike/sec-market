# Cross-day public source inventory repair

The one-line repair is complete. Public source rows now use the verified plan's original `scheduledAt`, so their task IDs join the original source receipts after UTC midnight. Current-time reconciliation, source freshness and snapshot expiry still use `now`. The JavaScript verifier is unchanged.

## Actual failure reproduced

The authenticated gate diagnostic log at `/var/tmp/smp-gate-diagnostics-40148005688/extracted/test.log` records the exact build refusal: `Daily v2 coverage completion differs from its source receipts`. The diagnostic artifact is `12581695199`, ZIP SHA-256 `4aad5a069e8160c286d6d5b3cfaf0ed63f64c7ad217e1ed5e708b11b7a909f0e`.

Before editing the runtime, the actual retained ac026 snapshot and original coverage reproduced the failure through the unchanged `verifyDaily` function. Calling the existing row builder with October 25 produced 557 unchecked rows and 557 row gaps, while the verified aggregate still said 264 checks and 293 gaps. Using the original plan instant, `2026-10-24T18:28:54.713214Z`, produced the original task identities, 264 checked rows and 293 matching gaps, and passed the same verifier.

The new portable regression also failed with the exact JavaScript error before the repair. It passes after the call-site change:

```python
public_coverage["sources"] = inventory(contract, plan["scheduledAt"], verified)
```

## Exact files and validation

| File | SHA-256 |
|---|---|
| `web/scripts/pipeline/snapshot.py` | `10b07fad6a1abbaa662ee141c43cd2ebfb6c40b890f35f8f412659fe1fc98b05` |
| `ops/ci/test_cross_day_snapshot_inventory.py` | `d473133a3f7097428a5d7316556e6ebe45f5b42d43f79b00c003a39517ae5bb6` |
| Unchanged `web/scripts/verify-daily.mjs` | `553a53b78118ddb593779c505ea3c57638948e59b29180f37a854eefcf284276` |

Host and OrbStack hashes agree. The runtime diff changes only the inventory call's clock argument. The five new portable tests build actual synthetic pipeline snapshots and execute the real JavaScript verifier with honestly regenerated content addresses and seals. They check the cross-UTC join, original source times and task IDs, matching gap IDs, processing/history summaries, same-day compatibility, rejection of the former row join, rejection of inconsistent rows and continued expiry under the current clock. The fixture includes a checked source, a missing required family and pending document processing, so a passing aggregate cannot hide unchecked or unreviewed work.

The focused OrbStack run passed all 150 tests: five new tests, five midnight-partition tests, 25 separation tests and 115 pipeline tests. Fresh Python cache paths were used.

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/smp-cross-day-focused-cache \
  PYTHONPATH=ops/ci:web/scripts/pipeline:web/tests \
  python3 -m unittest test_cross_day_snapshot_inventory test_midnight_partition_replay \
    test_separate_freshness_history test_pipeline -q
```

## Actual complete snapshot and public verifier replay

The receipt is `/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/cross-day-public-source-inventory-fix-handoff-2026-10-25.json`, SHA-256 `12dfc63318bd2135a0353ea2b519e07db5382be9901e3b4cbd335190a6a0e653`, 27,960 bytes.

The replay authenticated all 41,245 manifest entries in acknowledged archive `ac0260ed95c3bf5090b236e42b3a7090a70c3861`, manifest SHA-256 `895213b31bb9f75814acc9484cad9aabd3719e07ddd72c621275a9b2568a1e5c`, at `/var/tmp/smp-seven-source-40131875060-20261024/extracted`. It used MemoryStore for derived objects and never LocalStore against that archive. Full raw receipt reconciliation, collector continuity and `build_snapshot` ran at `2026-10-25T00:23:00Z`. Both the old source-row projection and the repaired snapshot were then honestly sealed and passed to the unchanged JavaScript verifier.

| Projection | Checked rows | Row gaps | Public verifier |
|---|---:|---:|---|
| Original gate-day inventory call | 0 | 557 | Rejects the exact observed completion error. |
| Original collection-day inventory call | 264 | 293 | Passes, with exact original task IDs and matching gaps. |

The original broken snapshot hash is `6feec3970cb598b8edf8cea93b4af3d51eb903dc5ba7bbfb2b767fc8d6eff846`. The repaired hash is `8ae128c6f731631b2036a844745b2776ee0d146d3c1290f39bf0aad4b4bf3d00`, file SHA-256 `7017d65eebaa876ff3897b150523e60e2d2f1de442f003305242a6ba08aaaf81`. Excluding source rows and the resulting snapshot content address, every field is exactly equal between these full projections.

The replay preserves H, the 557-task denominator, 264 successful checks, the four ordinary fact references, 33 review entries, current processing/history summaries and all original receipt dates. `lastCollectionAt` remains `2026-10-24T18:32:51.588317Z`; `validUntil` remains `2026-10-26T00:29:16.957017+00:00`. Every source row's `lastCheckedAt` equals its original receipt's `completedAt`. No new check or review is claimed. The six existing correction groups and their immutable evidence were not edited; their archived bytes are covered by the full manifest and unchanged seals.

The 41,249 files and 1,909 directories retain identical before/after seals:

| Seal | SHA-256 |
|---|---|
| Content inventory | `f7bc3b2de1ef5ec65e8a3070a1a081fb3bea9b989714748ee3a9d3246de4b4cc` |
| File modification times | `68f9ac508d47b9b37d0d96ccb30b4e8cf4af5f40afb021247b9e7fe874c64413` |
| Directory modification times | `4eb6c0290521914d53fca3cb905aa9135bab079abef4556c9d2879f3dcea1e25` |

There were zero archive writes and zero source, model or network calls. The protected reconstruction recorded zero filesystem/network/subprocess guard attempts. The separate JavaScript verifier ran only against new temporary fixture files. The original plan remains disabled ad1, SHA-256 `ad1c5cc234fe4fa69cbceb5370ac74825a37dc80b08528ca908d14b1352e53b4`; H and the correction policy stamp were unchanged.

## Local reproduction and remaining release work

The ignored scripts are `.ctx/reproduce_cross_day_inventory.py`, `.ctx/replay_cross_day_snapshot_actual.py` and `.ctx/finalize_cross_day_snapshot_actual.py`. The full before/after snapshots and seals are under `/tmp/smp-cross-day-actual-verifier/{beforeSnapshot,afterSnapshot}/web/src/data/generated/` in the dev VM. The raw full-proof output is `/tmp/smp-cross-day-snapshot-actual-full.json`, with its hash and size recorded in the handoff JSON.

This unit verifies raw reconstruction and the public-source JavaScript guard. The parent owns the isolated full local release rehearsal, independent review, commit, promotion and any remaining real gate attempt. The failed gate remains charged. No budget refund, reset, external retry, dispatch, source collection or publication occurred in this task. File writes stop at this handoff.
