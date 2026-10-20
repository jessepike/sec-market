# Daily market pipeline: implementation and activation

**Not live. Do not enable publication or claim full-site daily coverage.** This branch implements the execution core and a disabled collection workflow. Production still uses the existing SEC refresh and branch promotion system. No supplier, published fact, page or current production schedule was changed.

The owner's requirement is daily collection AND daily reconciliation across the entire current 74-supplier roster, with room for expansion, sourced factual deltas, automatic routine publication and independent failure alerts. The durable completion criterion is a live receipt chain, not a green workflow badge.

## Canonical inventory

[`contracts/market.json`](../../../contracts/market.json) is the single inventory used by planning and checking. [`coverage-matrix.md`](coverage-matrix.md) summarizes all suppliers; [`source-matrix.csv`](source-matrix.csv) lists every task, URL, method, registration, cadence and observed outcome.

- 74 suppliers; eight required information categories each; no fixed supplier ceiling in execution code.
- 557 required source tasks: 287 existing source bindings plus 270 explicit missing-family obligations.
- Bindings: 32 SEC companyfacts/submissions endpoints, 208 existing citation links, 47 discovery candidates. Existing citations are not discovery feeds. A candidate homepage cannot earn coverage.
- Families: official announcements (including results/earnings), distribution services, independent reporting, existing-citation integrity, investor/acquirer announcements where applicable, regulatory indexes and actual filing documents for public companies/segments.
- Startup status is unclassified. Ownership/private status is insufficient to classify a startup. Funding stage is preserved where present. Reviewing these labels adds no suppliers.
- Missing bindings remain failed work in every daily denominator. A verified registration records the intended collector; it does not mean a current check occurred.

The generated matrix initially says `not_checked` for every task. It does not borrow old citation retrieval dates or an unrelated SEC job's success as new daily receipts.

## What runs now in code

| Component | Implemented behavior | Evidence/limit |
|---|---|---|
| Inventory/planning | Policy hash; stable logical run per UTC day; fixed expected task inventory | Expansion to 251 suppliers tested; actual roster stays 74 |
| Collection | TLS/host and redirect checks, private-address rejection, per-host pacing, bounded 5xx retries, ETag/304 retained-body validation | Live source-host access remains unverified here |
| Discovery | RSS, Atom, sitemap indexes, explicitly registered HTML pagination; archived item manifests before extraction | Pagination exhaustion or missing registration cannot mean success; empty feeds require source-specific onboarding |
| Evidence/state | Immutable content-addressed bodies, append-only attempts, fsync/atomic writes, crash-released kernel locks, CAS checkpoints | POSIX local storage, single persistent host; not a distributed object-store integration |
| Deltas/recovery | Changed-byte cache, assertion deduplication, preserved provenance, pending-item manifests; source cursor moves only on completion | Failed partial-task facts are ineligible; resume/duplicate/concurrency cases tested |
| Subscription worker | Existing ChatGPT-authenticated Codex CLI, separate stateless extraction/review calls, explicit document/call limits persisted before use | No paid API fallback; tool features disabled; live CLI inference/isolation still needs validation on selected host |
| Fact validation | Source quotes, dates, entity, number/currency, qualifiers, ARR distinction, event status, exact review/evidence/policy hashes | `source_statement_matched` is source support, not independent proof that a reported claim is objectively true |
| SEC bridge | Archived JSON parsed by existing producer; existing independent verifier re-derives revenue/history, identity and indexed filed events | Does not replace the production 80-claim gate; full filing-document collection is still missing |
| Reconciliation | Every expected task and supplier; current archived source checks; facts and saved semantic reviews rechecked; fresh-process `verify` command | Same-host deterministic verifier; separate production trust boundary is not deployed |
| Release interfaces | Pinned code/data/artifact/test bindings, actual GitHub artifact provenance checks, fixed SEC cohort, preview/live acknowledgements, CAS, rollback | Vercel adapter, snapshot renderer and trusted release-gate workflow NOT implemented; publication disabled |
| Archive transport | Cloudflare R2 Worker example: role-scoped writes, immutable records, digest checks, CAS heads, no delete route | Handler tested with an R2 double; not provisioned, not integration-tested, not connected to Python storage |
| Outside watchdog | Pinned denominator/policy; missing/stale/incomplete receipt alerts; failed-delivery retry, deduplication and recovery | Worker tested with transport doubles; no deployed monitor, public coverage endpoint or notification destination |

[Validation receipts and precise test limits](validation.md).

## Development commands

From `web/`, Node 22 and Python 3.11+ (stdlib only):

```sh
npm ci
npm run test:pipeline
npm run test:data
npm run pipeline -- check-contracts
npm run pipeline -- plan
npm run pipeline -- report --destination ../docs/active/daily-pipeline
```

On a deliberately configured persistent host, state must be outside the checkout, on a persistent POSIX filesystem. The following commands perform real network/model work and deliberately exit 2 for degraded coverage:

```sh
python3 web/scripts/pipeline/cli.py run --state /srv/smp-state --subscription-worker
python3 web/scripts/pipeline/cli.py verify --state /srv/smp-state
python3 web/scripts/pipeline/cli.py status --state /srv/smp-state
python3 web/scripts/pipeline/cli.py report --state /srv/smp-state --destination /srv/smp-report
```

Without `--subscription-worker`, structured SEC and citation checks can run, but new unstructured documents are held. No model request is routed through an API key. Budget exhaustion creates failed receipts and leaves work pending; it never reduces the denominator. Current 40-document/80-call limits are conservative defaults, not a demonstrated daily capacity. Baseline discovery may require an explicitly reviewed bootstrap budget and/or multiple days. Measure capacity before promising freshness.

Back up after stopping collectors, so heads and journals form one consistent snapshot:

```sh
python3 web/scripts/pipeline/cli.py backup --state /srv/smp-state --destination /mnt/independent-backup/smp-unique-run
python3 web/scripts/pipeline/cli.py verify-backup --state /mnt/independent-backup/smp-unique-run --expected-sha256 '<independently-retained manifestSha256>'
```

Use a NEW backup destination per export. Keep its root hash outside both archives. A second directory on the same ephemeral cloud disk is a recovery test, not an independent durable backup. Retention, access control, restore drills and object-store replication are activation work.

## Schedule and trust boundaries

The disabled `.github/workflows/daily-market.yml` proposes daily collection at 12:17 UTC, with reconciliation in the same run. It only runs on reviewed `main`, never PR/fork code, on an isolated Linux runner labelled `smp-subscription`. State survives checkout cleanup. It needs the repository variables `MARKET_PIPELINE_ENABLED=true` and `MARKET_STATE_DIR` only after the activation gates below. Existing four-hour SEC automation stays in place during migration; the new workflow does not publish.

Target publication windows are 00:23 and 16:23 UTC. These are policy settings, **not implemented production jobs**. A later release must pair the last reviewed application revision with an immutable validated snapshot, rather than bundle unrelated application changes. The current branch-based Vercel auto-deploy path must be reconciled with that policy before enabling any replacement publisher. Import and verify today's production deployment as the rollback baseline first.

A model cannot waive a gate. Independent semantic review is a separate call with the original document, not the collector's confidence score. Deterministic reconciliation checks the entire expected inventory. Production should run verification, publication and monitoring with separate credentials/trust boundaries; the current collection process and its fresh-process recheck are not that final isolation.

Cloudflare files under `ops/` are unprovisioned deployment examples. Do not assume their free tiers establish a zero-dollar ceiling. Confirm account limits and billing controls, exact supported R2 conditional-write behavior, lifecycle/retention policy, secret roles and independent availability before selecting/deploying them. No infrastructure was bought and no credentials were created or copied into CI.

## Remaining end-to-end work and acceptance gates

Do not infer readiness from any one row passing.

1. **Host/auth/network:** choose and configure a persistent unattended subscription worker. Verify a real structured-output inference with no shell/apps/infrastructure credentials available to the model. Run capacity/rate-limit tests. This cloud login is recognized but its inference probe received proxy CONNECT 403. The owner confirmed no unattended host/schedule is configured.
2. **Source onboarding:** resolve all 270 missing bindings; validate all 47 discovery candidates against actual feeds/indexes, pagination and retained history. Implement filing-document/PDF support and the distribution/reporting discovery providers needed by the contract. Record positive, empty, late/amended and blocked fixtures for each collector. Classify startups explicitly. Register approved coverage boundaries without growing the supplier roster.
3. **Independent storage:** select an existing-cost-compatible evidence archive and backup destination. Integrate the Python store with it, including role boundaries, conditional writes, crash/interruption behavior and quotas. Restore into a new machine from an independently verified manifest. Exercise actual service concurrency/consistency; local tests cannot prove those semantics.
4. **Site snapshot:** implement mapping from eligible validated facts to every displayed field/event, precedence for conflicting sources, corrections/retractions, meaningful claim-category outcomes, historical backfill and carried-forward/undisclosed/stale labels. Re-run the current 80-claim SEC gate on that exact snapshot. Do not imply each information category was verified merely because one source family was fetched.
5. **Trusted release gate:** implement `market-release-gate.yml` on reviewed `main`, with actual test counts, exact application/snapshot/artifact hashes and a GitHub `daily-market-gate` artifact. The provenance verifier deliberately rejects worker-supplied trust flags. It has no real gate artifact to accept today.
6. **Vercel integration:** configure management access, inspect the real project/production aliases/build settings, implement the immutable artifact adapter, close competing production paths, then prove preview receipt → exact production receipt → forced-failure rollback. No raw working-tree upload or `vercel --prod` shortcut.
7. **Public operational proof:** add a coverage endpoint and reader-visible freshness/coverage labels. Publish only independently reconciled receipts. Deploy the outside watchdog, pin its contract hash and full task/supplier denominator, choose the owner's alert destination and verify actual delivery. Stop the scheduler/worker and prove a missing heartbeat alerts without relying on GitHub running. A green skipped job is never a heartbeat.
8. **Cutover/burn-in:** owner reviews the concrete preview and changed external-service/deploy policy; then disable overlapping legacy triggers, enable daily operation and verify the first full live cycle, no-change cycle, amendment, blocked-source degradation, dead worker, recovery and rollback. Agree a sustained burn-in duration before reader outreach. Do not erase failed runs from that record.

The next implementation stages are source onboarding, site snapshot mapping and the trusted release gate. Full live acceptance of all eight needs the missing host, allowed network, storage/notification configuration and Vercel access. None of the live acceptance gates is marked passed by offline tests.

## Access and setup receipts (2026-10-19 PDT)

- Git fetch and GitHub repository/Actions reads work through platform authentication; permission metadata reports push/admin capability. GitHub Actions secret administration returned 403. Do not request a redundant PAT based on missing environment variable names.
- Production GET works. `/app-release.json` reports application `54590be4d91113a50879a8fb5d180441e7d149f4`, certification `2026-10-18T02:36:44.349Z`. Latest refresh inspected: run `39324337964`, `2026-10-19T21:02:46Z`, certification succeeded and data publication skipped. A no-change refresh does not change the last certified-change timestamp.
- Vercel management token is neither bound in the cloud configuration nor present in the process. Unauthenticated project management access returned 403. Local laptop checkout is not accessible from this cloud task.
- Codex CLI 0.163.0 recognizes ChatGPT login. GitHub-hosted jobs do not inherit this login or pay for model API usage through it. No scheduled subscription host exists yet.
- Cloud setup draft retains tested Node 22 installation and system-Chromium startup/test instructions. Required source/auth/Actions-artifact network destinations were added to the saved draft (59 custom domains total). Draft persistence does not establish runtime propagation or publication; review/save it in environment settings. `VERCEL_TOKEN` remains an optional missing requirement scoped to `api.vercel.com`, entered securely there rather than chat.
