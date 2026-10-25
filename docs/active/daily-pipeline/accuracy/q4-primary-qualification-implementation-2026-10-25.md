# Dormant Q4 single-response qualification implementation

This build changes no visible page and grants no source qualification. The new parser and two-primary proposal operation are dormant. Both actual financial announcement bodies remain uncollected. H and the active 173-byte disabled ad1 plan remain byte-identical.

## Implemented behavior

`web/scripts/pipeline/q4_press_list.py` parses the exact observed Q4 press-list envelope and every row before deduplication. It retains every historical URL, persistent identity, full row hash and original date string. It rejects unknown/error/continuation envelopes, malformed records, duplicate or conflicting IDs/links, unsafe paths, invalid calendar dates and inconsistent ordering. There is no hardcoded 206/323 ceiling or universal TotalRecords requirement.

Unzoned API strings remain unzoned. Date-only scheduling hints, original window boundaries and explicit uncertain boundary items stay separate. Valid future written calendar dates are retained as undetermined work; farther-future dates also carry an unresolved source-date anomaly. They never count as current or quiet. An empty response cannot establish quiet. A valid nonempty older inventory may support a hypothetical later quiet calendar window under the independently bound stream proof.

`web/scripts/pipeline/q4_primary_qualification.py` adds schema-2 operation `bounded_q4_primary_qualification`. Complete original d660 report, ab6 main run identity, raw/canonical plan, source wrappers, both bodies, original HTML and complete controller/pager graph replay before any operation-specific write or reservation. It binds exact financial row 2, including title, date string, PressReleaseId, WorkflowId, full row hash and same-host literal GET URL. No JavaScript runs and no API, year, page or PDF request is generated.

The operation uses the existing acknowledged shared lease, fetch-only escrow, PersistentProbeBudget and Fetcher with 12-second timeout and 2,000,000-byte cap. It permits exactly two logical sample requests with no request bodies. Known raw bytes/status/final URL/MIME/clocks survive classification failures; unavailable fields stay unknown. Charged failures, pre-invocation denial and the final in-flight day/deadline/cancellation guard remain explicit.

A sample must have the exact final URL, accepted HTML MIME, readable primary text, canonical and heading joined to the observed source row. The operation reuses existing primary shape/readability checks. Its narrow metadata reader retains supplied publication values, including malformed and non-string JSON-LD, empty meta/time attributes, nested graph values, explicit offsets and duplicate-key/attribute ambiguity. Explicitly invalid or contradictory metadata holds the sample. Genuine absence may remain unknown. Calendar comparison never rebases an offset or assigns the API a timezone. The generic Page parser and old paths are unchanged.

The report exposes `proposalEvidenceComplete` only when both samples and both complete original streams replay successfully with no completion denial. QualifiedSources, sourceChecksCredited and modelCalls stay zero; qualified, semanticAdmission and coverageCredit stay false; facts stay empty. Minimal `ops/ci/collect.py` routing selects this dormant operation through the existing source-probe caller. No normal discovery mode, origin allowlist or registration is activated.

## Exact dormant plan and source proof

The plan is `/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/q4-primary-qualification-plan-2026-10-25.json`, 4,211 bytes. Raw SHA256 is `3a25e8e262b51fbf6f872c8655b25c9d255cf52b32ca0e9c4afa73d78893fbd4`; canonical SHA256 is `3b7fc7c4de41c68471d4343f103e7e5ee705e5a4a51f760f5387e34a49a660ee`.

The real d660 read/get-only replay preserved 76 consumed byte/size/mtime seals with sockets and LocalStore initialization denied. It reconstructed all 206 JFrog and 323 Rapid7 records, original 3/4 current-window counts and original `2026-10-25T10:19:17.801039Z` window anchor. The exact row-2 WorkflowIds remain `717ce770-88db-49b1-a63a-071d28989c99` and `c4a988fc-6aab-42ee-a2af-4fb57a7ed054`, both with literal `10/14/2026 16:05:00` dates. Fictional next-day sample transport tests preserve that original discovery window.

The frozen baseline remains 867 fetches, 80 calls, 38 documents and two gate attempts, with four fact references and 38 held rows. Its source expiry remains `2026-10-26T15:55:27.307096+00:00`; archived production remains fc8bf098…951e4, sequence 4. Tests use separate temporary writable stores and never reset a real ledger. These are preserved historical counters, not a new allowance.

All six original admissions and group hashes replayed unchanged:

| Group | Review policy SHA256 | Admission SHA256 |
|---|---|---|
| `FC-20261023-checkpoint-sase` | `36bc23722c1131f94ab3c2db1c553505539987aa55738cfa9bb72dfa3871ad6f` | `1bcaa2ca22fcb4c24597fc477c406abddf9ddb20853a4d290c79322bee46afa9` |
| `FC-20261023-optiv` | `4f9e7feb90232a3aafe2cd84265c2e8202c9e009229e7592c5ab87373f64bcf5` | `580099157608b61895574d2b136c93a940109f82d0a33459388a83f46fbc7bf2` |
| `FC-20261023-splunk` | `270b7c7a1f7180b3fef2896b7633a87bf0667b9f4a3c75593fa72b959ecb87f6` | `a42addfcd5043dceffcd259fc8bdac7486b012400fae4b82ce0e5b00968e18af` |
| `FC-20261023-zscaler` | `dc8522069fc87cbf0371e0ea29ec80fbf647c1dd7ce816e02a7fb4a94b35a390` | `f255c470cc078e1d44399f7e2027134b466f23cc5939437d196bef9d7aa04e4b` |
| `FC-20261023-expel` | `d1ea72b754450e603d89092cc38d9fa81d165575af2a36745e5938220fd82087` | `b120ca46429f8e52a09d4fce293c14ddb08319212b2b9a8e0f10b39661deed4c` |
| `XAGE-SOURCE-CLASS-20261023` | `c01560dba484aa5aa5696c8bfe5b44acefc6337ee1cebe0cd96751849e15646a` | `ec322362de6fb9e4e20cea0c9ed825990a01bf0c41d5b32662ab6131914f6c98` |

## Validation and review

- Final new focused tests: 11 parser and 21 operation cases, all passing.
- Final combined new/old-route tests: 126 passing, no skips.
- Final full operational suite on the reviewed code: 909 passing, no skips.
- Full application checks: 377 data tests, 115 pipeline tests, successful release build and 42 browser tests passed. One existing browser fixture was skipped. Lint had zero errors and one pre-existing warning.
- Independent review: PASS with zero open findings, 15 independently written cases, 88 total sealed files including 68 archive inputs, actual source/window/row joins and six-admission replay. The metadata findings were resolved and the final code was rechecked.

The [independent review](/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/q4-primary-qualification-independent-review-2026-10-25.md) is sealed at SHA256 `11ab6f34c2b054c9b6e2783955fba9a07bf64a23512539637c0ce582802c0925`; its JSON is `0906e5d173507af69201887bfee11f1a6efbaceefc21b883de84fc6a755738e7`. Reviewer evidence is attributed separately from the worker's full suites and renders.

Complete logs are retained as deterministic `.log.gz` files with byte-exact decompression, original raw hashes, sizes and line counts in `/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/receipts/q4-primary-qualification-implementation-2026-10-25/verification.json`. The same folder retains the reproducible actual input replay, all consulted input seals and the render comparison. Raw log bytes were not normalized. `git diff --check` passes.

## Visual verification

All four full-page 1440/390 production/local images were saved and viewed by worker and root under `/Users/jessepike/Documents/Codex/2026-10-22/security-market-pulse/renewal-20261024/`, with prefixes `q4-primary-production` and `q4-primary-local`. Current local screenshots are byte/pixel-identical to the prior `q4-initial-data-local` screenshots: zero differing pixels at both widths. Their SHA256 values remain `b044622ff53e695fee8334a95746b932c0df81ff6e26ecb810bfd9228765cdd9` and `7dc872da46a4cf5e2eb765df88e1ae28e34eb70f8d5c38b19835bab09afcd3df`.

Production and local contain different pre-existing data fixtures. Local summary counts are 29/11/19/11/12/42; production counts are 29/11/19/10/11/44, with their corresponding event lists. No equality between production and local data is claimed. Layout remains intact. The worker's port-18820 server is stopped.

## Changed files and remaining action

| Owned code or plan | SHA256 |
|---|---|
| `web/scripts/pipeline/q4_press_list.py` | `f1acf87f53b0b8c5ed9e5b3a181b7832a197f7276a9434a229d29317e7987594` |
| `web/scripts/pipeline/q4_primary_qualification.py` | `cfb164c4c0a19bd890d4522547351bc55a1dc3697d8df5b48af4ead460457235` |
| `ops/ci/test_q4_press_list.py` | `aa4492b0498ebdf0e59e91bb787076a6ed1c786f903fd4767c4d23aeea5256f4` |
| `ops/ci/test_q4_primary_qualification.py` | `7462fd77ea6c35004170acb2af0f670c7be63df313fb3f4956f76f997117b986` |
| `ops/ci/collect.py` | `044a560af19cc1e7a6fec9d87cc8461831dab491f7c42d3dd1d789c9bc3fe6d1` |
| `docs/active/daily-pipeline/accuracy/q4-primary-qualification-plan-2026-10-25.json` | `3a25e8e262b51fbf6f872c8655b25c9d255cf52b32ca0e9c4afa73d78893fbd4` |

H, disabled ad1, correction requests/stamp, source origins, discovery, onboarding, engine, prior Q4 operations, watchdog and workflows were checked byte-identical to HEAD. Root-owned status, backlog, build/activation specifications and independent review files were preserved.

Root's separate operational selection specification is `/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/q4-primary-qualification-operational-activation-spec-2026-10-25.md`. This build has not applied it. Actual sample capture and its authenticated run/artifact/archive audit remain required. A later inventory-only Q4 origin, exact H successor and fresh ordinary 200/304 intake remain separate from this dormant build. No source/model request, dispatch, commit, push, gate or publication was performed by the worker.
