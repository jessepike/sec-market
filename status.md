---
project: Security Market Pulse
stage: Operate
updated: 2026-10-24
---

# Current state

The coverage goal is active. D-111 prioritizes consistent, durable, accurate and fresh operation.
D-112 separates daily intake, document processing and history while preserving all 74 suppliers,
557 obligations, historical URLs and original dates. Activation and verification are approved.
Reader value remains unmeasured; the owner reports no useful real use. Search and company
ownership/funding/stage navigation remain queued as SEC-073/074.

## Actual public release and current collection

| Measure | Actual result |
|---|---|
| Public production | App 26181a2d, release 19fde803…26941, sequence 3; Vercel dpl_9KqhU2bnfcmaQyYg73ZB1tXT9WBV READY. Old combined coverage 244/557, source checked October 24 at 00:38:18.807979 UTC. |
| Accepted publication proof | Publisher 40050633432, independent gate 40050850177 and rollback/restoration 40051385049 passed; all 53 files matched both hosts. Varonis and six corrections remain live. |
| Current private intake | Manual collector 40120612027, policy 8b44bcbe…b445db, checked October 24 at 18:32:56.227836 UTC: 264/557. It still needs its actual scheduled run and public update. |
| Remaining intake gaps | 254 missing bindings, 25 candidates, 9 HTTP 403, 4 HTTP 429 and 1 unsafe redirect: 293 total. |
| Processing | 10,655 source/URL pairs; 23 reviewed, 10,632 pending, 5 held, 1 changed, 291 unknown dates. All 32 prior holds persist; Upwind revalidation adds a 33rd entry. |
| Historical review | 24 reviewed, 10,631 pending, 5 held. No original evidence date was renewed. |

Ping Identity, Delinea and Sonatype now pass actual intake; their 737 leads still need processing.
Upwind's current primary body is unknown after a later sitemap change. The Sonatype mislinked
card still needs primary-content review. Five known contradictions are resolved against the
accepted release; general precision/recall and sustained operation remain unmeasured.

[Public release receipts](docs/active/daily-pipeline/renewal-verification-2026-10-24.md).
[74-company overview and 557-row ledger](docs/active/daily-pipeline/evaluations/2026-10-24/current-source-coverage.md).
[Actual current collection](docs/active/daily-pipeline/accuracy/html-source-activation-actual-collection-review-2026-10-24.md).
[Rubric](docs/active/daily-pipeline/evaluation-rubric.md) and [bound scorecard](docs/active/daily-pipeline/evaluations/2026-10-24/html-activation-current-scorecard.md).

## Reviewed runtime and diagnostics

Main/preview runtime 1bf6324f passes preview web 40128710185, archive canary 40128710246 and main
web 40129048686. Preview dpl_5qNoo5vhgc4NB6kfBu2me6RFBWf1 is READY and matches reviewed 1440/390 pixels.
The midnight repair reconstructs the original sealed partition at collection time while checking
freshness at gate time. The actual archive passes all three next-day publisher reconstructions.
The Orca redirect repair passes 780 operational, 373 data, 115 pipeline and 42 browser checks, with one
appropriate fixture skip. Source observations and authority remain exact; Git main builds do not publish.

Actual Orca run 40129367275 completed 20:25:48 UTC. It charged 27 fetch reservations, retained 90 leads
from 26 successful index pages, then recorded five HTTP 302 responses redirecting page 27 to itself.
It remains unqualified. The archive 3511f25b, manifest 63f6a19b…ac205, verifies all 41,066 entries;
all earlier paths, normal 264-check head, four fact references, 33 queue entries and public release
head survive. Replay under disabled ad1 uses the immutable original plan and makes zero writes.
The original Orca plan is retired. Review-time replay used exact disabled ad1; this change
selects exact seven-endpoint plan 98b110fe… for one bounded follow-up after CI and promotion.

[Orca actual audit](docs/active/daily-pipeline/accuracy/orca-redirect-actual-source-review-2026-10-24.md).
[Latest-archive midnight replay](docs/active/daily-pipeline/accuracy/orca-disabled-plan-midnight-preflight-2026-10-24.md).
The seven-endpoint diagnostic is independently reviewed under unchanged H and bounded at 257
logical fetch reservations. It cannot qualify sources or publish. Restore exact disabled ad1
after its actual archive audit, then freeze main. The GitHub RSS article-CDATA parser repair
passes 800 operational and all web checks. Original reports, H origins, seed inventories and
the next-publication snapshot replay exactly; real DTDs remain rejected. Current counts do not change.
[Parser repair](docs/active/daily-pipeline/accuracy/github-rss-xml-guard-handoff-2026-10-24.md).
[Seven endpoints and bound](docs/active/daily-pipeline/accuracy/schema1-seven-source-endpoint-preflight-2026-10-24.md).

## Next receipts, allowance and remaining work

Current-policy timer proof is still pending. Earlier genuine scheduled collector 40082520067
passed under preceding policy 79cdd19b at 09:43 UTC, over four hours after its 05:17 schedule.
October 24 allowance is 1,980/5,500 fetch reservations, 80/80 models, 40/40 documents and 2/2 gates.
No reset/refund, purchase or API billing fallback. Assigned publisher issue 12 remains open for
DAILY_GATE_BUDGET_EXHAUSTED; issue 10 retains coverage/history gaps. Issue 13 closed after actual
archive-import recovery. GitHub assigned-issue delivery is verified; phone/email delivery is unproved.

Next natural allowance: 00:00 UTC October 25 (5 p.m. Pacific October 24). Publisher: 00:23 UTC;
collector: 05:17 UTC (10:17 p.m. Pacific October 24). Verify actual scheduled execution, gated public
bytes, assigned issue 12 recovery and controlled rollback/restoration. Keep final reviewed main
fixed during acceptance. The old public source expires 06:38:18 UTC October 25; schedule delays remain possible.
Finish candidate qualification, missing-family bindings, access recovery and pending review within
the unchanged limits. No owner source decision is currently required. Exact actions are in BACKLOG.md.

Implementation: /Users/jessepike/code/projects/sec-market-finish-20261022.
Preserve original /Users/jessepike/code/projects/sec-market at 0a660a72 with its modified
status/lessons and untracked web/tests/daily-measures.test.ts.
