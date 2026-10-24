# Separate daily freshness, processing and historical review

Implementation authority: D-112, the owner's explicit October 24 choice of the reviewed policy
proposal. This specification implements that choice. It does not change the governing intent,
supplier/source inventory, spending limits or publishing authority.

## Measures

Version the market contract and collection mode explicitly. Keep the legacy combined mode fully
replayable with its original policy and immutable reports. New reports must identify their source
measure as daily intake; never compare a new intake count with old combined coverage as though the
definitions were identical.

| Measure | Required proof | Meaning and limits |
|---|---|---|
| Daily source intake, out of the full 557 obligations | Real fresh source observations, exact source/host/registration, complete independently replayed discovery or the existing structured/citation check | The declared source was checked. Missing bindings, unqualified sources, blocked requests and incomplete traversal remain gaps. This does not claim every event or historical field is reviewed. |
| Fact processing | Exact observed discovery/delta inventory, selected/current/changed/unknown/deferred URLs, complete semantic dispositions and unresolved work | Reviewed facts can publish through the existing gate. Pending and unknown work remains visible even when intake passed. An index date is only a scheduling hint. |
| Historical review | Full retained inventory and independently replayed original proof, with original source/review times and explicit pending/held sets | Earlier checks can remain historical evidence without pretending they were fetched today. Every URL remains in the denominator. This is not all-site precision or current-event recall. |

Keep intake, processing and historical status in separate machine-readable fields and derive them
from evidence. Preserve all 74 suppliers, 557 required tasks and every discovery/predecessor/pending
URL. Do not use one boolean `complete` to imply all three outcomes. The public reader must be able
to distinguish a quiet checked source, stale/failed intake, and fetched but unprocessed work.

## Runtime boundaries

1. Freshness applies to actual source/discovery checks and new admissions under existing rules.
   Full pagination, request/body bindings, allowed hosts, latest failed/conflicting transport and
   real conditional-response chains remain independently enforced. Old body hashes never supply
   fresh transport by themselves.
2. Retain the bounded daily selection, document/call/fetch ledgers, source rotation and audit work.
   Intake success may coexist with processing or historical gaps. A selected failed document,
   unreviewed delta or undated item remains visible; it cannot be silently called old or quiet.
3. Every published new fact needs current primary-source support and proper independent review.
   Replay retained evidence at the original admission/check time. Keep exact original facts,
   holds, review reasons, effective dates, observation times and provenance. A known relevant
   change requires revalidation or an explicit hold; historical reuse cannot close it.
4. Preserve exact full inventory/predecessor and candidate/disposition partitions, even for
   partial source work. Maintain the positive legacy migration boundary, no downgrade fallback,
   same-time ambiguity holds and causal predecessor retention established by the retained-proof
   repair. Copied old facts never become `newFactIds`.
5. Policy migration must not simply rewrite old contract hashes. Resolve original contracts and
   prove exact semantic context compatibility before any retained reuse. Source, supplier/aliases,
   source class/scope/hosts, extraction input and review-rule changes require appropriate new
   validation. Exclude only the explicitly changed freshness/reporting semantics when proving
   compatibility; an origin's full original policy stays pinned and replayed.
6. Structured SEC and citation checks retain their existing evidence requirements. The 80-claim
   SEC gate, primary-source restrictions, all six admitted correction groups and their original
   publication dates remain required. A new coverage measure cannot bypass any release check.
7. Avoid inconsistent duplicate status derivations. Collection, independent reconciliation,
   snapshot/public metadata, monitors and the offline scorecard must either understand the new
   version explicitly or fail closed. Legacy receipt evaluation stays under its original rules.

## Acceptance

Test fresh complete intake with unfinished history; stale/blocked/incomplete discovery; pending
new and unknown-date processing; old unchanged admitted evidence with original times; current
content/policy/source changes; missing or tampered original proof; feed rollover and omitted
predecessors; new-version downgrade; exhausted budgets; and exact retention of all obligations.
Demonstrate that processing/historical failures do not disappear behind a green intake count.

Replay the real archived inventory with exact before/after pins and no new source/model work.
Report each measure independently and grant no live credit from replay. Run integrated pipeline,
operational and application checks. Render the changed reader labels at desktop/phone widths;
compare the same data when judging layout. Use the normal preview/main and independent
exact-artifact publisher, respecting the already charged allowance. Obtain actual scheduled
collection/publication and public-byte receipts under this policy before calling it operational.

No source qualification, accuracy percentage, sustained-operation rate or reader-value result is
created by this specification or the owner's policy choice.
