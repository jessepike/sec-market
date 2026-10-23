# Deliver the existing fonts from the tested application

Prepared October 23, 2026. Status: root accepted implementation with the CSP reduction below.
Root authorized font asset vendoring, local delivery, focused tests and before/after evidence.
No release or production approval is implied. The original design task changed only this file.

## Recommendation and observed failure

Self-host the exact WOFF2 files referenced by the stylesheet retained in the failing browser
trace. Preserve its 39 font-face declarations and all existing application typography rules.
Keep the current navigation timeout and wait state. The repair removes a network dependency
from actual readers and from the release gate; it does not merely make the test stop waiting.

The inspected trace is
`web/test-results/hybrid-approved-hybrid-wor-b2ea8-res-and-compact-phone-views-chromium/trace.zip`.
Its raw SHA-256 is `96abc934b491d8d816eb80c004eb27a329d58babcc4ecaa8830a363b1e16d554`
and its size is 140,255 bytes. The 1440px hybrid test times out after 30 seconds at
`page.goto('/')`, waiting for `load`. The trace shows the root HTML returning 200 in 34.822ms,
the Google Fonts stylesheet returning 200 in 1,077.613ms, and five font requests still without
a completed response. This is evidence of an unresolved external font dependency in this run,
not a claim that every past failure has the same cause.

The original stylesheet response is retained inside the trace at
`resources/7784532cba7fc023b6f8ec7e4876d1494eabf16c.css`. Its 15,994 decoded bytes hash to
`d84893df23e971bef0e94622938481eabd90b0c987f2acf948e25010cf733829`.
Use those exact CSS bytes as the source inventory, rather than a newly negotiated Google CSS
response that could select different files or subsets for another user agent.

## Existing typography and exact asset inventory

`web/index.html` contains two Google preconnect links and this stylesheet URL:

```text
https://fonts.googleapis.com/css2?family=Archivo:wght@600;800&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap
```

`web/src/index.css` sets IBM Plex Sans as the body family, Archivo as the display family,
and IBM Plex Mono as the monospace family, with existing system fallbacks. Every retained face
uses normal style and `font-display: swap`. Archivo and Plex Sans also declare 100% stretch.
No italic files are requested. Existing layout CSS also requests weights such as 550, 650 and
700; keep the current face selection and synthesis behavior instead of adding weights or
declaring broader variable ranges during this repair.

| Family and retained version | Declared weights | Subsets | Face rules | Unique files |
| --- | --- | --- | ---: | ---: |
| Archivo v25 | 600, 800 | Vietnamese, Latin extended, Latin | 6 | 3 |
| IBM Plex Mono v20 | 400, 500, 600 | Cyrillic extended, Cyrillic, Vietnamese, Latin extended, Latin | 15 | 15 |
| IBM Plex Sans v23 | 400, 500, 600 | Cyrillic extended, Cyrillic, Greek, Vietnamese, Latin extended, Latin | 18 | 6 |
| Total | | | 39 | 24 |

Several weights share a binary URL. Deduplicate file downloads while preserving each original
face declaration, weight, Unicode range and stretch descriptor. Keeping only the five files
requested by the failing page would silently reduce coverage for other pages and characters.
Keeping all 24 original files is the smallest inventory that preserves the complete existing
stylesheet without a separate font-subsetting or conversion toolchain.

The five unresolved requests in this trace are these exact primary-source URLs:

```text
https://fonts.gstatic.com/s/archivo/v25/k3kPo8UDI-1M0wlSV9XAw6lQkqWY8Q82sLydOxI.woff2
https://fonts.gstatic.com/s/ibmplexsans/v23/zYXzKVElMYYaJe8bpLHnCwDKr932-G7dytD-Dmu1syxeKYY.woff2
https://fonts.gstatic.com/s/ibmplexmono/v20/-F63fjptAgt5VM-kVkqdyU8n1i8q1w.woff2
https://fonts.gstatic.com/s/ibmplexmono/v20/-F6qfjptAgt5VM-kVkqdyU8n3twJwlBFgg.woff2
https://fonts.gstatic.com/s/ibmplexmono/v20/-F6qfjptAgt5VM-kVkqdyU8n3vAOwlBFgg.woff2
```

Extract the complete 24-URL inventory mechanically from the pinned CSS. Do not guess remaining
filenames, refresh the family versions, change Unicode ranges, add `local()` sources, recompress
or rename the internal font families. No font binaries were downloaded during this design; their
byte lengths and SHA-256 values remain implementation evidence to obtain after review.

## Upstream licenses and dependency boundary

Primary upstream license files were read on October 23, 2026:

- [Archivo OFL](https://raw.githubusercontent.com/google/fonts/main/ofl/archivo/OFL.txt).
- [IBM Plex Mono OFL](https://raw.githubusercontent.com/google/fonts/main/ofl/ibmplexmono/OFL.txt).
- [IBM Plex Sans OFL](https://raw.githubusercontent.com/google/fonts/main/ofl/ibmplexsans/OFL.txt).

All three declare SIL Open Font License 1.1. Retain the complete family-specific copyright and
license files alongside the distributed fonts. Archivo names its project authors; the IBM
licenses name IBM and reserve the font name Plex. Distribute the original bytes and preserve
their names and notices. Do not sell font files separately or imply upstream endorsement.
The implementation receipt must pin the downloaded license bytes and the upstream repository
revision used for them; these mutable `main` links are source locations, not immutable pins.

Use the existing Node, Python, Vite and Playwright installations in OrbStack. No package,
subscription, purchase, font conversion, build-time Google fetch or new external service is
needed. Obtain the original binary assets once in the VM over their exact HTTPS URLs after
review, then commit the pinned assets and license copies through the ordinary application
change path. These are software-asset requests, recorded separately from market-source intake.
They must never write market observations, allowance ledgers or source qualification state.

## Proposed implementation files

| Path | Change |
| --- | --- |
| `web/index.html` | Remove the two Google preconnects and external stylesheet link. |
| New `web/src/fonts.css` | Retain the 39 source declarations, changing only each external `src` URL to its exact local asset path. |
| `web/src/index.css` | Import the local font declarations before existing rules. Do not change existing font variables, sizes, weights, spacing, fallbacks or layout. |
| New `web/public/assets/fonts/<sha256>-<original-basename>.woff2` | Vendor 24 unique original files. Content-addressed names keep the current immutable asset-cache policy safe. |
| New `web/public/assets/fonts/<family>-OFL-<sha256>.txt` | Ship all three complete upstream notices and licenses under content-addressed paths. |
| New `web/fonts/google-fonts.css` | Retain the exact trace CSS as source provenance, outside the public runtime asset tree. |
| New `web/fonts/source-manifest.json` | Bind the source CSS, every URL/local-path/byte-hash pair, family/version/subset/weight mappings and license pins. |
| `web/scripts/serve-built.mjs` | Add only `.woff2: font/woff2` to the local built-site MIME map. Preserve its path safety and 404 behavior. |
| New `web/tests/fonts.test.mjs` | Check exact source-face inventory, local mapping, hashes, WOFF2 signatures, licenses and absence of Google runtime links. |
| New `web/tests/e2e/fonts.spec.ts` | Test the built site at 1440px and 390px with outside-network requests denied and explicit font assertions. |
| New `ops/ci/test_font_artifact.py` | Prove WOFF2/license inclusion and tamper rejection through the existing static artifact inventory. |
| New `web/scripts/check-font-delivery.mjs` | Produce the one-time before/after network, font and visual evidence described below from two immutable local builds. |

Root reduced the accepted scope: do not edit `web/vercel.json` or its CSP. Same-origin fonts
already work; the unused Google allowances remain. Existing cache headers stay unchanged.

No dependency or lockfile change is proposed. Existing test navigation calls, timeouts, retries,
market inputs, generated facts, correction admissions, workflows and publication authority stay
as they are. New tests may produce ordinary temporary output and attachments after implementation
review. Implementation proceeds only within the root-accepted file boundary above.

### Artifact and delivery constraints

`web/scripts/pipeline/artifacts.py` inventories every built file under `static/` and binds its
bytes, including arbitrary binary static assets. Its archive boundary permits `config.json`
and `static/` members, rejects unsafe paths and symlinks, and retains its current size/file caps.
It has no font-extension exception to bypass and needs no broader allowlist. Add a focused test
that WOFF2 and license files participate in the existing exact-byte artifact inventory and that
a font-byte mutation fails the existing payload integrity checks.

The local server currently lacks a WOFF2 MIME entry and defaults to `application/octet-stream`.
Add the specific MIME mapping instead of broad extension handling. Verify deployed font MIME
after preview as well. The current Vercel CSP already allows same-origin fonts, and `/assets/`
already receives immutable cache headers. Both preview staging byte verification and the Vercel
adapter verify all `static/` bytes without a font exclusion. Font assets and license copies must
remain inside that existing artifact and verification path; no parallel upload is proposed.

The promotion structure check includes built CSS and can correctly report this change even
when the rendered layout is identical. Its report does not replace the visual evidence.

## Why changing the navigation wait state is insufficient

Changing the hybrid test to `domcontentloaded` could allow its DOM assertions to run while fonts
are still unresolved or while system fallbacks determine line wrapping. That does not repair
the reader dependency. Adding only `document.fonts.ready` afterward would still wait for the
same external service and must additionally reject font errors, since readiness alone is not
proof that the intended face loaded. Playwright exposes separate navigation/load states; font
readiness is a separate browser API. See [Playwright navigation](https://playwright.dev/docs/api/class-page#page-goto)
and [FontFaceSet readiness](https://developer.mozilla.org/en-US/docs/Web/API/FontFaceSet/ready).

Keep the existing 30-second gate and navigation behavior. Do not increase global timeouts, add
automatic retries, abort Google requests in the existing suite to force a fallback success, or
change fonts to system families. Explicit bounded font assertions in the new offline test make
missing files and font/layout failures visible rather than hiding them.

## Exact verification and receipt plan after review

### 1. Pin the asset inputs and preserve a correct baseline

Save the current local build before changing the application, with its failed browser-test
status, complete artifact hash and data-input hashes. Extract the source CSS from the pinned
trace, download its 24 unique
binary URLs and three license files in the VM, and record each original/final URL, actual download
time, byte length and SHA-256. Check successful HTTPS responses, expected font signatures and
license contents. If an exact binary is unavailable, stop and report it; do not silently choose
a newer version or claim an identical layout from a different file.

Serve that unchanged baseline on a private loopback port, separate from the candidate and from
4173. A baseline browser route may fulfill the exact Google CSS and font URLs from these pinned
local bytes. Label this a local replay of the original font delivery. It establishes how the
original application looks with its intended fonts loaded, avoiding a false comparison against
the failure screenshot's unresolved fallback fonts. Deny every other outside request and retain
the original URL-to-byte mapping in the baseline receipt. No baseline HTML or typography rule is
rewritten to resemble the candidate.

### 2. Prove candidate delivery works without outside network

Use fresh browser contexts with service workers blocked and no persistent cache. Allow loopback
requests to the candidate build; record and reject every other network request. Do not use
browser-wide offline mode that also blocks loopback. Before navigating, collect request,
response and request-failure events so a requested-and-aborted Google URL cannot be mistaken
for zero external dependency.

At both 1440×900 and 390×844, keep `page.goto('/')` under the existing timeout. Assert zero
requests to either Google font host, no outside requests, same-origin WOFF2 200 responses with
the exact manifest hashes and correct MIME, and loaded intended font faces. Await font readiness
within the existing test budget and also inspect individual FontFace status and representative
family/weight checks. Exercise all 24 files in a dedicated font-loading check so unrequested
language subsets cannot be missing unnoticed; preserve the page's ordinary on-demand behavior.

Visit the root, corrections history and one existing issue route to cover body, display and
monospace usage. Capture console/font decode errors. Keep unrelated known same-origin analytics
404s explicitly recorded as existing behavior; they do not excuse a missing or wrong font file.
Negative fixtures must show that a missing/corrupt font or a reintroduced external stylesheet
fails the new font check, even if fallback text remains readable.

### 3. Compare pixels and layout at both widths

Run baseline replay and candidate in the same VM/browser version with identical source data,
fixed viewport, matching motion settings and fully loaded intended fonts. Capture full-page and
first-screen screenshots for root and corrections, plus representative source/detail text.
Use disabled screenshot animations and stable UI state. An agent must open and inspect the
paired images; passing a font request check is insufficient visual evidence.

Record pixel-difference results and bounding boxes/line wrapping for the masthead, first change,
reported-growth section, table, corrections row and detail drawer. Retain the existing checks
for no horizontal overflow, above-fold content, chart rows and compact phone height. Expect no
layout change from relocating identical font bytes and declarations. Report any differences
plainly with images and affected measurements, including browser raster differences; do not
describe a fallback-font baseline as unchanged design.

Store temporary images under `/tmp/smp-font-delivery-20261023/` with unambiguous
`baseline-replay-<route>-<1440|390>-<fold|full>.png` and
`candidate-<route>-<1440|390>-<fold|full>.png` names. Retain image hashes and stable paths in the
receipt. Local before/after evidence does not replace the mandatory production/preview visual
review before any later owner-approved promotion.

### 4. Bind tests, artifact and final evidence

After focused checks, the parent task runs disabled and enabled application suites sequentially,
then actual remote CI. No concurrent full suite or second server competes for 4173. The existing
artifact manifest must include every font, license and built CSS byte. Existing semantic and
release gates remain required and unchanged.

Write new `docs/active/daily-pipeline/accuracy/font-delivery-replay-2026-10-23.json` and `.md`
after those checks. The JSON receipt must include:

- Its kind `font_delivery_repair_verification`, actual verification time and application revision.
- The original trace hash/member/CSS hash and before/candidate build and input hashes.
- The complete 24-asset and three-license source/local inventory, hashes, sizes and source pins.
- Browser version, viewports, loopback origins, context isolation and network-denial policy.
- Every candidate font request URL/status/MIME/body hash, zero Google/outside request counts,
  FontFace statuses, readiness results, failures and any known unrelated local diagnostics.
- Screenshot paths/hashes, inspected pairs, pixel differences, layout measurements and the exact
  observed differences or explicit unchanged result.
- Focused/full/remote test commands and their actual results, logs and exact tested artifact hash.
- `semanticAdmission: false`, `marketSourceRequests: 0`, `modelCalls: 0`, `productionChanged: false`
  for this repair verification, with software-asset downloads counted separately.

Do not fill pass results, font hashes, screenshots or remote receipts before the corresponding
checks actually run. No market-source freshness, qualification, quota renewal or admission is
implied by downloading fonts or passing browser checks.

## Implementation verification

The accepted repair is implemented. The 24 exact WOFF2 files total 396,100 bytes; all 39 face
declarations are preserved by changing only their source URLs. All three complete OFL files are
pinned to Google/fonts revision `e7db6ca603fd4862010383ff17ffd6cc4ffac1c0`.
The source manifest SHA-256 is
`e808231661ea572ea5740da256ee7fc7f1e5f4ec928011afa63d2377f535d416`.
The existing CSP, navigation wait states, timeouts and package dependencies were unchanged.

OrbStack verification passed four integrity tests, one exact-byte artifact inclusion/tamper test,
five offline browser tests, focused lint, and the certified build. The browser tests reject a
missing font, corrupt HTTP-200 font, and reintroduced Google stylesheet. The two positive widths
load all 24 files, all 39 faces and the three license files with correct hashes and font MIME.

The unchanged baseline build was saved before application edits. Chromium 151.0.7922.34 rendered
the baseline with the original Google URLs fulfilled from the pinned bytes, and the candidate
with only its own origin allowed. Root, corrections and issue pages at 1440px and 390px produced
six comparisons, with zero changed pixels in both fold and full-page captures and identical
measured layout. Both images were opened for root/issue fold and corrections full-page pairs.
The candidate made zero Google or outside requests, and font decoding reported no errors.
This is a bounded same-data font-delivery comparison; it does not claim every interaction was
visually rechecked. Existing application and browser suites remain the parent's final gate.

The unchanged `web/scripts/shot.mjs` also captured current production and local root pages,
full-page and fold, at both widths. Those images were opened. Production contains a different
daily snapshot and October 23 window; the local baseline and candidate contain the same
October 21 window. Production shows 28 acquisition events and 10 change-log entries; local
shows 29 and 11. Their data text is visibly different and their pixels are not claimed equal.
The receipt retains both release identities and all screenshots. Actual preview/production
review is still required before promotion.

The candidate factual-correction bundle remains the empty disabled baseline. Both local builds
bind daily snapshot `d72a48eb1c4e6be667eba31bc8cff73f1088baea1521f0ad7db845b23345c935`;
all eleven public JSON files other than the build receipt have identical before/after bytes.
No synthetic admission or enabled fixture remains. No market source requests, model calls,
real state writes or production changes were made.

The detailed evidence is in
`docs/active/daily-pipeline/accuracy/font-delivery-replay-2026-10-23.json` and its accompanying
Markdown report. Full application suites and actual remote CI are pending with the parent.

## Remaining limits

The source CSS negotiates modern WOFF2; this
design preserves that existing browser support rather than adding older formats. Baseline and
candidate must use the same browser and intended font bytes to avoid confusing OS rasterization
or a fallback with a design change. Licenses and font files add static payload bytes, but remain
on-demand and subject to the current artifact limits. A future deliberate font update must
replace the pins and visual evidence rather than downloading changes during build or startup.

Root accepted exact self-hosting and the evidence plan while retaining the existing CSP.
Integrated release and preview evidence remain with the parent. No production approval is
requested or implied here.
