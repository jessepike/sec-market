# Governing Intent

## Control

- **Intent ID:** `SEC-MARKET-001`
- **Version:** `1.3`
- **Lifecycle state:** `accepted`
- **Gate 1:** `passed`
- **Supersedes:** `SEC-MARKET-001` v1.2
- **Created:** 2026-08-15
- **Last reconciled:** 2026-09-25 — the pipeline publishes sourced, machine-validated facts on its own with no human approval step; the machine publishes no judgments

## Compressed governing intent

> Enable security leadership, account teams, and clients to recognize consequential cybersecurity market shifts early enough to make better-timed GTM, account, and technology decisions. Use public national and global evidence interpreted with transparent provenance, confidence, uncertainty, and relevance.

**State:** `Decided`

## Purpose

Move cybersecurity planning from reactive response toward informed preparation while earning trust through useful, early, and epistemically honest market intelligence.

## Desired outcome

Security leaders, account teams, and clients use credible market insight to decide what to prioritize, prepare, investigate, influence, or defer across horizons ranging from the present through 24 months.

## Value

- Security leadership, including Client Security Principals (CSPs), can better allocate attention and resources, develop GTM motions, and establish informed market positions.
- Sales and account teams can improve account planning and sustain relevant client conversations.
- Clients can make better-informed technology, timing, and partner decisions.

## Beneficiaries

| Beneficiary | Value received | Relevant behavior or condition change |
|---|---|---|
| Security leadership and CSPs | Earlier, better-supported market direction | Priorities, preparations, and GTM choices respond to evidence before demand is obvious |
| Sales and account teams | Timely, credible conversation context | Market insight informs account planning and meaningful client conversations |
| Clients | Additional decision context | Market evidence informs technology, timing, and partner choices |

The core intelligence is not geographically constrained. Regional differences may later justify tuned views or interpretation, but they do not limit who may benefit or which national and global signals belong in the core.

## Observable success

Within two quarters, evidence shows that the intelligence has:

- changed or accelerated a GTM or resource decision;
- supported a meaningful account-team client conversation;
- helped a client evaluate technology, timing, or partner choices; and
- produced reasoning another person can reconstruct from its evidence.

Completing agents, a website, reports, or other deliverables alone does not constitute success.

## Boundaries and constraints

### Must remain true

- Initial outputs use public, publishable information.
- Market observation may be national or global.
- Claims preserve provenance, uncertainty, conflicting evidence, and credible alternatives.
- Forward-looking judgments appear only when the owner writes them himself, and must label their confidence and basis.
- Public intelligence augments rather than replaces client conversations, pipeline evidence, partner information, and local judgment.
- Scope remains practical enough to learn and deliver value incrementally.
- A machine may retrieve, extract, validate and publish sourced facts on its own schedule, with automated checks as the only publishing gate and no human approval step. A machine does not publish judgments: no stances, rankings, forecasts, or interpretation of what a fact means.

### Explicitly out of scope

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
| Weekly issue as the unit of product | Decided | Product shape, cadence, presentation | New accepted intent version |
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

## Traceability and handoff

- **Originating source documents:** [security-signal-workflow-spec-v0.4.md](docs/archive/security-signal-workflow-spec-v0.4.md); [security-signal-BUILD-SPEC-v1.0.md](docs/archive/security-signal-BUILD-SPEC-v1.0.md); Gate 1 discussion completed 2026-08-15
- **Downstream items governed:** Existing specifications require review against this intent. In particular, the build spec's partner-risk-first Phase 1 conflicts with the accepted priority and is not authorized merely by its presence in that document.
- **Reconciliation events:** `SEC-MARKET-RECON-001` resolved 2026-08-15; Episode 001 reclassified as thematic, governing intent unchanged
- **Current operational validation:** `SEC-MARKET-SIG-002` v0.2 completed and independently reviewed; stable infrastructure-to-security lag remains `NO-CALL`
- **Current MVP delivery:** `SEC-MARKET-WEB-001` — responsive evidence-linked website
- **Current product direction:** `SEC-MARKET-WEEKLY-001` — the weekly issue is the unit of product. The Episode 002 market call is a standing thesis scored by each weekly issue, not the site headline.
- **Fresh-agent minimum context:** [README.md](README.md), this artifact, [intent-reconciliation-2026-08-15.md](docs/active/intent-reconciliation-2026-08-15.md), the Episode 002 packet in [docs/episodes/002/](docs/episodes/002/), and [outcome-architecture.md](docs/reference/outcome-architecture.md). Consult historical specifications only for hypotheses and proposed mechanisms.

## Revision record

| Version | State | Change rationale | Human Acceptance | AI Readiness | Supersession impact |
|---|---|---|---|---|---|
| 1.0 | accepted | Establish governing authority for the new project | accepted, 2026-08-15 | ready, 2026-08-15 | Existing working and build specifications require downstream review |
| 1.1 | accepted | Promote the responsive evidence-linked website from Exploring to Decided for MVP delivery | accepted, 2026-08-16 | ready, 2026-08-16 | Website becomes the primary MVP consumption surface; purpose and evidence boundaries unchanged |
| 1.2 | accepted | Weekly issue as the unit of product; agent-drafted gather with a named person signing; newsletter to a named pilot list; ePlus overlay bounded downstream | accepted, 2026-09-03 | ready, 2026-09-03 | Episode 002 call becomes a standing thesis; purpose, beneficiaries and evidence boundaries unchanged |
| 1.3 | accepted | Remove the human approval step: sourced, machine-validated facts publish automatically; the machine publishes no judgments; judgments appear only when the owner writes them (D-76) | accepted, 2026-09-25 | ready, 2026-09-25 | The publish-on-approval path, signing and dated machine-proposed stances are superseded; purpose, beneficiaries and the public-evidence boundary unchanged |

## Gate result

- **Gate 1:** passed
- **Reason:** Human Acceptance and AI Readiness are explicit; the intended outcome, beneficiaries, success evidence, boundaries, assumptions, and non-blocking unknowns are sufficiently clear for a fresh agent to proceed without consequential invention.
- **Authorized next interface if passed:** satisfied by `SEC-MARKET-OA-001`; current project status and next authority are in [README.md](README.md) and [status.md](status.md)
