# Actual scheduled publisher stopped by owner intervention

Native scheduled publisher `40271992393` was created at `2026-10-26T05:00:49Z` on old main `3bb9e40c8f6324aa4f419fbe13022ec4dcaece55`. Its final conclusion is cancelled. This is an actual failed scheduled publication with manual intervention, not a scheduled success.

The owner reported that ordinary cancellation was accepted during setup. The job nevertheless completed its 972 guard tests in 90.559 seconds, with 60 explicit skips, and entered the restore/publication command at `05:03:05Z`. The owner then force-cancelled it. That command ended at `05:04:46Z` with exit 143. GitHub's job-level completed timestamp is separately `05:04:44Z`; both original metadata values are retained without rewriting. Receipt upload, alert and cleanup steps were skipped, and GitHub reports zero artifacts. No final application receipt exists to inspect.

The workflow's publish job uses `always()`. [GitHub's cancellation reference](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-cancellation) says a job whose condition remains true continues after an ordinary cancel. The observed continuation matches that rule. The separate force-cancel produced the terminal cancellation. The auditor issued neither cancellation nor any dispatch.

After termination, the actual remote evidence ref is still `5ddcbc51613f125c12cdc724db821384886722f5`, manifest `8f58843e0121ce686ec7bbcff5994cd10ca96f1ab827a591358bc21e752e992e`, with all 56,266 entries previously authenticated. Eight raw remote heads independently match that frozen archive byte for byte. Source counters remain 444 fetches, 76 calls and 37 documents. The real gate head remains `{attempts: 1}`; one of two attempts remains. No new gate run or gate-request archive entry exists. The publication-budget head remains absent, which is not represented as a fabricated zero counter. No refund or reset occurred.

The remotely persisted lease is still the prior publisher `github-publisher-40266519925-1`, released at `2026-10-26T04:07:01.428398Z`. No new bootstrap or lease claim was persisted remotely, and no new run entry exists. The killed runner's ephemeral local restore/claim state is unobservable; the audit does not infer fictional zero local use. Current collection and eight-group outcome heads remain exact.

All 106 static file checks on the live public domain and old immutable deployment return exact expected bytes. Public release `fc8bf0984dbeacbe79519574911837d8b638f42215f6547e31ae8968b29951e4`, sequence 4, remains unchanged. This event supplied no new release or public freshness.

A separate narrow cancellation repair is warranted after the current ee5 canary/promotion: use an expression-wrapped `!cancelled()` job status predicate while preserving all existing callback readiness, repository, private/main, concurrency, permission, timeout and budget conditions. Truth-table checks should retain eligible scheduled/manual runs with skipped callback preflight, require callback readiness for workflow_run, and reject cancelled workflows. No such edit was made by this audit.

The raw 233,902-byte job log remains VM-only, SHA-256 `cae42628aa3d9c833c296ef6c6e03642fa274b7283bcd0bd451d79d8e74b247b`. Safe metadata, bounded log signals, state digests and public-file digests are indexed separately.
