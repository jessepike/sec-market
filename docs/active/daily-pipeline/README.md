# Daily market pipeline

**Daily publication is disabled. Coverage is incomplete.** The candidate is connected to real
collection receipts; production still uses the four-hour SEC and branch-promotion workflows.
No roster expansion or paid API/infrastructure purchase has been made.

## Inventory and receipts

[`contracts/market.json`](../../../contracts/market.json) is the canonical inventory. The generated
[74-supplier matrix](coverage-matrix.md) and [source-task CSV](source-matrix.csv) show source,
method, daily frequency, registration and actual outcome. Registration is separate from checking.
Missing source families remain required work: 557 tasks, 303 bindings, 254 missing bindings,
28 unverified candidates. Nineteen sitemap registrations were tested against actual XML. Startup
classification remains unclassified until supported explicitly. The roster remains 74 suppliers;
execution has no hard-coded supplier ceiling.

The real October 22 UTC (October 21 Pacific) private subscription run completed **241/557** tasks:
32 SEC APIs, 16 primary filing-document archives and 193 existing citation checks. Two failed,
13 were blocked and 301 were not checked. Twenty-eight claims are held and 8,557 discovered URLs
remain pending. Actual usage was 80 model calls, 39 document reservations and 412 fetches. Four
historical source-backed events are retained in the unpublished snapshot; no supplier field patches.
The model allowance is exhausted for that UTC day. No paid API fallback exists. Citation accessibility
and archived filing text do not establish that every historical claim has been rechecked. Missing
bindings, blocked responses and exhausted budgets stay incomplete. The final archive and snapshot
were independently restored/reproduced; the collector released its lease and correctly exited 2.
[Actual collection and verification receipt](receipts/subscription-collection-2026-10-21.json).

## Execution and trust boundaries

1. The current implementation route is a private GitHub-hosted subscription worker using
   [official managed account-auth persistence](subscription-ci.md). The owner approved dedicated
   credential setup under D-109. Dedicated runner sign-in, refreshed-auth write-back and a fresh-runner real model probe passed;
   Vercel project access also passed. The first corrected bounded collection completed and archived an incomplete result.
   The attempted native cloud scheduler could not bind this repository/environment and saved no
   tasks. Do not repeat that failed handoff. Native durable work remains available if a scheduler
   with enforceable binding becomes available; the Mac/Linux CLI worker remains a fallback.
2. The collector archives exact source bodies, conditional-fetch chains, inventory, attempts,
   candidates/reviews and pending work. Only completed sources advance their cursor. Independently
   validated individual documents can contribute facts while the remaining source stays incomplete.
   Daily call/document/fetch budgets survive restart and policy changes; two-hour collection and
   three-hour worker phase limits bound work. Initial historical backfill still needs a practical
   dated-window policy and measured capacity; the current limits do not clear 8,875 URLs daily.
3. Native Git saves the immutable state to **`refs/archive/market-evidence`** in the existing private
   repository. Normal branch fetches exclude this reference. Hash manifests, ordinary fast-forward
   pushes and pinned fresh restores are implemented and exercised. This avoids a database, new
   service, GitHub runner admin scope or release-upload token. Monitor repository/storage growth;
   one repository remains a shared failure/access boundary, not an independent second provider.
4. A fresh GitHub-hosted `market-release-gate.yml` checks out reviewed main and the exact archive
   commit, verifies every evidence hash, reconciles the full inventory, rebuilds the snapshot and
   replays the SEC producer/verifier from archived source bytes. Actual source-check dates survive
   replay. Unchanged values preserve the prior deployed last-data-change date. It runs the full
   application suite and exports the exact static payload with bound code/data/test receipts.
   Publisher checks GitHub's real run identity and artifact digest; a worker cannot self-assert trust.
5. The Vercel adapter stages only this prebuilt payload, probes exact receipts, journals and archives
   the proposed release before promotion, probes production, and rolls back to the retained prior
   deployment on failure. Initial adoption requires a verified current production rollback baseline
   and closure of competing production paths. No working-tree upload or `vercel --prod` shortcut.
6. A separate GitHub freshness job checks the external worker's archived heartbeat, fixed contract
   denominator, live code/data/deployment receipts and public coverage deadline. It raises/updates
   an owner-assigned GitHub issue and closes on recovery. GitHub account notification preferences
   determine push/email delivery; actual owner delivery is not yet proved. A GitHub outage can also
   prevent this monitor from running; it is independent of the worker, not independent of GitHub.

The worker batches publication after daily collection and reconciliation, with at most two gate/
publication attempts per UTC day for recovery. `publicationCron` currently records target windows,
not an installed second scheduler. macOS runs at 05:17 local time with launchd wake catch-up;
Linux runs at 12:17 UTC with a persistent user timer. A sleeping/offline host cannot promise a fixed
completion time. Both operate within existing account quotas; no extra paid capacity is enabled.
The legacy four-hour cadence stays until a validated, reviewed cutover reconciles all overlapping jobs.

## Hosting decision and local fallback

The owner requests native Codex Cloud scheduling research before selecting a local host.
Current official documentation confirms web schedules and remote cloud coding using shared
subscription allowance. [Research and cloud acceptance tests](cloud-scheduling.md) distinguish
product capability from this account's still-unverified scheduled environment binding. No native
schedule has been created by the available onboarding tools. The native runner and exact prompt
generator are implemented in `ops/cloud/`; see its task handoff and acceptance instructions.
Native queued work has separate collector/reviewer contexts, immutable responses, persisted budget
reservations, replay without duplicate downloads, remote archive compare-and-swap and expiring
leases. These protections do not establish full source coverage or timed scheduling. The following
installer is a fallback.

The temporary cloud checkout is suitable for development, tests and supervised real collection.
It does not become an unattended host when this chat ends. Use a clean, dedicated checkout on an
existing regularly awake Mac/Linux computer. Required programs: Node 22, Python 3.11+, Git,
GitHub CLI, official Codex CLI and `pdftotext` (Poppler). Use that computer's own official sign-ins:
`codex login --device-auth`, `gh auth login`, and `vercel login`. Never copy login files into CI or
an environment snapshot. Vercel project/team configuration comes from inspected management APIs.

Dry-run first (creates a new private configuration directory; does not activate a timer):

```sh
python3 ops/worker/install.py --directory "$HOME/.local/share/securitymarketpulse-dry-run"
```

After the reviewed implementation and operational acceptance gates below, install using a NEW
state directory:

```sh
python3 ops/worker/install.py --install --directory "$HOME/.local/share/securitymarketpulse"
```

The installer restores existing remote evidence/budgets before scheduling, refuses an existing
configuration/schedule, and never transfers credentials. Linux logout persistence uses linger.
The copied launcher follows only fast-forward reviewed main commits; divergence or dirty code is
held. Its initial reviewed setup pin remains until main contains that implementation. Check the
installed timer/launchd status and run its printed `oneShot` command to validate the actual host.
Installation in this cloud was dry-run only; no unattended schedule has been activated.

## Development and recovery

From `web/`: `npm ci`, `npm run test:pipeline`, `npm run test:data`, `npm run pipeline -- check-contracts`.
For separately authorized real collection (state outside checkout):

```sh
python3 web/scripts/pipeline/cli.py run --state /srv/smp-state --subscription-worker
python3 web/scripts/pipeline/cli.py verify --state /srv/smp-state
python3 web/scripts/pipeline/cli.py report --state /srv/smp-state --destination /srv/smp-report
python3 web/scripts/pipeline/cli.py snapshot --state /srv/smp-state --destination /srv/smp-report/dailyMarket.json
```

Degraded collection/reconciliation deliberately exits 2. A verified archive can restore incomplete
coverage faithfully; restore integrity and business coverage are distinct acceptance checks. See
`archive-push --help` and `archive-restore --help` for pinned transport arguments. Keep the exact
archive commit and manifest SHA-256 in an independently retained receipt; verify all files on restore.
The October 20 remote restore at commit `7924a44781fea3d4b038686feefc50d4f30551a7` verified
19,998 files against manifest `875227e57ebfcc8bd1ed51fca131e5a6dd72dc7db59993e56bb30df44b0d5324`.

## Remaining acceptance gates

- Resolve 254 missing source bindings and 28 candidates with actual source-specific completeness
  rules, positive/empty/amended/blocked receipts and practical history windows. Add independent
  reporting search plus primary-document resolution. Link checks alone cannot satisfy this.
- Audit existing displayed claims and complete typed ownership/target roles, financial periods,
  conflicts/retractions and category-specific freshness. Current adapter handles selected company
  metrics/rounds/events; it does not establish every field/category is fresh.
- Measure ongoing delta/backfill/model capacity. Do not hide an impossible daily workload by
  dropping obligations. Subscription limits fail closed and preserve queues. Check existing GitHub
  usage/spending controls before activating new jobs; no increase in paid spend is authorized.
- Commit/test direct preview delivery (no PR), inspect the visible coverage disclosure, and obtain
  review of the concrete major cutover under AGENTS.md. Do not enable publication to bypass gaps.
- Vercel management, prebuilt staging, all 24 staged file hashes and the immutable rollback
  baseline are now verified. Execute production acknowledgement and forced rollback only after
  the concrete major cutover and its other acceptance gates pass.
- Run the real GitHub gate artifact path on reviewed main. Local reconstruction is not a trusted
  GitHub run. Verify issue creation/recovery and actual owner notification delivery.
- Install on the selected persistent host; prove restart, missed schedule, blocked source, no-change,
  amendment, bad release, recovery and multi-day burn-in. Agree an outreach acceptance duration.

Optional Cloudflare handler examples under `ops/archive` and `ops/watchdog/worker.mjs` are not
provisioned, selected default infrastructure or proof of a free tier. No credentials were copied to
CI. GitHub native Git and repository APIs work; admin runner/secrets endpoints do not have the
integration scope, and the design above does not depend on them. Vercel management browser approval
is separate from the already-working Git deployment integration.


## Vercel management verification (October 20)

Official browser authorization succeeded as `jessepike`, owner of `pikeholdings`.
The existing `security-market-pulse` project (`prj_g8sZPXo81XT2Xopa1oLrsbYjTehV`)
is linked to this GitHub repository, production branch main, root directory web. Its production
deployment is READY and matches the public application's exact revision. Current Git production
assignment remains enabled; no project setting or production alias was modified.

An actual prebuilt preview upload succeeded. The first live test found that Vercel CLI validates
an empty `web` directory even when uploading prebuilt output from `.vercel/output`; the adapter
and its regression assertion now accommodate that actual setting without uploading source files.
The cloud proxy initially rejected unique `*.vercel.app` hosts. The saved domain change
subsequently took effect: the exact staged receipt and all 24 static file hashes were fetched and
verified, and the immutable current-production deployment was imported as the rollback baseline.
No production promotion or forced rollback has been executed. No further Vercel sign-in is needed.


Vercel staging/management evidence was subsequently archived at commit
`b22e2d84d447d5a12bd343202aa732c0d057b84e`, manifest SHA-256
`6f03fbc6018e7249f00fd4606a71ff7273c317717fc0011693c38d65e34e31da`, 20,004 files.
This later evidence increment was pushed and hash-manifested; the fresh independent restore proof
above covers its earlier parent, not an unperformed second restore.

## Durable publisher and collection diagnosis (October 22)

The configured private CI credential now passes actual prebuilt staging in
[39797014280](https://github.com/jessepike/sec-market/actions/runs/39797014280). All 25 static files
(24 payload files plus the detached receipt) matched exactly. Production stayed on `54590be`;
no project setting, alias, archive head or model budget changed. The deployed payload remains the
retained smoke test, not a new independently gated daily release.
[Durable staging receipt](receipts/publisher-stage-2026-10-22.json).

An independent restore again verified all 22,468 evidence files and reproduced the 241/557
reconciliation and exact snapshot. The queue has 8,557 source/URL pairs, 7,936 distinct URLs and
28 held claims. Twenty-seven holds concern dates. A narrow publication-time parser correction
recovers metadata on five archived Mimecast documents without accepting their held claims or
spending another model call. [Collection diagnosis](receipts/collection-diagnosis-2026-10-22.json).
The existing application CI now retains full-page production and tested-build screenshots at
1440px and 390px. Major cutover, independent gate, production controls/rollback, complete source
coverage, usage limits and owner notification delivery still require acceptance.
