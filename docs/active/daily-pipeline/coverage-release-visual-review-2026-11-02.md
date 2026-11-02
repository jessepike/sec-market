# Combined coverage candidate visual review

The combined candidate adds no visible change to the already reviewed `2e443425` Preview.
Fresh production and local captures were taken on November 2 at approximately 19:58–19:59 UTC
using the existing OrbStack dependencies and unchanged `web/scripts/shot.mjs`. All eight images
were inspected: full-page 1440/390 and first-screen 1440×900/390×844 for both targets. No component,
style rule or data export was removed or changed during this review.

The candidate was the independently reviewed combination at `3bf5365268`, source
`370b802fa17c61a3ed530c4b977e7a0cfa88d6da`. Local rendering used the existing full npm build,
built at `2026-11-02T19:47:49.797Z`; its appRevision is explicitly null. This is local rendering
evidence, not a deployed revision receipt. The local snapshot is the exact prospective K
baseline `d222be9b407e2f2e75b637629c5dd581f37216d0a05ca11e9e92245fe75d5493` with zero intake credit.

## Comparison and findings

All four candidate images are byte-identical to the actual reviewed Preview captures retained
at `/Users/jessepike/.codex/worktrees/market-managed-runtime/sec-market/.ctx/always-visible-preview-2026-11-02/screenshots/`.
All four fresh production images are also byte-identical to their retained production counterparts.
The K/source and Q4/staging integrations therefore add no visible layout or data change to that
reviewed Preview. The exact tracked-byte check covers 141 UI, public and browser-test paths from
`2e44342520b1d102b8afa23aafc1618dac29dec3`; all remain exact. Only the three declared generated
baseline/seal and correction-policy binding files are excluded from this UI comparison. The
complete path/hash list is in `visual-proof.json`.

The visible differences between production and this candidate remain the previously requested
always-visible company search and existing Preview baseline data. Production shows 262/557
source checks, current processing/history counts and a November 2 window. The local prospective
baseline truthfully shows not yet collected, unevaluated processing/history and the historical
October 21 window. It has different historical event counts and rows. Those data differences
explain the remaining content-height changes; they do not represent fresh collection or coverage.
At desktop the full-page heights are 8,488 local and 8,225 production; at phone they are 7,785
local and 7,397 production. Layout, typography, navigation, charts, supplier cards and footer
remain the approved Preview rendering. Both desktop and phone retain a visible search field.

| Candidate capture | SHA-256, exact actual Preview match |
| --- | --- |
| Full 1440 | `095c7fe008d99ef8459cf163284057c557dbd99db99d085828fb8978bf332d2c` |
| Full 390 | `2095e1aa95f1137ae1249cfc273550343119efea8f2e974a9229d2262b4d8084` |
| First-screen 1440 | `364511d7bea442881159b3177975f0c3955fbd0a891a6673ab6478e7b9bc94b7` |
| First-screen 390 | `b549a8b5e23604cbae1db13d0d9811c28f4810069795d191efb700bb8a259f1d` |

Fresh public app/deployment receipts still identify production application
`2aa87f5dd3182bc214f6efee10e709e5114a06ad`, snapshot
`e44a985ce8e8960fc585a79c4ad64dd2cfda0ae67a0d2afa3e192c7846676b86`, certifiedAt
`2026-11-02T14:11:32.737Z`. The local static server correctly has no deployment receipt (404).
Its absent hosted analytics script is expected locally. Neither result was presented as a hosted
failure or production readiness proof. No external citation links were followed.

## Retained evidence and cleanup

The screenshots, all raw public/local read-backs and status/hash index, exact UI Git tree,
141-path hash comparison, and capture pins are committed under
`docs/active/daily-pipeline/receipts/coverage-release-visual-review-2026-11-02/`.
The raw 404 response is retained with its actual status. Public reads covered only this site's
own receipt/data endpoints; no provider settings, source captures or external citations changed.

The dedicated local server was PID 1502323, bound to 127.0.0.1:4371 with this worktree's
`web/dist` directory. Its exact command and working directory were checked before SIGTERM;
its process was confirmed absent afterward. The cleanup receipt is retained. There was no
provider build, branch push, GitHub dispatch, model call or package installation.

The present free operator preparation is complete. This review does not waive a fresh production
comparison if public data or candidate bytes change before the next Preview push. Cost planning,
reviewed release, genuine scheduled collection and exact public publication remain held gates.
