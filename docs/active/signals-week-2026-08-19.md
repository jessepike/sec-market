# Signals week packet — 2026-08-19

Second weekly desk run (one day late — due Tue 2026-08-18, run Wed 2026-08-19). **Not for publication** until lead signs read + headlines.

---

## Control

| Field | Value |
|---|---|
| **Week ID** | `2026-08-19` |
| **RoS issue** | **Security, Funded #257 — SASE and Sound** |
| **RoS URL** | https://www.returnonsecurity.com/p/security-funded-257 |
| **RoS publish date** | 2026-08-17 |
| **Window covered** | Week of **2026-08-10** (per RoS intro) |
| **Status** | `desk-run — lead reviewed 2026-08-19; owner sign-off pending` |
| **Collector** | sec-market weekly desk |
| **Collected at** | 2026-08-19 |
| **Newer issue check** | Homepage confirmed #257 as latest "Security, Funded" post; direct fetch of `/p/security-funded-258` returned **404 Not Found** — #257 is current as of this gather |
| **Funding count** | **4 product-company rounds** (thin week — see note) + **1 public-markets debt raise** (Cloudflare, listed separately, not counted in product total) |
| **M&A count** | **8 deals** (6 product + 2 service) |
| **Sources** | RoS #257 (spine); SYN + Forgepoint spot-check (no net-new names) |
| **Sources that failed to load** | None — RoS #257, SYN Ventures portfolio, and Forgepoint companies all loaded successfully. SecurityWeek monthly M&A roundup was **not checked** per checklist step 3 (skip unless a new month has posted since last gather — still August, same month as the 2026-08-16 packet) |

**Note on thin count:** RoS #257's own Market Summary states only **4 companies** raised private funding this window. The checklist targets 8–15 rows; this packet reports what the source actually shows rather than padding the table. See draft section read.

**Prohibited this run:** no `web/` edits, no deploy, no scrapers, no auto-publish.

**Lead review, 2026-08-19.** Every figure in this packet was re-checked against RoS #257 directly, not accepted from the desk run. The four rounds, the $97.1M total, the $24.3M average and $18.5M median, the eight M&A deals and the single disclosed $94.5M all match the source. Two corrections were applied: the Fortinet market reaction was missing, and the Fortinet billings figure was presented as new when it is a print the site already holds as evidence C3. Both are marked below. What still needs the owner is the section read, the five headlines, and the three heat chips.

---

## RoS market summary (this week)

From Security, Funded #257 (verbatim):

**Private markets:** "4 companies from 3 countries raised $97.1M across 4 unique categories"; average deal size $24.3M (median $18.5M); "100% of disclosed funding was product companies"; "8 companies from 4 countries were acquired for $94.5M across 8 unique categories"; 75% of acquired companies were product companies; 1 company announced layoffs.

**Public markets:** "1 public company raised $2.2B via Post-IPO Debt" (Cloudflare); 1 earnings report — Fortinet ($FTNT), marked **▼ 3.08%** on the day, with RoS citing the "SASE Firewall" strategy driving "33% billings growth amid AI infrastructure and sovereign security demands."

**Lead correction — the Fortinet line is not new.** That 33% billings figure is the *same* Fortinet Q2 2026 print the site already carries as evidence **C3** (quarter ended 2026-06-30, IR release 2026-07-29, excerpt "Revenue grew 26%… Product revenue grew 52%… Billings grew 33%"). RoS is restating a print we froze three weeks ago, not reporting a new one. The only genuinely new fact in the line is the **▼ 3.08% market reaction**, which the first pass of this packet omitted. Nothing here moves the `Fortinet +52%` print on the Network / SASE card, and the open `watch-fortinet` item still reads "next print" — that next print has not landed.

**Labor note (not a funding/M&A event):** Rapid7 reduced headcount by 12% (314 employees), attributed to restructuring and AI investment — noted for context only, not a headline candidate.

---

## Funding events (week of 2026-08-10)

Product companies only. One row per company.

| company | category | event_date | round | amount | investors | source_url | excerpt | confidence |
|---|---|---|---|---|---|---|---|---|
| Corma | AI for Security Ops | 2026-08-10 (week) | Seed | $60.0M | Sequoia Capital | https://www.returnonsecurity.com/p/security-funded-257 | "Corma … raised a $60.0M Seed from Sequoia Capital." | high |
| Mindgard | AI Model Threat Detection | 2026-08-10 (week) | Series A | $30.0M | Album VC | https://www.returnonsecurity.com/p/security-funded-257 | "Mindgard … raised a $30.0M Series A from Album VC." | high |
| Cytix | Penetration Testing / Vuln Mgmt | 2026-08-10 (week) | Series A | $7.0M | Northern Gritstone | https://www.returnonsecurity.com/p/security-funded-257 | "Cytix … raised a $7.0M Series A from Northern Gritstone." | high |
| AlpacaX | Privileged Access Mgmt | 2026-08-10 (week) | Seed | $100.0K | undisclosed | https://www.returnonsecurity.com/p/security-funded-257 | "AlpacaX … raised a $100.0K Seed round. (SEC Filing - may be incomplete)" | medium |

**Public-markets debt raise (same week — not a startup round, not counted in product funding total above):**

| company | category | round | amount | investors | excerpt |
|---|---|---|---|---|---|
| Cloudflare | Secure Networking | Post-IPO Debt | $2.2B | Qualified Institutional Buyers (undisclosed) | "Cloudflare … raised $2.2B in post-IPO debt offering from undisclosed Qualified Institutional Buyers." |

Cloudflare is a public company; this is corporate debt issuance, not venture funding. Listed for completeness because RoS included it, and because it dwarfs the private-funding total this window — but it must not be read as a startup capital signal.

---

## M&A events (same RoS post)

RoS reports 8 total deals, 8 categories, 75% product companies. Matched below: 6 product, 2 service (consistent with that ratio). Only one value is disclosed (CyberCatch).

### Product companies

| acquirer | target | category | value | prior funding (RoS) | excerpt | confidence |
|---|---|---|---|---|---|---|
| Datavault AI | CyberCatch | Security Automation | $94.5M | none disclosed | "CyberCatch … was acquired by Datavault AI for $94.5M. CyberCatch has not previously disclosed funding." | high |
| Seppmail | CyberPilot | Security Awareness | undisclosed | not stated | "CyberPilot … was acquired by Seppmail for an undisclosed amount." | high |
| Privacy Bee | EraseMe.app | Data Removal | undisclosed | not stated | "EraseMe.app … was acquired by Privacy Bee for an undisclosed amount." | high |
| Burson Cohn & Wolfe | Limbik | Trust & Safety | undisclosed | $2.3M | "Limbik … was acquired by Burson Cohn & Wolfe for an undisclosed amount. Limbik had previously raised $2.3M." | high |
| Guardsix | Logmanager | SIEM | undisclosed | not stated | "Logmanager … was acquired by Guardsix for an undisclosed amount." | high |
| Redwood AI | Quantumiq | Post-Quantum Crypto | undisclosed | not stated | "Quantumiq … was acquired by Redwood AI for an undisclosed amount." | high |

**Note — Limbik/Burson Cohn & Wolfe:** the acquirer is a PR/communications firm, not a security vendor. Flagging because it does not fit the usual platform-consolidation pattern; worth a second look if it recurs.

### Service companies

| acquirer | target | category | value | excerpt | confidence |
|---|---|---|---|---|---|
| Andersen Tax | BD Emerson | Risk Advisory | undisclosed | "BD Emerson … was acquired by Andersen Tax for an undisclosed amount." | high |
| New Charter Technologies | CyberTrust IT Solutions | MSSP | undisclosed | "CyberTrust IT Solutions … was acquired by New Charter Technologies for an undisclosed amount." | high |

---

## Portfolio spot-check (SYN + Forgepoint)

**No net-new names this week.** Both portfolios were re-checked against last week's discoveries (2026-08-16 packet):

| company | source | signal | status |
|---|---|---|---|
| Arcade | SYN — Series A 2026 | Secure action layer for production AI agents | already captured 2026-08-16 — not re-promoted |
| Balance Theory | SYN — Series A 2026 | Cybersecurity investment / program intelligence | already captured 2026-08-16 — not re-promoted |
| CodeIntegrity | SYN — Seed 2026 | Runtime control layer for AI agents | already captured 2026-08-16 — not re-promoted |
| Nullify | SYN — Seed 2026 | Autonomous AI workforce for product security | already captured 2026-08-16 — not re-promoted |
| Arkenstone Defense | Forgepoint — First Partnered 2026 | Defense / national-security bridge | already captured 2026-08-16 — not re-promoted |

No new 2026-labeled active names or newly acquired-flag names appeared on either portfolio page this pass. Forgepoint fetched as a single request (no query-string URL; crawl-delay honored by not issuing repeat requests).

---

## Draft section read (3–4 sentences)

Return on Security's week of August 10th was a **notably thin private-funding week** — RoS's own Market Summary counts just **4 companies raising $97.1M** — led by **Corma's $60M Seed** for AI-driven security operations and **Mindgard's $30M Series A** for AI model threat detection, both continuing the AI-native tooling theme from prior weeks. The far larger capital event, **Cloudflare's $2.2B post-IPO debt offering**, is public-markets corporate debt, not venture funding, and should not be read as startup-market heat. M&A stayed busier at **8 deals across 8 categories**, but only one value was disclosed — **CyberCatch's $94.5M acquisition by Datavault AI** in security automation — with the rest small, undisclosed tuck-ins spanning SIEM, post-quantum crypto, and trust & safety. This is capital and consolidation activity, not evidence of buyer spend, and it does not change the published infrastructure-lag market call.

---

## Five draft headlines

1. **Cloudflare — $2.2B post-IPO debt** — largest capital event of the window by a wide margin, but public-markets debt, not a startup round; flag clearly as non-venture in any surface copy.
2. **Datavault AI acquires CyberCatch — security automation — $94.5M** — only disclosed M&A value this week.
3. **Corma — AI for Security Ops — $60M Seed (Sequoia Capital)** — largest private venture round this window.
4. **Mindgard — AI model threat detection — $30M Series A (Album VC)** — continues the AI-native security tooling thread from prior weeks.
5. **Cytix — penetration testing / vuln management — $7M Series A (Northern Gritstone)** — smallest priced round this week worth a slot given how few rounds exist to choose from.

*Alternates for checker swap:* AlpacaX $100K Seed (PAM, SEC-filing caveat — thin); Limbik→Burson Cohn & Wolfe (PR firm acquiring a trust & safety startup, undisclosed value — unusual acquirer type worth watching).

---

## Three heat chips

- **AI-native security ops & threat detection** — Corma, Mindgard; continues prior weeks' AI-governance/AI-threat cluster
- **Platform & category consolidation (M&A)** — Datavault AI/CyberCatch, Guardsix/Logmanager, Redwood AI/Quantumiq — SIEM, security automation, and PQC absorbed into buyers, mostly undisclosed value
- **Public-markets security capital** — Cloudflare $2.2B debt raise, Fortinet earnings — context for private-market comparison, not a startup signal

---

## Conflicts / missing amounts

| item | issue |
|---|---|
| **AlpacaX ($100.0K)** | RoS marks **SEC filing — may be incomplete**; treat as thin/unconfirmed, medium confidence. |
| **Cloudflare ($2.2B)** | **Not a startup funding round** — public-company post-IPO debt. Excluded from the product-company funding count; listed separately so it is not read as private-market heat. |
| **7 of 8 M&A deals** | **Undisclosed value** — only CyberCatch's $94.5M is priced. Do not invent or estimate the rest. |
| **CyberCatch** | RoS states target "has not previously disclosed funding" — no prior-round baseline to compare against the $94.5M acquisition price. |
| **Limbik** | Acquisition value undisclosed, but RoS states $2.3M prior funding — noted for context, not a conflict. |
| **Funding count below target (4 vs. target 8–15)** | RoS's own Market Summary confirms only 4 private companies raised this window — packet reflects source truth rather than padding to hit the target range. |
| **Portfolio spot-check** | No net-new SYN or Forgepoint names this week; the five names from 2026-08-16 (Arcade, Balance Theory, CodeIntegrity, Nullify, Arkenstone Defense) remain the only 2026-labeled discoveries and are not re-promoted as new. |
| **Rapid7 layoff (12%, 314 employees)** | Labor-market signal from RoS, not a funding/M&A event — noted for context only, not eligible for a headline slot. |
| **Fortinet 33% billings** | **Not a new print.** Same Q2 2026 result already frozen as evidence C3 (IR release 2026-07-29). RoS is restating it. Do not surface as new. The `▼ 3.08%` day move is the only new fact. |

---

## Published market call

**Recommendation: keep frozen — no change.**

A thin private-funding week plus a public-company debt raise and mostly-undisclosed M&A from RoS #257 is **capital and consolidation-activity signal**, not a falsifier for Episode 002's **infrastructure-to-security demand lag** call.

The one item in this packet that *looks* like macro evidence — Fortinet's 33% billings growth attributed to AI infrastructure demand — is a print already held as evidence **C3**, and C3 already lists `LAG-NO-CALL` among its conflicting evidence. It was weighed when the call was set. The market also marked the stock down 3.08% on that report. So the packet adds no new macro evidence either way, and the call stands frozen. Human checker must confirm before any call language moves.

---

## What this week does **not** do

- Does not re-dump prior weeks' packets (2026-08-16 or earlier)
- Does not authorize site publish or static-data edits
- Does not merge undisclosed or filing-sourced amounts into certain headline numbers
- Does not count Cloudflare's public-markets debt raise as a startup funding round
- Does not change governing intent or product contract

---

## Exit (this run)

- [x] Week packet sourced from verifiable RoS #257 URL
- [x] 4 product funding rows + 1 public-markets row (separated) + 8 M&A rows captured
- [x] Draft read, five headlines, three heat chips
- [x] Conflicts and thin-count flagged; market call unchanged pending checker
- [x] No code; no `web/` edits

**Next:** Lead human checker — sign or reject read + headlines; poster handoff only if approved later.
