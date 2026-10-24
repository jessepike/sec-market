# Orca diagnostic integration under unchanged H

Status: implementation specification. This unit permits an Orca-only fetch diagnostic through the existing manual main `source_probe` path. It grants no source registration, normal intake, semantic, publication or timer credit. H remains exactly `8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db`.

## Narrow routing

The actual operational path is `contracts/source-qualification-probes.json`. In `ops/ci/collect.py:execute_source_probe`, read its bounded raw JSON and select only exact `bounded_orca_qualification` for `orca_qualification.validate_plan`. All other operations continue through the unchanged onboarding validator and dispatcher. Unknown or malformed operations fail before escrow or transport. No arbitrary URL or new workflow input is added.

After the existing source-probe context/lease checks, instantiate the same `PersistentProbeBudget`, install cooperative cancellation, and acknowledge the same fetch-only remote escrow before calling the Orca module. `execute` rechecks exact committed raw-plan bytes before its first reservation. A source-probe session still returns before HTML seed import, account restoration, model construction, corrections, normal collection, snapshotting or publication. The whole policy, H authority/seed package and existing three-source historical replay remain unchanged.

## Final guards and immutable replay

A naive route is insufficient: the existing collector's extra final guard changes lifecycle fields and budget context after a diagnostic has already sealed itself. With Orca, expiry at that boundary leaves self-reported readiness inconsistent with independent body replay. The reviewer reproduced `ORCA_REPLAYED_RESULT_DIFFERS` with a complete temporary report followed by that caller mutation.

Add operation-aware finalization to the Orca module. It captures the final timestamp between pre/post guards, records each actual final guard denial in an ordered `completionDenials` array, retains a descriptive last `completionDenial`, and derives the entire report again from its unchanged raw requests/observations. Initial module sealing and caller sealing use this same implementation. A denial already recorded by module sealing is preserved when the caller also denies; the exact counter totals include every request denial and every retained completion denial. Do not refund, collapse repeated events or merely force completion flags false.

Keep immediate response-check times, original fetched times, source/adapter wrappers, body references and request reservations unchanged across finalization. Retain all partial URLs. The pure verifier checks the exact denial multiset, contiguous charge interval, unchanged non-fetch counters, complete sequential page graph, terminal, sample and resulting flags. Historical replay continues to load the original immutable plan reference after the live path is restored to disabled. Internal replay grants no external Actions authority.

## Exact operational plan and later restoration

Use the dormant module's closed schema-2 plan, fixed H whole-contract reference, exact Orca candidate/adapter digests and fixed historical endpoint proof. The bound is 60 index requests plus one inventory-selected primary sample, maximum61 logical fetch reservations. The standard fetcher, shared daily 5,500 cap, runtime limit, current-day checks, exclusive remote lease and archive compare-and-swap remain intact. New model/document/gate allowances are zero.

Before any actual dispatch, validate this exact plan against the latest fully authenticated acknowledged H archive through a read-only `MemoryStore`, with no missing-object overlay or writes. Independently authenticate the original start proof's observation/body hashes and dates. Retain the plan's raw/canonical hashes and original H bytes. A successful static preflight proves no new source response.

After review and deliberate main integration, the existing workflow may be dispatched with only `source_probe=true`. Its immutable result/artifact/archive must retain the original main revision and exact plan. Then restore the exact prior 173-byte disabled plan, raw/canonical `ad1c5cc234fe4fa69cbceb5370ac74825a37dc80b08528ca908d14b1352e53b4`, and freeze that reviewed main before the next natural publisher. Do not dispatch ordinary collection or publication for this diagnostic. A manual diagnostic's completion callback cannot earn scheduled-publication credit.

Ordinary collection does not read the probe plan, and the fixed H seed does not hash it. Restoration is therefore an explicit operational sequencing requirement, not a new policy bridge. Check that no queued normal/publisher run is pinned to the temporary plan commit. Collector and publisher already share the account concurrency group and remote mutation lease. A main code change also changes the publisher's exact-code identity; restoring a plan does not make a new app revision eligible for a previously acknowledged code/artifact gate. Existing publisher guards and natural allowance renewal remain authoritative. H2 activation is separate and stays pending the verified 264 publication.

## Files and acceptance

Change only `ops/ci/collect.py` within source-probe routing/finalization, the new Orca module/tests, a new focused leased integration test, this document and the exact operational probe plan. Do not edit onboarding, H/registration, seeds/authorities, baseline, workflow or gate rules.

Tests must exercise the real leased entry point with fictional archive acknowledgements/transport: fixed-H plan/proof preflight before escrow; lease and escrow acknowledgement before first request; exact final archive CAS; zero auth/model/correction/normal-head/publication work; invalid proof and stale plan with zero transport; failed escrow with its conservative ceiling retained; daily cap; cancellation; UTC/deadline at the caller's last guard; repeated module/caller denials; and immutable original-plan replay after disabled restoration. Keep the existing disabled and older schema paths covered without weakening them. Actual archived-body and current acknowledged-plan validation remain read-only, with hashes and modification-time seals preserved.
