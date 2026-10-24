# Daily freshness and retained history

Proposed coverage-policy decision, October 24, 2026. No policy, denominator, allowance or runtime
behavior changes through this document. Daily activation remains approved.

## Decision

I recommend measuring daily source freshness and historical review separately. Keep every
required source and historical URL, preserve their original evidence dates, and show unfinished
history explicitly. Continue the authorized code repairs under the current strict rules until
the owner decides this proposal.

| Choice | Required behavior | Consequence |
|---|---|---|
| Separate daily freshness from historical review | Require fresh, complete discovery checks and proper review of new or changed facts. Replay retained evidence at its original admission time. Report the entire historical inventory and its reviewed/pending counts separately. | This permits a bounded daily-monitoring design while history progresses; actual intake and processing capacity still need measurement. An old source document never acquires a new retrieval date or a fresh label from replay. |
| Keep the current combined rule | Require every historical document in a source's inventory to have successful transport within 30 hours, under the current two-document scheduled source limit. | Large historical sources remain incomplete. A completed initial audit cannot make their whole inventories stay fresh through the current daily job. |

The choice concerns what a successful source check establishes. It does not authorize spending,
raising limits, removing difficult sources or declaring unknown claims accurate.

## Observed conflict

The current contract sets a 24-hour interval, a 30-hour overdue threshold, at most two processed
documents per source invocation, one audit document per source, 40 documents and 80 model calls
per daily allowance, and 5,500 fetch reservations. Generic reconciliation requires successful
document observations to fall within the same 30-hour limit.

The retained archive has 9,914 source/URL obligations across 17 historical sources. Dragos alone
has 3,256. The retained-proof repair preserves all these URLs. It can authenticate earlier work;
it cannot turn an old fetch into a fresh request.

The independent inventory count finds 9,276 distinct article URLs. Exactly 638 are shared by
Exabeam and Sophos; current transport keeps their source identities separate. Keeping just these
articles within 30 hours requires an average 7,931.2 source-bound article requests per day. Even
ideal safe sharing of every duplicate would require 7,420.8 per day. Both exceed 5,500 before
index traversal and all other required tasks. A successful conditional response still consumes
a fetch. These are necessary sustained-throughput bounds, not a claim that every request
succeeds or that every page needs new model work.

Two regular daily invocations can fall within a 30-hour interval, providing at most four selected
documents for a source. The normal daily path therefore cannot supply fresh transport for all
3,256 Dragos documents at once. Repeating arbitrary manual invocations is outside this proposed
operating solution. Conditional responses and semantic caches can save work, but neither creates
a new request without selection, reservation and actual successful transport.

The bounded-delta implementation explicitly says that historical audit may take many days and
that unchanged checked documents rotate out for 30 days. This conflicts with requiring their
transport to remain less than 30 hours old for whole-source success. A scheduler or timestamp
repair alone cannot reconcile the two definitions.

## Required boundaries if the separation is accepted

1. Preserve the 74 suppliers, all 557 required source tasks, every retained historical URL and all
   unresolved facts. Keep historical 121/557 and 244/557 reports unchanged under their original
   policy. A new policy needs an explicit version and a separate measured baseline.
2. Keep the daily source/discovery observation fresh within 30 hours. Require full demonstrated
   pagination and source scope. Missing pages, blocked transport and an unfetched shell remain
   incomplete. Visiting one index cannot establish that all current events were found.
3. Separate a successful intake check from completed fact processing. Unreviewed new or changed
   documents remain visible processing work; a quiet source requires evidence. Unknown dates
   cannot be relabelled old and silently removed from current uncertainty.
4. Admit a new fact only through the existing current primary-source and independent-review
   checks. A retained fact must replay its complete original proof and preserve its evidence,
   effective date and review time. Relevant source, policy, input or content changes require
   proper new validation. The old document must never be labelled freshly retrieved.
5. Report historical review with its complete inventory denominator and exact completed,
   unresolved and deferred sets. Show original review dates and incomplete coverage. An intake
   pass cannot become a historical-review pass or an all-site accuracy claim.
6. Reuse the existing ledger, daily workflow, exact-artifact publisher, Vercel project and alerts.
   Do not add a service, purchase capacity, refund usage or introduce paid API fallback.
7. Before activation of a changed policy, test missed current events, feed rollover, unknown
   dates, old unchanged evidence, real changes, failed requests, policy mismatch, stale intake,
   exhausted budgets and full inventory retention. Obtain actual scheduled and production
   receipts under the accepted policy. Existing activation approval does not supply these receipts.

## Evidence and countercase

The contract is `contracts/market.json`; the accepted implementation description is
`docs/active/daily-pipeline/bounded-delta-2026-10-22.md`. The retained inventory and original chains
are pinned in `retained-audit-rebinding-spec-2026-10-24.json` beside this document. The independent
[feasibility audit](historical-freshness-feasibility-2026-10-24.md) supplies exact per-source counts,
unique transport inventory and the limits of the arithmetic.

The strongest case for keeping the combined rule is that a fresh index cannot prove an old
article has not changed. Separate freshness requires clear evidence-age labels and honest audit
limits; it cannot promise daily verification of every historical claim. Existing semantic caches,
safe entity screening or a better qualified source can reduce work. They do not, by themselves,
make every retained page fresh. Evidence that current source-specific boundaries safely reduce
the required inventory within the present work limits would change the recommendation for those
sources; unproved exclusions do not.

Current live coverage stays 244/557. This proposal provides no source qualification, new review,
coverage credit, scheduled-run proof or publication.
