# Operational evaluation rubric

The present priority is a site that works consistently, survives failures, and presents accurate,
fresh information. The owner reports no observed real use yet. Value remains unmeasured; it is
not a current acceptance gate. Broader discovery and reader-use measurement follow reliability work.

The governing intent orders freshness, coverage, use and reconstructability. This scorecard makes
those outcomes inspectable through separate durability, accuracy, freshness, coverage and value
measures. There is no weighted average, overall confidence percentage or compensating score.

## Measures and interpretation

| Axis | Current measure | Pass condition | Evidence boundary |
|---|---|---|---|
| Durability | Scheduled execution, exact publication, rollback/restoration | Each supplied receipt is internally bound to its expected run/release and records the required successful result | A successful cycle is historical proof for that cycle. Multi-day durability stays unmeasured without a complete observation-window history. |
| Accuracy | Known release checks, with executed test count | Independent SEC/release checks report pass with pinned log hashes and exact coverage/artifact identities | Passing known tests is not an estimated all-site precision or recall rate. |
| Accuracy | Claim precision and eligible-event recall | Unmeasured until a reviewed benchmark and explicit scoring denominators exist | No invented percentage from passing tests, source links or a semantic reviewer's confidence. |
| Accuracy | Fixed published-record audit and known contradictions | Complete the pinned audit inventory and retain zero known contradicting records | Review coverage and semantic correctness are separate. Known factual errors fail this measure even when release checks pass; insufficient evidence is not proof that a claim is false. |
| Freshness | Collection receipt age | Receipt age is within the pinned contract's overdueHours | A recent governance check cannot renew an older source check. This offline evaluator reports check age and does not replay source bodies. |
| Freshness | All required checks | All fixed obligations complete and collection receipt within deadline | Partial fresh work cannot make the whole roster fresh. |
| Coverage | Required source tasks and SEC subset | Successful tasks equal the complete contract-derived denominator | Registration, source checking and historical claim accuracy remain separate. Missing bindings stay in the denominator. |
| Value | Observed use | Unmeasured now | No real use reported. Analytics installation and operational success do not establish reader value. |

Each machine-readable measure records status (`pass`, `fail`, `unmeasured`), exact numerator and
denominator where applicable, original observation time, evidence references and limitations.
Unmeasured numbers are null. Freshness reports also include age and the contractual age limit.

## Executable implementation

`ops/evaluation/scorecard.py` produces JSON and Markdown offline from an explicit hash-pinned
manifest. It checks raw file hashes, contract/run/task identities, full receipt inventories,
coverage counters, gap sets, gate-to-collection binding and publication-to-rollback binding.
Changing a denominator or supplying inconsistent evidence is an error, not a lower score.
The tool refuses future observations and never replaces timestamps with the evaluation time.
It uses the existing contract planner and does not modify pipeline state or wire a new workflow.

The first actual baseline is 121/557 source checks, including 48/48 SEC tasks, under the accepted
October 23 policy. Coverage is incomplete. The first scheduled execution, publication and rollback
have evidence. Sustained operation, overall claim precision, eligible-event recall and value do not.
Retain each generated report's pinned policy and evidence so later working-contract changes cannot
rewrite this baseline. Offline corrections do not imply improved live coverage.

The October 24 [operational report](evaluations/2026-10-24/operational-scorecard.md) records
244/557 checks and 48/48 SEC source tasks using the original collection receipt and the repaired
release's exact gate, publication and rollback receipts. The report's evaluation time is fixed;
its freshness result describes that time. Scheduled execution on this repaired revision and
sustained operation remain unmeasured. Manual execution is not a failed or successful timer
attempt. See `ops/evaluation/README.md` for the reproduction command and input boundaries.

Under `daily_intake_with_separate_history`, intake, processing and historical review are distinct
coverage measures. Intake requires a collected schema-2 observation. A checked task must have
complete raw discovery and observation references; failed intake may retain partial or ineligible
observations. Pending or held current processing remains visible even when intake
passes; historical backlog is reported separately and cannot renew source age. Empty observed
document inventories are unmeasured, not 0/0. These separate summaries do not estimate claim
precision, event recall or all-site accuracy, and they do not change the fixed source denominator.

The actual new-policy [manual collection observation](evaluations/2026-10-24/new-policy-manual-observation.md)
records 261/557 intake checks at 05:41:33 UTC on October 24, with processing/history still 24/9,914.
Its separate scorecard leaves timer execution and new-policy publication unmeasured. The matching
archive canary passes, but supplies no source, timer or release credit. Preserve the old-policy
reports and actual public-release evidence alongside this new private-policy observation.

## Trust and further evaluation

The October 25 [recovery observation](evaluations/2026-10-25/recovery-observation.md) applies
the same evaluator to actual recovery release fc8bf098: intake 264/557, processing 38/10,655
and history 39/10,655. Known release checks, publication, rollback/restoration and explicit
continuity checks pass. Genuine timer evidence on this revision, sustained operation, general
claim precision/recall and reader value remain unmeasured. The actual source-bound expiry
stays distinct from the evaluator's collection-receipt age. The prior overdue window is retained.

Later that day, [genuine scheduled run 40182324149](accuracy/scheduled-h-acceptance-2026-10-25.md)
passed its exact-H source and continuity audit on main 71c39356. GitHub started it 4h33m43s late.
Intake remains 264/557; processing/history reached 40/41 of 10,655 and the hold queue reached 38.
This supplies one genuine repaired-code timer receipt. Automatic publisher 40183462577 failed
at the unchanged daily gate allowance and created assigned issue 14; no new public release followed.
The private snapshot expiry and actual public expiry remain separate. Preserve the earlier
recovery evaluation at its original time rather than substituting this later source receipt.
Multi-day durability, general precision/recall and reader value remain unmeasured.

The separate [authenticated current-remediation observation](accuracy/current-correction-resolution-observation-2026-10-24.md)
records all five mapped contradictions resolved around 04:01 UTC on October 24. It binds the
original accepted reviews and reservations, exact gate/publisher evidence and live static bytes.
The historical 177-record audit retains its original results. Five repaired benchmark records
do not establish general current accuracy, event recall, sustained operation or reader value.

Pins establish byte identity and reproducibility, not independent authenticity. The caller must
obtain reviewed actual receipts. Archive body replay, actual GitHub run verification and current
live probes remain the existing release/monitor responsibilities. This scorecard cannot certify
sources by reading a summary receipt.

A future accuracy benchmark should contain fixed reviewed primary documents covering positive,
quiet, amended, ambiguous and blocked cases across supported claim types. Record expected eligible
facts, extracted facts, correct extracted facts, omissions and rejected/held claims. Score precision
and recall independently with explicit counts; do not count a held document as a true negative
without an established expected answer. Proposed benchmark metrics have no present pass result.

Sustained durability needs a complete dated window of expected schedules, actual scheduled runs,
missed/failed runs, correct quiet runs, publication acknowledgements and recovery events. Record
that window and its denominator before calculating a rate. Its acceptance duration remains an
explicit choice; this tool does not invent one.

## Data continuity and broad coverage

Data continuity is a separate durability measure. The source snapshot retained 28 pending
reviews while the accepted snapshot retained 14; four historical candidates had no
retained/quarantined counterparts there. Those candidates were held under an older policy and
must not be treated as four expected publications. Their expected outcome is durable
review/quarantine retention. Record failed continuity when the pinned audit is supplied;
without it the evaluator reports unmeasured. The first-cycle rollback result remains independent.

Coverage tables expose all 557 obligations by reason, source family, supplier and domain, along
with 275 verified registrations, 28 candidates and 254 missing bindings. Those registration
counts do not reduce the full denominator or imply successful checks. Domain counts may overlap.

## October 25 later timer evidence

The registration counts immediately above describe the earlier policy. Current H has 278 verified
and 25 candidate bindings, with 254 missing obligations retained. Its 264/557 successful tasks comprise
196 citation-integrity, 48 SEC, 17 official-announcement and three investor/acquirer checks. This remains
partial coverage; it does not measure event recall or general factual precision.

Actual genuine scheduled collector 40182324149 passed with new source observations, preserved
facts/admissions/holds and an authenticated complete archive. Actual scheduled publisher 40190348786
subsequently failed at the unchanged two-attempt gate allowance and updated assigned issue 14.
The [scheduled-publisher audit](accuracy/scheduled-publisher-attempt-2026-10-25.md) verifies released
lease, unchanged 869/80/38/gates 2, normal-state continuity and four byte-exact public files.
This adds unattended execution and failure-alert evidence. It supplies no successful automatic
publication, new public freshness, multi-day availability rate or measured reader value. Keep the
earlier manual recovery/publication scorecard and its original inputs intact.

Actual [repaired scheduled monitor 40191154739](accuracy/scheduled-monitor-acceptance-2026-10-25.md)
ran on main bd38e818 at 11:59 UTC. Its 36 actual
runner tests and exact-main offline replay pass. The accepted public coverage bytes and original
collection-plan binding pass; neither former reader nor schedule-matching error recurred. Its
actual failure correctly reports coverage, review and held-claim gaps plus the publisher failure,
and updates issue 10. This supplies one genuine monitor receipt, not a healthy-state verdict.

Later diagnostic 40190857026 authenticated all 48,245 archive entries and replayed its full result.
Its 116 requests include all seven explicit HTTP 200 captures. The settled ledger is 985 fetches,
80 calls, 38 documents and two gates; six admissions, four facts, 38 holds and source expiry stay
exact. These observations provide source-qualification inputs without adding intake or public
freshness credit. The separate accepted retained-Q4-template proof remains dormant and supplies
no operational credit. General accuracy, event recall, reader value and multi-day durability
remain unmeasured.

The later [listing/pagination capture 40193925490](accuracy/narrow-listing-pagination-actual-source-review-2026-10-25.md)
also passes its full 48,420-entry archive and original report replay. Its 116 retrieval charges
settle the ledger at 1,101/80/38 with two gates; ordinary facts, holds, six admissions and both
private/public freshness clocks remain unchanged. Its reviewed disabled-plan closure on main
61265b57 passes preview/main CI and all four live public files remain byte-exact. Source-qualified
intake remains 264/557. Retained listing/window/primary proof inputs add no intake, semantic review,
historical-review, scheduled-run or publication credit. Cato's positive current-window evidence
and unknown older archive remain distinct; the daily-window parser still requires its own review.
