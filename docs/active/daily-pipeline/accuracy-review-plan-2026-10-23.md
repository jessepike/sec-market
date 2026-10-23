# Archived review of existing published claims

## Purpose and authority

Continue SEC-072 and the active coverage/accuracy goal while October 23's collection allowance is
spent. Check existing published records against evidence already retained in the verified archive.
This is current-site accuracy work, before new source families, supplier expansion or search.
No source fetches, extraction/review service calls, allowance changes or production mutations.

## Fixed scope

Freeze the complete `handCollectedEvents` array in `web/src/data/tracker/events.ts`, partitioned
by supplier ID a–m and n–z. Separately freeze `lastRound`, `headlineMetric` and `ownership` fields
on `manualTrackerSuppliers` without an `edgarId`. Record each partition's exact IDs and field count.
These files and `web/src/data/evidence.ts` match production application revision
`7bd94ec77e99462c068f254e134235a894585cbb`; confirm that comparison before relying on the scope.

Pin raw dataset-file SHA-256 values and exact published record objects. Evidence is the verified
25,777-file archive at commit `b78cfa15980d7be9da54b31e28b16a0840c1d112`, manifest SHA-256
`760b5c38fcb7fba2a3a223233539cce4eb5aa47d559571efa95b287047ac1ff8`.
The restored baseline is read-only. Every source reference must bind an archived observation,
actual URL, original fetched time and verified body hash. Archive accessibility is not claim support.

## Review rules

Check the named entity, exact action, announced versus completed status, figures and units,
qualifiers, reporting period and date. An article publication date cannot establish when an older
event occurred. A listing card or related-story sidebar cannot establish an article's subject.
Primary source support is required to mark a record supported. Treat secondary-source claims,
missing bodies, ambiguous dates and unsupported clauses explicitly.

Use `supported`, `contradicted`, `insufficient` or `primary_source_missing`, with concise evidence
and limitations. Record the expected inventory, every reviewed ID and any omitted records. Keep
source-age/current endpoint coverage separate from historical source support. Suggest precise
corrections where archived primary evidence is sufficient, but do not edit published records during
the audit. Apply any later correction under the existing record/correction rules and normal gate.

## Deliverables and limits

Retain partition JSON ledgers under `docs/active/daily-pipeline/accuracy/`, then reconcile counts,
proof hashes and correction candidates in a single review. Validate the source/dataset bindings
separately from semantic review. An automated check can establish byte identity and inventory
completeness; it cannot turn an agent's source interpretation into an independent factual oracle.

The operational scorecard may consume a hash-pinned binding report for the same production
application revision. Expose reviewed inventory and known contradicting records separately from
release-test results. A known contradiction fails its own measure even when the release tests
passed. Do not convert supported/insufficient counts into an overall accuracy percentage.

This scope does not include every rendered field, SEC-derived records, missing eligible events,
or the frozen issue/thesis. It therefore cannot produce all-site precision, recall or usefulness
scores. Preserve the scorecard's unmeasured results until a suitable benchmark and denominators
exist. Never count an unavailable source as correct or silently waive a coverage obligation.
