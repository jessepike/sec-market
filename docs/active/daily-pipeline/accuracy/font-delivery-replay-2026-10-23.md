# Local font delivery verification

The font repair preserves the intended typography while removing the Google runtime dependency.
The exact source CSS retained in the failed trace supplies 39 face declarations and 24 unique
WOFF2 files. The files total 396,100 bytes. Three complete family licenses are retained from
Google/fonts revision `e7db6ca603fd4862010383ff17ffd6cc4ffac1c0`.

The source inventory is `/Users/jessepike/code/projects/sec-market-finish-20261022/web/fonts/source-manifest.json`.
Its SHA-256 is `e808231661ea572ea5740da256ee7fc7f1e5f4ec928011afa63d2377f535d416`.
The accompanying JSON receipt binds each source URL, downloaded byte hash, local file, license,
test result, built-file inventory, public data hash and screenshot. It also records actual
download times. Software-asset downloads were separate from market-source intake.

## Focused results

All execution used the OrbStack dev VM and the existing dependencies.

| Check | Result |
| --- | --- |
| Font inventory, exact bytes, declarations and license integrity | 4 passed |
| Static artifact inclusion and font/license tamper rejection | 1 passed |
| Offline loading at 1440px and 390px, missing/corrupt fonts, restored external CSS | 5 passed |
| Focused lint | 0 errors, 0 warnings |
| Certified application build | Passed |
| Full disabled and synthetic enabled application suites | Each passed 353 data, 112 pipeline and 43 browser tests |
| Hosted web run 40035860583 | Passed 353 data, 112 pipeline and 43 browser tests |
| Hosted runtime run 40035860591 | 414 passed, one pinned-local-archive test skipped; all 415 passed locally |
| Actual immutable preview | Ready; all 24 fonts and three licenses match; desktop/phone renders inspected |

The browser check loads every language subset explicitly. All 24 files return 200 with
`font/woff2`, correct lengths and SHA-256 values. All 39 font faces load; representative family
checks pass. Candidate requests to Google and other outside origins total zero. The three
shipped license files also match. Missing files, corrupt HTTP-200 data and an injected Google
stylesheet fail instead of passing with fallback fonts. Existing navigation timeouts and wait
states were unchanged. The CSP was unchanged as directed.

## Visual evidence

The original build was copied before application edits. Its original Google CSS and font URLs
were fulfilled from the pinned local bytes for the comparison, explicitly labelled
`baseline_replay`. The candidate served the same files from its own origin without replay.
Fresh contexts with service workers blocked used Chromium 151.0.7922.34.

Root, corrections and issue routes each ran at 1440×900 and 390×844. All six comparisons have
zero changed pixels for both first-screen and full-page captures, identical measured layout,
and no horizontal overflow. The baseline and candidate root/issue first-screen images and
corrections full-page images were opened and inspected at both widths. Text wrapping, spacing,
navigation, cards and phone widths match. No visual change from relocating the fonts was found.
This check does not claim a separate visual replay of every drawer interaction.

Images are available to the parent under `/tmp/smp-font-delivery-20261023/` on the host, with
original VM copies under the same path in OrbStack. The JSON receipt records all image hashes.
For example, the font-only root comparison is
`/tmp/smp-font-delivery-20261023/baseline_replay-root-1440-fold.png` against
`/tmp/smp-font-delivery-20261023/candidate-root-1440-fold.png`.

The existing screenshot tool additionally captured current production and local pages at
1440px and 390px, full-page and first-screen, and both sets were opened. Production release
`7bd94ec77e99462c068f254e134235a894585cbb` binds daily snapshot
`53b49106fa9118d603db5e64e37cf03f7f2c6fd1fb797acf18e73f540196c84f` and an October 23 window.
The local builds bind snapshot
`d72a48eb1c4e6be667eba31bc8cff73f1088baea1521f0ad7db845b23345c935` and an October 21 window.
Both local build receipts have `appRevision: null`; this report does not assign an unrecorded
Git revision to them.

Production shows 121/557 source checks, 28 acquisition events and 10 change-log entries. Local
shows 0/557, 29 and 11. The local original event `EV-veeam-2` is dated 2025-10-21: the actual
365-day window includes it at October 21 and excludes it at October 23. These date/data
differences are visible and are not attributed to fonts. Production/local pixels are not
claimed identical. The same-data baseline replay is the isolated evidence for this repair.

All eleven public JSON files other than `app-release.json` match between local builds. The
candidate correction bundle remains disabled with no groups. No synthetic enabled fixture
remains. The font repair and application tests made no market-source requests, model calls,
real allowance/archive mutations or production changes. The separate hosted runtime canary made
one SEC connectivity request, retaining zero collection credit and no archive change.
Hosted validation is retained in
[the actual remote receipt](../receipts/coverage-repair-remote-validation-2026-10-23.json).
