# Validation receipts

Actual checks in the Codex cloud checkout on 2026-10-20 UTC, Node 22.23.3, Python 3.12,
system Chromium. **Publication remains disabled; full-site daily operation has not passed.**

| Check | Result | Practical limit |
|---|---|---|
| Lint | Pass | JS/TS lint |
| Data/application tests | 251 passed, zero failures/skips | Includes exact snapshot seal, fixed task denominator, claim/evidence joins and freshness clock |
| Pipeline tests | 85 passed, zero failures/skips | Real store/planner/validation, archive transport against local Git, snapshot, artifact, recovery and publication logic; external service adapters use explicit doubles |
| Production build | Pass, 80/80 SEC checks, zero drift | Current exact committed SEC inputs, plus materialized daily snapshot; does not assert daily coverage complete |
| Browser tests | 32 passed, zero failures/skips | Desktop/phone behavior, public receipt agreement and overdue status after clock advance |
| Visual review | Full-page production/candidate captured and inspected at 1440 and 390 | Visible change: collection paragraph near headline and qualification beside SEC receipt; content below shifts 27px desktop / 61px phone |
| Actual subscription | Pass | Official ChatGPT login, real bounded extraction/review pilot and 80 collection calls; no paid API. Not a capacity guarantee |
| Actual collection | Degraded: 252/557 complete | 296 not checked, six failed, three blocked; 14 claims held, 8,875 URLs pending. Missing work is not removed |
| Remote evidence archive | Pass | Native Git push to private custom ref, about 1.5 GB raw state; no deployment branch change |
| Fresh remote restore | 19,998 files hash-verified | Commit `7924a44781fea3d4b038686feefc50d4f30551a7`; manifest SHA-256 `875227e57ebfcc8bd1ed51fca131e5a6dd72dc7db59993e56bb30df44b0d5324` |
| Restored independent reconciliation | Degraded, exact 252/557 reproduced | Successful restoration is separate from source completeness |
| SEC reconstruction from restored evidence | 80 proofs, 256 unchanged field leaves, zero failures | Independent isolated app copy, exact archived source bytes; no GitHub trust claim |
| Repeat unchanged certification | Pass | Last-data-change remains `2026-10-18T02:36:44.349Z`; later verification does not make source retrieval newer |
| Worker installation | Dry-run only | Mac/Linux schedule and launcher implemented; no persistent host activated |
| Vercel management | Official browser approval pending | Public GET/Git integration works; management stage/promote/rollback not exercised |
| GitHub independent gate | Implemented, not live-executed | Workflow must reach reviewed main; no self-declared trusted receipt accepted |
| Owner notification | Implemented, not delivered | Issue transport and account push/email settings still need actual delivery test |

Local raw receipts, logs and images live under `/workspace/sec-market-review-evidence/`; those paths
are not themselves durable hosted artifacts. Exact source bodies/reviews and collection receipt
are saved remotely under `refs/archive/market-evidence`. Ordinary fetches exclude that custom ref.
The independent fresh restore used a new mirror and state directory, not a copy of the live state.

## Failure/recovery checks

The suites cover immutable collisions, path escapes, stale CAS, real process-lock release after
crash, missing/duplicate/policy-mismatched task receipts, stale/future observations, broken 304
chains, SEC index retention, interrupted queues, subscription limits, daily budgets across policy
changes, rejected ambiguous claims, independently reviewed empty documents, partial-document
eligibility without source coverage, exact candidate/evidence/policy review hashes, future dates,
ARR/revenue and qualifiers. Snapshot/build seals, denied unknown field patches, artifact inventory,
real-shaped GitHub authority, stage/live receipt mismatches, journal recovery and forced rollback
are tested. Doubles do not prove actual Vercel promotion/rollback or notification delivery.

## Still required

Complete source bindings, bounded dated backfill and semantic delta capacity; historical claim and
category audits; typed ownership/financial-period adapters; actual trusted GitHub gate artifact;
official Vercel management connection, baseline/stage/probe/rollback; actual owner alert and missed
schedule; persistent host restart/recovery; full complete daily cycle and multi-day burn-in.
No supplier expansion or spending increase was performed. The earlier local-only foundation test
results (63 pipeline, 244 data, 30 browser) are superseded by the counts above. The earlier draft PR
was closed; delivery proceeds directly through preview under repository governance.
