# Independent review of the leased Orca diagnostic

The reviewed unit has no remaining blocking finding. I recommend the existing bounded manual diagnostic path, followed by restoration of the exact disabled plan. This review grants no source qualification, normal intake, semantic, publication or scheduled-run credit.

## Reviewed boundary and pins

The implementation keeps the current whole policy at `8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db` and Orca's registration at `candidate`. The operational plan selects only `orca:official:1`, at most 60 index reservations and one deterministic primary sample. Its raw and canonical SHA-256 are both `93257fbffe11598ffff5ee7b890fdd0e992d59d4b276d0ad09aa8ddfe56f7d98`, with 1,040 bytes.

The host and OrbStack copies matched these stable implementation hashes before testing and remained unchanged at the final check:

| File | SHA-256 |
|---|---|
| `ops/ci/collect.py` | `f1569eb265112efb51611eaa244f882bc02d1e2b19a3683860ecd3ca19a16c62` |
| `web/scripts/pipeline/orca_qualification.py` | `731ee99cdc88bc4e69ef135f4c2e60f75248bc4db9bc389a3b5aa5773457935d` |
| `ops/ci/test_leased_orca_probe.py` | `fc75b61e7b049112aac09354cbb5ba76d61e4a2b558f2a64740d260c7dd84416` |

The plan joins the exact current candidate source hash `11dc1755e9febe013fbc5d35a636afc948432251f6186cf62ce3effcb5cac4cf`, original whole-contract bytes and the archived endpoint proof. The proposed adapter hash is `6b64c7c761c899e28297fe3e8bf18784dbf6da9dcb88f2d2d7ccab1671c963b2`. The original observation remains dated `2026-10-23T04:14:41.172921Z`; it records the original press-releases request and its news-index destination. No date is renewed by preflight.

## Independent execution and counterchecks

All scripts and tests ran in OrbStack. The 29 focused Orca module and leased-entry tests passed. A separate run of 46 existing leased-source, budget and disabled-plan tests passed. An initial extra-suite invocation named a nonexistent test module; the corrected command below passed all 46 tests. There was no runtime failure behind that invocation error.

```sh
PYTHONPATH=ops/ci:web/scripts/pipeline:web/tests PYTHONDONTWRITEBYTECODE=1 \
  PYTHONPYCACHEPREFIX=/tmp/smp-orca-independent-review-cache \
  python3 -m unittest test_leased_orca_probe test_orca_qualification -v

PYTHONPATH=ops/ci:web/scripts/pipeline:web/tests PYTHONDONTWRITEBYTECODE=1 \
  PYTHONPYCACHEPREFIX=/tmp/smp-orca-independent-legacy-cache2 \
  python3 -m unittest test_leased_source_probe test_onboarding_budget \
    test_disabled_qualification_plan -q
```

Four additional temporary-fixture counterchecks used the real leased caller and pure historical replay:

| Countercheck | Retained result |
|---|---|
| The final caller timestamp capture advances the monotonic clock to the deadline. | Three charged responses remain, index traversal remains complete, evidence and execution become incomplete, and the deadline denial replays exactly. |
| The final caller timestamp capture crosses UTC midnight. | Three charges remain on the original day, no next-day reservation is made, evidence and execution become incomplete, and the day-change denial replays exactly. |
| A reservation succeeds, then the immediate pre-transport guard expires. | No HTTP call occurs, one reservation stays charged, and the request denial plus both completion denials are retained. The denial counter is three. |
| The first transport raises an error. | One reservation stays charged, no inventory or sample completion is invented, and historical replay reproduces incomplete evidence. The diagnostic execution itself may finish successfully because transport failure and budget denial are distinct outcomes. |

The checked-in repeated-denial test also proves that identical module and caller denials remain two events. Removing one event while keeping its counter fails replay. The finalizer derives pages, inventory, primary sample, reason, readiness and lifecycle fields together from the original request records. It does not merely change completion flags.

The leased tests exercise the actual entry point and checkpoint code with fictional remote transport. They check private manual-main context, lease acknowledgement, fetch-only escrow acknowledgement before HTTP, exact archive compare-and-swap ancestry, preservation of normal heads and budget counters, cancellation, failed escrow, failed final acknowledgement, invalid proof, changed live plan and exhausted daily allowance. The archive acknowledgement fixture uses the real return shape: `commit`, `parentCommit`, `manifestSha256`, `files` and `ref`. Auth restoration, model construction, corrections, normal collection, snapshots and publication are forbidden in that fixture and are never called.

## Actual acknowledged archive preflight

I independently reran the read-only preflight against:

`/var/tmp/smp-html-collection-40120612027-20261024/extracted/jessepike-sec-market-b78bd35bb531ed49480ce1557780d3b2d9a522a2`

The manifest digest is `3971ae961442d6a18c5ed145c64660d68190d91f470acf27b74c3d136f6d6849`. Every one of its 40,917 entries passed hash and byte-size checks. The independently reconstructed plan exactly matches the committed 1,040-byte operational plan. It validates against the archive with no missing-object overlay, no MemoryStore mutations and no network, subprocess or filesystem-write guard attempts.

The archive contained 40,921 files and 1,904 directories. Before and after seals matched:

| Seal | SHA-256 |
|---|---|
| File content inventory | `4a62d684028c83306c446b4468685abd2b2ec6d48c9d2ce2b6c64473f0816a09` |
| File modification times | `41afa5b58bf402a96da392552113918a9055fbdaa37749a799423528b9d49a14` |
| Directory modification times | `0d09fc1fd0fd80ec691efb26c61f624330f7a22f8938de492403eb487e47779a` |

The preflight output is retained at `/tmp/smp-orca-independent-preflight.json` inside the dev VM. The independent countercheck output is `/tmp/smp-orca-independent-edges.json`; its ignored reproduction script is `.ctx/orca-independent-edge-review.py` in the finish worktree. These local artifacts are supporting evidence, not authority for registration.

## Historical replay and operational limits

The pure replay path authenticates the immutable original raw-plan reference, source-bound observation wrappers, body bytes, response times, request sequence and charge interval. The leased test replaces the live plan with the exact 173-byte disabled plan, SHA-256 `ad1c5cc234fe4fa69cbceb5370ac74825a37dc80b08528ca908d14b1352e53b4`, then successfully replays the original report without writes or transport. External Actions, artifact and archive authentication remains the responsibility of the actual receipt review; a self-consistent replay is insufficient for source activation.

The existing workflow keeps probe runs separate from ordinary account collection and records their bounded nonsecret receipt. A probe does not create a normal collector checkpoint or earn scheduled-publication credit. The temporary plan must be restored after the actual diagnostic, and exact-code publication guards remain applicable to the final reviewed main revision. The review does not authorize changing H, adding Orca to normal intake, refreshing old semantic facts or spending model/document allowances.

Only this new review document and ignored review scratch were written during this task. No implementation, contract, source registration, acknowledged archive, source response or production state was changed.
