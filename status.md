---
project: Security Market Signal Pipeline
stage: Operate
updated: 2026-10-14
---

# Status

## Current State

**2026-10-14: the owner selected the October bake-off hybrid and authorized implementing and pushing it to the existing Vercel preview (D-82).** Built in the app from preview base `a021795`, using corrected fix-pass-4 data already integrated at `32a771c`. The first screen pairs a capped, sourced change log with the public-company revenue comparison. Derived counts, supplier facts/records, a keyboard/touch timeline and a compact phone domain selector replace the stacked front-page tables. The empty owner's-read placeholder and unsupported domain medians are absent. The snapshot remains explicitly 2 October 2026; shipping a design does not refresh evidence. No production promotion is authorized. Lint, TypeScript, full build/data gates, 255 data tests and the built-page browser suite passed. App commit `ddb316b82f40401ffec40a3711e6205483b06f4b` is deployed Ready on the existing stable preview URL. All 32 browser tests passed against that deployed page; desktop/phone screenshots were inspected. The measured phone page is 7,311px versus production’s 18,698px, with no horizontal overflow. Production remains at `28c7ffd`, deployment `dpl_9mjdUV7fWSSgBrmSPuUbv4ekRUeg`. Jesse’s review of the resulting preview is next; production promotion remains unapproved. See `docs/active/design-hybrid-preview-2026-10-14.md`.

The October 2 paragraph below is historical: `mon/fitfix` is already an ancestor of `preview`; `mon/uifix` remains divergent and is not implicitly merged by selecting the redesign.

**2026-10-02: fix pass 4's data side is done, committed on branch `mon/fitfix` in worktree `sec-market-wt/fitfix`, synced with `origin/preview`, not yet merged into `preview`.** Two blind scorers
failed the preview build on rubric v3.0 (Opus 59.8/100, Sol 39.0/100); the 12-item data/pipeline brief
(see `docs/active/auto/fitfix4/data-report.md`) is complete, every gate green including
`verify:integrity` (5 pre-existing unreferenced records, same as preview; see SEC-058 for the gate's
zero margin). The coordinator's review caught a real build-breaking regression and two wrong ownership
cells (Delinea, Ivanti), all fixed and re-verified against primary sources. `mon/fitfix` has been
merged with `origin/preview` (three real conflicts resolved: decisions.md, generate-seo.ts,
HowThisWorks.tsx) and the full `npm test` suite is green on the merged tree. The newsroom
failed-supplier count fell from 28 to 11 of 74 after a fallback-chain rewrite and a full incremental
collector run (D-81). A separate UI builder worked layout/type/accessibility in parallel in another
worktree; merging and promoting both
is the coordinator's next step, not done by this session.

**2026-09-20: the owner restated what the site is for, a front page aimed at it was built, and he
promoted it the same day (D-69). On 2026-09-21 he promoted again (D-72): the founding thesis moved to
`/thesis/`, with D-70 and D-71 from a parallel session. `main` was at `35a888f` after that and the live host was
checked.** The working statement of purpose is
`docs/active/product-core.md` (D-67): a credibility asset for his advisory work and a working
instrument for supplier decisions, written for security leaders first, not for investors, with the
founding thesis as one standing analysis. Read it before any design, rubric or review work.

**2026-09-21 (D-73 to D-75): the owner approved three builds so the site can be kept up from his
phone, all three are done, and two promotions landed the same day.** His approval of a weekly draft
pull request, or his comment `publish`, now signs and publishes the issue after every check passes;
the weekly job proposes scorecard updates behind a check on what each figure means and lists what is
going stale; the word `reconfirm` in his approval re-dates stale, unchallenged domain stances under
his name; the thesis verdict left the weekly issue. The spec, with an "as built" section covering two
review passes' worth of hardening, is `docs/active/publish-path-spec.md`
(SEC-MARKET-PUBLISH-001 v0.2). `main` is `9b98353` (D-75). The task ledger is
`docs/active/fable-run/RUN-STATE.md`, phase T7, done through T7-9 except one promotion (below).

**2026-09-21, SEC-054 (D-75 wording): the Platform pressure table wrongly called Palo Alto Networks
and F5 "a hyperscaler" when absorbing AI security companies.** Owner-approved replacement wording is
built, tested, dated to the approval and listed at `/corrections/`; merged to `preview` (`48fd77f`)
but **not yet promoted** — this is a visible change and needs the owner's word to reach production.

**2026-09-21 through at least 2026-09-25: macbook2014 has been unreachable.** It dropped off the
network partway through a hand-started run of the week-38 gather (issue due `2026-w38`, window
2026-09-14 to 2026-09-20) and has not answered ssh or ping since, apart from one "connection
refused" blip. No receipt and no pull request exist for that week. Its own Tuesday 07:00 schedule
(2026-09-22) would also have needed the machine awake, so that firing is unconfirmed too. Nothing
else in this run waits on that host; when it is back, check `~/gather-logs/receipts/` for anything
after 2026-09-21T21:08Z, and re-run `SMP_WEEK_ENDING=2026-09-20 ./scripts/gather.sh` there if there
is no receipt for it. Two fixes already landed and are live: the job loads `~/.env.local` for its
subscription token (it does not inherit a login shell), and it pre-approves the narrow set of shell
commands its brief needs (`--allowedTools`), because a headless run cannot answer a permission
prompt — the first hand-started attempt failed for exactly that reason before this fix shipped.

What that promotion put on production (merges f557b4c, 0ece0ce, 7535fc4): a one-sentence description, "Not a news
site and not investment advice.", a line giving the update date and the date the domain stances
were judged, a plain-words note under the headline, and a new first section, "The market by
domain", which lists every tracked supplier alphabetically under the owner's dated stance with its
exact metric and period and ranks nothing. Lane headings are in plain words, there is a visible
feed link and a follow line, and the page links its machine-readable files. The preview URL is
https://security-market-pulse-git-preview-pikeholdings.vercel.app. Promotion is the owner's call:
`git checkout main && git merge --ff-only preview && PROMOTE=1 git push origin main`.

**The correction to issue `2026-w36` is approved and on `preview` (SEC-043, D-68).** The signed issue
gave Zscaler's $898.2M and Palo Alto's $3.41B as fiscal-year revenue; both are fourth-quarter
figures. The owner approved the correction text on 2026-09-20. The locked issue is untouched: a
dated CORRECTED note sits beside each item, `/corrections/` lists it, the machine-readable files
carry it, and a gate now fails a fiscal-year label over a quarterly source. Live on production since the D-69 promotion.

Also on `preview` since the first merge (0ece0ce): the author's name on every dated JUDGED stamp
with a test behind it, compacted supplier rows so the signed read starts within two screens at
1440, phone chrome cut from 221 to 184 px, and "Weekly issue" in place of the issue id on the
front-page eyebrow.

Waiting on the owner, in order of value: say "promote" to put the SEC-054 wording fix live (it is
correct on `preview` now, wrong on production); amend `.claude/rules/constraints.md` and `intent.md`
with the wording proposed in `docs/active/publish-path-spec.md` section 2.3, now that the phone-tap
publish path is real rather than proposed (not urgent — nothing is blocked on it); decide whether
GitHub Pro is worth ~$4/month to lock `main` (SEC-051 — the weekly job's deploy key can currently push
anywhere, including `main`, and a free private repo has no branch protection); sign or close pull
request #2, the `2026-w37` draft, which predates the thesis-off-the-issue and sign-on-approval changes
and should be re-checked against the current schema before signing; edit or reject the first
machine-drafted buyer brief (`docs/active/fable-run/drafts/buyer-brief-network-sase.md`).

The run's state, ledger and log are in `docs/active/fable-run/RUN-STATE.md`. Its lessons have been
promoted into `lessons.md` (the KB-worthy ones) and this file (the project-specific ones); the
`docs/active/fable-run/lessons-pending.md` scratch file is now empty and can be deleted next time
someone is in that directory. New backlog items: SEC-043 to SEC-055.

**The weekly issue is published.** `2026-w36` was signed by the owner on 2026-09-19, who adopted the
gather's proposal as written, and `main` was promoted `b423b70` → `aa04875` the same day (D-66). That
is fifty-four commits and the first promotion since 2026-08-28, and it carries the whole weekly-issue
model into production: the issue hero and its four lanes, the `/issues/` archive, per-issue
permalinks, `/feed.xml`, `/issues/<id>.json`, the lock manifest at `/issues/lock.json`, and the
vendor lens. Confirmed by render rather than by deploy log — production returns 15,033 pixels at 1440
and 17,760 at 390, identical to preview at both widths, and every new endpoint returns 200. The page
carries `Signed by Jesse Pike · 19 Sep 2026` and `Holds in 1 of 1 issues since 19 Sep 2026`.

**The thing to look at next is the first screen.** Production used to open with a two-line thesis
headline, a stat band of three numbers, "The read" with its confidence lines, and the Do and Avoid
panels. It now opens with the issue headline and goes straight into the Formation lane — a
chronological list of funding rounds starting at $156.0M and running down to a $60.0K pre-seed. The
judgment sits below four lanes of items. That is the accepted D-64 composition rendering exactly as
`weekly-issue-spec.md` §4 specifies, so nothing is broken, but it is a real change in what a reader
meets first and nobody had seen it at full page height before the promotion. It is the first thing
SEC-042 should be pointed at.

A run brief for that work exists: `docs/active/fable-run-brief.md` (`SEC-MARKET-FABLE-001` v0.1),
written for Fable 5.1 as coordinator — a thesis surface that develops week over week, a researched
site scoring rubric, an agent-readable machine surface, and a monetization plan, with worktrees,
branch previews and a resumable run state. Owner-approved as a brief; the gates inside it are still
owner-held.

Earlier context: `main` was promoted to `4916a95` on 2026-08-25 (D-57), carrying eighteen commits and closing a five-day gap in which the trunk held finished work that no reader could see.

A visitor now gets three things production did not have before. The vendor scorecard is a top-level section with its forty-two cards grouped by domain, rather than buried inside a collapsed block below the author's signature. The phone page opens with its framing sentence and headline above the four domain cards. And six evidence records carry source attributions the 71-source sweep found missing, so every claim on the page names the document that states it. Confirmed by render, not by deploy log: production returns 8,274 pixels at 1440 and 8,237 at 390, identical to preview at both widths.

The desktop page roughly doubled in length as a result, 4,315 to 8,274 pixels. That is the cost of making the evidence findable and it was approved knowingly.

There are two long-lived branches (D-50). `preview` is the trunk and serves a fixed public URL at https://security-market-pulse-git-preview-pikeholdings.vercel.app. `main` is production, serves https://securitymarketpulse.com, and moves only by a fast-forward promotion from `preview` on an explicit owner yes. A pre-push hook refuses a direct push to `main`; promotion requires `PROMOTE=1`. Install per clone with `./.githooks/install`.

## Project truth

| Layer | State |
|---|---|
| Purpose | Help security leaders, account teams, and clients time GTM, account, and technology decisions |
| Live site | https://securitymarketpulse.com — accepted by owner |
| Episode 001 | Done. One-time call on agent security readiness. Still usable as background. |
| Episode 002 | Done. Current published market call. Infra spend is up. We will not fake a security-spend lag. |
| Recurring signals | Ops artifacts live (D-43). Issue `2026-w36` published and signed 2026-09-19 (D-66). The gather job is still unarmed and has no working runtime. |
| Git / production | `main` at `9b98353` is live on Vercel, promoted 2026-09-21 (D-75). Promotion only by fast-forward from `preview` with `PROMOTE=1`. |
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
- [x] D-48 landscape merged, pushed, and confirmed serving on https://securitymarketpulse.com
- [x] One-product preview pass: collapse edition stack, fix Cloud chip, drop edition CTA and weekly claim, unprotect preview URLs (D-48)
- [x] Loop A: first multi-source gather under the new ops docs (RoS #257) — packet at `docs/active/signals-week-2026-08-19.md`, lead reviewed, owner sign-off pending
- [x] 71-source verification sweep; six unattributed claims fixed (SEC-020)
- [x] Vendor scorecard made findable — Phase 1 top-level section, per-group collapse (SEC-021, D-54)
- [x] Project scorecard v0.2 written with an honest baseline (SEC-022, D-55)
- [x] Phone view corrected back to the accepted Option D design (SEC-023, D-56)
- [x] Promote the eighteen pending commits to production after a rendered before-and-after (D-57)
- [x] SEC-025 Part 1: a print may carry a secondary domain, with three new integrity gates (`preview` only)
- [x] SEC-025 Part 2: bounded AI coverage gather across twelve vendors, lead-verified against filings
- [x] SEC-MARKET-AI-002: the AI acquisition read published to the scorecard and the domain rationale
- [x] SEC-MARKET-READ-001: the market read promoted out of the disclosure to the top of the page (D-60)
- [x] Build gate: a must-see section nested in a disclosure now fails the build
- [x] Stale end-to-end smoke test repaired; suite green
- [x] Date constant split so the site stamp and the judgment dates move independently
- [x] Promoted to production `b423b70` (D-61), confirmed serving by browser query
- [x] Owner accepted intent v1.2 as written (D-63); `intent.md` updated
- [ ] Write `weekly-issue-spec.md` and `gather-job-spec.md`, review, then dispatch the builds (SEC-027, SEC-028)
- [ ] Owner: name the pilot set and the independent scorer (D-58 shape, names still missing)
- [x] Sign `2026-w36` and promote the weekly-issue model to production (D-66)
- [ ] Owner: how the AI coverage finding gets presented on the site — largely answered by the weekly issue model if the plan is accepted
- [ ] Owner: who scores the project scorecard independently, and who counts as qualified exposure
- [ ] Owner: shorter phone footer labels, yes or no (SEC-023)
- [ ] Enforce `sourceAttributions` in `verify:integrity` when an excerpt spans more than one source
- [ ] Refresh Activity when Return on Security publishes a new Security, Funded issue
- [x] Weekly desk: first real gather + reusable checklist (RoS #256; not published)
- [x] Domain coverage map: watch list across Pulse domains
- [x] M&A source catalog (map only) — lead reviewed
- [x] Durable gather → synthesize → check → post model (map only) — lead reviewed
- [x] Local / GitHub / Vercel sync finished (`8b35e45`, D-31 / D-32)

## Pending Decisions

None blocking the signals job. Feed design (which VC pages, which public-record sources, what cadence) is lead work, not an owner gate.

## Blockers

None. The D-48 promotion record was reconciled on 2026-08-19 (D-51) and production is current as of D-57. What remains open is owner input, listed under Next Steps, and it blocks the roadmap rather than the build.

## Merged to `preview`, still awaiting owner review (D-65) — RESOLVED 2026-09-19 by D-66

Two of the four decisions D-65 named have landed. The owner signed `2026-w36` on 2026-09-19 and
authorized the promotion, so `main` is now `aa04875` and the issue is published. Two remain open:
the pilot list is still unnamed, and routine `trig_01VeQpLYzXjccqKeSFS1Xgo6` is still disabled with
no runtime that can reach the public web. The account below is kept for the record of what was
pending.

**New since D-65:** a durability specification, `docs/active/durability-spec.md`
(`SEC-MARKET-DURABLE-001` v0.1, SEC-039), proposing a Sunday-afternoon cadence, a runtime chosen by
a probe (cloud allowlist first, a local `claude -p` runner as the fallback — the 2026-09-05 dry run
found the cloud routine's egress proxy blocks every public host), run-receipt and site-freshness
alerts owned by jobs-agent, a fifteen-minute signing script, and a post-promote check. A frontier-AI
fifth lane was scoped as SEC-040, not authorized, kept separate from the ePlus-relative reading that
belongs downstream. Both reviewed with the owner and published as artifacts; commits
`705135e`/`a725d55` on `preview`.

**Also new: an unrelated inbox intake, 2026-09-09, not part of this build.** The owner routed five
documents from a separate chat exploration into `docs/inbox/2026-09-09-category-compression/` —
an ecosystem/category-compression market thesis with vendor claims on Cloudflare, Fortinet,
SentinelOne, Varonis and Rubrik, a twelve-item hypothesis register, and a barbell-market structural
argument. Tracked as SEC-041, intake only. Two separate decisions are still open: whether the vendor
claims enter a gather packet as candidate card updates, and whether the structural lens becomes a
proposed market read for the owner to sign. Committed locally as `d2cae33`; **not yet pushed to
origin/preview** — `preview` is one commit ahead of `origin/preview`.

**Still open from D-65, unchanged:**

Gather dry run: one-off routine `trig_01La16jZAq9WaQPHyqpUUcyG` fired 2026-09-05 16:45 UTC,
drafting `2026-w35` onto `issue/2026-w35-dryrun` without a PR. Result: the mechanics passed and the network did not. The routine checked out `preview`, read the brief, wrote the issue file and index, ran all five gates and recorded their exit codes (the overlap failure was the expected one), committed with the right author and pushed `issue/2026-w35-dryrun` without opening a PR. But every source fetch was refused: the cloud environment's egress proxy returns 403 on CONNECT to any host outside its allowlist (npm, GitHub, Anthropic), so Return on Security, SEC.gov, SecurityWeek, Cybersecurity Ventures and even example.com were unreachable. Zero evidence was gathered. The run log is at https://claude.ai/code/session_019GoBZ3Bwt2x7zMmivUUvuU. Do not arm the schedule in this environment until its network allowlist includes the brief's §2 hosts (set at https://claude.ai/code/environments), or move the job to a runtime that can reach the public web (a Tuesday `claude -p` run from the repo on the laptop, or a launchd job on macmini). The stray branch `issue/2026-w35-dryrun` on GitHub can be deleted.

## Session Log

| Date | Summary |
|------|---------|
| 2026-09-19 | `2026-w36` signed and production promoted (D-66): `main` `b423b70` → `aa04875`, fifty-four commits, the weekly-issue model live at last. Owner adopted the gather proposal as written. All gates, 58 data tests and 25 e2e green; one live test repaired that had asserted against real data. Confirmed live by render at both widths and by four endpoint checks. Recorded that the first screen now leads with the Formation lane rather than the judgment. Fable run brief `SEC-MARKET-FABLE-001` written and backlogged as SEC-042. |
| 2026-09-19 | Session wrap: confirmed no owner action has landed on D-65 (issue still unsigned, `main` unchanged, routine still disabled); found and reconciled an unpushed local commit (`d2cae33`, the 2026-09-09 SEC-041 inbox intake) that this session did not make; recorded durability-spec follow-up state. No code changed. |
| 2026-09-05 | Autonomous build finished and merged to `preview` (D-65): weekly issue model and gates, `2026-w36` unsigned draft with receipts, reframed front page, archive and permalinks, JSON and RSS, lock manifest, vendor lens, three external review rounds, live e2e and screenshots at 1440 and 390. Gather dry run fired on a one-off cloud routine. Owner review, signature, pilot list, promotion and schedule arming are open. |
| 2026-09-03 | Orientation and intent-versus-built review. Finding: the intent describes a decision instrument and the site is a research edition with excellent hygiene; exposure denominator still 1, decision log still empty, and the frozen Episode 002 call sits where a weekly read should. Owner confirmed the two goals (ePlus GTM anticipation; a low-friction weekly pulse for CISOs on formation, absorption, prints and capital) and approved the approach: weekly issue as the product, agent-drafted and human-signed, emailed to a named pilot, ePlus consuming downstream (D-62). An `eplus.` subdomain was declined. Plan written to `docs/active/weekly-issue-plan.md` and sent to canvas; SEC-027 to SEC-031 opened; SEC-017 superseded. Nothing on `web/` changed. |
| 2026-08-25 | Production promoted to `4916a95` (D-57), the first promotion since 2026-08-20 and eighteen commits' worth. Approval followed a rendered before-and-after at 1440 and 390 rather than preceding it. The scorecard is findable, the phone opens with its framing line, the placeholder spark is gone from all forty-two cards, and six evidence records carry their missing source attributions. Confirmed live by render at both widths. Next work is the roadmap, grounded in intent's four observable-success tests rather than in further site features. |
| 2026-08-20 | Integrity pass shipped and promoted. An intent-versus-built audit found the site asserting things about itself that were not true — a provenance legend state with zero instances, a hero saying four domains while six carried postures, a navigation claiming a weekly cadence the method denied, and an evidence resolver that would have crashed the moment SecOps was promoted. `SEC-MARKET-INTEGRITY-001` specified eight corrections and a `verify:integrity` build gate; Cursor Composer implemented, the CPO session verified by perturbing all five gate checks and by rendering the page. Owner promoted to production (D-53). Live and confirmed by query. |
| 2026-08-19 | Prod and preview put on a stable footing. Production verified by query to be serving the accepted D-48 landscape. `preview` created as the standing trunk with a fixed public URL; `main` is production and moves only by fast-forward promotion (D-50). Pre-push guard added and proven to fire. Owner confirmed he approved D-48, so D-49 is retracted by D-51: the failure was that the approval was never written down, not that it was missing. |
| 2026-08-19 | Loop A ran for the first time since the landscape shipped. RoS #257: four product rounds totalling $97.1M, one $2.2B public-markets debt raise held out of the product count, eight M&A deals with one disclosed value, no net-new VC portfolio names. Every figure re-verified against the source directly. Two lead corrections: the Fortinet earnings line omitted the 3.08% day decline, and its 33% billings figure is the print already frozen as evidence C3, not new. Market call frozen. Three merged branches deleted. |
| 2026-08-19 | CTO verified the D-48 landscape is genuinely serving on production by query, not by doc. Backlog duplicates removed. Open: D-48 says do not merge to `main` and the merge landed with no recorded approval. |
| 2026-08-19 | Repo health cleanup pushed to `origin/main` (`68b74e9`): landscape merge, CI, doc reorg, edition gate, signals retired. |
| 2026-08-19 | Repo health cleanup complete: edition integrity gate, orphaned signals retired, branch cleanup. |
| 2026-08-19 | Repo health cleanup: governance backported to `main` (D-45–D-48). PR #1 closed as superseded by `landscape/ui`. Production unchanged. |
| 2026-08-19 | Session wrap. D-48 one-product preview is public and ready for feedback. Production unchanged. Do not merge. |
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
| 2026-08-17 | Landscape UI (Task 2) on branch `landscape/ui`: provenance rail, four domain cards, what-moved, platform pressure, hypotheses, corrections. Not merged. |
| 2026-08-18 | Session wrap. Owner is holding the `landscape/ui` preview. Repo left clean. No P0 implementation work remains. |

## Handoff — 2026-08-19

**From:** CTO session (Opus), sec-market design and delegation arc
**To:** fresh CTO session (Opus)
**Context:** The Option D landscape shipped and is confirmed live. Design, both implementation specs, and the delegation to Cursor Composer are done. This repo has no P0 build work left. The next session's job is the CTO inbox first, then small repo tidying here.

**Next actions:**
1. Work the CTO inbox at `/Users/jessepike/code/_shared/agent-exec/cto/inbox/` — 10 notes are open. Start with `2026-08-19-1654-knowledge-items-sit-in-three-client-repo-kb-db-silos-an.md`, which needs a real architecture call: 2023 knowledge extractions sit in 12 repo-local `kb.db` files, ten of them client repos, and bulk-loading them into the shared store is an unreviewed cross-boundary export. Sequence the redaction stage before any migration, or decide some silos are written off.
2. Then `2026-07-25-config-drift-findings.md`, which expires 2026-08-25.
3. Then `2026-07-27-cls-sync-ssh-alias-exit-255.md` (P1, one line in the owner's `~/.ssh/config`, needs him).
4. Then the small sec-market items: resolve the D-48 record above, and check whether Task 2's `landscape/ui` branch still needs deleting now that it is merged.

**Key files:**
- `/Users/jessepike/code/_shared/agent-exec/cto/inbox/` — the actual queue
- `/Users/jessepike/code/projects/sec-market/decisions.md` — D-48 is the unreconciled entry
- `/Users/jessepike/code/projects/sec-market/BACKLOG.md` — SEC-013 carries the current landscape state

**Model recommendation:** Opus. Every remaining item is a judgment call about data boundaries or a governance record, not implementation.

## Session — 2026-08-20 (CPO): source verification sweep

**What ran.** Every one of the 71 canonical evidence sources in `web/src/data/evidence.ts` was
checked against the live page on three questions: does the link resolve, is every figure and clause
in the stored excerpt actually on that page, and is there any sign the page was corrected or
restated. Six agents in pass one, three more to recover blocked records and hunt missing sources.

**The result that matters: no figure on the site contradicts its source.** Not one. Every number
that could be read against its page matched.

**Six records had a genuinely unattributed second claim. All six are fixed and committed.** Each
bundled a claim from a second document without using the `sourceAttributions` array the schema
already provides and `EvidenceDrawer.tsx` already renders. A3 Arista, A5 Vertiv, B1 Microsoft, C2
Palo Alto, C7 Okta, and the Marsh half of D6 now each name the document that states the claim, with
every URL fetched and quoted verbatim before use. Nothing was deleted, reworded, or re-dated to fit
a page. Build passes `verify:edition`, `verify:panel` and `verify:integrity`.

**Owed and not built — the one thing that stops this recurring.** `verify:integrity` should fail the
build when a record's excerpt spans more than one organization or economic period and the record
carries no `sourceAttributions`. All six defects would have been caught at authoring time. This is
the durable fix and it is the recommended next action here.

**Read the audit before trusting any count in it.** `docs/audits/2026-08-20-source-verification.md`
is the append-only record, and its Correction section at the top matters more than its findings: the
sweep overstated the defect twice before landing on six. Three separate false-positive rounds all
came from the same mistake — a check scoped narrower than the data it was checking. The third round
was mine, and it produced a well-evidenced recommendation to delete two entirely accurate records.

**Still unreadable: 11 records, all host-side blocks.** Investor-relations timeouts, two Akamai 403s,
and one Incapsula bot challenge on Cato that must not be bypassed. None are dead links, none are
known defects. Broadcom needs a real browser rather than a fetcher.

**Untouched and still owed by the owner:** the above-the-fold decision that blocks SEC-019, the
cadence table naming which signal families refresh at what interval, and the Activity board's
"Jul 6 – Aug 10" window question. Nothing was promoted to production this session; `preview` carries
the work.

## Session — 2026-08-20/22 (CPO): the missing scorecard, a project scorecard, and the phone view

**The vendor cards were never removed.** The owner remembered a grid of per-vendor cards organised
by domain and asked which decision had taken it away. None had. All 42 were in the served markup,
nested inside a collapsed `<details>` four sections down. I first said they were present on the
strength of the HTML, which was wrong in the way that matters — being in the markup is not being on
the page. A browser measurement returned 42 in the document and zero visible. D-54 records this.

**Phase 1 of the visibility fix is on `preview`.** The scorecard is now a top-level section under
the tracked hypotheses, its eight domain groups collapse individually so a phone does not get a
17,000-pixel wall, and the group counts derive from the data. Specification:
`docs/active/scorecard-visibility-spec.md` (`SEC-MARKET-VIS-001`). Phases 2 and 3 — mapping each
print to the posture it supports, and a real archive of prior editions — are specified and not
started.

**A project scorecard now exists and its baseline is deliberately unflattering.**
`docs/active/project-scorecard.md`, v0.2 after an external model took v0.1 apart and was right on
every count. It measures outcomes by evidence state against an exposure denominator that currently
reads one, refuses a composite number, and keeps per-edition shipping discipline separate from
impact. Every outcome is `not_assessed`, legibility fails, and the decision impact log has zero
entries. Two questions belong to the owner: who scores this independently, and who counts as
qualified exposure. D-55 records the design.

**The phone view had drifted from the accepted design.** Rendered at 390 pixels, the page opened
straight into four domain cards with no framing at all — the eyebrow, headline and lede all rendered
after them, because the Option D implementation set `order: 2` on the intro and `order: 1` on the
cards. The accepted render at `.design/out/option-d-mobile-1of2.png` shows one short framing
sentence above the cards. Every build gate passed the whole time; nobody had rendered a phone width
since Option D landed. Fixed on `preview` and confirmed by render, not by report: document order
restored, the phone eyebrow hidden as the design has it, the lede tightened, the card judged footer
collapsed from three stacked lines to one, and the missing Scorecard entry added to the navigation.
Phone page 8,309 → 8,237 pixels; desktop identical at 8,274 pixels with its judged footer still two
stacked lines. D-56 records it. The rest of the phone page was inspected end to end and reads
correctly.

One phone item is left deliberately undecided. The accepted design uses shorter footer labels
("JUDGED 17 AUG · THIS QUARTER · CONF MEDIUM") that fit one line where the current wording wraps to
two. That drops the year and the word CONFIDENCE from a provenance stamp, so it is the owner's call
rather than mine. SEC-023 carries it.

**Nothing has been promoted to production.** `preview` carries all of the above.

## Session — 2026-08-25/27 (CPO): AI security coverage

**A reader said the AI security coverage was thin and the measurement agreed.** Seven AI-relevant
items across the 42-print scorecard, six of them capital. The single buyer-side item sat under Cloud
security. Three of the seven sat under other domains and none was misfiled — each print carries one
`group` string, so the model could not say a print belongs to two domains. Spec:
`docs/active/ai-coverage-spec.md` (`SEC-MARKET-AI-001`).

**Part 1 is on `preview` at `810e13e` and not promoted.** A print may now carry a `secondaryGroup`,
set on exactly three records. A borrowed card renders in the second group with a visible label
naming its primary group, and the eyebrow still counts distinct prints, so the board cannot inflate
itself. Three new `verify:integrity` checks, each observed to fail under a deliberate perturbation
before being accepted; the third server-renders the component and asserts the label is really in the
output. One defect came from my own spec: I told the implementer to keep primary and borrowed counts
separate, which produced a header reading "0 prints" above a group displaying a genuine comparable
print. Every gate passed. Fixed so every number in a header describes what is actually rendered.
Nothing yet enforces that relationship, which is the remaining hole.

**Part 2, the gather, is complete and lead-verified.** Record:
`docs/active/ai-coverage-gather-2026-08-27.md`. Twelve public companies checked across investor
pages, newsrooms and their two most recent filings. None discloses revenue, ARR, customer count,
seats or attach rate for an AI security product. That null result is real but it was the wrong
altitude: the hard evidence sits one layer down in the same filings. F5 paid $145.2M for CalypsoAI
and states its revenue and earnings were not material; $114.2M of that price is goodwill and nothing
is assigned to customer relationships. Palo Alto paid $634.5M for Protect AI with $515.8M goodwill,
$70.0M of developed technology and again no customer-relationships intangible, against the IBM
QRadar deal in the same filing where $464M of $476M in intangibles was customer relationships. A
third F5 deal, SurePath AI at $50.1M closed 2026-06-15, was on no list and surfaced only from
reading the filing. Every figure in that paragraph was re-extracted from the filing by the lead
rather than taken from a lane report.

**One finding touches live site data.** CyberArk filed Form 15-12G on 2026-02-23 and no longer
trades or files. The Identity card's watch item "Palo Alto vs CyberArk mix" cannot resolve as
written, because they are now one filer.

**Nothing has been promoted and no posture, call or confidence value has been changed.** How the
finding gets presented is the owner's call and the spec deliberately held it until coverage was
known. Coverage is now known.

## Session — 2026-08-28 (CPO): the read was never on the page

**The owner asked how a research finding actually reaches the page, and the answer was that it
doesn't.** I had specced three acquisition cards into a collapsed scorecard group and reported that
as publishing the finding. Adding evidence is not publishing a read.

Chasing that turned up something worse. `#read` — the market call, what changed, Do, Avoid, the
no-call boundaries — was inside a closed disclosure on production, along with the masthead carrying
the headline. Confirmed in a browser at 1561 pixels: in the document, `checkVisibility()` false. A
reader saw a tagline, four domain cards and forty-two vendor cards. Evidence with no read attached.
This is the same defect D-54 fixed for the scorecard six days earlier, on more valuable content.
D-60 records it.

**Both are now on `preview` and verified by me, not by report.** `#read` returns true at 1440 and
390, has no disclosure ancestor, and the page's single `h1` is the market call. The landscape tagline
dropped to `h2`; both headings kept their exact sizes, and all four domain card titles still compute
to 19px at weight 600, so the `.landscape h2` collision that would have blown them up did not happen.
The read carries the acquisition finding in What changed and in Avoid, in a separate commit so it can
be rejected without unpicking the promotion. Desktop 8,274 → 10,340 pixels, phone 8,237 → 11,369,
because content that rendered at zero height now always renders.

**Two durable fixes shipped with it.** The build now fails when any of seven must-see sections ends
up nested in a disclosure, proven by perturbation — moving the read back inside exits 1 with a named
failure, reverting exits 0. My first attempt at that proof was invalid because the script died on a
stale artifact before reaching the assertion, which is the same trap this project hit on 2026-08-20.
And the end-to-end smoke test, which had been asserting a page structure that stopped existing over a
week ago, was repaired without touching a line of application code; the suite runs green.

**One thing blocks promotion and it is visible on the page.** The stamp reads "EDITION 2026-08-28"
beside "UPDATED August 17, 2026". `LAST_UPDATED_ISO` is doing four jobs at once: the site's as-of
stamp, the judgment date on the tracked hypotheses, the judgment date on the platform pressure reads,
and the date deriving the "what moved" week window. Recommended fix is to split it, move the site
stamp to 28 August, and pin the judgment dates at 17 August because nobody re-judged them. The fourth
job is the "Jul 6 – Aug 10" window question already owed by the owner, so both should be decided
together.

Twenty commits now sit on `preview` ahead of production.

## Next session — start here (written 2026-09-25, superseding the 2026-09-21 block below it)

**The Fable run (SEC-MARKET-FABLE-001, phase T7) that the previous block described as "active in
parallel" is this session, and it is done. Read the "Current State" section at the top of this file
first — it carries D-70 through D-75, all landed.** The phone-tap publish path is real and live on
production (`main` at `9b98353`): approving a weekly draft, or commenting `publish`, signs and
publishes it; `publish reconfirm` also re-dates stale stances; the weekly job proposes scorecard
updates and flags what is going stale. `docs/active/publish-path-spec.md` v0.2 is the as-built record
and `docs/active/fable-run/RUN-STATE.md` is the full ledger.

**Two things need attention, in order:**

1. **macbook2014 has been down since partway through 2026-09-21 and, as of 2026-09-25, still is.**
   Check it first: `ssh macbook2014 uptime`. If it answers, read `~/gather-logs/receipts/` for
   anything since 2026-09-21T21:08Z. If there is nothing for `2026-w38` (window 2026-09-14 to
   2026-09-20), run `SMP_WEEK_ENDING=2026-09-20 ./scripts/gather.sh` there by hand and watch the
   output — the two fixes that shipped this run (loading `~/.env.local`, pre-approving the shell
   commands the brief needs) are untested against a real unattended pass, only against a hand-started
   one that got partway through before the host dropped off the network.
2. **SEC-054 (the Platform pressure wording fix) is correct on `preview` and wrong on production.**
   It is a one-word promotion once the owner says so; nothing else is blocking it.

**Pull request #2, the unsigned `2026-w37` draft, is still open**
(https://github.com/jessepike/sec-market/pull/2) and predates several schema changes from this run
(the thesis field going optional, the sign-on-approval pipeline, the file allowlist a draft branch
must satisfy). Check it against the current `docs/active/gather-brief.md` and `types.ts` before
approving it — it may not pass the new guards as committed.

**Known residual risk, not fixed by this run and not urgent:** the weekly gather's deploy key can
push to any branch, including `main`, and this private repository has no branch protection to stop
it (SEC-051). The various guards in `scripts/publish-issue.sh` sit beside that open door rather than
closing it. GitHub Pro (~$4/month) would close it; that is the owner's call, not a blocker.
