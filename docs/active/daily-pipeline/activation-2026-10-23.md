# Daily pipeline activation receipts

Owner: "Approve activation and verification". D-110 records this approval for the reviewed daily
facts pipeline, including controlled rollback and restoration, on October 22 Pacific time.
The platform is private GitHub Actions and the existing Vercel project. No Codex Cloud scheduler,
paid model API fallback, purchase or pull request was used. The original checkout's uncommitted
status and lessons edits remain preserved; implementation uses `/Users/jessepike/code/projects/sec-market-finish-20261022`.

## First activation cycle verified

Production serves application `7bd94ec77e99462c068f254e134235a894585cbb`, release
`2e17a786a85e46406df0cdc10da99819dd20f3f6b385f5acc328e51a7a4ec390`, sequence 1, at
https://securitymarketpulse.com. Its immutable deployment is
https://security-market-pulse-6cyvuucv4-pikeholdings.vercel.app.

Vercel reports READY deployment `dpl_3fEZ6y9gBbqabjfEpKK2mo44VWq1`. All 25 public static files
matched the accepted gate artifact byte for byte. Artifact SHA-256:
`f05659e33f0d590fad939119a37f7c87ebc0a01808292c15df9a400c06de7826`.
Snapshot SHA-256: `53b49106fa9118d603db5e64e37cf03f7f2c6fd1fb797acf18e73f540196c84f`.
Hosted browser verification passed 31 tests. Its three repository-bound source checks ran in the
full 389-check gate, which includes all 34 browser checks. Full-page production screenshots at
1440px and 390px were inspected; layout is intact and the sourced Varonis update is live.

| Actual run | Receipt |
| --- | --- |
| [Collector 39946689429](https://github.com/jessepike/sec-market/actions/runs/39946689429) | Actual `schedule` on main, successful bounded execution, 121/557 source tasks, `complete: false`, `executionCompleted: true`, `completed_with_gaps`, zero model calls. |
| [Publisher 39947099729](https://github.com/jessepike/sec-market/actions/runs/39947099729) | Actual `workflow_run` callback from scheduled collection; `published: true`, sequence 1, exact immutable production deployment. The event is retained as a callback. |
| [Independent main gate 39947450834](https://github.com/jessepike/sec-market/actions/runs/39947450834) | Successful main provenance, exact evidence-bound artifact, complete SEC certification and passing application checks. |
| [Controlled drill 39947974279](https://github.com/jessepike/sec-market/actions/runs/39947974279) | Passed. Retained baseline acknowledged, then current production restored at `2026-10-23T11:46:13.860251Z`. `currentBytesVerified: true`; the production head stayed on the accepted release. |
| [Regular publisher 39948978666](https://github.com/jessepike/sec-market/actions/runs/39948978666) | Actual scheduled run confirmed that no new release was needed. |
| [Repeat collector 39954446259](https://github.com/jessepike/sec-market/actions/runs/39954446259) | Verified scheduled source reuse; no renewed source check time or claim of another source fetch. |
| [Reuse callback publisher 39954827589](https://github.com/jessepike/sec-market/actions/runs/39954827589) | The exact code and collection were already acknowledged, so no new release or gate was needed. |
| [Independent monitor 39950995198](https://github.com/jessepike/sec-market/actions/runs/39950995198) | Actual scheduled monitor reports coverage gaps and 28 held reviews, with no missing-clock or cutover errors. |

Retained receipts: [scheduled collection](receipts/actual-scheduled-collection-2026-10-23.json),
[publication](receipts/actual-publication-2026-10-23.json),
[accepted main gate](receipts/accepted-main-gate-2026-10-23.json),
[rollback/restoration](receipts/actual-rollback-restoration-2026-10-23.json),
[scheduled publisher no-op](receipts/actual-scheduled-publisher-noop-2026-10-23.json),
[scheduled source reuse](receipts/actual-scheduled-reuse-2026-10-23.json),
[production byte verification](receipts/production-byte-verification-2026-10-23.json),
[Vercel READY](receipts/vercel-ready-2026-10-23.json),
[scheduled monitor](receipts/actual-scheduled-monitor-2026-10-23.json) and
[post-rollback controls](receipts/post-rollback-controls-2026-10-23.json).
The [source and budget audit](receipts/source-budget-audit-2026-10-23.json) retains the observed
request counts, conservative reservations and unchanged reuse timestamps.

The drill's upstream publisher receipt identifies `39947099729`, event `workflow_run`, application
revision `7bd94ec77e99462c068f254e134235a894585cbb`. Its source clock identifies actual scheduled
collector `39946689429`, attempt 1, and current contract
`de1932f7698d6b5ec86c23da52e77b1440c34d368e101c2aaabcbae6b39abfbe`.
The legacy baseline has an exact retained app receipt and immutable URL but no original full static
inventory: `baselineByteInventoryAvailable: false`. Restoration of the current accepted release
received the complete static-byte check. The receipt retains this distinction.

## Immutable archive checkpoints

These pins identify the corresponding finished receipts. Restore the latest remote archive before
any state write; these are historical checkpoint pins, not instructions to overwrite a newer head.

| Receipt | Archive commit | Manifest SHA-256 |
| --- | --- | --- |
| Actual collection | `e356266b3e43b0bb225c11fa4833011395f62a8c` | `f8f3455ad10d80af9ce38194226f5d67da124afa952c8c6185e48aaa224e8f8b` |
| Accepted publication | `563a632b90f98e1f531ea71583a0d7d9fd323bd8` | `586eb7c3f76bcc053c3043575944550d4900819037c3c89d7af2af5e25cd7841` |
| Passed rollback/restoration | `4ede66ac2c2f571a04acf30942edf3238546b1ac` | `ef17af087129ee1de49f37d2ad8285eab750f7aa706c5a742b4a22b62a193e44` |

The archive ref is `refs/archive/market-evidence`. Auth stays outside its contents.

## Alerts and coverage boundary

Execution issues [8](https://github.com/jessepike/sec-market/issues/8) and
[9](https://github.com/jessepike/sec-market/issues/9) closed on actual recovery.
[Issue 10](https://github.com/jessepike/sec-market/issues/10) remains open for coverage.
The monitor's remaining reasons are `OVERDUE_OR_INCOMPLETE_COVERAGE`,
`PUBLIC_COVERAGE_INCOMPLETE_OR_OVERDUE` and `OWNER_REVIEW_QUEUE_28`.
They are not missing scheduler or production acknowledgement errors.

The scheduled source receipt checked 121/557 tasks: all 48 SEC tasks and 73 citations. It retained
149 fetch-cap failures, five blocked tasks and 282 not checked (254 missing family bindings and
28 unverified bindings). The decline from the earlier 244 checks comprises 123 citation checks
held by the exhausted fetch allowance. The source run spent 133 new fetches, taking the ledger
from 5,367 to 5,500. Charged model/document reservations remained 80/40; the scheduled run made
zero model calls. It reused 191 immutable SEC filing bodies anchored by fresh checks of 16 indexes.
This is genuine bounded source work with preserved source-specific limitations.

The repeat scheduled collector retained coverage receipt
`370c35cf48074658a53f920c66b4ba1e4be711a158111fd04a03ad9c8cfde410` and original check time
`2026-10-23T11:34:15.010723Z`,
and every budget counter stayed unchanged. Full source coverage is incomplete, with 254
missing family bindings and 28 held claims. Individually verified facts may publish with these
explicit gaps, while complete SEC certification remains required. Varonis ownership remains
announced rather than closed. A successful bounded execution is not a completed historical audit.
This proves the first activation cycle; multi-day burn-in and full-roster freshness remain open.
No spent or conservatively reserved counter was reset or refunded.

## Operating state and cleanup

The daily collector remains 05:17 UTC; scheduled publishers remain 06:23 and 16:23 UTC. Genuine
scheduled collection can also start publication through its independently checked callback.
GitHub emitted the acceptance jobs late. Earlier manual runs did not supply the scheduled proof;
initial publication waited without spending an independent-gate attempt until real proof existed.

Temporary October 23 06:07 and 07:07 UTC acceptance crons stay guarded to that UTC date. A later
acceptance timer can verify prior real scheduled source work and explicitly retain its original
receipt hash and check time. The recorded drill phase prevents another automatic acceptance.
Leave these safe guards in place until the next regular code promotion; their cleanup does not
justify moving main while October 23's gate allowance is spent.

Main stays frozen at `7bd94ec77e99462c068f254e134235a894585cbb`. The daily gate allowance is
2/2 spent, including the earlier failed attempt. Documentation may advance on preview only;
changing main would require another code-bound gate. Existing legacy certified-refresh and
branch-promotion workflows remain disabled. Vercel production paths remain controlled: automatic
custom-domain assignment is false, the exact main/archive Git-build ignore rule stays installed,
and alias operations verify the rule and restore only that assignment flag if necessary.
Post-rollback read [39978528957](https://github.com/jessepike/sec-market/actions/runs/39978528957)
succeeded and confirmed `productionPathsControlled: true`.

## Earlier evidence and validation

Original Vercel probe
[39701439701](https://github.com/jessepike/sec-market/actions/runs/39701439701) failed during CLI
account lookup before it reached the existing project. Diagnostic `39703939654` isolated
`USER_LOOKUP`; explicit team/project read `39704072043` and prebuilt stage `39797014280` passed
with the configured credential. The successful post-rollback read `39978528957` verifies that
same approach on the active production controls. No replacement login or billing fallback was needed.

The earlier [main gate 39908495114](https://github.com/jessepike/sec-market/actions/runs/39908495114)
passed 389 checks, but [publisher 39908275916](https://github.com/jessepike/sec-market/actions/runs/39908275916)
failed after staging during the high-level CLI account-discovery path. Production then remained
on `54590be4d91113a50879a8fb5d180441e7d149f4`. Fixed team-scoped project APIs, immutable READY
project/target checks, live acknowledgement and fixed failure categories corrected that path.
The failed attempt remained charged. It did not establish a successful production release.

Before activation, 83 operational tests passed in OrbStack. Application runs
[39914573163](https://github.com/jessepike/sec-market/actions/runs/39914573163) and
[39914570279](https://github.com/jessepike/sec-market/actions/runs/39914570279), plus canary
[39914569790](https://github.com/jessepike/sec-market/actions/runs/39914569790), passed.
[Probe 39909753143](https://github.com/jessepike/sec-market/actions/runs/39909753143) confirmed the
configured production controls. Prior source and review evidence remains in the
[earlier acceptance record](finish-acceptance-2026-10-22.md) and Git history.
