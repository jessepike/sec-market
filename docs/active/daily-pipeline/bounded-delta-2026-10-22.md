# Bounded daily collection

Implementation amendment for the owner's October 22 request to finish daily public-source
collection on GitHub Actions and Vercel. This records the implementation; it does not assert
approval of unseen artifacts or change the governing intent.

Daily semantic collection selects at most two documents per registered non-SEC discovery source.
Changed index timestamps and new timestamps within 30 days go first. An index timestamp is a
scheduling hint and never establishes a fact's date. One remaining slot can audit an older or
undated document. Successfully checked unchanged documents rotate out for 30 days; changed index
timestamps make them immediately eligible again. Same-priority sources rotate deterministically
each UTC day so the global subscription limit does not always favor the first suppliers.

Every discovered URL remains archived. Prior pending URLs survive disappearance from feeds.
Deferred URLs stay in the pending manifest, and a separate audit-work cursor advances only for
documents with completed semantic validation. The successful full-source cursor never advances
for an incomplete source. Required families, the 74-supplier denominator and all 557 tasks remain.
This policy cannot establish freshness of every displayed historical field. Missing source bindings,
held claims, undated documents and unaudited history remain incomplete in coverage.

The existing release policy allows degraded discovery coverage. Independently reviewed primary
source facts can therefore publish through the existing exact-artifact gate while discovery gaps
stay visible. Each changed fact retains its evidence, effective date and semantic review. The
SEC tier still requires its complete claim inventory and fresh certification. No new financial
field receives a fresh label merely because a source index was visited.

The collection schedule is 04:37 UTC daily; publication checks are 05:23 and 16:23 UTC.
Daily model, document and fetch reservations remain persistent and are never reset by this change.
The first historical audit may take many days; this policy makes daily work finite rather than
claiming that subscription capacity can clear the historical queue every day.

The committed preview snapshot predates this policy. Its old source successes are conservatively
held as `POLICY_CHANGED_RECHECK_REQUIRED`, so it now reports zero of 557 current-policy checks.
The original collection times stay unchanged; `supersededPolicy` retains the old contract and
snapshot hashes. No fresh collection or financial certification is implied by regenerating this
preview file. The independently reconstructed release replaces it after real collection.
