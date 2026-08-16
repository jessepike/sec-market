# Market Signal Episode 001 — Source and Integrity Manifest

## Control

- **Manifest ID:** `SEC-MARKET-SIG-SRC-001`
- **Version:** `0.2`
- **Research freeze:** `2026-08-15T18:18:04-07:00`
- **Retrieval date:** 2026-08-15, on or before the research freeze
- **Canonical claim record:** `SEC-MARKET-SIG-EV-001` v0.2

## Capture contract

Each ledger entry preserves:

- canonical source title and URL;
- publication or event date;
- source class;
- exact short contextual evidence excerpt;
- disposition, strength, and limitation; and
- a stable ledger item ID.

The ledger anchors below are the immutable excerpt manifest for this pilot. Full source-page binaries were not archived because licensing and redistribution rights were not evaluated. The packet therefore proves the integrity of the frozen claim excerpts, not the continued availability or byte identity of external pages.

## Source index

| Ledger ID | Canonical document or event | Publication/event date | Frozen context anchor |
|---|---|---:|---|
| D1 | McKinsey, *The State of AI in 2025* | 2025-11 | `D1 — Scaled agent use is real but narrow` |
| D2 | Gartner, *2026 Hype Cycle for Agentic AI* | 2026-04-02 | `D2 — Current deployment remains behind intent` |
| D3 | ETR, *Why GenAI Protection Just Overtook Cloud Security Budgets* | 2026-04-29 | `D3 — AI protection became an explicit security-budget priority` |
| D4 | Microsoft FY2026 Q4 earnings call | 2026-07-29 | `D4 — Enterprise registration of agents is accelerating` |
| D5 | Okta, *Global CISO Insights 2026* | 2026-07-29 | `D5 — Security leaders have material inventory and authorization gaps` |
| I1 | The Register, production database-volume deletion report | 2026-04-27 | `I1 — A bounded autonomous-action failure has occurred publicly` |
| S1 | Palo Alto Networks, *AI Runtime Security now available* | 2024-10-11 | `S1 — Multi-cloud AI runtime security was commercially available in 2024` |
| S2 | Anthropic MCP announcement and MCP 2026-07-28 specification | 2024-11-25 / 2026-07-28 | `S2 — MCP standardized a large tool-action surface` |
| S3 | OpenAI agent tools and Responses API updates | 2025-03-11 / 2025-05-21 | `S3 — Tool use became a mainstream model-provider primitive` |
| S4 | Protect AI, Prompt Security, CalypsoAI, Pangea, and Lakera transaction filings | 2025-07 through 2025-10 | `S4 — Runtime specialists were absorbed by established platforms` |
| S5 | AWS, AgentCore Policy GA | 2026-03-03 | `S5 — Externalized agent-tool policy reached GA in a major cloud` |
| S6 | Netskope agentic broker and guardrails announcement | 2026-03-11 | `S6 — Agent and MCP controls reached SASE distribution` |
| S7 | Microsoft Agent 365 GA and runtime-protection update | 2026-05-01 / 2026-07-27 | `S7 — Administrative control matured before runtime enforcement, which is now mixed GA and preview` |
| S8 | Check Point AI Network Firewall announcement | 2026-07-30 | `S8 — AI inspection entered the firewall` |
| S9 | Cloudflare WriteGuard and MCP detection updates | 2026-08-05 / 2026-08-12 | `S9 — High-consequence write controls remain partly pre-GA` |
| S10 | Varonis Atlas, Cyera Agent Guardian, and Cortex Data Security announcements | 2026-02 through 2026-08 | `S10 — Current focal-partner launches cluster at the edge of the freeze` |
| G1 | NIST AI 800-5 | 2026-05-18 | `G1 — NIST recognizes an agent-specific security gap` |
| G2 | CISA, *Careful Adoption of Agentic AI Services* | 2026-05-01 | `G2 — CISA and international partners advise bounded, least-privilege adoption` |
| G3 | EU AI Act consolidated text and Regulation (EU) 2026/1744 | 2026-07-27 | `G3 — EU obligations create an implementation runway, not an immediate universal mandate` |
| G4 | OWASP Top 10 for Agentic Applications 2026 | 2025-12-09 | `G4 — Agent-specific threat guidance is now usable` |
| G5 | A2A v1.0 specification | 2026-04 | `G5 — Agent communication is stable while authorization remains local` |
| C1 | Gartner agentic-project cancellation forecast | 2025-06-25 | `C1 — Cancellation risk is material` |
| C2 | Cross-source public operating-evidence check | through freeze | `C2 — Independent runtime-control operating evidence remains sparse` |
| C3 | NIST COSAiS and OWASP AI Agent Security Cheat Sheet | through freeze | `C3 — Conventional controls remain the default challenger` |
| C4a | NIST agent red-team competition | 2026-03-23 | `C4a — Independent government testing found residual hijacking risk` |
| C4b | Anthropic, *How we contain Claude across products* | 2026-05-25 | `C4b — Vendor testing also favors containment beyond the model` |

## Packet integrity

SHA-256:

```text
b927e1957acf97663d7939ffda7884d6031950da4f88c2db7436515de25f74d8  market-signal-episode-001.md
c5b37af3d0680218f23120f17232f18ccee3bdfea09c04bf2e3cda6da92f64bd  market-signal-episode-001-evidence.md
4d4afde90ea761682ab9a2e6d49b5f994f5e4e542e0ae8bae50ecdf478c34120  market-signal-episode-001-brief.md
6ff93ec757dbddfcd59cebed8117b9e8d165d7c86c2e72ebfe078ed454a462dd  market-signal-runbook.md
84e6039b892f0221b18e9e609900850c1e414afcbc8fbb8dd263fb8b3f6ad802  market-signal-episode-001-change-manifest.md
```

Any change to a hashed file requires a new packet version, research-freeze decision, and updated integrity manifest.

