# Ordinary stage guard handback

Source commit: `06894f56c6f665d4c7f71224136b28b46682faa0`, based on origin/preview
`2e44342520b1d102b8afa23aafc1618dac29dec3`. Independent review:
`51b9b4f074489c975f9c47f1369f6baef51d0556`. The review found no blocking defect.
Nothing was pushed, deployed, dispatched, purchased or activated. The paid runtime trial stays
stopped. The original dirty checkout and all other branches were preserved.

## Delivered behavior

The existing publisher rejects accepted static output above 20,000,000 bytes, including its
configuration and detached receipt. Its existing artifact validator still rejects Functions,
executable output and external rewrites. Before creation, a native project read must positively
show the pinned project/account, fixed Basic build machine and elastic concurrency off. Missing
or changed fields hold before creation; no provider settings are changed.

Publication remotely saves the consumed attempt and release before creation. Official CLI
`--no-wait` returns a deployment URL without occupying the process through the entire build.
Release/application/artifact metadata is attached. A returned URL is retained as an explicitly
unverified hint. Only a native response matching project, URL, target, native ID and all metadata
permits a creation identity to be saved and remotely checkpointed before readiness polling.
That creation receipt never supplies the tested deployment authority used by crash recovery.

A 90-second local elapsed deadline starts before creation, with a 30-second create timeout and
10-second management-call timeouts. Known owned deployments receive at most one cancellation
request after deadline or an observation/checkpoint failure. Native read-back is attempted even
after a lost cancellation response. Late READY and unknown cancellation outcomes hold. There is
no create retry, guessed cancellation, automatic promotion or reservation refund. Fixed safe
failure codes preserve the distinction in existing publisher alerts, without remote error text.

The source Git configuration enables only `preview` and disables `**`, including slash-containing
branches. Headers, build commands and page source are unchanged. The production publisher still
uploads only prebuilt accepted output from a fresh temporary directory; it never uploads the
checkout or its Git configuration. The ignored-build command remains unchanged as defense in depth.

## Verification on the final source

All execution used OrbStack dev and already installed dependencies. No dependency was installed.

| Check | Result |
| --- | --- |
| Complete operational suite | 1,047 passed, zero skipped, 187.776 seconds |
| New stage guard cases | 15 passed; independently repeated by the reviewer |
| Existing staging cases | 13 passed |
| Publisher cases | Eight passed |
| Full `npm test` | Passed: lint, 384 data, 115 pipeline, gated build and 44 browser cases |
| Browser skip | One existing source-deadline case; no deadline is present in committed Preview inputs |

The complete operational and npm logs are in
`docs/active/daily-pipeline/receipts/normal-stage-cost-guard-2026-11-02/`.
Their SHA-256 values are respectively
`ed12f7c141fcec11b35b01acb21cdd8cf7d7d0f4355bd517492615a46f2cdc03` and
`0f61b9f916159df6475f39e63da2b2bd4db4f83c4424cd969c96f932aabafd11`.
The browser server's process working directory was checked to be this candidate's `web/`.
Host and VM hashes matched for the adapter, publication module, publisher, guard tests and Vercel config.

The already available official Vercel CLI 64.7.0 printed its version on Node 22.22.2 and its help
positively lists `--no-wait`, metadata, prebuilt output and skipped domain assignment. The retained
help is in the receipt folder. Cached package.json SHA-256 is
`5047c4a4a3eafc5cfb3d3782ff25b7ca4209016590304d23ea1635127ba4fe6a`;
CLI entry SHA-256 is `2538efad3c4dd3dc1e8ac189a82f1e095d0bff0ee7bd741158ddff682bcc5282`.
No account operation or login was used to obtain this help.

## Fresh visual review

Fresh captures began at November 2 19:38:04 UTC. The project's screenshot script captured public
production and this local build at 1440 and 390 pixels, both full-page and first-screen. All eight
captures were visually inspected. The adapter repair adds no visible change to the approved
always-visible search. All four local screenshots are byte-for-byte identical to the existing
actual `2e443425` Preview captures in the manager's screenshot directory. The differences from
current production are the already requested search field and the known historical Preview data.
Local rendering is layout evidence, not fresh intake or a live release.

| Capture | SHA-256, identical to the corresponding reviewed Preview capture |
| --- | --- |
| Local full 1440 | `095c7fe008d99ef8459cf163284057c557dbd99db99d085828fb8978bf332d2c` |
| Local full 390 | `2095e1aa95f1137ae1249cfc273550343119efea8f2e974a9229d2262b4d8084` |
| Local first-screen 1440 | `364511d7bea442881159b3177975f0c3955fbd0a891a6673ab6478e7b9bc94b7` |
| Local first-screen 390 | `b549a8b5e23604cbae1db13d0d9811c28f4810069795d191efb700bb8a259f1d` |

Captures and public/local JSON read-backs are retained at
`/Users/jessepike/.codex/worktrees/market-stage-cost-bound-20261102/sec-market/.ctx/normal-stage-cost-guard-2026-11-02/`.
The approved comparison captures are at
`/Users/jessepike/.codex/worktrees/market-managed-runtime/sec-market/.ctx/always-visible-preview-2026-11-02/screenshots/`.
A separate first-load browser check at 390×844 confirmed scrollY zero, body focus, header top zero
and the search input visible at y432.6875–476.6875, with no autofocus.

Fresh production JSON still identifies application `2aa87f5dd3182bc214f6efee10e709e5114a06ad`,
release `ed8ffe5d14d6e5df4e3555ab55df315d8d0f2870228d1865e3c4b2b0ba38250a`,
snapshot `e44a985ce8e8960fc585a79c4ad64dd2cfda0ae67a0d2afa3e192c7846676b86`,
and certifiedAt `2026-11-02T14:11:32.737Z`. No new production is claimed.

## Limits and remaining hosted proof

The 90-second guard is not an enforced billing ceiling. Vercel includes post-build work and
rounds to whole minutes. Provider/network/checkpoint delay, a lost create response, failure of
the first identity lookup, or a worker crash can leave a paid build that cannot safely be canceled.
The remote consumed attempt remains. An untrusted URL hint is archived by normal failure
finalization; loss before that finalization leaves an explicitly unknown creation outcome.
No guaranteed one- or two-minute charge follows from this implementation.

The native account's actual resource fields still need positive read-back. After adoption,
the main push must be observed to create no competing Git build. The genuine publisher must
show scoped identity, checkpoint and readiness timing, exact static bytes, production receipts,
and the actual billable duration. A provider-cancellation failure exercise remains separate.
These local checks do not prove any of those hosted results or a completed five-cent day.

Delivery should combine the existing search/runner candidate and these controls in one future
Preview. All publication writers and scheduled occurrences must fit the Pacific billing day's
remaining allowance, including a UTC schedule that can occur on the previous Pacific day.
Use the normal exact-artifact route only after the separate actual cost review permits it.
