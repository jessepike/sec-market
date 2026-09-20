# Fable run state — SEC-MARKET-FABLE-001

## Resume here

Phase 1, research fan-out. The owner said go on 2026-09-20 with no changes to the prompts. All
eight research tasks T1-1 to T1-8 were dispatched in one message at about 04:00Z, each told to
follow its section of `docs/active/fable-run/phase1-dispatch.md`. If this session died while they
were running, check which of the eight output files exist under
`docs/active/fable-run/research/`, mark those rows done after skimming them, and re-dispatch only
the missing ones from the same dispatch file with the model in each heading. Once all eight are
done: commit the research files (named paths only, never `lessons.md`), then the coordinator
writes `docs/active/fable-run/research-synthesis.md`, then Phase 2 (rubric and production
baseline).

Last updated: 2026-09-20T04:00:00Z

## Phase

Phase 1 — research fan-out. Closes when all eight research files exist, are committed, and
`research-synthesis.md` is written and committed.

## Task ledger

| ID | Task | Model | Status | Worktree | Branch | Preview URL | Artifact | Updated |
|---|---|---|---|---|---|---|---|---|
| T0-1 | Read the section 11 list (README, status, weekly-issue-spec, project-scorecard, durability-spec, routes.ts, generate-seo.ts, generate-feed.ts, BACKLOG SEC-027 to SEC-042, decisions D-60 onward) and write a summary | claude-haiku-4-5 | done | none (read-only, main checkout) | preview | n/a | docs/active/fable-run/reading-summary.md | 2026-09-20T03:40Z |
| T1-1 | Research: thesis-driven publications | claude-sonnet-5 | running | none | preview | n/a | docs/active/fable-run/research/01-thesis-publications.md | 2026-09-20T04:00Z |
| T1-2 | Research: data-dense public intelligence products | claude-sonnet-5 | running | none | preview | n/a | docs/active/fable-run/research/02-data-dense-products.md | 2026-09-20T04:00Z |
| T1-3 | Research: security-market peers and the price umbrella | claude-haiku-4-5 | running | none | preview | n/a | docs/active/fable-run/research/03-peers-and-pricing.md | 2026-09-20T04:00Z |
| T1-4 | Research: monetization mechanics with real numbers | claude-haiku-4-5 | running | none | preview | n/a | docs/active/fable-run/research/04-monetization-mechanics.md | 2026-09-20T04:00Z |
| T1-5 | Research: agent-readable web, current practice, both sides of the crawler argument | claude-sonnet-5 | running | none | preview | n/a | docs/active/fable-run/research/05-agent-readable-web.md | 2026-09-20T04:00Z |
| T1-6 | Research: first-screen and information design craft, WCAG 2.2 AA as a design input | claude-sonnet-5 | running | none | preview | n/a | docs/active/fable-run/research/06-first-screen-craft.md | 2026-09-20T04:00Z |
| T1-7 | Current-site teardown: render production and preview at 1440 and 390, read the markup, describe 5s / 30s / 3min | claude-sonnet-5 (with a claude-haiku-4-5 screenshot step inside it) | running | none | preview | n/a | docs/active/fable-run/research/07-site-teardown.md | 2026-09-20T04:00Z |
| T1-8 | Inventory of dated thesis history already in the repository (added by the coordinator; a history surface built from issues alone has one row) | claude-haiku-4-5 | running | none | preview | n/a | docs/active/fable-run/research/08-thesis-history-inventory.md | 2026-09-20T04:00Z |

Status is one of: pending, running, blocked, in-review, done, abandoned.

## Owner gates

- 2026-09-20 — Phase 1 go-ahead. The owner asked to see the read and the Phase 1 plan before
  anything is dispatched. Blocks T1-1 to T1-8. Read and plan delivered 2026-09-20T03:45Z. **Answered: go, no changes, 2026-09-20T04:00Z.**
- 2026-09-20 — Two owner actions outside this run cap its value and were raised in the terminal:
  choosing the gather runtime in `docs/active/durability-spec.md` section 12 (SEC-039), and naming
  the pilot list. Neither blocks Phase 1 to 3. Both are preconditions in the monetization plan.
- 2026-09-20 — Path ownership between this run and the parallel session in the same checkout.
  Blocks nothing until Phase 4 merges into `preview`.

## Decisions made this run

- Baseline target is production, https://securitymarketpulse.com. At run start `origin/main`
  (aa04875) is one docs-only commit behind `origin/preview` (a482fda), so production carries the
  same site as the trunk. Reversed if `preview` gains `web/` changes that are not promoted before
  Phase 2 starts.
- The coordinator writes `RUN-STATE.md` and the Phase 3 specs itself and commits them; every other
  file edit, build, fetch and screenshot goes to a subagent with an explicit model. Reason: the
  brief makes the state file and the specs the coordinator's own work. Reversed on owner say-so.

## Log

- 2026-09-20T03:20Z — Session 1 started. `RUN-STATE.md` did not exist; created it before any other
  work. `git worktree list` shows only the main checkout on `preview`. Unpushed count is zero.
- 2026-09-20T03:22Z — Reality check against the brief's section 2. The brief says issue `2026-w36`
  has sat unsigned on `preview` for fourteen days. That stopped being true about an hour after the
  brief was written: commit aa04875 signed and published `2026-w36` and a482fda records D-66,
  production promoted and confirmed live. Both commits landed in this checkout at 20:20 and 20:24
  local time, after this session's start snapshot (e0f41d6), which means **another session is
  working in this same checkout right now**.
- 2026-09-20T03:23Z — `lessons.md` has an uncommitted two-line change (knowledge-base promotion
  tags) that this session did not make. It belongs to the parallel session. This run will not
  touch, stage or commit `lessons.md`; every commit from this run stages named paths only.
- 2026-09-20T03:26Z — T0-1 row written, then dispatched.
- 2026-09-20T03:40Z — T0-1 returned. Summary is 156 lines. Key facts: the thesis is "Infrastructure
  is running ahead. Security is splitting, not booming." and each signed issue gives it a verdict;
  the running score reads "Holds in 1 of 1 issues"; the front page opens with the funding lane and
  the signed judgment sits below all four lanes (D-66 names this as the first thing for this run);
  issue 2026-w37 was due 2026-09-15 and does not exist; no `llms.txt`, no Markdown variants, no
  thesis endpoint; public email is held to the 2026-10-08 review and four held issues.
- 2026-09-20T03:45Z — Phase 1 prompts written to `phase1-dispatch.md`. Added T1-8. Model split:
  sonnet for the four tasks that need design judgment and for the teardown, haiku for pricing,
  monetization numbers and the repository inventory, with a fetched-versus-remembered rule on
  every number.
- 2026-09-20T03:45Z — Noted, not acted on: `.claude/rules/constraints.md` still says the website
  is not authorized, which the live site and `intent.md` v1.2 contradict. Not this run's file to
  edit. Raised with the owner.
- 2026-09-20T04:00Z — Owner said go. Rows T1-1 to T1-8 set to running, then dispatched in one message.
