# Leased source diagnostics

Date: 2026-10-23. Implementation scope under the existing daily coverage repair. This does not activate sources or authorize new source families.

## Purpose and boundary

Standalone `pipeline/cli.py onboard` currently has a local persistent reservation lock but cannot acknowledge its ceiling to the shared remote archive before a request. It must fail before reading a contract, creating state, or constructing transport. The existing collector workflow will provide the bounded live diagnostic entry point. Standalone `archive-push` must require a full expected commit and pass it to the existing archive compare-and-swap implementation.

The collector gains the manual `source_probe` boolean, default false. It is accepted only for an actual private `jessepike/sec-market` GitHub Actions `workflow_dispatch` on `refs/heads/main`, with the dispatch input true and the actual run/attempt identity. Scheduled and ordinary manual collection retain their current behavior. The probe branch does not restore account auth, install an account client, create a model agent, extract facts, admit corrections, reconcile source checks, or invoke publication.

## Lease and remote acknowledgement

The existing restore, abandoned-run recovery, exclusive remote lease, budget escrow and expected-commit archive checkpoint remain the only durability implementation. The normal `github-<run>-<attempt>` session identity remains compatible with abandoned-run recovery. Bootstrap accepts the explicit `source_probe` checkpoint profile only in the guarded manual context. It writes that profile into both immutable session metadata and the lease, whose session digest also binds the complete metadata. Checkpoint reads this bound profile and rejects mismatches, unknown profiles, or use through native work commands. It does not accept a per-checkpoint bypass flag.

For this profile, bootstrap, budget reservation, finish and failure write diagnostic checkpoint objects under `ci/source-probe-checkpoints`. They preserve `heads/cloud-collector.json`, `heads/worker-heartbeat.json`, `heads/latest-run.json`, snapshots, normal cloud session proofs and `ci/collection-runs` byte for byte. The profile may write diagnostic observations and bodies, source-probe receipts, daily budget reservations/escrow, the existing lease, and remote archive acknowledgements. Source contracts and registration stay unchanged.

The sequence is: restore; acquire and remotely acknowledge the bound lease; create the real-current-day `PersistentProbeBudget`; persist the conservative fetch ceiling through `escrow_budgets`; await remote acknowledgement; restore the runner's known local starting counts; call existing `probe_sources`; archive a distinct run receipt; finish through the same expected-commit checkpoint. The bound diagnostic profile escrows fetches only and preserves calls/documents and other fields exactly, because it cannot run a model. The default collector still escrows all three existing counters. A failed ceiling acknowledgement starts no requests and retains the ceiling. A killed runner leaves the last acknowledged ceiling in the remote archive. Lease recovery never refunds unknown usage. No old bucket is reset.

## Bounds and results

The probe uses the current contract's candidate sources only, existing endpoint discovery and host/robots restrictions, four workers at most, and a 60–1200 second outer limit further bounded by the contract. The real UTC clock owns the day; no supplied observation time is accepted. Every attempted logical request reserves against the shared current-day fetch cap before transport, including failed requests. Existing calls/documents and extra ledger fields survive. No calls or documents are consumed by diagnostics.

Cancellation stops new transport. Deadline/day/clock validity is checked after escrow, before requests, after in-flight work and before final result construction. A late final request cannot produce `executionCompleted: true`. Budget, deadline, day or cancellation denial produces incomplete execution and a nonzero CLI outcome. An unavailable endpoint can be a completed diagnostic with zero qualification. No response, XML shape or diagnostic completion grants source coverage.

The nonsecret receipt is immutable `ci/source-probe-runs/<run>-<attempt>.json`, containing the actual GitHub identity, code/contract digest, diagnostic report and zero model calls/coverage/source qualification/publication. It contains no ordinary collection `runId` or claimed coverage counts. The final acknowledgement is returned only after the existing archive CAS succeeds. A failure produces only a diagnostic failure receipt/checkpoint, where persistence remains available. The manual publisher callback remains skipped by its existing schedule-only guard. Probe runs skip the collector alert step, so neither success nor failure closes or changes a daily collector alert. GitHub job results and diagnostic receipts retain failures.

## Verification

All tests use temporary fictional stores and mocked transport/archive/GitHub metadata in OrbStack. They verify manual/private/main guards before restore, profile binding and tamper rejection, lease/escrow acknowledgement before first transport, final expected commit chaining, protected state preservation on bootstrap/finish/failure, no account/model construction or normal collection proof, cap/day/deadline/cancellation behavior, remote failure retaining ceilings, CLI fail-closed behavior and mandatory expected commit. Existing collector and pipeline suites check the default profile remains unchanged. No live source, model, archive or production action is part of this implementation verification.

The candidate passed 21 focused leased-probe tests, all 415 operational tests and all 112 pipeline tests in OrbStack. The killed-run simulation retained the full acknowledged fetch ceiling and exact prior model counters. The midnight-during-escrow simulation started zero requests and created no new-day budget. No real diagnostic workflow was dispatched.
