# Independent review: scheduled source freshness cycle

Date: October 25, 2026. Verdict: **pass for the specified future preview change**. Two review passes found no material or minor finding. This is code and isolated-test evidence. Actual scheduled collection and public acceptance of this repaired revision remain pending. Main `6d5e87feba4ffbc75e50f35cb564cb8fd91708ca` and recovery `40169973257` were not changed or dispatched by the reviewer.

## Scope and implementation

The first pass compared the diff with `/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/scheduled-source-freshness-cycle-spec-2026-10-25.md` and the same-day cadence review. The second pass checked focused tests, independent failure/retry scenarios and unchanged historical admissions. The reviewer wrote only this document and its companion JSON. The implementation worker handled full operational/application suites and rendering; those results are separate evidence.

`scheduled_source_refresh` in `/Users/jessepike/code/projects/sec-market-finish-20261022/ops/ci/collect.py` requires all five exact values: GitHub Actions `true`, repository `jessepike/sec-market`, event `schedule`, ref `refs/heads/main` and cron `17 5 * * *`. The existing workflow supplies the cron from `github.event.schedule`. Manual, other branch/repository/event and retired temporary schedules do not select the override. Source-probe execution returns before this selection and account collection work. No workflow or trigger changed.

The engine already skipped successful receipt reuse when forced. The new conditions also skip reading and writing the immutable run-download pointer when `force_refresh` is true. A new source observation and receipt are still retained. The source-specific mutable download head remains available for ETag/Last-Modified conditional requests. Ordinary retries retain their original pointer and receipt paths. There is no arbitrary clock update or unconditional-200 requirement.

The current-invocation transport cache, rate/host/size guards, conditional 304 handling, source-specific reuse chains and immutable SEC document handling are unchanged. Forced index transport still supplies a genuine current SEC anchor before the document can be marked retained immutable; its original body-fetch clock is preserved while its current verification clock is distinct. Semantic cache keys, facts, held claims, correction review rules and admission code are unchanged.

## Focused verification

All commands ran in OrbStack dev with bytecode writes disabled. No package installation was needed.

| Check | Result |
|---|---|
| `python3 -B -m unittest discover -s ops/ci -p test_scheduled_source_freshness.py -v` | 12 passed; zero skips. |
| Six selected existing retry, held-claim, semantic-cache and correction-replay regressions | Six passed. |
| Additional independent isolated failure/retry scenarios | Seven passed. |
| Actual existing correction policies and immutable admissions | All six replayed unchanged. |

The new focused tests cover exact schedule selection and exclusions; real caller argument routing; probe exclusion; ordinary same-day clock preservation; bypass of both reuse layers; actual conditional-request header construction and HTTP 304 body provenance through a mocked opener; current-invocation full-response sharing; depleted allowance; cancellation/deadline; current SEC anchors; and unchanged-body semantic-cache reuse.

The six selected existing tests were `PipelineTests.test_exhausted_retry_reuses_hash_checked_success_without_refreshing_dates`, `test_success_can_recover_after_forced_cap_failure_overwrites_task_head`, `test_changed_policy_and_new_day_never_borrow_prior_task_success`, `test_rejected_claim_is_quarantined_without_blocking_a_supported_fact`, `test_full_cycle_is_idempotent_and_cache_saves_model_calls`, and `CorrectionCollectionTests.test_replay_invokes_corrections_without_repeating_valid_source_or_model_work`.

Independent scenarios checked forced transport failure followed by ordinary retry; forced exhausted allowance followed by ordinary retry with no refund; newest successful forced receipt followed by another failed force and ordinary recovery; cold forced success with no pointer; cold partial transport failure; explicit denial of every forced immutable-pointer read; and cold semantic-pending work followed by ordinary completion. In-memory fixtures and temporary synthetic stores were used. Network transport was denied in these checks.

## Retry limits retained

After a failed forced check, an ordinary retry can still recover a valid sealed earlier success under the existing last-good policy. Independent tests verified its original source clock remains unchanged. This is not evidence of a new source check. Where a newer forced success exists, the retry selected that successful receipt rather than the earlier immutable pointer.

A cold forced cycle deliberately writes no run-download pointer. If its transport succeeds but semantic work is pending, a later ordinary retry can need additional conditional transport. The independent two-URL fixture spent two additional fetch reservations and completed, without an immutable-object collision or invented source time. Successful tasks in a cold partial cycle were reused while the failed task alone retried. This bounded cost is consistent with the explicit read/write suppression; it does not promise zero-fetch resumption or extend the existing last-good policy.

Actual fresh source results, fetch allowance, completion time and next-day publication remain uncertain until this revision executes on the real daily timer. The prior-policy same-day reuse receipt and the older public-expiry evidence remain separate; this review assigns no sole-cause or repaired-H runtime credit to either.

## Preservation and reviewed pins

H, the 173-byte disabled diagnostic plan, operational correction requests, original inventory, baseline, correction policy stamp and collector workflow remain pinned in the companion receipt. Admission replay used only a read-only archive adapter. All 36 consulted archive files retained identical hashes, sizes and nanosecond modification times; touched-file seal `488a889eed1b93db07739ce265d77c27295deb62eae9521527789ba96de3ccf0`. This is not a new whole-archive authentication claim.

| File, relative to `/Users/jessepike/code/projects/sec-market-finish-20261022/` | SHA-256 |
|---|---|
| `web/scripts/pipeline/engine.py` | `e471f18006a4899406510cdede42829476ba1945b58c420c61f6edce767a7e19` |
| `ops/ci/collect.py` | `d27a676d6adc50faa7004f109a5507fa2d441627f4709b65ba8de855b4f5a7d5` |
| `ops/ci/test_scheduled_source_freshness.py` | `84c7fe20666cbaa173173d7dbc98ac5e5a3072eef71a86f6fc31955a45147523` |
| `docs/active/daily-pipeline/accuracy/scheduled-source-freshness-cycle-spec-2026-10-25.md` | `acfa65a63af35b77b5e794f795e4232e132a9633a400519739c7211727362ef1` |
| `docs/active/daily-pipeline/accuracy/same-day-manual-and-scheduled-source-cadence-review-2026-10-25.md` | `f9ff71617c886c21ad89b13103fb5e83469ca4a86c6053d7b668669c0559073c` |

## Issue log and boundary

No findings. No implementation fix was made by the reviewer. I would retain the narrow change for the future reviewed preview because it makes the normal daily timer perform current transport while preserving ordinary retry policy and honest clocks. It does not authorize changing frozen main, another dispatch, quota reset, operational correction activation or a production claim.
