# Governing Intent

## Control

- **Intent ID:** `SEC-MARKET-001`
- **Version:** `1.4`
- **Lifecycle state:** `accepted`
- **Gate 1:** `passed`
- **Supersedes:** `SEC-MARKET-001` v1.3
- **Created:** 2026-08-15
- **Last reconciled:** 2026-09-25 — purpose, readers, scope and success brought in line with the owner's product core (`docs/active/product-core.md`); v1.3's autonomy rule unchanged

## Compressed governing intent

> Give security leaders, and the people who advise and sell to them, a current, sourced picture of the business of the security market: who is growing, stalling, consolidating, being bought, or in financial trouble, so they can see which suppliers in each domain are on solid footing. Built from public national and global evidence with transparent provenance, and published automatically as facts.

**State:** `Decided`

## Purpose

Security Market Pulse is first a credibility asset for the owner's advisory work and a working instrument he uses himself for supplier and domain decisions: for each security domain, which suppliers are on solid footing and what the public evidence says about why. It moves security planning from reactive response toward informed preparation, and it earns trust by being accurate, fresh and epistemically honest.

## Desired outcome

Security leaders and the people who advise them use current, sourced market facts to decide which suppliers deserve attention, what to prepare for, and what to question. The look back covers the last three to six months of what actually happened, in filings and public numbers; the facts shown are the ones that bear on the next three to six months.

## Value

- Security leaders can see whether the suppliers they buy from are growing, stalling, consolidating, being absorbed or in financial trouble, before it reaches them as a renewal, a support change or a surprise.
- The owner, his colleagues and vendor partner teams can ground supplier recommendations and client conversations in current evidence rather than impression.
- Anyone who wants a practitioner's pulse on the security market gets one that is sourced and current.

## Beneficiaries

| Tier | Reader | What they come for |
|---|---|---|
| 1. Written for | Security leaders and decision makers: chief information security officers, security architects, people running a security program | What is happening in the market they buy from; who is growing, fading, being absorbed, or might not be here in two years |
| 2. Also for | People who advise and sell to tier 1: the owner, his colleagues and leadership at his employer, vendor partner teams | The same picture, used to decide which suppliers to build around and what to bring to a client conversation |
| 3. Welcome | Anyone who wants a practitioner's pulse on the security market | The same |

Investors are not a designed-for reader, and the site gives no investment advice. The core is not geographically constrained. Regional differences may later justify tuned views, but they do not limit who may benefit or which national and global signals belong in the core.

## Observable success

In order of priority:

1. **Fresh without fail.** Every scheduled update ran; the newest fact is days old, never weeks; a failed or incomplete run is visibly distinct from a quiet week. If this is not true, nothing else counts.
2. **Covered.** Each declared domain lists its declared suppliers with current footing facts, and what is not covered is stated.
3. **Used.** Readers return and share it, people write in with requests, and the owner uses it in meetings and introductions and it holds up. Measuring return visits, sharing and engagement is allowed and wanted; measuring raw traffic is not the goal.
4. **Reconstructable.** Another person can trace every fact to its public source.

Decisions changed by the site are welcome evidence and may be logged, but are not a current measure. Completing agents, a website, reports, or other deliverables alone does not constitute success.

## Boundaries and constraints

### Must remain true

- Initial outputs use public, publishable information.
- Market observation may be national or global.
- Claims preserve provenance, uncertainty, conflicting evidence, and credible alternatives.
- Forward-looking judgments appear only when the owner writes them himself, and must label their confidence and basis.
- Public intelligence augments rather than replaces client conversations, pipeline evidence, partner information, and local judgment.
- Scope remains practical enough to learn and deliver value incrementally.
- A machine may retrieve, extract, validate and publish sourced facts on its own schedule, with automated checks as the only publishing gate and no human approval step. A machine does not publish judgments: no stances, rankings, forecasts, or interpretation of what a fact means.

### Covers

- The business of the security market, from public information: earnings and growth by supplier; funding; acquisitions and consolidation; distress, meaning debt, ratings actions, layoffs, restructuring and shutdowns; platform moves; and, for each security domain, the tracked suppliers' footing. AI security is covered as a market (who buys whom, what is actually revenue), not as news.
- The founding question, whether security spending lags infrastructure spending, is one standing analysis kept as a dated record, not the site's organizing question.

### Explicitly out of scope

- Daily security news, vulnerabilities, breaches as events, product reviews and technical evaluations. It is a market pulse, not a news site.
- Revenue is not a current goal. It may be explored once an audience exists, never at the expense of an unbought reading of the evidence.
- Client-identifying or confidential ePlus information in the initial core.
- Investment advice.
- Partner-risk monitoring as the primary project outcome.
- A requirement to perfect regional or audience-specific tuning before the core proves useful.

### Must not optimize

- Automation, output volume, coverage breadth, traffic, or apparent certainty at the expense of decision value and trust.
- Citation quantity or institutional prestige as a substitute for relevant, independent evidence.
- A forced market call when the available evidence cannot support one.

## Assumptions

| Assumption | Basis | Consequence if false | Validation owner or path |
|---|---|---|---|
| Public information can produce sufficiently early and actionable signals | Working specifications and initial research | Source strategy or intended scope must change | Test through two quarters of operation |
| Infrastructure, investment, hiring, financial, analyst, and market signals can reveal future cybersecurity needs across multiple horizons | Current market thesis; not yet proven | The signal model and possibly the desired outcome require reconciliation | Maintain falsifiers and test against observed outcomes |
| A common intelligence core can serve multiple beneficiaries through later tuning | Audience-neutral core proposed in the workflow spec | Separate products or intents may be required | Observe beneficiary use and feedback |
| Regional differences can be handled as later tuning rather than core segmentation | Current human judgment | Earlier segmentation may become necessary | Revisit when evidence shows materially different needs |

## Unknowns

| Unknown | Blocking? | Why it matters | Resolution path |
|---|---|---|---|
| Longer-term distribution beyond the website, including newsletters | no | May extend reach after the core website proves useful | Learn from actual use |
| Autonomous-agent architecture | no | Affects implementation and maintainability | Decide during downstream design |
| Detailed confidence and evidence-weighting rubric | no | Affects consistency and trust | Develop and test without changing the transparency boundary |
| Audience- or region-specific views | no | May improve relevance after the core proves useful | Learn from actual use |
| Future partner-risk monitoring | no | May create additional value but is not primary | Keep as uncommitted backlog |
| Potential confidential overlays | no | Could support account-specific action but changes governance | Reconcile intent and confidentiality before introduction |

## State register

| Item | State | What it may influence | Promotion condition |
|---|---|---|---|
| Public, publishable initial core | Decided | All downstream scope | New accepted intent version |
| National and global market observation | Decided | Source and analysis scope | New accepted intent version |
| Transparent, calibrated judgments | Decided | Reasoning and output behavior | New accepted intent version |
| A standing supplier tracker updated as facts change, with a machine-generated weekly change log, as the unit of product (replaces the signed weekly issue; `SEC-MARKET-AUTO-001`) | Decided | Product shape, cadence, presentation | New accepted intent version |
| Autonomous worker agents and reasoning layer | Decided: gather, validate and publish sourced facts with no human approval step; judgments are published only when the owner writes them | Implementation | New accepted intent version |
| Responsive public-data website | Decided | MVP presentation and distribution | New accepted intent version |
| Audience- or region-specific views and newsletters | Decided for a named pilot list; public distribution follows four held issues | Presentation and distribution | Owner decision at the 2026-10-08 review |
| Partner-risk monitor | Exploring | Potential backlog | Separate prioritization and scope decision |
| Confidential client overlay | Exploring, with a decided boundary: built downstream inside ePlus surfaces, never in the core, never on this domain | Potential future product boundary | Explicit reconciliation and governance decision |

## Dual acceptance

### Human Acceptance

- **Result:** accepted
- **Statement:** “Yes, this represents what I’m trying to achieve and what I value.”
- **Accepted by:** project owner
- **Date:** 2026-08-15

### Delivery Acceptance

- **Result:** accepted
- **Statement:** “yes this represents what i want to use”
- **Requirement:** maintain attribution and access to supporting research and evidence
- **Date:** 2026-08-16
- **v1.2 Human Acceptance:** accepted — "approve the intent v1.2 text as written" — project owner, 2026-09-03
- **v1.4 Human Acceptance:** accepted — "go, and apply the four intent amendments" (purpose, readers, scope, success, as proposed in `docs/active/autonomy-coverage-plan.md` section 2) — project owner, 2026-09-25
- **v1.3 Human Acceptance:** accepted — "Source check facts can publish. I don't want to be the bottleneck for this. So it needs to be automated. There doesn't need to be any gates." Asked what the machine may say beyond facts, the owner chose "facts only, no judgments", and approved rewriting this file and the project rules to match — project owner, 2026-09-25

### AI Readiness

- **Result:** ready
- **Statement:** “Yes. I have sufficient context to reason and act against this intent without filling consequential gaps with assumptions.”
- **Agent or model:** GPT-5.6 Sol
- **Date:** 2026-08-15
- **Reconfirmed for v1.1:** ready — website delivery, attribution, and evidence-access requirements are explicit
- **Reconfirmed:** 2026-08-16
- **Reconfirmed for v1.2:** ready — the weekly issue, the machine-proposes / person-signs line, the pilot list and the downstream ePlus boundary are explicit; purpose, beneficiaries and the public-evidence boundary are unchanged
- **Agent or model:** Claude Fable 5.1, sec-market orchestrator session
- **Reconfirmed:** 2026-09-03
- **Reconfirmed for v1.3 and v1.4:** ready — facts publish automatically with checks as the only gate, no machine judgments, security leaders first, distress and consolidation in scope, freshness as the first test of success
- **Agent or model:** Claude Opus 5.5, sec-market orchestrator session
- **Reconfirmed:** 2026-09-25

## Traceability and handoff

- **Originating source documents:** [security-signal-workflow-spec-v0.4.md](docs/archive/security-signal-workflow-spec-v0.4.md); [security-signal-BUILD-SPEC-v1.0.md](docs/archive/security-signal-BUILD-SPEC-v1.0.md); Gate 1 discussion completed 2026-08-15
- **Downstream items governed:** Existing specifications require review against this intent. In particular, the build spec's partner-risk-first Phase 1 conflicts with the accepted priority and is not authorized merely by its presence in that document.
- **Reconciliation events:** `SEC-MARKET-RECON-001` resolved 2026-08-15; Episode 001 reclassified as thematic, governing intent unchanged
- **Current operational validation:** `SEC-MARKET-SIG-002` v0.2 completed and independently reviewed; stable infrastructure-to-security lag remains `NO-CALL`
- **Current MVP delivery:** `SEC-MARKET-WEB-001` — responsive evidence-linked website
- **Current product direction:** `SEC-MARKET-AUTO-001` ([autonomy-coverage-plan.md](docs/active/autonomy-coverage-plan.md)) — a standing supplier tracker across declared domains, published automatically as validated facts. `SEC-MARKET-WEEKLY-001` (the signed weekly issue) is superseded; signed issue `2026-w36` and the thesis record stay as a dated archive.
- **Fresh-agent minimum context:** [README.md](README.md), this artifact, [product-core.md](docs/active/product-core.md), [autonomy-coverage-plan.md](docs/active/autonomy-coverage-plan.md), [intent-reconciliation-2026-08-15.md](docs/active/intent-reconciliation-2026-08-15.md), the Episode 002 packet in [docs/episodes/002/](docs/episodes/002/), and [outcome-architecture.md](docs/reference/outcome-architecture.md). Consult historical specifications only for hypotheses and proposed mechanisms.

## Revision record

| Version | State | Change rationale | Human Acceptance | AI Readiness | Supersession impact |
|---|---|---|---|---|---|
| 1.0 | accepted | Establish governing authority for the new project | accepted, 2026-08-15 | ready, 2026-08-15 | Existing working and build specifications require downstream review |
| 1.1 | accepted | Promote the responsive evidence-linked website from Exploring to Decided for MVP delivery | accepted, 2026-08-16 | ready, 2026-08-16 | Website becomes the primary MVP consumption surface; purpose and evidence boundaries unchanged |
| 1.2 | accepted | Weekly issue as the unit of product; agent-drafted gather with a named person signing; newsletter to a named pilot list; ePlus overlay bounded downstream | accepted, 2026-09-03 | ready, 2026-09-03 | Episode 002 call becomes a standing thesis; purpose, beneficiaries and evidence boundaries unchanged |
| 1.4 | accepted | Purpose becomes a credibility asset and working instrument for supplier and domain decisions; security leaders first, investors out; scope adds distress and consolidation and excludes news; success led by freshness; standing tracker replaces the signed weekly issue (D-77) | accepted, 2026-09-25 | ready, 2026-09-25 | Account-team GTM timing is no longer the organizing purpose; the thesis becomes a dated record; the public-evidence boundary and v1.3 autonomy rule unchanged |
| 1.3 | accepted | Remove the human approval step: sourced, machine-validated facts publish automatically; the machine publishes no judgments; judgments appear only when the owner writes them (D-76) | accepted, 2026-09-25 | ready, 2026-09-25 | The publish-on-approval path, signing and dated machine-proposed stances are superseded; purpose, beneficiaries and the public-evidence boundary unchanged |

## Gate result

- **Gate 1:** passed
- **Reason:** Human Acceptance and AI Readiness are explicit; the intended outcome, beneficiaries, success evidence, boundaries, assumptions, and non-blocking unknowns are sufficiently clear for a fresh agent to proceed without consequential invention.
- **Authorized next interface if passed:** satisfied by `SEC-MARKET-OA-001`; current project status and next authority are in [README.md](README.md) and [status.md](status.md)
