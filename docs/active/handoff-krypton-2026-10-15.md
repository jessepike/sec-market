---
for: Krypton and any agent picking up this project
from: Claude (claude.ai session with the owner), 2026-10-15
branch: proposal/auto-002
---

# Handoff: hosted automation proposal (SEC-MARKET-AUTO-002)

## What happened

On 2026-10-15 the owner reviewed the live site and the preview with Claude, then set new goals: fully automated, no laptop, no recurring human step, no written opinions, neutral facts, email capture tied to jessepike.dev, and a durable production site that is one property in his portfolio as an AI CISO advisor and entrepreneur.

Claude drafted `docs/active/automation-portfolio-proposal-2026-10-15.md`, ran a three-reviewer council (durability, governance and credibility, CI security), and revised it to v0.2. All three reviewers: approve with changes.

## State

- Nothing is built. Only two docs and a status entry exist, on branch `proposal/auto-002`.
- `preview` and `main` are unchanged. Production is still `28c7ffd`.
- No workflow, secret, schedule, credential or setting was created or changed.
- The session has push access to `jessepike/sec-market` as of 2026-10-15. Workflow-file write may still be blocked.

## Owner decisions logged 2026-10-15

D-88 to D-99 in decisions.md. All open items resolved: 4-hour check cadence (D-96), byline Jesse Pike (D-97), no-cost branch protection by design (D-98), security hardening (D-99). Owner to-do: DNS and account steps in `dns-hardening-2026-10-15.md`; merge jessepike.dev `sec/headers`; promote `preview` when ready. Next agent work: AUTO-002 Phase 0.

## Originally waiting on the owner

Nine decisions, listed in the proposal under "Decisions the owner must make". The ones that block everything:

1. Production promotion: auto-promote certified data-only commits, or keep manual promotion.
2. Certified scope: Option A (SEC filers, fixed by source class) or Option B (per-field dating, reverses D-85).
3. Attribution: supersede D-80 with a Method-page byline, or keep the site anonymous.
5. Email capture and digest: authorize, which needs a `.claude/rules/constraints.md` change with owner approval.

When the owner answers, log each as a D-number in `decisions.md` with his words, then start Phase 0.

## Do not

- Do not schedule anything before Phase 0 makes the gate passable.
- Do not push to `main`. Do not change `.claude/rules/` or `intent.md` without explicit owner approval.
- Do not copy local Claude credentials to CI (D-83).

## Update 2026-10-15 late

- Security headers live on both sites; Cloudflare email records set (see `dns-hardening-2026-10-15.md`). Owner click pending: Cloudflare DMARC Management for jessepike.dev. DNSSEC and CAA not done.
- Phase 0 complete (D-100). Run from `web/`: `npm run refresh:edgar && npm run refresh:filing-events && npm run certify:sec && npm run certify:gate`. Expect 80/80.
- Next agent work: Phase 1. Workflow on GitHub Actions every 4 hours (D-96): job A read-only fetch/compute/certify; job B write, no third-party code, pushes allowlisted data to `preview`; job C gated promotion of certified data-only commits (D-88); upload `.collect/sec-archive` as artifact; rewrite `freshness.yml`; external dead-man check. Workflow-file push may need the owner.

## Update 2026-10-15 later (Phase 1)

- Phase 1 workflows are on `preview`; they take effect once `preview` is promoted to `main` (owner's call). After promotion, watch the first scheduled `certified refresh` run: confirm the publish job pushes to `preview` and Vercel builds that commit (author is set to jesse@keatingpike.com because Vercel refuses unmapped authors).
- Open owner decisions: remove retired `publish-issue.yml` and `gather-pr.yml`; enable Cloudflare DMARC Management for jessepike.dev; DNSSEC and CAA.
- Next agent work after the first scheduled run is confirmed: Phase 2 (site shows certified vs not-certified, SEC event window from `filingRun.json`, "re-derived from SEC filings" wording, remove run-status panels, switch production from the frozen snapshot to the certified tier, then schedule `promote-certified.yml`).

## Update 2026-10-16 (Phase 2 live)

- Production renders the certified tracker (`main` `f765f2b`). Spec: `auto-002-phase2-spec.md`, decision D-101.
- Data path is now fully automatic: `certified-refresh.yml` every 4 h pushes changed certified data to `preview`; `promote-certified.yml` daily fast-forwards `main` after a 24 h soak and a fresh 100% re-certification. Any non-data commit on `preview` blocks auto-promotion until the owner promotes, so keep `preview` and `main` in step after docs or code work.
- Still to confirm: the first scheduled refresh and its Vercel build.
- Next work: email workstream (D-92) as one unit. Owner inputs needed: Buttondown API key as a GitHub secret, postal address, approval to change the `.claude/rules/constraints.md` line on email.
- Open owner items: remove retired `publish-issue.yml` and `gather-pr.yml` (they fail on every push); Cloudflare DMARC Management for jessepike.dev; DNSSEC and CAA.
