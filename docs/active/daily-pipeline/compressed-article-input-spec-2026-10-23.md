# Bounded decoding of compressed article input

Prepared October 23, 2026 under SEC-072. The retained-body diagnostic found one gzip body among
204 available full citation responses: Barracuda's newsroom shell. The article path currently
feeds compressed bytes through UTF-8 replacement decoding, creating 17,274 misleading characters
with 7,597 replacement characters. The bounded decoded view contains 198 characters. This repair
changes parser/model input and independent replay, without changing raw evidence or source status.

Citation tasks are transport/link checks: their discovery returns no article items and they do
not run semantic extraction. The Barracuda diagnostic manually compares parser views of retained
citation bytes; it does not prove that a live citation task submitted compressed text to a model.
Preserve citation behavior and distinguish this general-extractor repair from citation coverage.

## Input and provenance

Use the existing bounded gzip decoder before article parsing and primary-document text decoding.
Retain raw body references, hashes, observation IDs and original times as provenance. Do not
rewrite archived bytes or set a new retrieval time. Ordinary uncompressed inputs retain their
current text, source scoping, publication rules, cache identity and review behavior.

Use the same deterministic decoded article view for extraction, statement verification, shared
publisher entity exclusion and empty-extraction replay. Correction source reading and primary
filing text reading must also use the bounded view; their current limits, quote checks, identity,
freshness and independent admission requirements stay in force. Decode before detecting PDF.
Malformed/truncated or oversized gzip fails before model calls or successful validation. A decoded
JavaScript newsroom shell remains incomplete discovery; do not infer quiet results or event dates.

## Cache and receipt rules

Only compressed input gets a new cache identity. Preserve the existing scoped/time/generic
extractor distinction within that identity. Old extraction and validation caches remain immutable,
but cannot supply compressed-input work under the repaired parser. Do not blanket-invalidate
ordinary inputs or reset model/document reservations. Record a deterministic compressed-input
descriptor binding the decoded bytes and actual article/extractor input used.

Independent reconciliation must reconstruct that descriptor from the raw body and reject absent,
altered or old compressed-input descriptors. This prevents same-day successful-receipt reuse,
legacy empty reviews or shared-publisher exclusions from bypassing actual re-extraction/review.
Partial-document eligibility must apply the same rule. Any affected previously checked URL in a
bounded source's audit history must become eligible for a real check rather than disappear for
the rest of its audit window. Preserve unrelated URLs, historical facts and pending holds.

The descriptor is mechanical input provenance, never semantic admission. New facts still require
the actual subscription extraction/review and independent statement checks. No source binding,
coverage denominator, certified tier, allowance, workflow or production route changes.

## Verification

Use fictional agents/transports and temporary stores in OrbStack. Cover compressed article
extraction and exact quote/date verification, compressed shared-publisher exclusion and empty
reviews, malformed/truncated/oversized input, cache separation from the old compressed parser,
unchanged ordinary cache identity, source-specific scoping, same-day receipt reuse rejection,
partial-validation rejection and bounded audit rescheduling. Cover correction text/quote reading
and compressed primary document/PDF detection without weakening their limits.

Replay the exact retained Barracuda body with original hashes/times. Its decoded shell must still
require the known data endpoint, with no qualifying or fresh source check. Existing plain correction
source replays and the complete pipeline/operational/application tests must remain valid. No real
source/model request, onboarding, state/archive mutation, quota change or publication occurs here.

## Candidate implementation and verification results

`documents.article_input` supplies the bounded decoded parser view and exact extractor text.
Compressed articles use strict UTF-8. Plain articles keep the existing UTF-8 replacement behavior
in collection and the existing strict decoding in statement verification. Statement verification
continues to use HTML publication metadata only for an HTML content type; compression does not
expand the allowed date evidence for other content types. Correction text retains strict decoding,
whole-document and total-input limits, exact quote checks and original source provenance.

Only gzip inputs receive `compressedInput`. Its deterministic fields are `schemaVersion`,
`inputView`, `extractor`, `sourceUrl`, `rawSha256`, `decodedSha256`, `decodedBytes`, `articleSha256`,
`modelInputSha256` and `modelInputChars`. `inputView` is `bounded-gzip-1`; `extractor` retains the
existing generic, time-publication or scoped parser value of 3, 4 or 5. The compressed cache
identity includes that base and the descriptor hash. Plain identities and validation/extraction
record shapes remain unchanged. Old compressed caches and reservation objects remain intact;
the repaired parser creates separate work under the existing cumulative allowances.

Extraction and validation records carry the descriptor for compressed inputs. Collection verifies
it before cache reuse. Full and partial reconciliation reconstruct it from the exact original body
and reject missing or changed values. Same-day receipt reuse therefore cannot reuse an old
compressed validation. Bounded audit scheduling makes a known compressed URL due when its prior
entry lacks the current body/input descriptor, while preserving ordinary URL stamps. A completed
compressed check records its original body reference and descriptor for subsequent audit rotation.

Primary-document reading decodes before PDF detection. Compressed PDF bodies continue through
the existing PDF extractor and text limit. Compressed non-PDF text is strict UTF-8, including
rejection of a nested gzip payload. Original archived body bytes and fetch times are retained.

OrbStack verification on October 23, 2026 used fictional agents, transports and temporary stores:

- The new `ops/ci/test_compressed_article_input.py` suite passed all 22 tests with zero skips.
- The operational suite passed 353 tests with zero skips before the final two test-only additions.
  The final focused run includes both additional cases: an incomplete compressed newsroom shell
  and rejection of an old compressed empty-review descriptor during partial work.
- The existing web pipeline suite passed 112 tests with zero skips.

The tests cover exact decoded extraction/review input, quote/date verification, HTML/non-HTML
parity, all three existing parser variants, source scoping, shared-publisher exclusion, empty
reviews, old cache separation, missing/altered descriptors, same-day reuse, partial facts, bounded
audit rescheduling, malformed/truncated/oversized gzip, invalid UTF-8, correction source limits and
quotes, and decode-before-PDF detection. A synthetic compressed Barracuda shell remains incomplete
and requires its known data endpoint. The actual frozen Barracuda and eight ordinary correction
source replays are separate retained-body checks coordinated by the parent task.

No source or model request, real archive/state write, source qualification, registration activation,
allowance reset, denominator change, workflow change or publication occurred in this implementation.
Fictional review responses establish mechanics only and do not create an actual admission.

## Integrated retained-byte and application validation

The final OrbStack operational run passed all 355 tests with zero skips, and the monitor run passed
all 12. Disabled and isolated synthetic enabled application runs each passed 321 data, 112 pipeline
and 38 browser checks plus the full production build. Four inspected desktop/phone screenshots
match the preceding local images byte for byte. These are candidate checks, with no admission.

The actual retained Barracuda response decodes to the same bounded shell and still requires its
disclosed data endpoint. Its body hash and original fetch time are unchanged. All eight ordinary
correction source documents and five complete group text views compare exactly with the reader at
revision `e239e784`; all 25,777 frozen archive file sizes and modification times remain unchanged.
The [replay receipt](receipts/compressed-input-replay-2026-10-23.json) and
[validation receipt](receipts/compressed-input-validation-2026-10-23.json) bind exact files and logs.
Citation tasks remain transport-only. This replay supplies no newly completed source check.
