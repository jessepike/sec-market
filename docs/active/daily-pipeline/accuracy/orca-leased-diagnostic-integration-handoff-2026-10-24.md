# Orca leased diagnostic integration

Status: implemented locally for independent review. No actual request, workflow dispatch, qualification, normal collection or publication occurred in this unit.

## Result and scope

The existing private manual `source_probe` entry point recognizes only the exact `bounded_orca_qualification` operation and routes it to the closed Orca helper. The helper accepts only whole policy H (`8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db`), the unchanged `orca:official:1` candidate, its fixed historical endpoint proof, and the fixed proposed adapter. Its maximum is 60 consecutive index responses plus one inventory-selected primary sample, with at most 61 logical fetch reservations. The standard fetcher can perform its existing bounded wire behavior within each logical request; this unit does not change that accounting contract.

The existing remote mutation lease, fetch-only escrow, 5,500 daily cap, current-day/runtime checks and archive compare-and-swap remain authoritative. No account, model, correction, normal-head, snapshot, gate or publisher path is entered. All non-Orca plan operations keep their existing onboarding route.

The extra collector final guard now uses operation-aware report finalization for Orca. Module and caller denials remain separate ordered events even when their reason strings match. Finalization replays original request reservations, immediate response-check times, raw observations, body bytes, complete page sequence and primary shape before returning derived completion fields. A late caller denial cannot preserve evidence readiness from an earlier successful module report. No charges are refunded. A cancelled or failed diagnostic retains its partial evidence and cannot return qualification or coverage credit.

## Exact files and pins

| File | SHA-256 |
|---|---|
| `ops/ci/collect.py` | `f1569eb265112efb51611eaa244f882bc02d1e2b19a3683860ecd3ca19a16c62` |
| `web/scripts/pipeline/orca_qualification.py` | `731ee99cdc88bc4e69ef135f4c2e60f75248bc4db9bc389a3b5aa5773457935d` |
| `ops/ci/test_orca_qualification.py` (unchanged prior unit) | `5a60b9e4baed46de347623bb7d2fa618088c7b3cb3b5ce781feedc0a9c3963ca` |
| `ops/ci/test_leased_orca_probe.py` | `fc75b61e7b049112aac09354cbb5ba76d61e4a2b558f2a64740d260c7dd84416` |
| `contracts/source-qualification-probes.json` | `93257fbffe11598ffff5ee7b890fdd0e992d59d4b276d0ad09aa8ddfe56f7d98` |

The new operational plan is exactly 1,040 canonical bytes; its raw and canonical hashes are equal. The old disabled plan is exactly 173 canonical bytes with raw/canonical SHA-256 `ad1c5cc234fe4fa69cbceb5370ac74825a37dc80b08528ca908d14b1352e53b4`. These tests construct their closed Orca plan from a fixed H asset and fictional original-proof fixture, so later restoring the live disabled plan does not invalidate their intended historical context.

The integration spec is `docs/active/daily-pipeline/accuracy/orca-leased-diagnostic-integration-spec-2026-10-24.md`. No market contract, registration, onboarding parser/dispatcher, H seed, activation authority, baseline, workflow or publisher guard was changed by this unit. Parent-owned status work remains separate.

## Actual archived preflight

`docs/active/daily-pipeline/accuracy/orca-leased-diagnostic-preflight-2026-10-24.json` records validation against the acknowledged H archive at `/var/tmp/smp-html-collection-40120612027-20261024/extracted/jessepike-sec-market-b78bd35bb531ed49480ce1557780d3b2d9a522a2`. Its commit is `b78bd35bb531ed49480ce1557780d3b2d9a522a2`; canonical manifest SHA-256 is `3971ae961442d6a18c5ed145c64660d68190d91f470acf27b74c3d136f6d6849`.

All 40,917 manifest entries passed byte-count and hash checks. Full before/after content, file modification-time and directory modification-time seals match across 40,921 files and 1,904 directories. The `MemoryStore` had zero mutations and no overlay. The guard recorded zero attempted writes, subprocesses or network operations during validation and final seals.

The original observation remains `observations/b5d6182ff2fed713a7cc26fea913c63719a2f97c369ff420be7212b8a360be9a.json`, raw SHA-256 `4d1106359471da8aa436527bd3324f4dfea325c0b9364a52537bb4aac203c757`, 596 bytes. It records the citation-source request to `https://orca.security/resources/press-releases/`, actual final URL `https://orca.security/resources/news/`, HTTP 200 and original fetched time `2026-10-23T04:14:41.172921Z`. Its 236,182-byte body SHA-256 is `9f0503f9a7c15f5a6e4686ebd9d3a4cf6be13626d43746154af19a7d1f627e54`. This proves the literal historical endpoint and captured first-page structure. It supplies no current traversal or complete qualification proof.

## Tests

The following OrbStack command passed 126 tests, with zero skipped tests:

```sh
cd /mnt/mac/Users/jessepike/code/projects/sec-market-finish-20261022
PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/smp-orca-installed-plan \
PYTHONPATH=ops/ci:web/scripts/pipeline python3 -m unittest \
  test_leased_orca_probe test_orca_qualification test_leased_source_probe \
  test_disabled_qualification_plan test_onboarding_budget \
  test_neutral_sec_qualification test_discovery_repairs -q
```

The 11 new leased-entry tests cover exact lease/escrow/CAS ordering with the real `GitArchive.push` return shape, unchanged non-fetch counters, original-plan replay after exact disabled restoration, caller expiry, repeated module/caller denials, UTC rollover, cooperative cancellation, tampered plan and original body before escrow, plan replacement during escrow, failed escrow/final acknowledgements and exhausted daily capacity. The existing 18 Orca tests retain actual immutable root-body replay, terminal/continuation/path failures, 60-page bounds, readable-primary requirements, charge forgeries and no-write internal replay. The older leased, disabled, SEC and parser suites remain in the focused run.

## Operational handoff and acceptance boundary

I recommend reviewing and integrating this one diagnostic route, then using only the existing `source_probe=true` dispatch. Independently authenticate the actual main run, attempt, artifact, final receipt, archive manifest and all retained observation/body/charge/time joins before treating its result as operational evidence. A complete report remains diagnostic evidence with zero qualified sources and zero source checks credited. Incomplete traversal, missing/blocked/redirected primary response, runtime/day denial or failed acknowledgement must retain their explicit result.

After that run, restore the exact disabled `ad1c5cc2...` bytes and independently replay the archived Orca record using its immutable original raw plan. The new test proves this replay does not depend on the current live plan. Freeze the reviewed final main before the natural publisher; no diagnostic callback counts as a scheduled collection or publisher gate. Any eventual Orca source activation is a separate exact policy transition after the existing 264 verified publication. Preserve all current H inventories, original proof dates, 33 current review-queue rows, old 32 holds and correction/quarantine continuity under that later transition.
