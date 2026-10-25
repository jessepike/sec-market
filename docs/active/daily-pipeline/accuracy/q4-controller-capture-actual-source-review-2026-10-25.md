# Actual Q4 controller capture audit

October 25, 2026. Actual diagnostic run [40179255547](https://github.com/jessepike/sec-market/actions/runs/40179255547) passes this audit. It captured all six prescribed scripts with six charged requests. It makes no source qualification, semantic admission, intake, publication or scheduled-execution claim.

## Actual run and retained archive

The private manual main run used exact application revision `99617db0f0ef4c70bb6f0b563cac9a40c50e0385`, policy H `8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db`, and the reviewed six-request raw plan `007f1f940d48727da9a921d0c1138f27e5249870dd5ed6aaa3da3e844582ba91`. Its canonical plan hash is `e787c1c94704dd3a21ff4e71ffaf35dac1ac18f9d3ea2b0a7e16690da3561600`. GitHub records creation at `2026-10-25T09:06:04Z`, terminal success updated at `09:10:40Z`, event workflow_dispatch and attempt 1. The ordinary collection, account installation and owner-alert steps were skipped for this diagnostic profile.

Artifact 12593371749, `source-probe-receipt`, is 2,241 bytes with SHA-256 `7cb5b87b5c91fbc7507076ff527ffc9a32fa9ae94e1bacf3d2ba7c0db2807972`. Its GitHub run, branch and revision match the actual run. The downloaded ZIP matches its GitHub digest and contains only `smp-collection-receipt.json`.

The receipt acknowledges archive commit `9634b916c15b18f38605a168f7642de764670aab`. The audit pins this commit, independent of any later moving archive head. Its manifest is 9,326,098 bytes, SHA-256 `600e58564c989206856ba48795bf4ce9f6fbbf73a604e806594e95327b53203a`, and Git blob `f53c21d0d576a8ebba3f57da5173d2b7ef8dec69`. All **45,307 entries** pass exact length, SHA-256 and content-address checks. Extraction rejects links and unsafe paths. The full read-only VM extraction is `/var/tmp/smp-q4-controller-actual-20261025/extracted`; no LocalStore was initialized on it.

The full retained tarball is `/var/tmp/smp-q4-controller-actual-20261025/acknowledged-archive.tar.gz`, 312,332,485 bytes with SHA-256 `278c1013b6e78c4af518e5ce81c511096fe8587a4e01145a18757dd711387392`. The archived diagnostic result exactly equals the artifact result after removing its subsequent archive acknowledgement. The archived raw plan, original charged parent proofs, six observation wrappers, raw observations, body references and original clocks all replay through the unchanged real verifier with sockets and LocalStore initialization denied.

## Actual requests

Every request returned HTTP 200 with exact unchanged final URL and MIME `application/javascript`. No transport error or denial was recorded. The two literal paths are `/js/module/widgets/dist/latest/evergreen.q4Api.min.js` and `/js/module/widgets/dist/latest/evergreen.q4Pager.min.js`; the complete six URLs and all request/check/response clocks are retained in the companion JSON.

| Source and script | Charge | Original fetchedAt on October 25, UTC | Body bytes |
|---|---|---|---|
| JFrog, API, investors.jfrog.com. | 445. | `09:09:54.344075Z`. | 25,534. |
| JFrog, pager, investors.jfrog.com. | 446. | `09:09:54.592902Z`. | 7,642. |
| Rapid7, API, investors.rapid7.com. | 447. | `09:09:54.775895Z`. | 25,534. |
| Rapid7, pager, investors.rapid7.com. | 448. | `09:09:55.055776Z`. | 7,642. |
| Rubrik, API, ir.rubrik.com. | 449. | `09:09:55.277144Z`. | 25,534. |
| Rubrik, pager, ir.rubrik.com. | 450. | `09:09:55.519322Z`. | 7,642. |

The API body is identical across the three hosts: SHA-256 `2ce36889709b0c9ff34e2b657d5abe0600009604d7e5407d41198f9a9c72d5e7`. The pager body is also identical across the hosts: SHA-256 `4e9d26dabe182ce0694a7e892892b5dc24a502cf14ee1b251542c9b920796a79`. Separate authentic observations and clocks remain for each actual request. The diagnostic starts at `09:09:32.159902Z` and completes at `09:09:55.789354Z`. Captured JavaScript is retained for reading as data; this audit does not execute it or infer a complete newsroom from it.

## Charges, lease and preservation

The authenticated parent chain is baseline b08469e0, bootstrap 13db59f9, fetch escrow d23f8926, then final 9634b916. The escrow commit at `09:09:52Z` retains the fetch ceiling before the first request at `09:09:54.127347Z`. The archived bootstrap, budget_reserved and finish checkpoints match the source-probe profile. The shared lease is released at `09:09:55.902526Z`.

| Counter | Before | Escrow ceiling | Final |
|---|---|---|---|
| Fetches. | 444. | 5,500. | 450. |
| Model calls. | 72. | 72. | 72. |
| Documents. | 33. | 33. | 33. |
| Gate attempts. | 2. | Unchanged. | 2. |

All six reservations map exactly to charges 445 through 450. There is no refund, extra model/document reservation or new gate attempt. The current allowance remains 5,500 fetches, 80 model calls, 40 documents and two daily gate attempts.

Against authenticated baseline b08469e082606def8ef37d9bfeb1cc9609f48176 and its 45,287-entry manifest, every one of 36,680 immutable entries and 8,605 normal head entries remains exact. No baseline entry is missing. Only two existing entries change: the daily fetch-budget head and shared lease head. Twenty new entries retain the diagnostic plan, observations, two unique bodies, escrow and checkpoints. Of the top-level state trees, only ci, heads and objects change; the other 35 trees remain exact.

All six old correction admissions replay against the unchanged six per-group policy hashes. The four fact-provenance references, their bodies, the 37 queue entries, old dates and unresolved holds remain exact. Normal collection/publication heads, old immutable source evidence, factual corrections, gate state and accepted release fc8bf098 sequence 4 remain unchanged. New scripts create no new fact, registration, source check, coverage or qualification credit and do not advance the old newsroom freshness clocks.

The runner guard step reports 858 tests with 19 retained-fixture skips, so 839 executed. This differs from the separately retained local selection checks: 55 focused, 858 operational and 36 watchdog tests, all with zero skips. The actual guard output is retained as deterministic gzip with a verified byte-exact round trip, raw SHA-256 `1cfb03f079ef2be23eb0d0eaaffa0ef8760cec50b07d5f93eecada90ff851fe0`, 234,072 bytes and 1,503 lines. The gzip SHA-256 is `f78062bd7aa7d1a17f89777184e74fc9580877d765c6182297b1dce54bd8ae05`.

## Restoration and remaining proof

At root's direction, the local operational diagnostic contract was restored mechanically from original main bytes to the exact disabled 173-byte plan, raw SHA-256 `ad1c5cc234fe4fa69cbceb5370ac74825a37dc80b08528ca908d14b1352e53b4`. Root owns its reviewed commit, preview checks and main restoration; this audit does not claim that remote restoration has occurred. The actual archived 007f plan continues to govern replay of this completed run.

I would retain this diagnostic as authentic controller evidence and keep all three candidate qualifications open until literal endpoint, record, date-window, pagination/terminal and primary-sample proof passes separately. Independent controller inspection uses the frozen extracted bytes as data. Genuine H scheduled collection and automatic publication remain separate open receipts. This verifier makes no primary-source or model requests, archive writes, dispatch, promotion, commit or push.

The complete audit JSON is `/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/q4-controller-capture-actual-source-review-2026-10-25.json`. Its receipts, original input seals, exact request references and test-log metadata are under `/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/receipts/q4-controller-capture-actual-2026-10-25/`.
