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

## Trust and further evaluation

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
