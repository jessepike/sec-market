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
| Vercel management | Official OAuth and existing project/deployment inspection passed | Owner account confirmed; no production settings changed |
| Vercel prebuilt staging | Adapter upload, exact receipt and all 24 static-file hashes passed | Root-directory defect corrected; cloud network restriction resolved. No production promotion/rollback executed |
| Vercel rollback baseline | Actual immutable production receipt imported and verified | Baseline is retained; executing production rollback remains untested |
| Real staged browser suite | 32 passed | Cloud proxy configured for API requests; Vercel preview toolbar disabled at test-deployment creation, project setting restored exactly afterward |
| GitHub independent gate | Implemented, not live-executed | Workflow must reach reviewed main; no self-declared trusted receipt accepted |
| Owner notification | Implemented, not delivered | Issue transport and account push/email settings still need actual delivery test |

Local raw receipts, logs and images live under `/workspace/sec-market-review-evidence/`; those paths
are not themselves durable hosted artifacts. Exact source bodies/reviews and collection receipt
are saved remotely under `refs/archive/market-evidence`. Ordinary fetches exclude that custom ref.
The independent fresh restore used a new mirror and state directory, not a copy of the live state.

Actual GitHub full-suite run [39510441692](https://github.com/jessepike/sec-market/actions/runs/39510441692)
passed on implementation `b8f6ecb4d10c7f05f51a3ad156cdd7e1ee31866e`.
The stable Vercel preview's `/app-release.json` acknowledged that revision; `/daily-coverage.json`
reported the exact run, 252/557, incomplete and automation disabled. Production still acknowledged
`54590be4d91113a50879a8fb5d180441e7d149f4`. The independent data-release gate is a separate workflow
and remains unexecuted; this web CI run must not be substituted for its evidence-bound artifact.
GitHub's billing usage endpoint returned 403 for the integration, so remaining account quota and
spending caps are unverified. No paid capacity or billing configuration was changed.

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
Vercel baseline/live probe/promotion/rollback (management connection and staging are verified); actual owner alert and missed
schedule; persistent host restart/recovery; full complete daily cycle and multi-day burn-in.
No supplier expansion or spending increase was performed. The earlier local-only foundation test
results (63 pipeline, 244 data, 30 browser) are superseded by the counts above. The earlier draft PR
was closed; delivery proceeds directly through preview under repository governance.


The remote browser run first exposed direct-DNS failures in Playwright API requests and Vercel's
preview-toolbar injection conflicting with the existing CSP. A cloud-only override now uses the
existing credential-free proxy. A fresh prebuilt test deployment was created with preview feedback
disabled; all 32 unmodified browser assertions passed, and the project setting was restored to its
original null value. All 24 files on that final deployment also match the tested hash inventory.
Production feedback, security headers, aliases and promotion controls were not changed.


The subsequent adapter fix and current cloud-scheduling research were delivered directly on preview
as `530af0b9da4ba9d20ca07ec113b7c57136cdcaf4`; its actual GitHub full suite
[39519068246](https://github.com/jessepike/sec-market/actions/runs/39519068246) passed.
The final staging/browser/baseline evidence is archived at
`d38721ca1e1e6b2869c1dfb2dbce14024270ce3c`, manifest SHA-256
`07d9bd0426c7b85c48920973f5ebf25ab611cf33db8b1b28cb7d9d4792809110` (20,010 files).
The pinned fresh restore proof remains the earlier 19,998-file archive; no second restore is implied.


## Native cloud execution delivery and live canaries (October 20, 2026)

Commit `6a43ed1c4a9439fc9ef0ddc13fb76bfab3f54299` is on preview and acknowledged by Vercel.
[Actual full GitHub CI 39523581752](https://github.com/jessepike/sec-market/actions/runs/39523581752)
passed: 251 data, 91 pipeline and 32 browser tests, with 80 SEC proofs and zero drift. Added
adversarial checks cover native strict schemas/roles/policies/staleness/contradictory replies,
separate review context, capped-budget replay without duplicate fetches, real Git fresh-session
restore/lease exclusion, expired-lease recovery and stale archive writers. Full-page renders at
1440/390 were inspected; no additional visible change beyond the existing preview disclosure.

The actual native wrapper restored and verified the 20,010-file remote archive, acquired a remote
lease and archived a supervised one-source known-fact canary. Fresh HiddenLayer source bytes
matched the prior body hash; the funding statement passed one actual official ChatGPT CLI review
in a different isolated context. The native collector and review context IDs, task/policy/body
hashes and fact date are retained. Three native work reservations include a diagnostic duplicate
caused by reordered metadata; none was refunded or reset. One document and one fetch were reserved.
This tests the durable queue with actual evidence, not fresh scheduled-VM authentication or a
new market announcement. The historical canary did not update site events or full-run coverage.

Owner notification canary: private [issue #7](https://github.com/jessepike/sec-market/issues/7)
was created with jessepike assigned, then the same issue was acknowledged closed on controlled
recovery. The first recovery query returned a stale empty listing; a current updated-order listing
and no-cache API request resolved it. Phone/email delivery and scheduled watchdog execution are
not proved by the issue API cycle.

Native finish independently retained 252/557 incomplete coverage, 14 held claims and zero new
site events, exited 2 as required, archived its final receipt and released the lease. Latest remote
archive `02c04f568c010e4fa036bd90c791bd9ece01e6e7`, manifest SHA-256
`26f7d3249981cdb983ff6339c5f7237bdd2e57bd5c02ce49c66cddd3d50972df`, has 20,035 files.
A separate fresh remote restore verified all 20,035 and confirmed all canary responses, the retained
3/1/1 budget, released lease and owner-alert receipt. This supersedes the earlier restore-count
limits above. Ordinary old local state is now stale and must not overwrite newer remote heads.

No recurring native schedule has been created; the saved environment draft is not published by
this chat. [Exact UI handoff and prompts](scheduler-handoff.md) are pinned to the tested commit.
Full source onboarding, fresh scheduled execution, actual production gate/cutover/rollback,
missed-worker delivery and sustained complete operation remain acceptance requirements.
