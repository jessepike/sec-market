# Cyera one-primary build specification review

PASS for accepted v0.2, SHA-256 `4356cae1aefc85238030c9688d36ed572a1301ef57137a71aeb0e1fd39acd509`, 17,130 bytes. One concrete draft issue was resolved; no material finding remains.

The original default Fetcher retries HTTP 500/502/503/504. An independent fake-opener 503 check reproduced three attempts with its default and one with `attempt=2`. Accepted v0.2 requires `fetcher.fetch(source, exact_url, previous=None, attempt=2)`, one charged logical fetch and no caller retry. Existing bounded redirect handling stays unchanged; any redirect or changed final URL holds the sample. The scope makes no unconditional one-wire redirect claim.

The exact candidate plan remains `25bf0ff72555188e7a8446b9499f3b8ba56c9327e397f8b70a5ce9deb82d350f`, 5,090 bytes. CSV remains `2de6dd83504c513f12087960e77d0bfc3251c2be5836991cbcc67a1da7a583a4`, 18,265 bytes. Original draft `78eef42356afef9e6374c575c16bd4657d87bd04a84ef9314eabf653dae63ab4` remains unchanged.

Read/get-only checks against authenticated actual J archive `8b3811df40cfdbec9d5ed52252524294566c88e0` reconstructed exact H with the accepted whole-object inverse, validated the complete original seven-target plan and replayed the unchanged strict charged-parent Cyera observation join. Current and historical Cyera source rows are identical. Its real J task identity matches the spec.

All 56 CSV rows were independently rebuilt from the pinned HTML, including each URL, headline, written date, calendar day, CMS collection/item identity and window/seed flags. All five declared seeds occur. The October 16 row is the only current sample; the next row is September 22 and supplies an older boundary. The oldest retained row is March 29, 2022. This supports the declared bounded publisher-list window; it does not claim universal recall or require complete lifetime history. The index window remains anchored to its original October 25 12:41:43.919481 UTC observation, with unknown timezone.

The design fixes the canonical plan, source, sample, original graph and CSV path/hash before operation-specific writes or reservation. A direct closed caller branch avoids all generic candidates. Existing lease, escrow, day, deadline and final-in-flight guards remain required; model, document and gate costs remain zero. Returned raw failures stay attributable without invented status/body/MIME/final URL. Missing primary publication metadata stays unknown, while malformed/conflicting metadata and failed generic shape stay held. No Cyera template exception is assumed.

The required hosted tests keep parser, metadata, guards and single-fetch mechanics portable, with explicit skips confined to full external archive checks. These requirements still need implementation and independent execution review. This is a spec review: no primary was fetched, implementation accepted, source qualified, clock renewed or operational state changed.

The companion JSON and safe receipts retain original/v0.2 pins, read/get proof, all consulted immutable input seals and the retry counterexample. No source/model request or checkout write occurred.
