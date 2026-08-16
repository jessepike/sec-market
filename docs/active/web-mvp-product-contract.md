# Security Market Pulse — Web MVP Product Contract

## Control

- **Product ID:** `SEC-MARKET-WEB-001`
- **Version:** `0.1`
- **Lifecycle state:** `accepted — implementation authorized`
- **Owner acceptance:** “yes this represents what i want to use”
- **Evidence requirement:** “ensure it maintains attribution and access to research and supporting evidence if people want to validate or dive deeper”
- **Governing Intent:** `SEC-MARKET-001` v1.0
- **Initial evidence basis:** `SEC-MARKET-SIG-002` v0.2

## Outcome

Deliver a responsive website that lets a security leader, account team member, or client understand the current cybersecurity market position in under two minutes and inspect the supporting research when desired.

The website—not the collection machinery—is the MVP product.

## Primary user questions

1. What is happening in the cybersecurity market?
2. What changed?
3. Why does it matter?
4. What should I prepare for, investigate, or avoid claiming?
5. How confident is the call?
6. What evidence supports or contradicts it?

## MVP experience

### Overview

- current market call;
- what changed;
- what it means;
- confidence and no-call boundaries;
- what would change the call.

### Market layers

- AI and data-center infrastructure;
- hyperscaler capital spending;
- cybersecurity vendor outcomes; and
- buyer budgets and adoption.

### Security domains

- Network and SASE
- Cloud Security
- Identity and Machine Identity
- Data and AI Security
- Security Operations
- AI Runtime Security

Each domain displays momentum, evidence strength, posture, supporting evidence, counter-evidence, and what to watch.

### Latest signals

A dated stream of financial results, investment, acquisitions, buyer evidence, regulation, and operating events.

### Research and evidence

Every material call, chart, metric, and domain posture must expose:

- source title and organization;
- publication date and economic period;
- canonical URL;
- exact supporting excerpt or table locator;
- source class;
- interpretation;
- limitation or confound;
- conflicting evidence; and
- relevant research-artifact link.

Attribution must be accessible from the surface where the claim appears, not hidden only in a methodology page.

## Evidence UX rules

- Every material claim carries one or more evidence IDs.
- Clicking an evidence link opens an evidence panel without losing the user’s place.
- Charts expose source and metric-definition details.
- Supporting and conflicting evidence render separately.
- `NO-CALL` and `INSUFFICIENT COVERAGE` remain visible states.
- Vendor marketing, investment, buyer intent, realized spend, deployment, and outcomes are not collapsed.
- No generated or inferred source attribution is permitted.
- A missing or unavailable source displays honestly.

## Initial content

Use the accepted Episode 002 decision:

> Infrastructure investment is accelerating. A stable infrastructure-to-security spending lag remains `NO-CALL`. Use infrastructure activation as an account qualification trigger, not as proof of a broad cybersecurity boom.

Episode 001 may appear as a thematic research item but must not replace the core market call.

## Technical delivery

- React + TypeScript static website
- responsive desktop and mobile layouts
- static, version-controlled data derived from accepted research
- local development and production build
- no database, scheduler, authentication, or autonomous collection required for MVP
- deployment is a later explicit decision

## Acceptance criteria

- website opens locally from one documented command;
- production build succeeds;
- primary call is understandable in under two minutes;
- mobile and desktop layouts are usable;
- all material claims and chart series link to evidence;
- users can inspect exact source excerpts and limitations;
- no governance/process documents dominate the user experience;
- no unsupported market, causal, vendor, or investment claim appears;
- manually updating the static data is possible without rewriting components; and
- independent product and evidence reviews pass.

