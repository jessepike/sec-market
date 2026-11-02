# Scheduled publication cost review

November 1, 2026. Read-only financial review, with GitHub observations saved at 18:17:26 UTC and a fresh Vercel export downloaded at approximately 18:18:50 UTC and retained by root at 18:22 UTC. This file is the only project file written by this review. No provider setting, reservation, source, workflow or billing authority was changed.

## Finding and recommendation

The existing GitHub-hosted pipeline completed a genuine scheduled collection and its publisher and independent gate on November 1. Another paid Vercel trial is unnecessary to prove that occurrence. **Further paid work must remain stopped:** the fresh combined provider baseline plus retained reservations exceeds the approved cumulative trial stop. Market's partial November 1 rows also already exceed the normal five-cent daily limit, dominated by the actual publication's **$0.105 Turbo build despite using prebuilt artifacts**. The cheapest defensible repair is Basic build capacity on the existing reader project, bounded retained storage, and reduced GitHub usage. Root owns any authorized control correction; this audit changes none. No purchase or trial is needed to establish today's scheduled success. Durability and sustained daily fit remain open.

The normal full-day limit remains **$0.05**. The owner directly approved a **$0.30 cumulative projected trial stop on November 1 within the same existing $1 allowance**, recorded in `/Users/jessepike/.codex/worktrees/market-managed-runtime/sec-market/docs/active/daily-pipeline/vercel-built-in-auth-2026-10-30/trial-stop-approval-2026-11-01.json`. The old October 31 proposal and status called this pending; preserve those dated records. This review does not change the execution guard or claim that the approval has been bound to it. The trial stop and the daily limit are different controls. Neither is a provider hard cap.

Canonical financial inputs for this review are D-115/D-119/D-120/D-121, the retained trial financial contract and raw provider CSV, and actual GitHub job timestamps. There is no product-revenue model involved. Future run timing, traffic, shared credits, storage growth and billing lag are assumptions, identified below.

## Actual GitHub execution

The repository API currently reports `jessepike/sec-market` as private and owned by user `jessepike`. Every executed job below has `ubuntu-latest` and a GitHub Actions runner. The four successful runs used main revision `2aa87f5dd3182bc214f6efee10e709e5114a06ad`.

| Run and job | Actual UTC start to completion | Elapsed seconds | Whole minutes, rounding each job up |
| --- | --- | ---: | ---: |
| [41303798977](https://github.com/jessepike/sec-market/actions/runs/41303798977), schedule-guard | 11:52:20 to 11:52:31 | 11 | 1 |
| Same scheduled run, collect-and-reconcile | 11:52:33 to 12:17:56 | 1,523 | 26 |
| [41305812133](https://github.com/jessepike/sec-market/actions/runs/41305812133), callback-preflight | 12:18:01 to 12:18:16 | 15 | 1 |
| Same publisher run, publish | 12:18:19 to 12:41:45 | 1,406 | 24 |
| [41306711599](https://github.com/jessepike/sec-market/actions/runs/41306711599), gate | 12:29:07 to 12:39:00 | 593 | 10 |
| [41307712849](https://github.com/jessepike/sec-market/actions/runs/41307712849), preflight | 12:41:51 to 12:42:03 | 12 | 1 |
| Total executed jobs | Six jobs | **3,560** | **63** |

The collector event is `schedule`; publisher and rollback preflight are `workflow_run`; the independently invoked gate is `workflow_dispatch`. The publisher waits while the gate also occupies a runner. Add both job durations; the elapsed collection-to-publication clock is not the amount of hosted compute.

The rollback run's `rollback-and-restore` job was **skipped**. Its successful preflight adds one minute to this forecast; this occurrence supplies no new exercised rollback result or rollback compute measurement.

All four `/actions/runs/{id}/timing` responses report Ubuntu `total_ms:0`, including zero job duration values, while their actual job timestamps show the work above. Preserve that returned zero as the endpoint's observation. It is not a settled bill, an account allowance receipt or a safe zero-cost forecast. GitHub now warns that the [workflow-run usage endpoint is closing down](https://docs.github.com/en/rest/actions/workflow-runs#get-workflow-run-usage).

The November 1 UTC run inventory at observation includes nine runs, fourteen executed jobs, **4,462 elapsed job-seconds and 84 whole runner-minutes**. It includes the prior failed publisher `41280871226` (13 minutes), failed gate `41281561059` (2 minutes), two freshness runs `41282463357` and `41334885662` (3 minutes each), and the successful chain above. The fully skipped rollback `41281710761` adds zero. Gross runner value is `84 × $0.006 = $0.504`. This is a partial UTC-day inventory and a derived gross estimate, not reported net spend. Earlier UTC runs can fall in the prior Pacific billing day. Use the provider's actual reporting boundaries when joining costs.

## Recurring forecast and shared-account exposure

Current official [runner pricing](https://docs.github.com/en/billing/reference/actions-runner-pricing) charges standard Linux x64 at $0.006 per minute and rounds each job upward. The measured successful cycle is therefore `63 × $0.006 = $0.378` before included capacity. This is 7.56 times the five-cent daily limit if fully charged, before hosting/storage/traffic.

The freshness workflow runs every six hours. Its two actual November 1 occurrences each executed three sub-minute jobs, so a scenario of four such runs adds twelve whole minutes per day. A future healthy watchdog can take longer; this is an observed-shape forecast rather than an upper bound.

| Scenario, same timing every day | Runner minutes/day | Gross runner value/day | Gross value/30 days |
| --- | ---: | ---: | ---: |
| One successful publication cycle, including rollback preflight | 63 | $0.378 | $11.34 |
| That cycle and four watchdogs at the observed three-minute shape | 75 | $0.450 | $13.50 |

These scenarios omit retries, failed extra publications, development CI, visual checks, source probes, account bootstrap and an exercised rollback. They also omit all Vercel and artifact charges. A 31-day month at 75 minutes/day consumes 2,325 minutes and $13.95 gross value.

Root's fresh browser read at approximately 18:16–18:20 UTC confirms **GitHub Free at $0/month**. The November 1–30 panel reports gross metered usage **$0.51**, included discounts **$0.51**, and billed **$0**. Actions Compute displays **$0.50 used of $12 included**. The rounded display implies approximately $11.50 remaining at that observation, rather than an exact-cent remaining allowance. Top repository usage shows sec-market $0.51 and Threat less than $0.01. The account's Actions budget is **$0 used of $0**, with **Usage blocked** and included-usage alerts On. Root made no setting changes. These are partial-day provider UI observations relayed by root, not an invoice or evidence that all storage is free.

The [GitHub billing reference](https://docs.github.com/en/billing/concepts/product-billing/github-actions) describes included compute as account-wide credit; $12 corresponds to 2,000 standard Linux minutes at this rate. Both the legacy Actions billing API and current user usage API returned HTTP 404 with a missing `user` scope notice; no authorization refresh was attempted. The successful authenticated browser account read supplies plan evidence that those API attempts could not supply.

At the actual $12 included credit, the 30-day normal scenario exceeds that entire credit by $1.50 before other repositories. If paid, that equals $0.05/day averaged over the month, leaving nothing for Vercel; actual overage days could cost much more. Under the observed $0 overage budget, the expected consequence of credit exhaustion is blocked execution. The current Free account therefore cannot support this unmodified forecast throughout the month. A hypothetical $18 credit would leave only $4.50 for other eligible compute, but no plan upgrade is requested or authorized here. Production still needs sufficient shared headroom, a measured reduction in usage or a separately accepted qualified route. The fresh account read explains why hosted jobs resumed this month; it does not establish durable recurring capacity.

Current four-page artifact inventory contains all **328 artifacts totaling 518,973,395 bytes**, all unexpired. Cache usage is **113,666,444 bytes across two caches**, below the separate 10-GiB repository allowance. The newly successful cycle retained **5,229,982 bytes**: two gate artifacts at seven days plus collector/publication receipts at fourteen days. That is approximately 0.0342 GiB of steady-state new-cycle artifacts under the same sizes and retention, before old history and other work. Actual artifact billing uses accrued byte-hours and the account's shared Packages/artifact allowance. Current size alone cannot reconstruct the bill. At 500 MiB, this repository's current artifacts alone leave only **5,314,605 bytes**; other repositories and Packages can consume that remainder. Root's account UI displays storage **0 GB of 0.5 GB**, a coarse rounded usage view that does not erase the inventory or establish byte-hour charges. Do not assume removal or expiration refunds accrued charges. [Storage billing reference](https://docs.github.com/en/billing/concepts/product-billing/github-actions).

## Existing Vercel trial and reported spend

### Fresh November 1 evidence supersedes the old spending forecast

The fresh raw CSV at `/Users/jessepike/code/projects/sec-market-finish-20261022/.ctx/vercel-managed-runtime/evidence-20261101-1822/billing.csv` has SHA-256 `7dfb007a52acb9a41c34916781fcccbf9b1ac5b23af24c1d0a051ea20824022a`. This audit independently re-summed all **31 selected rows out of 379 source rows**, using integer decimal arithmetic. Original download metadata identifies `vercel-costs (25).csv`, original file/download milliseconds **1793557130103**, period start **1793343600000** and end **1793606400000**. The returned range is DST-aware; preserve it rather than imposing three 24-hour UTC days. All observations remain partial/unsettled at export time.

| Fresh selected scope | Exact reported USD |
| --- | ---: |
| Proof project | 0.1403494072361169979014 |
| Market reader project | 0.1180338402691456359496 |
| Combined | **0.2583832475052626338510** |
| Combined, upward-rounded once to picodollars | **0.258383247506** |
| October 30 row-start bucket, 07:00 UTC | 0.1449451104028299979044 |
| October 31 row-start bucket, 07:00 UTC | 0.0046556286466056666466 |
| November 1 row-start bucket, 07:00 UTC | **0.1087825084558269693** |

The October 31 bucket is now a closed provider day, reporting approximately $0.004656 across both projects. It had no successful scheduled publication, does not establish a normal successful operating day, and remains subject to provider lag/settlement. November 1 is incomplete. Its reported subtotal is already **$0.0587825084558269693 above $0.05**, before any additional unreported cost.

All November 1 selected rows belong to Market. The components are **Build CPU Minutes $0.105 / 30 CPU-minutes**, Deployment Storage **$0.0037750084558269693 / 1.1325138618867097 displayed usage GB**, additional CDN CPU **$0.0000075**, and zero-reported CDN requests/transfer. The nonbuild subtotal is **$0.0037825084558269693**. No proof-project new build appears in this export; its cumulative build row remains $0.140/40 CPU-minutes.

The actual source is now bound to published deployment **`dpl_4TYQBozYnNJYvWNyb24mxPqzCQ8n`**, native build **`bld_qjmqgrq90`**. Its eight authenticated events are retained in `/Users/jessepike/.codex/worktrees/market-managed-runtime/sec-market/docs/active/daily-pipeline/receipts/scheduled-2026-11-01/reader-build-events.json`, SHA-256 **`ba533603bb8def41fa917ce5cf1a7875124e2509d3cb5c992111346f2ef83939`**. At 12:39:13.495 UTC the log identifies 30 cores / 60 GB Turbo; at 12:39:14.332 UTC it explicitly uses `.vercel/output` prebuilt artifacts; at 12:39:15.280 UTC it reports deployment completed. Native deployment metadata reports 1.358 seconds from building to ready. Root's complete November 1 inventory contains exactly one new reader deployment and zero new proof deployments. Those sources tie the new charge to the scheduled publication rather than to another synthetic proof.

The charge re-derives as **`30 CPU-minutes × $0.0035 = $0.105`**, consistent with a full minute charged on the observed 30-core machine. Event elapsed time alone could not prove that minimum; the provider's actual 30-CPU-minute row supplies the billed quantity. Prebuilt output avoided installation/compilation but still consumed the paid build class. [Vercel's current build rate](https://vercel.com/changelog/reduced-pricing-for-turbo-build-machines).

A conditional Basic scenario uses two cores at $0.007/minute. For one similarly one-minute charged publication, it would reduce the build component by **$0.098**. Adding the currently reported nonbuild subtotal gives **$0.0107825084558269693** for that partial-day scenario. This is a repair forecast, not a new actual day or upper bound. It still needs actual project-setting readback, an unchanged publication path, enforced build/storage/traffic/retry bounds and later billing. [Basic build pricing](https://vercel.com/changelog/basic-build-machines). The current 75-minute/day GitHub forecast also needs at least 8.334 minutes/day removed merely to fit $12 over 30 days, before all other account work; a cheaper Vercel machine cannot solve that shared capacity issue.

The CSV contains reported usage charges, not an invoice or a complete team-credit funding ledger. Root's GitHub included discounts apply to GitHub, not this Vercel build row. Whether Vercel shared credit offsets this row must be established by Vercel billing evidence; that cannot erase resource consumption or the project's reserved-cost condition.

Applying the same retained trial-scope rules to fresh B gives **`$0.258383247506 + $0.1046 = $0.362983247506`**, exceeding the approved **$0.30** stop by **$0.062983247506**. That formula includes the prospective $0.0112 corrected copy. With that unmade action omitted, existing retained net reservations still give **`B + $0.0934 = $0.351783247506`**, exceeding the stop by **$0.051783247506**. No scope exclusion, new match, refund or reserve release has been approved for the new build. Therefore no paid dispatch is financially admissible from this evidence. Do not silently restrict B to the proof project to make it fit; the accepted cumulative source selection covers both projects.

### Historical source retained for comparison

The retained CSV at `/Users/jessepike/code/projects/sec-market-finish-20261022/.ctx/vercel-managed-runtime/evidence-20261031-1810/billing.csv` has SHA-256 `173e22847ca3c72e0c3e893d8fc88bdd27678435450933b657b990aa71cf4591`. This audit independently selected and summed its 23 matching rows with integer decimal arithmetic. These are historical, partial and unsettled reports, not November 1 full-day costs.

| Exact selected project | Raw reported USD |
| --- | ---: |
| Proof `prj_d2GuxLptHspqQjh2CeT7fW8H8pvd` | 0.1402534028295039979014 |
| Market `prj_g8sZPXo81XT2Xopa1oLrsbYjTehV` | 0.007562948338522914203 |
| Exact sum | **0.1478163511680269121044** |
| Sum rounded upward once to picodollars | **0.147816351169** |

Original download metadata records observed milliseconds `1793469925862`, requested/report interval `1793343600000` through `1793516400000`, and 250 source rows. Selected row starts are October 30 and October 31 at 07:00 UTC. Preserve these original times. A copied file's modification time is not a new provider observation.

The reported proof build row is 40 CPU-minutes and raw $0.13999999999999999, conservatively treated as $0.140. The known set is the deleted failed Turbo build's 30 CPU-minutes plus five terminal Basic builds at two CPU-minutes each: `30 + 5 × 2 = 40`. Failed/deleted work remains counted.

The separately reviewed accounting retains all original reservations, transfer/storage buffers and failures. Its prospective formula is `B + $0.1046`, after only the specific evidenced build/floor overlap rules. With historical B of $0.147816351169, **$0.252416351169** is correct. The approved $0.30 stop formerly left **$0.047583648831** against that historical forecast. The fresh source above supersedes that illustrative headroom and denies further paid work. Outstanding overlap/reservation matches cannot be inferred. No next build was performed by this review.

The original failed Vercel Workflow remains an actual failed-before-step run. Three events, stored bytes and seven-day retained data are chargeable components; Functions and Queues are separate. Its full $0.020 permission reservation remains retained. Five completed proof deployments, their output/function storage, the failed Turbo history, original absent acknowledgement and all uncertainty buffers survive the successful GitHub publication. Success on a different executor releases none of them. [Workflow pricing](https://vercel.com/docs/workflows/pricing).

The one corrected copy's $0.0042 storage reservation is sound at the reviewed 41.5-MB maximum: `0.0415 GB × $0.10/GB-month = $0.00415`, rounded upward. It covers that entire additional output for thirty days, without assuming deduplication or early deletion. It is a retained liability, not today's invoice or the cost of every future daily deployment. Historical Market Deployment Storage rows of $0.004315957573326 and $0.0028712407651969142 belong to separate provider day buckets. Do not sum them into one normal daily baseline.

## What remains necessary for complete cost proof

The normal-cost adapters in `ops/vercel-runtime/cost.mjs` and `ops/vercel-runtime/billing/README.md` preserve a five-cent conservative projection, retained high-water observations, reservations before work, unknown-charge holds, exact project selection and continuing storage. The initial policy proposal remains explicitly unqualified with `livePolicyCreated:false` and `activationAllowed:false`. Local checks establish those rules' implementation only. They do not supply an actual complete day, live evidence access, a qualified resource ceiling or a provider hard cap. The now-successful GitHub jobs did not exercise the proposed Vercel Sandbox runner or its daily resource envelope.

Fresh proof needs these independent receipts, without exporting credentials:

1. Retain root's fresh GitHub account plan, cycle, usage/discount/billed amount and $0 overage-budget receipts. The present account read closes the plan/credit/budget visibility gap. Still obtain current accrued artifact/Packages usage with sufficient precision and a recurring account-wide capacity bound, including other repositories and retries. The deprecated timing zeros cannot replace these.
2. Retain root's fresh Vercel CSV, metadata and exact native build-event attribution above. These close the cumulative observation and build-cause gaps and expose the paid-work stop. Still obtain Vercel team-credit funding evidence and any missing/unreported meters. Keep the actually returned billing period and preserve higher historical liability if a later report is lower. Current November 1 is incomplete; use an end-of-day report after provider lag and a later reconciled report for complete daily conclusions.
3. A complete terminal deployment inventory for both projects with all pages, creation time, status, target, resource class, exact output/function sizes and retention/protection exceptions. Bind today's real production deployment to its publication receipt. Include existing proof storage, any aliases that protect deployments, and every other writer. Count daily retained growth rather than one deployment alone.
4. Actual Workflow run/event/payload/retention inventory, registry/image/snapshot/worker inventory and stopped-state receipts. Empty listings must have complete pagination and observation times. Zero new sandbox use from the GitHub path does not prove all retained proof resources are absent.
5. Reported normal execution, Vercel deployment/function storage, site transfer/requests, analytics, GitHub runners/artifacts and durable archive growth, plus any applicable tax. Keep one-off trial/setup rows separately attributable while including their continuing storage in subsequent days. A shared plan's fixed subscription is disclosed separately from incremental project usage; do not charge it twice or silently call consumed shared credit unlimited.
6. One fully observed operating day plus justified reservations for provider lag, traffic variability, retries and retained growth. Repeat observations are needed for durability. Keep independent missed/stale monitoring and actual alert receipt open; the latest freshness workflow still failed its daily-pipeline job even though the collection/publication chain succeeded.

GitHub currently reports $0 billed after included discounts. Fresh Vercel selected usage already exceeds the five-cent day threshold, while actual eventual November 1 total spend remains unsettled. The retained cumulative trial forecast exceeds $0.30, and the current unmodified recurring compute forecast also does not fit GitHub Free's included capacity. No additional trial, purchase, deployment, paid model call or credential action is needed to produce the remaining read-only attribution receipts.

## Audit provenance

Raw read-only GitHub responses and timestamps are in temporary scratch `/tmp/smp-cost-review-20261101/`. Commands used `/repos/jessepike/sec-market`, `/actions/runs?created=2026-11-01&per_page=100`, each run's `/jobs` and `/timing`, fully paginated `/actions/artifacts`, and `/actions/cache/usage`. Skipped jobs were excluded before timestamp arithmetic. Run inventory SHA-256 is `2ab711a2cb9cdce0ef30077e79eb4729d2fac4d1439a454798e24e33745584d1`; artifact inventory is `c4b74876ca7d6a8b602df536d33c1e4bb09fe3908a69d47fb0fdf8f7e31870e1`; cache receipt is `f0f6321b9e254e8d37ed36c9e68d232d75fb8be78cb94daca4b2378d10c3bed7`. Temporary scratch is not durable project evidence unless retained by the owning session.

The provisional personal-platform README, preferred-stack and RECONCILIATION were read at `ff32b0055293e4fb3bce550bade4652cc2ee1aa3`. Pulse is T2 Important; public results, Internal evidence and Confidential credentials remain separate. The existing GitHub runtime exception is preserved. Memory supplied historical lookup context only; live APIs and retained raw CSV supply the financial claims above.
