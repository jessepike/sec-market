---
id: SEC-MARKET-AUTO-002
version: 0.1
state: draft for council review
created: 2026-10-15
author: Claude (claude.ai session with the owner)
supersedes: nothing yet
---

# Hosted automation, rule-based signals and portfolio tie-in

## Why this exists

The owner restated the goal on 2026-10-15:

- The site should run with no laptop and no weekly human step. Low friction, low overhead, fully automated.
- He does not want to commit to a written point of view. Credibility should come from accuracy and from a published method.
- He wants rule-based, neutral signals instead of opinions. No "vendor risk" framing (he sells some tracked vendors in his day job).
- securitymarketpulse.com stays the product domain. jessepike.dev becomes the author hub and email home.
- The site is one property in a portfolio (jessepike.dev plus future sites) meant to build his profile as an AI CISO advisor and entrepreneur.
- It must be a durable production site.

This document proposes how to get there. Several parts conflict with recorded decisions. Those are listed first, because they need the owner's decision before any build.

## Conflicts with recorded decisions and rules

| Rule or decision | What it says | What this proposal would change | Decision needed |
|---|---|---|---|
| `.claude/rules/constraints.md` | "A database and an email digest are not yet authorized" | Add an email signup (Kit) and an automated digest of verified changes | Owner authorizes email capture and digest; rules file updated with his approval |
| `.claude/rules/constraints.md`, D-76 | Machine may not publish judgments: stances, rankings, forecasts, interpretation | Publish rule-based signals computed by the machine | Owner decides whether owner-written rules applied mechanically count as his judgment (allowed) or machine interpretation (not allowed) |
| D-80 | Owner's name on no live page; no employer named | Link the site to jessepike.dev as author hub | Owner chooses: (a) named byline linking to jessepike.dev, (b) neutral footer link only, (c) keep site anonymous and link one way from jessepike.dev |
| D-85, D-86 | A data update publishes only at 100% substantive verification of every required applicable claim | Make publishing actually able to complete | See "Refresh gate" below. Option A keeps D-85 intact |
| D-83 | Collector runs under the owner's Claude subscription; no copying credentials to CI, no new tokens without action-time approval | Retire the laptop collector; optional phase 2 uses an API key in GitHub Secrets | Phase 1 needs no AI and no new credential. Phase 2 needs explicit approval |
| D-73, D-75 | Weekly issue signed by owner's PR approval | Retire the weekly signed issue | Owner confirms retirement; archive stays |

## Current state (from the repo, 2026-10-15)

- Production `main` is `28c7ffd` (D-78). It still shows the signed postures and Jesse's name from before D-80.
- Preview is the facts-only tracker (D-82), 74 suppliers, 12 domains.
- No complete refresh has ever passed the D-85 gate. The 2026-10-14 attempt: 16 of 16 SEC filers succeeded; 248 field checks failed, almost all from newsroom and investor-relations pages that block automated reading (HTTP 403, Cloudflare and Akamai challenges).
- The EDGAR runner (`web/scripts/edgar-refresh.ts`, `refresh:filing-events`) is deterministic and has no AI in it.
- The newsroom collector (`scripts/collect.sh`) runs headless Claude Code on the owner's Mac under his subscription login. That is the only part tied to the laptop.
- A GitHub Actions workflow for the EDGAR refresh is drafted (`docs/active/auto/step4/workflows/edgar-refresh.yml.txt`) but never committed: the pushing token lacked workflow scope.
- `freshness.yml` already probes the live site daily from GitHub and opens an issue when stale.

## Proposal

### 1. Run the refresh on GitHub Actions

- Nightly scheduled workflow on GitHub-hosted runners. Steps: EDGAR XBRL revenue, EDGAR submissions for 8-K events (Items 1.01, 2.03, 2.05, 5.02 and similar), compute signals, run the existing data tests and build, commit data to `preview`.
- Vercel stays the host. It redeploys on push. No change to the static Vite architecture.
- Vercel Cron and Cloudflare Workers were considered and rejected: both would require moving data out of the build into a runtime store, a rebuild of the site's architecture, for no gain. Vercel Hobby cron also runs at most daily within a one-hour window and does not retry.
- Moving off the laptop will not fix newsroom blocking. Cloud runner IP ranges are blocked more often than home connections. The plan stops depending on newsrooms.

### 2. Refresh gate

Option A (recommended, keeps D-85): narrow the certified snapshot to what can be verified automatically every night.

- Certified tier: SEC filers (currently 16) plus the EDGAR-derived fields and events for them. These can reach 100% substantive verification without a human.
- Second tier: private companies and non-SEC filers shown as "last verified on <date>" records, clearly outside the certified snapshot. They never advance the certified refresh date.
- The scope change is an explicit, logged owner decision and is stated on the Method page. That is a scope decision, not denominator gaming.

Option B: per-field publishing, each figure with its own as-of date and no all-or-nothing gate. Simpler, but it reverses D-85.

### 3. Rule-based signals

Owner-written, published rules, applied mechanically to filed numbers. Neutral wording. No colors, no scores, no ranking, no "risk".

Candidate rules (council to challenge each):

1. Year-over-year revenue growth lower than the prior quarter's for two consecutive quarters.
2. Year-over-year revenue growth negative in the latest quarter.
3. Two or more officer changes (8-K Item 5.02) within 12 months, or CFO and CEO changes within 12 months.
4. A restructuring or workforce reduction disclosed (8-K Item 2.05) in the last 12 months.
5. New debt or convertible notes issued (8-K Item 2.03) in the last 12 months.
6. The company was acquired or announced an agreement to be acquired.

Each signal shows the rule text, the filings that triggered it, and the date. The Method page explains what each rule does and does not mean.

### 4. Retire

- The laptop collector from the nightly path (kept in the repo, not scheduled).
- The weekly signed issue (archive kept).
- Public run-status, failed-field lists and diagnostic banners. Replace with one line: "Certified figures as of <date>". The full coverage report moves to a footer link.

### 5. Portfolio tie-in

- Email signup through Kit (free tier), tagged `smp`. jessepike.dev uses the same Kit account with its own tag. Future sites add tags.
- Automated weekly email of verified changes, generated from the existing change log or RSS. No human writing.
- Privacy line on the site naming Kit as the processor.
- Attribution per the owner's D-80 choice.

### 6. Phase 2, optional

Press-wire RSS (GlobeNewswire, PR Newswire, Business Wire) for private-company funding, acquisitions and leadership, with a small AI extraction step using an API key in GitHub Secrets and a spend cap. Requires explicit approval under D-83. Outputs stay in the second tier until verified against the primary document.

## Durability requirements

- Runs with the owner's laptop off, and with no agent session open.
- Every run leaves a receipt in the repo. Failures open a GitHub issue (reuse `freshness.yml` pattern), which reaches the owner's phone.
- A failed run never changes published data.
- No secrets in phase 1. SEC requires a User-Agent with contact info; use a dedicated alias rather than a personal address.
- Production still moves only by promotion from `preview`, unless the owner reaffirms D-76/D-79 auto-promotion for certified data commits.
- Rollback: Vercel instant rollback plus `git revert` on `preview`.

## Rollout

1. Owner decides the six conflicts above.
2. Build on a short-lived branch into `preview`. Visual review at 1440px and 390px per AGENTS.md.
3. Workflow file committed by the owner or by a token with workflow scope.
4. Two weeks of nightly runs on `preview` before any production promotion.
5. Owner promotes.

## Open questions for the council

- Is the certified-tier narrowing (Option A) honest under D-85, or is it denominator gaming?
- Do mechanical signals cross the no-machine-judgment line?
- What breaks first in a year of unattended operation?
- Is auto-commit from Actions to `preview` (and possibly `main`) safe with no branch protection on a free private repo?
- Does an author link help or hurt credibility, given D-80?
