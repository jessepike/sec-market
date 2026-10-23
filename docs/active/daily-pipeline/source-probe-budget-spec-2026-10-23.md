# Persistently budget source qualification probes

Prepared October 23, 2026. This closes the unbounded `onboard` fetch path before any future
source qualification. It changes no source, endpoint discovery rule, active registration,
coverage obligation, factual record, model allowance or publication route.

## Implementation contract

Add a `PersistentProbeBudget` context bound to the exact store object, full contract digest
and actual current UTC day. `probe_sources` must receive that explicit context; its previous
unbounded library call fails closed. The CLI's `onboard` branch creates the context from
`utcnow`, rejects `--at` and all native/subscription/model-worker flags, and keeps all other
CLI behavior unchanged. Operators must restore the verified real state before any future
probe; no actual onboarding is run during this implementation.

Before every logical `get`/`fetch`, take the existing `daily-budget-reservation` lock and a
compare-and-swap update to `heads/budget-<current UTC day>.json`. Increment only `fetches`,
preserving `calls`, `documents` and all additional counters. The cap is the contract's existing
`schedule.maxFetchesPerRun`, with a hard maximum of 5,500. Failed, blocked, timed-out and 304
requests retain their charge. Never reset, refund or alter an earlier day's ledger.

The context expires at the earlier of 20 minutes and the existing contract runtime bound.
Reject deadline expiry, UTC day change, invalid ledger or exhausted capacity before a new
fetch. At most four probe workers run. Existing fetcher timeouts and retry behavior continue;
the reservation unit is each logical probe request. An expired request already in flight may
finish, but cannot start another logical request.

Retain explicit reservation denial reasons and a context summary containing its initial
ledger and actual probe reservation count. Probe results always remain candidate,
unqualified and non-admitting, with no facts or coverage credit. They never modify the
coverage receipt, source registration or `heads/latest-run.json`.

## Verification plan

Use fictional fetchers and temporary synthetic stores in OrbStack. Prove zero requests and
byte-identical counters at a charged 5,500/80/40 ledger; serialized last-unit admission at
5,499/5,500 and separately 4,999/5,000; persistent charges for failures and 304 responses;
deadline/day-change rejection; a naturally later day's new bucket preserving the earlier
charged ledger; exact store/contract binding; CLI rejection of backdating and worker flags;
and unchanged candidate-only scope. No network, model, real archive write, quota operation,
workflow dispatch or Git action is authorized by these tests.

## Candidate verification result

All 16 dedicated tests passed in OrbStack using fictional fetchers and temporary synthetic
states. The full 5,500/80/40 ledger admitted zero requests and retained its exact bytes. Parallel
last-unit tests admitted one request at both 5,499/5,500 and the synthetic 4,999/5,000 cap.
Separate contexts shared the persistent lock correctly. Failed, blocked, 304 and timeout
requests kept their charges; deadline, day change and reservation persistence failures started
no new transport. The worker bound remained four.

The CLI returns exit 2 for reservation guard failures and rejects `--at` and worker flags.
Those reports explicitly set `executionCompleted: false`, `budgetDenied: true`,
`sourceChecksCredited: 0`, `qualifiedSources: 0` and `semanticAdmission: false`. An ordinary
unavailable endpoint can complete diagnostic work while retaining zero qualification and
coverage credit. No actual onboarding command, real ledger change, source request or model
call was run for this implementation.
