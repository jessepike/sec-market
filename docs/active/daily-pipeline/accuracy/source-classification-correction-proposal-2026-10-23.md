# Xage syndicated-release classification: pending correction

The missing-source audit found a separate source-classification defect in original evidence
`TR-xage-1`. Its Yahoo Finance page is labelled `INDEPENDENT`, and its limitation calls it a
trade-press relay. The retained page explicitly identifies a paid press release and a GlobeNewswire
dateline. It cannot establish an independent-reporting source binding. This finding concerns the
source's role; it does not independently confirm or refute every number in the release.

## Exact retained evidence

- URL: `https://finance.yahoo.com/news/xage-security-hits-record-growth-120000615.html`.
- Observation: `3659081ca33f1558ed74ea30327c580c2d1664dcf7429e440758089b872499b6`.
- Original retrieval: `2026-10-23T04:14:56.139543Z`.
- Body SHA-256: `01cf60192caf9038e618e16a67aed61087e163a4aff82a724ca406f56c1e2afc`.
- Immutable record: `web/src/data/tracker/originals.json`, evidence ID `TR-xage-1`.

The companion missing-distribution/reporting audit retains exact supporting excerpts and all
source-observation/body bindings. No new source request or observation time is claimed here.

## Recommended correction and remaining work

Use a dated metadata correction to classify the attributed issuer release as `OFFICIAL` and
describe it as a paid GlobeNewswire release republished by Yahoo Finance. Retain Yahoo Finance as
the physical publisher, retain the canonical URL and original record, and preserve the limits on
independent verification. Do not upgrade a company-stated revenue, valuation or funding figure.

The current factual-correction adapter deliberately protects `sourceClass` and `organization`.
It also requires an already classified primary evidence record for its source bindings. Do not
weaken those protections or insert this record into the five current groups. A separate narrowly
specified metadata-classification operation and proper current-policy review are required, with
retained publisher/issuer provenance supporting the new class. Obtain any missing original wire
or issuer proof under the normal naturally renewed allowance; do not invent an origin URL.

This is additional pending accuracy work under SEC-072. It does not change the fixed 177-record
event/supplier-field audit, its five contradicting verdicts, the 273 original evidence objects, any
of the five existing correction requests, or the 121/557 live source result. No correction is
admitted or published by this proposal. Preparing the provenance and repair is agent-owned; no
owner choice or source waiver is currently needed.
