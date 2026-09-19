# Lessons

Hot buffer. One line per insight, newest date first. Keep the last ~15; promote
cross-project patterns to the knowledge base and drop them from here.

## 2026-09-19

- A 12-day silent gap between build-review turns let a locally-committed change (`d2cae33`, an inbox intake) sit unpushed and undiscovered until session-wrap's own `git log`/`git status` pass caught it. Re-check `git status`, unpushed-commit count, and the D-65-style owner-action list at the start of any session that resumes after a long gap, not just at wrap.

## 2026-09-05

- [promoted:kb:aa5fea38:2026-09-05] Claude Code cloud routines run behind an egress proxy that refuses CONNECT to any host outside a short allowlist (npm, GitHub, Anthropic). A job whose whole purpose is fetching the public web cannot run there until the environment's allowlist is set. Probe the network with one curl in the first run of any fetch job before trusting the design.

## 2026-09-04

- [promoted:kb:f42e4576:2026-09-04] An operator testing a gate's "no git remote" fallback ran `git remote remove origin` and never restored it; the next push failed with "'origin' does not appear to be a git repository". Tell operators to test such fallbacks with an env override or a temp clone, never by mutating the working repo's remotes, and check `git remote -v` before any push.
- [promoted:kb:8f53a57c:2026-09-03] Sub-agents stall on any Bash command containing `cd`: the permission prompt goes unanswered and the agent dies silently. Put the prohibition at the very top of every operator brief; use absolute paths, `git -C`, `npm --prefix`.
- [promoted:kb:66e6a872:2026-09-03] Creating a Claude Code cloud routine auto-attaches every account MCP connector. Clear them explicitly with `clear_mcp_connections: true` and confirm with `get` before arming a job that must see only the public web and the repo.
- [promoted:kb:20eae532:2026-09-03] `vercel project web-analytics <project> --scope <team> --format json` is the non-interactive form on CLI 54; `--yes` is rejected.
- [promoted:kb:c7efa364:2026-09-05] `verify:issue` check 12 reads bare digits in quarter labels ("Q2 FY2027", "M12") as numeric claims. Keep period labels out of headlines or extend the allow-list; do not weaken the check.
- [promoted:kb:dd61935e:2026-09-03] External review invocations that work: `codex exec -m gpt-5.6-sol --sandbox read-only -C "$PWD" - < prompt` and `claude -p --model claude-sonnet-5 --permission-mode plan`. Feed each the spec plus the diff, ask for numbered findings with severity, and fold them into the spec's amendment record.

## 2026-09-03

- [promoted:kb:eb06c6c0:2026-09-03] The first research question's frozen answer became the headline of a product meant to be a weekly pulse, and the recurring content sat in a collapsed board whose window had ended three weeks earlier. When a project moves from an episode to a recurring product, check that the front page carries the recurring question rather than the first one asked.
- [promoted:kb:1406388d:2026-09-03] Three weeks of gates, sweeps and visibility fixes were all correct and none of them moved the exposure denominator off one. Craft work on an unread page has a ceiling; the next unit of work should be the one that puts the page in front of a named reader.

## 2026-08-28

- [promoted:kb:b51ee163:2026-08-28] The site's whole message layer was collapsed and nobody had checked. "The read" — the market call, the do and avoid lists, the no-call boundaries — sits inside a closed `<details>` on production; `checkVisibility()` at 1561px returns false. The vendor scorecard was promoted out of exactly this pattern six days earlier and the read was never tested for it. Fixing one instance of a defect is not fixing the pattern, and the second instance was hiding the more valuable content.
- [promoted:kb:2f162256:2026-08-28] Adding evidence is not publishing a read. I specced three acquisition cards into a collapsed scorecard group and called it publishing the finding. The owner asked how the message actually reaches the page, which was the right question and one I had not asked myself.

## 2026-08-27

- [promoted:kb:fb388c8e:2026-08-27] A research subagent that spawns its own sub-agents can exhaust a session budget with no warning. Three lanes fanned out into eight-plus children and killed the run. The containment that worked: ban sub-agent spawning in the prompt, replace an open sweep with a fixed target list, add an explicit "record none disclosed and move on" stopping rule, and cap the output length.
- [promoted:kb:1ca920a5:2026-08-27] A null result can mean the question was aimed one layer too high. Twelve vendors disclose nothing about AI security revenue, which reads as an empty lane. The hard evidence was in the same filings one layer down, in the purchase price allocations of the acquisitions.
- [withheld:2026-08-27] A purchase price allocation says what an acquirer thinks it bought. Two AI security deals put almost the whole price in goodwill and assigned nothing to customer relationships, while an adjacent deal in the same filing put $464M of $476M into customer relationships. That contrast is stronger evidence than any figure either company would state directly.
- [promoted:kb:8dce3e63:2026-08-27] A header that undercounts what is on screen is the same defect as one that inflates it. My own spec told the implementer to keep primary and borrowed counts separate, which produced "0 prints" above a group displaying a real comparable print. Every gate passed. Nothing enforces that a group header matches its own rendered cards.
- [promoted:kb:0d1eff9b:2026-08-28] `node_modules` in `web/` was installed inside the OrbStack dev VM, so npm, npx and tsx cannot run on the host at all — esbuild refuses with a platform mismatch. Run them through `orb run -m dev`. Playwright and `shot.mjs` are the exception and do run on the host against system Chrome.

## 2026-08-22


## 2026-08-20


## 2026-08-19

- [withheld:2026-08-19] A figure in a record's `note` field is not interchangeable with one in its `value` field. Falcon Cloud at $800M is an absolute amount; every other row in that table is a growth rate. The delegate caught this and was right.

