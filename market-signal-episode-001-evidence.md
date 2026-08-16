# Market Signal Episode 001 — Frozen Evidence Ledger

## Control

- **Evidence Packet ID:** `SEC-MARKET-SIG-EV-001`
- **Version:** `0.2`
- **Lifecycle state:** `sealed — independently reviewed`
- **Episode:** `SEC-MARKET-SIG-001`
- **Research freeze:** `2026-08-15T18:18:04-07:00`
- **Scope:** public evidence bearing on the emergence of agents as an additional runtime control surface alongside AI data discovery and posture
- **Capture method:** public-page retrieval, original-source review, independent reporting, and frozen claim excerpts below
- **Limitation:** linked pages were not archived as full binaries or cryptographically hashed; links may change

## Source classes

- **OFFICIAL:** regulator, standards body, government, protocol foundation, or official specification
- **FILING:** public-company regulatory filing or investor disclosure
- **INDEPENDENT:** independent research, analyst, survey, or reporting
- **VENDOR:** vendor-authored announcement or product documentation
- **VENDOR-RESEARCH:** vendor-authored technical evaluation with disclosed methods; useful operating evidence but not independent validation
- **VENDOR-SURVEY:** vendor-sponsored or vendor-operated telemetry/survey
- **CUSTOMER-CASE:** named deployment described by the customer or a supplying vendor

Availability, investment, adoption, efficacy, and market timing are separate judgments. A product release is not adoption; an acquisition is not demand; a survey response is not production use.

## Baseline

| Period | Observable baseline | Interpretation |
|---|---|---|
| 2024 | AI-BOM, discovery, DSPM, posture, and misconfiguration were the mature center; initial multi-cloud runtime products and prompt filters reached availability. | Runtime was an adjacent extension to a posture-led market. |
| 2025 | Tool-use APIs and MCP broadened the action surface; established security platforms acquired runtime specialists; gateway and model-provider controls became commercially available. | Control began shifting from AI assets and data exposure toward prompts, tool calls, and actions. |
| 2026 through freeze | Agent identity, tool authorization, runtime policy, MCP brokerage, write controls, and control planes entered cloud, SASE, firewall, gateway, browser, endpoint, and IAM products. Several high-consequence controls remain preview, beta, or newly GA. | Runtime control is becoming an additional security plane; buyer adoption, operating maturity, and category structure remain unsettled. |

## Enterprise demand and adoption

### D1 — Scaled agent use is real but narrow

- **Date:** 2025-11
- **Source class:** INDEPENDENT
- **Source:** [McKinsey, The State of AI in 2025](https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai)
- **Frozen evidence:** “Twenty-three percent of respondents report their organizations are scaling an agentic AI system somewhere in their enterprises” and another 39 percent were experimenting. In any individual business function, no more than 10 percent reported scaling.
- **Disposition:** supports a growing action surface; rejects claims of broad enterprise autonomy
- **Signal strength:** medium-high
- **Limit:** self-reported global survey; “scaling somewhere” may mean only one function

### D2 — Current deployment remains behind intent

- **Date:** 2026-04-02
- **Source class:** INDEPENDENT
- **Source:** [Gartner, 2026 Hype Cycle for Agentic AI](https://www.gartner.com/en/articles/hype-cycle-for-agentic-ai)
- **Frozen evidence:** “only 17% of organizations have deployed AI agents to date, yet more than 60% expect to do so within the next two years.”
- **Disposition:** strong forward-intent signal and strong current-maturity counter-signal
- **Signal strength:** medium
- **Limit:** “deployed” does not distinguish bounded, supervised, or autonomous use

### D3 — AI protection became an explicit security-budget priority

- **Date:** 2026-04-29
- **Source class:** INDEPENDENT
- **Source:** [ETR, Why GenAI Protection Just Overtook Cloud Security Budgets](https://research.etr.ai/etr-data-drop/why-genai-protection-just-overtook-cloud-security-budgets)
- **Frozen evidence:** 59 percent planned increased LLM/GenAI protection spending versus 54 percent for cloud security. For agentic workloads, respondents prioritized compliance and audit reporting (48 percent), non-human identity (44 percent), unified enforcement (40 percent), and built-in agent controls (39 percent).
- **Disposition:** direct demand signal for governance, identity, and enforcement; not proof of specialist-product demand
- **Signal strength:** high
- **Limit:** 517 respondents; agent-specific questions used 260 respondents; spending intent is not realized spend

### D4 — Enterprise registration of agents is accelerating

- **Date:** 2026-07-29
- **Source class:** FILING
- **Source:** [Microsoft FY2026 Q4 earnings call](https://www.microsoft.com/en-us/investor/events/fy-2026/earnings-fy-2026-q4)
- **Frozen evidence:** “Just two months in, Agent 365 now has nearly 40 million agents registered across tens of thousands of companies.”
- **Disposition:** strong control-plane distribution signal
- **Signal strength:** medium-high
- **Limit:** registered agents are not necessarily active, autonomous, or in production; Microsoft separately reported Copilot seats

### D5 — Security leaders have material inventory and authorization gaps

- **Date:** 2026-07-29
- **Source class:** VENDOR-SURVEY
- **Source:** [Okta, Global CISO Insights 2026](https://www.okta.com/newsroom/articles/global-ciso-insights-2026/)
- **Frozen evidence:** 47 percent could identify all agents, 46 percent centrally controlled access, 45 percent authorized individual tool calls, and 21 percent used shared or broad-permission credentials.
- **Disposition:** supports a preparation need
- **Signal strength:** medium
- **Limit:** vendor-sponsored survey of 306 security executives; respondent definitions of “agent” may differ

## Independent operating evidence

### I1 — A bounded autonomous-action failure has occurred publicly

- **Date:** 2026-04-27
- **Source class:** INDEPENDENT
- **Source:** [The Register, coding agent deleted a production database volume](https://www.theregister.com/software/2026/04/27/cursor-opus-agent-snuffs-out-startups-production-database/5224442)
- **Frozen evidence:** an agent using a permissioned Railway token deleted a production volume; Railway confirmed the legacy endpoint lacked delayed deletion and restored the data.
- **Disposition:** demonstrates consequential tool-action risk and the relevance of permissions, approval, and recovery
- **Signal strength:** medium
- **Limit:** one small-company incident; no verified aggregate loss rate

## Supply, product maturity, and consolidation

### S1 — Multi-cloud AI runtime security was commercially available in 2024

- **Date:** 2024-10-11
- **Source class:** VENDOR
- **Source:** [Palo Alto Networks, AI Runtime Security now available](https://www.paloaltonetworks.com/blog/network-security/ai-runtime-security-now-available/)
- **Frozen evidence:** “AI Runtime Security is now available” for Google Cloud, Microsoft Azure, and Amazon Web Services.
- **Disposition:** establishes an early runtime baseline
- **Signal strength:** high for availability; low for efficacy or adoption

### S2 — MCP standardized a large tool-action surface

- **Date:** 2024-11-25; current specification 2026-07-28
- **Source class:** OFFICIAL
- **Sources:** [Anthropic MCP announcement](https://www.anthropic.com/news/model-context-protocol), [current MCP specification](https://modelcontextprotocol.io/specification/2026-07-28)
- **Frozen evidence:** MCP was introduced as “an open standard” connecting AI systems to data and tools. The current specification supports scoped authorization but states that “MCP itself cannot enforce these security principles at the protocol level.”
- **Disposition:** strong infrastructure and governance-demand signal
- **Signal strength:** high
- **Limit:** protocol distribution is not equivalent to enterprise production use

### S3 — Tool use became a mainstream model-provider primitive

- **Date:** 2025-03-11 and 2025-05-21
- **Source class:** VENDOR
- **Sources:** [OpenAI, new tools for building agents](https://openai.com/index/new-tools-for-building-agents/), [OpenAI, Responses API updates](https://openai.com/index/new-tools-and-features-in-the-responses-api/)
- **Frozen evidence:** OpenAI introduced computer use and an Agents SDK for multi-agent workflows, then remote MCP-server access.
- **Disposition:** expands the action surface faster than independent governance evidence
- **Signal strength:** high for availability

### S4 — Runtime specialists were absorbed by established platforms

- **Date:** 2025-07 through 2025-10
- **Source class:** FILING
- **Sources:** [Palo Alto Networks / Protect AI](https://www.sec.gov/Archives/edgar/data/1327567/000132756725000027/R37.htm), [SentinelOne / Prompt Security](https://www.sec.gov/Archives/edgar/data/1583708/000158370826000041/s-20260430.htm), [F5 / CalypsoAI](https://www.sec.gov/Archives/edgar/data/1048695/000104869526000051/ffiv-20260331.htm), [CrowdStrike / Pangea](https://www.sec.gov/Archives/edgar/data/1535527/000153552725000033/R18.htm), [Check Point / Lakera](https://www.sec.gov/Archives/edgar/data/1015922/000117891326001932/R11.htm)
- **Frozen evidence:** five transactions recorded at least approximately $1.35 billion of consideration or cash. Several filings described acquired revenue or operating impact as immaterial; allocations were goodwill-heavy.
- **Disposition:** strong strategic-investment and platform-convergence signal; weak standalone-demand proof
- **Signal strength:** high for consolidation, low for adoption

### S5 — Externalized agent-tool policy reached GA in a major cloud

- **Date:** 2026-03-03
- **Source class:** VENDOR
- **Source:** [AWS, AgentCore Policy generally available](https://aws.amazon.com/about-aws/whats-new/2026/03/policy-amazon-bedrock-agentcore-generally-available/)
- **Frozen evidence:** AgentCore Gateway “intercepts agent-tool traffic and evaluates each request against the policies before allowing or denying tool access.”
- **Disposition:** strong evidence that deterministic runtime authorization is becoming native infrastructure
- **Signal strength:** high for availability
- **Limit:** AWS-centered and dependent on routing through AgentCore Gateway

### S6 — Agent and MCP controls reached SASE distribution

- **Date:** 2026-03-11
- **Source class:** VENDOR
- **Source:** [Netskope, agentic broker and guardrails](https://www.netskope.com/press-releases/netskope-unveils-netskope-one-ai-security-delivering-high-performance-protection-across-the-entire-ai-ecosystem)
- **Frozen evidence:** Agentic Broker governs MCP transactions and Guardrails moderates user and automated-agent interactions; both were announced as generally available.
- **Disposition:** runtime governance is entering installed traffic-control infrastructure
- **Signal strength:** high for availability; low for independent efficacy

### S7 — Administrative control matured before runtime enforcement, which is now mixed GA and preview

- **Date:** 2026-05-01
- **Source class:** VENDOR
- **Sources:** [Microsoft, Agent 365 generally available](https://www.microsoft.com/en-us/security/blog/2026/05/01/microsoft-agent-365-now-generally-available-expands-capabilities-and-integrations/), [Microsoft, runtime protection update](https://techcommunity.microsoft.com/blog/microsoft-security-blog/securing-ai-agents-at-runtime-real-time-protection-and-threat-detection-for-micr/4541255)
- **Frozen evidence:** Agent 365 became GA on 2026-05-01. On 2026-07-27, real-time protection for Work IQ and registered custom MCP tool invocations became GA, while threat detection remained public preview.
- **Disposition:** supports the transition while preserving the maturity distinction
- **Signal strength:** high
- **Limit:** coverage depends on supported and registered tool paths; unsupported tools and alternate runtimes are not covered

### S8 — AI inspection entered the firewall

- **Date:** 2026-07-30
- **Source class:** VENDOR
- **Source:** [Check Point, AI Network Firewall](https://www.checkpoint.com/press-releases/check-point-revolutionizes-the-firewall-market-new-ai-network-firewall-closes-the-networks-ai-blind-spot-everywhere/)
- **Frozen evidence:** the announced firewall covers prompts, agents, local and SaaS discovery, runtime protection, and guardrails through existing firewall infrastructure.
- **Disposition:** supports feature convergence into existing security platforms
- **Signal strength:** high for availability; unknown for adoption and efficacy

### S9 — High-consequence write controls remain partly pre-GA

- **Date:** 2026-08-05 and 2026-08-12
- **Source class:** VENDOR
- **Sources:** [Cloudflare WriteGuard private beta](https://blog.cloudflare.com/mcp-portal-writeguard-private-beta/), [Cloudflare MCP detection beta](https://developers.cloudflare.com/changelog/post/2026-08-12-mcp-detection-and-dashboard/)
- **Frozen evidence:** WriteGuard private beta can block tools before execution; Gateway MCP detection remained beta.
- **Disposition:** strong direction-of-travel evidence and strong maturity counter-signal
- **Signal strength:** high

### S10 — Current focal-partner launches cluster at the edge of the freeze

- **Date:** 2026-02 through 2026-08
- **Source class:** VENDOR
- **Sources:** [Varonis Atlas](https://www.varonis.com/blog/atlas-ai-security), [Cyera Agent Guardian](https://www.cyera.com/press-releases/cyera-launches-agent-guardian-to-secure-the-autonomous-workforce), [Palo Alto Cortex Data Security](https://www.paloaltonetworks.com/blog/security-operations/cortex-data-security-ai-data-protection/)
- **Frozen evidence:** Varonis Atlas became GA shortly after the AllTrue acquisition; Cyera Agent Guardian launched 2026-08-03; Cortex Data Security entered public preview 2026-08-11.
- **Disposition:** relevant local market signal but too recent and vendor-authored to support a procurement call
- **Signal strength:** high for announcement tempo, low for operating maturity

## Standards, regulation, and government guidance

### G1 — NIST recognizes an agent-specific security gap

- **Date:** 2026-05-18
- **Source class:** OFFICIAL
- **Source:** [NIST AI 800-5](https://www.nist.gov/publications/summary-analysis-responses-request-information-regarding-security-considerations-ai)
- **Frozen evidence:** commenters widely agreed that agents present “novel security threats,” that security concerns impede adoption, and that fundamental cybersecurity practices “will require adaptation.”
- **Disposition:** supports preparation and adaptation of existing controls
- **Signal strength:** high for government direction; medium for implementation specificity
- **Limit:** synthesis of RFI responses, not binding or final control guidance

### G2 — CISA and international partners advise bounded, least-privilege adoption

- **Date:** 2026-05-01
- **Source class:** OFFICIAL
- **Source:** [CISA, Careful Adoption of Agentic AI Services](https://www.cisa.gov/news-events/news/cisa-us-and-international-partners-release-guide-secure-adoption-agentic-ai)
- **Frozen evidence:** avoid broad or unrestricted access, begin with low-risk and non-sensitive use cases, and account for agentic AI in the organization’s security model and risk posture.
- **Disposition:** direct prepare-now signal that favors existing security models rather than a new universal platform
- **Signal strength:** high

### G3 — EU obligations create an implementation runway, not an immediate universal mandate

- **Date:** consolidated through 2026-07-27
- **Source class:** OFFICIAL
- **Sources:** [EU AI Act consolidated text](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX%3A02024R1689-20260727), [Regulation (EU) 2026/1744](https://eur-lex.europa.eu/eli/reg/2026/1744/oj/eng)
- **Frozen evidence:** the Act generally applies from 2026-08-02; Annex III high-risk provisions apply from 2027-12-02 and Annex I product provisions from 2028-08-02. High-risk systems must support automatic event logging, human oversight, monitoring, and retained records.
- **Disposition:** strong preparation signal for qualifying use cases; weak immediate procurement forcing function
- **Signal strength:** high
- **Limit:** high-risk provisions do not apply to every copilot or agent

### G4 — Agent-specific threat guidance is now usable

- **Date:** 2025-12-09
- **Source class:** OFFICIAL
- **Source:** [OWASP Top 10 for Agentic Applications 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)
- **Frozen evidence:** the threat set includes goal hijacking, tool misuse, identity and privilege abuse, supply-chain compromise, unexpected code execution, memory poisoning, insecure inter-agent communication, cascading failure, human-trust exploitation, and rogue agents.
- **Disposition:** practical threat-model baseline
- **Signal strength:** medium-high
- **Limit:** community guidance is not proof that a product prevents these failures

### G5 — Agent communication is stable while authorization remains local

- **Date:** 2026-04
- **Source class:** OFFICIAL
- **Source:** [A2A v1.0 specification](https://a2a-protocol.org/v1.0.0/specification/)
- **Frozen evidence:** v1.0 adds signed Agent Cards, mTLS, and modern OAuth flows, but authorization logic remains specific to the agent implementation, data, and enterprise policy.
- **Disposition:** supports identity and authorization preparation; does not create a universal policy plane
- **Signal strength:** high

## Counter-evidence and unresolved quality

### C1 — Cancellation risk is material

- **Date:** 2025-06-25
- **Source class:** INDEPENDENT
- **Source:** [Gartner cancellation forecast](https://www.gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-over-40-percent-of-agentic-ai-projects-will-be-canceled-by-end-of-2027)
- **Frozen evidence:** Gartner forecast that more than 40 percent of agentic projects will be canceled by the end of 2027 because of cost, unclear value, or inadequate risk controls.
- **Disposition:** strong caution against scaling control spend ahead of stable use cases
- **Signal strength:** medium
- **Limit:** forecast, not measured cancellation

### C2 — Independent runtime-control operating evidence remains sparse

- **Date:** through freeze
- **Source class:** cross-source absence check
- **Frozen evidence:** reviewed focal-vendor, incumbent-platform, acquisition, and customer materials did not provide reproducible comparative results for adaptive bypass, false-block rate, latency, coverage, failover, incident reduction, or total operating cost.
- **Disposition:** blocks a priority or standardization call
- **Signal strength:** high as an evidence-quality finding
- **Limit:** absence of public evidence is not evidence that no private results exist

### C3 — Conventional controls remain the default challenger

- **Date:** through freeze
- **Source class:** OFFICIAL
- **Sources:** [NIST COSAiS](https://csrc.nist.gov/projects/cosais), [OWASP AI Agent Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html)
- **Frozen evidence:** both approaches adapt established identity, least privilege, authorization, sandboxing, egress, logging, approval, interruption, and rollback patterns.
- **Disposition:** requires an existing-stack-first test before specialist procurement
- **Signal strength:** high

### C4a — Independent government testing found residual hijacking risk

- **Date:** 2026-03-23
- **Source class:** OFFICIAL
- **Source:** [NIST agent red-team competition](https://www.nist.gov/blogs/caisi-research-blog/insights-ai-agent-security-large-scale-red-teaming-competition)
- **Frozen evidence:** across more than 250,000 attack attempts by more than 400 participants, at least one successful attack was found against every one of the 13 tested frontier models.
- **Disposition:** supports layered containment and rejects perfect model-layer prevention claims
- **Signal strength:** high

### C4b — Vendor testing also favors containment beyond the model

- **Date:** 2026-05-25
- **Source class:** VENDOR-RESEARCH
- **Source:** [Anthropic containment research](https://www.anthropic.com/engineering/how-we-contain-claude)
- **Frozen evidence:** Anthropic reported that repeated adaptive attempts raised attack success and recommended filesystem and egress boundaries rather than model defenses alone.
- **Disposition:** supports deterministic containment and layered controls
- **Signal strength:** medium-high
- **Limit:** vendor-authored evaluation of its own systems; not independent comparative validation

## Evidence quality summary

| Question | Evidence state |
|---|---|
| Are agents becoming an additional runtime control surface? | **Evidenced — high confidence on supply and control architecture; medium confidence on buyer-side operating adoption.** Product, acquisition, protocol, standards, budget-intent, and early adoption signals converge without showing broad displacement of posture-led controls. |
| Are enterprises broadly operating autonomous agents? | **Not evidenced.** Deployment is growing but remains bounded and definition-sensitive. |
| Are runtime controls commercially available? | **Evidenced — mixed maturity.** Multiple controls are GA; consequential components also remain preview, beta, newly integrated, or cloud-specific. |
| Do specialist products outperform existing or native controls? | **Unknown.** Independent comparative operating evidence is insufficient. |
| Is a separate product category durable? | **Hypothesized.** Platform absorption may turn it into features across IAM, SASE, CNAPP, gateways, endpoint, browser, and cloud services. |
| Is preparation warranted before procurement? | **Conditional — medium-high confidence for organizations with current or planned tool, write, or sensitive-data exposure; investigate otherwise.** |

