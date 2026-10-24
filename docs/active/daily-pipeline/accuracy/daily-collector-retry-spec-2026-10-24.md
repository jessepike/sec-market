# Daily collector retry proposal

## Recommendation

Keep the existing 05:17 UTC daily collector. Consider two same-day retry opportunities around 09:17 and 11:17 UTC, each behind a schedule-only guard. Those times are candidates based on the four-to-six-hour delays observed on October 23, not final selections: the original scheduled run could still arrive between retry slots, and GitHub Actions does not guarantee that a scheduled event will start on time or at all. Before choosing slots, compare actual timer start delays with the cost of extra queued runs.

The retry entries must not start duplicate collection after a successful scheduled run for the same UTC day. Reuse the current verifier in `ops/ci/collect.py` as the basis for that decision. The skip must require an authenticated completed successful `schedule` run on `main`, the exact workflow path, current main revision and application-code pins, current market-contract and correction-policy hashes, matching run attempt and app revision, and a current receipt whose source timestamp remains within the contract's overdue window. The correction join must replay the current configured admissions and bind their outcome to that same collection run. It must preserve the verified receipt's original `checkedAt` as `sourceCheckedAt`; it must not write a new source verification, gate, or publication result. The archived retry result should say it reused that run and show zero fetches and zero model calls.

## Correction-cache condition

The existing shortcut refuses reuse whenever `contracts/factual-corrections.json` exists. Keep that refusal until a correction-specific join is added. A safe no-op requires the current correction request and baseline policy digest to match a retained correction outcome for the same verified collection run, every configured group to have an authenticated replayable admission, and no pending group or new review attempt. If any comparison is missing or fails, take the existing collection path. That path can replay accepted admissions and process outstanding work; a schedule retry must not silently skip it.

## Evidence and limits

The deployed workflow currently schedules only `17 5 * * *` as its durable daily event. Its other two cron entries are explicitly temporary October 23 acceptance times, guarded by `ops/ci/schedule_guard.py`. `reuse_scheduled_collection` is also tied to that acceptance date and those entries, so it does not protect future retry slots.

The October 24 manual collection is a `workflow_dispatch`, not timer evidence. The retained audit at `docs/active/daily-pipeline/accuracy/actual-new-policy-private-transition-2026-10-24.md` records 261 of 557 intake checks at the manual run's original time and explicitly says the normal 05:17 timer was unobserved. The operator-reported absence of the 05:17 run at 08:40 UTC is consistent with that record; the manual run cannot satisfy the scheduled-run check.

Retry slots do not establish sustainable capacity. `docs/active/daily-pipeline/accuracy/historical-freshness-feasibility-2026-10-24.md` calculates a 7,421-per-day ideal-sharing lower bound for the superseded combined/full-history policy. That number does not apply to the current split `daily_source_intake_v2` measure. Its sustained request cost remains unmeasured; retries may improve daily intake, but cannot establish feasibility without actual current-policy receipts over time. Keep the existing budgets and 557-obligation denominator. Today's 80-call and 40-document allowance is already exhausted in the retained manual-run audit, so later attempts must report their actual reservations and gaps.

## Smallest implementation boundary

If observed timer delays justify retries, add fixed UTC retry cron entries and accept them only for the production repository's `schedule` event on `main`. Broaden the reuse guard through a separate ordinary-daily path while leaving the October 23 acceptance guard unchanged. Bind current code, main revision, market and correction policy, and current correction admissions before allowing a zero-work skip. Add tests for a late original timer arriving before a retry, an absent timer, a successful same-day timer, a manual run that must not count, changed code or correction policy, pending corrections, stale source receipts, and unchanged `checkedAt`. Do not add retries for manual dispatches, modify the source contract, raise allowances, or treat a skipped retry as a new collection.

The smallest useful trial is a bounded period with the existing primary timer and any selected retry times, recording each actual Actions event and the exact selected path: fresh collection, verified reuse, or guarded rejection. Continue only if timer receipts show that retries improve delivery without duplicating source work. A retry schedule alone is not proof of recurring operation.
