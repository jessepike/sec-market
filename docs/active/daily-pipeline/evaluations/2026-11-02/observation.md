# November 2: current operational scorecard and remaining source work

The existing five-axis rubric is usable and has been refreshed against the accepted November 2
production receipts. Daily source intake is **262 of 557 checks, with 295 gaps**. A genuine
scheduled collector and its publication passed. The older 121/557 number used a combined rule;
it keeps its original policy and is not directly interchangeable with the current separated-intake
measure. The count change alone is not measured coverage improvement. Complete coverage,
sustained operation and reader value remain unproved.

I recommend using this scorecard together with the exact gap queue. The scorecard says which
outcomes are demonstrated; the queue names the source work that can move coverage. Keep the
entire 557-check denominator and report intake, document processing and historical review
separately.

## Five axes, without a blended grade

Evaluation time is November 2 at 17:05:36 UTC. The collected observation is November 2 at
13:47:47.878832 UTC. This is a dated readout of those pinned receipts, not a claim about later
live state.

| Axis | What the evidence proves | What remains open |
| --- | --- | --- |
| Freshness | The collection check is 3.30 hours old against the unchanged 30-hour threshold. | Full-roster freshness fails because only 262/557 declared intake obligations passed. A recent check is not a fresh source body or complete-event inventory. |
| Coverage | 262/557 intake checks passed; all 48/48 SEC source checks passed. Processing reviewed 83 of 11,671 documents; historical review reviewed 84 of 11,671. | Intake has 295 gaps. Processing has 11,588 pending, 20 held and 1,479 unknown-date documents. History has 11,587 pending and 20 held. The review queue has 51 items. Reviewed does not mean accurate or eligible for publication. |
| Accuracy | The pinned independent release gate passed four required checks and reports 538 executed tests. The separate accepted-release audit proves all 80 required SEC claims passed with zero drift and all eight accepted corrections remain. | General claim precision, event recall, a current published-claim audit and absence of contradictions remain unmeasured. Passing release checks do not score every supplier fact. |
| Durability | One genuine scheduled collection and its exact accepted publication passed. The separately retained byte audit matched all 53 build files and all 52 public static files. | The current rollback drill was skipped. The unchanged evaluator has no qualifying current rollback or held/history continuity audit and no complete observation-window history, so those measures remain unmeasured. One or two successful days do not establish a sustained-operation rate. |
| Value | The owner has reported no actual useful decision or conversation yet. | Value stays unmeasured. No use, retention, or decision-quality score is invented from technical operation. |

The [separately pinned byte audits](supplemental-evidence.json) retain the November 1 and November 2
observations: each matched 53 accepted build files and 52 public static files. This supplies two
dated occurrences, without inventing a complete expected/attempted schedule history.

The [machine-readable scorecard](scorecard.json) and its [generated table](scorecard.md) were
produced by the unchanged `ops/evaluation/scorecard.py`. The evaluator itself is pinned in
`verification.json`. It checks raw receipt identities and counters; it does not authenticate
GitHub, replay archived source bodies or adjudicate every claim. Separate authenticated archive,
artifact and public-byte evidence remains in the [actual production audit](../../receipts/scheduled-2026-11-02/audit.md).

## Exactly what the 295 gaps need

The [JSON action queue](gap-action-queue.json) and [tab-separated action queue](gap-action-queue.tsv)
contain every actual unsuccessful required task, once. Both preserve the original daily task ID,
source ID or explicit null, supplier, source family, outcome/error and declared URL where one
exists. A missing source receives no guessed URL or invented registration. The stable derived
supplier/family work key for a missing binding is clearly distinguished from a source ID. Daily
task IDs change with their run; use stable named sources or the derived obligation key when
comparing work across days.

| Operator work | Exact current count | Next action |
| --- | ---: | --- |
| Qualify undeclared discovery sources | 254 | Find and prove the existing supplier/family source obligation, entity and date scope, pagination and positive/quiet/blocked cases. Preserve the obligation until registration. |
| Qualify declared candidates | 23 | Complete the candidate's primary-evidence and complete-discovery proof before granting coverage. A retained candidate or passing parser test alone earns no credit. |
| Repair source transport | 16 | Inspect nine HTTP 403, four HTTP 429, two HTTP 504 and one unapproved redirect-host result. Use approved routes and bounded retries; retain blocked/unknown until actual successful collection. |
| Repair the observed Q4 inventory parser | 2 | JFrog and Rapid7 returned `Q4_INDEX_INCOMPLETE:Q4_LIST_ROW_SCHEMA_INVALID`. Reproduce against the saved primary bytes, preserve scope/identity/date/completeness guards and verify an actual normal run after any repair. |

The 254 missing obligations break down into 39 official-announcement, 52 investor/acquirer,
74 independent-reporting, 67 release-distribution and 22 regulatory obligations (11 regulatory
filings and 11 filing-document obligations in the exact contract). The declared
source inventory includes 280 verified registrations plus 23 candidates; registration
is not successful intake. Three net lost checks since November 1 are Cohesity's official source
returning 403 and WitnessAI's citation and official sources returning 504. They explain the
change from 265 to 262 without reducing the denominator. See the [retained day comparison](../../receipts/scheduled-2026-11-02/coverage-delta.json).

The current intake errors establish operator work. They do not establish a specific question
that only the owner can answer. Ordinary source and factual review remain operator-owned. A
later resource, access, authority or unavailable-source limitation needs its own concrete proof
before an owner decision is requested. Existing source-addition and production-release review
rules remain in force. The separately pending visible company-search Preview review does not
turn these source checks into owner tasks.

## Cost and runtime are separate conditions

The accepted release used GitHub-hosted execution and the existing subscription CLI, with
`apiFallback: false`; it did not use Codex Cloud or the held managed-runtime trial. Its actual
Basic build charged $0.007. The retained November 2 16:36 UTC export reports a $0.01133548 site
subtotal, before the later search Preview; that day is incomplete. November 1's closed two-project
reported total is $0.10936186 and failed the unchanged five-cent condition. The $0.30 trial stays
stopped because the retained forecast is $0.363698081765. This scoring run made no provider call,
model call, budget change, credential action or production write.

A complete successful Basic-day bill, actual scheduled runner savings after the reviewed change,
retained resource growth, independent missed/stale detection, actual device delivery and fresh
recovery evidence remain separate operating work. Refer to the [cost review](../../receipts/scheduled-2026-11-02/cost-review.md)
and the [tested Preview receipts](../../receipts/search-preview-2026-11-02/audit.md) for their exact
current bounds. They are not folded into a flattering overall score.

## Exact replay and skipped-rollback limit

Run from the repository in the OrbStack dev VM, choosing a new output prefix:

```sh
python3 ops/evaluation/scorecard.py \
  --manifest docs/active/daily-pipeline/evaluations/2026-11-02/scorecard-inputs.json \
  --output /tmp/smp-nov2-scorecard-replay
```

`scorecard-inputs.json` pins exact copied raw input bytes. The full 1,373,348-byte coverage
receipt, all 557 raw task receipts and all 557 intake views are retained here. The source
contract's raw SHA differs from its canonical policy digest; both are recorded and checked.
Changing formatting was not used to manufacture the gate's collection hash.

The actual skipped preflight is preserved verbatim as `inputs/rollback-preflight.json`. It has
no `drill` object. A separate attempt to supply it to the unchanged evaluator exited 2 with
`Evaluation refused: 'drill'` and wrote no scorecard. The [refused manifest](rollback-refusal-inputs.json)
and [exact refusal](rollback-schema-refusal.json) retain this schema boundary. The valid report
omits the nonqualifying optional rollback input and reports rollback as unmeasured. No substitute
successful receipt or method relaxation was created.

The canonical personal-platform standard source remains
`ff32b0055293e4fb3bce550bade4652cc2ee1aa3`: this is T2 Important, with Public source facts,
Internal operational evidence and no copied Confidential credentials. Existing hosted execution
and private evidence-archive exceptions remain. This report creates no platform or provider choice.
