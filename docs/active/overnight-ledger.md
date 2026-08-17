# Overnight ledger — launch hardening

State file for the autonomous continuation loop. Every cycle reads this first and
updates it before ending. Keep it short and factual: what is done, what is running,
what is next, and what a human must decide.

| Field | Value |
|---|---|
| **Branch** | `pulse/launch-hardening` |
| **Goal** | Make https://securitymarketpulse.com hold up under a first public share |
| **Owner decisions pending** | Enable Web Analytics in the Vercel project settings (one toggle, not an agent's to make) |

## Standing rules

- Never invent a market figure, revenue number, ARR, funding amount, date, or company
  fact. Every claim traces to a real cited source. This outranks everything else.
- Do not modify `intent.md` or `.claude/rules/`.
- Builds run in the OrbStack dev VM, never on the host.
- Nothing merges to `main` until it passes a clean build, the Playwright suite, and an
  adversarial review. Deploy is local → GitHub → Vercel, commit email
  `jesse@keatingpike.com`.
- Cheaper models for mechanical and research work; top tier for adversarial review.
- Leave the tree clean at the end of every cycle.

## Done

| # | Item | Commit | Evidence |
|---|---|---|---|
| 1 | Static prerendering at build time | `9aaf386` | `dist/index.html` 1,103 → ~118,000 bytes; headline, prints, tempo, activity, and all 72 evidence records present as real text; no hydration warnings |
| 2 | Discoverability layer | `786188d` | OG/Twitter/canonical tags, `og.png` verified 1200×630 at 54KB, JSON-LD + `sitemap.xml` generated at build from `meta.ts`, `robots.txt`, Vercel Analytics mounted, reader CTA (`NextEdition`) |
| 3 | Polish pass | `197a000` `354d39e` `003ac24` `d7a1ebf` `2d55b19` | Dead components and the inert `artifactLinks` stub removed; accessibility fixes and a mobile horizontal-scroll bug; recharts code-split out of the initial bundle; stale smoke-test assertions repaired; orphaned signals data flagged to the backlog |

Not yet independently verified — the polish agent's own claims still have to survive the
build check and adversarial review below before any of this merges.

## In flight

Wave 2, dispatched 2026-08-17 ~05:10 PT. Polish is committed. Still running: the
six-way evidence URL audit and the two verification agents (independent clean-build
check, adversarial fabrication/overclaim/deploy-contract review).

Next cycle: if the workflow has reported, triage its findings, fix what is real, then
merge to `main` and confirm the live deploy. If it died on a session limit, resume it
with `resumeFromRunId: wf_315e236a-31e`.

## Next, in order

1. Merge the verified launch-hardening slice to `main`, push, confirm the Vercel deploy
   is Ready, then curl the live host before calling it shipped.
2. Durability: split content out of TypeScript literals in `web/src/data/` into
   validated data files, so a weekly update is a data edit rather than a code change.
   This is the fix that makes the weekly loop survivable.
3. Edition + "what changed" model, so a returning reader has a reason to come back.
4. Sourced breadth into uncovered domains — application security, OT, and services —
   with hard source verification on every new claim.

## Known issues a human should see

- `web/tests/e2e/smoke.spec.ts:15` asserts `Google closed Wiz` is visible, but that item
  is `surface: 'background'` in `activity.ts` and correctly renders inside a collapsed
  `<details>`. The test fails and predates all of this work. Fixing it means deciding
  whether the assertion or the item's surface is wrong, which is a content call.

## Lost time

The 2026-08-16 session limit (reset 10:40pm PT) killed 10 of 11 agents mid-wave and no
loop was scheduled, so roughly six hours passed with no work. The recurring continuation
job now exists to prevent a repeat. It is session-scoped and expires after seven days.
