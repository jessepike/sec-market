---
project: Security Market Signal Pipeline
stage: Operate
updated: 2026-08-17
---

# Status

## Current State

Security Market Pulse is live at https://securitymarketpulse.com. Owner has already reviewed it. The site currently shows one frozen research edition (Episode 002). That is not enough. The product job is now recurring cybersecurity market intelligence: what changed, what it means, and what new startups, funding, and M&A belong on the page.

Local, GitHub `main`, and Vercel are synced by committing the live scorecard tree and deploying that GitHub commit (D-31). Future ships go local → GitHub → Vercel only.

## Project truth

| Layer | State |
|---|---|
| Purpose | Help security leaders, account teams, and clients time GTM, account, and technology decisions |
| Live site | https://securitymarketpulse.com — accepted by owner |
| Episode 001 | Done. One-time call on agent security readiness. Still usable as background. |
| Episode 002 | Done. Current published market call. Infra spend is up. We will not fake a security-spend lag. |
| Recurring signals | Ops artifacts live (D-43). Activity + prints on site. Loop A: Tuesday multi-source gather. |
| Git / production | `main` is live on Vercel. Deploy only via `git push origin main`. |
| Auto-publish judgments | Still not allowed without a human check |

## Next Steps

- [x] Publish the first market call on a public site
- [x] Point `securitymarketpulse.com` at Vercel
- [x] Owner reviewed the live site
- [x] Sync local scorecard tree → GitHub `main` → Vercel (D-31)
- [x] Startup-source research: catalog written and lead-reviewed (`SEC-MARKET-STARTUP-SRC-001`)
- [x] Cheap collection packet from the 10 allowed sources
- [x] Lead critique of startup insights and first-screen shape
- [x] Fable review accepted (D-36); Activity edition drafted — held for RoS 257+ (D-40)
- [x] Judgment layer wired; D-38 Avoid-line on the working tree
- [x] Five vendor prints on the scorecard (Cato, Netskope, Upwind, CRWD cloud, Torq)
- [x] Prints board converted to a dense table; `--content-max` 1280px
- [x] Ship ungated slice to `main` `67b53ff` (judgment + prints + table + Avoid) — live
- [x] SEC-009 execution plan written (D-41) — this is the steering page
- [x] Leadership ops artifacts: funding, M&A, domains, dashboard, brief (D-43)
- [x] Dated domain postures + edition delta on Tempo (D-45)
- [x] Edition delta derived from an append-only posture history, not hand-written (D-46)
- [ ] Owner review of branch `edition-dated-postures` on its Vercel preview, then merge
- [ ] Visual design pass — the site has never had one; it is the gating work for a public share
- [ ] Loop A: first Tuesday multi-source gather under new ops docs
- [ ] Refresh Activity when Return on Security publishes a new Security, Funded issue
- [x] Weekly desk: first real gather + reusable checklist (RoS #256; not published)
- [x] Domain coverage map: watch list across Pulse domains
- [x] M&A source catalog (map only) — lead reviewed
- [x] Durable gather → synthesize → check → post model (map only) — lead reviewed
- [x] Local / GitHub / Vercel sync finished (`8b35e45`, D-31 / D-32)

## Pending Decisions

None blocking the signals job. Feed design (which VC pages, which public-record sources, what cadence) is lead work, not an owner gate.

## Blockers

Branch `edition-dated-postures` is waiting on owner review before it merges. `main` is production, so an agent no longer merges web changes without that review (AGENTS.md § Production deploy).

More than one session is working this repository. On 2026-08-17 a Cursor session built the dated postures on a branch and separately restored the vendor print cards to `main`, while a Claude session held the branch checked out. Branch checkouts moved under an active session. Use a worktree for any parallel work, and do not assume the branch you checked out is still the branch you are on.

`main` is two commits ahead of `origin/main` and unpushed. Pushing `main` publishes.

## Session Log

| Date | Summary |
|------|---------|
| 2026-08-15 | ADF v2 scaffolding initialized; governance and episode docs moved to `docs/reference/`; historical specs to `docs/archive/` |
| 2026-08-15 | Episode 001 (`SEC-MARKET-SIG-001` v0.2) completed; research freeze and independent review passed |
| 2026-08-15 | Owner reconciliation reclassified Episode 001 as thematic and authorized Episode 002 to test the infrastructure-to-security demand lag thesis |
| 2026-08-15 | Episode 002 research frozen; first review held the gate; v0.2 correction added a sparse quarterly panel, atomic provenance, coverage-limited domain calls, and bounded CSP actions |
| 2026-08-15 | Episode 002 v0.2 passed evidence, strategy, and practitioner review; fixed-lag result remains `NO-CALL` |
| 2026-08-15 | Human-verified shadow collection design v0.2 and seven-row replay corpus passed Gate S0 review; implementation remains unauthorized |
| 2026-08-15 | Gate S1 implementation specification v0.2 passed architecture, security, and builder review; implementation and replay remain unauthorized |
| 2026-08-16 | Security Market Pulse web MVP implemented; unsupported chart data corrected; evidence and product reviews passed |
| 2026-08-16 | Other Models usage reached ~65%; project switched to Composer-only, then Grok restored on the Cursor Models pool |
| 2026-08-16 | Website recalibrated: 2025 items moved to background, current 2026 prints and domain heat added |
| 2026-08-16 | Public Vercel project live; custom-domain cutover complete |
| 2026-08-16 | Owner closed product-review pending. Duplicate decision IDs fixed (deploy=D-25, DNS=D-26). Recurring public-signal intelligence is now the job (D-28). |
| 2026-08-16 | Startup-source catalog completed and lead-reviewed. First-week set is specialist cyber VC pages plus Return on Security and Cybersecurity Ventures. |
| 2026-08-16 | Three-copy sync closed. `main` `8b35e45` is live on Vercel via GitHub. Commit email must be `jesse@keatingpike.com` (D-31, D-32). |
| 2026-08-16 | Pulse sync session wrapped. Comparison shots deleted. Deploy path and email trap recorded in AGENTS.md and KB. |
| 2026-08-16 | D-40: shipped prints table, five vendor rows, judgment layer, Avoid-line (`67b53ff`). Activity edition held for RoS 257+. |
| 2026-08-17 | D-45: dated domain postures, horizons, producing evidence, and edition-to-edition delta on Tempo. Market call unchanged. |
| 2026-08-17 | Overnight launch hardening merged and live: prerendering, discoverability, bundle split, 11 citation repairs, mobile scroll fix. All invisible to a reader. Owner stopped the autonomous loop; it is cancelled and must not be resumed. |
| 2026-08-17 | Deploy contract changed: `web/` changes go branch → Vercel preview → owner approval → `main`. New mandatory visual review at 1440px and 390px, and a ban on deleting components on static analysis alone (AGENTS.md, CLAUDE.md, `web/scripts/shot.mjs`). |
| 2026-08-17 | D-46: edition delta rebuilt on an append-only posture history with two fail-closed build gates. Duplicate change line removed; mobile Tempo overflow fixed. On branch `edition-dated-postures`, awaiting owner review. |
