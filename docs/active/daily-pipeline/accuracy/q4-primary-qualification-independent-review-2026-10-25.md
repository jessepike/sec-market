# Q4 primary qualification implementation review

October 25, 2026. Verdict: **PASS**, with no open findings after two passes. This is an independent offline implementation review. It does not establish that either new primary request has run or that a source is operationally qualified.

The governing build specification is `/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/q4-single-response-qualification-build-spec-2026-10-25.md`. The separate activation specification is `/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/q4-primary-qualification-operational-activation-spec-2026-10-25.md`. Both current file hashes are retained in the companion JSON. I recommend proceeding to the prescribed exact selection review after the implementation worker's final checks pass.

## Proof and request boundaries

`q4_primary_qualification.py:32` replays the complete actual initial-data report through the unchanged initial-data verifier before returning targets. It binds actual run 40184027106, its main revision, original raw/canonical plan, archive and manifest attestation, original controller and HTML graph, source definitions, source-specific wrappers, raw observations, bodies, and original response clocks. The parser recomputes every record and the original window before binding the approved financial row 2 by its complete row hash, persistent identity, title, literal date and resolved URL.

The unpatched actual replay passes against acknowledged d6606a4f5dd1e1afc5f16dea6d91bc422347f8aa and manifest 40873bfd2dca9836b58ac325a3afb32919fb463b2082752cb72fc785a2d7239d. It retains all 206 JFrog and 323 Rapid7 URLs and the original three/four calendar-window records. The row hashes match the independently prepared bindings: JFrog b9a2d2e2000c8d5d8794b49e6b3d0552055ab4051c96c89fe20a027709297949 and Rapid7 68f92eeb69a75ed608462310b72798f7efa0c8f9a1118d28712b3cce9716d8f5. No JavaScript executes during replay.

`validate_plan:109` requires the exact canonical plan. `execute:286` rereads its current raw bytes and repeats full proof validation before operation writes or reservations. The caller at `/Users/jessepike/code/projects/sec-market-finish-20261022/ops/ci/collect.py:256` selects the dedicated route before creating its bound budget and acknowledged escrow. The selected transport keeps the existing Fetcher, GET behavior, timeout of 12 seconds, 2,000,000-byte cap and diagnostic retention. The new operation has two logical reservations and no discovery fanout. Existing transport retry behavior remains applicable; two reservations do not assert exactly two physical wire attempts.

The dormant plan is 4,211 bytes, raw SHA-256 3a25e8e262b51fbf6f872c8655b25c9d255cf52b32ca0e9c4afa73d78893fbd4, canonical SHA-256 3b7fc7c4de41c68471d4343f103e7e5ee705e5a4a51f760f5387e34a49a660ee. The active contract still has exact disabled ad1 bytes. This review verifies the dormant selection candidate and the activation specification; it does not claim the later operational copy or remote selection occurred.

## Parsing, primary shape and failure handling

`q4_press_list.py:28` validates the exact nonempty envelope and every row before producing an inventory. Duplicate JSON keys, malformed rows, conflicting identities, unsafe URLs, impossible dates and inconsistent ordering reject. Valid additional historical records remain retained; the parser has no hard-coded 206/323 count ceiling. The complete returned array and fixed client graph support the declared stream without inventing a TotalRecords field or a server page/year request.

Dates remain literal strings plus calendar-day scheduling hints with timezone unknown. Exact cutoff/as-of days are flagged. Later written days remain undetermined; farther-future days also carry an explicit source-date anomaly. They cannot establish a quiet window. A later quiet calendar window requires a valid nonempty older inventory. This contract does not establish exact rolling UTC publication instants. The two actual arrays contain no boundary rows, and the original proof-bound operation does not rebase their window when a later primary sample is checked.

`_primary_response:188` requires actual HTTP 200, exact requested/final identity, no redirect evidence, valid HTML MIME, authentic raw bytes, a readable first-party document, exact canonical and a heading joined to the selected source-row title. The primary-only publication reader at line 122 preserves supplied date values and offsets. It compares their written calendar date to October 14 without assigning the API a timezone. Genuine metadata absence remains unknown and permitted. Supplied invalid or conflicting metadata holds the sample.

Known response bytes remain available on held samples. Unknown transport fields remain unknown after unobserved failures. `_results:221`, `_seal:265` and `verify_report:334` replay authentic observations, attempts, ordered charges, UTC-day/deadline completion and denial accounting. Pre-invocation denial retains its charge and clears the request marker. Partial success cannot complete the two-source proposal. Final in-flight expiry or cancellation prevents completion. All qualification/check/model/fact/semantic/coverage credit remains zero.

## Findings resolved during review

1. Explicit invalid JSON-LD publication values were silently dropped by the reused generic Page reader, allowing proposal completion with metadata marked unknown. The new primary-only reader now holds empty, non-string, malformed and conflicting supplied values and duplicate JSON keys. It leaves generic Page behavior unchanged.
2. Whitespace surrounding the JSON-LD MIME type could hide a conflicting supplied date. The reader now trims that MIME spelling and rejects ambiguous self-closing script/inert contexts and relevant duplicate HTML attributes. Independent regressions exercise these cases.

The first pass inspected the proof, parser, caller and failure paths and reproduced both findings in synthetic transport. The second pass inspected the fixes and reran the independent adversarial cases on the final sealed code. No code, plan, source, workflow or archive changes were made by this reviewer.

## Independent evidence and limits

Fifteen independently written focused tests passed with zero skips. They cover actual graph/row joins, original inventory/window retention, malformed duplicate rows, future-date uncertainty, genuine missing metadata, preserved explicit offsets, invalid/empty/non-string and conflicting publication metadata, duplicate JSON keys, MIME whitespace, self-closing contexts, partial samples, response failures and report tampering. The duplicate HTML-attribute guard was inspected in the final code. All six original admission and review-policy hashes replay unchanged at the explicit historical test clock. That replay creates no new admission or transport freshness.

The read/get-only actual adapter ran with sockets and frozen-archive LocalStore construction denied. All 68 consumed archived inputs and 88 total consulted file seals retained bytes, sizes and nanosecond mtimes. The companion JSON contains the individual seals and six admission references. The full archive was previously authenticated by the actual-capture auditor; this review independently validates the consumed immutable proof graph rather than claiming another full 48,045-entry audit.

Final reviewed SHA-256 values:

| File | SHA-256 |
|---|---|
| `web/scripts/pipeline/q4_press_list.py` | f1acf87f53b0b8c5ed9e5b3a181b7832a197f7276a9434a229d29317e7987594 |
| `web/scripts/pipeline/q4_primary_qualification.py` | cfb164c4c0a19bd890d4522547351bc55a1dc3697d8df5b48af4ead460457235 |
| `ops/ci/collect.py` | 044a560af19cc1e7a6fec9d87cc8461831dab491f7c42d3dd1d789c9bc3fe6d1 |
| `ops/ci/test_q4_press_list.py` | aa4492b0498ebdf0e59e91bb787076a6ed1c786f903fd4767c4d23aeea5256f4 |
| `ops/ci/test_q4_primary_qualification.py` | 7462fd77ea6c35004170acb2af0f670c7be63df313fb3f4956f76f997117b986 |

Reproducible scripts, exact gzip log and raw/gzip hashes are under `/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/receipts/q4-primary-qualification-independent-review-2026-10-25/`. The raw independent log is 1,508 bytes, SHA-256 8b0c6bdd18345f98514396fc62f0351f29b1bed7b4e5f70a3cacc735425e3b02. Its deterministic gzip roundtrip is exact. The implementation worker separately owns the final full operational/application checks and both render comparisons; those remain required before promotion.

No source requests, model calls, leases, budget changes, dispatches, archive writes, source registrations, H changes or publication occurred in this review. Actual samples, a separately reviewed inventory-only origin and exact H successor, fresh normal intake and public publication remain later evidence.
