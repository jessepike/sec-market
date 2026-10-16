---
id: SEC-MARKET-AUTO-002
version: 0.2
state: council reviewed; owner decisions D-88 to D-95 logged 2026-10-15; open items listed below
created: 2026-10-15
revised: 2026-10-15
author: Claude (claude.ai session with the owner)
reviews: council review 2026-10-15, three independent reviewers (Opus 5.5 durability/ops, Fable 5.1 governance/credibility, Sonnet 5.5 CI security). All three: approve with changes.
supersedes: v0.1 (same file, git history)
---

# Hosted automation, filed events and portfolio tie-in

## Owner goals (stated 2026-10-15)

- Runs with no laptop and no recurring human step. Low friction, low overhead.
- No written weekly point of view. Credibility comes from accuracy and a published method.
- Neutral, rule-based facts. No "vendor risk" framing (the owner works in security sales at a reseller that sells some tracked vendors).
- securitymarketpulse.com stays the product domain. jessepike.dev is the author hub and email home.
- One property in a portfolio (jessepike.dev and future sites) building the owner's profile as an AI CISO advisor and entrepreneur.
- A durable production site.

## What the council found that v0.1 got wrong

All verified against the repo on 2026-10-15 unless marked.

1. **Nothing can pass the D-85 gate today, newsrooms or not.** `web/src/data/generated/refreshVerification.json` has 0 verified claims. The proof adapter that would generate substantive proofs does not exist (`docs/active/complete-refresh-gate-2026-10-14.md`). The 16 SEC filers also carry 128 failed fields (identity, headline metric, ownership, events), because current discovery requires IR pages that return 403. v0.1's claim that the SEC tier "can reach 100% today" was wrong.
2. **Option A does not work with current code.** `refresh-publication-gate.mjs` `evaluateRefresh` requires every supplier in `contract.supplierIds` across every group. It needs a v2 contract, a proof adapter, EDGAR submissions accepted as discovery, and a tier split in the release build.
3. **8-K coverage is narrower than stated.** `filing-events.ts` maps Items 5.02, 2.01, 1.03, 2.05 and 3.01. Items 1.01 and 2.03, and DEFM14A for announced acquisitions, need new code.
4. **The drafted workflow is stale and unsafe.** `edgar-refresh.yml.txt` runs only `refresh:edgar`, then `auto-publish.sh`, which can push `main`, all in one job holding `contents: write` while running `npm ci` and third-party code.
5. **"No human step" and "production moves only by promotion" contradict each other.** The owner has to pick one.
6. **`freshness.yml` watches the weekly issue index.** Once the weekly issue is retired, it alerts forever or checks nothing useful. It also runs on the same platform as the job it watches.
7. **Repo bloat.** `refreshCoverage.json` is 857 KB. Committed nightly, that is roughly 300 MB of history a year.
8. **Silent staleness.** `edgar-refresh.ts` keeps the previous record when a filer fails, and exits 0 unless more than 50% fail. `selectRevenueFacts` takes the first revenue concept with any USD fact, so a tag change can freeze a filer's latest quarter without an error (reviewer finding; not independently re-verified).
9. **Vercel builds use `npm install`** (`web/vercel.json`), not `npm ci`, so builds can drift without a commit.

## Owner decisions (2026-10-15)

Logged in decisions.md as D-88 to D-95: 1 auto-promote data (D-88), 2 Option A (D-89), 3 byline (D-90, name vs alias open), 4 filed events (D-91), 5 email as one complete workstream (D-92), 6 retire weekly issue (D-93), 8 backlog SEC-059 (D-94), 9 defer (D-95). Open: 7 branch protection (owner prefers no cost), update cadence, brand identity.

## Decisions as presented to the owner

| # | Decision | Council recommendation |
|---|---|---|
| 1 | **Production promotion.** Auto-promote certified, data-only commits to `main` after gates and a soak, or keep manual promotion (a recurring human step) | Auto-promote, but only from a separate promotion job: allowlisted diff (data files only), per-value sanity bounds, preview deploy Ready, 24 hour soak on `preview`. Never from the job that ran dependencies |
| 2 | **Certified scope (D-85).** Option A: certified tier is the SEC filers, set by source class before results are known. Option B: per-field dating, which reverses D-85 | Option A. Honest only if scope is fixed by source class in advance, logged, and stated on the Method page. Certified count derived from the filer list, never hand-set |
| 3 | **Attribution (D-80).** (a) Named byline with an interests statement on the Method page, linking to jessepike.dev. (b) Neutral footer link. (c) Site stays anonymous, one-way link from jessepike.dev | (a), after checking ePlus outside-activity policy. If not cleared, (c). Not (b): hidden-but-findable reads worse than either |
| 4 | **Machine-published facts (constraints.md, D-76).** Replace "signals" with "filed events": dated, uniform, rule-listed facts, no thresholds tuned after seeing results | Accept. Drop the growth-slowdown rule. List officer changes individually instead of counting them. Show debt events with amount and purpose. Add late-filing notices (NT 10-K/10-Q) |
| 5 | **Email capture and digest (constraints.md says not yet authorized)** | Authorize the minimum version: double opt-in, plain HTML form post (no third-party script), privacy line naming the processor, digest contains only verified changes, no send when the gate fails. List lives in the jessepike.dev account |
| 6 | **Retire the weekly signed issue (D-73, D-75)** | Retire; keep the archive |
| 7 | **Branch protection.** Upgrade to GitHub Pro (about $4/month) for rulesets on `main`, or record that the token is the only barrier | Owner's call. Reviewers split on value; at minimum record the choice |
| 8 | **Optional: quarterly signed note per domain** | Optional. Facts alone prove method, not judgment. A dated quarterly note per domain, auto-marked "awaiting review" when facts under it change, is the smallest addition that shows judgment |
| 9 | **Phase 2 AI extraction for private companies** | Defer. Prompt injection from press releases into published data is a real risk, and it conflicts with D-83 and the no-human-step goal |

## Revised plan

### Phase 0: make the gate passable (before any schedule)

1. New contract `smp-refresh-v2`: the SEC filers only; groups limited to revenue (latest, prior), identity from EDGAR submissions, and SEC-filed events. Headline metric (ARR) and ownership leave the certified tier.
2. Proof adapter that writes `structured-validation` proofs with SEC response hashes.
3. EDGAR submissions accepted as discovery for the certified tier.
4. Staleness checks: pick the revenue concept with the newest period end; fail a filer if its latest quarter ended more than about 150 days ago; watch for Form 25 or 15 and name changes. A single filer failure blocks that filer and opens an issue.
5. Tier split in the release build: second-tier (non-SEC) records render with their own last-verified dates, never under the certified date.
6. Extend `filing-events.ts`: Items 1.01, 2.03, NT 10-K/10-Q, DEFM14A.

### Phase 1: hosted nightly run

1. Workflow on GitHub Actions, odd-minute schedule. The file must land on `main`, because schedules only run from the default branch.
2. Job A, `contents: read`: `npm ci --ignore-scripts` where possible, fetch EDGAR, compute, run data tests, upload the data files as an artifact.
3. Job B, `contents: write`, no `npm ci` and no third-party code: apply only the allowlisted data files from the artifact, validate, push to `preview`.
4. Job C, promotion, only if decision 1 is auto-promote: separate workflow; gates listed under decision 1.
5. Commit a small summary each night. Keep full receipts as Actions artifacts, not in git.
6. All workflows: `permissions: {}` default, least privilege per job, actions pinned to full SHAs.
7. Vercel: `npm ci`, exact pins. Test once that Vercel builds bot-authored commits.
8. SEC User-Agent from one environment variable with a dedicated alias.
9. Two weeks of nightly runs on `preview` before any production change.

### Phase 2: site changes

1. Remove public run-status, failed-field lists and diagnostic banners. One line: "Certified figures as of <date>". Coverage report linked in the footer.
2. Filed events per decision 4, with rule text, triggering filings and dates. Rules published with a date; changes go on the corrections page.
3. Method page wording for the two tiers, for example: "Certified figures cover the SEC filers we track, verified nightly from EDGAR. The other tracked suppliers show last-verified dates and are outside the certified snapshot."
4. Attribution per decision 3.
5. Email signup and digest per decision 5. CSP in `vercel.json`: `form-action 'self'` plus the processor's form host, `script-src 'self'`, `frame-ancestors 'none'`.

### Monitoring

- Rewrite `freshness.yml` to check certified-date age and latest-attempt age, not the issue index.
- `if: failure()` step on every run that opens or updates one GitHub issue.
- Alert when blocked for N nights in a row, or when the certified date is older than the latest 10-Q.
- External dead-man check (healthchecks.io or UptimeRobot) on `/refresh-publication.json`, 48 hour threshold. Owner confirms GitHub issue notifications reach his phone.
- Monthly scheduled canary build that alerts on failure. No Dependabot PRs (they are a human step).

### Simplify (cut once phase 1 is certified)

- `web/published-app` dual renderer (about 1.4 MB with pinned hashes), after the first certified release.
- `scripts/auto-publish.sh`, `scripts/publish-issue.sh`, `gather.sh`, `gather-pr.yml`, issue signing.
- `check-live-sources.py` and `audit-supplier-receipts.py` on the nightly path.
- Playwright end-to-end on data-only runs.
- Laptop collector removed from the schedule (kept in the repo).

Per AGENTS.md, nothing is deleted on static analysis alone; each removal is proven with a before/after render.

## Email workstream (D-92): one complete unit

Ships together or not at all. Depends on Phase 1 producing a certified change log; nothing in it sends until that exists.

- Provider chosen on free tier with automated sending verified first. Kit's free plan excludes RSS campaigns, so an automated digest needs its API or another provider.
- Sender domain authentication on jessepike.dev: SPF, DKIM, DMARC.
- Plain HTML form on securitymarketpulse.com and jessepike.dev, double opt-in, tag per site.
- Privacy page naming the processor; unsubscribe in every email; postal address in the footer (required by CAN-SPAM; use a business address, not a home address).
- Digest generator in GitHub Actions from verified changes only; "no verified changes" line on quiet weeks; no send when the gate failed.
- CSP `form-action` for the provider's form host.
- `.claude/rules/constraints.md` update in the same pull request.
- jessepike.dev must exist as a hub page before the byline links to it.

## Durability requirements

- Runs with the laptop off and no agent session open.
- A failed run never changes published data.
- No secrets in phase 0 or 1.
- Rollback runbook written and tested once: `git revert` on `preview`, Vercel instant rollback on production.
- Node 22 reaches end of life in April 2027; schedule the upgrade.

## Portfolio pattern (reusable for future sites)

GitHub Actions refreshes data and commits to the trunk. Vercel serves static builds. One email account with a tag per site, owned by jessepike.dev. Same monitoring stack: failure issue plus external dead-man check.
