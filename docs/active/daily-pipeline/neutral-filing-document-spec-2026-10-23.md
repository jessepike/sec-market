# Parent and direct issuer filing-document retention

Prepared October 23, 2026 under SEC-072. This closes the filing-document half of the existing
22 regulatory/document gaps. The preceding neutral `sec_index` adapter covers index checking.
The existing `sec_documents` kind already retains readable filing bodies without extracting
facts. Extend that kind with an explicit `regulatoryIssuer` binding and independently verified
index provenance. Do not introduce a second semantic or certified tier.

## Contract and invariants

An explicit issuer-bound `sec_documents` source belongs only to `filing_documents`. Require the
same exact issuer declaration, supplier-kind/direct-or-parent join, exact submissions URL, CIK,
legal name and bounded retention window as the neutral index adapter. Allowed hosts are exactly
`data.sec.gov` and `www.sec.gov`; the latter is solely for exact primary accession document URLs.
CIK fields must agree. A source cannot gain qualification merely by declaring this mapping.
Candidate registration performs no requests and remains a gap. Existing certified-company
sources retain their behavior; active contracts, roster, 557 obligations and counters do not change.

## Discovery, collection and independent reconciliation

Verify the complete retained submissions traversal with the existing neutral index verifier.
Derive exact eligible primary URLs and filing dates from its validated rows, using the existing
SEC form set including 20-F/6-K and amendments. Reject unsafe paths, wrong/missing issuer, sparse
or unequal tables, omitted older pages, conflicting duplicate rows, missing primary documents,
future dates and incomplete traversal. Share the form set rather than duplicating it.

Collect the eligible primary documents under existing charged fetch, time, document and retention
bounds. Use the existing readable-document check; unreadable, blocked or missing documents keep
the task incomplete. Preserve exact immutable accession body provenance and current index anchors
when reusing a previously retained filing. A successful empty document selection requires a
complete validated index proving no eligible documents in the declared window.

Archive a bound index-verification record with its ordered index observations, actual traversal
and verification times, exact source/subject/contract identity and eligible URL/date selection.
Independent reconciliation reconstructs this record and the eligible inventory from exact retained
index bodies, verifies every document URL/body/readable-text binding and requires that the document
set equals the selected inventory. Do not use a hash of a self-authored summary as the only proof.
Retain original source times; crossing a UTC-day window fails before it can establish completeness.
Reject nonempty validated facts, new fact IDs, semantic document validations or held claims for
this path, including partial reconciliation and inherited source-head caches. `documents` is the
explicit body-retention list, never semantic admission. Invoke no structured SEC adapter or model.

Keep generic HTML extraction, existing certified-company sources and ordinary-source supplier
isolation unchanged. Do not change the main gate, publication route, budgets or model allowance.
No actual source qualification or registration activation is part of this implementation.

## Verification

Use temporary stores and fictional transports in OrbStack. Cover direct and parent subjects,
foreign forms, older-index traversal, empty eligible selection, immutable reuse, wrong issuer,
malformed/unsafe/conflicting tables, future dates, wrong document/text/body bindings, omitted or
extra documents, inherited semantic references, partial reconciliation and zero model/structured
calls. Run existing pipeline and operational tests. An actual retained-body replay may demonstrate
historical mechanics only, with exact original hashes/times and no current credit or renewed dates.
No network, onboarding, state/archive write, quota operation or publication occurs in this work.

## Candidate implementation results

The implementation extends `sec_documents` only when `regulatoryIssuer` is explicitly present.
It validates the exact ordered host list `["data.sec.gov", "www.sec.gov"]`, matching ten-digit CIK
fields, the submissions endpoint, source family and supplier relationship. The shared
`SEC_FILING_FORMS` constant supplies both the existing document route and the explicit route.
Legacy document sources keep their existing collection and evidence behavior.

`regulatoryFilingValidation` binds the original source, subject, contract, traversal time,
index-verification time and ordered index observations. Its `selectedDocuments` contains the
sorted exact `{url, filingDate}` inventory derived from the fully verified index. Reconciliation
independently decodes those retained index bodies, repeats index validation and selection, then
requires the exact primary-observation and body-retention lists. It regenerates readable text
from the original primary bodies and compares the exact retained text bytes. Immutable reuse
preserves the original body and fetch time and requires the current complete index anchors.
Index summaries continue to contain `facts: []`.

The collector rejects inherited semantic references before requesting a document. Reconciliation
rejects semantic fields even on incomplete receipts, and the partial-document release path returns
no facts for this source type. UTC-day changes prevent a successful completeness cursor. A declared
candidate produces a gap with `SOURCE_BINDING_UNVERIFIED` and makes zero transport requests.

The dedicated 25-test fictional-transport suite covers direct and parent subjects, foreign forms
and amendments, safe XSL paths, older pages, verified empty selections, immutable reuse, compressed
bodies, unreadable and blocked responses, malformed or conflicting tables, future dates, omitted
and extra documents, changed URL/date/body/text bindings, altered subjects and observation IDs,
inherited semantic caches, partial receipts, UTC-day changes and legacy document compatibility.
Mocks reject model and structured-adapter calls.

OrbStack verification completed on October 23, 2026:

- `python3 -m unittest discover -s ops/ci -p "test_*.py" -q`: 333 passed, zero skipped.
- From `web/`, `python3 -m unittest discover -s tests -p test_pipeline.py -q`: 112 passed, zero skipped.

Only fictional transports and temporary test stores were used by the new suite. No source was
qualified or registered, no real collection or onboarding ran, and no current source check or
semantic fact was credited. These tests establish implementation mechanics. They do not establish
that a declared parent relationship qualifies a segment or that current filing bodies are complete.
No active contract, certified registry, generated data, workflow, coverage denominator or budget
limit changed.
