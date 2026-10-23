---
project: Security Market Pulse
stage: Operate
updated: 2026-10-23
---

# Status

## Current checkpoint: October 23, 07:02 UTC

The owner approved activation and verification under D-110. GitHub `main` and `preview` are at
`7bd94ec77e99462c068f254e134235a894585cbb`. Production https://securitymarketpulse.com still serves
`54590be4d91113a50879a8fb5d180441e7d149f4`; the daily release has not been acknowledged live.
The legacy certified refresh and automatic promotion workflows are disabled. Vercel automatic
domain assignment is false and its exact main/archive Git-build ignore rule is installed;
fresh-runner probe [39909753143](https://github.com/jessepike/sec-market/actions/runs/39909753143)
confirmed the controls. Alias operations now verify and preserve those controls.

Daily collection is 05:17 UTC; publication is 06:23 and 16:23 UTC. GitHub had emitted none of the
new actual scheduled runs by this checkpoint. Date-bound October 23 retries at 06:07 and 07:07
UTC retain the normal schedule. Manual dispatches do not count as timer evidence.

Initial publication stays held until a genuine completed scheduled main collector has an immutable
receipt matching the current policy, actual GitHub identity and latest reconciled source coverage.
That hold consumes no independent-gate attempt. A successful scheduled collector can also trigger
the publisher through its verified GitHub callback. Duplicate temporary acceptance runs can verify
and reuse that same scheduled source work without new fetches, model calls, changed counters or
renewed source timestamps. The controlled rollback check follows an accepted publication only
after a read-only preflight verifies its actual scheduled source; its manual route remains available.

## Evidence and remaining limits

The first main gate [39908495114](https://github.com/jessepike/sec-market/actions/runs/39908495114)
passed 389 checks. Publisher [39908275916](https://github.com/jessepike/sec-market/actions/runs/39908275916)
staged its exact READY production artifact, then failed during high-level CLI alias handling.
Production stayed unchanged; owner-assigned [issue 9](https://github.com/jessepike/sec-market/issues/9)
remains the execution alert. Explicit team-scoped API operations and fixed failure categories now
replace that account-discovery path. The failed gate/publication attempts remain charged.

Latest validation: 83 operational tests passed locally in OrbStack. Hosted application runs
[39914573163](https://github.com/jessepike/sec-market/actions/runs/39914573163) and
[39914570279](https://github.com/jessepike/sec-market/actions/runs/39914570279), and canary
[39914569790](https://github.com/jessepike/sec-market/actions/runs/39914569790), passed.

The latest completed source collection remains manual run
[39899030431](https://github.com/jessepike/sec-market/actions/runs/39899030431): **244/557** checks,
including the complete SEC source cohort, with zero additional model calls. Its older runner exited
2 for incomplete coverage. Current code distinguishes completed execution from coverage gaps.
There remain 254 missing family bindings and 28 held claims. Full source coverage and sustained
operation are unproved. October 23 charged capacity remains 80 model calls, 40 documents and
5,367 of 5,500 fetches; no counter was reset. Restore the latest `refs/archive/market-evidence`
before writing state; credentials stay outside that archive.

Next evidence required: an actual scheduled collection receipt, accepted exact-artifact production,
controlled rollback and restoration, then independent monitoring and sustained operation. Do not
move main while a publisher is binding its main gate. No PR, purchase or paid API fallback is used.

[Activation and receipts](docs/active/daily-pipeline/activation-2026-10-23.md) ·
[Current operations](docs/active/daily-pipeline/github-operations.md) ·
[Earlier acceptance evidence](docs/active/daily-pipeline/finish-acceptance-2026-10-22.md) ·
[Coverage matrix](docs/active/daily-pipeline/coverage-matrix.md).
Implementation checkout: `/Users/jessepike/code/projects/sec-market-finish-20261022`.
Earlier checkpoints remain in Git history; the original checkout's local edits were preserved.
