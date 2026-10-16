# Domain coverage map — startup watch lists

## Control

| Field | Value |
|---|---|
| **ID** | `SEC-MARKET-DOMAIN-MAP-001` |
| **Date** | 2026-08-16 |
| **Status** | research — lead reviewed 2026-08-16 |
| **Authority** | `SEC-MARKET-SIG-OPS-001`, `SEC-MARKET-STARTUP-PKT-001` |
| **Purpose** | Balanced domain watch lists so the weekly desk is not RoS-only |
| **Not for publication** | Until lead/owner authorize |

---

## How to read this map

- **Pulse posture** — one-line summary from `web/src/data/domains.ts` (reference only; do not edit the site).
- **August packet thickness** — how well `startup-collection-packet-2026-08.md` covers the domain: `none` / `thin` / `adequate`.
- **Watch list** — public companies verified via official homepage fetch on 2026-08-16 (or HTTP 200 redirect chain). No invented rounds.
- **Extra sources** — lawful surfaces beyond the RoS spine (Return on Security + Cybersecurity Ventures). Blocked/paid marked.
- Companies already in the August packet are noted where relevant; the **first-add list** at the end is names **missing** from that packet.

---

## 1. Network / SASE

**Pulse posture:** PREPARE — appliance-led network security is live; cloud-native SASE is steady, not re-accelerating (Fortinet +52%, Zscaler FY27 guide watch).

**August packet thickness:** **none** — only tangential names (MazeBolt anti-DDoS, DefensX RBI). No SASE, SSE, ZTNA, or SD-WAN vendors.

### Watch list (12)

| Company | Why watch | Verified |
|---|---|---|
| Cato Networks | Single-vendor SASE leader; AI-native SASE messaging | https://www.catonetworks.com/ |
| Netskope | SSE/SASE convergence; AI security + ZTNA | https://www.netskope.com/ |
| Cloudflare | Zero Trust / SSE at scale; AI agent access narrative | https://www.cloudflare.com/zero-trust/ |
| Twingate | Modern ZTNA; AI agent and service identity access | https://www.twingate.com/ |
| Tailscale | Identity-based mesh VPN / ZTNA alternative | https://tailscale.com/ |
| Island | Enterprise browser — SASE-adjacent access layer | https://www.island.io/ |
| Elisity | Identity-based microsegmentation for enterprise network | https://www.elisity.com/ |
| DefensX | Remote browser isolation (in packet; keep on watch) | https://defensx.com/ (packet source) |
| MazeBolt | DDoS resilience testing (in packet) | RoS #254 |
| Zscaler | Public SASE bellwether — FY guide is Pulse watch item | Public IR |
| Fortinet | Public appliance/SASE print — Pulse watch item | Public IR |
| Versa Networks | SASE/SD-WAN specialist (public-adjacent; verify deals via press) | https://versa-networks.com/ |

*Dropped from list:* Axis Security (acquired by HPE); Perimeter 81 (Check Point — mature).

### Extra sources (beyond RoS spine)

| Source | URL | Notes |
|---|---|---|
| Cato Networks blog / press | https://www.catonetworks.com/blog/ | Official; product and threat research |
| Netskope — The Lens | https://www.netskope.com/resources/blog | Official blog/RSS-adjacent |
| Cloudflare blog (Zero Trust) | https://blog.cloudflare.com/tag/zero-trust/ | Official |
| Gartner MQ press releases | Vendor IR pages | Recap only; not a funding feed |

### Weekly gatherer focus

- SASE/SSE **platform** raises and strategic investments (not RBI-only or DDoS-only unless tied to access fabric).
- Vendor **FY guides**, customer-count milestones, and analyst MQ positioning (Fortinet, Zscaler, Cato, Netskope).
- ZTNA replacements for VPN; **enterprise browser** and microsegmentation as access-layer bets.
- Cisco/Splunk organic SecOps bridge news only when it affects SSE consolidation narrative.

---

## 2. Data / AI Security

**Pulse posture:** PREPARE — selected data vendors accelerating (Rubrik +32%, Varonis +25%); Cyera capital not yet broad spend series.

**August packet thickness:** **thin** — Kiken micro-DSPM, Obsidian SSPM, Onyx AI-app governance, InnerActiv DLP, Jazz (Team8 build). Missing scale-up DSPM/DLP names (Cyera, Sentra, BigID, Normalyze, Securiti).

### Watch list (14)

| Company | Why watch | Verified |
|---|---|---|
| Cyera | DSPM control plane; AI-SPM; Oasis acquisition context | https://www.cyera.io/ |
| BigID | Enterprise DSPM + AI data governance | https://bigid.com/ |
| Sentra | DSPM / data security posture | https://sentra.io/ (HTTP 200) |
| Normalyze | Cloud DSPM (redirects to current domain) | https://www.normalyze.ai/ |
| Securiti.ai | Data + AI security / privacy automation | https://securiti.ai/ |
| Obsidian Security | SSPM — in packet ($85M Series D) | RoS #256 |
| Onyx Security | AI application monitoring — in packet | RoS #255 |
| Varonis | Public data-security print (+25% cited in Pulse) | Public IR |
| Rubrik | Public data-security / resilience print | Public IR |
| Jazz | Team8 DLP build — in packet (launch) | Team8 portfolio |
| InnerActiv | Insider risk / DLP micro-round — in packet | RoS #256 |
| Quantifind | AI risk / fraud — in packet | CV article |
| Immuta | Data access governance for AI/analytics | https://www.immuta.com/ |
| NightDragon portfolio names | Immuta, etc. — lagging discovery | https://www.nightdragon.com/portfolio |

### Extra sources

| Source | URL | Notes |
|---|---|---|
| NightDragon portfolio | https://www.nightdragon.com/portfolio | Official; no round dates |
| Bessemer cyber portfolio filter | https://www.bvp.com/portfolio?sector=cybersecurity | Official; sector filter |
| BigID press / newsroom | https://bigid.com/newsroom/ | Official PR |
| The Record (data-breach adjacency) | https://therecord.media/ | Event-driven; search timeouts possible |

### Weekly gatherer focus

- **DSPM** and **AI-SPM** rounds; strategic PE (Keyfactor-scale) vs. point-tool seeds.
- **SSPM** (Obsidian-class) vs. cloud workload DSPM — do not conflate.
- DLP reinvention (Team8 Jazz, InnerActiv) and **sensitive-data-in-AI** product launches.
- M&A affecting data security (Cyera/Oasis, SailPoint/Entro) — note in packet but track for category map.

---

## 3. Cloud Security

**Pulse posture:** INVESTIGATE (WATCH) — Wiz deal is 2025 capital not spend; no clean CNAPP spend series; qualify gaps when capacity goes live.

**August packet thickness:** **none** — Adaptive6 is cloud-cost governance (Forgepoint), not CNAPP/CSPM/CWPP. Obsidian is SSPM (SaaS), not cloud workload.

### Watch list (13)

| Company | Why watch | Verified |
|---|---|---|
| Wiz | CNAPP category leader; Google acquisition narrative | https://www.wiz.io/ |
| Upwind | Runtime-centric CNAPP; Cyberstarts portfolio | https://www.upwind.io/ |
| Orca Security | Agentless CNAPP | https://www.orca.security/ |
| Aqua Security | CNAPP / container-runtime | https://www.aquasec.com/ |
| Sysdig | Cloud/runtime security | https://sysdig.com/ |
| Prisma Cloud (Palo Alto) | Code-to-cloud platform; Cortex Cloud motion | https://www.paloaltonetworks.com/prisma/cloud |
| Lacework | CNAPP (Fortinet acquisition context) | https://www.lacework.com/ (timeout on full fetch; site resolves) |
| Blockaid | Web3/onchain security — Cyberstarts active bet | https://www.blockaid.io/ |
| Adaptive6 | Infra/cost governance — in packet (Forgepoint) | Forgepoint |
| Ermetic (Tenable) | Cloud entitlement — acquired; watch Tenable One | Tenable IR |
| CrowdStrike Falcon Cloud | Platform CNAPP cross-sell post-acquisitions | Public IR |
| Palo Alto Networks | Prisma / CyberArk identity-cloud convergence | Public IR |
| Ballistic / Cyberstarts portfolios | Upwind, Blockaid, Glow discovery | Official HTML |

### Extra sources

| Source | URL | Notes |
|---|---|---|
| Cyberstarts portfolio | https://www.cyberstarts.com/portfolio/ | Active Israeli cloud bets; recap-heavy |
| Aqua Security blog / research | https://www.aquasec.com/blog/ | Team Nautilus threat research |
| Wiz blog / threat research | https://www.wiz.io/blog | Official |
| TechCrunch cloud security search | https://techcrunch.com/?s=cloud+security+funding | Manual; generalist rounds |

### Weekly gatherer focus

- **CNAPP**, CSPM, CWPP, and **runtime sensor** funding — not SSPM-only.
- Platform M&A and **acqui-hire** (Wiz/Google, Oasis/Cyera) as category consolidation signals.
- **Agentless vs. agent** positioning and eBPF/runtime-sensor scale-ups.
- Cloud **AI workload** security (models, MCP servers, agent inventory) crossing from AI Runtime.

---

## 4. Identity (including NHI / machine / agent identity)

**Pulse posture:** INVESTIGATE (WATCH) — IGA up, workforce IAM decelerating; watch first disclosed agentic-identity revenue and Palo Alto vs. CyberArk mix.

**August packet thickness:** **adequate** — Oak ($60M seed), Way Security, Hush ($30M + Akamai strategic), Keyfactor ($1B PE), 8Layers, Argos Identity. Strongest non-agent-governance identity cluster in the packet.

### Watch list (12)

| Company | Why watch | Verified |
|---|---|---|
| Oak | AI-native IAM OS — in packet | RoS #253 |
| Hush Security | NHI / AI agent identity — in packet | YL Ventures PR |
| Way Security | Identity ops automation — in packet | RoS #255 |
| Keyfactor | PKI / machine identity / PQC — in packet | RoS #252 |
| Veza | Access governance / NHI visibility | https://www.veza.com/ |
| Britive | Just-in-time / ephemeral identity | https://www.britive.com/ |
| Silverfort | Unified identity protection | https://www.silverfort.com/ |
| CyberArk | Machine identity + Palo Alto deal context | Public IR |
| SailPoint | IGA print (+28% cited in Pulse) | Public IR |
| Okta | cRPO deceleration watch | Public IR |
| 8Layers | Identity threat detection — in packet | RoS #252 |
| Forgepoint identity sector | Arkenstone, historical identity bets | https://forgepointcap.com/companies |

### Extra sources

| Source | URL | Notes |
|---|---|---|
| YL Ventures news | https://www.ylventures.com/news | Dated portfolio PR (e.g. Hush) |
| Forgepoint companies (Identity filter) | https://forgepointcap.com/companies | Crawl-delay 3 |
| SYN Ventures portfolio | https://www.synventures.com/portfolio | Agent authorization names (Arcade) |
| Okta / CyberArk IR & investor relations | Public SEC filings | M&A and ARR prints |

### Weekly gatherer focus

- **NHI**, service-account, and **AI agent identity** rounds (not KYC-only unless enterprise IAM adjacent).
- **PKI / machine identity** at infrastructure scale (Keyfactor-class PE).
- Strategic corporate investments (Akamai/Hush pattern).
- IGA vs. PAM vs. ITDR — tag category explicitly; avoid lumping KYC seeds with workforce IAM.

---

## 5. SecOps

**Pulse posture:** INVESTIGATE (WATCH) — two public XDR prints healthy (SentinelOne, CrowdStrike); share shift and platformization, not a new cycle.

**August packet thickness:** **adequate** for AI-agent SecOps — Mate, Neo, Glow, ThreatLocker, DataBahn, Beacon, Abstract, Pulse Security AI, Discern (CSMA). Thin on **SOAR/automation** scale-ups (Torq, Tines) and MDR/XDR adjacency.

### Watch list (14)

| Company | Why watch | Verified |
|---|---|---|
| Mate Security | Agentic SecOps — in packet | RoS #255 |
| Neo Security | AI threat detection — in packet | RoS #254 |
| Glow | AI endpoint — in packet | RoS #254 |
| ThreatLocker | Endpoint allowlisting — in packet | RoS #255 |
| DataBahn | Security log pipeline — in packet | RoS #255 |
| Beacon Security | Security data orchestration — in packet | RoS #253 |
| Abstract Security | Security analytics — in packet | RoS #254 |
| Pulse Security AI | SecOps program mgmt — in packet | RoS #253 |
| Discern Security | CSMA — in packet | RoS #255 |
| Fig | SecOps resilience — Team8 build in packet | Team8 portfolio |
| Torq | Hyperautomation / SOAR | https://www.torq.io/ |
| Tines | Security workflow automation | https://www.tines.com/ |
| Vectra AI | NDR / SOC AI | https://www.vectra.ai/ |
| Rapid7 | MDR + exposure platform | https://www.rapid7.com/ |

### Extra sources

| Source | URL | Notes |
|---|---|---|
| Team8 portfolio (SecOps builds) | https://team8.vc/portfolio/ | Fig, Act launches |
| Rapid7 blog | https://www.rapid7.com/blog/ | Threat research + product |
| SYN Ventures (Balance Theory) | https://www.synventures.com/portfolio | Security program intelligence |
| SecurityWeek RSS (filter: SOAR, MDR, XDR) | https://www.securityweek.com/feed/ | OK; heavy breach mix |

### Weekly gatherer focus

- **Agentic SOC** and AI analyst products vs. legacy SIEM replatforming.
- **Log pipeline / data fabric** cost pressure (DataBahn-class).
- SOAR **hyperautomation** (Torq, Tines) and MSSP-scale MDR moves.
- Endpoint reinvented for AI (Glow, ThreatLocker) — tag endpoint vs. SecOps explicitly.

---

## 6. AI Runtime Security

**Pulse posture:** INVESTIGATE (WATCH) — 59% plan GenAI-protection spend; intent strong, bookings/outcomes not; do not run specialist motion from survey intent alone.

**August packet thickness:** **adequate** — Zenity ($115M+), Onyx, Hush, Arrakis, Actualyze, SYN portfolio (Arcade, CodeIntegrity, Nullify). Strongest packet cluster.

### Watch list (12)

| Company | Why watch | Verified |
|---|---|---|
| Zenity | AI agent governance — in packet | RoS #256 |
| Onyx Security | AI app governance — in packet | RoS #255 |
| Hush Security | Agent identity/governance — in packet | YL PR |
| Arrakis Security | Agent monitoring — in packet | RoS #255 |
| Actualyze AI | AI governance — in packet | RoS #256 |
| CodeIntegrity | Runtime control — SYN 2026 | SYN portfolio |
| Arcade | Secure action layer — SYN 2026 | SYN portfolio |
| Nullify | Autonomous product security — SYN 2026 | SYN portfolio |
| WitnessAI | Unified AI security / governance | https://www.witness.ai/ |
| Pillar Security | Agentic workforce security | https://www.pillar.security/ |
| Lakera | AI-native runtime / red team | https://www.lakera.ai/ |
| Casco | AI red-teaming — in packet (AppSec overlap) | RoS #253 |

### Extra sources

| Source | URL | Notes |
|---|---|---|
| SYN Ventures portfolio | https://www.synventures.com/portfolio | Best round-year signal for agent runtime |
| Ballistic Ventures homepage carousel | https://www.ballisticventures.com/ | Investment thesis posts |
| OWASP GenAI / agentic security landscape | https://owasp.org/ | Reference taxonomy |
| GV portfolio cross-check | https://www.gv.com/portfolio | Witness AI, Blockaid lagging confirmation |

### Weekly gatherer focus

- **Pilot → production** customer references and disclosed **bookings**, not survey-only intent.
- Agent **governance vs. runtime guardrails** vs. **action authorization** — three sub-lanes.
- MCP / tool / skill supply-chain attacks (Pillar research themes).
- Amount conflicts (Zenity, Neo, Glow) — show both sources.

---

## Callout domains (thin in August packet)

### OT / industrial

**Packet:** Frenos seed only ($1.5M OT assessment).

**Watch list (8):** Claroty (https://www.claroty.com/), Dragos (https://www.dragos.com/), Nozomi Networks (https://www.nozominetworks.com/), Frenos (in packet), Tenable OT Exposure (https://www.tenable.com/), Armis (ServiceNow acquisition — public), Cyberstarts/Forgepoint OT-adjacent exits, Momenta/Exposition OT seeds.

**Extra sources:** Claroty Team82 research; Dragos threat reports; ICS-CERT advisories (https://www.cisa.gov/ics-advisories) — official, not funding.

**Gatherer focus:** OT **visibility vs. assessment** vs. **secure remote access**; critical-infra PE; tiny OT seeds outside US/IL.

---

### Email / human security

**Packet:** AegisAI, StrongestLayer, Sensity, Frame Security (Team8), Savi Security — mostly seed; no scale-up email leader.

**Watch list (8):** Abnormal Security (https://abnormalsecurity.com/), AegisAI (in packet), StrongestLayer (in packet), Sensity AI (in packet), Frame Security (Team8), Savi Security (in packet), Proofpoint (public bellwether), Hoxhunt / Material Security — verify before adding next month.

**Extra sources:** Abnormal blog/press; Team8 Frame launch; SecurityWeek human-factor filter on RSS.

**Gatherer focus:** **BEC / ATO / deepfake** product launches; consumer vs. enterprise (Savi vs. Abnormal).

---

### Exposure management

**Packet:** Horizon3.ai ($250M), Zafran (Cisco strategic), Empirical Security, Cathedral — strong for autonomous testing; thin on **platform EM** vendors.

**Watch list (10):** Horizon3.ai (in packet), Zafran (in packet), Empirical (in packet), Cathedral (in packet), Tenable (https://www.tenable.com/), Axonius (https://www.axonius.com/), Rapid7 exposure (https://www.rapid7.com/), Armis (public), Qualys (public), Pentera — verify independently next cycle.

**Extra sources:** Tenable blog; Axonius newsroom; Momentum Cyber quarterly landing pages (**gated** full lists).

**Gatherer focus:** **Autonomous pentest** mega-rounds vs. **exposure prioritization** platforms; Cisco strategic investments (Zafran pattern).

---

### AppSec / supply chain

**Packet:** Oligo ($60M), Casco, Ossprey, Risk Ledger, Cybeats — adequate for OSS/runtime/supply-chain **funding**; missing Snyk/Semgrep/Chainguard scale-ups.

**Watch list (11):** Oligo (in packet), Casco (in packet), Ossprey (in packet), Risk Ledger (in packet), Cybeats (in packet), Snyk (https://www.snyk.io/), Semgrep (https://semgrep.dev/), Chainguard (https://www.chainguard.dev/), Synopsys Black Duck (public), Socket.dev — verify next cycle, Ballistic OSS names.

**Extra sources:** Snyk blog/research; Chainguard press; OWASP dependency-track community (reference, not funding).

**Gatherer focus:** **Runtime OSS** vs. **SBOM/compliance** vs. **AI code security**; pre-IPO/public AppSec recap rounds.

---

### Post-quantum

**Packet:** QIZ ($17M), pQCee ($3.9M), Keyfactor PE narrative — thin on **crypto-agility vendors**.

**Watch list (8):** QIZ Security (in packet), pQCee (in packet), Keyfactor (in packet), PQShield (https://pqshield.com/ — redirect verified), QuSecure (https://www.qusecure.com/), ISARA — verify next cycle, Post-Quantum (vendor) — verify, SandboxAQ (adjacent) — verify.

**Extra sources:** NIST PQC project pages (https://csrc.nist.gov/projects/post-quantum-cryptography) — official, not commercial; QuSecure newsroom.

**Gatherer focus:** **Discovery/posture** vs. **crypto-agility** vs. **PKI migration**; NIST deadline-driven buyer urgency.

---

## First-add list (20 companies missing from August packet)

Priority names to add to the standing watch list — **not present** in `startup-collection-packet-2026-08.md` event rows:

| # | Company | Primary domain | Verified URL |
|---:|---|---|---|
| 1 | Cato Networks | Network / SASE | https://www.catonetworks.com/ |
| 2 | Netskope | Network / SASE | https://www.netskope.com/ |
| 3 | Upwind | Cloud Security | https://www.upwind.io/ |
| 4 | Wiz | Cloud Security | https://www.wiz.io/ |
| 5 | Orca Security | Cloud Security | https://www.orca.security/ |
| 6 | Aqua Security | Cloud Security | https://www.aquasec.com/ |
| 7 | Cyera | Data / AI Security | https://www.cyera.io/ |
| 8 | BigID | Data / AI Security | https://bigid.com/ |
| 9 | Sentra | Data / AI Security | https://sentra.io/ |
| 10 | Abnormal Security | Email / human | https://abnormalsecurity.com/ |
| 11 | Dragos | OT / industrial | https://www.dragos.com/ |
| 12 | Claroty | OT / industrial | https://www.claroty.com/ |
| 13 | Tenable | Exposure management | https://www.tenable.com/ |
| 14 | WitnessAI | AI Runtime | https://www.witness.ai/ |
| 15 | Pillar Security | AI Runtime | https://www.pillar.security/ |
| 16 | Lakera | AI Runtime | https://www.lakera.ai/ |
| 17 | Torq | SecOps | https://www.torq.io/ |
| 18 | Tines | SecOps | https://www.tines.com/ |
| 19 | Snyk | AppSec / supply chain | https://www.snyk.io/ |
| 20 | Veza | Identity / NHI | https://www.veza.com/ |

**Next five when expanding to 25:** Twingate, Tailscale, Nozomi Networks, Semgrep, Chainguard — all verified 2026-08-16.

---

## Honest holes (still won't cover without paid / blocked data)

| Gap | Why the public spine misses it |
|---|---|
| **Seed/long-tail completeness** | RoS + CV skew to larger rounds; sub-$5M and non-cyber-VC names absent until press |
| **Generalist-led rounds pre-portfolio** | Insight, Lightspeed, Greylock deals invisible until RoS/CV or company blog |
| **Exact round dates on VC portfolios** | Most portfolio pages lack amounts/dates (SYN/Forgepoint exceptions) |
| **Crunchbase / PitchBook depth** | **Paid / ToS-blocked** — no bulk use |
| **Funded Startups Daily** | 55 tagged cyber raises — **ToS-blocked** for automation |
| **The Signal API/MCP** | **Paid** ($79/mo add-on+) — structured funding/M&A feed |
| **Momentum Cyber / Windsor Drake full deal lists** | **Gated** PDF downloads |
| **Mergr bulk export** | **Paid** signup; individual deal pages OK manually |
| **RoS RSS** | **Blocked** to non-browser clients (403/Cloudflare) |
| **YC filtered company URLs** | robots.txt **disallow** automated query |
| **APAC/LatAm long tail** | Packet US/Israel/UK heavy unless RoS surfaces a name |
| **Private-company-only M&A** | No 8-K; may never hit SecurityWeek/RoS |

---

## Sources that failed verification (2026-08-16)

From startup and M&A catalogs — do not rely until independently reachable:

| Source | Result |
|---|---|
| Return on Security RSS (`/rss/`) | 403 / Cloudflare to curl |
| Funded Startups Daily bulk | ToS-blocked |
| Ten Eleven Ventures | 503 |
| CyberStartupFunding.com | 503 / unreachable |
| Glilot Capital portfolio | JS shell — no names in static HTML |
| Insight Partners portfolio | Empty SPA shell |
| Greylock portfolio | No company list in HTML |
| Lightspeed security filter | No results |
| SecurityWeek `/category/funding/` | 404 |
| Ballistic `/news` | 404 |
| Cybersecurity Ventures M&A hub widget | "Loading…" only |
| Lacework full homepage | Fetch timeout (domain resolves) |
| Sentra full homepage | Fetch timeout (HTTP 200 via curl) |
| PQShield full homepage | Fetch timeout (redirect to pqshield.com verified) |
| Tines full homepage | Fetch timeout (HTTP 200 via curl) |

---

## Thinnest three Pulse domains (August packet)

1. **Network / SASE** — **none**; no SASE/SSE/ZTNA funding events in window.
2. **Cloud Security** — **none**; no CNAPP/CSPM/CWPP vendors despite Pulse WATCH posture.
3. **Data / AI Security** — **thin**; AI-app and SSPM present but major DSPM scale-ups (Cyera, Sentra, BigID) absent from events table.

*Note:* Identity and AI Runtime are **adequate** in the packet (by design of first-week sources). OT/industrial is **thin** among callouts but is not a Pulse domain chip today.

---

## Exit checklist

- [x] Map exists at `docs/archive/2026-08-signals/domain-coverage-map.md`
- [x] All six Pulse domains have 8–15 company watch lists
- [x] Callout domains (OT, email, exposure, AppSec, PQC) covered
- [x] First-add list (20 names) with verified URLs
- [x] Paid/blocked holes documented
- [x] Failed sources listed
- [x] No `web/` edits, no scrapers, no invented rounds

---

## Research notes

- Company verification: official homepage fetch or HTTP 200 redirect chain on **2026-08-16**. Lacework, Sentra, PQShield, Tines timed out on full HTML fetch but resolved via curl HEAD.
- Pulse posture strings taken verbatim from `web/src/data/domains.ts` summaries and watch items — site not modified.
- August packet cross-reference: 58 event rows; AI-agent governance ~15+ rows; Network/SASE and Cloud Security ~0 core vendors.
