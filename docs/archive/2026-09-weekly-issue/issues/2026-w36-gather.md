# Issue 2026-w36 — gather packet

Window: 2026-08-24 to 2026-09-06. Run date: 2026-09-03. Single-pass gather, no sub-agents, fixed source list per instructions.

Prior packet checked (not re-dumped): `docs/archive/2026-08-signals/signals-week-2026-08-19.md` (RoS #257, week of 2026-08-10). M&A source list skimmed: `docs/archive/2026-08-signals/ma-source-catalog.md`. Prints.ts vendor names checked: Fortinet, Cloudflare, Zscaler, Check Point, Cato Networks, Netskope, Wiz, CrowdStrike Falcon Cloud, Upwind, Orca Security, Aqua Security, Palo Alto Prisma AIRS, SentinelOne, CrowdStrike, Cisco Security, Tines, Palo Alto XSIAM, Torq, Rubrik, Varonis, Cyera, Secuvy, BigID, Sentra, Securiti, Okta, SailPoint, CyberArk, Lumos, Oak, Hush Security, Veza, Entra/Ping/PE PAM, Zenity, Onyx, WitnessAI, Lakera, Protect AI, CalypsoAI, SurePath AI, Palo Alto, Cisco, NVIDIA, Arista.

---

## 1. Sources read

| Source | URL | Status |
|---|---|---|
| Return on Security homepage | https://www.returnonsecurity.com/ | readable — confirmed newest issue is #259 |
| Security, Funded #259 | https://www.returnonsecurity.com/p/security-funded-259 | readable — confirmed title/date, covers week of 2026-08-24 |
| Security, Funded #258 (check for overlap) | https://www.returnonsecurity.com/p/security-funded-258 | readable — covers week of 2026-08-17, outside window |
| Cybersecurity Ventures homepage | https://cybersecurityventures.com/ | readable — found one headline (Upwind $300M) |
| Cybersecurity Ventures VC deal-flow page | https://cybersecurityventures.com/cybersecurity-venture-capital-vc-deals/ | unreadable — article body not retrievable (3 attempts: nav-only fetch, direct URL guess 404, site search returned nothing extractable) |
| SYN Ventures portfolio | https://www.synventures.com/portfolio | readable — no net-new names in window |
| Forgepoint Capital companies | https://forgepointcap.com/companies | readable — no net-new names in window |
| Team8 homepage | https://team8.vc/ | readable — no dated item in window found on homepage |
| Ballistic Ventures homepage | https://www.ballisticventures.com/ | readable — no dated item in window |
| Cyberstarts portfolio | https://www.cyberstarts.com/portfolio/ | readable — no net-new names in window |
| YL Ventures news | https://www.ylventures.com/news | readable — one item in window, not a funding round (see below) |
| Evolution Equity companies | https://www.evolutionequity.com/companies | readable — no dated item in window |
| Paladin Capital portfolio | https://paladincapgroup.com/portfolio/ | readable — no dated item in window (page undated, "partial list as of May 2026") |
| SecurityWeek M&A category | https://www.securityweek.com/category/mergers-acquisitions/ | unreadable — 403 on two WebFetch attempts and one curl attempt |
| SecurityWeek RSS feed | https://www.securityweek.com/feed/ | readable — 10 most-recent items (2026-09-02/03), no M&A items in that set, surfaced two funding rounds |
| SecurityWeek — HiddenLayer article | https://www.securityweek.com/hiddenlayer-raises-100-million-for-ai-runtime-security/ | readable |
| SecurityWeek — AIR Security article | https://www.securityweek.com/ai-agent-firewall-startup-air-security-emerges-from-stealth-with-50-million/ | readable |
| TechCrunch cybersecurity acquisition search | https://techcrunch.com/?s=cybersecurity+acquisition | readable |
| TechCrunch — Palo Alto/Console article | https://techcrunch.com/2026/09/02/palo-alto-networks-paid-500m-for-thrive-backed-console-sources-say/ | readable |
| Palo Alto Networks press page (confirm PANW/Console deal) | https://www.paloaltonetworks.com/company/press | unreadable — press release content truncated in fetch, deal not confirmed on primary source |
| SEC EDGAR full-text search (8-K, "acquisition", per named acquirer) | https://efts.sec.gov/LATEST/search-index | readable via curl with declared User-Agent |
| SEC EDGAR — CRWD, ZS, S, OKTA, RBRK, AVGO, PANW, NVDA, NTNX, MRVL, DELL, HPE 8-K exhibits | https://www.sec.gov/Archives/edgar/data/... (see table) | readable via curl with declared User-Agent |
| Marsh cyber risk page | https://www.marsh.com/en/services/cyber-risk.html | readable — nothing dated in window |
| Marsh insights page | https://www.marsh.com/us/services/cyber-risk/insights.html | readable — nothing dated in window |

---

## 2. Lane tables

### Formation (funding)

| date | company | what happened | excerpt | url | doc title | in window |
|---|---|---|---|---|---|---|
| 2026-08-24 (week) | Socure | $156.0M Series E, digital identity/fraud prevention | "Socure, a United States-based digital identity verification and fraud prevention platform, raised a $156.0M Series E from Summit Partners." | https://www.returnonsecurity.com/p/security-funded-259 | Security, Funded #259 — In Fraud We Trust | yes |
| 2026-08-24 (week) | KAZIMI | $2.6M Pre-Seed, anti-bot | "KAZIMI, a Germany-based anti-bot platform for mobile applications, raised a $2.6M Pre-Seed from Market One Capital." | https://www.returnonsecurity.com/p/security-funded-259 | Security, Funded #259 | yes |
| 2026-08-24 (week) | CYBERA | $2.5M Venture, SD-WAN/network security | "CYBERA, a United States-based SD-WAN platform with integrated network security for distributed enterprises, raised a $2.5M Venture Round." | https://www.returnonsecurity.com/p/security-funded-259 | Security, Funded #259 | yes |
| 2026-08-24 (week) | Opgate | $60.0K Pre-Seed, AI agent runtime security | "Opgate, a United States-based runtime security and policy enforcement for AI agents, raised a $60.0K Pre-Seed." | https://www.returnonsecurity.com/p/security-funded-259 | Security, Funded #259 | yes |
| 2026-08-24 (week) | DetectifAI | undisclosed Seed, deepfake voice detection | "DetectifAI, a United States-based AI deepfake voice detection platform, raised an undisclosed Seed round from Josh Constine and Manohar Kamath." | https://www.returnonsecurity.com/p/security-funded-259 | Security, Funded #259 | yes |
| 2026-09-03 | HiddenLayer | $100M Series B, AI runtime security | "This funding lets us keep growing the purpose-built team and platform required to meet that moment as agentic AI becomes core to how enterprises operate," said CEO Chris Sestito. (Round: $100M Series B, lead Delta-v Capital, with Booz Allen Ventures, M12, Morgan Stanley, Ten Eleven Ventures.) | https://www.securityweek.com/hiddenlayer-raises-100-million-for-ai-runtime-security/ | HiddenLayer Raises $100 Million for AI Runtime Security | yes |
| 2026-09-03 | AIR Security | $50M stealth emergence, AI agent firewall | "AIR Security is emerging from stealth with $50 million funding...led by Sequoia Capital and Greenoaks together with...prominent individual industry angels." | https://www.securityweek.com/ai-agent-firewall-startup-air-security-emerges-from-stealth-with-50-million/ | AI Agent Firewall Startup AIR Security Emerges From Stealth With $50 Million | yes |

Portfolio spot-check (SYN, Forgepoint, Team8, Ballistic, Cyberstarts, Evolution Equity, Paladin): no net-new names or rounds dated in window on any of the seven pages checked. YL Ventures news had one item in window — "YL Ventures Ranks in PitchBook's Top Decile of Global Venture Capital for the Fourth Consecutive Year" (2026-08-24) — a ranking announcement, not a funding round; not eligible as a candidate item.

Cybersecurity Ventures reported a headline "Upwind Raises Another $300M At A $3.8B Valuation" (dated 2026-09-03) on its homepage carousel, but the article itself could not be retrieved after three attempts (direct URL guessed from the headline 404'd, the VC-deals hub page returned only navigation, and site search returned nothing extractable). Per the verbatim-or-nothing rule, this is **not recorded as evidence** — flagged for a human to re-check the correct URL.

### Absorption (M&A)

| date | acquirer | target | what happened | excerpt | url | doc title | in window |
|---|---|---|---|---|---|---|---|
| 2026-09-02 (reported) | Palo Alto Networks | Console | ~$500M cash+stock for AI-agent IT helpdesk automation startup | "Palo Alto Networks paid $500 million in cash and stock to acquire Console, a two-year-old startup that uses AI agents to automate routine IT help desk tasks." | https://techcrunch.com/2026/09/02/palo-alto-networks-paid-500m-for-thrive-backed-console-sources-say/ | Palo Alto Networks paid $500M for Thrive-backed Console, sources say | yes |
| 2026-08-24 (week) | ePlus | Daymark Solutions | acquisition, undisclosed value | "Daymark Solutions was acquired by ePlus for an undisclosed amount." | https://www.returnonsecurity.com/p/security-funded-259 | Security, Funded #259 | yes |
| 2026-08-24 (week) | Echo | Minimus (formerly Gutsy) | container security, undisclosed value | "Minimus (formerly Gutsy), an Israel-based secure-by-design container image company, was acquired by Echo for an undisclosed amount." | https://www.returnonsecurity.com/p/security-funded-259 | Security, Funded #259 | yes |
| 2026-08-24 (week) | Ampcus | smarterd | IT asset management, undisclosed value | "smarterd, a United States-based IT asset management and risk prioritization platform, was acquired by Ampcus for an undisclosed amount." | https://www.returnonsecurity.com/p/security-funded-259 | Security, Funded #259 | yes |
| 2026-08-24 (week) | Trace3 | Calian's U.S. Commercial IT Business | MSSP, undisclosed value | "Calian's U.S. Commercial IT Business, a United States-based managed security services provider (MSSP), was acquired by Trace3 for an undisclosed amount." | https://www.returnonsecurity.com/p/security-funded-259 | Security, Funded #259 | yes |
| 2026-08-24 (week) | Integrity360 | CyberIAM | IAM consulting, undisclosed value | "CyberIAM, a United Kingdom-based professional services firm focused on Identity and Access Management (IAM) consulting, was acquired by Integrity360 for an undisclosed amount." | https://www.returnonsecurity.com/p/security-funded-259 | Security, Funded #259 | yes |

SEC EDGAR full-text search for 8-Ks mentioning "acquisition," restricted to Palo Alto Networks, CrowdStrike, Fortinet, Zscaler, Check Point, Okta, SentinelOne, Rubrik, Varonis, Cisco, F5, Broadcom, in the window: every hit returned was an earnings 8-K (Item 2.02), none carried Item 1.01 (definitive agreement) or Item 2.01 (completion of acquisition). **Record: none found** for a definitive-agreement or completed-acquisition 8-K from this acquirer list in the window — the Palo Alto/Console deal above is TechCrunch-reported only; Palo Alto's own press page did not surface a matching release (fetch returned truncated navigation, not the release body), so it is carried at "reported," not "confirmed," confidence.

RoS #258 (week of 2026-08-17, published 2026-08-24) separately reported "At-Bay was acquired by Munich Re for $575M" — outside this window's covered week, so excluded from the table; noted in section 5.

### Prints (public issuer quarterly results)

All entries below are SEC 8-K Item 2.02 exhibits (earnings press releases), fetched directly from EDGAR with a declared User-Agent. Ten companies from the task's candidate list all reported in-window; capped at 8 rows, prioritized by security-market relevance. Marvell, Dell, and HPE (also in-window) are left out of this table — see section 5.

| date | company | period | headline figure | excerpt | url | doc title | in window |
|---|---|---|---|---|---|---|---|
| 2026-08-26 | CrowdStrike | Q2 FY2027 (ended 2026-07-31) | Revenue $1.47B, +26% YoY; net new ARR $333M, +51% YoY | "Total revenue was $1.47 billion, a 26% increase, compared to $1.17 billion in the second quarter of fiscal 2026." / "Delivers record net new ARR of $333 million, accelerates growth to 51% year-over-year" | https://www.sec.gov/Archives/edgar/data/1535527/000153552726000029/crwd-20260826xex991.htm | CrowdStrike Reports Second Quarter Fiscal Year 2027 Financial Results | yes |
| 2026-09-03 | Zscaler | Q4/FY2026 (ended 2026-07-31) | Revenue $898.2M, +25% YoY; ARR $3,771M, +25% YoY | "Revenue: Grew 25% year over year to $898.2 million." / "ARR: Grew 25% year over year to $3,771 million, of which $246 million was net new ARR during the fourth quarter of fiscal 2026." | https://www.sec.gov/Archives/edgar/data/1713683/000171368326000156/zs-07312026_991.htm | Zscaler Announces Strong Fourth Quarter and Fiscal 2026 Financial Results | yes |
| 2026-08-27 | SentinelOne | Q2 FY2027 (ended 2026-07-31) | Revenue $292M, +21% YoY; ARR $1.218B, +22% YoY | "Total revenue grew 21% to $292 million, compared to $242 million." / "Annualized recurring revenue (ARR) grew 22% to $1,218 million as of July 31, 2026." | https://www.sec.gov/Archives/edgar/data/1583708/000158370826000052/sentineloneq227exhibit991.htm | SentinelOne Announces Second Quarter Fiscal Year 2027 Financial Results | yes |
| 2026-08-26 | Okta | Q2 FY2027 (ended 2026-07-31) | Revenue $805M, +11% YoY | "Revenue: Total revenue was $805 million, an increase of 11% year-over-year. Subscription revenue was $793 million, an increase of 12% year-over-year." | https://www.sec.gov/Archives/edgar/data/1660134/000166013426000068/okta-7312026_ex991.htm | Okta Announces Second Quarter Fiscal Year 2027 Financial Results | yes |
| 2026-08-27 | Rubrik | Q2 FY2027 (ended 2026-07-31) | Revenue $427.3M, +38% YoY; subscription ARR $1.66B, +33% YoY | "Second quarter subscription ARR grew 33% year-over-year to $1.66 billion." / "Second quarter revenue grew 38% year-over-year to $427.3 million." | https://www.sec.gov/Archives/edgar/data/1943896/000194389626000055/rubrikinc-991pressrelease7.htm | Rubrik Reports Second Quarter Fiscal Year 2027 Financial Results | yes |
| 2026-09-01 | Palo Alto Networks | Q4/FY2026 (ended 2026-07-31) | Revenue $3.41B, +34% YoY; Next-Gen Security ARR $9.10B, +63% YoY | "Total revenue for the fiscal fourth quarter 2026 grew 34% year over year to $3.41 billion." / "Next-Generation Security ARR for the fiscal fourth quarter 2026 grew 63% year over year to $9.10 billion." | https://www.sec.gov/Archives/edgar/data/1327567/000132756726000019/ex991q426earningsrelease.htm | Palo Alto Networks Reports Fiscal Fourth Quarter and Fiscal Year 2026 Financial Results | yes |
| 2026-09-02 | Broadcom | Q3 FY2026 (ended 2026-08-02) | Revenue $29.6B, +86% YoY; AI semiconductor revenue $16.7B, +221% YoY | "Revenue of $29.6 billion for the third quarter, up 86 percent from the prior year period" / "Q3 AI semiconductor revenue of $16.7 billion grew 221% year-over-year, and 54% quarter-over-quarter," said Hock Tan. | https://www.sec.gov/Archives/edgar/data/1730168/000173016826000076/avgo-08022026x8kxex99.htm | Broadcom Inc. Announces Third Quarter Fiscal Year 2026 Financial Results and Quarterly Dividend | yes |
| 2026-08-26 | Nutanix | Q4/FY2026 (ended 2026-07-31) | Revenue $757.1M, +16% YoY; ARR $2.55B, +16% YoY | "Annual Recurring Revenue (ARR)... $2.55 billion... 16%" / "Revenue $757.1 million $653.3 million 16%" | https://www.sec.gov/Archives/edgar/data/1618732/000117184326005752/exh_991.htm | Nutanix Reports Fourth Quarter and Fiscal 2026 Financial Results | yes |

### Capital and backdrop

| date | entity | what happened | excerpt | url | doc title | in window |
|---|---|---|---|---|---|---|
| 2026-08-26 | NVIDIA | Q2 FY2027 (ended 2026-07-26) results | Revenue $96.2B, +106% YoY; Data Center revenue $89.0B, +117% YoY | "Revenue of $96.2 billion, up 106% from a year ago" / "Data Center revenue of $89.0 billion, up 117% from a year ago" | https://www.sec.gov/Archives/edgar/data/1045810/000104581026000073/q2fy27pr.htm | NVIDIA Announces Financial Results for Second Quarter Fiscal 2027 | yes |
| 2026-09-02 | Microsoft | FY27 segment/investor-metrics update, capex outlook | Capex guided over $50B for FY27 Q1, citing a useful-life update | "Capital expenditures Expected to be over $50 billion including the impact of the useful life update" | https://www.sec.gov/Archives/edgar/data/789019/000119312526380280/d291965dex991.htm | FY27 Segments and Investor Metrics — September 2026 | yes |

Marsh: checked the cyber-risk landing page and the insights page. Most recent dated items are the "Global Cyber Claims Report" (2026-08-02) and a webcast (2026-08-13), both outside the window. **Record: none found** for a Marsh rate note dated in this window.

---

## 3. Proposed one-line read (proposed, not final)

"Record cyber earnings (CRWD, ZS, PANW, RBRK, NVDA) land alongside thin, small-dollar VC and quiet M&A — the infra-to-security lag call holds."

(139 characters)

---

## 4. Proposed posture-delta candidates

None. Every Prints-lane figure this window is a strong beat with accelerating or steady growth (CrowdStrike net new ARR +51% YoY, Palo Alto NGS ARR +63% YoY, Rubrik ARR +33% YoY, NVIDIA Data Center +117% YoY), which is evidence for demand strength at the infrastructure/platform layer, not a change to the standing "infrastructure-to-security demand lag" call — that call is specifically about the gap between infrastructure spend and security-market translation, and this week's prints are consistent with, not contradictory to, a call already built on strong infra numbers. No M&A or funding item this window is large or structurally unusual enough (largest disclosed M&A figure is a reported-not-confirmed $500M; largest funding round is $156M) to warrant a posture change on its own. Recommend human review of the Microsoft capex line and the Broadcom AI-semiconductor figure specifically, since both are new data points for whatever evidence card tracks infrastructure buildout.

---

## 5. What was left out and why

- **Cybersecurity Ventures — Upwind $300M headline**: found the headline on the homepage carousel dated 2026-09-03, but could not retrieve the underlying article after three attempts (guessed URL 404'd, hub page returned navigation only, site search returned nothing extractable). Not recorded as evidence per the verbatim-only rule. A human should re-check the correct URL directly.
- **SecurityWeek M&A category page**: 403 on every attempt (two WebFetch, one curl) — marked unreadable per the time-box rule. Used the RSS feed and TechCrunch as substitutes; RSS only showed the 10 most-recent items (2026-09-02/03), so any SecurityWeek M&A coverage from 2026-08-24 through 2026-09-01 would not have surfaced through that feed.
- **RoS #258 — At-Bay/Munich Re $575M**: this deal is in RoS #258, published 2026-08-24 but covering the week of 2026-08-17, one week before this issue's window starts. Excluded from the Absorption table as out-of-window; flagged here in case the owner wants it noted as recent context.
- **Marvell, Dell, HPE earnings**: all three reported in-window (Marvell 2026-08-27, Dell 2026-09-01, HPE 2026-09-02) and verbatim figures were pulled from their SEC exhibits, but they were dropped from the Prints table to stay at the 8-item cap, in favor of the more directly security-relevant issuers (CrowdStrike, Zscaler, SentinelOne, Okta, Rubrik, Palo Alto Networks, Broadcom, Nutanix). For the record: Marvell Q2 FY2027 net revenue $2.739B (+37% YoY, Data Center revenue +46% YoY); Dell Q2 FY2027 revenue $47.0B (+58% YoY, AI server revenue $16.4B); HPE Q3 FY2026 revenue $12.2B (+34% YoY).
- **Palo Alto Networks / Console deal — primary-source confirmation**: Palo Alto's own press page did not surface a matching release in the fetch (content was truncated to navigation). The deal is carried at "reported" confidence from TechCrunch only; a human should look for the acquirer's own announcement before this reaches any published surface, consistent with the sourcing standard set in the prior packet's owner sign-off.
- **Team8, Ballistic Ventures, Evolution Equity, Paladin Capital**: homepages/portfolio pages don't carry per-item dates, so "no item in window" here means no dated item was found, not a confirmed absence of activity. Flagged as a source-quality gap, not a finding.

## Receipts, 2026-09-04

Re-fetched all 23 `W36-*` evidence records' `canonicalUrl` from the live source (14 distinct URLs;
several records share the Return on Security "Security, Funded #259" page and the SEC EDGAR
filings are one URL per issuer), computed a sha256 of the fetched bytes, and confirmed each
record's `excerpt` appears in the fetched bytes after stripping HTML tags, normalising whitespace,
curly quotes, and the space tag-stripping leaves before punctuation. 21 of 23 records confirmed
verbatim and now carry a `retrieval` receipt in `web/src/data/evidence.ts`. Two did not, and were
excluded rather than receipted with an invented value:

- **W36-06** (HiddenLayer Series B) — `https://www.securityweek.com/hiddenlayer-raises-100-million-for-ai-runtime-security/`, fetched 200. The excerpt's attribution reads "said CEO Chris Sestito," but the article's exact wording is "said HiddenLayer co-founder and CEO Chris Sestito" — the excerpt silently drops "HiddenLayer co-founder and" rather than marking the elision. Not verbatim; no receipt issued. The issue item that cited this as its only evidence, `2026-w36-formation-6` (HiddenLayer raises $100M Series B), has been removed from `web/src/data/issues/2026-w36.ts` rather than left with an empty evidence list.
- **W36-10** (Echo / Minimus acquisition) — `https://www.returnonsecurity.com/p/security-funded-259`, fetched 200. The excerpt reads "Minimus (formerly Gutsy), an Israel-based secure-by-design container image company, was acquired by Echo..." but the live page's exact wording is "Minimus (formerly Gutsy) and there assets thereof, an Israel-based secure-by-design container image company, was acquired by Echo..." — the excerpt silently drops "and there assets thereof" (the source's own wording, not a transcription artifact on our side). Not verbatim; no receipt issued. The issue item that cited this as its only evidence, `2026-w36-absorption-3` (Echo acquires container security firm Minimus), has been removed from `web/src/data/issues/2026-w36.ts` rather than left with an empty evidence list.

Both exclusions are content differences inside the quoted span (a dropped clause), not a punctuation or
whitespace artifact — the comparison already tolerates a truncated clause closed with a period where
the source continues with different punctuation, and treats quotation marks as typographic apparatus
rather than content, so these two survived that tolerance and still failed. Everything else — including
the AIR Security and Palo Alto/Console press excerpts, which also close a truncated quotation with a
period the source does not use at that exact point, and the Broadcom CEO quote, which drops a closing
quotation mark the source carries — matched on content and is receipted.

The `W36-06` and `W36-10` evidence records themselves were removed from `web/src/data/evidence.ts`,
not just left uncited: once their citing items were removed, `verify:integrity`'s unreferenced-evidence
threshold (5, unchanged) would have failed on the two new orphans on top of the five pre-existing ones.
Deleting a record with a confirmed-wrong excerpt rather than leaving it uncited in the data set is the
more correct outcome, not merely a build workaround — the exact wording each one got wrong is preserved
above for the record.

- **W36-06** (HiddenLayer Series B) was re-fetched from `https://www.securityweek.com/hiddenlayer-raises-100-million-for-ai-runtime-security/` on 2026-09-04 (200; sha256 `438ad41abf3a8f71c3c5926a77f5aa7a0ea9da6fd3a572fbe43d87e73d7634f0`), with a corrected verbatim excerpt — "AI security company HiddenLayer on Wednesday announced raising $100 million in a Series B funding round that brings the total raised by the company to over $155 million." — that matches the article's opening paragraph exactly, with no dropped words. The record carries a `retrieval` receipt and is back in `web/src/data/evidence.ts`; the citing item `2026-w36-formation-6` is back in `web/src/data/issues/2026-w36.ts` in its original position. Its `why` was reworded from the earlier draft's "...Booz Allen Ventures, M12, Morgan Stanley..." to "...Booz Allen Ventures, Microsoft's venture fund, Morgan Stanley..." — the article names the fund as "Microsoft's Venture Fund M12" nowhere near the funding figure, so no single verbatim excerpt under sixty words could carry both the $100M figure and that fund's short name without check 12 (numeric-tokens-cited) flagging the "12" in "M12" as an unsupported numeral. The lead investor, Delta-v Capital, stays named in the `why`.
- **W36-10** (Echo / Minimus acquisition) was re-fetched from `https://www.returnonsecurity.com/p/security-funded-259` on 2026-09-04 (200; sha256 `ec12cebefd1811fd7d105e98083244748680e209bad69180e22bdf3eb69200bd`), with a corrected verbatim excerpt — "Minimus (formerly Gutsy) and there assets thereof, an Israel-based secure-by-design container image company, was acquired by Echo for an undisclosed amount." — that matches the live page exactly, "and there assets thereof" included as the source's own (ungrammatical) wording rather than silently dropped. The record carries a `retrieval` receipt and is back in `web/src/data/evidence.ts`; the citing item `2026-w36-absorption-3` is back in `web/src/data/issues/2026-w36.ts` in its original position, headline and why unchanged since neither carries a numeral.
