# Manual Market Signal Runbook

## Control

- **Runbook ID:** `SEC-MARKET-RUN-001`
- **Version:** `0.2`
- **Lifecycle state:** `validated once — second-domain validation required before shadow automation`
- **Governing Intent:** `SEC-MARKET-001`
- **First completed use:** `SEC-MARKET-SIG-001`

## Purpose

Turn a consequential cybersecurity-market question into a reconstructable timing judgment without first building an autonomous pipeline.

The unit of work is a **decision episode**, not a topic report, vendor landscape, newsletter, or collection sprint.

## Required input contract

Before research begins, record:

1. the market-shift question;
2. the leadership decision it supports;
3. the present-to-24-month horizon;
4. the available posture choices;
5. the working hypothesis;
6. the strongest known alternative;
7. explicit falsifiers;
8. public/confidential evidence boundary; and
9. the event that seals the research freeze.
10. the exposure conditions under which different beneficiaries may warrant different postures.

If the question cannot change a decision, do not run the episode.

## Execution sequence

### 1. Establish the baseline

Describe the prior observable state in dated periods. State which controls, buyer behaviors, standards, and product classes were mature before the suspected shift.

### 2. Collect across independent signal families

Research in parallel:

- enterprise demand and adoption;
- product and control maturity;
- capital allocation and consolidation;
- standards and regulatory pressure;
- ecosystem and infrastructure controls; and
- independent operating evidence.

At least one demand-side and one non-vendor source must bear on the final call. Supply announcements alone cannot authorize a timing change.

### 3. Normalize each material claim

Capture:

- event/publication date;
- canonical source and URL;
- source class;
- exact short evidence excerpt;
- availability or legal status;
- evidenced fact;
- interpretation;
- signal direction and strength;
- limitation or conflict; and
- decision relevance.

Preserve original origin when an announcement or statistic is repeated.

### 4. Separate epistemic states

Label conclusions as:

- **Evidenced**
- **Assumed**
- **Hypothesized**
- **Unknown**

Do not translate announcement volume, funding, registration, downloads, or forecasts into adoption without independent evidence.

### 5. Seal the research freeze

Record a timestamp when the packet contains enough evidence to support or reject a posture. Later evidence starts a new version or episode; it does not silently rewrite the frozen basis.

### 6. Make the timing call

Choose one posture:

- **Prioritize**
- **Prepare**
- **Investigate**
- **Defer**
- **No-call**

Report confidence separately from action readiness. A low-maturity market can still justify highly reversible preparation.

### 7. Challenge the call

Produce the strongest alternative interpretation. Test:

- demand versus supply;
- GA versus preview or roadmap;
- product availability versus operating efficacy;
- specialist products versus existing/native controls;
- current adoption versus forecasts;
- category durability versus platform absorption; and
- the cost of acting versus the cost of waiting.

### 8. Define falsifiers and triggers

State the events that would:

- weaken or reverse the posture;
- strengthen or accelerate it;
- justify procurement or standardization; and
- warrant a new research freeze.

### 9. Verify

An independent reviewer must be able to:

- reconstruct every load-bearing claim;
- distinguish evidence from interpretation;
- identify broken, repeated, stale, or weak sources;
- verify that counter-evidence is represented fairly; and
- identify the exact evidence or assumption behind disagreement.

### 10. Decide what to automate

After the episode, separate:

- stable, repetitive collection and normalization work;
- domain-specific but reusable analysis; and
- judgment and authorization that should remain human-steered.

Do not automate a pattern until it survives a materially different second episode. A second episode may authorize shadow mode only; human review remains required until explicit promotion criteria are met.

## Exit conditions

An episode is complete when:

- the evidence packet is frozen;
- the posture is explicit;
- confidence and action readiness are separate;
- the strongest alternative and falsifiers are visible;
- immediate actions are reversible and proportional;
- no-call areas prevent overreach;
- independent review has no unresolved high-severity defect; and
- automation candidates are documented without authorizing premature infrastructure.

## Current validation state

`SEC-MARKET-SIG-001` exercised this sequence, exposed material improvements to applicability, source-status verification, and automation gating, and passed independent review after revision. One run is still insufficient to prove cross-domain repeatability or authorize a collection pipeline.

