---
project: Security Market Pulse
stage: Operate
updated: 2026-10-25
---

# Current state

D-110 activation and verification remain approved. D-111 prioritizes consistent current operation;
D-112 separates daily intake, processing and history. Preserve all 74 suppliers, 557 obligations,
historical URLs, original dates, six admissions and every hold. Value and multi-day durability
remain unmeasured. Search and ownership/funding/stage navigation are SEC-073/074.

## Actual production

Accepted release fc8bf098…951e4, sequence 4, still serves app 6d5e87fe and snapshot 8ba13011…5a89.
Vercel dpl_GFKc3mfpR6CSeZt7u62B5LVBqQjv is READY. Public expiry remains October 26 at
12:45:29.479727 UTC. Public intake is 264/557; processing/history remain 38/39 of 10,655,
with 10 held and queue 37. No later private check or diagnostic renews this public expiry.

Manual publisher 40172130763 and gate 40172376435 published this release. Manual drill
40173134585 exercised baseline 19fde803 and restored fc8bf098; all 106 exact host-file checks
passed. [Publication](docs/active/daily-pipeline/accuracy/manual-freshness-publication-2026-10-25.md)
and [drill](docs/active/daily-pipeline/accuracy/recovery-rollback-restoration-2026-10-25.md).
The earlier release expired at 06:05:06 UTC and was observed overdue at 06:39; recovery does
not erase that failure window. Varonis and the six admitted corrections remain live.

## Genuine scheduled collection and automatic failure

[Actual scheduled collector 40182324149](docs/active/daily-pipeline/accuracy/scheduled-h-acceptance-2026-10-25.md)
passed on main 71c39356 under H, 8b44bcbe…b445db. GitHub started it at 09:50:43 UTC,
4 hours 33 minutes 43 seconds after its 05:17 schedule. All 48,030 archive entries, 557-task reconciliation,
original facts/dates, six admissions and old holds pass the authenticated replay.

| Private scheduled result | Actual state |
|---|---|
| Intake | 264/557; 293 gaps: 254 missing bindings, 25 candidates, 9 HTTP 403, 4 HTTP 429, 1 unsafe redirect. |
| Processing | 40/10,655 reviewed; 10,615 pending; 11 held, 1 changed, 291 unknown dates. |
| History | 41/10,655 reviewed; 10,614 pending; 11 held. |
| Continuity | Four fact references and all 37 old held rows preserved; one additional HiddenLayer candidate lacks a fact date. Queue 38. No new accepted facts/events. |
| Actual source clocks | New full/304 observations and separate immutable rechecks derive private expiry October 26 at 15:55:27.307096 UTC. Original logical-plan and evidence dates remain. |
| October 25 ledger | 985/5,500 fetches, 80/80 model calls, 38/40 documents; gates 2/2. The later seven-source diagnostic charged 116 requests; no reset or paid fallback. |

Those 264 passes comprise 196 existing-citation checks, 48 SEC checks, 17 official-announcement
checks and three investor/acquirer checks. Broader source coverage remains incomplete.

Collector acknowledgement is 310082e9, manifest 69882c24…cd16a. Automatic publisher
40183462577 actually failed with DAILY_GATE_BUDGET_EXHAUSTED, without a third gate or public
change. Assigned [issue 14](https://github.com/jessepike/sec-market/issues/14) records that failure;
issue 12 stays historically closed. Callback drill 40183832621 skipped. Post-callback baseline
6708f37f, manifest 8f7ae5e9…5350d, is authenticated and its lease released.
Automatic publication remains unproved. Wait for ordinary next-UTC capacity; do not manually
retry a gate or publisher. The next publisher may use still-fresh retained collection before
the next daily collector; that cannot establish another timer execution.

Actual [scheduled publisher 40190348786](docs/active/daily-pipeline/accuracy/scheduled-publisher-attempt-2026-10-25.md)
also failed DAILY_GATE_BUDGET_EXHAUSTED on main 900a51f9. Its authenticated 496ad86a poststate
has 48,060 entries; only three governance heads/three session records changed. Lease released,
869/80/38/gates 2 unchanged; four public files remain exact. Issue 14 updated at 11:51:44 UTC.
This proves unattended failure reporting, not successful automatic publication.

## Current source work

The preceding main 900a51f9 restored exact disabled ad1 remotely. Closure preview web 40188932479
and main web 40189180649 pass. Preview dpl_7PwRGz8EsZphVp17a8wj19wmr633 is READY; main
Git build dpl_Bd4iXsMGpF6iPpmbuF6gKEBv1jRN is CANCELED. Public receipt remains byte-exact.
The preceding sample selection b7c7841a passed preview web 40187747470/canary 40187747473
and main web 40187990840. These code moves did not publish.
[Closure proof](docs/active/daily-pipeline/accuracy/receipts/q4-primary-qualification-restoration-2026-10-25/verification.json).

Actual six-script diagnostic 40179255547 captured JFrog/Rapid7/Rubrik controllers and preserved
all earlier evidence. Their static inspection supports two exact JFrog/Rapid7 data GETs.
The closed implementation, 877 operational checks, full application checks and independent
reviews pass; both screen widths are unchanged. Manual two-request diagnostic 40184027106
passed on main ab6a7c68. Its [actual audit](docs/active/daily-pipeline/accuracy/q4-initial-data-capture-actual-source-review-2026-10-25.md)
verifies all 48,045 entries of d6606a4f, the full report and six admissions. JFrog returned
206 records and Rapid7 323; literal dates have no timezone. All normal heads, facts, 38 holds
and expiry remain exact. Actual callbacks skipped publication and rollback. Qualification
and coverage credit remain zero. Its disabled ad1 closure was verified on main 118e4882;
45 focused checks passed. This is the preceding data-capture closure, not the later article run.
[Closure verification](docs/active/daily-pipeline/accuracy/receipts/q4-initial-data-disabled-restoration-2026-10-25/verification.json)
retains both passing CI receipts, exact remote ad1 and the ignored main Git deployment.
[Execution specification](docs/active/daily-pipeline/accuracy/q4-initial-data-operational-activation-spec-2026-10-25.md).

The [current 25-source queue](docs/active/daily-pipeline/accuracy/current-candidate-source-queue-2026-10-25.md)
joins actual scheduled task IDs and full/304 clocks. Each missing scope, date-window,
pagination/terminal and primary-sample proof remains explicit. Rubrik still lacks its legacy
.news controller join; do not invent a route. Three rolling feeds remain incomplete, Orca's
page 27 self-redirect proves no terminal. Reviewed main bd38e818 now selects the exact seven-
target plan 3077d93e, with a 257-request whole-operation bound including all 25 generic probes.
Preview web 40190348231/main 40190772532 pass; Vercel preview READY/main Git ignored.
[Actual single diagnostic 40190857026](docs/active/daily-pipeline/accuracy/next-seven-newsroom-actual-source-review-2026-10-25.md)
completed successfully at 12:00:02 UTC from authenticated
496ad86a/869 baseline. All seven explicit targets returned HTTP 200 HTML at their exact final URLs.
It charged 116 requests: 109 generic reservations and seven explicit targets. Acknowledgement
9deb0c9c has 48,245 authenticated entries; only budget/released-lease heads changed. Six admissions,
four facts, 38 holds, normal heads and expiry remain exact. Independent full offline replay passes.
Listing/pagination leads remain unqualified. Exact disabled-plan ad1 restoration passes 27 focused
checks; reviewed preview/main closure and live verification follow this completed local unit.
No owner source decision is currently required.
The [next Q4 build specification](docs/active/daily-pipeline/accuracy/q4-single-response-qualification-build-spec-2026-10-25.md)
now has its dormant single-response parser and two exact financial primary samples. Independent
implementation review passes with no open findings after two date-metadata fixes. Final operational
checks pass 909/909, focused route checks 126/126, and the full application checks pass with one
existing browser skip. Both rendered widths remain byte-exact to the preceding local build.
Actual article run [40188161705](docs/active/daily-pipeline/accuracy/q4-primary-qualification-actual-source-review-2026-10-25.md)
passed execution on b7c7841a, completing at 11:20:57 UTC.
Both exact pages returned HTTP 200 HTML, but qualification accepted zero: both omit canonical
links and have generic H1 “News Details”. Original holds remain exact. Its independent audit
authenticates all 48,057 entries of d2efafcb, manifest bb1c3da1…383e4d, complete report replay,
six admissions, all 39,438 preceding immutable entries and 8,605 normal heads. Charges rose
867→869 only; facts, 38 holds and private/public expiry remain unchanged. No retry or credit.
Their [cold source-template review](docs/active/daily-pipeline/accuracy/q4-primary-retained-template-source-review-2026-10-25.md)
finds exact OG URL/title and same-item article H3/date/readable body; JFrog also has matching
NewsArticle metadata. The versioned offline proof now passes independent final-path review and
921 operational tests plus full application checks. Both render widths are unchanged. It derives
two complete proposal samples while preserving the old accepted-zero result and all zero operational
credit fields. Reviewed dormant proof is committed as 7a1aee7b. Normal-source integration is now
building in an isolated worktree under its accepted design; it still needs exact policy/package
review, fresh ordinary intake and later scheduled/public receipts.
Exact ad1 restoration passes 69 focused checks and both remote closure checks.

## Remaining acceptance

The repaired monitor is on main. Actual manual preview monitor40177951978 passed 36 runner
checks and reported real coverage/history/held gaps without its former byte-limit exception.
[Genuine repaired scheduled monitor 40191154739](docs/active/daily-pipeline/accuracy/scheduled-monitor-acceptance-2026-10-25.md)
ran on main bd38e818 at 11:59:34 UTC.
All 36 runner tests and exact-main offline replay pass; the accepted 1,337,257-byte public reader
and original-plan binding work. The actual workflow correctly fails on real coverage/review/held
gaps and the publisher failure, updating issue 10. No reader or schedule-matching error recurred.
Issue 10 retains coverage gaps;
GitHub issue delivery is proven, phone/email delivery unmeasured. One passing scheduled cycle
does not prove sustained operation. General claim precision/recall and reader value remain unmeasured.
[Evaluation rubric](docs/active/daily-pipeline/evaluation-rubric.md).
Remaining corrections stay in the [record qualification queue](docs/active/daily-pipeline/accuracy/remaining-record-qualification-status-2026-10-25.md);
none gains admission from a diagnostic. Old 121/557 combined coverage is not comparable to 264/557 daily intake.

Implementation: /Users/jessepike/code/projects/sec-market-finish-20261022.
Preserve /Users/jessepike/code/projects/sec-market at 0a660a72 with modified status/lessons and
untracked web/tests/daily-measures.test.ts. Exact remaining work is in BACKLOG.md.
