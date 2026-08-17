# Security Market Pulse — Consolidated Review Findings

## Control

- **Doc ID:** `SEC-MARKET-REVIEW-FINDINGS-001`
- **Date:** 2026-08-16
- **Sources:** CTO read-only product/evidence review of the web MVP; independent Fable review of the proposed startups section; direct verification of both against the repo.
- **Status:** findings only. Nothing in here has been implemented.
- **Verification note:** every claim below marked **VERIFIED** was checked directly against the repo or the running site. Claims marked **HYPOTHESIS** were not confirmable from available material and need a primary source.

---

## Part 1 — Web MVP (`SEC-MARKET-WEB-001`)

### Shipped and closed this cycle

Three P1 defects were found and have since been fixed and re-validated:

1. **Artifact links 404'd in production.** The evidence drawer built research-artifact links from `https://github.com/jessepike/sec-market`, which returns HTTP 404 — the repo is not public. Every source link on the public site would have been dead. Now resolved: `researchArtifactUrl()` returns null unconditionally, packet identifiers render as plain text, and the canonical source is the only link.
2. **The site instructed RUN where the accepted research forbids it.** The Tempo table showed RUN for Network / SASE. `market-signal-episode-002-brief.md` caps that row at "PREPARE the observed motion; do not rebrand it as infrastructure-lag capture" and reserves anything stronger for "a separate decision episode; this episode does not." Now PREPARE, with `posture` and `tag` in agreement across all six domains.
3. **Mobile stripped evidence access.** A `hidecol` rule at the 768px breakpoint removed the Tempo "Why" column — which carried both the reasoning and the Sources control — and the Method table's "We do not" guardrails. Now restructured so the detail row is always rendered.

Also closed: surface-refresh evidence records relabelled, edition provenance copy corrected, prints grid reduced to actual prints with no-series names collapsed, D12 reclassified from INDEPENDENT to IR, `LAG-NO-CALL` given an `OWN_ANALYSIS` source class, C6 split into C6a/C6b with no dangling references, annual prints marked as annual, IANS falsifier added to Watch next.

### Open — highest value item in this document

**The judgment layer is authored and not rendered.** In `web/src/data/market.ts`, the fields `whatChanged`, `actions.doItems`, `actions.avoidItems`, `meaning`, `confidenceNote`, `noCallBoundaries` and `changeTriggers` are referenced by **no component**. `SummaryCards.tsx` and `SignalFeed.tsx` exist and are not imported into `App.tsx`. **VERIFIED.**

The product contract's Overview requires: current market call, what changed, what it means, confidence and no-call boundaries, what would change the call. Four of those five are not on the page. The site currently shows the evidence and withholds the judgment, which is backwards — the judgment is the part nobody else can produce.

This is component work against already-reviewed content. No new research, no new claims, no re-review needed.

### Open — other

- **Information density.** Content column is ~960px inside a 1419px viewport. The prints board spends 24 cards on roughly 16 data points, one number per card, forcing serial reading. A dense table would use the width, allow comparison, and better serve the two-minute read. Cards are the wrong form for a scorecard.
- **No archive.** No Episode 001, no back issues, no dated permalink. A recurring briefing with no back catalogue does not compound; each edition overwrites the last. The running record of past calls and whether they held is the most defensible asset this product could build. Product-strategy decision — recommend CPO involvement.
- **Header nav.** Section links update the hash but the page does not scroll. Could not fully isolate; may be browser-specific. `Header.tsx` looks correct. Suspect `scroll-behavior: smooth` interacting with `scrollIntoView` called in the same tick as the `setNavOpen` state update; try `requestAnimationFrame`. Needs a human check in a normal browser.
- Evidence library subhead still says "Search frozen Episode 002 sources" though 13 of 44 records are surface-refresh.
- `TempoTag` union in `types.ts` still permits `'RUN'`. Unused; delete so it cannot be reintroduced by autocomplete.
- Three orphaned evidence records: A6 (Broadcom), B4 (Meta), B5 (Oracle).

---

## Part 2 — Proposed startups / funding section

### Finding A — the Zenity "conflict" is arithmetic, not a conflict. **VERIFIED.**

The packet's own Zenity row quotes Return on Security: *"raised an $115.0M Series C from Norwest and an additional $10.0M Secondary Market"*, and Cybersecurity Ventures: *"$125M Series C."* 115 + 10 = 125. One transaction counted two ways.

The brief proposed displaying this as an unresolved conflict and as evidence of epistemic honesty. It is the opposite: a reader who opens the drawer resolves it in thirty seconds and concludes the desk did not read its own evidence. **Resolve before anything ships.**

Related but **HYPOTHESIS**, not resolvable from the packet:
- Glow — $100.0M Series B (RoS) vs "$180M stealth emergence" (CV)
- Neo Security — $75.0M Series A (RoS) vs "$100M at launch" (CV)

Round-versus-cumulative-at-emergence is the likely explanation for both, but the packet does not contain the arithmetic to close them. Either confirm with a primary source or keep them as genuinely unresolved — which is what dual display is actually for.

### Finding B — the barbell claim is refuted by our own packet. **VERIFIED.**

Insight 3 ("capital is a barbell") was slated for the page. The middle of the packet is populated with dated rows: Valarian $50M, Inforcer $50M, DataBahn $40M, AegisAI $36M, Risk Ledger $32.2M, Twenty Technologies $30M, Empirical Security $25M, plus a stack of smaller rounds.

Publishing a barbell claim above an evidence drawer full of $25M–$50M rounds is a thesis its own footnotes refute. **Kill the named claim.** The defensible version is about *location*, not distribution: the largest checks go to established platforms while the newest names cluster in agents and identity. One sentence in the read, not a named thesis.

### Finding C — this is not a new section. **VERIFIED.**

`docs/active/signals-operating-model.md`:
- Line 89: "M&A events use the **same Activity surface** on the site (`lead` / `more` / `background`) but a **separate gather pass** and separate working packet."
- Line 91: "**One human checker** still signs combined first-screen headlines (five slots shared across funding + M&A, **not five of each**)."

The section brief's "do not put M&A on this first screen yet" contradicts the settled operating model *and* the live page, which currently leads with two M&A closes.

The live Activity board already carries: Google/Wiz close ($32B, Mar 11), Palo Alto/CyberArk close ($25B, Feb 11), Cyera $600M at $12B (Jun 10), Onyx $113M Series B (Jul 29), Cisco/Astrix (undisclosed, Jun 29), plus collapsed "More in this window" (Portkey close, Symmetry intent) and "Background" (Lumos 2024, Secuvy 2023).

**Reframe the work as the next edition of the existing Activity surface**, in which the February and March closes rotate down and the funding cluster rotates up. This is a smaller build than the brief describes, and it disposes of the Onyx duplication automatically because there is only one board. It also fixes the weakest content on the live page — the Background rows are currently a 2024 Lumos round and a 2023 Secuvy seed.

### Finding D — the strongest read is not among the three insights. **VERIFIED.**

In one five-week window, six platform actors moved on agent identity and control:

| Actor | Move | Target | Status |
|---|---|---|---|
| Akamai | strategic investment | Hush Security ($30M Series A, NHI / agent identity) | packet |
| Cisco Investments | strategic investment | Zafran Security (undisclosed) | packet |
| CrowdStrike Falcon Fund | strategic investment | Above Security (insider threat / agents, undisclosed) | packet |
| Cisco | acquisition, completed | Astrix (NHI) | **already on live board** |
| Zscaler | intent to acquire | Symmetry Systems | **already on live board** |
| Palo Alto | acquisition, closed | Portkey (AI gateway) | **already on live board** |

The platforms that just finished buying identity are now seeding and buying agent control. Three by investment, three by acquisition, and half already published on the site.

This requires **no new collection**, it is visible only because this page holds both funding and M&A on one surface, and it is more original than insights 1 or 2 as written. **Recommend this as the spine of the section read.**

### Finding E — insights 1 and 2 need rewording

- **Insight 1** is carried mostly by rounds that are not formation. Zenity is a Series C, Onyx a Series B — companies formed 2021–2023 now getting traction. The formation evidence is the seeds: Arrakis $8M, Actualyze $7M, CodeIntegrity, Way $20M. Stronger version: *agent governance got funded at every stage in one five-week window, seed through Series C plus strategic checks* — the signature of a category assembling.
- **Insight 2** — "buyers are in pain now" is unsupported by any spend or revenue evidence in the packet. What exists is strategics paying to be near the problem. Also, **Keyfactor does not belong in this insight**: a $1B Summit Partners PE recap of a mature PKI company proves machine identity is bankable at infrastructure scale, not that identity is being rebuilt for agents.

### Finding F — headline slots

Keep Zenity (stated as "$115M Series C plus $10M secondary; some outlets report $125M total"), Oak ($60M seed — the amount is the story), Hush ($30M with Akamai strategic — the cap table is the story).

Kill from the lead row:
- **Arcade / CodeIntegrity** — no amount, no date beyond "2026," single-sourced to a VC's own portfolio page, and two companies in one slot reads as padding. The design already routes unpriced names to "just appeared"; that is where they go.
- **Horizon3.ai** — the brief's own hedge ("only if labeled a scale-up check") is the tell. Drags in a fourth theme.

Candidates for the remaining slots, remembering the five are **shared across funding and M&A**:
- **Cyera acquiring Oasis Security at $1B** — verified in `ma-source-catalog.md` via SecurityWeek. Strong, because Cyera sits on the live board as a $600M raise eight weeks earlier; raise-then-acquirer is a connection only this page can make.
- Keyfactor $1B PE, if it earns the slot on the strength of the sentence (machine identity priced as infrastructure) rather than the size of the number. Weakest of the candidates.
- Cathedral $160M (a16z, autonomous red team) is excluded from lead but **must** appear in "more in this window" with a one-line defense-tech note, or readers who know the window will ask where it went.

### Finding G — cadence is already decided; state it out loud

`signals-operating-model.md` §4 already settles this: weekly internal gather on Return on Security, event-driven promotion for mega-events, **public refresh on the monthly edition pass**. The section inherits the edition clock.

A public weekly clock puts the site in a cadence race with its own free upstream source, which it loses by construction, and it breaks the human-checker economics and the frozen-edition identity that is the differentiation. Print the window on the page ("Window: Jul 6 – Aug 10, 2026") so slowness reads as discipline.

**Dependency:** RoS 257 and 258 will exist by ship date. The window must be re-gathered at ship or the section is born stale.

### Finding H — the gap to world-class

Four specific gaps, all actionable:

1. **Resolve conflicts, don't display them.** Per Finding A. Reserve dual display for genuinely unresolved amounts.
2. **Delta discipline.** The core repeatable read of a top-tier product is what changed versus the prior window. Structure edition one so edition two's delta is automatic — the packet's event-record fields already suffice. *(Independently flagged in Part 1 as the missing archive: two reviewers converged on this without seeing each other's work.)*
3. **Cross-surface join.** Nobody else can write "Okta decelerating on the print grid while Oak and Way raise mega-seeds against the same buyer problem." Not writing sentences like that leaves the only structural advantage unused.
4. **Second-source every lead headline.** Hush already has YL Ventures' release; Zenity and Oak need company or press confirmation. Single-sourced headlines are where a professional checks first.

Also recommended: publish a condensed version of the packet's coverage-holes section in the method note. Naming your own misses is on-brand and nobody else does it.

### Finding I — the derivative risk, and the answer to it

All five headline amounts trace to Return on Security issues 252–256, a free newsletter the target audience already reads. Attribution does not fix that. The answer is not more data; it is the two things RoS structurally cannot do:

- the capital-versus-buyer-spend frame the rest of the site already owns; and
- the join across the site's own surfaces — funding next to M&A next to vendor prints next to domain postures.

**Falsifier.** The section needs one in the site's idiom, and it already exists in `watch.ts`: *the first disclosed agentic-identity revenue print decides whether this category is real spend or product naming.* Publishing capital heat and its falsifier in the same breath is what makes this a Pulse section rather than a funding ticker.

### Finding J — reconcile the heat chips with the Tempo board

The DomainBoard currently rates Identity and AI Runtime as WATCH with low evidence strength. Heat chips next to that read as the page arguing with itself unless one sentence reconciles them: **capital heat is arriving ahead of disclosed revenue.** Recommend the chips link to their corresponding DomainBoard rows.

---

## Recommended order of work

1. Resolve Zenity. Attempt Glow and Neo against primary sources; accept unresolved if the lookup fails.
2. Rewrite the three insights: one platform-absorption spine (Finding D) plus a stage-spread observation. Kill the barbell.
3. Reframe as an Activity-surface refresh, not a new section (Finding C).
4. Re-gather the window against RoS 257–258.
5. Pick five combined funding + M&A slots.
6. Separately, and independent of all the above: render the judgment layer already sitting in `market.ts` (Part 1).

## Things not to do

- Do not put 58 rows on the page. Five lead slots, rest collapsed.
- Do not build a sibling section alongside the existing Activity board.
- Do not publish "capital is a barbell."
- Do not present the Zenity amounts as an unresolved conflict.
- Do not introduce a public weekly cadence.
- Do not treat raises, valuations, or deal values as ARR or buyer spend.
