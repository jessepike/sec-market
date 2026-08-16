---
project: Security Market Signal Pipeline
stage: Operate
updated: 2026-08-16
---

# Status

## Current State

Security Market Pulse is live at https://securitymarketpulse.com. Owner has already reviewed it. The site currently shows one frozen research edition (Episode 002). That is not enough. The product job is now recurring cybersecurity market intelligence: what changed, what it means, and what new startups, funding, and M&A belong on the page.

## Project truth

| Layer | State |
|---|---|
| Purpose | Help security leaders, account teams, and clients time GTM, account, and technology decisions |
| Live site | https://securitymarketpulse.com — accepted by owner |
| Episode 001 | Done. One-time call on agent security readiness. Still usable as background. |
| Episode 002 | Done. Current published market call. Infra spend is up. We will not fake a security-spend lag. |
| Recurring signals | Not built. This is the stall. Now the next job. |
| Git / production | Live site was uploaded from the working tree. GitHub `main` is behind until that tree is committed and pushed. |
| Auto-publish judgments | Still not allowed without a human check |

## Next Steps

- [x] Publish the first market call on a public site
- [x] Point `securitymarketpulse.com` at Vercel
- [x] Owner reviewed the live site
- [ ] Commit and push the live working tree so GitHub matches production
- [ ] Stand up a signals job: gather public startup, funding, and M&A events, reason on them, and feed the site
- [ ] Keep the published call honest when new evidence arrives

## Pending Decisions

None blocking the signals job. Feed design (which VC pages, which public-record sources, what cadence) is lead work, not an owner gate.

## Blockers

- Another local session (`bc-a52b0155-9d4a-4ccf-9450-aa99b8de1ad1`) may still be editing the site. Do not overwrite that work.
- GitHub `main` is stale relative to the live CLI deploy. Commit the live tree, then push. Do not push the old committed `main`.

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
