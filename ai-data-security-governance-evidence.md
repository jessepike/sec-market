# AI Data Security and Governance — Frozen Evidence Ledger

## Control

- **Evidence Packet ID:** `SEC-MARKET-EV-001`
- **Version:** `0.1`
- **Research freeze:** `2026-08-15T17:11:38-07:00`
- **Scope:** material claims used in `ai-data-security-governance-brief.md`
- **Completion state:** focal-vendor and bounded alternative evidence frozen
- **Alternative evidence:** `SEC-MARKET-ALT-001` v0.1 in `ai-data-security-governance-alternatives.md`
- **Capture method:** public-page retrieval plus locally preserved excerpts below
- **Limitation:** full webpage binaries and cryptographic hashes were not archived; live URLs may change. The excerpts below are the frozen claim evidence for this pilot.

## Source labels

- **REGULATORY-FILING:** issuer filing with a regulator
- **COMPANY-FURNISHED:** company results or announcement furnished through a regulator
- **VENDOR:** vendor-authored product or announcement material
- **COMMERCIAL-PARTNER:** partner-authored integration or solution material
- **INDEPENDENT-REPORTING:** reporting independent of the vendor
- **VENDOR-SELECTED-CASE:** customer evidence selected and published by the vendor
- **CUSTOMER-REVIEW:** customer review platform; self-selection and syndication limitations apply

## Varonis

### Self-hosted end of life

- **Source type:** REGULATORY-FILING
- **Source:** [Varonis 2025 Form 10-K](https://www.sec.gov/Archives/edgar/data/1361113/000162828026005450/vrns-20251231.htm)
- **Publication context:** fiscal year ended 2025; filed 2026
- **Captured excerpt:** “As part of our strategic transition to SaaS, we have announced the end-of-life of our self-hosted products as of December 31, 2026.” The filing separately states the end of on-premises subscriptions on the same date.
- **Disposition:** supported
- **Decision relevance:** Varonis can cover on-premises data sources through its SaaS model, but should not be positioned for environments requiring a self-hosted or disconnected control plane.

### SaaS ARR

- **Source type:** COMPANY-FURNISHED
- **Source:** [Varonis Q2 2026 results](https://www.sec.gov/Archives/edgar/data/1361113/000117184326004948/exh_991.htm)
- **Publication date:** 2026-07-28
- **Captured excerpt:** “Total SaaS ARR was $726.0 million, up 52% year-over-year” and “SaaS ARR, excluding conversions increased 25% year-over-year.”
- **Disposition:** supported as company-reported financial momentum
- **Decision relevance:** indicates scale and investment capacity; does not prove Atlas adoption, control efficacy, or platform integration.

### Established DSPM, permissions, and activity positioning

- **Source type:** VENDOR
- **Source:** [Varonis DSPM](https://www.varonis.com/platform/dspm)
- **Accessed:** 2026-08-15
- **Captured excerpt:** Varonis describes an access graph using “entitlements, group memberships, sharing links” and a searchable audit trail of “data access activity, permissions changes, link sharing, email send/receive, authentication events.”
- **Disposition:** vendor-claimed capability; extensive documentation and customer testimony exist, but independent comparative validation remains limited
- **Decision relevance:** supports a validation hypothesis that Varonis is strongest where effective permissions, activity, remediation, and response are central.

### Atlas AI-security breadth

- **Source type:** VENDOR
- **Source:** [Varonis Atlas](https://www.varonis.com/blog/atlas-ai-security)
- **Last updated:** 2026-05-28
- **Captured excerpt:** Atlas is described as generally available and covering AI inventory, AI-SPM, AI penetration testing, runtime guardrails, compliance, third-party risk, activity monitoring, and AI detection and response.
- **Disposition:** product availability and vendor-described scope supported; operating efficacy and comparative maturity unverified
- **Decision relevance:** Atlas requires a distinct technical and customer proof rather than inheriting confidence from the established Varonis platform.

## Cyera

### DSPM core

- **Source type:** VENDOR
- **Source:** [Cyera DSPM](https://www.cyera.com/platform/dspm)
- **Accessed:** 2026-08-15
- **Captured excerpt:** Cyera describes agentless scanning across hybrid environments, contextual classification, risk correlation using sensitivity, purpose, identities, activity, and exposure, plus 30+ remediation actions.
- **Disposition:** vendor-claimed capability; mixed customer-review and vendor-selected customer evidence supports rapid deployment and visibility, not universal performance
- **Decision relevance:** supports a validation hypothesis that Cyera is well positioned for broad cloud/SaaS discovery and posture.

### Agent Guardian and Endpoint recency

- **Source type:** VENDOR
- **Source:** [Cyera Agent Guardian launch](https://www.cyera.com/press-releases/cyera-launches-agent-guardian-to-secure-the-autonomous-workforce)
- **Publication date:** 2026-08-03
- **Captured excerpt:** Cyera launched Agent Guardian and introduced Cyera Endpoint, claiming inventory, governance, inline tool-call controls, quarantine, red testing, browser/framework/API hooks, and local-agent controls.
- **Disposition:** launch and vendor-described scope supported; production efficacy and integration maturity unverified
- **Decision relevance:** the launch occurred twelve days before the research freeze and must be treated as a separate proof requirement.

### Privacy platform

- **Source type:** VENDOR
- **Source:** [Cyera Privacy](https://www.cyera.com/platform/privacy)
- **Accessed:** 2026-08-15
- **Captured excerpt:** Cyera claims DSR lifecycle automation, identity verification, live RoPA/data maps, PIAs/DPIAs/TIAs, AI risk assessments, consent management, and a privacy-risk register.
- **Disposition:** product positioning supported; workflow depth and independent customer outcomes unverified
- **Decision relevance:** privacy breadth is plausible but should not be inferred from DSPM maturity.

### Financing

- **Source type:** INDEPENDENT-REPORTING
- **Source:** [Reuters report](https://www.reuters.com/legal/transactional/data-security-firm-cyera-raises-600-million-12-billion-valuation-2026-06-10/)
- **Publication date:** 2026-06-10
- **Captured fact:** Reuters reported a $600 million funding round at a $12 billion valuation.
- **Capture limitation:** the page rejected unauthenticated retrieval during verification; the fact was independently located by the research reviewer but no quotation is frozen here.
- **Disposition:** usable only as company-viability context, not capability evidence

## Secuvy

### AI-data platform and DBOM

- **Source type:** VENDOR
- **Sources:** [Secuvy platform overview](https://secuvy.ai/overview/), [Secuvy AI Data Platform](https://secuvy.ai/ai-data-platform/)
- **Accessed:** 2026-08-15
- **Captured excerpt:** Secuvy says it discovers and classifies unstructured data, tags data for AI pipelines, and records “what data classes fed each model or workload, what was held out and why” in a Data Bill of Materials.
- **Captured human-control statement:** Secuvy recommends what a pipeline may use under customer policies and “Your team confirms.”
- **Disposition:** vendor positioning supported; classification performance, DBOM completeness, lineage integrity, policy enforcement, and production outcomes are unverified
- **Decision relevance:** Secuvy may supply classification and provenance evidence to an owner-led AI-use approval process; it cannot itself determine lawful, appropriate, or authorized use.

### Hammerspace integration

- **Source type:** COMMERCIAL-PARTNER
- **Source:** [Hammerspace and Secuvy](https://hammerspace.com/hammerspace-and-secuvy/)
- **Last updated:** 2026-05-28
- **Captured excerpt:** Hammerspace describes Secuvy as the “Data Intelligence and Governance Platform” providing discovery, classification, exposure/access-risk context, and visibility across hybrid and multi-cloud unstructured environments.
- **Disposition:** announced integration supported; commercial-partner evidence does not establish Secuvy efficacy or customer outcomes
- **Decision relevance:** corroborates product direction toward distributed AI data planes, not DBOM performance.

### Privacy and access claims

- **Source type:** VENDOR
- **Current-page finding:** previously cited Secuvy access and privacy URLs changed content and no longer reconstruct the broad claims originally made.
- **Disposition:** no-call on current PrivacyOps breadth and access-intelligence depth until active product documentation or direct proof is obtained
- **Decision relevance:** do not use those capabilities to differentiate Secuvy in active positioning yet.

## Category-boundary evidence

### Microsoft Purview enterprise data governance

- **Source type:** VENDOR
- **Source:** [Microsoft Purview data governance overview](https://learn.microsoft.com/en-us/purview/data-governance-overview)
- **Document date:** 2025-02-19; current page metadata captured 2026-08-15
- **Captured excerpt:** Microsoft describes Data Map and Unified Catalog with governance domains, business concepts, data products, data quality, lineage, ownership, stewardship, and federated governance roles.
- **Disposition:** supported as an adjacent enterprise-governance boundary
- **Decision relevance:** sensitive-data discovery and security posture do not by themselves replace business governance.

### Forcepoint enforcement boundary

- **Source type:** VENDOR
- **Source:** [Forcepoint DLP](https://www.forcepoint.com/product/dlp-data-loss-prevention)
- **Accessed:** 2026-08-15
- **Captured excerpt:** Forcepoint describes enforcement across endpoint, web, email, cloud, network, and AI, including copy/paste, printing, screen capture, removable media, uploads, and outbound email.
- **Disposition:** vendor-described enforcement breadth supported; comparative performance unverified
- **Decision relevance:** use as a channel-coverage benchmark when assessing whether DSPM/DLP orchestration products replace existing enforcement.

## Evidence-quality conclusion

- The strongest frozen evidence concerns corporate status, launch dates, stated product scope, and Varonis's self-hosted transition.
- The bounded alternative packet adds claim-level evidence for BigID, Veeam/Securiti, Microsoft Purview, Forcepoint, Palo Alto Networks, Collibra, and existing-stack/no-buy.
- Public evidence does not support a procurement winner or universal partner priority.
- The brief may support bounded validation hypotheses and qualification questions.
- It must not be treated as proof of connector parity, classification accuracy, remediation safety, runtime efficacy, privacy-workflow depth, interoperability, or total cost.

