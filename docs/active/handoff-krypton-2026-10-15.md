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

D-87 to D-94 in decisions.md. Still open: branch protection (owner prefers no added cost), update cadence, and whether the byline uses his legal name or his alias.

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
