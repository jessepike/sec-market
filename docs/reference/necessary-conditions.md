# Necessary Conditions

## Control

- **Model ID:** `SEC-MARKET-NC-001`
- **Version:** `0.1`
- **Lifecycle state:** `consolidated draft`
- **Gate 2:** `not independently active`
- **Governing intent:** `SEC-MARKET-001` v1.0, accepted 2026-08-15
- **Created:** 2026-08-15
- **Consolidated into:** `SEC-MARKET-OA-001` v0.1 in [outcome-architecture.md](outcome-architecture.md)

> **Handoff notice:** This exploratory model is retained as supporting reasoning. Its decision-episode, warranted-judgment, timely-advantage, and reasoned-uptake concepts have been reconciled into [outcome-architecture.md](outcome-architecture.md), which is the sole active Gate 2 candidate.

## Candidate minimum sufficient model

> Given influenceable decisions, observable public evidence, and access to beneficiaries, the project must turn attributable evidence into warranted market judgments that provide a timely decision advantage and fit a live decision context. Beneficiaries must then incorporate those judgments alongside their other evidence before the relevant commitment. Success exists only when that use produces observable decision impact.

This model is **Hypothesizing** until accepted. It describes causal conditions, not a solution architecture. Its necessity can be reasoned about now; its sufficiency must be demonstrated empirically.

No project can guarantee beneficiary behavior or decision impact. P1–P3 and C1–C4 create the minimum causal opportunity for B1 and the intended outcomes; they do not make those outcomes logically inevitable.

## Causal chain

```text
Influenceable decision opportunities
        +
Observable public evidence
        +
Access to beneficiaries and decision contexts
        ↓
Acquired, preserved, and attributable evidence
        ↓
Warranted, reconstructable market judgment
        ↓
Timely decision advantage
        ↓
Fit and availability in a live decision
        ↓
Reasoned beneficiary uptake
        ↓
Observable GTM, account, or client decision impact
```

## 1. Prerequisites

Prerequisites are not outcomes the project is trying to create. They must hold sufficiently for progress to be possible.

| ID | Prerequisite | Current standing | If absent |
|---|---|---|---|
| **P1** | Each beneficiary context—security leadership, account teams, and clients—has at least one consequential and still-influenceable decision episode within the accepted present-to-24-month horizon | Plausible but unvalidated until concrete episodes are identified | That beneficiary outcome cannot be tested |
| **P2** | Public, publishable evidence potentially relevant to each selected decision episode exists and can support the resulting output | Plausible based on existing source research, but lead value remains unvalidated | If no publishable public evidence can inform a beneficiary context, the intent or source boundary requires reconciliation |
| **P3** | A path exists for each beneficiary context to receive insight before commitment and for contribution to be observed without introducing confidential data into the public core | Plausible for leadership and account teams; unvalidated for clients | That beneficiary outcome has no valid observation path |

The stronger proposition that public evidence is consistently early enough is an assumption to test, not a prerequisite that must be proven before work begins.

P1–P3 must eventually hold for all three beneficiary contexts because the accepted intent currently requires outcome evidence in all three. They need not all be fully validated before bounded learning begins.

## 2. Conditions the project must create

### C1 — Attributable evidence

Potentially consequential public, publishable evidence is acquired, preserved, and represented with enough provenance, temporal context, scope, and source-dependence disclosure to support interpretation or an explicit no-call.

Nominal corroboration does not count as independent support when multiple sources repeat the same underlying claim. Without C1, there is no trustworthy basis for insight.

### C2 — Warranted judgment

Evidence becomes a reconstructable, decision-relevant judgment that:

- distinguishes observation from inference;
- names the relevant decision posture, such as prioritize, prepare, investigate, influence, defer, or no-call;
- states its horizon, basis, evidence independence, confidence, uncertainty, conflicts, credible alternatives, and falsifiers; and
- can be revised when new evidence arrives.

Without C2, the project produces information rather than decision intelligence.

### C3 — Timely decision advantage

The judgment becomes available early enough—and is materially clearer or more useful than the beneficiary's existing information—to preserve an opportunity to prepare, influence, choose, or defer.

Earlier is not automatically better. The required lead time and acceptable error cost depend on the decision. “Timing beats accuracy” is therefore a hypothesis to test by decision class, not a universal rule.

Before C3 can be evaluated for a selected decision, that decision must have an explicit comparison baseline for “early enough” and an accepted error-cost posture.

Without C3, the project can explain the market but cannot improve timing.

### C4 — Decision fit and availability

For each beneficiary context, a warranted judgment reaches an appropriate beneficiary before commitment and is understandable and relevant to a specific:

- GTM or resource decision;
- account plan or client conversation; or
- client technology, timing, or partner evaluation.

The condition does not require a website, newsletter, regional cut, or any other particular channel.

Without C4, valid intelligence remains unused potential.

## 3. Jointly controlled bridge condition

### B1 — Reasoned uptake

The beneficiary incorporates the judgment alongside other relevant available evidence, which may include pipeline, partner, client, local, and professional evidence, when considering a live decision.

Delivery, readership, or the occurrence of a conversation does not establish uptake. Uptake requires a traceable contribution to understanding, evaluation criteria, timing, a next action, or the decision itself.

The project can create the opportunity and support appropriate use; it cannot control the beneficiary's final behavior.

## 4. Later validation evidence

Validation evidence tests whether the prerequisites and created conditions hold. It is not, by itself, evidence that the governing outcome occurred.

| Evidence | What it validates |
|---|---|
| A second person can reconstruct a judgment from its cited evidence | C1 and C2 |
| Observation and inference, evidence confidence and interpretive confidence, uncertainty, alternatives, and falsifiers remain distinguishable | C2 |
| Point-in-time evaluation uses only evidence available before the stated cutoff | C2 and C3 |
| Multiple positive cases, healthy controls, false-positive behavior, calibration, and appropriate abstention are examined | C2 and C3 |
| The judgment was available before the relevant decision point | C3 and C4 |
| The beneficiary can state what the insight clarified or what they would consider differently | C4 and readiness for B1 |
| The model can reverse or revise a judgment when falsifying evidence appears | C2 |
| “No signal,” “negative signal,” share shift, and category shift remain distinct | C2 |
| Reproducibility, idempotency, and operational health are demonstrated | A chosen recurring implementation, if those properties become relevant |

A backtest, running pipeline, scorecard, or published report can validate part of the causal model but cannot prove decision impact.

## 5. Ultimate outcome evidence

Under the accepted intent, success within two quarters requires observable evidence that:

1. a GTM or resource decision changed or accelerated;
2. an account-team client conversation was meaningfully supported;
3. a client technology, timing, or partner evaluation was helped; and
4. the reasoning contributing to those outcomes remains reconstructable.

The first three are beneficiary outcome evidence. The fourth is an integrity condition that must accompany them.

**Proposed Gate 2 operationalization:** “meaningfully supported” and “helped” should require a traceable contribution to changed understanding, evaluation criteria, timing, a next action, or a decision—not merely delivery or conversation occurrence. This proposal requires project-owner acceptance; it does not silently change the accepted intent.

As currently written, the governing intent requires evidence across all three beneficiary contexts, not merely one qualifying event in any one context. Changing that requirement would require intent reconciliation.

## 6. Reconciliation with existing project work

### Retained as causal or quality knowledge

- Multiple decision horizons and explicit postures from the workflow spec.
- Provenance, confidence, uncertainty, falsifiers, and the ability to make no call.
- Supply- and demand-side corroboration as a candidate way to improve warrant and timing.
- Distinguishing share shift from category shift and no signal from negative signal; controlling for acquisition or financial-presentation distortions when material.
- Coverage gaps and the rule that insufficient coverage must remain visible.
- One audience-neutral intelligence core with later tuned views as an assumption to test.
- Point-in-time evaluation, leakage prevention, multiple calibration cases, healthy controls, reproducibility, and operational-health concepts from the build spec.
- The public-core confidentiality boundary; any future representation of exposure remains a mechanism decision.

### Revised in status or interpretation

- The workflow's decision classes are candidate expressions of C2, not yet a required taxonomy.
- Three-vendor minimums, confidence tiers, backfill depths, cadence, and source lists are candidate validation or design choices, not universal necessary conditions.
- Workflow success criteria such as calling an inflection, moving a lag estimate, or reversing a recommendation validate analytical quality; they do not by themselves establish beneficiary outcomes.
- The build spec's Varonis backtest and unattended-run gate validate a partner-risk implementation, not the accepted governing outcome.
- “Timing beats accuracy” applies only where the cost asymmetry of a particular decision supports it.
- “No synthesis until Phase 4” must not prevent C2. The governing boundary prohibits unsupported or falsely certain synthesis, not reasoned interpretation.

### Conflicts

- The build spec makes partner-risk monitoring the first phase and gate to later market-intelligence work. The accepted intent explicitly says partner-risk monitoring is not the primary outcome. The governing intent wins; the existing Phase 1 order is not authorized.
- A pipeline or monitor can satisfy its technical acceptance tests while producing no C4, B1, or outcome evidence.
- Treating West or NorCal as the required early-warning cut would impose a geographic constraint that the accepted intent rejected.

### Deferred without blocking Gate 2

- Partner-risk monitoring as a possible later use case.
- Website, newsletters, autonomous agents, audience cuts, and regional views.
- Database, schema, scheduling, runtime, cadence, and deployment choices.
- Full-domain coverage, startup and analyst sources, composite indices, and lag automation.
- Paid-source access, confidential overlays, and external-publication governance.

## 7. Active assumptions and non-blocking unknowns

| Item | State | Why it does not yet block |
|---|---|---|
| Public evidence can provide useful lead time | Assumption under test | Existing sources support bounded experiments |
| One common core can serve all three beneficiary groups | Assumption under test | Initial use can reveal where tuning or separation is necessary |
| First live decision episode | Provisionally resolved in [outcome-architecture.md](outcome-architecture.md) | The selected security-leadership lane supports gap analysis and may be refined before final intervention selection |
| What baseline defines “early enough” or “better-timed” | Unknown | It can be defined relative to each selected decision |
| What false-positive cost is acceptable | Unknown | It varies by reversible versus irreversible decision |
| How client contribution will be observed without confidential data in the core | Unknown | Account-mediated observation is a viable hypothesis |
| Detailed evidence and confidence rubric | Unknown | Minimum semantics are defined in C2; implementation can mature through testing |
| When the accepted two-quarter outcome clock begins | Unknown | It must be decided before outcome evaluation begins, not before accepting the causal model |

No current unknown blocks acceptance of this necessary-conditions model. An unknown becomes blocking only when it prevents a selected intervention from satisfying a prerequisite or created condition.

## 8. Gate 2 result

- **Gate 2:** `consolidated into SEC-MARKET-OA-001`
- **Historical acceptance test:** The project owner agrees that P1–P3 and C1–C4 create the minimum causal opportunity for B1 and the intended outcomes; that empirical sufficiency remains to be tested; that validation evidence and outcome evidence are correctly separated; and that the reconciliation preserves useful prior work without allowing mechanisms to govern. This wording is retained for provenance and is not the active Gate 2 acceptance question.
- **Mechanism selection:** not authorized by this draft
- **Next interface:** governed by [outcome-architecture.md](outcome-architecture.md)
