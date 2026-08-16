# Market Timing Brief — AI Runtime and Agentic Data Controls

## Control

- **Brief ID:** `SEC-MARKET-SIG-DB-001`
- **Version:** `0.2`
- **Episode:** `SEC-MARKET-SIG-001`
- **Lifecycle state:** `accepted — conditional PREPARE`
- **Independent review:** `passed 2026-08-15`
- **Research freeze:** `2026-08-15T18:18:04-07:00`
- **Evidence ledger:** `SEC-MARKET-SIG-EV-001`
- **Decision horizon:** present through 24 months
- **Permitted use:** conditional leadership posture and bounded readiness planning
- **Not suitable for:** universal applicability, platform selection, broad procurement, market-size claims, or partner authorization

## Market question

> Are agents becoming a consequential cybersecurity action surface quickly and credibly enough that organizations with material exposure should move from **investigate** to **prepare now**?

## Applicability

A **materially exposed organization** currently has, or expects within the present-to-24-month horizon to have, an agent that can:

- invoke tools or write to systems through delegated human or non-human credentials;
- access sensitive, regulated, privileged, or mission-critical data;
- or create difficult-to-reverse consequences through its tool or data access.

| Exposure state | Warranted posture |
|---|---|
| No material agent exposure and none planned within the present-to-24-month horizon | **INVESTIGATE** — monitor named triggers; no distinct readiness motion |
| Material exposure is planned but not yet approved | **PREPARE** — use the approval process to establish minimum controls |
| Material exposure exists in pilot or production | **PREPARE** — run one bounded existing-control assessment |
| Consequential production actions exist with an unresolved material control gap or repeatable incident | **PRIORITIZE** the specific remediation, not a market-wide platform |

## Timing judgment

> **Conditional PREPARE:** organizations with material exposure should perform bounded readiness work now. Organizations without that exposure should remain in INVESTIGATE. The evidence does not support broad platform standardization.

The market evidence shows that agent identities and control planes are scaling, tool and write controls are entering established infrastructure, and security leaders are expressing budget intent for audit, non-human identity, and unified enforcement. It does **not** show that autonomous action is broadly scaled or that runtime controls are replacing discovery and posture.

The practical shift is additive: discovery and posture increasingly feed decisions about agent identity, tool access, runtime policy, evidence, interruption, and recovery.

## Confidence and action readiness

### Rubrics

- **High confidence:** multiple independent signal families converge and no unresolved contradiction changes the direction.
- **Medium confidence:** evidence converges but is definition-sensitive, vendor-heavy, forecast-led, or operating outcomes remain sparse.
- **Low confidence:** the conclusion depends mainly on announcements, inference, or one source family.

- **High action readiness:** the action is reversible, bounded to an existing decision event, uses current controls first, and has an explicit stop condition.
- **Medium action readiness:** the action needs dedicated engineering or a product test but remains bounded.
- **Low action readiness:** the action creates a standing program, platform dependency, or broad procurement before a measured gap exists.

| Judgment dimension | Assessment | Basis |
|---|---|---|
| Agents are becoming an additional runtime control surface | **High confidence** | Product, protocol, acquisition, standards, budget-intent, and early adoption signals converge |
| Buyer adoption of runtime controls alongside posture | **Medium confidence** | Budget intent and early control-plane uptake exist; deployment, renewal, and operating-program evidence is limited |
| Speed and broad market consequence | **Medium confidence** | Current use is bounded and definition-sensitive; intent and supply are accelerating |
| Bounded preparation for exposed organizations | **High action readiness** | Can attach to an existing deployment approval and stop if no gap is found |
| Broad product standardization | **Low action readiness** | Category structure and comparative efficacy remain unresolved |
| Standalone specialist-category durability | **Low-medium confidence** | Platform absorption may convert the category into features |

## Evidence crossing the conditional threshold

### Budget intent and early control-plane uptake

- ETR found LLM/GenAI protection leading 2026 security budget-increase intent at 59 percent.
- Surveyed buyers prioritized audit reporting, non-human identity, unified enforcement, and built-in agent controls for agentic workloads.
- Microsoft reported nearly 40 million agents registered in Agent 365.
- CISO surveys show material gaps in inventory, access control, and tool-call authorization.

Planned spend is not realized spend. Registration is not production use. These signals cross the **monitor-to-prepare threshold only when an organization also has material exposure**.

### Runtime controls are entering established enforcement points

The frozen evidence shows agent-tool policy in AWS gateways, real-time tool-invocation blocking in Microsoft Agent 365, agent and MCP controls in SASE, AI inspection in firewalls, and write controls in beta gateway services. Several controls are GA; others remain preview, beta, newly integrated, or path-dependent.

This supports testing existing and native enforcement before assuming a specialist platform is required.

### Government and standards bodies describe an adaptation need

- NIST found broad agreement that agents create novel threats and that established cybersecurity practices require adaptation.
- CISA and international partners advise bounded deployment, least privilege, monitoring, and inclusion in the existing security model.
- MCP and A2A stabilize tool and agent interaction while leaving enterprise authorization and enforcement to implementations.
- The EU AI Act creates logging, oversight, monitoring, and evidence requirements for qualifying high-risk systems, with an implementation runway into 2027–2028.

These sources support preparation for qualifying exposure; they do not create a universal runtime-product mandate.

## Strongest alternative interpretation

> Agent risk is growing, but it remains a per-use-case extension of application, cloud, identity, data, and operational security. Most organizations should use ordinary architecture review and keep the portfolio-level market posture at INVESTIGATE rather than create a distinct agent-security readiness motion.

This null interpretation is materially supported:

- only 17 percent of organizations had deployed agents in Gartner’s 2026 survey, while McKinsey found no individual function above 10 percent scaled use;
- public-company filings described several acquired specialists as financially immaterial;
- product announcements cluster around recent acquisitions;
- high-consequence controls remain uneven in maturity and coverage;
- public comparative evidence on adaptive bypass, false blocks, latency, failover, and incident reduction is insufficient; and
- existing identity, DLP, gateways, sandboxing, egress, approval, logging, and rollback remain credible default controls.

The null **wins** for organizations without material exposure: remain in INVESTIGATE. It loses only when a real approval or operating decision would otherwise permit consequential agent access without testing whether established controls cover the action path.

## Bounded action for exposed organizations

No new standing program is authorized.

| Step | Owner | Scope and entry trigger | Success and stop condition |
|---|---|---|---|
| 1. Identify material exposure | Existing AI-governance or security-architecture owner | At the next approval for a tool-using, write-capable, privileged, or sensitive-data agent; review no more than the 3–5 highest-consequence workflows | Stop and remain **INVESTIGATE** if no material workflow exists |
| 2. Check the existing control path | Workflow technical owner with security review | For each selected workflow, record identity/delegation, allowed tools and data, approval, logs, halt, and recovery using existing IdP, cloud, gateway, DLP, application, and operational controls | Stop if current controls cover the path and a halt/recovery test succeeds |
| 3. Test one measured residual gap | Security engineering owner | Only if Step 2 finds a material gap; compare the current/native control with at most one additional challenger on one workflow | Close or escalate based on bypass, false blocks, latency, coverage, evidence completeness, and failure behavior; no platform standard follows from one test |

A new provider-neutral schema, broad inventory, argument-level policy program, or adversarial test suite is not authorized unless the bounded assessment proves existing evidence and controls insufficient.

## Falsifiers and posture-change triggers

### Market-transition hypothesis

- **Weakens:** demand-side deployment, ownership, and realized spend remain flat while supply announcements continue.
- **Strengthens:** independent customer counts, renewals, operating programs, and production outcomes move with GA control adoption.

### Organizational PREPARE applicability

- **Weakens to INVESTIGATE:** no material exposure exists, or ordinary architecture review fully covers identity, action, evidence, halt, and recovery.
- **Strengthens to bounded PRIORITIZE:** a consequential workflow has a reproducible residual gap, incident, or binding unmet requirement.

### Specialist-category durability

- **Weakens:** native and established controls provide comparable cross-path coverage and specialist capabilities remain financially immaterial or absorbed.
- **Strengthens:** independent testing shows repeatable cross-provider protection and acceptable latency, false-block, bypass, and operating cost advantages.

## Monitoring

The security-market project owner owns the posture, not a vendor or platform team.

| Source set | Review trigger | Threshold and effect |
|---|---|---|
| Official product status pages for the controls in `SEC-MARKET-SIG-EV-001` | GA, preview, beta, coverage, deprecation, or enforcement-path change | Two independently operated GA control paths with comparable semantics strengthen market maturity; a material loss of coverage weakens it |
| SEC filings, earnings disclosures, and independent adoption research | New realized-spend, customer, renewal, production, or cancellation evidence | Two independent demand sources showing production operating programs strengthen the market-transition hypothesis; supply-only growth does not |
| NIST, CISA, EU, OWASP, MCP, A2A, and relevant identity/authorization standards | Final guidance, binding date, or specification-status change | A new unmet control requirement can escalate an exposed workflow; guidance already met by the current stack does not |
| Independent adaptive tests and incident reports | New efficacy comparison, material bypass, repeatable loss, or operating failure | Reproducible residual gaps can escalate the affected workflow; isolated or vendor-only claims remain evidence inputs |

A new evidence version is required before the next materially exposed workflow is approved or before the project issues another timing judgment, whichever event comes first. This is the maximum review interval; it is decision-bound rather than calendar-bound.

## Boundary with the prior vendor pilot

This market-signal episode does not modify or authorize the prior Varonis, Cyera, or Secuvy posture. Vendor launches are supply evidence here, not decision candidates. Any later partner comparison must begin with a named material workflow and a measured residual gap after current and native controls are tested.

## No-call areas

The frozen evidence does not support:

- universal PREPARE for every security leader;
- one universal AI-security winner;
- broad replacement of existing data, identity, cloud, network, application, endpoint, or browser controls;
- a claim that autonomous agents are already broadly scaled;
- a durable standalone market-category boundary;
- comparative product efficacy or default-vendor authorization;
- a reliable aggregate loss rate from agent failures; or
- a universal regulatory deadline for all enterprise agents.

## Automation decision after the manual run

### Candidate mechanics

- official-source status and specification change detection;
- acquisition, filing, funding, and dated-survey event capture;
- canonical-source and repeated-origin detection;
- source-class labeling and evidence-versus-interpretation separation; and
- research-freeze manifests and trigger reminders.

### Enforceable gate

This episode does not authorize an autonomous collection pipeline. A materially different second episode may authorize **shadow mode only** if:

- every load-bearing item retains a canonical URL, date, source class, and frozen excerpt;
- review finds no high-severity status, date, attribution, or provenance error;
- repeated reports resolve to one original event;
- unclassifiable or failed retrievals remain visibly blocked rather than silently omitted; and
- a human verifies every proposed ledger change and every posture judgment.

Any high-severity provenance or product-status miss immediately demotes the automation candidate. Judgment and posture authorization remain human-steered.

## Decision

**Conditional PREPARE.**

Organizations with current or planned material agent exposure should attach one bounded existing-control assessment to the relevant approval event. Organizations without that exposure should remain in INVESTIGATE and monitor the named triggers. No standing program, specialist-platform motion, or broad procurement is authorized.

