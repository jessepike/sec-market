# SentinelOne filing transport identity

Date: October 25, 2026. Scope: future preview correction support. Main remains frozen at
6d5e87feba4ffbc75e50f35cb564cb8fd91708ca until the current-policy scheduled/public cycle is accepted.

## Problem and evidence

The configured SentinelOne filing citation requests the SEC issuer directory with leading zeros.
The retained SEC response ends at the same filing in the directory without those zeros. The
correction validator requires exact final URL identity and therefore rejects this source. Eight
retained observations share one 49,404-byte body. Its inline XBRL identifies issuer 0001583708,
SENTINELONE, INC., Form 8-K, report date May 28, 2026. This supports one closed transport rule.

## Closed allowance

An optional explicit source attestation may authorize only this exact tuple:

* Supplier: `s1`; source: `s1:citation:TR-s1-3`; evidence: `TR-s1-3`.
* Request and canonical URL: `https://www.sec.gov/Archives/edgar/data/0001583708/000158370826000039/s-20260528.htm`.
* Final URL: `https://www.sec.gov/Archives/edgar/data/1583708/000158370826000039/s-20260528.htm`.
* Configured source canonical digest: `805521d2061b61699a39e64403905b99564731550501130c3038b3c442f89298`.
* Immutable evidence digest: `26c50e6237d1ac662287a3ed05ab51a304773df643e5f5860cc2b5fbc795ab80`.
* Body SHA-256: `e9cc9fc8a899fc7367c173837291a7f8f27d0adad52f81e5adf9dfdf04b04b78`; bytes: 49404.

Use a strict, versioned attestation shape. Python and JavaScript must agree on its validation
and per-group review-policy hash. Bind the exact rule and attestation only to the group that
uses it. Keep all six existing group review-policy hashes and admissions unchanged. Do not
change the global review-rules version. A missing attestation preserves exact final identity.

The runtime must still bind observation ID, exact request, actual final, source, body and actual
observation time. Keep complete body decoding, literal excerpt, size, freshness and independent
admission requirements. The body pin prevents another response from inheriting this exception.
Use genuine retained HTTP 200 and 304 observations with their original clocks and reuse provenance.
No URL normalization, new source registration, source budget charge, admission, operational group
activation, source-policy H change or production promotion is included.

## Acceptance

Test the real retained filing and observation chain read-only. Test Python/JavaScript policy
parity. Reject changed identities, digests, body, request/final reversal and nearby URL spellings
(host, scheme, port, issuer, accession, filename, query, fragment, encoding and traversal), missing
or extra fields, another source using the rule, stale/future evidence and altered observation
joins. Replay the six old groups unchanged. Run the appropriate operational and web checks and
render both widths before pushing preview. Track unsupported Varonis wording and all other
pending source/record work separately. Successful transport validation earns no coverage or
independent admission credit.
