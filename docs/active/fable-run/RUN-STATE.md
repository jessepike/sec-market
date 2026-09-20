# Fable run state — SEC-MARKET-FABLE-001

## Resume here

Phase 0, orientation. The state file was created fresh on the first session. The coordinator has
read the brief, `AGENTS.md`, `intent.md` and `.claude/rules/constraints.md` itself, and task T0-1
(a `claude-haiku-4-5` reader summarizing the rest of the section 11 reading list into
`docs/active/fable-run/reading-summary.md`) was dispatched. The owner asked for the coordinator's
read on the situation and the Phase 1 plan **before** any Phase 1 research agent is dispatched, so
the exact next action is: confirm T0-1 returned and its file exists, give the owner the read and
the Phase 1 plan in the terminal, and wait for his go-ahead. Only then write the seven Phase 1 task
rows (T1-1 to T1-7, drafted below as pending) to running and dispatch them in one message.

Last updated: 2026-09-20T03:26:00Z

## Phase

Phase 0 — orientation. Closes when the owner has the coordinator's read and the Phase 1 plan and
says go. Phase 1 (research fan-out) follows.

## Task ledger

| ID | Task | Model | Status | Worktree | Branch | Preview URL | Artifact | Updated |
|---|---|---|---|---|---|---|---|---|
| T0-1 | Read the section 11 list (README, status, weekly-issue-spec, project-scorecard, durability-spec, routes.ts, generate-seo.ts, generate-feed.ts, BACKLOG SEC-027 to SEC-042, decisions D-60 onward) and write a summary | claude-haiku-4-5 | running | none (read-only, main checkout) | preview | n/a | docs/active/fable-run/reading-summary.md | 2026-09-20T03:26Z |
| T1-1 | Research: thesis-driven publications | claude-sonnet-5 | pending | none | preview | n/a | docs/active/fable-run/research/01-thesis-publications.md | 2026-09-20T03:26Z |
| T1-2 | Research: data-dense public intelligence products | claude-sonnet-5 | pending | none | preview | n/a | docs/active/fable-run/research/02-data-dense-products.md | 2026-09-20T03:26Z |
| T1-3 | Research: security-market peers and the price umbrella | claude-haiku-4-5 | pending | none | preview | n/a | docs/active/fable-run/research/03-peers-and-pricing.md | 2026-09-20T03:26Z |
| T1-4 | Research: monetization mechanics with real numbers | claude-haiku-4-5 | pending | none | preview | n/a | docs/active/fable-run/research/04-monetization-mechanics.md | 2026-09-20T03:26Z |
| T1-5 | Research: agent-readable web, current practice, both sides of the crawler argument | claude-sonnet-5 | pending | none | preview | n/a | docs/active/fable-run/research/05-agent-readable-web.md | 2026-09-20T03:26Z |
| T1-6 | Research: first-screen and information design craft, WCAG 2.2 AA as a design input | claude-sonnet-5 | pending | none | preview | n/a | docs/active/fable-run/research/06-first-screen-craft.md | 2026-09-20T03:26Z |
| T1-7 | Current-site teardown: render production and preview at 1440 and 390, read the markup, describe 5s / 30s / 3min | claude-sonnet-5 (with a claude-haiku-4-5 screenshot step inside it) | pending | none | preview | n/a | docs/active/fable-run/research/07-site-teardown.md | 2026-09-20T03:26Z |

Status is one of: pending, running, blocked, in-review, done, abandoned.

## Owner gates

- 2026-09-20 — Phase 1 go-ahead. The owner asked to see the read and the Phase 1 plan before
  anything is dispatched. Blocks T1-1 to T1-7.

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
