# Security Market Signal Pipeline — Workflow Spec v0.4

**Status:** Historical source hypothesis — non-governing.
**Date:** 2026-08-14
**Supersedes:** v0.1, v0.2, v0.3

> **Handoff notice:** [intent.md](../../../intent.md) is the governing authority. The accepted Gate chain and completed `SEC-MARKET-SIG-001` packet supersede this document wherever they conflict. Do not treat this file as a build order or canonical current state. Its tempo, posture, tier, coverage, and mechanism proposals remain inputs to test rather than authorized project controls.

**Changes in v0.4:**
- Added §5 **demand-side signal layer** — job postings, transcript term frequency, analyst category creation, startup formation. First inputs that observe buyers rather than vendors.
- Added §4.2 **domain × vendor coverage matrix** — makes uncallable domains explicit
- Added **two-tier coverage model** (Core / Extended) to reconcile breadth against maintenance cost
- Deferred: public-sector RFP language, conference agendas, prediction markets (§5.5)

---

## 1. Why This Exists

Resource allocation under uncertainty on a 12–24 month horizon, where **timing beats accuracy.** Early-funnel demand gen and account planning require committing effort to a domain *before* demand is visible in pipeline.

**The asymmetry:** two quarters early on a domain that materializes → you shape the field. Two quarters late → you answer someone else's RFP. Early on a domain that doesn't materialize → recoverable. Costs are not symmetric; that's the whole argument.

---

## 2. The Decision Model

| Class | Question | Trigger |
|---|---|---|
| **Tempo** | Build or run? | Time-to-demand per domain (§2.1) |
| **Double down** | What deserves more? | Accelerating + existing capability |
| **Taper** | Declining return? | Decelerating or commoditizing + effort still allocated |
| **Exit** | Walk away? | Structural decline, or consolidation kills the standalone conversation |
| **Prop up** | Necessary but weak? | Weak alone, required as entry to a strong adjacent domain |
| **Watch** | Not yet actionable? | Signal present, confidence low, horizon too far |

### 2.1 Tempo windows
| Window | Posture |
|---|---|
| 0–2 qtr | **Run** — partner or resell; no build time |
| 3–4 qtr | **Build narrow** — focused offer or POV |
| 5–8 qtr | **Build deep** — real IP and methodology |
| 8+ qtr | **Watch** — track, don't spend |

**Every tempo window must carry a confidence tier and a stated basis.** A window derived from judgment must not render identically to a figure sourced from a filing. *(Added after self-review: visual consistency was implying evidentiary consistency that did not exist.)*

### 2.2 Decision hygiene
Every recommendation names its signal and tier. Every *changed* recommendation says what changed. Unchanged for three months → flagged for challenge.

---

## 3. Core Thesis Under Test

> Infrastructure leads; security trails by N quarters; governance trails security.

**Complication:** prior cycles had no early regulatory forcing function. This one does. Working hypothesis: **the lag is compressed relative to cloud.**

**Falsifiers (restate every run):** security accelerating *simultaneously* with infra; infra decelerating with no security response within 2–4 quarters; security growth driven by pricing/consolidation not volume; governance arriving *ahead* of security.

**Status: untested.** One period of data is a baseline, not a finding.

---

## 4. Vendor Universe (supply side)

### 4.1 Two-tier coverage model

**Core (14)** — full field capture, quarterly series, sparklines, feeds composite indices.
**Extended (8)** — headline revenue + guidance direction only. Exists to satisfy the three-vendor domain minimum without carrying full maintenance cost.

Rationale: breadth is required by the §6.1 domain rule, but full capture on 22 entities is unaffordable monthly. Tiering buys callable domains at bounded cost.

### 4.2 Domain × vendor coverage matrix

| Domain | Core | Extended | Callable? |
|---|---|---|---|
| Network security — appliance/converged | Palo Alto, Fortinet, Check Point | Juniper *(inside HPE — degraded)* | ✅ 3 |
| Network security — cloud SASE/SSE | Zscaler, Cloudflare, Palo Alto | Fortinet *(FortiSASE)* | ✅ 3 |
| Endpoint / XDR | CrowdStrike, SentinelOne | Trend Micro | ✅ 3 |
| SecOps / SIEM / MDR | CrowdStrike, Palo Alto, Cisco *(Splunk)* | Elastic, Rapid7, Datadog | ✅ 3+ |
| Exposure / vuln mgmt | Tenable | Qualys, Rapid7 | ✅ 3 |
| Data security / DSPM | Rubrik, Varonis | Commvault | ✅ 3 |
| Cloud security / CNAPP | Palo Alto, CrowdStrike | Tenable, Datadog | ✅ 3 |
| Identity — human | Okta, SailPoint | — | ⚠️ **2 — below minimum.** CyberArk absorbed into Palo Alto; Ping private; Microsoft Entra undisclosed. No third exists. |
| **Identity — non-human / agentic** | — | — | ❌ **0 public vendors.** Astrix→Cisco, Portkey→Palo Alto, Symmetry→Zscaler. Aembit, Oasis, Token, Britive all private. |
| **GRC / AI governance** | — | — | ❌ **0 public vendors.** Drata, Vanta, Credo AI, Holistic AI all private. |
| AppSec / supply chain | — | GitLab, Black Duck | ⚠️ 2 — weak public coverage |

**The finding this matrix produces:** the two domains rated **build deep** — the highest-value lanes in the analysis — have zero public vendor coverage. Earnings data is structurally blind to them. This is the load-bearing argument for §5.4.

### 4.3 Infrastructure (leading layer)
**Core:** Nvidia (silicon), Cisco (networking + security incumbent), Arista (networking), Dell (compute/platform), **Vertiv** (power & thermal).
**Extended:** Broadcom, HPE, Pure Storage, Supermicro.

*Vertiv is the non-obvious inclusion: power and thermal is the binding physical constraint on buildout, making it the earliest-moving signal in the stack — ahead of silicon.*

**Hyperscaler capex** (Microsoft, Amazon, Alphabet, Oracle, Meta) and **neoclouds** (CoreWeave, Nebius, Crusoe) are **demand context, not vendor performance.** Rendered separately; never mixed into vendor comparisons.

---

## 5. Demand-Side Signal Layer *(NEW)*

Every input in v0.3 was supply-side — vendors reporting on vendors. These four observe buyers, category formation, and capital allocation instead.

### 5.1 Vendor job postings
**Lead time: 2–4 quarters.** Companies staff a product line before it ships and long before it becomes a disclosed line item.

- **Source:** Greenhouse and Lever public boards for the Core 14. Both expose real JSON APIs (`boards-api.greenhouse.io/v1/boards/<token>/jobs`, `api.lever.co/v0/postings/<token>`), so this is structured, free, and not scraping. **Workday is not in that class** *(corrected 2026-08-14)*: its board data comes from a per-tenant CXS POST endpoint that changes without notice, and treating it as equivalent is how this input acquires the fragility the sentence claims it avoids. Cover Workday-hosted vendors by a separate adapter with an explicit "unavailable" state, and let the coverage note say so rather than showing a silent zero.
- **Metric:** open req count per company per domain keyword ("AI security," "non-human identity," "agent," "AI governance"), plus req *mix* shift quarter over quarter.
- **Read as:** commitment signal. A vendor tripling agent-security reqs is telling you where next year's revenue line comes from.
- **Confounds:** hiring freezes, layoffs, and offshoring move counts independently of demand. Always read as ratio-to-total-reqs, never absolute.
- **Confidence:** T3.

### 5.2 Earnings call transcript term frequency
**Lead time: ~4 quarters.** Narrative precedes revenue. Free, and reuses a source already being pulled.

- **Source:** quarterly call transcripts, Core 14.
- **Metric:** mentions per call of tracked terms; first-mention date per term per company; prepared remarks vs. Q&A *(prepared = strategy, Q&A = analyst pressure — different signals, track separately)*.
- **Read as:** when a term appears in every covered vendor's prepared remarks, it becomes a line item roughly a year later.
- **Confounds:** hype inflation. A term can saturate discourse without producing revenue — cross-check against §5.1 hiring.
- **Confidence:** T3.

### 5.3 Analyst category creation
**Lead time: 2–4 quarters. Possibly the strongest single signal on this list.**

- **Source:** Gartner Market Guides, Hype Cycle placements, Magic Quadrant creation; Forrester Wave initiation; IDC taxonomy additions.
- **Metric:** date a category is *named*; date it gets its first MQ/Wave; movement along the Hype Cycle.
- **Why it matters more than it looks:** naming a category makes it **RFP-able.** Procurement can now write it into a requirement, budget can be line-itemed against it, and vendors can be scored on it. That's the moment a category becomes purchasable — a sharper trigger than any revenue number.
- **Confounds:** analyst naming is partly vendor-influenced. Category creation ≠ category viability.
- **Confidence:** T4 for the event, T2 for what it implies.

### 5.4 Startup formation index *(the only instrument for uncovered domains)*
**Lead time: 8–12 quarters at seed; 4–6 at Series B.**

- **Source:** funding announcements — Crunchbase, PitchBook, or press releases as fallback.
- **Metric: domain-level aggregates only.** Count of newly funded companies per domain per quarter; total capital per domain; median round size; **and the category *names* used in announcements** *(category vocabulary forms in funding language a year before analysts name it — this connects directly to §5.3)*.
- **Hard scope limit — do not build a startup database.** Individual startups are noise; ~90% fail. Keep aggregates only. **Promote a company to named tracking only when it raises Series B+ or is acquired by a Core vendor.**
- **The acquisition payoff:** Cisco→Astrix, Palo Alto→Portkey, Zscaler→Symmetry were all observable as seed-stage formation 2–3 years before the deals. The startup layer tells you which domains incumbents will buy into next — which is a direct forward read on the tempo board.
- **Why this is load-bearing:** per §4.2, agentic identity and AI governance have zero public vendors. This is the only signal that observes them at all.
- **Confounds:** funding tracks capital-market appetite as much as demand. A funding boom in a domain can precede a bust. Weight formation *count* over dollars.
- **Confidence:** T3 for counts, T2 for interpretation.

### 5.5 Deferred inputs
| Input | Status | Why |
|---|---|---|
| Public-sector RFP language (SAM.gov, state portals) | **Deferred** | Genuine buyer-side demand signal and the natural SLED bridge. Revisit after the demand layer proves out. |
| Conference agenda composition (RSA, Black Hat) | **Deferred** | ~4 month lead; low effort. Add opportunistically. |
| Prediction markets | **Rejected** | No liquidity on enterprise software questions. Thin markets are noise wearing a probability. *Narrow exception:* high-volume regulatory markets feed the governance clock. |
| Distributor earnings (TD Synnex, Ingram) | **Candidate** | Sits closer to ePlus's actual position in the value chain than vendor earnings. Worth evaluating next revision. |
| Cyber insurance underwriting requirements | **Candidate** | Insurer mandates create purchases regardless of buyer enthusiasm — a genuine forcing function. |

### 5.6 Wildcard scenario — carried, not forecast
**A major agent-mediated breach.** Incident classes drive spend faster than any trend. One high-profile agentic compromise would collapse the governance tempo window from 5–8 quarters to ~2. Unpredictable in timing, highly predictable in effect. **Carry as a standing scenario on the tempo board, never as a forecast.**

---

## 6. Captured Fields

**Point-in-time:** revenue + YoY/sequential; segment revenue; margins; billings.
**Forward (weighted higher):** RPO/cRPO; net new ARR; ARR growth; NRR/DBNER; guidance direction and magnitude; **next-period guide vs. current growth rate** *(deceleration detector)*; capex guidance revisions; orders/backlog/purchase commitments.
**Emerging-segment disclosure:** vendor-defined "emerging"/"next-gen" buckets, captured verbatim with the vendor's own definition attached. Never aggregate across vendors — definitions differ.
**Demand-side (§5):** req counts by domain keyword; transcript term counts; analyst category events; startup formation counts by domain.
**Provenance (mandatory):** `source_url`, `filing_type`, `period_end`, `captured_at`, `confidence` T0–T5.

### 6.1 Minimum coverage threshold
**A domain heat call requires 3+ covered entities with material exposure.** Below three → marked `INSUFFICIENT COVERAGE`, no direction, and **no tempo window may be published for it from supply-side data alone.** Domains at zero public coverage (§4.2) may be assessed only from §5 demand-side signals, at correspondingly lower confidence.

*This rule exists because the prototype called an "appliance-led acceleration" off Fortinet alone. Check Point inverted it.*

---

## 7. Derived Analytics

**Composites:** Infra Growth Index; Security Growth Index; **Spread** = Infra − Security; Hyperscaler Capex Index.
**Organic adjustment (mandatory):** publish reported and acquisition-adjusted side by side. The gap measures how much apparent demand is consolidation.
**Lag estimation:** cross-correlation, lags 0–8 quarters. *Carry the caveat every run* — directionally suggestive, never a fitted constant.
**Domain heat:** subject to §6.1.
**Time-to-demand:** per domain, with confidence tier and stated basis (§2.1).

### 7.5 Share-shift vs. category-shift decomposition *(mandatory)*
| Pattern | Interpretation | Implication |
|---|---|---|
| All covered vendors moving together | **Category shift** — real demand movement | Feeds lag thesis and tempo board |
| Some up, some down, offsetting | **Share shift** — competitive rotation | Changes *which vendor* to lead with. Does **not** move tempo. |
| Mixed with net movement | Both | Separate components before concluding |

*Demonstration: Fortinet product +52% / Check Point −14%; Cloudflare +36% / Zscaler guide 16.5%. Read as category shifts these say "appliances are back, cloud SASE is dying." Decomposed correctly: **demand is stable, share is rotating.***

### 7.6 Cross-signal corroboration *(new, enabled by §5)*
A domain call gains a tier when supply and demand signals agree, and loses one when they diverge. Divergence is itself informative:

| Pattern | Meaning |
|---|---|
| Hiring ↑ + transcripts ↑ + revenue flat | **Demand is coming.** The build window is still open. |
| Transcripts ↑ + hiring flat | **Narrative without commitment.** Hype, discount it. |
| Startup formation ↑ + analyst category named | **Category forming now.** 2–4 quarters to RFP-able. |
| Revenue ↑ + hiring ↓ | **Harvest phase.** Late; window closed. |

---

## 8. Output Architecture

**Principle:** one core read, audience-neutral. Cuts derive from core; core never derives from cuts.

**8.2 Store** — append-only fact table, `entity | layer | domain[] | period_end | metric | value | unit | yoy_pct | organic_flag | source_url | confidence_tier | captured_at`. Companion tables: `entities`, `events`, `signals` *(new — demand-side series)*, `calendar`, `runs`.

**8.3 Scorecard (HTML)** — the layer actually read monthly. Generated from the store, never hand-authored. Demand context (capex, spread) rendered distinctly from vendor performance. Sparkline per entity; honest empty state where no series exists.

**8.4 Brief (Markdown)** — reasoning and evidence, 1,200–1,800 words. Sections: The Call · Lag Scorecard · Share vs. Category · Domain Heat · Tempo Board · Demand-Side Signals · Vendor Movements · Infrastructure & Capex · Governance Watch · Deltas · Watch List · Coverage Gaps.

**8.5 Cuts** — A Universal · B ePlus National · C **ePlus West** *(ships v1; NorCal leads national by 1–2 quarters, so this is the early-warning instrument for Cut B)* · D Personal *(optional)* · E SLED *(deferred; §4.4 calendar inputs added regardless)*.

---

## 9. Cadence

Monthly. Heavy months (Feb/May/Aug/Nov) carry Layer 2 earnings clusters. **Demand-side signals (§5) refresh monthly regardless of earnings calendar — which materially improves light-month value.** Rolling state: the brief reflects the full current picture, not just the last 30 days. Run log declares coverage completeness and staleness.

---

## 10. Quality Rules

1. Provenance or it doesn't ship.
2. Confidence tiers are load-bearing — never flatten them into one voice.
3. Forward indicators outrank trailing.
4. Three-vendor minimum per domain call (§6.1).
5. Decompose share vs. category before concluding (§7.5).
6. Publish organic alongside reported.
7. **Every tempo window carries a tier and a stated basis.**
8. The thesis must be falsifiable every month.
9. Distinguish "no signal" from "negative signal."
10. **Aggregates only for startups — no entity database below Series B.**
11. Core carries no recommendations; cuts carry no unsourced claims.
12. No investment advice.

---

## 11. Open Decisions

| ID | Decision | Status |
|---|---|---|
| D-1 | Layer 2 breadth | **Resolved.** Two-tier: Core 14 / Extended 8. |
| D-2 | Backfill depth | **Open — gates everything.** Recommend 12 quarters; 8 minimum for seasonality separation. |
| D-3 | Composite weighting | Revenue-weighted + equal-weighted published together; divergence is signal. |
| D-9 | Vendors absorbed by acquisition (CyberArk) | Recommend **freeze + annotate**, don't rewrite history into the acquirer. |
| D-10 | Emerging-segment definitions vary | Capture verbatim with vendor definition; never aggregate. |
| **D-11** | **Startup data source** | **Open.** Crunchbase/PitchBook are paid. Press-release fallback is free but lossy. Decide before §5.4 build. |
| **D-12** | **Analyst source access** | **Open.** Gartner/Forrester are paywalled. Does ePlus have a seat? Public Hype Cycle summaries are a partial substitute. |
| **D-13** | **Identity domain is uncallable at 2 vendors and no third exists** | **Open.** Accept the gap, or bridge it with §5 demand-side signals at lower confidence? Recommend the latter, explicitly tiered. |

---

## 12. Success Criteria

After two quarters:
- Called a domain inflection before consensus, evidence in the record
- The lag estimate moved on data, not pinned to the opening assumption
- At least one **tempo change** that altered what you actually did
- A recommendation reversed by new signal, defensibly
- ✅ **A share-shift correctly distinguished from a category-shift** *(already achieved in prototype — the reason §7.5 exists)*
- **A demand-side signal (§5) contradicted a supply-side read, and the contradiction proved informative**
- Someone else could reconstruct the reasoning from the store without you
