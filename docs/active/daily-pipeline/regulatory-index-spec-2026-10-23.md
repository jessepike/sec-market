# Neutral SEC filing-index checks

Prepared October 23, 2026 under SEC-072. The archived regulatory-gap audit found that the existing
structured SEC adapter is restricted to the 16 certified suppliers and emits company identity and
events. A product segment's parent filing index must not enter that path. This specification adds
the missing deterministic index-check capability; it activates no source and changes no roster,
required family, denominator, budget, certification tier or public factual record.

## Source contract

Add an explicit `sec_index` kind for `regulatory_filings` only. A future source must retain the
normal supplier/source join, registration state, required flag, allowed hosts and bounded page
policy. A candidate remains an explicit gap and performs no request; only verified registration
may earn an index check. A well-formed candidate must not prevent the other suppliers' tasks from
being planned. It additionally has `regulatoryIssuer` with exactly `cik`, `legalName` and `relationship`.
CIK is a ten-digit string. The legal name is the exact independently qualified SEC submissions
name. Relationship is `direct` for a public supplier or `parent` for a segment. This declaration
requires retained primary issuer/subject relationship evidence at source qualification; adding
fields cannot establish that relationship. Unknown mappings stay incomplete.

The source URL must be the exact HTTPS SEC submissions endpoint for that CIK on `data.sec.gov`,
with no credentials, query or fragment. The allowed hosts are restricted to that host for this
index kind. Validation rejects a different family, unsafe URL, malformed issuer, inappropriate
relationship or a different subject supplier kind. Existing 16-company SEC contracts stay intact.

## Deterministic discovery and verification

Reuse the bounded SEC submissions traversal, including older index files needed for the retained
window. Initial response CIK and legal name must match the explicit issuer. Require the normal
filing table arrays and equal lengths, valid accession/date/primary-document fields, no duplicate
accession with conflicting row values, and valid retained-index boundaries. Secondary index files
cannot substitute for the initial issuer response. A missing, blocked, truncated, conflicting or
wrong-issuer response stays incomplete. Keep existing host/path/page/time and fetch bounds.

After complete discovery, independently validate the exact collected index documents against
the same source contract before accepting the task. Archive its original observations and an
issuer-index validation summary. Emit zero facts and make zero extraction/review model calls.
Do not invoke the certified SEC adapter for this kind. It does not produce a revenue snapshot,
supplier identity change, ownership event, certified claim or whole-site accuracy result.

Reconciliation must independently replay the exact ordered index URL/body observations and compare
the archived summary before accepting this task. Reject nonempty `validatedFacts`, `newFactIds`
or semantic `documentValidations` on an index-only receipt. Do not let a partially validated HTML
path or an old source head carry parent facts into this task. The certified SEC cache continues
to exclude `sec_index`.

The actual archived CrowdStrike and Palo Alto older-index metadata uses enclosing date ranges:
its declared end dates are later than the last rows' dates. Require every row inside the declared
range and the exact declared filing count; equality of observed extrema to enclosing boundaries
would incorrectly reject these complete bodies. Retain declared and observed ranges separately
in the summary. Out-of-range rows, missing pages, count mismatches and conflicting duplicates
still fail. These observations do not supply current source qualification or renewed timestamps.

An index task and a filing-document task retain their separate meanings: an issuer index was
checked versus the eligible primary documents were retained/read. Add foreign-private-issuer
`20-F`, `20-F/A`, `6-K` and `6-K/A` to the existing filing-document selection. Each URL remains
bound to the exact source CIK and filing record; reading it does not admit all its statements.
No foreign source mapping is invented from a familiar name or URL pattern.

## Integration and limits

Schedule this index work with deterministic SEC work, before citations and optional models.
Existing compatible SEC transport sharing may reuse full responses while retaining each source's
original observation provenance. The complete 557-obligation inventory remains unchanged until a
later explicitly qualified registration replaces an existing missing-family task one for one.
This code change does not edit `contracts/market.json` or mark any missing task successful.

For the four SEC kinds on the exact `data.sec.gov` host under the same data-only redirect policy,
the physical GET may be shared across subject suppliers: the fetcher's headers and URL are the
same. Reuse only a successful full HTTP 200 response from this invocation. Keep its original
fetch time and bytes, create distinct source observations, and run each subject's own validation.
Leave ordinary-source supplier isolation intact. A source-specific 304, failed response or broader
redirect policy cannot supply shared evidence. Tests must demonstrate that raw parent-index
reuse cannot emit a parent's certified facts under a segment's identity.

## Verification

Synthetic fixtures cover direct and segment/parent index checks, older pages, no-current-filing
indices with retained history, blocked/missing/truncated/malformed arrays, wrong issuer/name,
duplicate/conflicting accession, unsafe archive paths and zero emitted facts/model calls. Existing
certified supplier behavior and independent SEC checks must remain unchanged. Foreign-form tests
prove eligible document URL/date retention without turning the source check into fact admission.

Use actual archived parent index bytes only where they exist and the qualification evidence
supports the mapping. Label such replay as historical, non-admitting and non-activating. Other
mappings require fresh endpoint/relationship checks after natural allowance renewal. All local
runtime/test work runs in OrbStack; no network, model, archive mutation or live collection occurs
as part of this implementation.
