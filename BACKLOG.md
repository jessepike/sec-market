# Backlog

Canonical work queue for the Security Market Signal Pipeline. Owner decisions live in [decisions.md](decisions.md). Nothing here is authorized merely by appearing in this file unless [README.md](README.md) or [intent.md](intent.md) already authorize it.

## Completed episode

### SEC-002 — Test infrastructure-to-security demand lag

**Status:** completed

Run `SEC-MARKET-SIG-002` to determine whether infrastructure and AI-capex acceleration leads increased cybersecurity demand, over what horizon, and in which domains.

**Requires:**

- A 2023-to-current quarterly baseline
- Infrastructure-supplier and hyperscaler-capex signals
- Cybersecurity financial and demand-side signals
- A 0–8-quarter lag assessment
- Category-shift versus share-shift decomposition
- A public evidence freeze
- A timing posture with falsifiers
- Independent review

**Method:** [market-signal-runbook.md](docs/reference/market-signal-runbook.md)

**Contract:** [market-signal-episode-002.md](docs/episodes/002/market-signal-episode-002.md)

**Result:** completed and independently reviewed; stable lag remains `NO-CALL`

**Not authorized by this work:** production infrastructure or automated posture judgment

## Completed design

### SEC-003 — Human-verified shadow mode exploration

Design a human-verified shadow collection process after the second episode passes.

**Eligibility condition:** satisfied by SEC-002 completion and independent review

**Result:** `SEC-MARKET-SHADOW-001` v0.2 and replay corpus v0.1 accepted; Gate S0 passed

## Completed specification

### SEC-004 — Gate S1 replay implementation specification

Specify—but do not yet run—the bounded seven-row replay implementation.

**Requires:**

- explicit owner authorization to specify;
- implementation choices for runtime and storage;
- replay tests against `SEC-MARKET-SHADOW-CORPUS-001`; and
- no scheduler, live run, or automated promotion.

**Result:** `SEC-MARKET-SHADOW-S1-SPEC-001` v0.2 accepted and independently reviewed

## Pending owner authorization

### SEC-005 — Implement the Gate S1 replay instrument

Build—but do not run—the accepted seven-row replay instrument.

**Hard prerequisites:**

- separate owner authorization for implementation;
- named human verifier and different promotion authority;
- later separate authorization for fixture capture/source retrieval; and
- later separate authorization for the replay run.

**Authorization state:** not authorized

## Completed product MVP

### SEC-006 — Security Market Pulse website

Build a responsive, evidence-linked website using accepted Episode 002 research.

**Result:** implemented under `web/`; build, lint, evidence review, accessibility review, and leadership-product review passed

## Completed product decisions

### SEC-007 — Owner review and deployment

Owner reviewed the live site. Public Vercel deploy is live at https://security-market-pulse.vercel.app and https://securitymarketpulse.com.

**Result:** live at https://securitymarketpulse.com. Local, GitHub `main`, and Vercel match (`8b35e45` / `f780e88`). Deploy only via `git push origin main` with `jesse@keatingpike.com`.

## Active work

### SEC-027 — The weekly issue is the product

Turn the site from a dated research edition into a weekly issue: five sourced lanes, a signed "what we
now think", an archive with a permalink per issue, and the Episode 002 call demoted to a standing
thesis each issue scores against. Domain cards lead with their trigger sentence, which closes the
SEC-019 frame question. Absorbs SEC-021 Phase 3 (the archive).

**Plan:** [weekly-issue-plan.md](docs/active/weekly-issue-plan.md) (`SEC-MARKET-WEEKLY-001` v0.1, WS-B). Spec to follow: `weekly-issue-spec.md`.

**Authorization state:** approach approved (D-62), intent v1.2 accepted (D-63), autonomous build to `preview` authorized (D-64), all 2026-09-03. Spec: [weekly-issue-spec.md](docs/active/weekly-issue-spec.md). Building on branch `weekly-issue`.

**Not authorized by this work:** changing a posture, call or confidence without a signature; any push to `main` except by promotion.

**Status 2026-09-05:** built and merged to `preview` (D-65). Issue `2026-w36` is on the preview site as a labelled unsigned draft with 23 items and a machine proposal; the archive and permalink routes, the standing-thesis block and the trigger-sentence landscape cards are live. The owner signs the first issue by hand per gather-job-spec §6. Promotion to `main` is the owner's call.

### SEC-028 — The Tuesday gather job

A scheduled agent gathers from the catalogued sources every Tuesday, drafts the issue as a pull request
against `preview` with every figure quoted verbatim from a fetched document, and never publishes. A
person reviews, signs and merges. Supersedes SEC-017.

**Plan:** [weekly-issue-plan.md](docs/active/weekly-issue-plan.md) WS-C. Spec to follow: `gather-job-spec.md`. Schedule registered by jobs-agent; any agent definition by Forge.

**Authorization state:** approach approved (D-62), intent v1.2 accepted (D-63), build authorized (D-64), all 2026-09-03. Spec: [gather-job-spec.md](docs/active/gather-job-spec.md). Runs as a Claude Code cloud routine; no jobs-agent or Forge dependency.

**Not authorized by this work:** auto-publishing; editing intent, decisions, the call, a posture or a confidence; scrapers or collectors beyond the one job.

**Status 2026-09-05:** routine `trig_01VeQpLYzXjccqKeSFS1Xgo6` exists, disabled, no connectors, brief v0.2 on `preview`. A one-off dry run (`trig_01La16jZAq9WaQPHyqpUUcyG`, drafting `2026-w35` onto `issue/2026-w35-dryrun` without a PR) fired 2026-09-05; its result is recorded in status.md. Because the first issue covers two weeks (window 2026-08-24 to 2026-09-06), the first useful scheduled run is Tuesday 2026-09-15 for `2026-w37`; a 2026-09-08 fire would stop at "issue exists". The dry run proved the mechanics (checkout, brief, files, gates, commit, push) and failed on network: the cloud environment's egress proxy blocks every public host, so zero sources were read. Before arming, either add the brief's §2 hosts to the environment allowlist at https://claude.ai/code/environments or move the job to a runtime with public-web access (`claude -p` from the repo on Tuesdays, or a macmini launchd job). Owner decision.

### SEC-029 — Distribution

Analytics on, issue #1 emailed to the pilot list by hand, RSS feed and per-issue permalink and Open
Graph image by issue #2, email provider and public list only after four held issues.

**Plan:** [weekly-issue-plan.md](docs/active/weekly-issue-plan.md) WS-D.

**Authorization state:** build authorized 2026-09-03 (D-64) for analytics, feed, permalinks and the JSON copy. Public email not authorized before the 2026-10-08 review.

**Status 2026-09-05:** Web Analytics on; `/feed.xml`, `/issues/<id>/`, `/issues/<id>.json`, `/issues/index.json` and `/issues/lock.json` build and serve on `preview`. The feed carries only published issues, so it is empty until the first signature. Per-issue Open Graph images are SEC-032. The pilot email is still by hand; provider choice is SEC-034.

### SEC-030 — ePlus downstream digest interface

Pulse ships a machine-readable copy of each issue at `/issues/<id>.json`. That file is the whole
interface. The ePlus internal digest, with account triggers and partner framing, is built and owned
in the ePlus channel repo and cockpit. No ePlus surface on this domain; no account data flows back.

**Plan:** [weekly-issue-plan.md](docs/active/weekly-issue-plan.md) WS-E. Handoffs to `eplus-security-advisor` and `eplus-ops` after plan acceptance.

**Authorization state:** approach approved 2026-09-03 (D-62). An `eplus.securitymarketpulse.com` subdomain was considered and declined the same day.

**Status 2026-09-05:** the JSON copy is live on `preview` at `/issues/2026-w36.json` with the issue object and its full evidence records, identity-checked by `verify:dist`. Handoffs sent to `eplus-security-advisor` and `eplus-ops` on 2026-09-05 with that URL shape.

### SEC-031 — Vendor lens

Filter the current issue and the scorecard by vendor or OEM, shareable by URL. Public and
non-confidential. After issue #2.

**Plan:** [weekly-issue-plan.md](docs/active/weekly-issue-plan.md) WS-F.

**Authorization state:** build authorized 2026-09-03 (D-64), in the same pass as SEC-027.

**Status 2026-09-05:** built and merged to `preview`. `?vendors=a,b` filters the issue lanes and the scorecard after hydration, shows "Showing N of M" on each, clears by link, round-trips through the chips, and scrolls as one row at 390. Prerendered HTML is never filtered. Only on `/`; permalinks carry no lens. An in-page vendor picker is SEC-036.

### SEC-009 — Recurring public-signal intelligence

Turn Pulse from a one-shot research edition into a living cybersecurity market-intelligence site.

**Steer from:** [docs/active/sec-009-execution.md](docs/active/sec-009-execution.md) + [leadership-brief-2026-08.md](docs/active/leadership-brief-2026-08.md).

**Shipped:** site, prints, Activity, ops artifacts (D-43).

**Ongoing:** Loop A — Tuesday multi-source gather (funding + M&A + domain checks).

**Also done:** M&A catalog, weekly desk checklist, domain vendor packet. Mapping and desk only — no scrapers.

**Authorization state:** authorized by owner on 2026-08-16 (D-28); parallel mapping authorized 2026-08-16 (D-33)

**Not authorized by this work:** auto-publishing a market call without a human check; inventing sources; using confidential ePlus data

### SEC-013 — Landscape page (Option D)

Rebuild the front page as a standing landscape reference rather than a single dated edition. Accepted direction is Option D (D-47).

**Two tasks, in order:**

1. [landscape-data-spec.md](docs/active/landscape-data-spec.md) — merged to `main`.
2. [landscape-ui-spec.md](docs/active/landscape-ui-spec.md) — Option D, merged to `main` in `57d4f5b`.

**Live:** https://securitymarketpulse.com. The `landscape/ui`, `landscape/data`, and `edition-dated-postures` branches were merged and deleted on 2026-08-19; their preview URLs no longer resolve.

**Authorization state:** design accepted (D-47), one-product pass accepted (D-48), promotion to production approved by the owner and reconciled on 2026-08-19 (D-51 retracts D-49). Merged to `main` and live, verified by query against https://securitymarketpulse.com. Closed.

**Not authorized by this work:** the weekly collection loop, new sources, auto-publishing, any change to the published market call or Episode 002 tags.

### SEC-014 — Visual design pass on the live site

Option D landscape is the accepted visual pass (D-47, D-48). It is merged and serving on production.

**Status:** shipped. No open items; the D-48 promotion record was reconciled on 2026-08-19 (D-51).

### SEC-018 — Integrity pass

Remove the places where the site states something about itself that is not true. Eight items: derive the landscape eyebrow from the data, remove the never-used "needs a source" provenance state, stop asserting a weekly cadence, fix the SecOps print line before promoting SecOps crashes the page, de-duplicate evidence ids in the moved-this-window section, give the two judged rows a stated basis, add a `verify:integrity` build gate, and derive the evidence-library filter options from the records present.

**Spec:** [integrity-pass-spec.md](docs/active/integrity-pass-spec.md) (`SEC-MARKET-INTEGRITY-001` v0.1)

**Status:** complete. All eight items landed as eight atomic commits, merged to `preview` in `c9384de`. Verified independently on 2026-08-20: every acceptance criterion in the spec holds, all five `verify:integrity` checks were observed to fail closed under deliberate perturbation and to pass once reverted, and the rendered diff against production shows only the six expected visible changes. `main` untouched and still a fast-forward ancestor of `preview`.

**Authorization state:** approved by the owner 2026-08-20 (D-52). Implemented by Cursor Composer, verified by the CPO session. Promotion to production is a separate owner decision and has not been made.

**Not authorized by this work:** new content of any kind — no new domains, sources, vendors, figures, print cards, or changed postures. No push or merge to `main`.

### SEC-019 — Make the declared model mean something

Deferred from SEC-018 on purpose, because each item is a judgment or design call rather than a correction.

- Confidence is `medium` on all six domains, so the mark carries no information. Either it varies or it goes.
- `DecisionHorizon` tops out at "Next 1–4 quarters" while intent promises the present through 24 months. The longer horizon is currently unrepresentable in the type.
- Three domain taxonomies coexist and share no identifiers: six posture domains, eight scorecard groups, seven free-text activity labels.
- All 42 print cards render a hardcoded "— no series yet —" placeholder. There is no sparkline behind it. Build it or remove the slot.
- Wire the five unreferenced evidence records — Dell, Vertiv, Broadcom, Meta, Oracle — into the infrastructure and hyperscaler-capex surfaces the method already names. Figures must be verified against each source.
- Intent names relevance as one of four properties every claim preserves. No field or proxy for it exists anywhere.

**Measured 2026-08-25, and it corrects an earlier overstatement in this session.** Six domains carry
a signed, dated posture; four render as landscape cards. I first said the other two "do not render
anywhere," which was wrong. They render inside the collapsed market-read disclosure, on the Tempo
board, which maps over all six. Browser measurement at 1440 and 390 pixels: the string "AI Runtime"
is in the document twice and visible zero times at both widths, and "SecOps" is in the document three
times and visible once, where the one visible instance is the scorecard group header rather than the
posture. So both postures are one click away, not absent. That is the collapsed pattern, not the
buried-and-unlabeled pattern D-54 dealt with.

**The frame question, opened 2026-08-25 and deliberately not answered.** The domain axis is not
discriminating well. Across the six postures there are two distinct posture values (two PREPARE, four
INVESTIGATE), confidence reads MEDIUM on every one, and the horizons collapse to three values with
repeats. Meanwhile the market call, which is the sharpest writing on the site, does not use the domain
frame at all: it is written as do and avoid, with the do items expressed as client triggers. That is
evidence the trigger-and-action frame carries more of the value than the category frame does.

Candidate change, unbuilt on purpose: lead each card with its trigger sentence and demote the domain
name to a label. Cloud currently reads "Cloud Security / WATCH / Qualify residual gaps when capacity
goes live"; the third line is the useful one.

This is not being built because it is a theory about what a reader needs, and the D-58 pilot answers
it more cheaply and more honestly than reasoning does. Changing the accepted Option D front page
immediately before exposing it would also destroy the baseline: reader reactions could not then be
separated from an untested edit. Whichever frame wins determines what the canonical identifiers
should be, so the three-taxonomy reconciliation above waits on the same answer.

**Authorization state:** not authorized. Needs the owner's direction first on what belongs above the fold — six of thirteen top-level sections are currently collapsed behind a click, including the market call, the scorecard, the method and the evidence library.

### SEC-021 — Make the vendor scorecard findable

The owner remembered a per-vendor, per-domain card grid and asked which decision removed it. None
did. All 42 cards were in the served markup, nested inside a collapsed `<details>` four sections
down, so nothing told a reader they existed. Measured in a browser: 42 in the document, zero visible.

**Spec:** [scorecard-visibility-spec.md](docs/active/scorecard-visibility-spec.md) (`SEC-MARKET-VIS-001`). Decision: D-54.

**Phase 1 complete and live in production** (promoted 2026-08-25, D-57). The scorecard is a top-level section under the tracked
hypotheses, its eight domain groups collapse individually so a phone does not receive a 17,000-pixel
wall, the group counts derive from the data, and the placeholder spark that never became a chart is
gone. Phone page height fell from 17,013 to 8,309 pixels; desktop unchanged.

**Phase 2 — not started.** Map each print to the posture it supports, so a reader can move from a
domain card to the evidence under it rather than to an undifferentiated list.

**Phase 3 — not started.** Give the archive real prior editions instead of a single frozen snapshot.

**Rejected in review before it was built:** promoting all 42 cards to the top of the page. That
trades a reader who cannot find the evidence for a reader who cannot find the read.

**Authorization state:** Phase 1 authorized and built. Phases 2 and 3 need an owner go, and Phase 2
overlaps the above-the-fold question that gates SEC-019.

### SEC-022 — Project scorecard and its baseline

An instrument to keep the work honest against `intent.md`, which says plainly that completing agents,
a website or reports does not constitute success.

**Instrument:** [project-scorecard.md](docs/active/project-scorecard.md) v0.2. Decision: D-55.

Outcomes carry an evidence state rather than a score, every rate reads against an exposure
denominator, there is no composite number to optimise, and the per-edition pass/fail health check is
kept separate from the outcome review so shipping discipline is never mistaken for impact.

**Baseline, deliberately unflattering:** every outcome is `not_assessed`, the exposure denominator is
1, legibility fails, and [decision-impact-log.md](docs/active/decision-impact-log.md) has zero entries.

**Both answers settled 2026-08-25 (D-58).** Qualified exposure is a named pilot set drawn from ePlus
account teams and CSPs and from named clients; peers outside the engagement are excluded because
their decisions are not observable. The outcome review is scored by a named human who did not build
this; the edition health check is scored by an agent. Identities are recorded as role, segment and a
pseudonymous identifier here, with the mapping held in the ePlus operating cockpit.

**Still owner-owned:** the actual names. Who is in the pilot set, and who scores the outcome review.
The denominator stays at 1 until the first exists, and H1 and H4 stay self-assessed until the second
does.

**Open work off the baseline:** raise the exposure denominator above 1; close the legibility check;
add lead-time and incremental-value questions to the decision impact log.

### SEC-023 — Phone view

**Fixed 2026-08-22 (D-56) and live in production since 2026-08-25 (D-57).** The phone view had drifted from the accepted Option D design: the
framing sentence, headline and lede all rendered *after* the four domain cards, because the
implementation set `order: 2` on the intro and `order: 1` on the cards inside the phone breakpoint.
Every build gate passed the whole time and nobody had rendered a phone width since Option D landed.

Corrected and now serving: document order restored, the eyebrow hidden above the framing line as the
design has it, the lede tightened, the card judged footer collapsed from three stacked lines to one,
and the missing Scorecard entry added to the navigation. Phone page 8,309 → 8,237 pixels; desktop
identical at 8,274 pixels and its judged footer still two stacked lines, both confirmed by render.

**Open, needs an owner yes or no:** the accepted design uses shorter footer labels — "JUDGED 17 AUG ·
THIS QUARTER · CONF MEDIUM" — which fit one line where the current wording wraps to two. That drops
the year and the word CONFIDENCE from a provenance stamp, so it is a content call rather than a
styling one. Worth roughly another 70 pixels off the phone page.

## Completed mapping

### SEC-010 — Durable signals operation (map only)

How weekly gather → synthesize → human check → post works so this is not a one-off.

**Output:** `docs/active/signals-operating-model.md`

**Authorization state:** mapping authorized (D-33). Build not authorized.

### SEC-011 — M&A source catalog (map only)

Where public cybersecurity M&A actually shows up, and what we can use. Same shape as the startup catalog.

**Output:** `docs/active/ma-source-catalog.md`

**Authorization state:** research authorized (D-33). Collection not authorized.

### SEC-024 — Working-zone hygiene in `docs/active/`

`docs/active/` holds 35 files and nine of them are orphaned: nothing in `BACKLOG.md`, `status.md`,
`decisions.md`, `README.md`, `AGENTS.md` or `docs/reference/` points at them. Since the context map
sends every fresh agent into `docs/active/` as the default working zone, a new session currently
reads mostly finished work.

Orphaned: `activity-edition-draft-2026-08.md`, `domain-coverage-map.md`,
`domain-vendor-signals-2026-08.md`, `durable-signals-job.md`, `signals-week-2026-08-16.md`,
`signals-weekly-checklist.md`, `startup-collection-packet-2026-08.md`, `startup-section-brief.md`,
`vercel-dns-handoff.md`.

Most are plainly finished. Two are not obviously dead despite being unlinked — the weekly signals
checklist and the domain coverage map both sound operationally live — so the move needs the owner to
confirm which two stay before the other seven go to `docs/archive/`.

**Authorization state:** not authorized. Proposed 2026-08-25.

### SEC-025 — AI security coverage

A reader told the owner the AI security coverage is too thin. Measured, they are right twice over.
Seven AI-relevant items exist across the 42-print scorecard and six of them are capital. The single
buyer-side item, Palo Alto Prisma AIRS at 300-plus customers up from 100, is filed under Cloud
security. Three of the seven sit under other domains, none of them misfiled: each print carries one
`group` string and the model cannot say a print belongs to two domains.

**Spec:** [ai-coverage-spec.md](docs/active/ai-coverage-spec.md) (`SEC-MARKET-AI-001` v0.1)

Part 1 adds an optional secondary domain to a print, with a visible primary-group label on any
borrowed card and three new `verify:integrity` checks, because once a print appears twice the group
counts sum to 45 against an eyebrow that says 42.

Part 2 is a bounded gather for buyer-side AI security evidence, the acquisition record, and
AI-native vendors carrying any public number. Capital is deliberately deprioritised: every round we
already hold says the same thing, and the read cannot improve without buyer-side evidence.

**Part 1 complete and on `preview` 2026-08-25.** Three prints now carry `secondaryGroup: 'AI runtime'`
and render in both sections with an "also counted under X" label. AI runtime went from 4 cards to 7,
including Palo Alto Prisma AIRS at 300-plus customers, which is the only buyer-side AI item we hold.
Three new gate checks were each observed to fail with exit code 1 under deliberate perturbation and
to pass on revert.

**Part 2 complete 2026-08-27.** Record: [ai-coverage-gather-2026-08-27.md](docs/active/ai-coverage-gather-2026-08-27.md).
The first attempt died on a session usage limit because the lanes fanned out into their own
sub-agents; the re-run banned that, used fixed target lists, and held. Twelve public companies
checked: none discloses revenue, ARR, customer count, seats or attach rate for an AI security
product. The evidence that matters is one layer down in the same filings, in the acquisition
accounting — F5 paid $145.2M for CalypsoAI and states its revenue was not material, with $114.2M in
goodwill and nothing assigned to customer relationships; Palo Alto paid $634.5M for Protect AI on
the same shape, against an IBM QRadar deal in that filing where $464M of $476M went to customer
relationships. A third F5 deal, SurePath AI at $50.1M closed 2026-06-15, was on no list. Every one
of those figures was re-extracted from the filing by the lead.

**Open and owner-gated: how this gets presented.** The spec held presentation until coverage was
known and coverage is now known. This is the decision that unblocks the rest of SEC-025.

**A gate hole this exposed, not yet closed.** My spec told the implementer to keep primary and
borrowed counts separate, which produced a header reading "0 prints" for AI runtime while the group
displayed a genuine comparable print. Every existing gate passed. The counts now describe what is
actually rendered, but nothing enforces that a group header's number matches the cards in that group.
`verify:integrity` should assert it, since check 8 already renders the component.

**Authorization state:** both parts authorized by the owner 2026-08-25. Findings are re-verified by
the lead against primary documents before anything reaches `preview`.

**Not authorized by this work:** changing any published posture, market call or confidence value;
adding a domain card; changing the landscape frame. Presentation waits until coverage is known.

### SEC-026 — the Identity card's CyberArk watch item cannot resolve

CyberArk filed Form 15-12G on 2026-02-23 and no longer trades or files; its investor pages redirect
to Palo Alto Networks' Idira platform. The Identity domain card in `web/src/data/domains.ts` carries
the watch item "Palo Alto vs CyberArk mix," which is now unanswerable as written because the two are
one filer. Its sibling watch item, "First disclosed agentic-identity revenue," is also harder than
when it was written: all four identity vendors checked disclose nothing and one has stopped filing.

Rewording a watch item on a published card is a judgment change, so it needs the owner rather than a
silent edit. Surfaced by the SEC-025 gather.

**Authorization state:** not authorized. Proposed 2026-08-27.

## Flagged (not authorized)

### SEC-012 — Orphaned signals data

`web/src/data/signals.ts` (`marketSignals`) and `MarketSignal` in `types.ts` lost their only consumer when `SignalFeed` was removed. Real evidence-linked content — wire into UI or retire with a logged decision.

**Status:** resolved — retired 2026-08-19. Content superseded by Activity board and landscape what-moved; array removed.

### SEC-015 — Lock past editions against silent edits

`web/src/data/edition.ts` is append-only by convention. Two build gates check the current edition snapshot, but nothing stops editing a shipped edition snapshot. Extend the `verify-panel.ts` SHA-256 pattern.

**Status:** partial — `verify-edition.ts` added (locks full editions array hash).

### SEC-016 — Print cards vs table presentation

Commit `727ce6a` restored vendor print cards on `main`, partially reversing the prints-table conversion. Resolve before the next public share.

**Status:** resolved by landscape merge — print cards remain in collapsed scorecard section per D-48.

### SEC-017 — Weekly refresh loop

Make the tracked layer actually refresh weekly. Separate from SEC-013 on purpose.

**Status:** superseded by SEC-028 on 2026-09-03.

### SEC-008 — Account conversation prompts

Reconsider account-facing prompts only after the core monthly scorecard, recency model, and domain coverage are trusted.

**Status:** parked by owner feedback; removed from the MVP website

### SEC-032 — Per-issue social preview images

Each `/issues/<id>/` page shares the site-wide OG image. A per-issue image carrying the read and the
week would make a shared permalink recognisable in Slack and email. Generate at build from the issue
data; no design tooling.

**Status:** flagged 2026-09-04 during the weekly-issue build. Not authorized.

### SEC-033 — `verify:issue` check 12 and period labels

Check 12 treats bare digits inside quarter and fiscal labels ("Q2 FY2027", "M12") as numeric claims
and fails a headline that carries one. The 2026-w36 draft worked around it by keeping period labels
out of headlines. Decide whether to allow-list period-label patterns or keep the rule as is and say
so in the gather brief.

**Status:** flagged 2026-09-04. Not authorized; do not weaken the check without a decision.

### SEC-034 — Email provider for the pilot list

The pilot issue is sent by hand from the owner's mailbox until four issues have held (D-64,
SEC-029). Choose a provider only after that: one that takes the `/issues/<id>.json` copy, keeps the
list private, and needs no tracking pixels.

**Status:** flagged 2026-09-04. Decision at the 2026-10-08 review.

### SEC-035 — Archive rows as a real table

`IssueArchive.tsx` lays each issue out as a flex row of spans. A `<table>` with column headers would
read better in a screen reader once there are several issues. Small and reversible; do it after the
second issue exists so the table has more than one row to justify it.

**Status:** flagged 2026-09-04 by the page-build operator. Not authorized.

### SEC-036 — Vendor picker for the lens

The vendor lens (SEC-031) is driven by the URL alone: a reader can remove or clear vendors from
the control but cannot add one without editing the address bar. An in-page picker listing the
scorecard's vendors would make the lens discoverable. Net-new surface; needs a product decision.

**Status:** flagged 2026-09-04 by the lens operator. Not authorized.

### SEC-037 — Local e2e and the analytics script

Against a local `vite preview`, the `@vercel/analytics` tag requests `/_vercel/insights/script.js`;
newer Vite preview servers answer that path with the SPA index instead of a 404, so the page logs
"Unexpected token '<'" and the suite's zero-page-errors assertion fails on nine tests. Against the
live preview the script exists and the suite is green. Route that path to an empty script in the
Playwright config when `E2E_BASE_URL` is unset, or drop the tag from local builds.

**Status:** flagged 2026-09-05 by the second fix operator. Small; do it with the next test change.

### SEC-038 — Make `verify-issue.ts` unit-testable

The issue gate is a plain script with no exported functions, so its validators (the network-anchor
body check, the date rules, the tokenizer's callers) can only be proven by perturbation runs.
`verify-dist.ts` already exports its checks and is exercised by a fixture test. Bring the issue gate
to the same shape. Also note the feed parser's entity and attribute checks do not cover CDATA or
DOCTYPE, which the writer never emits today.

**Status:** flagged 2026-09-05 by the final fix operator. Not authorized.

### SEC-039 — Durable weekly pipeline

Sunday-afternoon cadence, a runtime that can reach the web (allowlist or local runner chosen by a
probe), run receipts with alerts, a daily site probe owned by jobs-agent, a fifteen-minute signing
pass, a post-promote check, source alternates.

**Spec:** [durability-spec.md](docs/active/durability-spec.md) (`SEC-MARKET-DURABLE-001` v0.1).

**Authorization state:** proposed 2026-09-07; owner decisions listed in spec §12. Not yet authorized.

### SEC-040 — A frontier lane

A weekly fifth lane on AI-frontier security developments (model and agent capabilities that move
security demand, frontier-lab security disclosures, major incident reports), sourced and quoted like
the other four. The ePlus-relative reading of it belongs in the ePlus channel digest, not here. A
daily cadence is out: it would optimise output volume, which the intent forbids.

**Authorization state:** idea 2026-09-07; needs an owner decision on scope and a data-model change
(the `Lane` type has four values). Not authorized.

### SEC-041 — Triage the category-compression intake

Ten documents from an owner exploration on 2026-09-09 landed in
`docs/inbox/2026-09-09-category-compression/` with an intake note. Two things to decide, separately:
whether the vendor claims on Cloudflare, Fortinet, SentinelOne, Varonis and Rubrik enter the next
gather packet as candidate card updates, and whether the structural lens (barbell market, category
compression into outcome loops, ecosystem as the unit of analysis) becomes a proposed market read for
the owner to sign or reject. The twelve-item hypothesis register is the likeliest durable piece.

**Authorization state:** intake only, 2026-09-09. Nothing on the scorecard or the read changes until
the owner signs.

### SEC-043 — Correct the two mislabelled figures in issue `2026-w36`

The signed issue gives Zscaler's $898.2M and Palo Alto's $3.41B as fiscal-year revenue. Both are
fourth-quarter figures (evidence records `W36-15`, `W36-19`). Live on production. Proposed text and a
mechanism that leaves the locked issue untouched (an append-only `corrections.ts`, a note beside
each item, a `/corrections/` page) are in `docs/active/fable-run/drafts/correction-2026-w36.md`.
Found by the external review on 2026-09-20.

**Status 2026-09-20:** the owner approved the text and the mechanism (D-68). Built and merged to
`preview` (7535fc4): `web/src/data/corrections.ts`, a dated note beside both items, `/corrections/`,
`/corrections.json`, a `corrections` field in the per-issue JSON, a feed entry, and a
`verify:issue` gate that fails a fiscal-year label over a quarterly source. The locked issue file
is untouched. It reaches production when the owner promotes `preview`. Noted and not built: a
correction cannot itself be marked as amended later; the list is flat and append-only.

### SEC-044 — Validate what a figure means, not only that it appears

**Status 2026-09-21: built.** `web/scripts/verify-prints.ts` (npm script `verify:prints`, in the
`build` chain) compares every scorecard print with the evidence it cites on company or segment,
period, and value/units together; the comparison logic is a pure module
(`web/src/data/printChecks.ts`, `web/src/data/printPeriod.ts`) with data tests
(`web/tests/print-checks.test.ts`), including a deliberately wrong period label and a value absent
from evidence, both of which fail. Metric has no structured field on `EvidenceRecord`, so that
dimension is always reported "not-checkable" rather than guessed — see the module's own comments;
the same gap means the check cannot tell a balance metric (e.g. ending ARR) from a flow metric
(e.g. revenue), which matters because a quarter labelled a fiscal year is a real mistake for a flow
and a probably-fine convention for a balance, since a balance's quarter-end and year-end values
coincide. One print, `print-crwd-cloud`, is listed on `web/src/data/printsUnverified.ts` for this
exact reason (dated, shrink-only against `web/scripts/prints-unverified-baseline.json`) — its
"FY26" label against a quarterly ending-ARR record is not a confirmed defect, only a case the check
cannot resolve on its own, flagged for the owner to confirm or relabel. The figure-meaning check is
the precondition SEC-045 needed and is now in place.

### SEC-045 — The issue pipeline never writes back to the scorecard

`prints.ts` still carries April-to-June figures for CrowdStrike, Zscaler, SentinelOne, Okta, Rubrik
and Palo Alto while issue `2026-w36` has August-to-September figures for the same companies
(`docs/active/fable-run/content-inventory.md`). **Still open:** the gather job itself does not yet
write `prints.ts` updates. `docs/active/gather-brief.md` §3 step 5 now instructs the job to update
the matching scorecard entry for each supplier print in the window, from the same evidence it
gathers, and run `verify:prints` (SEC-044, now built) before opening the pull request — but no
gather run has exercised that step yet. `tone` is scoped to compare a supplier only against its own
previous figure on the same metric.

**Also built 2026-09-21 (publish-path-spec.md §4.2, same task as SEC-044):** `web/scripts/stale-report.ts`
(npm script `report:stale`, pure logic in `web/src/data/staleReport.ts`, data-tested in
`web/tests/stale-report.test.ts`) prints every judged claim older than 45 days and every scorecard
print whose period ended more than 150 days ago, oldest first, plus a "period not understood" list
for anything the parser cannot place. `docs/active/gather-brief.md` §3 step 6 now has the job paste
its output under "Going stale" in the pull request body. No SEC number of its own; tracked here
because it shipped alongside SEC-044/045.

### SEC-046 — Buyer brief

What a development means for someone who buys from these suppliers: continuity, renewals,
consolidation, what to ask the supplier. The external review called it the product's missing
centre (`docs/active/product-core.md` section 10). A first machine draft for one domain is at
`docs/active/fable-run/drafts/buyer-brief-network-sase.md`. It is judgment, so it is the owner's to
edit and approve. Not published and not on the site.

### SEC-047 — Distress and financial-position signals

Debt, layoffs, shutdowns. The owner asked for these by name on 2026-09-20. Sources and a five-rung
signal ladder are researched in `docs/active/fable-run/research/11-distress-signal-sources.md`.
Rule from that research: never say more than a named source said, and take a media lawyer's advice
before publishing distress claims regularly. Not built.

### SEC-048 — Declared coverage list and reader-facing disclosure

Six inherited domains leave endpoint and managed security services with no home. Publish a bounded
supplier list, how suppliers are chosen, that partners and competitors are held to the same
evidence standard, and the author's professional role. Both are the owner's wording to decide
(`docs/active/product-core.md` section 10, points 2 and 3).

### SEC-049 — Automation: runtime, channel, cadence

**Status 2026-09-20: mostly answered by D-70, built by a parallel session.** The weekly gather runs
under launchd on macbook2014 every Tuesday at 07:00, `.github/workflows/gather-pr.yml` opens the pull
request, GitHub's own mobile notification is the owner's one tap, and
`.github/workflows/freshness.yml` watches the live site daily. One owner step remains there: an
interactive `claude setup-token` on macbook2014.

The Fable run's webhook notification action (`notify-decision.yml`) is superseded by that design and
was never pushed. Its branch and worktree are removed; the file is kept for reference at
`docs/active/fable-run/evidence/notify/notify-decision.yml.txt`. The owner does not need the
`workflow` token scope or a Slack webhook.

Still open from `docs/active/fable-run/automation-plan.md`: what may publish without the owner
(`docs/active/product-core.md` section 6), the duplicate and link-liveness gates, and writing issue
figures back to the scorecard (SEC-045) behind the figure-meaning gate (SEC-044).

### SEC-050 — Smaller items deferred by the Fable run

- Order lane items by consequence, not by date (belongs with SEC-027)
- Keyboard shortcuts and a command palette
- A "late" label when the promised cadence is missed (not possible on a static site without a
  build-time clock rule)
- Counting fetches by AI agents
- A quarterly scored recap of past calls
- A plain-chromium fallback in `web/scripts/shot.mjs`, which needs Google Chrome and fails in the
  OrbStack VM; `docs/active/fable-run/evidence/baseline/capture.mjs` works there
- Rubric v2.1 still double counts between D1 and D4 and between D3 and D11, and D6 uses item
  counts where a scanning task would be better
- Analytics: Plausible at about $9 a month is the recommendation
  (`docs/active/fable-run/research/12-analytics-options.md`); paid service, owner gate
- Wave 2 of the machine-readable surface (`docs/active/fable-run/agent-surface-spec.md` v0.2)
- After the thesis moved to `/thesis/` (2026-09-20), the "Standing analysis" link is reachable only
  from the front page; `/corrections/`, `/issues/` and issue pages have no link to it. Needs a
  site-wide footer
- Parked by the owner on 2026-09-20: monetization
  (`docs/active/fable-run/monetization-plan.md`) and the employer outside-activity question

### SEC-051 — Lock `main` so only the owner and the publish workflow can move it

Found by the adversarial review of the publish path (2026-09-21). The weekly job on macbook2014
pushes over a read-write deploy key, which can write to any branch including `main`, and a free
private repository cannot protect a branch. The pre-push hook is per clone and stops mistakes, not a
confused or hijacked job. Every guard in `scripts/publish-issue.sh` sits beside that open door.
Options: GitHub Pro (about $4 a month) for branch protection on `main`; or make the repository
public, which also unlocks it and suits a site built on public sources, but exposes the run's
working documents. Paid service or a visibility change, so an owner gate. Recommendation: GitHub
Pro. Related residual: on an approving review GitHub runs the pull request's own copy of
`publish-issue.yml`; the `publish` comment always runs the default branch's copy.

### SEC-052 — Promote everything on `preview` from the phone

Out of scope for D-73 on purpose (`docs/active/publish-path-spec.md` section 5). A `promote`
comment would move site work the owner has not looked at. Revisit only together with a way to show
him the preview render in the same notification.

### SEC-053 — A structured event date on point-in-time evidence

Found by the scorecard check build (2026-09-21). A few point-in-time figures carry their date only
in free text, so `verify:prints` falls back to a text search, and it cannot tell a balance (ending
ARR) from a flow (revenue) because evidence has no structured metric field. Needs fields added to
`web/src/data/evidence.ts`. One entry, `print-crwd-cloud`, waits on this or on the owner's word in
`web/src/data/printsUnverified.ts`.

### SEC-054 — Platform pressure fallback sentence is wrong for most rows (owner wording needed)

**Status:** done on `mon/pressure-wording`, built to `preview` only, waiting on the owner's word to
promote to `main`.

Found by the blind score of 2026-09-21 and confirmed against the live page.
`web/src/data/platformPressure.ts` gave every absorbed supplier outside Identity the sentence
"Cloud security absorbed into a hyperscaler. Watch what it does to the specialist gap." That was
right for Wiz under Google and wrong for Protect AI under Palo Alto Networks and for the two F5
rows (CalypsoAI, SurePath AI): neither acquirer is a hyperscaler and all three targets are AI
security, not cloud security.

Owner-approved wording (D-75, 2026-09-21) is built and tested. The acquirer/target decision reads
from an explicit, documented hyperscaler list (Alphabet, Google, Microsoft, Amazon, AWS) and the
row's own `VendorPrint.group`, never string-guessing in a component
(`buyingInWording` in `web/src/data/platformPressure.ts`). Every non-Identity buying-in row today
falls inside one of the three approved cases; none needed to be left alone. Each reworded row's
JUDGED stamp now carries its own 2026-09-21 date rather than the shared August date, done by
passing an override into the existing `judged()` helper — no reconfirmation record was used, since
a reworded claim is a new judgment, not a reconfirmation.

A correction (`C-2026-09-21-01`) is published at `/corrections/`, naming Palo Alto Networks/Protect
AI and F5/CalypsoAI and SurePath AI and the corrected sentence. It has no `issueId` because it
corrects the standing Platform pressure table, not a published issue — `Correction.issueId` is now
optional to allow that, and the existing 2026-09-20 issue correction renders exactly as before. No
inline "CORRECTED" banner was added beside the reworded rows: issue items keep their original wrong
text and get a note added beside it, but Platform pressure rows are corrected in place, so the two
correction UIs are not the same shape and forcing them to match would be a new design call, not a
natural reuse. Flagging this rather than building it (scope discipline).

`web/src/data/meta.ts`'s `LAST_UPDATED_ISO`/`LAST_UPDATED_DISPLAY` moved to 2026-09-21 to match — it
drives the as-of stamp, the sitemap `lastmod`, and the JSON-LD dates, and this is a real site
update, not free text.

Full test suite (`npm test`: lint, 199 data tests, build+verify, e2e) passes. Visual review done —
see `docs/active/fable-run/evidence/pressure/report.md`.

### SEC-055 — The two largest score gains left (from `docs/active/fable-run/score-2026-09-21.md`)

- Mark which weekly items matter most to a security leader. Decision value carries the most weight
  in the rubric and sits at 2 of 5 because a plain list gives no signal of consequence (relates to
  SEC-027 and the ordering item in SEC-050).
- A short note on who the author is, including that he works for a security reseller and
  integrator, which the scorer puts at trust 2 to 4. The employer is not to be named in this
  repository; the wording is the owner's.

## Not authorized

- Partner-risk-first sequencing
- Varonis backtest as governing acceptance gate
- T0–T5 collapsed evidence/inference/action score
- West/NorCal-first core delivery
- Universal AI-security platform call
- Production infrastructure or broad automation
- Reproducing or modifying CISO Advisory ontology or vendor catalog

### SEC-042 — Weekly destination and monetization run

Turn the site into a place CISOs, investors, and security leaders return to weekly, and give it a
monetization model. Three parts: a thesis that visibly develops week over week, a first-screen and
information design rebuilt against a researched scoring rubric, and a machine-readable surface that
treats an AI agent as a first-class reader.

The run brief is `docs/active/fable-run-brief.md` (`SEC-MARKET-FABLE-001` v0.1), written for Fable
5.1 as coordinator with subagents on the cheapest model that fits each task, worktrees per stream,
Vercel branch previews, and a resumable run state at `docs/active/fable-run/RUN-STATE.md`.

**Authorization state:** the brief is owner-approved as a build brief, 2026-09-19. The gates inside
it are still owner-held — no promotion to `main`, no paywall or payment provider, no signed thesis,
no `intent.md` amendment, no robots policy change without an explicit yes.

**Known precondition, recorded honestly:** the weekly cadence is not running. `2026-w36` is an
unsigned draft, the gather routine is disabled, and the exposure denominator is 1. A paywall in
front of a site that does not publish is worth nothing, so cadence sequencing belongs inside this
run's plan rather than after it. SEC-027, SEC-028 and SEC-039 carry the cadence work itself.

### SEC-020 — Accuracy and traceability sweep

The owner's standard is 100% certainty that everything shown is accurate, current, and traceable to a source a reader can check. Opened 2026-08-20.

**Desk audit complete.** 150 displayed figures checked against the evidence records they cite: 141 fully supported, 8 partial, 1 unsupported. Three defects were corrected the same day (see below). The rest need a source, not a judgment.

**Fixed 2026-08-20:**

- `act-oasis` claimed Cyera raised $600M "eight weeks earlier". No cited source states a week count, and the gap between the two records' own dates is 48 days. Now reads "weeks earlier", matching what evidence D22 actually says.
- `print-panw` attributed the whole headline-versus-organic gap to CyberArk. Evidence C2 names CyberArk *and Chronosphere*. Corrected.
- `marketCall` quoted Cisco networking orders +40% and Zscaler organic ARR +21% without citing A2 or C4, the records that prove them. Both added. Separately, `chartEvidenceIds` cited C6b (Cisco) although the security composite in `derivePanel.ts` is a median of CrowdStrike, Okta, Fortinet, Zscaler and Check Point — no Cisco. Removed from the chart citations; it stays on the market call where it belongs.

**Open — needs a source or an owner answer, not a guess:**

- The Activity board states "Window: Jul 6 – Aug 10, 2026" while four items predate it and none reach the end date. It is unclear whether this describes a *collection* window (in which case background items are outside it by design and the wording should say so) or an event-date window (in which case it is wrong). Do not rewrite it until that is settled.
- `edition.ts` claims the activity window covers RoS issues #252–#256. Only #254 and #256 are cited anywhere in the evidence set. Verify before the next edition.
- `print-varonis` sources its "headline 52%" from evidence C8b's `limitations` field rather than its excerpt; `print-secuvy` and `act-secuvy` source the "Seed" label from a structured attribution field, not the excerpt. Defensible, but both should be confirmed against the primary release during the source sweep.
- Latent, not currently visible: `trackedPrintEvidenceIds()` resolves print-line tokens by prefix, and `print-crwd-cloud` precedes `print-crwd` in the array, so a bare "CrowdStrike" token would silently bind to the Falcon Cloud segment (C13) rather than total ending ARR (C1). The SecOps print line now contains exactly that token. It does not fire today because SecOps is not a landscape card — but promoting SecOps is under active consideration and would mis-cite on the first render. Fix the resolver before any promotion.

**Source sweep pass one complete 2026-08-20.** All 71 canonical sources checked by six parallel
agents on three questions each: does the link resolve, is every figure and clause in the stored
excerpt actually on that page, and is there any sign the page was corrected or restated. Results:
39 exact, 5 close, 4 drift, 23 unverifiable (recounted from per-record rows; one agent's own summary line miscounted its table). Full record at
[docs/audits/2026-08-20-source-verification.md](docs/audits/2026-08-20-source-verification.md).

**No figure on the site contradicts its source.** Every drift is a missing source rather than a
wrong number.

**The sweep initially overstated the defect and was corrected the same day.** Agents were fed only
each record's top-level `canonicalUrl`, but the schema also carries a `sourceAttributions` array
with a per-source `canonicalUrl` that `EvidenceDrawer.tsx` already renders and seven records already
use. Five records reported as drift (B3, D7, D10, D11, D12) were correctly cited all along. The real
defect is six records, not eleven.

**Fixed 2026-08-20** — `sourceAttributions` added, each URL independently located and quoted
verbatim from the primary document before use:

- A3 Arista: the $1.351B comparison now attributes Arista's 2023-05-01 Q1 2023 release.
- A5 Vertiv: orders +252%, book-to-bill 2.9x, backlog $15.0B now attribute the Q4 2025 exhibit
  (2026-02-11), which states them verbatim.
- B1 Microsoft: "Customer demand continues to exceed available capacity" now attributes the FY26 Q4
  earnings call, which is where the CFO said it, using the same `aka.ms/transcriptfy26q4` link D11
  already uses for that document.

**Closed 2026-08-20 — all six.** C2 attributes the Q3 FY2026 investor deck (slide 3) for the
excluding-acquisition growth rates. C7 attributes Okta's Q1 FY2027 posted commentary for the 107%
net retention figure. D6 attributes Marsh for both halves — the Q2 2026 US rates page and the
twelve-controls page.

A caution recorded with them: the source hunt recommended deleting C2 and C7 as unverifiable,
because I told it in the prompt that they claimed a quarter ended 2026-07-31. They do not; both
correctly state the quarter ended 2026-04-30. The agent reasoned correctly from a false premise I
supplied and produced a well-evidenced recommendation to remove two accurate records. D9 and D10
were flagged the same way and are also fine.

**Still unreadable — 11 records, all host-side.** Eight investor-relations timeouts, two BusinessWire
403s from Akamai, one Incapsula bot challenge on Cato which must not be bypassed. Broadcom loads but
serves a JavaScript shell that a fetcher cannot read; a browser would resolve it. Fortinet was
separately confirmed healthy in a real browser. None of these are dead links and none are known
defects.

**Owed and not built — the durable fix.** `verify:integrity` should fail the build when a record's
excerpt spans more than one organization or economic period and the record carries no
`sourceAttributions`. All six defects would have been caught at authoring time. This replaces the
earlier data-model recommendation: no schema change is needed, because the field already exists and
already renders. It is not being enforced.

**Pass two complete.** The recoverable records were re-fetched with the method that worked (SEC.gov's
documented identified-User-Agent policy, `pdftotext` on PDFs, a browser user agent on investor-relations
hosts) and a primary source was located for each genuinely unattributed claim. Eleven records remain
unreadable for host-side reasons only, listed above.

**Authorization state:** authorized by the owner 2026-08-20. Fixes above already applied; the source sweep is scoped and awaiting a go on full versus partial.
