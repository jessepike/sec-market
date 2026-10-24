# D-112 operational evaluation and monitoring

Extend the existing offline scorecard and watchdog for the accepted versioned policy. Keep legacy
reports byte-reproducible and historical labels unchanged. This adds no authority to supplied
JSON and grants no new source credit.

For `market-daily-v2` / `daily_intake_with_separate_history`, require coverage schema 2 and measure
`daily_source_intake_v2`. Derive intake successes from each receipt's explicit intake outcome,
preserve the full contract-derived task denominator, and compare the complete task inventory,
intake aliases and gaps. An old processing outcome cannot substitute for an intake outcome.

Independently check source/task processing and historical summaries before aggregating them.
Counts are nonnegative integers, never booleans. `inventoryDocuments = reviewedDocuments +
pendingDocuments`; held documents are a subset of reviewed documents. Processing is complete
only with zero pending and held documents; historical review is complete with zero pending,
while held documents remain explicit. Changed and unknown-date classifications are disjoint
and may overlap the reviewed/pending sets. Count source/URL obligations rather than pretending
the shared publisher's duplicate source contexts are unique fetched documents.

Add distinct intake, processing and historical-review measures with exact counts and limits.
An empty observed document inventory supplies no accuracy percentage. State that a completed
review may hold claims and that an intake pass supplies no all-site accuracy or event-recall
result. Preserve original collection timestamps and the existing age limit. Manual execution
still creates no scheduled-attempt denominator.

The watchdog must identify the new measure explicitly, report intake gaps separately from
pending/held processing, and expose historical backlog independently. Stale intake, inconsistent
schema/counters, incomplete discovery or pending current processing must not hide behind an
intake pass. Historical progress alone cannot renew source age. Keep existing delivery through
the same assigned GitHub issue, with no new service or notifications mechanism.

Tests cover legacy byte-exact reproduction, valid separate summaries, false completeness,
tampered aggregate/task/receipt counters, boolean/negative counts, unknown versions, processing
holds with successful intake, empty observed inventory, stale dates and independent historical
backlog. Real scheduling, publication and alert delivery retain their separate actual receipts.
