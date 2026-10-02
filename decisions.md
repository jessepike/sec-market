# Decision Log

Append-only. Record owner and project decisions that shape direction. Do not edit past entries; supersede with a new entry.

---

**D-1 · 2026-08-15 — Governing Intent accepted (`SEC-MARKET-001` v1.0).**

Gate 1 passed. Human Acceptance and AI Readiness recorded in [intent.md](intent.md). Public, publishable initial core; national and global observation; transparent calibrated judgments. Partner-risk-first Phase 1 from the build spec is not authorized.

**D-2 · 2026-08-15 — Outcome Architecture accepted provisionally (`SEC-MARKET-OA-001` v0.1).**

Gate 2 passed — provisional. Minimum causal architecture in [outcome-architecture.md](docs/reference/outcome-architecture.md).

**D-3 · 2026-08-15 — Manual decision episode selected (`SEC-MARKET-G3-001` v0.1).**

Gate 3 passed — provisional. Intervention rationale in [intervention-selection.md](docs/reference/intervention-selection.md).

**D-4 · 2026-08-15 — Initial decision contract sealed (`SEC-MARKET-DC-001` v0.1).**

AI data security and governance vendor landscape pilot completed. Contract in [decision-contract.md](docs/reference/decision-contract.md).

**D-5 · 2026-08-15 — Episode 001 decision: Conditional PREPARE (`SEC-MARKET-SIG-001` v0.2).**

Question: Are agents becoming a consequential cybersecurity action surface quickly enough to require preparation?

- Organizations with current or planned material agent exposure: attach one bounded existing-control assessment to the relevant approval event
- Organizations without material exposure: remain in INVESTIGATE
- No standing program, specialist-platform motion, or broad procurement authorized

Research freeze: 2026-08-15. Independent review passed. Packet authority: [market-signal-episode-001-change-manifest.md](docs/reference/market-signal-episode-001-change-manifest.md).

**D-6 · 2026-08-15 — Next authorized action: repeatability test.**

Run one materially different cybersecurity market-signal episode before any collection/normalization mechanics or production infrastructure. Identity is a candidate domain, not automatic for market-timing.

**D-7 · 2026-08-15 — ADF v2 project initialization.**

Repository scaffolded per ADF Folder Structure v2: root control surfaces, `docs/` lifecycle folders, workflow directories. Governance and episode packet promoted to `docs/reference/`; historical workflow and build specs to `docs/archive/`.

**D-8 · 2026-08-15 — Episode 001 reclassified as thematic validation.**

Owner review found that Episode 001 did not test the original core thesis that infrastructure, investment, financial, and demand signals can reveal future cybersecurity demand. The accepted Governing Intent already contains that thesis, so no intent-version change is required. Episode 001 remains a valid frozen thematic artifact but is not evidence that the core signal model or cross-domain repeatability has been validated. Reconciliation: [intent-reconciliation-2026-08-15.md](docs/active/intent-reconciliation-2026-08-15.md).

**D-9 · 2026-08-15 — Episode 002 infrastructure-to-security lag question authorized.**

Owner acceptance: “agree. proceed.”

Question: Is the current infrastructure and AI-capex cycle producing a measurable leading signal for increased cybersecurity demand, over what horizon, and which security domains are likely to capture it first?

Episode contract: [market-signal-episode-002.md](docs/episodes/002/market-signal-episode-002.md). Production automation remains unauthorized.

**D-10 · 2026-08-15 — Episode 002 decision accepted after independent review (`SEC-MARKET-SIG-002` v0.2).**

- Infrastructure and hyperscaler investment remain broadly accelerating.
- A stable infrastructure-to-security lag is `NO-CALL`; the public window cannot support an exact band or causal claim.
- Domain momentum differs, but infrastructure causality and “which domain captures first” remain `NO-CALL`.
- Use infrastructure activation as an account qualification trigger.
- Bounded readiness is appropriate only where cloud/AI capacity, sensitive data, machine identity, network refresh, or SASE displacement is becoming operational.
- No broad cybersecurity-boom narrative, vendor selection, procurement, or production automation is authorized.

Evidence, baseline, quarterly panel, source manifest, and accepted brief are under [docs/active/](docs/active/). Evidence, strategy, and practitioner reviews passed.

**D-11 · 2026-08-15 — Shadow-mode eligibility reached; authorization still required.**

The manual method has now been exercised across two materially different episodes. Collection and normalization mechanics may be proposed for human-verified shadow mode, but no design or build begins without a separate owner decision. Posture judgment remains human-steered.

**D-12 · 2026-08-15 — Reconciliation metadata and current authority registered.**

Owner authorization: “agree. proceed.”

The owner-authorized reconciliation required a metadata-only update to `intent.md`: `Last reconciled`, the reconciliation-event pointer, current operational validation, and fresh-agent context now identify `SEC-MARKET-RECON-001` and the completed Episode 002 packet. Governing Intent `SEC-MARKET-001` remains version 1.0; purpose, outcome, beneficiaries, boundaries, assumptions, state register, and dual acceptance are unchanged.

Current supporting authorities:

- `SEC-MARKET-SIG-MAN-002` — Episode 002 v0.2 packet and correction authority
- `SEC-MARKET-RUN-VAL-002` — second-domain validation overlay for frozen runbook v0.2

These records preserve the frozen Episode 001 packet while making current handoff state explicit.

**D-13 · 2026-08-15 — Human-verified shadow collection design authorized.**

Owner selection: “design of a human-verified shadow collection process.”

Authorization was limited to design. It did not authorize a collector, storage implementation, replay, live cycle, scheduler, database, publication, or automated evidence promotion.

**D-14 · 2026-08-15 — Shadow collection design v0.2 accepted; Gate S0 passed.**

`SEC-MARKET-SHADOW-001` v0.2 and `SEC-MARKET-SHADOW-CORPUS-001` v0.1 passed independent architecture, governance, and operator reviews.

Version authority: `SEC-MARKET-SHADOW-MAN-001`.

The accepted design:

- limits the first slice to seven primary financial facts;
- requires human-only verification and a different human promotion authority;
- makes blind bulk promotion structurally invalid;
- preserves source, definition, omission, and failure provenance;
- writes only append-only shadow evidence;
- prohibits automated posture, publication, and run closure; and
- keeps S1–S3 manually triggered.

The next possible step is a bounded Gate S1 replay implementation specification. It requires separate owner authorization and assignment of two distinct human identities. No implementation or replay is authorized by this decision.

**D-15 · 2026-08-15 — Gate S1 replay implementation specification authorized.**

Owner authorization: “go.”

Authorization is limited to producing and independently reviewing the implementation specification. It does not authorize:

- implementation or package installation;
- fixture capture or source retrieval;
- assignment of invented human identities;
- the replay run;
- S2/S3 live collection;
- a scheduler, database service, posture change, or publication.

The two distinct human identities remain a hard blocker for implementation and replay.

**D-16 · 2026-08-15 — Gate S1 implementation specification v0.2 accepted.**

`SEC-MARKET-SHADOW-S1-SPEC-001` v0.2 passed architecture, security/governance, and builder/operator review.

The accepted specification selects:

- Python 3.12 standard library in the OrbStack `dev` VM;
- local content-addressed artifacts and append-only/tamper-evident SQLite state;
- seven issuer runs in one replay cycle;
- canonical source and locator recipes for the seven gold facts;
- owner-attested SSH identities with human-only verification and separate promotion;
- signed two-person manual retrieval fallback for blocked IR sources;
- manually triggered commands only;
- atomic promotion and rollback testing; and
- a complete negative/bypass test matrix.

Implementation remains unauthorized. Fixture capture/source retrieval and the replay run each require later separate authorization. The named human verifier and different promotion authority remain unset.

**D-17 · 2026-08-16 — Responsive website selected as the MVP delivery mechanism.**

Owner acceptance: “yes this represents what i want to use.”

The website must maintain attribution and access to supporting research and evidence for users who want to validate or investigate a claim. This promotes the website from Exploring to Decided in Governing Intent v1.1 without changing the project’s purpose or public-evidence boundary.

**D-18 · 2026-08-16 — Project lead and model-routing team established.**

- `sec-market-lead`: Claude Sonnet high, outcome and orchestration
- `sec-market-builder`: Composer 2.5, implementation
- `sec-market-reviewer`: Claude Sonnet high, read-only review
- Claude Opus reserved for consequential architecture or final high-risk review
- One worker by default; at most two concurrent workers unless independent

**D-19 · 2026-08-16 — Security Market Pulse web MVP completed for local review.**

The React/TypeScript static website presents the accepted Episode 002 call, derived market-layer data, domain postures, latest signals, account prompts, and an evidence library with source links, excerpts, limitations, conflicting evidence, and research-artifact access.

Evidence, accessibility, and leadership-product reviews passed after correcting unsupported chart data, evidence navigation, modal accessibility, mobile behavior, and first-screen usability. Local build and lint pass. Deployment remains a later explicit decision.

**D-20 · 2026-08-16 — Emergency model-usage recalibration.**

The Ultra plan’s Other Models pool reached approximately 65% usage one day into the cycle.

Effective immediately:

- Composer 2.5 is the default for all project orchestration, implementation, research, testing, and review.
- GPT, Claude, Gemini, and other external models require explicit owner authorization for each invocation.
- Grok remains disabled until the owner confirms the Cursor Models pool status.
- Only one agent runs at a time unless the owner explicitly authorizes parallel work.
- Direct work is preferred when delegation would duplicate context.
- Automatic council/reviewer/verifier launches are disabled.

The owner must switch the main chat model to Composer 2.5 in Cursor; agents cannot change the parent model from inside a session.

**D-21 · 2026-08-16 — Grok restored to the Cursor Models pool.**

Owner confirmed Grok is included in the same Cursor Models pool as Composer. The emergency Composer-only hold on Grok is lifted.

Effective immediately:

- Lead / orchestrator / thinking: Grok 4.6 (`grok-4.6` frontmatter; `cursor-grok-4.6-high-fast` for Task).
- Worker / implementer / routine review: Composer 2.5 (`composer-2.5` frontmatter; `composer-2.5-fast` for Task).
- GPT, Claude, Gemini, and other Other Models invocations still require explicit owner authorization.
- Single-worker default, no automatic council launches, and no `inherit`/omitted Task models remain in force.

This aligns the project with the global Ultra model-routing rule.

**D-22 · 2026-08-16 — Pulse is a frozen edition with headline-first depth.**

The website is a dated edition, not a live feed. Old data is demoted, not deleted: current on the scorecard, still-true context in Background, superseded prints in evidence only, acquired vendors frozen and annotated.

Capital activity (M&A and funding) shows one section read and five headlines; notes and sources expand on the row. Remaining window events and last-disclosed raises stay collapsed.

Refresh is manual: earnings clusters, material closes or raises, and Watch-next falsifiers. Not a weekly news cycle. Raises and deal values are not ARR.

External reviewers start at [web-mvp-external-review-brief.md](docs/active/web-mvp-external-review-brief.md). Deploy remains a separate track.

**D-23 · 2026-08-16 — External review P1 fixes before public ship.**

Research-artifact links no longer point at a private GitHub repo; packet labels are text and canonical sources stay in the drawer. Network / SASE is capped at PREPARE, matching Episode 002. Tempo and Method guardrails stack on small screens instead of hiding. Scorecard cards are current prints only; no-series names collapse under the group.

**D-24 · 2026-08-16 — Render the written judgment; prints become a table.**

The overview contract fields in `market.ts` (what changed, do/avoid, meaning, confidence, no-call boundaries, change triggers) are now on the page. Prints are a comparable table. The content shell is 1200px for data; prose stays at 68ch.

An edition archive / back catalogue is a product-strategy decision and is not authorized by this change.

**D-25 · 2026-08-16 — Public website deployment authorized on Vercel.**

Owner selected `securitymarketpulse.com` and authorized public hosting. Vercel project `pikeholdings/security-market-pulse` is linked to `jessepike/sec-market` with root directory `web`.

- Production: https://security-market-pulse.vercel.app
- Custom hosts claimed: `securitymarketpulse.com` (apex) and `www.securitymarketpulse.com` (308 to apex)
- DNS remains on Cloudflare (`georgia` / `jerry`). Records must be DNS-only (grey cloud), not proxied.
- First production deploy was a CLI upload of the current working tree.

This authorizes the public static website. It does not by itself authorize auto-publishing judgments without a human check.

**D-26 · 2026-08-16 — `securitymarketpulse.com` DNS cutover complete.**

Two unproxied CNAMEs written on Cloudflare zone `34251ea7b517605f017007f13625555a` to `8406d7f2fc89acd7.vercel-dns-016.com`. Vercel domain config is no longer misconfigured. Apex returns HTTP 200 with a Vercel-issued Let’s Encrypt cert (`CN=securitymarketpulse.com`, SAN includes www). `www` 308s to apex. Title: `Security Market Pulse | Episode 002`.

GitHub `main` was behind the live CLI deploy at the time of cutover.

**D-27 · 2026-08-16 — Owner product review is complete.**

Owner stated the live Pulse site has already been reviewed and that “owner review pending” is stale. `SEC-MARKET-WEB-001` is accepted for use. Remaining work is to keep the site current and turn one-shot research into recurring market intelligence.

**D-28 · 2026-08-16 — Recurring public-signal intelligence is now the job.**

Owner direction: Security Market Pulse is a cybersecurity market-intelligence site, not a finished research paper. It must regularly show what is happening in the market — including new security startups, funding, and M&A — from public sources.

The previous hold that blocked collectors, schedulers, and a signal pipeline is lifted for this purpose. A dedicated signals job will gather public events, reason on them, and turn them into intelligence the site can publish. Auto-publishing a market call without a human check remains out of bounds.

Numbering note: the two 2026-08-16 entries previously both labeled D-23/D-24 are now D-25 (deploy) and D-26 (DNS).

**D-29 · 2026-08-16 — Signals first slice is startups only.**

Owner direction: branch the signals work into a separate session. Do not work M&A yet. First find the public sources for new security startups and see what information we can actually get. A source catalog comes before any collector or scrape.

**D-30 · 2026-08-16 — Prove startup-feed value with the easy set before any custom collection.**

The allowed public sources are enough to test whether a startup feed is worth building. Do not build browser scraping, click-through skills, or other custom collectors until one real packet is useful in an account conversation or on the site.

Value test: one cheap collection packet from the first-week set in `startup-source-catalog.md`. Completeness is not the test. Decision usefulness is.

**D-31 · 2026-08-16 — Production deploys only via local → GitHub → Vercel.**

Owner direction after the first public ship drifted: local, GitHub `main`, and Vercel were three different copies because production was a CLI upload of a dirty working tree.

Standing rule:

1. Preview on the OrbStack dev server.
2. Commit the accepted tree on `main`.
3. `git push origin main`.
4. Vercel builds that GitHub commit (`pikeholdings/security-market-pulse`, root `web`).

Do not `vercel --prod` an uncommitted tree. Do not treat `origin/main` as live until that commit has deployed. After this decision, the scorecard working tree is the git and production source of truth.

**D-32 · 2026-08-16 — Pulse git commits must use `jesse@keatingpike.com`.**

Vercel blocked GitHub production deploys of `90689cc` with `COMMIT_AUTHOR_REQUIRED`: GitHub could not associate committer `jesse@pikeholdings.co` with a user. This repo’s `user.email` is `jesse@keatingpike.com`. Do not change it back to `pikeholdings.co` or the local → GitHub → Vercel path breaks again.

**D-34 · 2026-08-16 — Startup work is a site feature, not another research episode.**

Owner correction: stop calling this an episode. The live site is one published research edition. Startups is a new section of Security Market Pulse.

Sequence: (1) collection packet, (2) owner + lead critique for insights and presentation, (3) a separate design/front-end agent only after the packet is good enough for a sharp San Francisco audience. Do not spin design before that review. World-class bar: if smart operators would dismiss it as a link dump, it is not ready.

**D-33 · 2026-08-16 — Map M&A sources and a durable signals operation in parallel.**

Owner authorized parallel mapping of M&A sources and a durable weekly operation. Site deploy path is already settled (D-31 / D-32).

Two research jobs only:

1. M&A source catalog — where public cybersecurity deal news actually lives, and what we can use.
2. Durable operating model — how gather → synthesize → human check → post repeats without a one-off hero pull.

No collectors, scrapers, schedulers, or auto-posting. Mapping only.

**D-35 · 2026-08-16 — Stand up the weekly desk and widen domain coverage, in parallel.**

The durability *map* exists. The repeating job does not. Owner wants ground made up now, independent of the Fable review and the startups-section design.

Two sessions:

1. Domain coverage — we are thin outside agent governance and identity. Map watch companies and extra lawful sources across Pulse domains.
2. Weekly desk — run the first real gather (funding + M&A from the latest Return on Security post) and leave a reusable checklist.

Still no scrapers, no auto-publish, no site design in these sessions.

**D-36 · 2026-08-16 — Accept the 2026-08-16 review findings for the Activity rewrite.**

Authority: [review-findings-2026-08-16.md](docs/archive/review-findings-2026-08-16.md).

The standing rewrite agent may resolve amounts and rewrite the statements. It may not edit `web/`, ship, build an archive, or change domain postures.

Accepted:

- Zenity is $115M Series C + $10M secondary, not an unresolved conflict.
- Kill the named “barbell” claim.
- This is the next edition of the existing Activity board, not a new Startups section.
- Spine of the read: platforms that just bought identity are now seeding and buying agent control.
- Insight 1 is stage-spread, not formation. Drop “buyers are in pain.” Keyfactor is not part of that sentence.
- Five shared funding + M&A slots. Arcade/CodeIntegrity are “just appeared.” Horizon3.ai is not a lead.
- Public cadence stays the monthly edition. Re-gather RoS 257–258 before ship, not before the rewrite.
- State that capital heat is ahead of disclosed revenue. Keep the agentic-identity revenue falsifier.

**D-37 · 2026-08-16 — Fill domain vendor signals and apply the Fable Activity rewrite, in parallel.**

1. Operator: pull a current public signal for five or six top vendors in each Pulse domain. Names are not enough. Need a print, raise, or deal with source and excerpt.
2. Apply D-36: rewrite the Activity edition (read + five shared slots) and update the live Activity data. Judgment layer is already on the page — do not rebuild it.

No scrapers. No auto-publish of the market call. No new Startups section.

**D-38 · 2026-08-16 — Avoid-line wording: announcements, not deals.**

The judgment layer is now on the page. The Avoid item “Treating 2025 Wiz or CyberArk deals as this month’s demand signal” collided with the Activity board, which correctly shows the **2026 closes** as current capital events.

Accepted wording: “Treating the 2025 Wiz or CyberArk **announcements** as this month’s demand signal.”

The 2025 announce is not this month’s demand. The 2026 close may stay on the board as capital, not spend. Do not treat either as buyer demand.

**D-39 · 2026-08-16 — Next build: put pulled vendor signals on the prints board, and convert prints to a table.**

The vendor pull is accepted as a research packet. Next is to show the five new prints we did not have (Cato, Netskope, Upwind, CrowdStrike cloud, Torq) and turn the prints wall into a dense table. Do not wait on Orca/Aqua. Do not ship the Activity edition to production until RoS 257–258 are re-gathered.

**D-40 · 2026-08-16 — Ship the ungated slice now; hold the Activity edition.**

RoS #256 (Aug 10) is still the latest Security, Funded post. #257–#258 are not published. Sitting on the prints table, vendor rows, judgment layer, and Avoid-line until those issues exist would stall authorized work.

Ship to production: JudgmentBoard, D-38 Avoid wording, five new prints, prints table, Identity coverage collapse (Entra / Ping / PE PAM as one row).

Hold: Activity edition rewrite (`activity.ts` + D19–D29). Re-gather when a newer RoS issue exists, then ship that edition.

**D-41 · 2026-08-16 — SEC-009 execution plan is the steering page.**

No new Governing Intent. `SEC-MARKET-001` v1.1 still governs. The lost-in-the-weeds problem is execution, not purpose.

The lead steers from [sec-009-execution.md](docs/active/sec-009-execution.md). Owner is not in the desk loop unless the published market call would change.

**D-42 · 2026-08-16 — Ship the labeled Activity window now. Do not wait on unpublished RoS issues.**

#257 is 404. #256 (Aug 10) is still the latest Security, Funded post. Holding the edition until a future Monday is how the lead went idle.

Ship the D-36 edition with the window on the page: **Jul 6 – Aug 10, 2026 / RoS #252–#256**. Market call stays frozen. When a newer issue exists, Loop 1 is a refresh, not a gate on first ship.

Supersedes the D-39 / D-40 / D-41 hold that blocked Activity until #257–#258.

**D-43 · 2026-08-16 — Leadership ops artifacts: funding, M&A, domains, dashboard.**

Owner needs plain artifacts for leadership in two days — not scattered research catalogs. Create:

- [intelligence-funding-ops.md](docs/active/intelligence-funding-ops.md)
- [intelligence-ma-ops.md](docs/active/intelligence-ma-ops.md)
- [intelligence-domains-ops.md](docs/active/intelligence-domains-ops.md)
- [intelligence-dashboard-ops.md](docs/active/intelligence-dashboard-ops.md)
- [leadership-brief-2026-08.md](docs/active/leadership-brief-2026-08.md)

Each doc: question answered, sources, refresh cadence, aggregation, signal quality, decisions driven. Multi-source — Return on Security is one weekly source among many. Weekly Loop A (Tuesday gather) runs without owner babysitting.

**D-44 · 2026-08-16 — Fill domain vendor tables on the live site.**

Populate Cloud security and AI runtime print groups; add sourced rows for top vendors per domain from the August operator pass (BigID, Sentra, Securiti, Oak, Hush, Veza, Tines, WitnessAI, Lakera, Orca, Aqua, Wiz, Prisma AIRS, XSIAM). Orca/Aqua get official 2026 GTM or last-disclosed equity — not invented ARR. Rewrite leadership brief in plain English; add decision-impact log template.

**D-45 · 2026-08-17 — Dated domain postures and edition-to-edition delta.**

Give each domain a dated posture, a decision horizon, and the evidence that produced it. Make each edition show what held or moved versus the one before.

This is the C3 + C5 cut: a reconstructable posture a beneficiary can be observed against (B1), without new breadth, new sources, or traffic work. Episode 002 tags do not move. This edition is the opening dated record; the next edition writes the first real delta into `web/src/data/edition.ts`.

**D-46 · 2026-08-17 — The edition delta is derived from an append-only history, never written by hand.**

`web/src/data/edition.ts` holds `editions`, an append-only array. Each record freezes the postures that edition published and is never edited afterwards. Held, Moved, and New are computed by comparing the current snapshot against the previous one, so the page cannot state that a posture held when it moved.

Two build-time gates enforce it. The current edition's snapshot must equal what `domains.ts` publishes — posture, tag, and horizon — or the build fails; this is proven fail-closed by perturbing a horizon and watching the build refuse. A snapshot referencing a domain that is not published also fails.

The 2026-08-16 record is transcribed from the domain data actually published in that edition (`domains.ts` at commit `ab8a6fd`). That edition published a posture and a tag but no horizon, so its horizons are recorded as `null` rather than backfilled. This satisfies C5's requirement to preserve prior states rather than overwrite them, and it removes a fabrication surface: nobody can assert a delta the data does not support.

Rejected: keeping the hand-written `domainNotes` model. It satisfied C3 but not C5, because it retained no prior state and asserted the delta as editorial copy.

**D-47 · 2026-08-17 — The landing page becomes a landscape, not an edition.**

Four directions were drawn. Option D is accepted, desktop and phone. Boards and renders in `.design/`.

The market call stops being the spine of the front page. It is Episode 002's answer to Episode 002's question, and its central claim is `NO-CALL`. The durable product is the landscape: dated postures, what moved, and where platforms are holding, buying in, or being outrun. The infrastructure-to-security thesis moves to a tracked hypotheses section with its falsifiers.

Every claim on the page declares a provenance layer. `tracked` is mechanically refreshed and carries at least one evidence ID, enforced by the type system. `judged` is signed and dated by a person at a stated confidence. `unsourced` is surfaced but not yet tied to evidence. This is what lets a weekly refresh move without a person re-approving the whole page, which was the constraint about to block a weekly cadence.

No "read the edition" call to action. The page is the product. `NextEdition.tsx` stops announcing that editions publish when the evidence moves, because that trains a reader not to return.

Platform pressure is derived from existing sourced records, not hand-authored. Two owner hypotheses recorded 2026-08-17 enter as `TRACKING`, not as claims.

Specs: [landscape-data-spec.md](docs/active/landscape-data-spec.md) then [landscape-ui-spec.md](docs/active/landscape-ui-spec.md). Neither is authorized to implement yet. `edition-dated-postures` must land first.

**D-48 · 2026-08-19 — Landscape preview is one product, and preview URLs are public.**

Owner direction before wider feedback: the `landscape/ui` preview must read as the landscape, not as the landscape plus the old edition. Episode 002, prints, Tempo, and Activity stay in the page, collapsed under “Episode 002 research and the full scorecard.” Do not delete those components.

Also accepted in the same pass:

- TRACKED chips on the four domain cards use the prints on the card. Cloud no longer labels Falcon Cloud / Upwind / Orca / Aqua as Alphabet / Mandiant.
- Remove the “tell me when the next edition publishes” CTA and the edition-era page title.
- Do not say “refreshed weekly” until the weekly loop exists.
- Disable Vercel Authentication on project `security-market-pulse` so the preview URL can be shared without SSO. Production custom domain was already public. Do not merge to `main`.

**D-49 · 2026-08-19 — The D-48 landscape reached production without an approval on record. Recording it as a gate crossing.**

D-48 ends with the words "Do not merge to `main`." Commit `57d4f5b` merged it to `main` at 09:22 the same morning, Vercel built it, and https://securitymarketpulse.com has served the Option D landscape since. No approval for that promotion exists in this log, in `status.md`, or in any session record. Asked directly on 2026-08-19 whether he had approved it, the owner's understanding was that the preview had not been promoted at all.

So the record is: the gate was crossed, nobody signed it, and the owner did not know production had moved. Verified the same day by query — the live host returns the provenance rail, the four domain postures, what-moved, platform pressure and tracked hypotheses, and the removed edition call-to-action is genuinely absent, so what is live is the accepted D-48 state rather than something unreviewed. The outcome is fine. The path was not.

D-48 is not edited. A silently corrected record is one that looks like it was always right, and the instructive part here is that the gate was crossable at all by an ordinary `git push`.

**D-50 · 2026-08-19 — Two long-lived branches: `preview` is the trunk, `main` is production.**

Superseding the ad-hoc "push a branch, get a URL" step in D-31: every change now lands on `preview`, which owns a stable public URL at https://security-market-pulse-git-preview-pikeholdings.vercel.app. `main` is production and moves only by a fast-forward merge from `preview` on an explicit owner yes.

Two properties are the point. The preview URL never changes, so it can be bookmarked and refreshed rather than re-sent every time a branch is born. And because `main` is always a fast-forward of `preview`, production is an exact earlier state of the trunk rather than a parallel history, so "what is live" is answerable with one `git log` instead of a comparison.

At the time of this entry the two surfaces render identically: production and preview differ only by the feedback widget Vercel injects into preview builds.

A `pre-push` hook now refuses a direct push to `main`, because D-49 happened by an ordinary push and a convention that only exists in a document is not a control.

**D-51 · 2026-08-19 — Retracting D-49. The D-48 promotion was approved; what failed was legibility, not authorization.**

D-49 recorded the landscape reaching production as an unapproved gate crossing. That is wrong and is retracted. Asked directly, the owner confirmed the same day: he approved D-48.

D-49 is left standing rather than edited, because a decision log that quietly rewrites its own wrong entries is worth less than one that shows where it was wrong. Treat D-49 as superseded in full by this entry.

What remains true, and is the part worth keeping: for roughly three hours the live site and the owner's understanding of the live site disagreed. The D-48 text ends "Do not merge to `main`", no promotion was recorded in this log or in `status.md`, and when the subject came up the owner's read was that the preview had not been promoted. The approval existed and simply never became visible anywhere a later reader — human or agent — would look.

So the defect was never authorization. It was that "what is live" could not be answered from the repository, only by querying the host. D-50's two-branch model is the response to that and stands unchanged: production as a fast-forward of the trunk makes the live state readable from one `git log`, and the pre-push guard makes a promotion a deliberate act that leaves a trace rather than an ordinary push that leaves none.

The prior session's instinct to verify production by query rather than by document was right, and remains the rule. This entry adds the other half: a promotion is not complete until it is written down.

**D-52 · 2026-08-20 — Integrity pass: the site stops saying things about itself that are not true.**

An alignment audit against `intent.md` found several places where a mark on the page means nothing, contradicts another mark, or would crash if used. The product's whole claim is that every mark is checkable, so these are not cosmetic. Specification: [integrity-pass-spec.md](docs/active/integrity-pass-spec.md) (`SEC-MARKET-INTEGRITY-001`).

Four calls settled in advance so the operator does not have to make them:

- **The "needs a source" provenance state is removed rather than populated.** The top rail advertised three provenance states. The third existed as a full `UnsourcedClaim` interface in the type system, was asserted visible by an end-to-end test, and had never once occurred in the data. A legend advertising a state that cannot happen is the same defect class as an unsourced figure. Removing it is not abandoning the idea — re-adding it is a small change and is expected the first time a real instance appears.
- **Section naming stops asserting a cadence and names its window instead.** The method section said refresh is manual and event-driven, "not a weekly news cycle," while the navigation and the section heading both said "this week." The gather loop is weekly; the edition is not. Naming the window is true under either cadence and survives a skipped week.
- **Domain card print lines use full vendor names.** The SecOps line used ticker shorthand (`S1`, `CRWD`) that resolves against nothing, so the evidence resolver throws for that domain. It has not fired only because SecOps is not on the landscape — and promoting SecOps is under active consideration, which would have broken the page. Full names fix the bug and match what every other card already does.
- **The five unreferenced evidence records stay, and get wired in a later pass.** Dell, Vertiv, Broadcom, Meta and Oracle are real, sourced, and belong to the two thinnest signal families on the site. Surfacing them means authoring figures, which is content work carrying a fabrication risk, so it does not belong in a correction pass. A build check now reports the count and fails if it grows past five.

The through-line is that each of these was true when written and nothing stopped it becoming false. So the pass adds a third build gate, `verify:integrity`, alongside `verify:edition` and `verify:panel`, and every one of its five checks must be observed to fail closed under a deliberate perturbation before the work is accepted. A gate nobody has watched fire is a comment.

Explicitly out of scope, and deferred on purpose: confidence is `medium` on all six domains and therefore carries no information; the decision-horizon type cannot express anything beyond four quarters while intent promises out to 24 months; three separate domain taxonomies coexist and share no identifiers; 42 print cards render a hardcoded "no series yet" placeholder; and six of thirteen top-level sections are collapsed behind a click, which is why the analysis reads as thin. Those are judgment and design calls, not corrections, and they need the owner's direction on what belongs above the fold before anyone writes code.

**D-53 · 2026-08-20 — The integrity pass is promoted to production. Owner approved by typing `PROMOTE=1`.**

`origin/main` moved `ff90978` → `9a75169` by fast-forward from `preview`, and https://securitymarketpulse.com has served that state since roughly 30 seconds after the push. Confirmed by query against the live host, not by reading a deploy log: HTTP 200, and all six expected changes present — the third legend chip gone from the provenance rail, the navigation and heading reading "What moved", the window label reading "WINDOW ·", the HELD row carrying an "Edition delta" basis link, and the landscape eyebrow rendering "four domains" from the data rather than from a hardcoded string. The market call, the vendor prints and the 72-source evidence library are unchanged.

What shipped is `SEC-MARKET-INTEGRITY-001` in full: eight corrections and a third build gate, `verify:integrity`, joining `verify:edition` and `verify:panel` in the build chain.

The gate was not accepted on its author's report. Each of its five checks was perturbed and observed to refuse the build, then reverted — the SecOps print line returned to `S1` shorthand, the HELD row's `basisHref` blanked, a duplicate `C9` injected into a supporting list, a nonexistent `ZZ99` referenced, and the orphan threshold lowered below the true count of five. All five refused. One of those perturbations initially produced no verdict at all because the edit that made it broke the file before the check ran; redone cleanly, it fired correctly. A gate that returns nothing is not a gate that passed, and the difference is only visible to someone who looks.

Recording this entry is the point of D-51. The approval existed there too; what was missing was any place a later reader could find it. `git log origin/main -1` now answers "what is live", and this entry answers "why, and who said so". This commit lands on `preview` and will reach `main` at the next promotion, which is the normal direction of travel for the trunk.

**D-54 · 2026-08-20 — The vendor scorecard was never removed. It was invisible, and it is promoted to a top-level section.**

The owner remembered a grid of per-vendor cards organised by domain and asked what decision had taken it away. No decision had. All forty-two cards were in the served markup the whole time, nested inside a collapsed `<details>` element four sections down, so nothing on the page told a reader they existed. I first reported them as present on the strength of the HTML, which was wrong in the way that matters: being in the markup is not being on the page. Measuring in a real browser returned forty-two cards in the document and zero visible.

Specification: [scorecard-visibility-spec.md](docs/active/scorecard-visibility-spec.md) (`SEC-MARKET-VIS-001`). Phase 1 is built: the scorecard moves out of the collapsed depth section to sit directly under the tracked hypotheses, its eight domain groups are collapsible individually so a phone does not receive a seventeen-thousand-pixel wall, and the group header carries a derived count rather than a hand-typed one. The "no series yet" placeholder spark is gone, since a placeholder that never becomes a chart is decoration claiming to be data.

One idea was rejected in review before it was built: promoting all forty-two cards to the top of the page. That trades one failure for its mirror — a reader who cannot find the evidence, replaced by a reader who cannot find the read. Phases 2 and 3, mapping each print to the posture it supports and giving the archive real prior editions, are specified and not started.

**D-55 · 2026-08-20 — The project scorecard measures outcomes by evidence state against an exposure denominator, and refuses a composite score.**

Instrument: [project-scorecard.md](docs/active/project-scorecard.md). Its job is to keep the work honest against `intent.md`, which says plainly that completing agents, a website or reports does not constitute success. Success is a decision changed, a client conversation supported, a technology or timing choice informed, and reasoning another person can reconstruct.

A first version was drafted and sent to an external model, which took it apart correctly. Scoring an untested outcome as zero implies it was tried and failed; giving credit for enabling work inflates the number the instrument exists to protect; capping the total simply moves the gaming into the outcomes; and I had, unsurprisingly, scored my own most recent work highest. It also caught that I had asserted `intent.md` ranks its beneficiaries when the document presents them as a table with no ordering, and that the first draft missed earliness entirely — which is the project's central thesis.

So v0.2 does four things differently. Outcomes carry an evidence state rather than a score: not assessed, no observed effect, anecdotal, independently evidenced, repeated. Every rate is read against an exposure denominator, currently one, so a strong-looking ratio cannot hide the fact that almost nobody has been shown the work. There is no composite number to optimise. And the per-edition health check is pass or fail on provenance, uncertainty, freshness, legibility and boundary safety, separately from the outcome review, so shipping discipline is never mistaken for impact.

The honest baseline: every outcome is not assessed, legibility fails, and the decision impact log has zero entries. Two open questions belong to the owner and not to me — who scores this independently, and which named people count as qualified exposure.

**D-56 · 2026-08-22 — The phone view is corrected back to the accepted Option D design.**

Rendering the deployed preview at 390 pixels showed the page opening straight into four domain cards with no framing at all. The eyebrow, the headline and the lede all rendered after the cards, because the Option D implementation set `order: 2` on the intro and `order: 1` on the cards inside the phone media query. The accepted design render at `.design/out/option-d-mobile-1of2.png` shows the opposite and shows it clearly: one short framing sentence, then the cards. So this was drift from an accepted design, not a design choice anyone made, and nothing caught it because every build gate passed and no one had rendered the page at a phone width since Option D landed.

Three further phone changes go with it. The eyebrow is hidden above the framing line, which is what the accepted design does. The lede is set smaller so the intro block stays short. And each card's judged footer collapses from three stacked lines to one wrapped line, which is again what the design shows; the desktop footer keeps its two stacked lines, and that must be proven by render rather than asserted. The navigation also gains the scorecard entry it was missing after D-54 made that section top-level.

The rest of the phone page was inspected end to end and is sound. What moved, platform pressure, tracked hypotheses, the collapsed scorecard groups and the corrections invite all read correctly at 390 pixels.

**D-57 · 2026-08-25 — The scorecard visibility work, the phone correction and the source attributions are promoted to production. Owner approved after a rendered before-and-after.**

`origin/main` moved `9a75169` → `4916a95` by fast-forward from `preview`, carrying eighteen commits. This is the first promotion since D-53 on 2026-08-20.

Approval followed the visual review the deploy contract requires rather than preceding it. Production and preview were both rendered at 1440 and 390 pixels, the differences were stated in full, and the owner approved what he had actually seen. Confirmed live two ways: the served markup carries the renamed disclosure and no longer contains the "no series yet" string, and a fresh render of https://securitymarketpulse.com returns 8,274 pixels at 1440 and 8,237 at 390, identical to the preview render at both widths.

What a reader gets that they did not have before. The vendor scorecard is a top-level section rather than forty-two cards buried inside a collapsed block below the author's signature (D-54). The phone page opens with its framing sentence and headline above the four domain cards instead of below them (D-56). The placeholder spark that never became a chart is gone from all forty-two cards. Six evidence records carry the source attributions the 71-source sweep found missing, so every claim on the page names the document that states it.

The desktop page roughly doubled in length, 4,315 pixels to 8,274. That is the honest price of making the evidence findable and it was approved as such, not overlooked.

One ordering change was a judgment rather than a correction and is recorded as such: the frozen provenance line and the closing method-and-corrections block swapped places, so the page now ends on a named person and an email address rather than on a disclaimer. A page whose entire claim is that a human signs the judgments should end on the human.

Still open and deliberately not decided here: the shorter phone footer labels in SEC-023, which drop the year and the word CONFIDENCE from a provenance stamp and are therefore a content call.

**D-58 · 2026-08-25 — Qualified exposure is a named pilot set from two beneficiaries, and the two scorecard instruments get different scorers.**

These were the two questions D-55 left open and explicitly refused to guess.

**Who counts as qualified exposure.** A small deliberate pilot set, named in advance, drawn from ePlus account teams and CSPs and from named clients. Security leadership peers outside the engagement are excluded from the denominator on purpose. Their reactions are worth having and they may read the site freely, but their decisions are not observable to us, so counting them would inflate the denominator with exposure that can never resolve into an outcome. Naming the set in advance is the whole mechanism: a denominator assembled afterwards from whoever happened to reply measures reach, not opportunity.

**Who scores what.** The outcome review is scored by a named human who did not build this. That is the only instrument where independence is load-bearing, because the instrument defines `independently_evidenced` as recorded by somebody who did not build it, and no amount of care lets an author satisfy that definition about his own work. The edition health check is scored by an agent, because its five checks are mechanical and repeatable and H4 in particular is a browser measurement anyone can reproduce; an agent running them every edition is more consistent than a human running them occasionally. The corollary is that the author of an edition never scores its own outcome review, including when the author is an agent.

**How identities are recorded, which follows from the first answer.** Two of the three chosen beneficiary groups are ePlus account teams and named clients, and intent excludes client-identifying and confidential ePlus information from this project while H5 checks for it. The repository is private, so this is a boundary rule rather than a disclosure risk, but it holds either way. This repository records role, segment and a stable pseudonymous identifier: "account team A, West NorCal", "client 3, financial services". The mapping to real people lives in the ePlus operating cockpit, which is the private store built for confidential engagement data. Nothing the instrument needs is lost, because a denominator is a count, a beneficiary tag is a role, and an outcome is a described change, and none of the three requires a name to be true.

Two things remain owner-owned and unanswerable by me: the names in the pilot set, and the name of the human who scores the outcome review. Until the first exists the denominator stays at one, and until the second exists the H1 and H4 health results stay self-assessed and provisional.

Encoded in [project-scorecard.md](docs/active/project-scorecard.md) and [decision-impact-log.md](docs/active/decision-impact-log.md). The impact log also gains the two questions D-55 flagged as missing, asking whether the reader already knew and whether their options were still open, because counting uses is not the same as knowing whether this works.

**D-59 · 2026-08-28 — The AI security coverage gets published as the acquisition read, not as more vendor cards. Posture unchanged.**

A reader said the AI security coverage was thin. It was, and the fix everyone reaches for first — add
more AI vendors to the board — would have made it thicker without making it better, because the
capital rounds already on the board all say the same thing and the site already carries six of them.

The bounded gather (`SEC-MARKET-AI-001` Part 2, recorded at
[ai-coverage-gather-2026-08-27.md](docs/active/ai-coverage-gather-2026-08-27.md)) asked twelve public
companies what they disclose about AI security revenue and got nothing from any of them. That null
result was real and it was also the wrong altitude. The evidence sits one layer down in the same
filings: Palo Alto paid $634.5M for Protect AI, F5 paid $145.2M for CalypsoAI and $50.1M for SurePath
AI, and in each case the filing states the acquired revenue was not material and assigns nothing to
customer relationships. The IBM QRadar transaction in the same Palo Alto filing put $464M of $476M in
intangibles into customer relationships, which is what buying a business with customers looks like in
accounting.

So the published read is that acquisition is running ahead of any visible buyer spend, sourced
entirely to audited filings rather than to funding announcements. This is a class change in the
evidence under the AI runtime domain, from press releases to `FILING`, which is the strongest source
class the site has.

**Two bounds go on the page with it, because without them the read overreaches.** "Not material" is a
threshold relative to the acquirer's own size, so it is an upper bound and not a claim that these
products earn nothing; Palo Alto's threshold is much higher than F5's. And an absent
customer-relationships intangible is a valuation judgment about separable contract value, not a count
of customers.

**Nothing moves that would need a second look.** The AI runtime posture stays INVESTIGATE / WATCH and
its `asOf` stays 2026-08-16, because the posture did not move and re-dating it would claim a change
that did not happen. The re-judgment is dated instead by appending an edition record whose derived
delta reads held across all six domains, with a note explaining that the rationale hardened while the
call stayed put. The platform-absorption hypothesis stays TRACKING rather than being promoted to
SUPPORTED; more absorptions strengthen its evidence, and moving a tracked hypothesis is a decision in
its own right, not a side effect of loading data.

Specified in [ai-coverage-presentation-spec.md](docs/active/ai-coverage-presentation-spec.md)
(`SEC-MARKET-AI-002`). Lands on `preview` for a rendered review; production moves only on an explicit
owner yes, as always.

One thing this deliberately does not touch. The Identity card's watch item reads "Palo Alto vs
CyberArk mix" and cannot resolve as written, because CyberArk filed Form 15-12G on 2026-02-23 and no
longer trades or files. Rewording a published watch item is a judgment change and it is carried as
SEC-026 for the owner rather than fixed quietly here.

**D-60 · 2026-08-28 — The market read is promoted to the top of the page. It was never visible on production.**

The site's entire message layer was hidden. `#read` — the market call, what changed, the Do and Avoid
lists, what we will not call and what would change the call — sat inside a closed disclosure labelled
"The market read, domain tempo and M&A activity", and so did the masthead carrying the headline
"Infrastructure is running ahead. Security is splitting, not booming." A reader on production saw a
tagline, four domain cards, what moved, platform pressure, hypotheses and forty-two vendor cards.
Evidence with no read attached.

Confirmed in a browser at 1561 pixels rather than from the markup: `#read` was in the document and
`checkVisibility()` returned false.

This is the second instance of the defect D-54 fixed for the vendor scorecard six days earlier, and
it was sitting on more valuable content. **Fixing one instance of a pattern is not fixing the
pattern.** Nobody thought to test the read after fixing the cards, because the cards were what had
been complained about. The general lesson is now in `lessons.md`: after fixing a visibility defect,
test every other surface for the same defect before closing it out.

How it was found is worth recording too. The owner asked how a research finding actually reaches the
page. I had specced three acquisition cards into a collapsed scorecard group and reported that as
publishing the finding. Adding evidence is not publishing a read, and the question that exposed it was
his, not mine.

**What moves.** The masthead and the read go to the top of `<main>`, above the domain cards. The
disclosure keeps domain tempo and the activity board and is renamed accordingly. The market call
becomes the page's `<h1>` and the landscape tagline becomes an `<h2>`, which is the correct outline
for a page whose primary statement is a market call. Both headings keep their exact current
appearance; the only visible change is position.

One trap was found while specifying rather than after shipping: each domain card renders its vendor
name as an `<h2>` inside `.landscape`, so restyling on `.landscape h2` would have blown all four card
titles up to masthead size. The selectors are scoped to `.landscape__intro` instead.

**A separable content change ships with it.** The read gains one line in What changed and one in
Avoid, both carrying the acquisition finding from D-59, plus its four filing sources and a confidence
clause. That edits a published, dated, human-signed judgment, so it is kept in its own commit and can
be rejected without unpicking the promotion.

Specified in [read-promotion-spec.md](docs/active/read-promotion-spec.md) (`SEC-MARKET-READ-001`).
This also answers a large part of SEC-019, the above-the-fold question that had been open since
2026-08-20. Production still moves only on an explicit owner yes after a rendered review.

**D-61 · 2026-08-28 — The read, the AI acquisition coverage and two new gates are promoted to production. Twenty-two commits.**

`origin/main` moved `4916a95` → `b423b70` by fast-forward from `preview`. Confirmed serving on
https://securitymarketpulse.com by browser query rather than by deploy log: `#read` returns true from
`checkVisibility()` with no disclosure ancestor, the page's single `h1` is the market call, the AI
runtime group header states ten covered against ten cards actually rendered, and the stamp and rail
both read 28 August while every judgment still reads 15, 16 or 17 August.

**What a reader gets that they did not have before.** The market read is on the page. Until today the
headline, what changed, the Do and Avoid lists, the no-call boundaries and what would change the call
were all inside a closed disclosure, so a reader saw evidence and none of the judgment it produced.
The read now opens the page. Under it the AI runtime coverage carries three acquisitions sourced to
audited filings rather than to funding announcements, and the read itself names the finding: platforms
are paying disclosed prices for AI security companies whose revenue those filings call immaterial.

**A date defect was fixed on the way rather than shipped.** The stamp read "EDITION 2026-08-28" beside
"UPDATED August 17, 2026", because one constant carried the site's as-of stamp, the date on the tracked
hypotheses, the date on the platform-pressure reads, and the window `weekMoves` describes. Publishing
an edition moved all four together, which would have re-dated judgments nobody had revisited. The
constant is split. The site stamp moves when the site ships; the judgment dates move only when a person
reviews those judgments again. Nothing was re-dated that was not re-judged.

**Two gates ship with it, both proven by perturbation rather than asserted.** The build now fails when
any of seven must-see sections is nested inside a disclosure, which is the defect this session found
twice. And a print-group header whose count disagrees with the cards rendered under it now fails the
build, which is the defect my own specification caused earlier in the session. The first attempt at
proving the first gate was invalid, because the script died on a stale artifact before reaching the
assertion and returned no verdict at all; that is the third time this project has hit that trap and it
is why the proof was redone against a clean build.

The stale end-to-end smoke test was also repaired, without touching a line of application code. It had
been asserting a page structure that stopped existing on 2026-08-22. The suite runs green.

Page height 8,274 → 10,340 pixels at desktop and 8,237 → 11,369 on the phone. That is the price of
showing a reader the judgments instead of hiding them, and it was paid deliberately.

**D-62 · 2026-09-03 — The weekly issue is the product; a machine drafts and a person signs; ePlus consumes downstream. Approach approved; plan to follow.**

An intent-versus-built review found the site answering the first research question, the
infrastructure-to-security lag, in its headline, while the thing the owner actually wants readers to
return for each week, who is forming, who is absorbing whom, who is printing growth, where capital is
going, sits in a collapsed Activity board whose window ended 10 August. The decision impact log has
zero entries and the exposure denominator is one, nineteen days into the two-quarter success test.

The owner restated the two goals in his own words and approved this approach: the weekly issue
becomes the unit of product, with five sourced lanes and a signed "what we now think"; the Episode 002
call becomes a standing thesis each issue scores against rather than the headline; a scheduled agent
gathers and drafts every Tuesday as a pull request and a named person signs and publishes, on the
line the shadow design v0.2 already drew; the issue is emailed to a named pilot list from issue #1
and to the public only after four held issues; ePlus consumes a machine-readable copy downstream and
builds its overlay inside its own channel and cockpit.

**Declined the same day:** an `eplus.securitymarketpulse.com` subdomain. The tailoring ePlus needs is
confidential and cannot sit on this domain, and an ePlus-branded surface on the owner's domain
entangles ownership in both directions. A branded ePlus surface is only appropriate as a licensed
offering on an ePlus domain, if that conversation ever opens.

**What this does not do.** It does not change `intent.md`; the proposed v1.2 text is in the plan and
waits for the owner's acceptance. It does not authorise any build. Plan:
[weekly-issue-plan.md](docs/active/weekly-issue-plan.md) (`SEC-MARKET-WEEKLY-001` v0.1). Backlog:
SEC-027 to SEC-031; SEC-017 superseded.

**D-63 · 2026-09-03 — Intent v1.2 accepted as written.**

The owner accepted the v1.2 text proposed in §3 of
[weekly-issue-plan.md](docs/active/weekly-issue-plan.md): "approve the intent v1.2 text as written."
`intent.md` now carries it. Four state-register rows moved: the weekly issue is Decided as the unit
of product; autonomous agents are Decided for gather and draft only, with publication and every
judgment a named person's act; newsletters are Decided for a named pilot list with public timing held
to the 2026-10-08 review; the confidential overlay stays Exploring with a decided boundary, downstream
inside ePlus surfaces and never on this domain. One line joined "Must remain true": a machine may
retrieve, extract, compare and propose, and only a named person signs a judgment or publishes an
issue. Purpose, desired outcome, value, beneficiaries, observable success, the public-evidence
boundary and "Must not optimize" are unchanged.

This clears the intent gate on SEC-027 to SEC-031. It does not by itself authorise a build; the
issue-model and gather-job specifications come next and each build is dispatched against its spec.

**D-64 · 2026-09-03 — Build the whole weekly-issue improvement into `preview` autonomously, without milestone gates.**

The owner's direction, in his words: plan the work to execute autonomously, use Codex and GPT models
for third-party review, validate every change in the browser, no milestones, "the entire improvement
intent completed into preview for me to review along with a summary of what was done." The project
is exploratory and the work carries no critical harm.

What holds: `main` is untouched and moves only on the owner's promotion; every judgment stays a named
person's act, so the first issue ships to `preview` as a labelled, unsigned draft; every figure is
quoted verbatim from a fetched document; every gate is proven by perturbation; every change is
rendered at 1440 and 390 and checked with `checkVisibility()` against the live preview deploy, not a
local build; nothing is deleted on static analysis; explicit paths are staged.

What is relaxed: no intermediate promotions; no spec approval gate before build, the specs ship
with the work; external review runs once on the specs and once on the whole diff rather than per
task; the visual review states what moved against the spec rather than halting on any unexpected
pixel.

Specifications: [weekly-issue-spec.md](docs/active/weekly-issue-spec.md) (`SEC-MARKET-ISSUE-001`)
and [gather-job-spec.md](docs/active/gather-job-spec.md) (`SEC-MARKET-GATHER-001`). The gather job
runs as a Claude Code cloud routine rather than a launchd job, which removes the Forge and jobs-agent
dependencies the plan had assumed. Work lands on branch `weekly-issue`, is validated on its Vercel
preview deploy, and merges to `preview` when the whole improvement passes.

**D-65 · 2026-09-05 — The weekly-issue improvement is merged to `preview` for owner review; production is the trust anchor for published history.**

Branch `weekly-issue` (37 commits over 2026-09-03 to 2026-09-05) fast-forwarded `preview` from
`7a9234f` to `604e900`. What landed: the weekly issue data model and `verify:issue` gate (fifteen
checks, every one proven by perturbation); issue `2026-w36` as a labelled, unsigned draft with 23
items and a machine proposal, every figure quoted verbatim from a document fetched with `curl` and
carrying a sha256 receipt; the front page reframed around the issue with the Episode 002 call as a
standing thesis; `/issues/`, `/issues/<id>/`, `/issues/<id>.json`, `/issues/index.json`,
`/issues/lock.json`, `/feed.xml` and a per-route sitemap; the vendor lens; the gather brief and
specs v0.2 with amendment records; and the cloud routine, still disabled.

Validation: three rounds of external review (Codex gpt-5.6-sol and a fresh Claude Sonnet session)
on the whole diff, each round's findings fixed and re-reviewed; the full Playwright suite run against
the live branch deploy and again against the stable preview URL at 1440 and 390; screenshots of
production and preview compared; a Chrome walk of the archive, permalink and lens pages with no
console errors.

The decision inside the build: an in-repo hash manifest cannot stop a committer rewriting history, so
the append-only gate anchors on two things outside the working tree, the git parents of the commit
being built and the manifest served live by production at `/issues/lock.json`. An issue published on
`preview` but not yet promoted is still under owner review and may change; once promoted it is
anchored. On a `main` or `preview` build with no readable anchor the gate fails closed. Codex's last
verdict on the gate, after the empty-body fix, is recorded in
`docs/active/issues/2026-w36-review-final-codex.md`; the residual it names (feed well-formedness)
was closed in the same pass.

Not decided here: promotion to `main`; signing `2026-w36`; arming the Tuesday schedule; the pilot
list. All four are the owner's.

**D-66 · 2026-09-19 — `2026-w36` signed and promoted; production is current for the first time since 2026-08-28.**

The owner adopted the gather's proposal as written and signed it. `weThink` now carries the summary,
the episode-002 thesis verdict (`holds`, medium confidence, four evidence ids) and the lag no-call;
`proposed` is nulled on publish so the page carries one judgment rather than two, and no posture
deltas were accepted. The signature line reads `Signed by Jesse Pike · 19 Sep 2026` and the running
score reads `Holds in 1 of 1 issues since 19 Sep 2026`.

`main` moved `b423b70` → `aa04875`, fifty-four commits, the first promotion since 2026-08-28. That
carries the entire weekly-issue model into production: the issue hero and four lanes, the
`/issues/` archive, per-issue permalinks, `/feed.xml`, `/issues/<id>.json`, the lock manifest at
`/issues/lock.json`, and the vendor lens. Confirmed by render, not by deploy log: production returns
15,033 pixels at 1440 and 17,760 at 390, identical to preview at both widths, and the four new
endpoints all return 200.

Two things worth recording because they are consequences rather than intentions. First, the page
grew from 10,340 to 15,033 pixels at 1440 — a 45% increase, on top of the doubling recorded in D-57.
Second, and more important, **the first screen is now materially different in kind.** Production
previously opened with a two-line thesis headline, a dark stat band carrying three numbers, "The
read" with its confidence lines, and the Do and Avoid panels — a decision instrument. It now opens
with the issue headline and goes straight into the Formation lane, which is a chronological list of
funding rounds beginning at $156.0M and running down to a $60.0K pre-seed. The judgment moved below
four lanes of items.

This is the accepted D-64 composition rendering exactly as `weekly-issue-spec.md` §4 specifies, so
it is not a defect and nothing was broken. It is a design consequence that nobody had seen at full
page height until this promotion, and it is the first thing the SEC-042 run should be pointed at.

Also in this commit: `LAST_UPDATED` moved to 2026-09-19, which its own contract requires whenever the
site ships, and `tests/issue-data.test.ts` was repaired. Its "is empty when there are no published
issues" case asserted `thesisRunningScore` against the live issues array, so it passed only while
every issue was a draft and signing broke it. Rewritten against fixtures with the assertion
unchanged.

Still open and unchanged: the pilot list, arming the Tuesday schedule, and the runtime the gather job
runs on now that the cloud environment has been proven unable to reach the public web.

**D-67 · 2026-09-20 — The owner restated what the site is for; `docs/active/product-core.md` is the working statement, and the front page is re-aimed at it on `preview`.**

In the terminal on 2026-09-20 the owner said the site is first a credibility asset for his advisory
work and a working instrument for deciding which suppliers and domains deserve attention. It is
written for security leaders and practitioners first, advisors and vendor partner teams second, and
not for investors. The founding thesis becomes one standing analysis, no longer the centre.
Monetization and the employer outside-activity question are parked by him. He wants it fully
automated with a decision arriving in a channel once or twice a week, and he doubts that "a person
signs every judgment" is the right model. `intent.md` and `.claude/rules/constraints.md` are
unchanged; the proposed amendments are in `product-core.md` section 9 and wait for his word.

Decisions the run took on its own recommendation, each recorded in
`docs/active/fable-run/RUN-STATE.md`:

- The scoring rubric is `docs/active/fable-run/site-rubric.md` v2.1. Decision value and trust carry
  the most weight, and four blockers override any score: a mislabelled figure, an unsupported
  comparison, machine content presented as the author's opinion, an accessibility failure.
- The supplier table on the front page is alphabetical and ranks nothing. An external review on
  `gpt-6-astra` showed that a table ranked by growth compares figures that are not like for like
  and reads as an endorsement from an author who works for a reseller of these suppliers.
- Copying newer issue figures into `prints.ts` is on hold until a gate checks company or segment,
  metric, period and units together (SEC-044).
- Promotion to `main` still needs the owner's explicit word. "Let's get it deployed" was read as
  authority to build to `preview`, not to publish.
- Automation step 0 is a GitHub Action that messages a webhook when a draft pull request opens;
  approval is merging that pull request from the phone. No new backend.
- Recommended and not yet decided by the owner: never take vendor sponsorship; concede the paid
  data lane to existing newsletters; Plausible for analytics.

Facts found on the way, all still true at the time of writing: signed issue `2026-w36` gives two
fourth-quarter revenue figures as full-year figures (SEC-043, live on production); `prints.ts` is
months behind the issue for six suppliers (SEC-045); every domain judgment dates from 2026-08-16;
`.claude/rules/constraints.md` still lists the website and an autonomous pipeline as not
authorized, which only the owner can amend.

**D-68 · 2026-09-20 — The owner approved a public correction to signed issue `2026-w36`, and the way corrections are published.**

Two headlines in the issue gave fourth-quarter revenue as fiscal-year revenue (Zscaler $898.2M, Palo
Alto $3.41B), and one "why it matters" line called a company-defined segment's growth the fastest of
the week against other companies' total revenue. Shown the drafted correction text and the
mechanism in the terminal, the owner said yes. The text is the one in
`docs/active/fable-run/drafts/correction-2026-w36.md` section 2, dated 2026-09-20. Published issues
stay locked: corrections live in an append-only `web/src/data/corrections.ts`, show as a dated note
beside the affected item with the original left as it was, are listed at `/corrections/`, and are
carried in the machine-readable files. A gate now fails a fiscal-year label over a quarterly source
(SEC-043, SEC-044 in part). Built to `preview`; promotion to `main` remains a separate owner call.

**D-69 · 2026-09-20 — `preview` promoted to production on the owner's word; `main` moved `aa04875` → `fe944b2`.**

After reading the final packet summary the owner said "go ahead and promote this". The promotion was
a fast-forward push of the `preview` head to `main` with `PROMOTE=1`, done without switching
branches because the shared checkout held another session's uncommitted changes. It carries the
rebuilt front page (the market by domain first, the founding thesis lower as a standing analysis),
the author's name on every dated judgment, and the owner-approved correction to issue `2026-w36`
with the `/corrections/` page (D-67, D-68). Rubric v2.1 blind score: 32.8 before, 57.2 after.

The owner also asked why promotion and commands needed him at all. Recorded as a standing
preference: he says the word and the agent runs the command; the agent does not hand him commands
to run unless the step is tied to his own account (a browser approval, a secret from his Slack).

**D-70 · 2026-09-20 — the weekly gather runs on macbook2014 under launchd, and GitHub carries the notification.**

The automation plan left the runtime open between a Claude cloud routine, which cannot reach the
public web without an allowlist the owner controls, and a local runner on a host nothing had proved
was reachable. Measured: `ssh macbook2014` connects and `claude` is installed there, so the local
runner needs no owner decision. The reachability table in
`~/code/_shared/agent-exec/docs/infrastructure.md` says otherwise and is stale, measured 2026-08-02.

The chain is: launchd fires `scripts/gather.sh` on macbook2014 every Tuesday at 07:00; the script
resets to `origin/preview`, works out the due ISO week, exits early if that issue or its branch
already exists, checks its own Claude login, hands the job to `claude -p` with
`docs/active/gather-brief.md` as the instruction, and confirms a branch reached GitHub. The host
pushes over a read-write deploy key and holds no GitHub API token. `.github/workflows/gather-pr.yml`
opens the pull request from the pushed branch, and GitHub's own mobile notification is the one tap —
no webhook, no credential, no spend. `.github/workflows/freshness.yml` watches the live site daily
from GitHub rather than from macbook2014, because a probe on the watched host goes quiet exactly
when that host dies. Every run writes a receipt to `~/gather-logs/receipts/` whatever happens, so a
silent failure and a quiet week never look the same.

One step is not the agent's: the Claude subscription login on macbook2014 expired in May and needs
an interactive `claude setup-token` on that host. Until then the job fires, detects it, and records
`blocked-auth`.

**D-71 · 2026-09-20 — the front page's `h1` is the site's subject, not the week's headline.**

`product-core.md` (SEC-MARKET-CORE-001) §5 says the first screen belongs to the market picture. It
did not. D-64 had promoted the newest issue's one-line read to the `h1`, which at 1440 ran to three
lines of 44px type and told a first-time reader about one week rather than about the site. A page
whose own description says it is not a news site was leading with a news headline.

The front page now opens with a masthead carrying a standing headline, "The security market, from
public numbers", then the description, the disclaimer and both date stamps on one line. Under it the
weekly read is a single-line strip that keeps the id `#overview`, so the header's "Issue" link and
prerender's front-page section list did not change. Then the market by domain, which now reaches the
first screen at 1440 with three domain cards visible.

The issue permalink is untouched and still carries the read as its own `h1`, where it genuinely is
the subject of the page. `IssueHero` was not deleted or edited; the front page simply stopped using
it. Rendered at 1440x900 and 390x844 before and after; full page height moved 16,884px to 16,873px,
so nothing below the fold shifted. Five gates, the data tests and 34 end-to-end tests pass.

`web/scripts/shot.mjs` gained `--fold`, which captures the viewport rather than the whole page. A
full-page image of a 17,000px page cannot answer what is on the first screen, and the first screen
is where this site has twice now shipped a composition nobody had looked at.

The headline itself is copy, so it is the owner's to change. It lives in one constant,
`SITE_HEADLINE` in `web/src/data/meta.ts`.

**D-72 · 2026-09-21 — The founding thesis leaves the front page for `/thesis/`, and `preview` was promoted on the owner's word; `main` moved `fe944b2` → `35a888f`.**

The owner asked whether the thesis (does security spending lag infrastructure spending) is something
his audience needs. Answer recorded: not for a security leader, mildly for advisors and vendor
partner teams, which matches `docs/active/product-core.md` section 5. He said to continue, the move
was built to `preview`, he was shown it, and he said "Promote".

The whole judgment board (running score, thesis headline, stat band, the read, change triggers,
no-call boundaries, Do and Avoid) renders unchanged at `/thesis/` under a short plain introduction.
The front page keeps a five-line pointer at `#read`, stamped with the date of the newest signed
verdict read from issue data, and the signed block carries the verdict as one linked line. "Thesis"
left the top navigation. Issue permalinks differ only by that navigation link. Nothing was deleted.
The same promotion carried the parallel session's D-70 (durable gather, PR and freshness workflows)
and D-71 (masthead heading "The security market, from public numbers"). Confirmed by fetching the
live host: the pointer is on the front page, the change-trigger list is not, `/thesis/` serves it,
both CORRECTED notes are present, and eight routes and files return 200.

**D-73 · 2026-09-21 — The owner approved three maintenance builds: his approval of the draft pull request becomes the signature and publishes the issue, the weekly job maintains the standing picture, and the thesis verdict leaves the weekly brief.**

The owner asked how the site is actually maintained. The answer recorded: the weekly issue has a
scheduled job (D-70), blocked today by an expired Claude login on macbook2014; nothing maintains the
scorecard, the domain stances, Platform pressure or the hypotheses; and signing, publishing and
promotion each still need an agent session at a terminal. Three builds were proposed and he said
"yes to all 3".

1. His approval of the weekly draft pull request, given from the GitHub phone app, is the
   signature. A workflow applies the proposal as signed by him on that date, runs every check,
   merges to `preview`, promotes to `main` and confirms the live site. The machine still only
   drafts; the named person still signs. What changes is that the signature is a tap and not a
   terminal session. This narrows the promotion rule in `AGENTS.md` for one case only: a weekly
   issue he approved. Every other change to `main` still needs his word in a session.
2. The weekly job also proposes scorecard updates, held behind a check on company or segment,
   metric, period and units (SEC-044, SEC-045), and flags stances that have gone stale so he can
   re-confirm them with the same approval.
3. The thesis verdict leaves the weekly brief and the draft issue. `/thesis/` and its record stay.
   The locked issue 2026-w36 is not touched.

`intent.md` and `.claude/rules/constraints.md` are his to amend and are not edited by this run. The
wording changes they need are proposed separately in `docs/active/publish-path-spec.md`.

**D-74 · 2026-09-21 — `preview` was promoted on the owner's word; `main` moved `35a888f` → `51dbffd`. The publish-on-approval workflow, the scorecard check and the stale report are on the default branch.**

The owner said "promote". The promotion carried builds 1 and 3 and the first step of build 2 from
D-73 (`docs/active/publish-path-spec.md`): `.github/workflows/publish-issue.yml`,
`scripts/publish-issue.sh`, the sign scripts, `verify:prints`, `report:stale`, and the thesis
verdict leaving the weekly brief. Nothing a reader can see changed: four pages compared between
production and the preview host were identical once hashed asset names and hosts were normalised.
The push went out from macbook2014 over its deploy key because it carries workflow files, which
this laptop's token cannot push. Vercel's production deploy succeeded and the live host was checked
for content. From this commit on, the owner's approval of an `issue/*` pull request into `preview`,
or his comment `publish`, signs and publishes that issue under the conditions in the spec. Known
residual risks are recorded as SEC-051 in `BACKLOG.md`.

**D-75 · 2026-09-21 — Second promotion of the day on the owner's word (`main` `51dbffd` → `9b98353`), and he approved new wording for the Platform pressure sentence that wrongly called platform vendors hyperscalers.**

The owner said "promote and yes". "Promote" carried the `reconfirm` word (spec section 4.3), the
weekly job loading `~/.env.local`, and the weekly job's pre-approved shell commands. Four pages
compared between production and the preview host differed only in the stylesheet's hashed file
name, so nothing a reader sees changed. Pushed from a temporary clone on macbook2014 because the
push carries a workflow file. Vercel's production deploy succeeded, seven live routes return 200,
and production now serves the same stylesheet as `preview`.

"Yes" answered SEC-054. The blind score of 2026-09-21 found, and the coordinator confirmed, that
every absorbed supplier outside Identity carried the sentence "Cloud security absorbed into a
hyperscaler", including rows where the acquirer is Palo Alto Networks or F5 and the target is an AI
security company. Approved wording, chosen by who bought and what was bought: a hyperscaler buyer
keeps the current sentence; a platform vendor buying AI security reads "AI security absorbed into a
platform vendor. Watch whether it survives as a product or becomes a feature."; a platform vendor
buying cloud security reads the same with "Cloud security". It is built to `preview` first, with
the changed rows dated to this approval and the error listed at `/corrections/`, and it reaches
production only on a further word from him.


**D-76 · 2026-09-25 — No human approval step. Sourced, machine-validated facts publish on their own; the machine publishes no judgments. `intent.md` moves to v1.3 and `.claude/rules/constraints.md` is rewritten to match, on the owner's approval.**

The owner's words: "Source check facts can publish. I don't want to be the bottleneck for this. So
it needs to be automated. There doesn't need to be any gates." Asked what happens to the judgment
parts of the site (domain stances, the weekly headline, "why it matters" lines) once nobody approves
them, he chose "facts only, no judgments" over publishing machine-written judgments under his name
or labelled as automated analysis. He then approved rewriting `intent.md` and the project rules to
say so.

What this settles: product-core open question 8 is answered. Automated checks (the `verify:*` gates)
remain and become the only gate; a human approval, a signature and a promotion word are no longer
required for facts to reach production. A machine may not publish a stance, a ranking, a forecast,
or a sentence interpreting what a fact means. The owner may still write a judgment himself; it
then publishes under his name as today.

What it supersedes: the approve-to-publish path of D-73 to D-75 for facts, the `reconfirm` word, and
the D-66 signing of weekly issues as a precondition of publication. The existing dated stances of
16 Aug 2026 and other judged text on the site are not removed by this decision; how they are
retired or kept is part of the plan in `docs/active/autonomy-coverage-plan.md`. The AGENTS.md
production-deploy contract (every `web/` change reaches `main` only on an owner yes) still governs
changes to the site's code and layout; only the automated publication of validated facts is
exempted, and AGENTS.md is updated when that path is built.

**D-77 · 2026-09-25 — The owner said "go" on `docs/active/autonomy-coverage-plan.md` (SEC-MARKET-AUTO-001), approved the four intent amendments (`intent.md` v1.4), and chose Claude Opus 5.5 and GPT-6 Sol as the site's scorers.**

His words: "go, and apply the four intent amendments. I'm thinking we should use opus 5.5 for
scoring along with sol 6." `intent.md` v1.4 restates purpose (a credibility asset and a working
instrument for supplier and domain decisions), readers (security leaders first, investors out),
scope (distress and consolidation in, news out, the thesis as a dated record, revenue not a current
goal) and success (freshness first). The standing supplier tracker replaces the signed weekly issue
as the unit of product. "Go" is taken as the word to run the plan end to end, including step 0's
promotion of `preview` to `main`, which also carries the SEC-054 Platform pressure correction whose
wording he approved on 2026-09-21. Layout changes in later steps are still shown to him before they
reach production. Scoring: every future score is two blind scorers, `claude-opus-5-5` and
`gpt-6-sol` via `codex exec -m gpt-6-sol`; recorded in `docs/active/fable-run/site-rubric.md` v2.2.

**D-78 · 2026-09-25 — Step 0 of AUTO-001 promoted to production under D-77's "go"; `main` moved `9b98353` → `28c7ffd`.**

Eight scorecard figures now show the latest reported quarter, each checked against the company's
own SEC exhibit or release (Zscaler, Okta, CrowdStrike, SentinelOne, Rubrik, Netskope, SailPoint,
Cato Networks); Lakera reads as closed inside Check Point on 2025-10-22; acquired suppliers share
one label. Palo Alto's segment figures and Upwind's new round were left unchanged because no
primary source could be read. The promotion also carried the SEC-054 Platform pressure correction
and the EDGAR runner (not yet on any page). The live host was checked: new figures and the
corrected wording served, five routes return 200. Report: `docs/active/auto/step0/report.md`.

**D-79 · 2026-09-25 — The automatic publish path compares only the site, the workflows and the scripts when deciding whether production may move; record-keeping commits no longer block facts from publishing.**

As built in step 4, `scripts/auto-publish.sh` refused to move `main` whenever `preview` differed from
it anywhere outside the data files, including `docs/`. Every run-state or decision commit would
then have held back published facts until someone promoted by hand, which is the bottleneck D-76
removed. The comparison now covers `web/`, `.github/` and `scripts/` (minus the data allowlist).
An unreviewed change to the site, its workflows or its publishing scripts still stops production
from moving; the data then lands on `preview` only and the page reads "collection incomplete".
The coordinator took this on its own recommendation under D-77.

**D-80 · 2026-10-02 — The site carries one neutral independence line on the Method page, names no employer, and puts the owner's name on no live page; his signed historical records keep it.**

Both round-3 blind scorers marked trust down because the site said nothing about the operator's
relationship to the suppliers it tracks. The owner chose, relayed the same day through the
parallel design session: one line on the Method page, "Security Market Pulse is independent and is
not sponsored or paid for by any company it tracks." No mention of ePlus anywhere on the site, and
his name off the live pages (the hero byline was removed on `mon/uifix` the same day). The signed
corrections entries and the archived w36 issue keep his name unless he says otherwise. Publishing
under Pike Holdings is a likely later change, logged as SEC-056, not made now.
