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
| October 25 ledger | 867/5,500 fetches, 80/80 model calls, 38/40 documents; gates 2/2. The diagnostic charged exactly two fetches; no reset or paid fallback. |

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

## Current source work

Reviewed main is closure 118e4882 with exact disabled ad1. Preview web 40185298950 and main
web 40185476864 pass; preview dpl_BmTzFF4dRCXwbnsyuWvFv8RT5RcN is READY, main Git build
dpl_87Zuaor1hVohRAWFPsZUrMrx18MQ is CANCELED. Main Git builds and automatic production-domain
assignment remain closed. A main push does not publish.
[Promotion proof](docs/active/daily-pipeline/accuracy/q4-initial-data-reviewed-code-promotion-2026-10-25.md).

Actual six-script diagnostic 40179255547 captured JFrog/Rapid7/Rubrik controllers and preserved
all earlier evidence. Their static inspection supports two exact JFrog/Rapid7 data GETs.
The closed implementation, 877 operational checks, full application checks and independent
reviews pass; both screen widths are unchanged. Manual two-request diagnostic 40184027106
passed on main ab6a7c68. Its [actual audit](docs/active/daily-pipeline/accuracy/q4-initial-data-capture-actual-source-review-2026-10-25.md)
verifies all 48,045 entries of d6606a4f, the full report and six admissions. JFrog returned
206 records and Rapid7 323; literal dates have no timezone. All normal heads, facts, 38 holds
and expiry remain exact. Actual callbacks skipped publication and rollback. Qualification
and coverage credit remain zero. Exact disabled ad1 is verified remotely on main 118e4882;
45 focused restoration/lease/report checks pass. Public receipt remains byte-exact.
[Closure verification](docs/active/daily-pipeline/accuracy/receipts/q4-initial-data-disabled-restoration-2026-10-25/verification.json)
retains both passing CI receipts, exact remote ad1 and the ignored main Git deployment.
[Execution specification](docs/active/daily-pipeline/accuracy/q4-initial-data-operational-activation-spec-2026-10-25.md).

The [current 25-source queue](docs/active/daily-pipeline/accuracy/current-candidate-source-queue-2026-10-25.md)
joins actual scheduled task IDs and full/304 clocks. Each missing scope, date-window,
pagination/terminal and primary-sample proof remains explicit. Rubrik still lacks its legacy
.news controller join; do not invent a route. Three rolling feeds remain incomplete, Orca's
page 27 self-redirect proves no terminal, and the next seven-index plan stays dormant with
a 257-request whole-operation bound. No owner source decision is currently required.
The [next Q4 build specification](docs/active/daily-pipeline/accuracy/q4-single-response-qualification-build-spec-2026-10-25.md)
now has its dormant single-response parser and two exact financial primary samples. Independent
implementation review passes with no open findings after two date-metadata fixes. Final operational
checks pass 909/909, focused route checks 126/126, and the full application checks pass with one
existing browser skip. Both rendered widths remain byte-exact to the preceding local build.
The dormant build is committed as 5b7e8f50. H remains unchanged. The separate operational
selection copies the exact 4,211-byte plan, raw hash 3a25e8e2 and canonical hash 3b7fc7c4,
for two article requests. Remote main still has disabled ad1 until reviewed promotion. Actual
samples, archived proof and normal-source activation remain. A subsequent test-file cleanup
removes only two trailing blank lines; historical reviewed code/log pins remain unchanged.

## Remaining acceptance

The repaired monitor is on main. Actual manual preview monitor40177951978 passed 36 runner
checks and reported real coverage/history/held gaps without its former byte-limit exception.
Genuine repaired scheduled-main monitoring remains pending. Issue 10 retains coverage gaps;
GitHub issue delivery is proven, phone/email delivery unmeasured. One passing scheduled cycle
does not prove sustained operation. General claim precision/recall and reader value remain unmeasured.
[Evaluation rubric](docs/active/daily-pipeline/evaluation-rubric.md).
Remaining corrections stay in the [record qualification queue](docs/active/daily-pipeline/accuracy/remaining-record-qualification-status-2026-10-25.md);
none gains admission from a diagnostic. Old 121/557 combined coverage is not comparable to 264/557 daily intake.

Implementation: /Users/jessepike/code/projects/sec-market-finish-20261022.
Preserve /Users/jessepike/code/projects/sec-market at 0a660a72 with modified status/lessons and
untracked web/tests/daily-measures.test.ts. Exact remaining work is in BACKLOG.md.
