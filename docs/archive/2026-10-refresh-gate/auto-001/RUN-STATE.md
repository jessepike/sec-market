# Run state — SEC-MARKET-AUTO-001

Plan: `docs/archive/2026-10-refresh-gate/autonomy-coverage-plan.md`. Authority: D-76, D-77, `intent.md` v1.4.
Coordinator: Claude Opus 5.5 session started 2026-09-25. Supersedes the Fable run's phase T7
publish-on-approval work (`docs/archive/2026-09-weekly-issue/fable-run/RUN-STATE.md`).

## Resume here

As of 2026-09-26: steps 0 to 5 are built and on `preview`; step 0 is live. Waiting on the owner for (1) his word to promote `preview` (the facts-only page and the tracker are visible changes), (2) `gh auth refresh -h github.com -s workflow` so the workflow drafts in docs/archive/2026-10-refresh-gate/auto-001/step3/collect.yml.txt and step4/workflows/edgar-refresh.yml.txt can be installed, (3) `claude setup-token` and the resulting CLAUDE_CODE_OAUTH_TOKEN repository secret. Then install workflows, retire publish-issue.yml and gather-pr.yml per step4/workflows/retire-notes.md, close the w37 pull request, and score.

Steps 0, 1 and 2 are building in worktrees under `/Users/jessepike/code/projects/sec-market-wt/`.
Coverage research for step 5 is running in three parts (results land in this session's scratchpad
and are committed under `docs/archive/2026-10-refresh-gate/auto-001/step5/` once reviewed).

"Go" (D-77) covers step 0's promotion to `main`, which also carries the SEC-054 correction. Step 1
and step 5 are layout changes: render, show the owner, promote on his word.

Owner-only steps still ahead: `gh auth refresh -h github.com -s workflow` (the laptop token cannot
push workflow files) and `claude setup-token` for the model runner's repository secret.

2026-09-26 10:05: two fix passes from the blind scores merged to preview (bb7bdf7). Full-year collector backfill running in seven batches of about twelve suppliers in worktree sec-market-wt/backfill, branch data/collect-backfill; logs in the session scratchpad. After it: review new facts, gates, merge, mark collectState as full coverage only if every batch completed, then rescore with both models.

## Task ledger

| ID | Task | Model | Status | Worktree / branch | Output |
|---|---|---|---|---|---|
| A0 | Refresh 11 stale figures, mark 6 acquired | claude-sonnet-5 | done, merged, promoted to main 28c7ffd (D-78); PANW segments and Upwind left, no readable primary source | sec-market-wt/refresh, mon/refresh | docs/archive/2026-10-refresh-gate/auto-001/step0/report.md |
| A1 | Take judged text off live pages, add run-status line | claude-sonnet-5 | done after one fix pass (dates from one source, Platform pressure and position labels off); merged to preview f2f1b24; visible, waiting on the owner's word to promote | sec-market-wt/facts-only, mon/facts-only | docs/archive/2026-10-refresh-gate/auto-001/step1/report.md |
| A2 | EDGAR daily runner, no model | claude-sonnet-5 | done, merged to preview (ea3c0e5); 14 suppliers, 0 failures; workflow drafted as .txt pending the workflow scope | sec-market-wt/edgar, mon/edgar | docs/archive/2026-10-refresh-gate/auto-001/step2/report.md |
| A5a | Coverage research: endpoint, SecOps, MDR and services, exposure | claude-sonnet-5 | done, 25 suppliers | none | scratchpad coverage-g1.md |
| A5b | Coverage research: network, cloud, identity, email | claude-sonnet-5 | done, 27 suppliers | none | scratchpad coverage-g2.md |
| A5c | Coverage research: data, appsec, OT, AI security | claude-sonnet-5 | done, 29 suppliers | none | scratchpad coverage-g3.md |
| A5 | Twelve-domain tracker: data model, verify:tracker, front page tables, what changed, coverage | claude-sonnet-5 | done after density pass (1440 page 10,131px, 390 page 13,837px); merged to preview 3993a4c; coordinator fixed the fixed-date gate and 12-month count (2cf1334) | sec-market-wt/tracker, mon/tracker | docs/archive/2026-10-refresh-gate/auto-001/step5/report.md |
| A4 | Automatic publish path: allowlist, drift rule, gates, workflow drafts | claude-sonnet-5 | done, merged to preview; drift rule narrowed to web/.github/scripts (D-79) | sec-market-wt/autopublish, mon/autopublish | docs/archive/2026-10-refresh-gate/auto-001/step4/report.md |

| A3 | Claude collector: brief, collect.sh, workflow, one real run on a five-supplier slice | claude-sonnet-5 | done; proof run on four suppliers added the Optiv ACT divestiture; merged to preview 3bcd6a1 | sec-market-wt/collect, mon/collect (from mon/tracker) | docs/archive/2026-10-refresh-gate/auto-001/step3/report.md |
| A7 | Rubric v3.0 for the facts-only tracker, then blind scores by claude-opus-5-5 and gpt-6-sol | claude-sonnet-5 (rubric) | round 3 scored on a8d3976: Opus 59.8, Sol 39.0, both not fit (Snyk last round wrong and stale; status line counts 14 public suppliers against 18 on the page) | none | docs/archive/2026-10-refresh-gate/auto-001/score3/ |
| A8 | Fix pass 4, data: Snyk and private-round sweep, dated facts, status-line denominator, 8-K events, one-decimal growth, document sources, tracker.json, collector fallbacks | claude-sonnet-5 | done, merged to preview 32a771c; failed newsrooms 28 to 11; integrity regression and two ownership cells fixed on review | sec-market-wt/fitfix, mon/fitfix | docs/archive/2026-10-refresh-gate/auto-001/fitfix4/data-report.md |
| A9 | Fix pass 4, UI: 390 keyboard and tap targets, phone rows, type and colour, self-hosted fonts, CLS, reference rows, selection statement | claude-sonnet-5 | done, HELD off preview: owner judged the design poor and opened a four-model redesign bake-off (docs/archive/2026-10-refresh-gate/design-bakeoff/); its accessibility and speed fixes are carried forward in the brief | sec-market-wt/uifix, mon/uifix | docs/archive/2026-10-refresh-gate/auto-001/fitfix4/ui-report.md |

Research files are committed at docs/archive/2026-10-refresh-gate/auto-001/step5/research/.

Last updated: 2026-10-02

Next: the bake-off winner is rebuilt on preview, then both blind scorers rescore. D-80 (independence line, owner name off live pages) is on preview.
