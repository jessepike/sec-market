# Current scorecard: HTML source activation

Evaluated at 2026-10-24 19:02 UTC under the operational rubric. This scorecard keeps private intake and public production separate and does not calculate an overall score.

The private current-policy run checked 264 of 557 required tasks, leaving 293 gaps. At 19:02 UTC, the live production-app receipt still identified release `19fde803d09aa544672183769c257e37faf727b75e1914955f54f3c5fb126941` and the same public daily run, with 244/557 coverage. That public coverage was checked at 00:38:18.811621 UTC; the latest successful task completed at 00:38:18.807979 UTC. The private run was manually dispatched and did not publish its new coverage.

| Measure | Status | Observed / required | Observation time | Evidence boundary |
|---|---|---:|---|---|
| Private current-policy source intake | fail | 264 / 557 | 2026-10-24 18:32:56 UTC | Fixed denominator; 293 tasks remain. |
| Public production source intake | fail | 244 / 557 | 2026-10-24 19:02:00 UTC | Live app check confirmed the same release and daily run; underlying collection check was at 00:38:18 UTC. The new private result is not public. |
| Private receipt age | pass | 0.46h / 30h | Receipt checked 2026-10-24 18:32:56 UTC | Receipt age only. Full-roster freshness fails. |
| Public receipt age | pass | 18.39h / 30h | Aggregate receipt checked 2026-10-24 00:38:18 UTC | The last successful task completed at 00:38:18.807979 UTC. The production roster is still incomplete. |
| Private full-roster freshness | fail | 264 / 557 | 2026-10-24 18:32:56 UTC | A recent partial check does not make every required task fresh. |
| Public full-roster freshness | fail | 244 / 557 | 2026-10-24 19:02:00 UTC | Production still serves the prior coverage result. |
| Private processing review | fail | 23 / 10,655 | 2026-10-24 18:32:56 UTC | 10,632 pending, five held, one changed and 291 dates unknown. |
| Private historical review | fail | 24 / 10,655 | 2026-10-24 18:32:56 UTC | Historical review is separate from current processing. |
| Review queue continuity | pass | 32 / 32 prior entries retained | 2026-10-24 18:32:56 UTC | The prior queue is an exact prefix; one Upwind revalidation entry brings the queue to 33. Four ordinary fact references and four older quarantine objects remain. |
| Earlier-policy scheduled collector execution | pass | 1 / 1 | 2026-10-24 09:43:25 UTC | Genuine scheduled run `40082520067` completed on revision `4b5e5ec` and policy `79cdd19b`. Its 261/557 result reused prior receipts; only 14 fetches were added. |
| Current-policy scheduled collector execution | unmeasured | — | — | No timer run is supplied for policy `8b44bcb` on revision `1ed94479`. Run `40120612027` was manual. |
| Current-policy scheduled publication | fail | 0 / 1 | 2026-10-24 18:55:18 UTC | Scheduled publisher `40122602778` reported `DAILY_GATE_BUDGET_EXHAUSTED`; no new public release was delivered. The prospective-publication preflight partition check is under repair; this is a publication-gate issue, not a source-accuracy finding. |
| Production release rollback and restoration | pass | 1 / 1 | 2026-10-24 01:52:28 UTC | One manual drill passed for release `19fde803`; it does not establish sustained operation or rollback behavior for an unpublished revision. |
| Archive-integrity canary | pass | 1 / 1 | 2026-10-24 18:41:36 UTC | Private archive integrity only. It is not a collection, timer, publisher or deployment result. |
| Current-policy known release checks | unmeasured | — | — | The canary and skipped preflight work do not establish a current-policy release-gate result or source accuracy. |
| Prior production release checks | pass | 4 / 4 checks; 511 tests | 2026-10-24 01:47:20 UTC | Checks apply to release `19fde803`, not the current private policy. |
| Historical fixed-record audit | fail | 5 known contradictions / 177 records | 2026-10-23 18:48:44 UTC | Immutable historical verdicts. The separate 5/5 mapped correction result does not rewrite this audit or measure general accuracy. |
| Mapped corrections in production | pass | 5 / 5 targets | 2026-10-24 01:47:20 UTC | Target-specific evidence for the five mapped records in release `19fde803`; it does not establish zero current errors. |
| Claim precision | unmeasured | — | — | No current reviewed benchmark and explicit denominator. |
| Eligible-event recall | unmeasured | — | — | No reviewed event benchmark and omission denominator. |
| Sustained operation | unmeasured | — | — | No complete dated window of current-policy executions, publications and recovery outcomes. |
| Observed reader value | unmeasured | — | — | The owner reports no observed real use. |

The current manual collection succeeded on 264 intake tasks and discovered 737 URLs from Sonatype, Delinea and Ping Identity. Their three intake results are counted in the intake measure. Their separate processing status is `not_checked` pending historical review; 63 index observations are retained and hash-verified. Those URLs add intake evidence, not facts or historical-review credit. The changed Upwind page remains pending because the current run did not fetch or conditionally verify its primary URL after its sitemap date changed.

The archive canary passed after the collection and verified the archived state. It did not run the collector or publisher. A real scheduled collector run exists for the earlier policy, but there is no scheduled collector proof for the current policy. The scheduled publisher failed, production stayed on the prior release, and sustained operation remains unmeasured.

The machine-readable companion at [html-activation-current-scorecard.json](/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/evaluations/2026-10-24/html-activation-current-scorecard.json) pins the receipts and source files behind each measure. The [557-task gap ledger](/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/evaluations/2026-10-24/current-source-coverage.md) lists the current intake gaps by reason.
