# Domain vendor signals — August 2026 operator pass

## Control

| Field | Value |
|---|---|
| **ID** | `SEC-MARKET-DOMAIN-VENDOR-SIG-001` |
| **Date** | 2026-08-16 |
| **Status** | operator — lead reviewed 2026-08-16 |
| **Authority** | `SEC-MARKET-DOMAIN-MAP-001`, `SEC-MARKET-SIG-OPS-001` |
| **Operator** | sec-market research worker |
| **Scope** | Six Pulse domains × 6 target vendors each (36 slots) |
| **Method** | Official IR / company press / SEC filings fetched 2026-08-16. No Crunchbase, PitchBook, LinkedIn, or Funded Startups Daily. Raises are capital signals, not buyer spend. |
| **Posture** | Unchanged — reference only from `web/src/data/domains.ts`; no site edits. |

---

## Summary for lead

| Metric | Count |
|---|---|
| Target vendors attempted | 36 / 36 |
| Slots with a real 2025–2026 signal | 34 / 36 |
| `NO-PRINT` (checked, no qualifying public number) | 2 (Orca Security, Aqua Security) |
| Domains at 5–6 signal bar | 5 / 6 |
| Domains below bar | **Cloud Security** (4 of 6 with signals; Orca + Aqua open) |

**Five highest-value signals not already on the live prints board** (vendor cards in `web/src/data/prints.ts`):

1. **Cato Networks** — 2025 ARR **>$350M**, **+43% YoY** (private SASE print; fills Network/SASE gap).
2. **Netskope** — FY26 ARR **$811M**, **+31% YoY** (public SSE/SASE bellwether now on IR).
3. **Upwind** — **$250M** Series B at **$1.5B** valuation (Jan 2026; first Cloud-domain CNAPP capital signal in packet).
4. **CrowdStrike Falcon Cloud** — ending ARR **>$800M**, **>35% YoY** (Q4 FY26 cloud segment — distinct from total ARR card).
5. **Torq** — **$140M** Series D at **$1.2B** valuation (Jan 2026; SOAR/agentic SecOps scale signal).

Also material for desk: **Securiti / Veeam close at $1.725B** (Dec 2025), **WitnessAI $58M** (Jan 2026), **Zenity $125M Series C** (Aug 2026 official; RoS had $115M).

---

## 1. Network / SASE

**Pulse posture (reference):** PREPARE — appliance-led network security is live; cloud-native SASE steady, not re-accelerating.

| Vendor | Signal type | Date | Number | Already on site? | Source URL | Excerpt | Confidence |
|---|---|---|---|---|---|---|---|
| Fortinet | Earnings | 2026-07-29 | +52% product revenue (Q2 2026) | Yes — `print-fortinet` / C3 | https://investor.fortinet.com/news-releases/news-release-details/fortinet-reports-strong-second-quarter-2026-financial-results | "Product revenue grew 52%… Billings grew 33%." | high |
| Zscaler | Earnings | 2026-05-26 | +21% organic ARR (Q3 FY26) | Yes — `print-zscaler` / C4 | https://www.sec.gov/Archives/edgar/data/1713683/000171368326000095/zs-04302026_991.htm | "ARR grew 25%, or 21%, excluding the contribution from the Red Canary acquisition." | high |
| Cloudflare | Earnings | 2026-08-06 | +36% revenue (Q2 2026) | Yes — `print-cloudflare` / C5 | https://www.cloudflare.com/en-gb/press/press-releases/2026/cloudflare-announces-second-quarter-2026-financial-results/ | "Second quarter revenue totaled $696.1 million, representing an increase of 36% year-over-year." | high |
| Check Point | Earnings | 2026-06-30 | +1% revenue (Q2 2026) | Yes — `print-checkpoint` / C6a | https://www.checkpoint.com/downloads/investor/check-point-software-second-quarter-2026-financial-results.pdf | "Check Point revenue grew approximately 1 percent while security subscriptions grew 12 percent." | high |
| Cato Networks | ARR print | 2026-02-24 | >$350M ARR; +43% YoY (2025) | No | https://www.catonetworks.com/news/cato-surpasses-350-million-arr-with-43-yoy-growth-in-2025/ | "Its 2025 annual recurring revenue (ARR) surpassed $350 million, an increase of 43% year-over-year (YoY) compared to 2024." | high |
| Netskope | Earnings | 2026-03-11 | $811M ARR; +31% YoY (FY26) | No | https://investors.netskope.com/news-releases/news-release-details/netskope-announces-strong-fourth-quarter-and-fiscal-year-2026 | "ARR grew 31% year-over-year to $811 million as of January 31, 2026." | high |

---

## 2. Cloud Security

**Pulse posture (reference):** INVESTIGATE (WATCH) — Wiz deal is 2025 capital, not spend; no clean CNAPP spend series.

| Vendor | Signal type | Date | Number | Already on site? | Source URL | Excerpt | Confidence |
|---|---|---|---|---|---|---|---|
| Wiz | M&A close | 2026-03-11 | ~$32B (announced 2025-03-18) | Activity — D5a, D13; not on prints board | https://blog.google/innovation-and-ai/infrastructure-and-cloud/google-cloud/wiz-acquisition/ | "Google LLC today announced the completion of its acquisition of Wiz… initially announced in March 2025." | high |
| Palo Alto (Prisma / Cortex Cloud) | Earnings call metric | 2026-06-02 | 300+ Prisma AIRS customers (Q3 FY26) | Platform print only — `print-panw` +14% organic; no cloud SKU print | https://investors.paloaltonetworks.com/news-releases/news-release-details/palo-alto-networks-reports-fiscal-third-quarter-2026-financial | Q3 FY26 call: "We have over 300 Prisma AIRS customers as of Q3, up from just 100 at the end of Q2." (Product adoption; not ARR.) | medium |
| CrowdStrike (Falcon Cloud) | Earnings call metric | 2026-03-03 | >$800M cloud ending ARR; >35% YoY | SecOps card only (+24% total ARR); no cloud segment on prints board | https://ir.crowdstrike.com/news-releases/news-release-details/crowdstrike-reports-fourth-quarter-and-fiscal-year-2026 | Q4 FY26 call: "For the first time, our cloud business exceeded $800 million in ending ARR… grew more than 35% year over year." | high |
| Orca Security | — | — | **NO-PRINT** | No | https://orca.security/resources/press-releases/orca-security-td-synnex-partnership/ | Checked official site + Apr 2026 TD SYNNEX GTM PR — no 2025–2026 funding, revenue, or M&A with a disclosed dollar figure. Last equity round Series C $550M (Oct 2021). | high (negative) |
| Aqua Security | — | — | **NO-PRINT** | No | https://www.aquasec.com/news/aqua-security-doubles-down-on-runtime-to-deliver-measurable-cloud-risk-reduction/ | Checked Feb 2026 transformation PR and 2025 leadership posts — no 2025–2026 ARR/revenue/funding/M&A number. Last funding Series E extension $60M (Jan 2024). | high (negative) |
| Upwind | Funding | 2026-01-26 | $250M Series B; $1.5B valuation; $430M total raised | No | https://www.securityweek.com/upwind-raises-250-million-at-1-5-billion-valuation/ | "Upwind today announced raising $250 million in a Series B funding round… valuation to $1.5 billion… total raised… $430 million." (Company-quoted; official `/press` URL 404 on fetch.) | medium |

---

## 3. Data / AI Security

**Pulse posture (reference):** PREPARE — selected data vendors accelerating; Cyera capital not yet broad spend series.

| Vendor | Signal type | Date | Number | Already on site? | Source URL | Excerpt | Confidence |
|---|---|---|---|---|---|---|---|
| Rubrik | Earnings | 2026-06-04 | +32% subscription ARR; $1.57B (Q1 FY27) | Yes — `print-rubrik` / C8a | https://ir.rubrik.com/news-events/press-releases/news-details/2026/Rubrik-Reports-First-Quarter-Fiscal-Year-2027-Financial-Results/default.aspx | "Subscription ARR was up 32% year-over-year, growing to $1.57 billion." | high |
| Varonis | Earnings | 2026-07-28 | +25% SaaS ARR ex-conversions (Q2 2026) | Yes — `print-varonis` / C8b | https://www.sec.gov/Archives/edgar/data/1361113/000117184326004948/exh_991.htm | "SaaS ARR excluding conversions growth of 25%." | high |
| Cyera | Funding | 2026-06-10 | $600M Series G; $12B valuation | Yes — `print-cyera` / D8 (Activity) | https://www.cyera.com/press-releases/cyera-raises-600-million-at-12-billion-valuation-to-continue-building-the-trust-layer-for-the-ai-era | "Latest funding round of $600 million… valuation… to $12 billion." | high |
| BigID | Revenue milestone (company-stated) | 2025-05-16 | >$100M revenue | No | https://www.prweb.com/releases/bigid-expands-global-partner-strategy-with-appointment-of-ian-williamson-as-svp-of-global-channel--alliances-302454829.html | "BigID is the first data security posture management (DSPM) platform to surpass $100M in revenue." | medium |
| Sentra | Funding | 2025-04-22 | $50M Series B; >$100M total funding; >300% YoY revenue (company-stated) | No | https://sentra.io/news/sentra-closes-50-million-series-b-amid-surging-demand-for-securing-data-for-ai-adoption | "Closed a $50 million Series B… total investment to more than $100 million, following a more than 300% year-over-year increase in revenue." | high |
| Securiti | M&A close | 2025-12-11 | $1.725B acquisition price | No | https://www.veeam.com/company/press-release/veeam-acquires-securiti-ai.html | "Completion of its $1.725 billion acquisition of Securiti AI." | high |

---

## 4. Identity

**Pulse posture (reference):** INVESTIGATE (WATCH) — IGA up, workforce IAM decelerating; watch agentic-identity revenue.

| Vendor | Signal type | Date | Number | Already on site? | Source URL | Excerpt | Confidence |
|---|---|---|---|---|---|---|---|
| Okta | Earnings | 2026-05-28 | +12% cRPO (Q1 FY27) | Yes — `print-okta` / C7 | https://www.sec.gov/Archives/edgar/data/1660134/000166013426000050/okta-4302026_ex991.htm | "cRPO $2.499 billion, +12 percent." | high |
| SailPoint | Earnings | 2026-03-18 | +28% total ARR (FY26) | Yes — `print-sailpoint` / C10 | https://www.sec.gov/Archives/edgar/data/2030781/000162828026019034/sailpointinc-20260131x991x.htm | "Total ARR was $1.125 billion, an increase of 28% year-over-year." | high |
| CyberArk | M&A close | 2026-02-11 | ~$25B (announced 2025-07-30) | Yes — `print-cyberark` / D14 | https://www.paloaltonetworks.com/company/press/2026/palo-alto-networks-completes-acquisition-of-cyberark-to-secure-the-ai-era/ | "Completion of its acquisition of CyberArk… shareholders… $45.00 in cash and 2.2005 shares… for each CyberArk ordinary share." | high |
| Oak | Funding | 2026-07-15 | $60M seed | No (August packet / RoS only) | https://www.prnewswire.com/news-releases/oak-raises-60m-in-seed-funding-to-build-the-ai-native-identity-operating-system-302826349.html | "Oak emerged from stealth today with $60 million in seed funding… co-led by Accel, Greylock Partners, and CRV." | high |
| Hush Security | Funding | 2026-07-28 | $30M Series A; $41M total | No (August packet / YL PR only) | https://www.ylventures.com/news/hush-security-raises-30m-to-close-the-ai-agent-governance-gap-with-akamai-joining-as-strategic-investor | "$30 million Series A funding round… total capital raised to $41 million." | high |
| Veza | M&A (intent → close) | 2025-12-02 | undisclosed (closed 2026-03-02) | No | https://newsroom.servicenow.com/press-releases/details/2025/ServiceNow-to-Expand-Security-Portfolio-With-Acquisition-of-Vezas-Leading-AI-native-Identity-Security-Platform/default.aspx | "Intent to acquire Veza… Update: The Veza acquisition closed on March 2, 2026." (Alternate 2025 signal: Series D $108M at $808M valuation, 2025-04-28, https://veza.com/company/press-room/series-d-announcement/ ) | high |

---

## 5. SecOps

**Pulse posture (reference):** INVESTIGATE (WATCH) — two public XDR prints healthy; platformization, not a new cycle.

| Vendor | Signal type | Date | Number | Already on site? | Source URL | Excerpt | Confidence |
|---|---|---|---|---|---|---|---|
| CrowdStrike | Earnings | 2026-06-03 | +24% ending ARR; $5.51B (Q1 FY27) | Yes — `print-crwd` / C1 | https://www.sec.gov/Archives/edgar/data/1535527/000153552726000022/crwd-20260603xex991.htm | "Ending ARR $5.51 billion, +24 percent." | high |
| SentinelOne | Earnings | 2026-05-28 | +23% ARR; $1.163B (Q1 FY27) | Yes — `print-s1` / C9 | https://investors.sentinelone.com/press-releases/news-details/2026/SentinelOne-Announces-First-Quarter-Fiscal-Year-2027-Financial-Results/default.aspx | "ARR grew 23% to $1,163 million." | high |
| Cisco Security | Earnings | 2026-08-12 | +2% FY2026 security revenue | Yes — `print-cisco-secops` / C6b | https://investor.cisco.com/news/news-details/2026/CISCO-REPORTS-FOURTH-QUARTER-AND-FISCAL-YEAR-2026-EARNINGS/default.aspx | "Cisco Security revenue… $8.232 billion, +2 percent for FY2026." | high |
| Torq | Funding | 2026-01-12 | $140M Series D; $1.2B valuation; $332M total | No | https://torq.io/news/torq-seriesd/ | "Closed a massive $140 million Series D funding round, propelling its valuation to $1.2 billion and total funding to $332M." | high |
| Tines | Funding | 2025-02-11 | $125M Series C; $1.125B valuation | No | https://www.prnewswire.com/news-releases/tines-secures-125m-in-series-c-financing-bringing-total-valuation-to-1-125b-302372726.html | "$125 million in Series C financing, valuing the company at $1.125 billion… total capital raised… $272 million." | high |
| Palo Alto (Cortex / XSIAM) | Earnings call metric | 2026-06-02 | >$600M XSIAM ARR; +100% YoY; 740 customers | Platform print only — `print-panw`; no XSIAM line | https://investors.paloaltonetworks.com/news-releases/news-release-details/palo-alto-networks-reports-fiscal-third-quarter-2026-financial | Q3 FY26 call: "We ended third quarter with more than $600 million in ARR, representing 100% year-over-year increase across a growing base of 740 customers." | high |

---

## 6. AI Runtime Security

**Pulse posture (reference):** INVESTIGATE (WATCH) — intent strong; bookings/outcomes not; do not run specialist motion from survey intent alone.

| Vendor | Signal type | Date | Number | Already on site? | Source URL | Excerpt | Confidence |
|---|---|---|---|---|---|---|---|
| Zenity | Funding | 2026-08-03 | $125M Series C | No (packet RoS $115M; official says $125M) | https://zenity.io/company-overview/newsroom/company-news/zenity-raises-125-million-to-secure-the-era-of-1-billion-ai-agents | "Announced a $125 million Series C led by Norwest." | high |
| Onyx Security | Funding | 2026-07-29 | $113M Series B; $153M total | Activity — D18; not on prints board | https://www.onyx.security/press-release/onyx-security-raises-113m-series-b-to-control-advanced-ai-quadrupling-revenue-since-stealth-launch-four-months-ago | "$113 million Series B… total funding to $153M… revenue grew fourfold in the four months since leaving stealth." | high |
| Hush Security | Funding | 2026-07-28 | $30M Series A | No (same as Identity row) | https://www.ylventures.com/news/hush-security-raises-30m-to-close-the-ai-agent-governance-gap-with-akamai-joining-as-strategic-investor | "$30 million Series A… total capital raised to $41 million." | high |
| WitnessAI | Funding | 2026-01-13 | $58M strategic round; +500% ARR YoY (company-stated) | No | https://witness.ai/resources/witnessai-raises-58-million-for-global-expansion-and-announces-new-ways-to-secure-ai-agents/ | "Strategic funding of $58 million… over 500% growth in ARR… scaled employee headcount by 5x." | high |
| Lakera | M&A (agreement) | 2025-09-16 | undisclosed | No | https://www.checkpoint.com/press-releases/check-point-acquires-lakera-to-deliver-end-to-end-ai-security-for-enterprises/ | "Entered into an agreement to acquire Lakera… expected to close in Q4 2025." | high |
| Pillar Security | Funding | 2025-04-16 | $9M seed | No | https://www.globenewswire.com/news-release/2025/04/16/3062627/0/en/pillar-security-raises-9m-to-help-enterprises-build-and-run-secure-ai-software.html | "Raised $9 million in Seed funding… led by Shield Capital." | high |

---

## Blanks still open

| Domain | Vendor | Status | What was checked |
|---|---|---|---|
| Cloud Security | Orca Security | **NO-PRINT** | Official Apr 2026 TD SYNNEX distribution PR; no 2025–2026 equity/revenue/M&A dollar disclosure. Last funding Oct 2021. |
| Cloud Security | Aqua Security | **NO-PRINT** | Official Feb 2026 operating-model PR; Nov 2025 leadership PR. No 2025–2026 financial or funding print. Last funding Jan 2024. |
| Cloud Security | Upwind | **Weak official URL** | `$250M` / `$1.5B` confirmed via SecurityWeek (company quotes); `upwind.io/press/*` paths returned 404 on fetch — needs official repost or IR page next cycle. |
| Data / AI | BigID | **Soft revenue claim** | `>$100M revenue` is company-stated in May 2025 PRWeb hire release, not audited ARR series. |
| Identity | Veza | **M&A terms** | ServiceNow intent/close confirmed; purchase price **undisclosed**. Fall back: Series D **$108M** / **$808M** valuation (2025-04-28). |
| AI Runtime | Lakera | **M&A terms** | Check Point agreement announced; price **undisclosed**; close status not re-verified on Check Point IR beyond Q4 2025 expectation. |
| AI Runtime | Zenity | **Resolved (D-36)** | Official **$125M** = RoS **$115M primary + $10M secondary**. Not a conflict. |

**Domain bar shortfall:** Cloud Security has **4 / 6** vendors with qualifying 2025–2026 signals (Wiz, Palo Alto Prisma AIRS adoption, CrowdStrike Falcon Cloud ARR, Upwind). **Orca** and **Aqua** remain open until a public print or qualifying M&A/funding lands.

---

## Research notes

- **Already-on-site?** means present on the live **prints board** (`web/src/data/prints.ts`) or cited Activity evidence (`web/src/data/evidence.ts`). Wiz, Cyera, CyberArk, Onyx appear on Activity/coverage surfaces but not as domain spend prints.
- **Network / SASE** and **Identity** move from packet-only to bench-backed: Cato, Netskope, Oak, Hush, Veza now have pulled URLs.
- **SecOps** SOAR gap partially closed: Torq and Tines have 2025–2026 funding signals; neither on prints board.
- **No `web/` edits.** No scrapers. No invented ARR.

---

## Exit checklist

- [x] File at `docs/archive/2026-08-signals/domain-vendor-signals-2026-08.md`
- [x] Control block; status `operator — lead review pending`
- [x] Six domain tables (36 target vendors attempted)
- [x] Blanks still open list
- [x] Domain postures referenced only; not edited
- [x] No code changes
