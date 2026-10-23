---
project: Security Market Pulse
stage: Operate
updated: 2026-10-23
---

# Status

## Current priority

Make today's site consistent, durable, accurate and fresh before expanding coverage or adding search
(D-111). The owner reports no useful decision or conversation yet; value is unmeasured. The thread
goal remains active. No owner decision is currently needed for the identified repair work.

Later work now explicitly includes search (SEC-073) and navigation by public/private status,
private-equity backing, startup stage and venture funding (SEC-074). Both are queued in the backlog
after current reliability work and coverage expansion.

[Current scorecard](docs/active/daily-pipeline/evaluations/2026-10-23/review-scorecard.md) ·
[Rubric](docs/active/daily-pipeline/evaluation-rubric.md) ·
[Recovery plan](docs/active/daily-pipeline/coverage-recovery-plan-2026-10-23.md) · [Work queue](BACKLOG.md).

## Actual production

https://securitymarketpulse.com serves application `7bd94ec77e99462c068f254e134235a894585cbb`,
release `2e17a786a85e46406df0cdc10da99819dd20f3f6b385f5acc328e51a7a4ec390`, sequence 1.
Vercel deployment `dpl_3fEZ6y9gBbqabjfEpKK2mo44VWq1` is READY; the accepted artifact's 25 static
files matched production. The primary-sourced Varonis agreement is live. Actual scheduled collection
[39946689429](https://github.com/jessepike/sec-market/actions/runs/39946689429), publication
[39947099729](https://github.com/jessepike/sec-market/actions/runs/39947099729), main gate
[39947450834](https://github.com/jessepike/sec-market/actions/runs/39947450834) and controlled rollback/restoration
[39947974279](https://github.com/jessepike/sec-market/actions/runs/39947974279) passed. Repeat scheduled
collection [39954446259](https://github.com/jessepike/sec-market/actions/runs/39954446259) reused the original
source evidence without changing its 11:34:15 UTC check time. One cycle does not prove sustained operation.

Current coverage remains **121/557**: 48 SEC tasks and 73 citations. The 436 gaps are 254 missing
registrations, 28 unverified registrations, 149 fetch-cap failures and five blocked pages. The separate
claim queue has 28 holds. Latest scheduled monitor
[39995104575](https://github.com/jessepike/sec-market/actions/runs/39995104575) verified the job/publication
receipts and updated assigned [issue 10](https://github.com/jessepike/sec-market/issues/10) for incomplete
coverage and the holds. Execution issues 8/9 recovered. Notification delivery beyond GitHub depends
on the owner's existing GitHub settings.

## Repair candidate on preview

The production baseline lost 14 of 28 held-review entries and omitted four older-policy candidate
facts from its pending state. This is a data-preservation defect; those four facts are not approved
for publication. The tested candidate preserves all 28 holds and quarantines all four with their
source/review chains. Exact current-policy admission can resolve only a matching held claim and
retains an immutable resolution record.

Same-day retries now independently validate and retain successful receipts instead of overwriting
them with exhausted-budget failures. Full archived replays preserved the actual 121 checks and the
historical 244-check counterfactual through two retries each, with original dates, zero new requests
or model calls, unchanged counters and an unchanged read-only archive. Compatible full responses
are shared within a run; supplier-specific URL hints prioritize work inside the existing limits.
eSentire article extraction excludes related-story sidebars and binds publication metadata to the
observed canonical URL. Conflicting dates remain unresolved. No live coverage increase is claimed.

Local verification passed 123 operational, 256 data, 112 pipeline and 34 browser tests, plus lint,
build and integrity checks. Rendered 1440px/390px pages were inspected and are pixel-identical to the
local baseline. This is invisible reliability work. Exact proofs are in
[validation](docs/active/daily-pipeline/receipts/coverage-recovery-validation-2026-10-23.json),
[retry replay](docs/active/daily-pipeline/receipts/coverage-retry-final-replay-2026-10-23.json) and
[continuity replay](docs/active/daily-pipeline/receipts/continuity-final-replay-2026-10-23.json).

Preview candidate `7c3d2eea35c783b866a6e955849d0e77a4017cac` passed actual GitHub
[web CI](https://github.com/jessepike/sec-market/actions/runs/40001666502) and
[private runner acceptance](https://github.com/jessepike/sec-market/actions/runs/40001666534).
Vercel preview is Ready; hosted 1440px/390px renders match the tested local pixels. The preview
uses repository baseline data; production data still comes from the accepted main artifact.
[Remote acceptance](docs/active/daily-pipeline/receipts/coverage-recovery-remote-2026-10-23.json)
pins both runs, the live production receipt and unchanged candidate code hashes.

## Next verification and limits

Main stays frozen on the accepted revision for October 23 UTC: both gate/publication attempts are
spent, and source/model/document counters are 5,500/80/40. Never reset or refund them. Preview fixes
await the next natural UTC allowance and normal main gate. Then verify actual scheduled collection,
publication and preservation receipts before upgrading the live scorecard. Overall factual accuracy,
eligible-event recall, sustained operation and reader value remain unmeasured. The coverage inventory
keeps all 557 obligations visible by family, supplier, domain and cause.

Daily collection is 05:17 UTC; publication follows verified scheduled collection and runs at 06:23
and 16:23 UTC. GitHub may run late. Legacy refresh/branch-promotion jobs remain disabled; Vercel's
competing production paths remain closed. The earlier Vercel probe failed in CLI account lookup;
explicit team/project API routes now have actual stage, promotion and rollback receipts. No Codex
Cloud dependency, purchase, PR or paid API fallback. Restore the latest evidence archive before writes.

Implementation checkout: `/Users/jessepike/code/projects/sec-market-finish-20261022`.
Original `/Users/jessepike/code/projects/sec-market` status/lessons edits remain untouched.
[Activation receipts](docs/active/daily-pipeline/activation-2026-10-23.md) ·
[Current operating route](docs/active/daily-pipeline/github-operations.md) ·
[Held-claim/source triage](docs/active/daily-pipeline/receipts/current-content-triage-2026-10-23.md).
