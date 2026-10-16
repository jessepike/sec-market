# Coverage research — Group 2: Network/SASE, Cloud security, Identity, Email security

Prepared for Security Market Pulse. Retrieval date for every sourced fact below is 2026-09-25 unless noted otherwise. Sourcing follows the ladder in `docs/archive/2026-09-weekly-issue/fable-run/research/11-distress-signal-sources.md`: rung 1 is a company's own SEC filing, rung 2 is the company's own press release/IR page, rung 3 is a rating-agency action republished by the company or a wire service, rung 4 is a state WARN notice, rung 5 is trade press or other secondary reporting — always labelled "secondary" and never stated as if company-confirmed. Anything marked "not found," "none found," or "unverified" was searched for and not located, not assumed absent. Where a research pass could not reach a primary source (search-tool budget limits, blocked fetches to moodys.com/spglobal.com, etc.) that is noted inline rather than silently smoothed over.

`existingId` fields reuse the ids already in `web/src/data/prints.ts` where the supplier is already tracked there.

---

## Domain 1: Network security and SASE / SSE

| Supplier | Public/Private | Latest footing figure (period) | Last round or ownership | Distress items |
|---|---|---|---|---|
| Zscaler | Public (ZS) | Revenue $898.2M, +25% YoY; ARR $3,771M, +25% YoY (Q4 FY2026, ended 7/31/26) | Independent, public since 2018 | Restructuring charge $5.5M in Q4 / $10.3M full FY26 (rung 1); secondary trade press separately reports a ~3% workforce reduction (~261 people, ~$30-33M) announced the same day as earnings (rung 5, unverified against a primary headcount disclosure); CRO transition, not CEO/CFO |
| Palo Alto Networks — Prisma SASE (product line inside PANW) | Public (PANW) | Total company revenue $3.41B, +34% YoY; Next-Gen Security ARR $9.10B, +63% YoY (Q4 FY2026) — SASE not broken out separately | Independent; closed $25B CyberArk acquisition Feb 11, 2026 | Assumed CyberArk's convertible notes as part of the acquisition (not distress, rung 1); secondary trade press reports ~500 CyberArk positions cut post-close (rung 5, unverified against a primary PANW disclosure) |
| Fortinet | Public (FTNT) | Revenue $2.05B, +26% YoY; billings $2.37B, +33% YoY (Q2 2026) | Independent; FortiSASE is a product line, not a separate entity | None found in any primary source. Moody's upgraded senior notes to A3 in July 2026 (positive, rung 3, not independently confirmed against Moody's own release). $500M notes matured and were repaid in cash, not refinanced |
| Cloudflare | Public (NET) | Revenue $696.1M, +36% YoY (Q2 2026) | Independent; Cloudflare One is the SASE line | Confirmed restructuring: $150.7M charge, ~1,100 employees, tied to an "agentic AI-first" operating-model shift, announced May 2026 (rung 1); $2.5B convertible notes issued August 2026 (rung 1); Chief Legal Officer transition (not CEO/CFO) |
| Netskope | Public (NTSK), IPO'd Sept 18, 2025 | Revenue $220.5M, +29% YoY; ARR $899M, +27% YoY (Q2 FY2027, ended 7/31/26) | Independent since IPO; raised ~$992M net, implied $7.3B valuation | CFO Drew Del Matto disclosed plan to retire (successor search underway), June 2026 (rung 1); $3.5M restructuring cost in latest quarter (rung 1) |
| Cato Networks | Private | Company-stated ARR >$350M for FY2025, +43% YoY (rung 2, primary release); $415M as of mid-2026, +42% YoY (rung 5, secondary trade press, not independently confirmed) | Venture-backed; Series G, ~$409M total (incl. extension) at >$4.8B valuation, led by Vitruvian Partners and ION Crossover Partners, closed June–Sept 2025 | None found. Company explicitly denied layoffs (Oct 2025, secondary); cancelled a planned Tel Aviv office expansion for a smaller lease instead (secondary, company says not financially driven) |
| Check Point — Harmony SASE (built on the acquired Perimeter 81) | Public (CHKP), Israeli foreign private issuer | Total revenue $674M, +1% YoY; Security Subscriptions revenue $333M, +12% YoY (Q2 2026) | Independent; Harmony SASE traces to the Perimeter 81 acquisition (~2023, not re-confirmed this pass) | $2B convertible notes issued in Q2 2026 (rung 1); large sales/GTM reorganization affecting roughly a third of employees, moved up from 2027 to 2026, drove a 14% product-revenue decline (rung 1/5 mixed); CRO change (Seddik in, Greenberg out) May 2026 (rung 1) |

```json
[
  {
    "supplier": "Zscaler",
    "existingId": "print-zscaler",
    "legalName": "Zscaler, Inc.",
    "publicPrivate": "public",
    "ticker": "ZS",
    "cik": "0001713683",
    "filerType": "domestic 10-K/10-Q filer",
    "fiscalYearEnd": "July 31",
    "irUrl": "https://ir.zscaler.com",
    "ownership": {
      "status": "independent",
      "details": "Independent public company since its 2018 IPO. No PE ownership or acquisition history."
    },
    "footing": {
      "latestQuarter": {
        "period": "Q4 FY2026, ended 2026-07-31",
        "releaseDate": "2026-09-03",
        "revenue": "$898.2 million",
        "revenueYoY": "25%",
        "fullYearRevenue": "$3,352.5 million (FY2026)",
        "headlineMetric": "ARR",
        "headlineMetricValue": "$3,771 million",
        "headlineMetricYoY": "25% (20% excluding $141M ARR added by the Red Canary acquisition)",
        "source": "https://www.sec.gov/Archives/edgar/data/1713683/000171368326000156/zs-07312026_991.htm",
        "retrievedDate": "2026-09-25"
      },
      "priorQuarter": {
        "period": "Q3 FY2026, ended 2026-04-30",
        "releaseDate": "2026-05-26",
        "revenue": "$850.5 million",
        "revenueYoY": "25%",
        "headlineMetricValue": "$3,525 million ARR",
        "headlineMetricYoY": "25% (21% excluding Red Canary)",
        "source": "https://www.sec.gov/Archives/edgar/data/1713683/000171368326000095/zs-04302026_991.htm",
        "retrievedDate": "2026-09-25"
      },
      "nextEarningsDate": "not found — not disclosed in the release",
      "guidance": {
        "fy2027_revenue": "$3.908-$3.938 billion",
        "fy2027_arr": "$4.396-$4.426 billion",
        "source": "https://www.sec.gov/Archives/edgar/data/1713683/000171368326000156/zs-07312026_991.htm",
        "retrievedDate": "2026-09-25"
      }
    },
    "distress": [
      {"category": "layoffs", "finding": "No confirmed headcount figure in a primary source. Trade press (secondary) reports a roughly 3% global headcount reduction (~261 employees) announced 2026-09-03, same day as Q4 earnings, with an estimated $30-33 million total cost landing mostly in H1 FY2027.", "date": "2026-09-03", "source": "https://www.bankinfosecurity.com/zscaler-to-lay-off-3-staff-as-shifts-spend-to-sales-a-32746 (secondary)", "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "restructuring charges", "finding": "Restructuring and other charges of $5.5 million in Q4 FY2026 and $10.3 million for full FY2026, described as severance/termination benefits, disclosed in the earnings release's non-GAAP reconciliation.", "date": "2026-09-03", "source": "https://www.sec.gov/Archives/edgar/data/1713683/000171368326000156/zs-07312026_991.htm", "ladderRung": 1, "retrievedDate": "2026-09-25"},
      {"category": "debt raised or refinanced", "finding": "none found in the 12-month window", "date": null, "source": null, "ladderRung": null, "retrievedDate": "2026-09-25"},
      {"category": "credit ratings actions", "finding": "not found", "date": null, "source": null, "ladderRung": null, "retrievedDate": "2026-09-25"},
      {"category": "going-concern language", "finding": "none found", "date": null, "source": null, "ladderRung": null, "retrievedDate": "2026-09-25"},
      {"category": "CEO or CFO departures", "finding": "none found for CEO/CFO. CRO Mike Rich stepping down effective 2026-10-01, succeeded by Ross Tackett. EVP Raj Judge resigned board seat effective 2026-04-16, employment ended 2026-07-31.", "date": "2026-09-24", "source": "https://www.sec.gov/Archives/edgar/data/1713683/000171368326000193/zs-20260924.htm", "ladderRung": 1, "retrievedDate": "2026-09-25"},
      {"category": "divestitures", "finding": "none found", "date": null, "source": null, "ladderRung": null, "retrievedDate": "2026-09-25"},
      {"category": "shutdown", "finding": "none found", "date": null, "source": null, "ladderRung": null, "retrievedDate": "2026-09-25"}
    ]
  },
  {
    "supplier": "Palo Alto Networks (Prisma SASE)",
    "legalName": "Palo Alto Networks, Inc.",
    "publicPrivate": "public",
    "ticker": "PANW",
    "cik": "0001327567",
    "filerType": "domestic 10-K/10-Q filer",
    "fiscalYearEnd": "July 31",
    "irUrl": "https://investors.paloaltonetworks.com",
    "ownership": {
      "status": "segment",
      "details": "Prisma SASE (Prisma Access, Prisma SD-WAN) is a product line inside Palo Alto Networks, not a separately reported financial segment. PANW itself is independent and public. Closed its acquisition of CyberArk on 2026-02-11 (reported ~$25B) and also acquired Chronosphere in the same period; both are consolidated into the company's Next-Generation Security (NGS) ARR, which blends SASE with cloud and AI security rather than breaking SASE out on its own."
    },
    "footing": {
      "latestQuarter": {
        "period": "Q4 FY2026, ended 2026-07-31",
        "releaseDate": "2026-09-01",
        "revenue": "$3.41 billion",
        "revenueYoY": "34%",
        "fullYearRevenue": "$11.48-11.5 billion (FY2026), +24% YoY",
        "headlineMetric": "Next-Generation Security (NGS) ARR",
        "headlineMetricValue": "$9.10 billion",
        "headlineMetricYoY": "63%",
        "source": "https://www.sec.gov/Archives/edgar/data/1327567/000132756726000019/ex991q426earningsrelease.htm",
        "retrievedDate": "2026-09-25"
      },
      "priorQuarter": {
        "period": "Q3 FY2026, ended 2026-04-30",
        "releaseDate": "2026-06-02",
        "revenue": "$3.0 billion (includes $388 million from CyberArk and Chronosphere)",
        "revenueYoY": "31%",
        "headlineMetricValue": "$8.1 billion NGS ARR (includes $1.6 billion from CyberArk and Chronosphere)",
        "headlineMetricYoY": "60%",
        "source": "https://www.sec.gov/Archives/edgar/data/1327567/000132756726000012/ex991q326earningsrelease.htm",
        "retrievedDate": "2026-09-25",
        "note": "31%/34% growth is elevated vs. PANW's historical mid-teens pace, largely reflecting CyberArk/Chronosphere consolidation; the release does not separate organic from acquired growth."
      },
      "nextEarningsDate": "~2026-11-12 (fiscal Q1 2027) — secondary aggregator estimate, not confirmed on PANW's own IR page",
      "guidance": {
        "fy2027_revenue": "$14.1-14.2 billion",
        "fy2027_ngsArr": "$11.075-11.175 billion",
        "source": "https://www.sec.gov/Archives/edgar/data/1327567/000132756726000019/ex991q426earningsrelease.htm",
        "retrievedDate": "2026-09-25"
      }
    },
    "distress": [
      {"category": "layoffs", "finding": "Secondary trade press reports roughly 500 CyberArk positions cut (over 10% of CyberArk's workforce, ~100 in Israel) the day after close. No PANW press release, SEC filing, or WARN notice confirms a specific figure.", "date": "2026-02-11 to 2026-02-12", "source": "https://www.calcalistech.com/ctechnews/article/hy707511ube (secondary)", "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "restructuring charges", "finding": "none found — no Item 2.05 8-K identified in the 12-month filing window", "date": null, "source": null, "ladderRung": 1, "retrievedDate": "2026-09-25"},
      {"category": "debt raised or refinanced", "finding": "PANW assumed CyberArk's 0.00% Convertible Senior Notes due 2030 and related capped-call transactions as part of closing. Balance sheet as of 2026-04-30 carried $160M short-term and $1,192M long-term convertible notes from this assumption — acquisition-related, not distress-driven refinancing.", "date": "2026-02-11 (First Supplemental Indenture); 2026-03-23 (settlement method notice)", "source": "https://www.sec.gov/Archives/edgar/data/0001327567/000132756726000015/panw-20260430.htm ; https://www.sec.gov/Archives/edgar/data/1327567/000119312526151637/d49517d8k.htm", "ladderRung": 1, "retrievedDate": "2026-09-25"},
      {"category": "credit ratings actions", "finding": "not found — primary ratings-agency sites not directly reachable this pass; treat as not found, not confirmed absence", "date": null, "source": null, "ladderRung": null, "retrievedDate": "2026-09-25"},
      {"category": "going-concern language", "finding": "none found", "date": null, "source": null, "ladderRung": null, "retrievedDate": "2026-09-25"},
      {"category": "CEO or CFO departures", "finding": "none found. 8-K filed 2026-08-21 (Items 5.02/5.03) established a new executive severance/change-in-control policy naming CEO Nikesh Arora, CFO Dipak Golechha, President BJ Jenkins, and CPTO Lee Klarich as continuing participants — no departure. (Founder/CTO Nir Zuk resigned as CTO effective 2025-08-14, before the 12-month window; not CEO/CFO.)", "date": "2026-08-21", "source": "https://www.sec.gov/Archives/edgar/data/1327567/000119312526361122/d180372d8k.htm", "ladderRung": 1, "retrievedDate": "2026-09-25"},
      {"category": "divestitures", "finding": "none found; all identified M&A activity in the window was acquisitive (CyberArk, Chronosphere)", "date": null, "source": "https://www.paloaltonetworks.com/company/press/2026/palo-alto-networks-completes-acquisition-of-cyberark-to-secure-the-ai-era", "ladderRung": 2, "retrievedDate": "2026-09-25"},
      {"category": "shutdown", "finding": "none found; not applicable at this scale", "date": null, "source": null, "ladderRung": null, "retrievedDate": "2026-09-25"}
    ]
  },
  {
    "supplier": "Fortinet",
    "existingId": "print-fortinet",
    "legalName": "Fortinet, Inc.",
    "publicPrivate": "public",
    "ticker": "FTNT",
    "cik": "0001262039",
    "filerType": "domestic 10-K/10-Q filer",
    "fiscalYearEnd": "December 31",
    "irUrl": "https://investor.fortinet.com",
    "ownership": {
      "status": "independent",
      "details": "Independent public company. FortiSASE / Unified SASE is a native product line, not a separately acquired or reported unit."
    },
    "footing": {
      "latestQuarter": {
        "period": "Q2 2026, ended 2026-06-30",
        "releaseDate": "2026-07-29",
        "revenue": "$2.05 billion",
        "revenueYoY": "26%",
        "productRevenue": "$773 million, +52% YoY",
        "headlineMetric": "Billings",
        "headlineMetricValue": "$2.37 billion",
        "headlineMetricYoY": "33%",
        "sasePlatformFigure": "Earnings-call commentary described the \"SASE firewall combined business\" growing 34% to over $2 billion, Unified SASE billings up 35%, FortiSASE billings up over 100% — no single dollar-figure SASE ARR was found in the press release itself; treat as not found for a discrete SASE ARR number.",
        "source": "https://investor.fortinet.com/news-releases/news-release-details/fortinet-reports-strong-second-quarter-2026-financial-results ; https://www.sec.gov/Archives/edgar/data/0001262039/000126203926000018/ftntq2-2026ex991.htm",
        "retrievedDate": "2026-09-25"
      },
      "priorQuarter": {
        "period": "Q1 2026, ended 2026-03-31",
        "releaseDate": "2026-05-06",
        "revenue": "$1.85 billion",
        "revenueYoY": "20%",
        "headlineMetricValue": "$2.09 billion billings",
        "headlineMetricYoY": "31%",
        "source": "https://www.sec.gov/Archives/edgar/data/0001262039/000126203926000010/ftntq1-2026ex991.htm",
        "retrievedDate": "2026-09-25"
      },
      "nextEarningsDate": "not found — no official date located; analyst estimates cluster late Oct–early Nov 2026 (unverified)",
      "guidance": {"q3_2026_revenue": "$2.010-$2.100 billion", "q3_2026_billings": "$2.250-$2.350 billion", "fy2026_revenue": "raised to $8.02-8.18 billion", "source": "https://www.sec.gov/Archives/edgar/data/0001262039/000126203926000018/ftntq2-2026ex991.htm", "retrievedDate": "2026-09-25"}
    },
    "distress": [
      {"category": "layoffs", "finding": "No company confirmation, WARN filing, or credible secondary corroboration found. Employee-forum posts allege ongoing/quarterly layoffs, including one unconfirmed claim of over 50% support-team cuts — unverified rumor, not a confirmed finding.", "date": null, "source": "https://www.thelayoff.com/fortinet (unverified forum chatter)", "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "restructuring charges", "finding": "none found — reviewed 8-Ks in the window; no Item 2.05 restructuring filing identified", "date": null, "source": null, "ladderRung": 1, "retrievedDate": "2026-09-25"},
      {"category": "debt raised or refinanced", "finding": "$500 million 1.000% senior notes matured 2026-03-15 and were repaid in cash from Fortinet's ~$3.9B cash/investments balance rather than refinanced — a scheduled repayment, not new debt.", "date": "2026-03-15", "source": "Fortinet 2025 10-K disclosure, referenced in earnings materials", "ladderRung": 1, "retrievedDate": "2026-09-25"},
      {"category": "credit ratings actions", "finding": "Moody's upgraded senior unsecured notes to A3 from Baa1 on 2026-07-29, coinciding with Q2 earnings — a positive action, not independently verified against Moody's own release (secondary republication).", "date": "2026-07-29", "source": "https://www.investing.com/news/stock-market-news/moodys-upgrades-fortinet-rating-to-a3-on-strong-execution-93CH-4801543 (secondary)", "ladderRung": 3, "retrievedDate": "2026-09-25"},
      {"category": "going-concern language", "finding": "none found; balance sheet strength ($3.3-3.9B cash/investments vs. ~$500M now-repaid debt) inconsistent with going-concern risk", "date": null, "source": null, "ladderRung": null, "retrievedDate": "2026-09-25"},
      {"category": "CEO or CFO departures", "finding": "none found within the 12-month window. Prior CFO's retirement (announced Feb 2025) predates the window; current CFO Christiane Ohlgart in role since May 2025.", "date": null, "source": "https://www.sec.gov/Archives/edgar/data/1262039/000126203925000007/ftnt-20250204.htm (context only, out of window)", "ladderRung": 1, "retrievedDate": "2026-09-25"},
      {"category": "divestitures", "finding": "none found", "date": null, "source": null, "ladderRung": null, "retrievedDate": "2026-09-25"},
      {"category": "shutdown", "finding": "none found", "date": null, "source": null, "ladderRung": null, "retrievedDate": "2026-09-25"}
    ]
  },
  {
    "supplier": "Cloudflare",
    "existingId": "print-cloudflare",
    "legalName": "Cloudflare, Inc.",
    "publicPrivate": "public",
    "ticker": "NET",
    "cik": "0001477333",
    "filerType": "domestic 10-K/10-Q filer",
    "fiscalYearEnd": "December 31",
    "irUrl": "https://cloudflare.net",
    "ownership": {
      "status": "independent",
      "details": "Independent public company since its September 2019 IPO. Cloudflare One is the SASE/SSE product line, one part of a broader platform; not broken out as its own reporting segment."
    },
    "footing": {
      "latestQuarter": {
        "period": "Q2 2026, ended 2026-06-30",
        "releaseDate": "2026-08-06",
        "revenue": "$696.1 million",
        "revenueYoY": "36%",
        "currentRpoGrowth": "35% YoY",
        "source": "https://www.sec.gov/Archives/edgar/data/1477333/000147733326000053/q226exhibit991.htm",
        "retrievedDate": "2026-09-25"
      },
      "priorQuarter": {
        "period": "Q1 2026, ended 2026-03-31",
        "releaseDate": "2026-05-07",
        "revenue": "$639.8 million",
        "revenueYoY": "34%",
        "source": "https://www.sec.gov/Archives/edgar/data/1477333/000147733326000035/q126exhibit991.htm",
        "retrievedDate": "2026-09-25"
      },
      "h1_2026SixMonthRevenue": "$1.335 billion, +35% YoY",
      "nextEarningsDate": "not found — not disclosed in the release",
      "guidance": {"q3_2026_revenue": "$736.0-$737.0 million", "source": "https://www.sec.gov/Archives/edgar/data/1477333/000147733326000053/q226exhibit991.htm", "retrievedDate": "2026-09-25"}
    },
    "distress": [
      {"category": "layoffs", "finding": "Approximately 1,100 employees affected as part of a restructuring tied to a shift to an \"agentic AI-first operating model,\" announced alongside Q1 2026 earnings.", "date": "2026-05-07", "source": "https://www.sec.gov/Archives/edgar/data/1477333/000147733326000035/q126exhibit991.htm", "ladderRung": 1, "retrievedDate": "2026-09-25"},
      {"category": "restructuring charges", "finding": "Item 2.05 8-K: total restructuring charge guided at $140.0-150.0 million ($105.0-110.0M cash, $35.0-40.0M non-cash); Q2 2026 release recognized $150.7 million as the majority of the charge, completion expected end of Q3 2026.", "date": "2026-05-07 (guidance); 2026-08-06 (Q2 recognition)", "source": "https://www.sec.gov/Archives/edgar/data/1477333/000147733326000035/q126exhibit991.htm ; https://www.sec.gov/Archives/edgar/data/1477333/000147733326000053/q226exhibit991.htm", "ladderRung": 1, "retrievedDate": "2026-09-25"},
      {"category": "debt raised or refinanced", "finding": "$2.5 billion aggregate principal of 0% Convertible Senior Notes due 2031 issued, ~$2,462.3 million net proceeds; capped call transactions costing $259.5 million entered alongside.", "date": "2026-08-13", "source": "https://www.sec.gov/Archives/edgar/data/1477333/000095010326012340/dp251721_8k.htm", "ladderRung": 1, "retrievedDate": "2026-09-25"},
      {"category": "credit ratings actions", "finding": "none found", "date": null, "source": null, "ladderRung": null, "retrievedDate": "2026-09-25"},
      {"category": "going-concern language", "finding": "none found", "date": null, "source": null, "ladderRung": null, "retrievedDate": "2026-09-25"},
      {"category": "CEO or CFO departures", "finding": "none found for CEO/CFO. Chief Legal Officer Doug Kramer resigned effective 2026-03-31 (to Senior Advisor), succeeded by Alissa Starzak. Two additional Item 5.02 8-Ks filed 2026-06-30 and 2026-07-01 — specific content not retrieved this pass; flagged unverified rather than assumed harmless.", "date": "2026-02-06", "source": "https://www.sec.gov/Archives/edgar/data/1477333/000147733326000009/cloud-20260206.htm", "ladderRung": 1, "retrievedDate": "2026-09-25"},
      {"category": "divestitures", "finding": "none found", "date": null, "source": null, "ladderRung": null, "retrievedDate": "2026-09-25"},
      {"category": "shutdown", "finding": "none found", "date": null, "source": null, "ladderRung": null, "retrievedDate": "2026-09-25"}
    ]
  },
  {
    "supplier": "Netskope",
    "existingId": "print-netskope",
    "legalName": "Netskope, Inc.",
    "publicPrivate": "public",
    "ticker": "NTSK",
    "cik": "0002063196",
    "filerType": "domestic 10-K/10-Q filer (newly public; first 10-K filed 2026-03-31)",
    "fiscalYearEnd": "January 31",
    "irUrl": "https://investors.netskope.com",
    "ownership": {
      "status": "independent",
      "details": "IPO'd on Nasdaq 2025-09-18: 47.8 million Class A shares at $19.00, implying $7.3B valuation; closed 2025-09-22 with full over-allotment exercise, net proceeds ~$992.2 million. Previously venture-backed private, prior to the 12-month research window."
    },
    "footing": {
      "latestQuarter": {
        "period": "Q2 FY2027, ended 2026-07-31",
        "releaseDate": "2026-09-02",
        "revenue": "$220.5 million",
        "revenueYoY": "29%",
        "headlineMetric": "ARR",
        "headlineMetricValue": "$899 million",
        "headlineMetricYoY": "27%",
        "grossMargin": "GAAP 74% (vs 72% prior-year period); non-GAAP 77% (vs 75%)",
        "source": "https://www.sec.gov/Archives/edgar/data/2063196/000119312526380188/ntsk-ex99_1.htm",
        "retrievedDate": "2026-09-25"
      },
      "priorQuarter": {
        "period": "Q1 FY2027, ended 2026-04-30",
        "releaseDate": "2026-06-03",
        "revenue": "$201.6 million",
        "revenueYoY": "28%",
        "headlineMetricValue": "$845 million ARR",
        "headlineMetricYoY": "29%",
        "source": "https://www.sec.gov/Archives/edgar/data/2063196/000119312526255439/ck0002063196-ex99_1.htm",
        "retrievedDate": "2026-09-25"
      },
      "cashPosition": "$1.1 billion in cash and securities as of latest quarter",
      "nextEarningsDate": "~2026-12-11 for Q3 FY2027 — secondary/aggregator estimate, not company-confirmed"
    },
    "distress": [
      {"category": "layoffs", "finding": "No SEC filing, press release, or confirmed WARN notice found. Forum posts reference repeated layoff rounds, including one unconfirmed claim of ~200 Engineering roles cut, with no confirmed dates in-window and no primary-source confirmation.", "date": "not found", "source": "unverified forum chatter", "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "restructuring charges", "finding": "$3.5 million in restructuring costs recognized in the quarter ended 2026-07-31.", "date": "2026-09-02", "source": "https://www.sec.gov/Archives/edgar/data/2063196/000119312526380188/ntsk-ex99_1.htm", "ladderRung": 1, "retrievedDate": "2026-09-25"},
      {"category": "debt raised or refinanced", "finding": "No new debt raise/refinancing. An 2025-09-23 8-K disclosed a contractual notice that the IPO constituted a \"Qualified Initial Public Offering\" under pre-IPO note indentures — administrative, not a new issuance.", "date": "2025-09-23", "source": "https://www.sec.gov/Archives/edgar/data/2063196/000119312525213627/0001193125-25-213627-index.htm", "ladderRung": 1, "retrievedDate": "2026-09-25"},
      {"category": "credit ratings actions", "finding": "none found; company too newly public to have an identified rated debt instrument", "date": null, "source": null, "ladderRung": null, "retrievedDate": "2026-09-25"},
      {"category": "going-concern language", "finding": "none found", "date": null, "source": null, "ladderRung": null, "retrievedDate": "2026-09-25"},
      {"category": "CEO or CFO departures", "finding": "CFO Drew Del Matto disclosed intention to retire after 40 years; remains CFO while a successor is sought, then transitions to advisory.", "date": "2026-06-03", "source": "https://www.sec.gov/Archives/edgar/data/2063196/000119312526255439/ck0002063196-20260603.htm", "ladderRung": 1, "retrievedDate": "2026-09-25"},
      {"category": "divestitures", "finding": "none found", "date": null, "source": null, "ladderRung": null, "retrievedDate": "2026-09-25"},
      {"category": "shutdown", "finding": "none found", "date": null, "source": null, "ladderRung": null, "retrievedDate": "2026-09-25"}
    ]
  },
  {
    "supplier": "Cato Networks",
    "existingId": "print-cato",
    "legalName": "Cato Networks Ltd.",
    "publicPrivate": "private",
    "ticker": null,
    "cik": null,
    "filerType": "not an SEC filer",
    "fiscalYearEnd": "unknown",
    "irUrl": "https://www.catonetworks.com/news/",
    "ownership": {
      "status": "independent (venture-backed)",
      "details": "No SEC filings; no CIK. Total funding raised exceeds $1 billion. Series G totaled roughly $409 million: a $359 million initial close (announced 2025-06-30) led by Vitruvian Partners and ION Crossover Partners, with Lightspeed Venture Partners, Acrew Capital, and Adams Street Partners also participating, at a valuation over $4.8 billion (up from $3 billion in a September 2023 round) — about a third of the new money (~$120M) was a secondary employee sale. A ~$50 million extension closed around 2025-09-04. Company leadership reaffirmed IPO intent in a July 2026 interview and the CEO denied acquisition rumors; no S-1/F-1 filed."
    },
    "footing": {
      "lastFundingRound": {
        "stage": "Series G (with extension)",
        "amount": "$359 million initial close + ~$50 million extension = ~$409 million total",
        "leadInvestor": "Vitruvian Partners and ION Crossover Partners",
        "otherInvestors": "Lightspeed Venture Partners, Acrew Capital, Adams Street Partners",
        "valuation": "more than $4.8 billion",
        "date": "2025-06-30 (initial close); ~2025-09-04 (extension)",
        "source": "https://www.prnewswire.com/news-releases/cato-networks-raises-359-million-at-a-valuation-of-more-than-4-8-billion-302494283.html",
        "retrievedDate": "2026-09-25"
      },
      "statedArrOrRevenue": [
        {"figure": "ARR surpassed $350 million, +43% YoY, for full year 2025; more than 4,000 enterprise customers", "date": "reported 2026-02-24", "source": "https://www.prnewswire.com/il/news-releases/cato-networks-surpasses-350-million-arr-with-43-yoy-growth-in-2025-302694952.html", "ladderRung": 2, "retrievedDate": "2026-09-25"},
        {"figure": "ARR exceeded $415 million, +42% YoY", "date": "reported 2026-07-27", "source": "https://www.calcalistech.com/ctechnews/article/b1bqq6nrfg (secondary, not independently confirmed against a primary Cato release)", "ladderRung": 5, "retrievedDate": "2026-09-25"}
      ]
    },
    "distress": [
      {"category": "layoffs", "finding": "none found. Company stated (secondary reporting, ~Oct 2025) it was \"not laying off employees or freezing recruitment\" and had 250+ open positions. Headcount ~1,800 (about half in Israel) as of Sept 2025.", "date": "2025-10", "source": "secondary aggregator coverage", "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "restructuring charges", "finding": "No formal restructuring found. Secondary trade press (2026-07-27) reported Cato cancelled a planned Tel Aviv office expansion for an additional floor at current HQ; source states this was not financially driven.", "date": "2026-07-27", "source": "https://www.calcalistech.com/ctechnews/article/b1bqq6nrfg", "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "debt raised or refinanced", "finding": "none found — Series G was equity; no rated or disclosed debt instrument identified", "date": null, "source": null, "ladderRung": null, "retrievedDate": "2026-09-25"},
      {"category": "credit ratings actions", "finding": "not applicable — unrated private company", "date": null, "source": null, "ladderRung": null, "retrievedDate": "2026-09-25"},
      {"category": "going-concern language", "finding": "none found", "date": null, "source": null, "ladderRung": null, "retrievedDate": "2026-09-25"},
      {"category": "CEO or CFO departures", "finding": "none found. CEO Shlomo Kramer confirmed in place as of 2026-07-27, denying acquisition speculation. A regional EMEA channel VP departure (~March 2026) noted but not CEO/CFO level.", "date": "2026-07-27", "source": "https://www.calcalistech.com/ctechnews/article/b1bqq6nrfg", "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "divestitures", "finding": "none found. Context: Cato acquired AI-security startup Aim Security (Sept 2025, reported ~$350M, undisclosed officially) — Cato as acquirer, not divestiture.", "date": "2025-09", "source": "https://en.wikipedia.org/wiki/Cato_Networks", "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "shutdown", "finding": "none found", "date": null, "source": null, "ladderRung": null, "retrievedDate": "2026-09-25"}
    ]
  },
  {
    "supplier": "Check Point (Harmony SASE)",
    "existingId": "print-checkpoint",
    "legalName": "Check Point Software Technologies Ltd.",
    "publicPrivate": "public",
    "ticker": "CHKP",
    "cik": "0001015922",
    "filerType": "foreign private issuer — annual 20-F, interim via 6-K (Israeli company; large accelerated filer)",
    "fiscalYearEnd": "December 31",
    "irUrl": "https://www.checkpoint.com/about-us/investor-relations/",
    "ownership": {
      "status": "segment",
      "details": "Check Point itself is independent and public. Harmony SASE is built on Perimeter 81, which Check Point acquired (announced ~Aug 2023; secondary sources put the deal at ~$490-503M, completion ~Sept 13, 2023) — predates the 12-month window and not re-confirmed against a primary filing this pass."
    },
    "footing": {
      "latestQuarter": {
        "period": "Q2 2026, ended 2026-06-30",
        "releaseDate": "2026-07-30",
        "totalRevenue": "$674 million",
        "revenueYoY": "1%",
        "subscriptionRevenue": "$333 million, +12% YoY",
        "productRevenue": "declined 14% YoY, tied to weaker firewall-appliance demand and the GTM reorganization below",
        "otherMetrics": "Non-GAAP EPS $2.55 (+8% YoY); GAAP EPS $1.87 (+2% YoY); non-GAAP operating income $260M (39% of revenue); RPO $2.6B (+7% YoY); operating cash flow $170M (25% of revenue)",
        "sasePlatformFigure": "not broken out separately",
        "source": "https://www.checkpoint.com/press-releases/check-point-software-reports-2026-second-quarter-financial-results/",
        "retrievedDate": "2026-09-25"
      },
      "priorQuarter": {
        "period": "Q1 2026, ended 2026-03-31",
        "releaseDate": "~2026-04-30",
        "totalRevenue": "$668 million",
        "revenueYoY": "5%",
        "subscriptionRevenue": "$323 million, +11% YoY",
        "otherMetrics": "Non-GAAP EPS $2.50 (+13% YoY); Adjusted Free Cash Flow $457M (+11% YoY)",
        "source": "https://www.sec.gov/Archives/edgar/data/0001015922/000117891326002310/a2635159.htm",
        "retrievedDate": "2026-09-25"
      },
      "nextEarningsDate": "~late October 2026, based on quarterly cadence — not confirmed to an exact date on Check Point's own IR page",
      "companyOutlook": "Company said Q3 2026 will mark the trough for the GTM reorganization, with a stronger Q4 expected."
    },
    "distress": [
      {"category": "layoffs", "finding": "No confirmed company-wide layoff or WARN notice found. A large sales/GTM reorganization — described by trade press as affecting about a third of employees — was moved forward from 2027 to 2026; characterized as a sales-force reorganization (300 gross new sales hires planned) rather than a confirmed net headcount reduction.", "date": "second half 2025 planning; effects landing in 2026", "source": "https://finance.yahoo.com/markets/stocks/articles/check-point-software-technologies-eyes-030346875.html (secondary)", "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "restructuring charges", "finding": "No SEC filing disclosing a specific restructuring-charge dollar figure was found. The GTM reorganization above drove the 14% Q2 2026 product-revenue decline. Sherif Seddik appointed CRO effective 2026-05-01, succeeding Itai Greenberg — a CRO change, not CEO/CFO.", "date": "2026-05-01", "source": "https://www.sec.gov/Archives/edgar/data/0001015922/000117891326002310/a2635159.htm", "ladderRung": 1, "retrievedDate": "2026-09-25"},
      {"category": "debt raised or refinanced", "finding": "$2 billion in convertible senior notes issued during Q2 2026, ~$1.8 billion net proceeds, disclosed in the Q2 2026 earnings release.", "date": "Q2 2026 (April-June 2026)", "source": "https://www.checkpoint.com/press-releases/check-point-software-reports-2026-second-quarter-financial-results/", "ladderRung": 1, "retrievedDate": "2026-09-25"},
      {"category": "credit ratings actions", "finding": "none found", "date": null, "source": null, "ladderRung": null, "retrievedDate": "2026-09-25"},
      {"category": "going-concern language", "finding": "none found", "date": null, "source": null, "ladderRung": null, "retrievedDate": "2026-09-25"},
      {"category": "CEO or CFO departures", "finding": "none found for CEO/CFO. CEO Nadav Zafrir confirmed current (assumed role Dec 2024, before window). CFO Roei Golan confirmed current (since 2023, before window).", "date": "2026-07-30 (confirmed current in Q2 earnings materials)", "source": "https://www.checkpoint.com/press-releases/check-point-software-reports-2026-second-quarter-financial-results/", "ladderRung": 2, "retrievedDate": "2026-09-25"},
      {"category": "divestitures", "finding": "none found", "date": null, "source": null, "ladderRung": null, "retrievedDate": "2026-09-25"},
      {"category": "shutdown", "finding": "none found. Context item, not a required category: a 6-K dated 2026-06-04 disclosed a security vulnerability in Remote Access VPN/Mobile Access functionality with confirmed instances of unauthorized customer access; the company stated it does not believe this is reasonably likely to be material.", "date": "2026-06-04", "source": "https://www.sec.gov/Archives/edgar/data/1015922/000117891326003128/zk2635514.htm", "ladderRung": 1, "retrievedDate": "2026-09-25"}
    ]
  }
]
```

**Suppliers considered and left out.** Seven names cover both shapes this domain asked for: independent pure-plays (Zscaler, Cloudflare, Netskope, Cato Networks) and SASE lines inside larger platform companies (Palo Alto's Prisma SASE, Fortinet's FortiSASE, Check Point's Harmony SASE). This matches all six suppliers already tracked in `prints.ts`, plus Palo Alto Networks as a clean "segment inside a bigger company" example. Cisco (Secure Access / Umbrella) was considered but left out to stay within range and because its SASE story is split across more product lines (Umbrella, Secure Access, Meraki) than the others. Versa Networks was considered — a recognized name reportedly carrying real financial strain (loan default, litigation reported from memory, not freshly sourced) — worth a dedicated follow-up. Forcepoint was considered and left out for lack of research time in this pass; it has been through PE ownership changes worth checking separately.

---

## Domain 2: Cloud security (CNAPP)

Two corrections surfaced during research and are carried through below: Sysdig has **not** gone public — it remains privately held (confirmed against its own "About" page and EDGAR, which has no filings under its name). And Palo Alto Networks has renamed Prisma Cloud: its FY2026 10-K (filed 2026-09-10) describes "Cortex Cloud, the next generation of Prisma Cloud," with customers being migrated; "Prisma Cloud" appears only twice in that filing while "Prisma AIRS" (a separate AI-runtime-security product, not CNAPP) appears more than a dozen times. Palo Alto discloses neither figure separately — only combined "Next-Gen Security ARR."

| Supplier | Public/Private | Latest footing figure (with period) | Last round or ownership | Distress items |
|---|---|---|---|---|
| Wiz | Acquired (was private) | Not disclosed separately — folded into Google Cloud segment from close | Acquired by Google/Alphabet; announced Mar 18, 2025 at $32B; closed Mar 11, 2026 at $29.5B after adjustments | None found in SEC filings checked; pre/post-acquisition leadership and layoff status not independently verified this pass |
| CrowdStrike Falcon Cloud Security | Public (segment of CrowdStrike Holdings, CRWD) | Total company ARR $5.84B, +25% YoY (quarter ended Jul 31, 2026); cloud-security-specific ARR not broken out this quarter | Independent public company; cloud security is a product line, not a subsidiary | None found (no restructuring/workforce-reduction 8-Ks in the last 12 months; two Item 5.02 filings were retention equity awards, not departures) |
| Palo Alto Cortex Cloud (formerly Prisma Cloud) / Prisma AIRS | Public (segment of Palo Alto Networks, PANW) | Total Next-Gen Security ARR $9.10B, +63% YoY (quarter ended Jul 31, 2026); Cortex Cloud/Prisma AIRS not broken out separately | Independent public company; Prisma Cloud rebranded Cortex Cloud, folded into the Cortex platform | None found in SEC filings checked (no restructuring 8-Ks in the last 12 months) |
| Orca Security | Private | No revenue/ARR figure found this pass | Last confirmed round: Series C, Oct 2021, $1.8B valuation (per project data, not re-verified this pass) | None found this pass; TD SYNNEX distribution deal not re-verified |
| Aqua Security | Private | No revenue/ARR figure found this pass | Last disclosed round: Series E extension, Jan 2024, $60M, $1B+ valuation (per project data) | Founder CEO Dror Davidoff and CTO Amir Jerbi stepped back Nov 5-6, 2025; Mike Dube (former President/CRO) became CEO |
| Upwind | Private | No revenue/ARR figure disclosed | Series B, $250M, announced Jan 26, 2026, led by Bessemer Venture Partners; total raised >$430M; company states it crossed unicorn status | None found this pass |
| Sysdig | Private (confirmed this pass, not public) | No revenue/ARR figure found this pass | No new funding round found this pass; board includes Bain Capital Ventures, Accel, Premji Invest, Third Point Ventures, Permira | New CEO Hatem Naguib announced Jun 16, 2026 (ex-Barracuda CEO); prior CEO's departure circumstances not stated in the release |

```json
[
  {
    "supplier": "Wiz",
    "existingId": "print-wiz",
    "legalName": "Wiz, Inc.",
    "publicPrivate": "acquired",
    "ticker": null,
    "cik": null,
    "filerType": "not an independent SEC filer; results consolidated into Alphabet Inc. (CIK 0001652044) within the Google Cloud segment",
    "fiscalYearEnd": "unknown standalone (Alphabet's FYE is Dec 31)",
    "irUrl": "https://abc.xyz/investor/",
    "ownership": {
      "status": "acquired",
      "details": "Acquired by Google LLC (Alphabet subsidiary). Announced March 18, 2025 for $32B all-cash, subject to closing adjustments. Closed March 11, 2026 for $29.5B after purchase price adjustments, excluding post-combination compensation. Results consolidated into Alphabet's Google Cloud segment from close."
    },
    "footing": {
      "standaloneDisclosure": "Not found — no standalone revenue/ARR figure located in the announcement 8-K/press release or Alphabet's Q1 2026 10-Q (Note 8). Alphabet does not disclose Wiz revenue as a discrete line.",
      "purchasePriceAllocation": {
        "totalPurchasePrice": "$29,467 million",
        "intangibleAssets": "$8,300 million (patents/developed technology $3,600M/7yr, customer relationships $4,500M/10yr, trade names $200M/7yr)",
        "goodwill": "$22,689 million",
        "netLiabilitiesAssumed": "-$1,522 million (includes $660M acquired cash)"
      },
      "source": "Alphabet Inc. 10-Q for quarter ended March 31, 2026, filed 2026-04-30, Note 8",
      "sourceUrl": "https://www.sec.gov/Archives/edgar/data/1652044/000165204426000048/goog-20260331.htm",
      "retrievedDate": "2026-09-25"
    },
    "distress": [
      {"category": "layoffs", "finding": "not found; not independently checked against WARN notices or trade press this pass", "date": null, "source": null, "ladderRung": null, "retrievedDate": "2026-09-25"},
      {"category": "restructuring", "finding": "none found in Alphabet 8-K filings", "date": null, "source": "EDGAR full text search, CIK 0001652044", "ladderRung": 1, "retrievedDate": "2026-09-25"},
      {"category": "CEO/CFO departures", "finding": "not verified this pass — Wiz leadership status post-close not checked against a primary source", "date": null, "source": null, "ladderRung": null, "retrievedDate": "2026-09-25"},
      {"category": "antitrust/regulatory (context)", "finding": "Deal closed March 11, 2026 with no caveat in the 10-Q, implying regulatory clearance was obtained. Prior scrutiny history not independently verified this pass.", "date": "2026-03-11", "source": "Alphabet 10-Q, Note 8", "ladderRung": 1, "retrievedDate": "2026-09-25"}
    ]
  },
  {
    "supplier": "CrowdStrike Falcon Cloud Security",
    "existingId": "print-crwd-cloud",
    "legalName": "CrowdStrike Holdings, Inc.",
    "publicPrivate": "public",
    "ticker": "CRWD",
    "cik": "0001535527",
    "filerType": "domestic 10-Q/10-K filer",
    "fiscalYearEnd": "January 31",
    "irUrl": "https://ir.crowdstrike.com/",
    "ownership": {
      "status": "segment",
      "details": "Falcon Cloud Security is a product line within CrowdStrike Holdings, Inc., not a separately reported segment for financial-statement purposes."
    },
    "footing": {
      "latestQuarter": {
        "period": "Quarter ended July 31, 2026 (fiscal Q2 2027)",
        "releaseDate": "2026-08-26",
        "totalRevenue": "$1,470.9 million",
        "totalRevenueYoyGrowth": "25.8% (vs. $1,168.95M in Q2 FY26)",
        "totalARR": "$5.84 billion",
        "totalARRYoyGrowth": "25%",
        "netNewARR": "$332.8 million added in the quarter",
        "cloudSecuritySpecificMetric": "Not disclosed in this quarter's press release — only aggregate module-adoption rates given"
      },
      "priorQuarter": {
        "period": "Quarter ended April 30, 2026 (fiscal Q1 2027)",
        "totalRevenue": "$1,385.6 million",
        "totalRevenueYoyGrowth": "25.6% (vs. $1,103.43M in Q1 FY26)",
        "totalARR": "$5.51 billion",
        "totalARRYoyGrowth": "24%"
      },
      "note": "The previously tracked figure (FY26, >35% cloud ARR growth, >$800M cloud ARR) could not be re-verified against a primary source in the last three quarterly press releases — CrowdStrike appears to have stopped disclosing a Falcon-Cloud-Security-specific ARR dollar figure in its standard earnings release; may still exist in an investor-day presentation not reached this pass.",
      "nextEarningsDate": "not found/not yet announced in sources checked",
      "sourceUrl": "https://www.sec.gov/Archives/edgar/data/1535527/000153552726000029/crwd-20260826xex991.htm",
      "retrievedDate": "2026-09-25"
    },
    "distress": [
      {"category": "layoffs/workforce reduction", "finding": "none found (EDGAR full text search, CIK 0001535527, 2025-09-25 to 2026-09-25)", "date": null, "source": "https://efts.sec.gov/LATEST/search-index?q=%22workforce+reduction%22&ciks=0001535527", "ladderRung": 1, "retrievedDate": "2026-09-25"},
      {"category": "restructuring (8-K Item 2.05)", "finding": "none found", "date": null, "source": "EDGAR full text search", "ladderRung": 1, "retrievedDate": "2026-09-25"},
      {"category": "CEO/CFO departures", "finding": "none found — CEO George Kurtz and President Michael Sentonas both received retention-based performance stock unit awards (Dec 22, 2025 and Apr 16, 2026), not departures", "date": "2025-12-29 / 2026-04-21", "source": "8-K filings, Item 5.02", "ladderRung": 1, "retrievedDate": "2026-09-25"},
      {"category": "debt/credit ratings/going concern/divestitures/shutdown", "finding": "none found this pass", "date": null, "source": null, "ladderRung": null, "retrievedDate": "2026-09-25"}
    ]
  },
  {
    "supplier": "Palo Alto Networks Cortex Cloud (formerly Prisma Cloud) / Prisma AIRS",
    "existingId": "print-panw-cloud",
    "legalName": "Palo Alto Networks, Inc.",
    "publicPrivate": "public",
    "ticker": "PANW",
    "cik": "0001327567",
    "filerType": "domestic 10-K/10-Q filer",
    "fiscalYearEnd": "July 31",
    "irUrl": "https://investors.paloaltonetworks.com/",
    "ownership": {
      "status": "segment",
      "details": "Cloud security is a product line, not a separate legal entity. FY2026 10-K (filed 2026-09-10) states 'Cortex Cloud, the next generation of Prisma Cloud, merges CNAPP with CDR'; existing Prisma Cloud customers are being migrated to Cortex Cloud. 'Prisma Cloud' appears only twice in the 10-K; 'Prisma AIRS' (a separate AI-runtime-security product, not CNAPP) appears 13+ times."
    },
    "footing": {
      "latestQuarter": {
        "period": "Quarter ended July 31, 2026 (fiscal Q4 2026)",
        "releaseDate": "2026-09-01",
        "totalRevenue": "$3.41 billion",
        "totalRevenueYoyGrowth": "34%",
        "nextGenSecurityARR": "$9.10 billion",
        "nextGenSecurityARRYoyGrowth": "63% (boosted materially by the CyberArk and Chronosphere acquisitions, which alone added $1.6B in NGS ARR per the Q3 FY26 release)",
        "cortexCloudOrPrismaAirsSpecificMetric": "Not disclosed separately — Palo Alto reports only consolidated Next-Gen Security ARR across Network & AI Security, Cortex, and Idira platforms"
      },
      "priorQuarter": {
        "period": "Quarter ended April 30, 2026 (fiscal Q3 2026)",
        "totalRevenue": "$3.0 billion",
        "totalRevenueYoyGrowth": "31%",
        "nextGenSecurityARR": "$8.1 billion",
        "nextGenSecurityARRYoyGrowth": "60%"
      },
      "nextQuarterGuidance": "Q1 FY27 NGS ARR guided to $9.54B-$9.56B, 63% YoY growth",
      "nextEarningsDate": "not found/not yet announced in sources checked",
      "sourceUrl": "https://www.sec.gov/Archives/edgar/data/1327567/000132756726000019/ex991q426earningsrelease.htm",
      "retrievedDate": "2026-09-25"
    },
    "distress": [
      {"category": "layoffs/workforce reduction", "finding": "none found (EDGAR full text search, CIK 0001327567, 2025-09-25 to 2026-09-25)", "date": null, "source": "https://efts.sec.gov/LATEST/search-index?q=%22workforce+reduction%22&ciks=0001327567", "ladderRung": 1, "retrievedDate": "2026-09-25"},
      {"category": "restructuring (8-K Item 2.05)", "finding": "none found", "date": null, "source": "EDGAR full text search", "ladderRung": 1, "retrievedDate": "2026-09-25"},
      {"category": "acquisitions (context, not distress)", "finding": "Acquired CyberArk and Chronosphere (contributing $1.6B combined NGS ARR); acquired 'Console,' an AI-native agentic-workflow platform, per the Q4 FY26 release", "date": "disclosed in Q3 and Q4 FY26 releases", "source": "earnings releases cited above", "ladderRung": 2, "retrievedDate": "2026-09-25"},
      {"category": "credit ratings/going concern/CEO-CFO departures/divestitures/shutdown", "finding": "none found this pass", "date": null, "source": null, "ladderRung": null, "retrievedDate": "2026-09-25"}
    ]
  },
  {
    "supplier": "Orca Security",
    "existingId": "print-orca",
    "legalName": "Orca Security Ltd. (per public references; not independently confirmed against a corporate registry this pass)",
    "publicPrivate": "private",
    "ticker": null,
    "cik": null,
    "filerType": "not an SEC filer",
    "fiscalYearEnd": "unknown",
    "irUrl": "https://orca.security/resources/press-releases/",
    "ownership": {
      "status": "independent",
      "details": "VC-backed. Investors named on the company site include YL Ventures, Willoughby Capital, Temasek, Silicon Valley CISO Investments, Stripes, Splunk, SAIC, Redpoint, Lone Pine Capital, ICONIQ, Harmony Partners, Notable, CapitalG, Adams Street. CEO is Avi Shua (co-founder)."
    },
    "footing": {
      "lastRound": "Series C, October 2021, $1.8B valuation (per existing project-tracked data; not independently re-confirmed and no newer round found in the newsroom page checked this pass)",
      "revenueOrArr": "Not found this pass",
      "note": "Orca's newsroom has 41 pages of releases; only the first page (July-September 2026, AI product launches, partner program, Japan localization) was checked, with no funding/revenue/distress items found there. The TD SYNNEX distribution deal in existing project data was not independently re-verified this pass.",
      "retrievedDate": "2026-09-25"
    },
    "distress": [
      {"category": "layoffs", "finding": "none found in the page checked; not exhaustively searched", "date": null, "source": null, "ladderRung": null, "retrievedDate": "2026-09-25"},
      {"category": "all other categories", "finding": "none found in the page checked; not exhaustively searched across the full archive", "date": null, "source": null, "ladderRung": null, "retrievedDate": "2026-09-25"}
    ]
  },
  {
    "supplier": "Aqua Security",
    "existingId": "print-aqua",
    "legalName": "Aqua Security Software Ltd.",
    "publicPrivate": "private",
    "ticker": null,
    "cik": null,
    "filerType": "not an SEC filer",
    "fiscalYearEnd": "unknown",
    "irUrl": "https://www.aquasec.com/news/",
    "ownership": {
      "status": "independent",
      "details": "VC-backed. Founded 2015, headquartered Boston, MA and Ramat Gan, Israel."
    },
    "footing": {
      "lastRound": "Series E extension, January 2024, $60M, $325M total raised, $1B+ valuation (per existing project-tracked data; no newer round found this pass)",
      "revenueOrArr": "Not found this pass; company states it protects 'over 40% of the Fortune 100' and '500+ of the world's largest enterprises' with no dollar figure",
      "retrievedDate": "2026-09-25"
    },
    "distress": [
      {"category": "CEO/CFO/leadership departures", "finding": "Co-founder/CEO Dror Davidoff and co-founder/CTO Amir Jerbi stepped back from day-to-day roles, remaining as strategic advisors. Mike Dube (formerly President and CRO) became CEO; Nir Makowski (former SVP Engineering) became Chief Product & Technology Officer. Framed by the company as succession planning, not distress.", "date": "2025-11-05/06", "source": "https://www.aquasec.com/news/aqua-security-announces-leadership-transition-as-company-enters-its-next-phase-of-growth/", "ladderRung": 2, "retrievedDate": "2026-09-25"},
      {"category": "layoffs/restructuring/debt/ratings/going concern/divestitures/shutdown", "finding": "none found in the news page checked", "date": null, "source": null, "ladderRung": null, "retrievedDate": "2026-09-25"}
    ]
  },
  {
    "supplier": "Upwind",
    "existingId": "print-upwind",
    "legalName": "Upwind Security, Inc.",
    "publicPrivate": "private",
    "ticker": null,
    "cik": null,
    "filerType": "not an SEC filer",
    "fiscalYearEnd": "unknown",
    "irUrl": "https://www.upwind.io/newsroom",
    "ownership": {
      "status": "independent",
      "details": "VC-backed. Founded October 2022, San Francisco. Investors include Bessemer Venture Partners (lead on Series B), Picture Capital, Cyberstarts, Greylock, Craft Ventures."
    },
    "footing": {
      "lastRound": {
        "round": "Series B",
        "date": "2026-01-26",
        "amount": "$250 million",
        "leadInvestor": "Bessemer Venture Partners",
        "totalRaisedToDate": ">$430 million",
        "valuation": "Not disclosed in primary sources reached; company describes the round as achieving 'unicorn status' (implying >$1B), consistent with but not confirming the existing project-tracked $1.5B figure"
      },
      "priorRound": "Series A, $100 million, announced December 2, 2024",
      "revenueOrArr": "Not found this pass. Company states 300+ employees, 150+ customers.",
      "sourceUrl": "https://www.upwind.io/feed/building-next-wave-cloud-security-upwind",
      "retrievedDate": "2026-09-25"
    },
    "distress": [
      {"category": "layoffs/restructuring/debt/ratings/going concern/CEO-CFO departures/divestitures/shutdown", "finding": "none found in the newsroom pages checked", "date": null, "source": null, "ladderRung": null, "retrievedDate": "2026-09-25"}
    ]
  },
  {
    "supplier": "Sysdig",
    "legalName": "Sysdig, Inc.",
    "publicPrivate": "private",
    "ticker": null,
    "cik": null,
    "filerType": "not an SEC filer — confirmed via SEC company-tickers.json and EDGAR full text search (zero matches for 'Sysdig' in S-1/10-Q/10-K forms)",
    "fiscalYearEnd": "unknown",
    "irUrl": "https://sysdig.com/newsroom/",
    "ownership": {
      "status": "independent",
      "details": "VC-backed, founded 2013 by Loris Degioanni. Board includes Bain Capital Ventures, Accel, Premji Invest, Third Point Ventures, Permira. Confirmed private, contrary to an initial (wrong) assumption of a Dec 2024 IPO."
    },
    "footing": {
      "lastRound": "Not found this pass — Sysdig's own site gives no funding-round dates, amounts, or valuation",
      "revenueOrArr": "Not found this pass",
      "retrievedDate": "2026-09-25"
    },
    "distress": [
      {"category": "CEO departure/change", "finding": "Hatem Naguib (former Barracuda CEO, prior VMware executive) named CEO. The release does not name or explain what happened to the previous CEO.", "date": "2026-06-16", "source": "https://sysdig.com/press-releases/sysdig-names-hatem-naguib-as-ceo-to-lead-next-generation-of-ai-driven-cloud-security", "ladderRung": 2, "retrievedDate": "2026-09-25"},
      {"category": "layoffs/restructuring/debt/ratings/going concern/divestitures/shutdown", "finding": "none found in the newsroom pages checked", "date": null, "source": null, "ladderRung": null, "retrievedDate": "2026-09-25"}
    ]
  }
]
```

**Suppliers considered and left out.** Lacework (genuine CNAPP leader before Fortinet acquired it in 2024) was considered and left out in favor of a second independent private vendor (Sysdig) once its true private status was confirmed, rather than a second "absorbed into a bigger platform" example alongside Wiz. Microsoft Defender for Cloud, the other "segment inside a hyperscaler" example alongside Wiz/Google, was not researched given the size this report already reached — a natural next addition. Snyk, Tenable, and Zscaler were not seriously considered: Snyk is developer/SCA-first rather than CNAPP-first, and Tenable/Zscaler are adjacent (exposure management, SSE) rather than core cloud-workload/posture players. For three of the seven suppliers (Orca, Aqua, Upwind), no company-stated revenue or ARR figure could be found anywhere researched — a real evidentiary gap, since it means their footing rests entirely on funding-round data rather than a revenue figure.

---

## Domain 3: Identity (IAM, PAM, IGA)

A tooling caveat applies to this whole domain: the research pass hit its web-search budget almost immediately and could not spawn parallel sub-agents (a concurrent-subagent limit was already at capacity), so it worked entirely through direct WebFetch against SEC EDGAR, company newsrooms, and Google News RSS feeds. That produced solid, source-backed figures for the two public companies and CyberArk's acquisition mechanics, but left real gaps on the three PE-owned companies — none of Ping Identity's, BeyondTrust's, or Delinea's Moody's/S&P/Fitch ratings could be located this way, and BeyondTrust's ARR/revenue figure could not be found at all. Marked "not found" rather than guessed, per the sourcing rule.

| Supplier | Public/Private | Latest footing figure (period) | Last round or ownership | Distress items |
|---|---|---|---|---|
| Okta | Public (OKTA) | Revenue $805M, +11% YoY (quarter ended Jul 31, 2026) | Independent, no ownership change | None found in any category |
| SailPoint | Public (re-IPO'd) | Revenue $308.8M, +16.8% YoY; ARR $1,230.7M, +25.3% YoY (quarter ended Jul 31, 2026) | Thoma Bravo take-private (2022), later returned to public markets (10-K trail starts 2025) | None found in required categories; made an acquisition (Entro Security, reported ~$200M, June 2026, secondary) |
| CyberArk | Acquired — absorbed into Palo Alto Networks | Last standalone: FY2024 revenue $1.0B, +33% YoY (reported Feb 2025, secondary); Q3 2025 figures exist but were not retrieved | Acquired by Palo Alto Networks; announced Jul 30-31, 2025; closed Feb 11, 2026; ~$25B reported deal value (secondary) | ~500-700 former CyberArk staff laid off within days of close (secondary, Feb 2026); CyberArk deregistered from SEC (Forms 25-NSE, 15-12G, Feb 2026) |
| Ping Identity | Private, PE-owned | Approaching $800M ARR, +30%+ SaaS growth (company release, Nov 2024 — stale, nothing newer found) | Thoma Bravo, announced Aug 3, 2022 ($2.8B), closed Oct 18, 2022; ForgeRock merged in, completed Aug 23, 2023 | None found in any category |
| BeyondTrust | Private, PE-owned | No revenue/ARR figure found; named to 2026 Inc. 5000 fastest-growing list (Aug 2026, secondary) | Clearlake Capital "strategic investment," announced Jun 1, 2021; majority vs. minority stake unverified | None found in required categories; separately, a critical RCE vulnerability (CVE-2026-1731) disclosed and actively exploited Feb 2026, prompting a CISA emergency directive (this is a security-incident item, outside the 8 required distress categories) |
| Delinea | Private, PE-owned | "Nearing $400M" ARR (company release, Mar 2025 — a $500M+ figure appears in secondary sources but is unverified) | TPG Capital; Thycotic+Centrify rebranded to Delinea Feb 2022 under TPG; a 2025 report said TPG was "considering" an IPO, not confirmed to have happened | New CFO (Timothy Regan) announced Sept 23, 2026; acquired StrongDM (announced Jan 20, 2026, closed Mar 12, 2026) |
| Microsoft Entra ID | Segment inside Microsoft Corp. (public, MSFT) | No discrete Security/Entra revenue figure in the FY2026 10-K; last standalone figure found was "$20B security revenue," dated Jan 2023, now stale | Product line inside Microsoft; not a distinct ownership entity | ~4,800 Microsoft layoffs announced Jul 2026 (mostly Xbox/sales, not Security-specific, secondary); Security leadership reported "replaced" the same month (secondary, specifics unconfirmed) |

```json
[
  {
    "supplier": "Okta",
    "existingId": "print-okta",
    "legalName": "Okta, Inc.",
    "publicPrivate": "public",
    "ticker": "OKTA",
    "cik": "0001660134",
    "filerType": "domestic 10-K/10-Q filer",
    "fiscalYearEnd": "January 31",
    "irUrl": "https://investor.okta.com",
    "ownership": {"status": "independent", "details": "No ownership changes identified. Publicly traded on Nasdaq."},
    "footing": {
      "latestQuarter": {
        "periodEnd": "2026-07-31",
        "releaseDate": "2026-08-24",
        "filedDate": "2026-08-27",
        "revenue": "$805 million",
        "revenueYoY": "11%",
        "subscriptionRevenue": "$793 million",
        "subscriptionRevenueYoY": "12%",
        "totalRPO": "$4,858 million (+17% YoY)",
        "currentRPO": "$2,585 million (+14% YoY)",
        "source": "https://www.sec.gov/Archives/edgar/data/1660134/000166013426000069/okta-20260731.htm",
        "ladderRung": 1, "retrievedDate": "2026-09-25"
      },
      "priorQuarter": {
        "periodEnd": "2026-04-30",
        "revenue": "$765 million",
        "revenueYoY": "11.2%",
        "source": "https://www.sec.gov/Archives/edgar/data/1660134/000166013426000051/okta-20260430.htm",
        "ladderRung": 1, "retrievedDate": "2026-09-25"
      },
      "nextEarningsDate": "not found"
    },
    "distress": [
      {"category": "layoffs", "finding": "none found", "date": null, "source": "Google News search, last 12 months", "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "restructuring", "finding": "none found", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "debt", "finding": "not found / not checked", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "credit rating", "finding": "not found", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "going concern", "finding": "none found", "date": null, "source": null, "ladderRung": 1, "retrievedDate": "2026-09-25"},
      {"category": "CEO/CFO departure", "finding": "none found; CFO Brett Tighe active as of Sept 2026 coverage", "date": null, "source": "Google News search", "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "divestiture", "finding": "none found", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "shutdown", "finding": "none found", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"}
    ]
  },
  {
    "supplier": "SailPoint",
    "existingId": "print-sailpoint",
    "legalName": "SailPoint, Inc.",
    "publicPrivate": "public",
    "ticker": "SAIL (commonly reported; not independently confirmed against a fetched primary-source document this pass)",
    "cik": "0002030781 (current active filer); legacy CIKs 0001627857 and 0001350136 associated with prior corporate history",
    "filerType": "domestic 10-K/10-Q filer",
    "fiscalYearEnd": "January 31",
    "irUrl": "https://investor.sailpoint.com (not independently fetched this pass)",
    "ownership": {
      "status": "public (re-IPO'd after a PE-owned period)",
      "details": "Taken private by Thoma Bravo (deal timing not independently reconfirmed this pass). Returned to public SEC filing status; first new-era 10-K filed 2025-03-27, full fiscal-year 10-K filed 2026-03-19 for FY ended 2026-01-31. Any residual Thoma Bravo stake is unverified this pass."
    },
    "footing": {
      "latestQuarter": {
        "periodEnd": "2026-07-31", "filedDate": "2026-09-10",
        "revenue": "$308.8 million", "revenueYoY": "16.8%",
        "arr": "$1,230.7 million", "arrYoY": "25.3%",
        "saasArr": "$846.9 million", "saasArrYoY": "36.0%",
        "source": "https://www.sec.gov/Archives/edgar/data/2030781/000203078126000021/sail-20260731.htm",
        "ladderRung": 1, "retrievedDate": "2026-09-25"
      },
      "priorQuarter": {
        "periodEnd": "2026-04-30",
        "revenue": "$280.142 million", "revenueYoY": "21.5%",
        "arr": "$1,162.7 million", "arrYoY": "25.8%",
        "source": "https://www.sec.gov/Archives/edgar/data/2030781/000203078126000011/sail-20260430.htm",
        "ladderRung": 1, "retrievedDate": "2026-09-25"
      },
      "nextEarningsDate": "not found"
    },
    "distress": [
      {"category": "layoffs", "finding": "none found", "date": null, "source": "Google News search, last 12 months", "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "restructuring", "finding": "none found", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "debt", "finding": "not found", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "credit rating", "finding": "not found", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "going concern", "finding": "none found", "date": null, "source": null, "ladderRung": 1, "retrievedDate": "2026-09-25"},
      {"category": "CEO/CFO departure", "finding": "none found; CEO Mark McClain referenced as active in Sept 2026 coverage", "date": null, "source": "Google News search", "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "divestiture", "finding": "none found; note SailPoint was an acquirer, not divester, in this window (reported purchase of Entro Security, ~$200M, announced/closed June 2026, secondary, not independently confirmed against a primary release)", "date": "2026-06", "source": "Google News aggregation", "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "shutdown", "finding": "none found", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"}
    ]
  },
  {
    "supplier": "CyberArk",
    "existingId": "print-cyberark",
    "legalName": "CyberArk Software Ltd.",
    "publicPrivate": "acquired (formerly public)",
    "ticker": "CYBR (Nasdaq, prior to delisting)",
    "cik": "0001598110",
    "filerType": "formerly 20-F/6-K foreign private issuer (Israel); deregistered",
    "fiscalYearEnd": "December 31 (based on 'full year 2024' release timing; not independently refetched this pass)",
    "irUrl": "ir.cyberark.com — no longer resolves (checked this pass), consistent with absorption into Palo Alto Networks",
    "ownership": {
      "status": "acquired",
      "details": "Acquirer: Palo Alto Networks (PANW). Merger agreement announced 2025-07-30/31 (SEC 8-K). Consideration: 2.2005 PANW shares plus $45.00 cash per CyberArk share. Deal closed 2026-02-11 (SEC 8-K Items 1.01/2.03/8.01; corroborated by CyberArk's Form 25-NSE filed 2026-02-11 and Form 15-12G filed 2026-02-23). Total deal value reported at ~$25 billion by trade press (secondary); not stated explicitly in the primary 8-K text retrieved."
    },
    "footing": {
      "lastStandaloneFullYear": {
        "periodEnd": "2024-12-31", "releaseDate": "2025-02-13",
        "revenue": "$1.0 billion", "revenueYoY": "33%",
        "source": "Business Wire (CyberArk earnings release, referenced via secondary aggregation)",
        "ladderRung": 3, "retrievedDate": "2026-09-25"
      },
      "lastStandaloneQuarter": "A Q3 2025 CyberArk earnings release (reported ~2025-11-06) is confirmed to exist via secondary reference but exact revenue/ARR figures were not retrieved this pass — not found.",
      "postAcquisitionDisclosure": "not found — Palo Alto Networks' most recent 10-Q was not checked for a CyberArk/identity-security revenue contribution line this pass."
    },
    "distress": [
      {"category": "layoffs", "finding": "Approximately 500-700 former CyberArk employees laid off within days of the deal closing", "date": "2026-02-12 to 2026-02-17", "source": "calcalistech.com and Globes (Israeli business press, secondary)", "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "restructuring", "finding": "not found / not checked against Palo Alto's own 8-K Item 2.05 disclosures", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "debt", "finding": "Palo Alto Networks assumed and modified CyberArk's 0.00% Convertible Senior Notes due 2030 via a First Supplemental Indenture at deal close", "date": "2026-02-11", "source": "https://www.sec.gov/Archives/edgar/data/1327567/000119312526045600/d40626d8k.htm", "ladderRung": 1, "retrievedDate": "2026-09-25"},
      {"category": "credit rating", "finding": "not found", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "going concern", "finding": "none found", "date": null, "source": null, "ladderRung": 1, "retrievedDate": "2026-09-25"},
      {"category": "CEO/CFO departure", "finding": "not found — could not confirm CyberArk CEO Matt Cohen's post-close status", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "divestiture", "finding": "none found", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "shutdown", "finding": "CyberArk ceased to exist as an independent SEC filer/public entity as of Feb 2026; operationally absorbed into Palo Alto Networks", "date": "2026-02-11 to 2026-02-23", "source": "SEC EDGAR (Forms 25-NSE, 15-12G)", "ladderRung": 1, "retrievedDate": "2026-09-25"}
    ]
  },
  {
    "supplier": "Ping Identity",
    "legalName": "Ping Identity Holding Corp.",
    "publicPrivate": "private",
    "ticker": null, "cik": "not found (no current SEC filer identified)",
    "filerType": "n/a", "fiscalYearEnd": "not found",
    "irUrl": "https://www.pingidentity.com/en/company/newsroom.html",
    "ownership": {
      "status": "pe-owned",
      "details": "Owner: Thoma Bravo. Acquisition announced 2022-08-03 at a reported $2.8 billion; completed 2022-10-18. ForgeRock, a separate Thoma Bravo portfolio company, was subsequently merged into Ping Identity; that merger completed 2023-08-23."
    },
    "footing": {
      "lastDisclosedMetric": {
        "figure": "Approaching $800 million ARR, with 30%+ SaaS revenue growth",
        "date": "2024-11-14",
        "source": "Ping Identity company press release ('Ping Identity Surpasses 30% Annual Growth in SaaS Revenue and Approaches $800M ARR')",
        "ladderRung": 2, "retrievedDate": "2026-09-25"
      },
      "note": "No revenue/ARR figure newer than November 2024 was located this pass; treat as stale relative to 2026-09-25.",
      "creditRating": "not found — no Moody's, S&P, or Fitch rating action for Ping Identity Holding Corp. was located via the tools available this session"
    },
    "distress": [
      {"category": "layoffs", "finding": "none found", "date": null, "source": "Google News search, last 12 months", "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "restructuring", "finding": "none found", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "debt", "finding": "not found", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "credit rating", "finding": "not found", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "going concern", "finding": "none found", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "CEO/CFO departure", "finding": "none found", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "divestiture", "finding": "none found", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "shutdown", "finding": "none found", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"}
    ]
  },
  {
    "supplier": "BeyondTrust",
    "legalName": "BeyondTrust Corporation (operating as BeyondTrust)",
    "publicPrivate": "private",
    "ticker": null, "cik": "not found",
    "filerType": "n/a", "fiscalYearEnd": "not found",
    "irUrl": "https://www.beyondtrust.com (newsroom page returned HTTP 403 when fetched directly this pass)",
    "ownership": {
      "status": "pe-owned",
      "details": "Clearlake Capital made a 'strategic investment' in BeyondTrust, announced 2021-06-01. Majority vs. minority stake not independently confirmed this pass. Clearlake's continued involvement corroborated by a 2024-04-17 report of BeyondTrust (under Clearlake) acquiring Entitle."
    },
    "footing": {
      "revenueOrArr": "not found — no company-stated revenue or ARR figure located this pass",
      "otherSignal": {
        "finding": "Named to the 2026 Inc. 5000 list of America's fastest-growing private companies",
        "date": "2026-08-11", "source": "Yahoo Finance / Inc. (secondary)", "ladderRung": 5, "retrievedDate": "2026-09-25"
      },
      "creditRating": "not found — no Moody's, S&P, or Fitch rating action located via the tools available this session"
    },
    "distress": [
      {"category": "layoffs", "finding": "none found", "date": null, "source": "Google News search, last 12 months", "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "restructuring", "finding": "none found", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "debt", "finding": "not found", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "credit rating", "finding": "not found", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "going concern", "finding": "none found", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "CEO/CFO departure", "finding": "none found", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "divestiture", "finding": "none found", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "shutdown", "finding": "none found", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "security incident (supplemental, outside the required 8 categories)", "finding": "A critical remote code execution vulnerability (CVE-2026-1731) in a BeyondTrust product was disclosed and actively exploited within 24 hours of proof-of-concept release, prompting a CISA emergency patching directive for federal agencies. Follows a separate, larger breach disclosed in late 2024/early 2025.", "date": "2026-02-09 to 2026-02-19", "source": "SecurityWeek, BleepingComputer, Unit 42, GreyNoise (multiple secondary outlets)", "ladderRung": 5, "retrievedDate": "2026-09-25"}
    ]
  },
  {
    "supplier": "Delinea",
    "legalName": "Delinea Inc. (formed from the Thycotic/Centrify merger)",
    "publicPrivate": "private",
    "ticker": null, "cik": "not found",
    "filerType": "n/a", "fiscalYearEnd": "not found",
    "irUrl": "https://www.delinea.com (dedicated newsroom URL returned HTTP 404 when fetched directly this pass)",
    "ownership": {
      "status": "pe-owned",
      "details": "Owner: TPG Capital. ThycoticCentrify was rebranded to Delinea under TPG, reported 2022-02-01 (secondary). A 2025-03-24 report said TPG was 'considering' a public offering for Delinea; not confirmed this pass to have occurred — treat IPO status as unconfirmed/pending."
    },
    "footing": {
      "lastDisclosedMetric": {
        "figure": "Nearing $400 million ARR", "date": "2025-03-18",
        "source": "Delinea company press release via GlobeNewswire",
        "ladderRung": 2, "retrievedDate": "2026-09-25"
      },
      "unverifiedFigure": "A $500 million+ ARR figure for 2025 appeared in a search-result snippet but could not be traced to a primary source this pass — unverified, not company-confirmed.",
      "creditRating": "not found — no Moody's, S&P, or Fitch rating action located via the tools available this session"
    },
    "distress": [
      {"category": "layoffs", "finding": "none found", "date": null, "source": "Google News search, last 12 months", "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "restructuring", "finding": "none found", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "debt", "finding": "not found", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "credit rating", "finding": "not found", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "going concern", "finding": "none found", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "CEO/CFO departure", "finding": "Timothy Regan appointed Chief Financial Officer of Delinea; whether this followed a predecessor's departure or filled a vacancy was not confirmed this pass", "date": "2026-09-23", "source": "GlobeNewswire ('Delinea Appoints Timothy Regan as Chief Financial Officer')", "ladderRung": 2, "retrievedDate": "2026-09-25"},
      {"category": "divestiture", "finding": "none found; note Delinea was an acquirer, not divester, in this window — announced acquisition of StrongDM 2026-01-20, closed 2026-03-12", "date": "2026-01-20 to 2026-03-12", "source": "Security Systems News, Dark Reading (secondary)", "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "shutdown", "finding": "none found", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"}
    ]
  },
  {
    "supplier": "Microsoft Entra ID",
    "existingId": "print-identity-no-series (partial overlap — see note below)",
    "legalName": "Microsoft Corporation (Entra ID is a product line, not a separate legal entity)",
    "publicPrivate": "public", "ticker": "MSFT", "cik": "0000789019",
    "filerType": "domestic 10-K/10-Q filer", "fiscalYearEnd": "June 30",
    "irUrl": "https://www.microsoft.com/en-us/investor",
    "ownership": {
      "status": "segment",
      "details": "Entra ID (formerly Azure Active Directory) is a product line inside Microsoft Corporation. Microsoft's FY2026 10-K (filed 2026-07-29) does not report a discrete 'Security business' or Entra ID revenue line; identity/security capability spans both the Intelligent Cloud segment and the Productivity and Business Processes segment (via the 'Enterprise Mobility + Security' bundle, which the 10-K names as competing with 'identity vendors')."
    },
    "footing": {
      "latestReportedQuarter": {
        "periodEnd": "2026-06-30 (fiscal Q4 2026 / fiscal year end)", "releaseDate": "2026-07-29",
        "source": "Microsoft Investor Relations (full text not retrievable this pass due to a 404 on the direct URL guessed)",
        "ladderRung": 2, "retrievedDate": "2026-09-25"
      },
      "securityBusinessFigure": {
        "finding": "No current-period (2025/2026) standalone Security business revenue figure was located. The most recent such figure found anywhere was '$20 billion in security revenue,' reported by trade press on 2023-01-30, citing Microsoft's own disclosure at the time — now nearly three years stale and not confirmed to still be current.",
        "ladderRung": 5, "retrievedDate": "2026-09-25"
      },
      "nextEarningsDate": "not found — Microsoft's investor relations page stated the next release would be 'announced soon' as of the date fetched; no specific date posted"
    },
    "distress": [
      {"category": "layoffs", "finding": "Microsoft announced approximately 4,800 job cuts, concentrated in Xbox/gaming (~3,200 of those) and commercial sales divisions — not reported as Security-specific", "date": "2026-07", "source": "secondary trade coverage", "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "restructuring (Security segment specifically)", "finding": "not found", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "credit rating (Microsoft Corporation overall)", "finding": "not found — no Moody's or S&P rating action located via the tools available this session", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "going concern", "finding": "none found (not applicable at this scale)", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "Security/Identity leadership departure", "finding": "Trade press reported Microsoft 'replaces security leaders weeks after announcing 4,800 layoffs,' but specific names, roles, and whether this was a departure versus an ordinary reorganization were not retrievable this pass", "date": "2026-07-16", "source": "secondary trade press", "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "divestiture", "finding": "none found", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "shutdown", "finding": "none found", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"}
    ]
  }
]
```

**Suppliers considered and left out.** Seven picked: Okta, SailPoint, CyberArk, Ping Identity, BeyondTrust, Delinea, Microsoft Entra ID — two independent public companies, one company public-then-acquired mid-window, three PE-owned private companies, and one identity line embedded in a much larger public company. Saviynt (private, IGA competitor to SailPoint) was left out; it is a real, growing player a security leader might name, especially for IGA deals, but researching it fully would have pushed past the requested range — worth a future pass. ForgeRock was not profiled separately since it no longer exists as an independent entity (Thoma Bravo folded it into Ping Identity in August 2023); it's covered inside the Ping Identity record instead. IBM Security Verify, Cisco Duo, RSA (privately held under STG since 2020), JumpCloud, and OneLogin/One Identity (Quest) were considered and excluded on the "who would a security leader name first" test against the goal of a mixed public/private sample.

---

## Domain 4: Email security

A tooling caveat applies here too: WebSearch was unavailable for nearly this entire research session (budget exhausted before a single call), so the findings below came from WebFetch against SEC EDGAR, company newsrooms, and Bing's static search/news pages. That reached two genuine SEC primary-source filings (Check Point, Microsoft) but means several "not found" items — particularly current Moody's/S&P ratings on the three PE-owned companies — reflect what these tools could reach today, not a confirmed absence of a rating.

There is no existing entry for any email security supplier in `web/src/data/prints.ts`, so no `existingId` applies to this domain.

| Supplier | Public/Private | Latest footing figure (with period) | Last round or ownership | Distress items |
|---|---|---|---|---|
| Proofpoint, Inc. | Private | No post-2021 company-stated revenue/ARR found; last Moody's action found is B3 CFR, positive outlook (June 2021, secondary) | Thoma Bravo take-private, closed Aug 31, 2021, $12.3B (secondary) | CEO/CFO stable, no layoffs found; completed a $1.8B acquisition of Hornetsecurity (Dec 8, 2025) — growth move, not distress |
| Mimecast Limited | Private | No post-2022 company-stated revenue/ARR found; 42,000+ customers, 2,000+ employees per current newsroom | Permira take-private, closed May 2022, $5.8B (secondary) | CEO change: Ranjan Singh replaced Marc van Zadelhoff, effective June 25, 2026; no layoffs, ratings, or debt actions found |
| Abnormal Security ("Abnormal AI") | Private | ARR >$200M, growing 100%+ YoY, as of Aug 6, 2024 (no later figure found) | Series D, Aug 6, 2024, $250M at $5.1B valuation, led by Wellington Management | None found in any category — no layoffs, no IPO filing, no CEO/CFO change |
| Barracuda Networks, Inc. | Private | No post-2022 company-stated revenue/ARR found | KKR acquired from Thoma Bravo, closed Aug 2022, ~$4B (secondary) | CEO change: Rohit Ghai replaced Hatem Naguib, announced Sept 23, 2025; acquired Evo Security (~July 2026); no layoffs or ratings action found |
| Microsoft Defender for Office 365 (segment inside Microsoft Corp.) | Public (MSFT) | Microsoft FY2026 (ended June 30, 2026) total revenue $331.8B, +18% YoY; no Defender-for-O365-specific or whole-Security-business figure disclosed since Jan 2023 ($20B+) | N/A — segment | Company-wide WA layoffs in the period (605 in July 2026, secondary WARN tracker) not tied to Security specifically; no restructuring 8-K, no CEO/CFO change |
| Check Point Harmony Email & Collaboration (segment inside Check Point Software) | Public (CHKP) | Check Point Q2 2026 (ended June 30, 2026) total revenue $674M, +1% YoY (Q1 2026 was +5% YoY — deceleration); Harmony Email growth not disclosed separately | N/A — segment (originated from Avanan, acquired ~Aug 30, 2021, $250-300M, secondary) | None found — no layoffs, restructuring, ratings action, or CEO/CFO change |

```json
[
  {
    "supplier": "Proofpoint",
    "legalName": "Proofpoint, Inc.",
    "publicPrivate": "private",
    "ticker": null,
    "cik": "0001212458",
    "filerType": "Formerly domestic 10-K/10-Q filer (NASDAQ: PFPT); filed Form 15-12B deregistration 2021-09-10; no SEC filings found since 2021",
    "fiscalYearEnd": "not independently verified post-privatization",
    "irUrl": "https://www.proofpoint.com/us/newsroom",
    "ownership": {
      "status": "pe-owned",
      "details": "Thoma Bravo take-private. Announced 2021-04-26, closed 2021-08-31 (confirmed by an 8-K filed 2021-08-31 covering merger/change-of-control items; deal value $12.3B per secondary reporting, not independently confirmed against a Thoma Bravo or Proofpoint press release this pass)."
    },
    "footing": {
      "publicReporting": false,
      "lastCompanyStatedRevenueOrArr": "not found — no post-2021 revenue or ARR figure located",
      "lastPreLboPublicRevenue": {"figure": "$1.050 billion", "period": "FY2020", "source": "secondary, historical only, superseded by go-private", "retrievedDate": "2026-09-25"},
      "creditRating": {
        "agency": "Moody's", "rating": "B3 Corporate Family Rating, outlook positive", "date": "2021-06-07",
        "source": "https://markets.businessinsider.com/news/bonds/proofpoint-inc-moody-s-assigns-b3-cfr-to-proofpoint-outlook-positive-1030499415",
        "ladderRung": 3,
        "note": "Periodic review completion noted 2021-12-13. No rating action found after 2021 despite searching."
      },
      "nextEarningsDate": "not applicable — private, no public earnings"
    },
    "distress": [
      {"category": "Layoffs", "finding": "none found", "date": null, "source": "Bing News search, no results", "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "Restructuring charges", "finding": "not applicable — private company, no 8-K obligation; none found in press", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "Debt raised or refinanced", "finding": "none found", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "Credit ratings actions", "finding": "none found in the last 12 months (last confirmed action 2021)", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "Going-concern language", "finding": "none found", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "CEO or CFO departures", "finding": "none found — Sumit Dhawan confirmed as current CEO; Sept 8, 2026 hires were Chief Legal Officer and Chief People Officer, not CEO/CFO", "date": "2026-09-08 (unrelated hires); CEO confirmed current as of Sept 2026", "source": "https://www.proofpoint.com/us/newsroom", "ladderRung": 2, "retrievedDate": "2026-09-25"},
      {"category": "Divestitures", "finding": "none found. Note: Proofpoint completed a $1.8B acquisition of Hornetsecurity on 2025-12-08 — Proofpoint acquiring another company, not divesting", "date": "2025-12-08", "source": "secondary financial press", "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "Shutdown", "finding": "none — actively publishing product announcements through September 2026", "date": "2026-09-22", "source": "https://www.proofpoint.com/us/newsroom", "ladderRung": 2, "retrievedDate": "2026-09-25"}
    ]
  },
  {
    "supplier": "Mimecast",
    "legalName": "Mimecast Limited (subsidiary of Permira-affiliated Magnesium Bidco Limited since 2022)",
    "publicPrivate": "private",
    "ticker": null,
    "cik": "0001644675",
    "filerType": "Formerly domestic 10-K filer (NASDAQ: MIME); last 10-K located filed 2021-05-27; no filings found after go-private",
    "fiscalYearEnd": "March 31",
    "irUrl": "https://www.mimecast.com/resources/press-releases/",
    "ownership": {
      "status": "pe-owned",
      "details": "Permira take-private via affiliate Magnesium Bidco Limited. Announced 2021-12-07, closed May 2022, deal value $5.8B (secondary, not independently confirmed against a primary press release this pass)."
    },
    "footing": {
      "publicReporting": false,
      "lastCompanyStatedRevenueOrArr": "not found — no post-2022 revenue or ARR figure located",
      "currentCompanyStatedMetrics": {"employees": "2,000+", "customers": "42,000+", "endUsersProtected": "27 million", "source": "https://www.mimecast.com/resources/press-releases/ (current site content, undated)", "ladderRung": 2, "retrievedDate": "2026-09-25"},
      "creditRating": {"agency": "none found", "rating": "not found", "note": "No Moody's or S&P rating located via available search tools this session"},
      "recentAcquisitionsByMimecast": ["Elevate Security (Jan 2024)", "Code42 (Jul 2024)", "Aware (Aug 2024)"],
      "nextEarningsDate": "not applicable — private, no public earnings"
    },
    "distress": [
      {"category": "Layoffs", "finding": "none found", "date": null, "source": "Bing News search, no results", "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "Restructuring charges", "finding": "not applicable — private company, no 8-K obligation; none found in press", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "Debt raised or refinanced", "finding": "none found", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "Credit ratings actions", "finding": "none found", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "Going-concern language", "finding": "none found", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "CEO or CFO departures", "finding": "CEO change: Ranjan Singh appointed CEO effective 2026-06-25, succeeding Marc van Zadelhoff", "date": "2026-06-25", "source": "secondary financial press and company newsroom", "ladderRung": 2, "retrievedDate": "2026-09-25"},
      {"category": "Divestitures", "finding": "none found", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "Shutdown", "finding": "none — actively publishing product announcements through August 2026", "date": "2026-08-03", "source": "https://www.mimecast.com/resources/press-releases/", "ladderRung": 2, "retrievedDate": "2026-09-25"}
    ]
  },
  {
    "supplier": "Abnormal Security",
    "legalName": "Abnormal Security Corporation (product/marketing brand now 'Abnormal AI')",
    "publicPrivate": "private",
    "ticker": null,
    "cik": "not found — no SEC filings located; Form D exempt-offering search inconclusive due to tool access issues",
    "filerType": "none",
    "fiscalYearEnd": "not disclosed",
    "irUrl": "https://abnormal.ai/newsroom",
    "ownership": {
      "status": "independent",
      "details": "Independent, venture-backed. Founded 2018. Headquarters commonly reported as San Francisco, CA but not verified against a fetched primary source this pass."
    },
    "footing": {
      "lastFundingRound": {
        "date": "2024-08-06", "stage": "Series D", "amount": "$250 million",
        "leadInvestor": "Wellington Management",
        "otherInvestors": ["Greylock Partners", "Menlo Ventures", "Insight Partners", "CrowdStrike Falcon Fund"],
        "postMoneyValuation": "$5.1 billion",
        "totalFundingToDate": "$546 million (as stated at time of round)",
        "source": "https://abnormal.ai/newsroom/press-releases/series-d-5b-valuation",
        "ladderRung": 2, "retrievedDate": "2026-09-25"
      },
      "companyStatedArr": {"figure": "over $200 million ARR, 100%+ YoY growth", "date": "2024-08-06", "source": "https://abnormal.ai/newsroom/press-releases/series-d-5b-valuation", "ladderRung": 2, "note": "No later ARR figure found despite searching through 2026-09-25"},
      "noLaterFundingRoundFound": true
    },
    "distress": [
      {"category": "Layoffs", "finding": "none found", "date": null, "source": "Bing News search, no results", "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "Restructuring charges", "finding": "not applicable — private company", "date": null, "source": "n/a", "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "Debt raised or refinanced", "finding": "none found", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "Credit ratings actions", "finding": "not applicable — venture-backed, no rated debt found", "date": null, "source": "n/a", "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "Going-concern language", "finding": "none found", "date": null, "source": "n/a", "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "CEO or CFO departures", "finding": "none found — Evan Reiser (founder) confirmed as current CEO", "date": "retrieved 2026-09-25", "source": "https://abnormal.ai/about", "ladderRung": 2, "retrievedDate": "2026-09-25"},
      {"category": "Divestitures", "finding": "none found", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "Shutdown", "finding": "none — actively publishing product announcements through September 2026", "date": "2026-09-24", "source": "https://abnormal.ai/newsroom", "ladderRung": 2, "retrievedDate": "2026-09-25"},
      {"category": "IPO filing", "finding": "none found — no S-1 or confidential filing located", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"}
    ]
  },
  {
    "supplier": "Barracuda Networks",
    "legalName": "Barracuda Networks, Inc.",
    "publicPrivate": "private",
    "ticker": null,
    "cik": "0001348334",
    "filerType": "Formerly domestic 10-K filer (NYSE: CUDA); last 10-K located filed 2017-05-15, consistent with the 2017-2018 Thoma Bravo take-private",
    "fiscalYearEnd": "not independently re-verified this session",
    "irUrl": "https://www.barracuda.com/company/news",
    "ownership": {
      "status": "pe-owned",
      "details": "KKR acquired Barracuda from Thoma Bravo. Announced April 2022, closed August 2022, deal value approximately $4 billion (secondary, not independently confirmed against a primary press release this pass)."
    },
    "footing": {
      "publicReporting": false,
      "lastCompanyStatedRevenueOrArr": "not found — no post-2022 revenue or ARR figure located despite multiple searches",
      "creditRating": {"agency": "none found", "rating": "not found", "note": "No Moody's or S&P rating located via available search tools this session"},
      "recentAcquisitionByBarracuda": {"target": "Evo Security (identity/PAM for MSPs)", "date": "approximately July 2026", "source": "secondary trade press (Help Net Security, Morningstar, Security InfoWatch)", "ladderRung": 5, "retrievedDate": "2026-09-25"},
      "nextEarningsDate": "not applicable — private, no public earnings"
    },
    "distress": [
      {"category": "Layoffs", "finding": "none found", "date": null, "source": "Bing News search, no results", "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "Restructuring charges", "finding": "not applicable — private company", "date": null, "source": "n/a", "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "Debt raised or refinanced", "finding": "none found", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "Credit ratings actions", "finding": "none found", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "Going-concern language", "finding": "none found", "date": null, "source": "n/a", "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "CEO or CFO departures", "finding": "CEO change: Rohit Ghai (former RSA CEO) appointed CEO, succeeding Hatem Naguib who stepped down after leading since 2021", "date": "2025-09-23", "source": "PR Newswire release, republished by secondary outlets", "ladderRung": 3, "retrievedDate": "2026-09-25"},
      {"category": "Divestitures", "finding": "none found", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "Shutdown", "finding": "none — actively acquiring and expanding (Evo Security deal, ~July 2026)", "date": "2026-07 (approximate)", "source": "secondary trade press", "ladderRung": 5, "retrievedDate": "2026-09-25"}
    ]
  },
  {
    "supplier": "Microsoft Defender for Office 365",
    "legalName": "Microsoft Corporation",
    "publicPrivate": "public",
    "ticker": "MSFT",
    "cik": "0000789019",
    "filerType": "Domestic large accelerated filer, 10-K/10-Q",
    "fiscalYearEnd": "June 30",
    "irUrl": "https://www.microsoft.com/en-us/investor",
    "ownership": {
      "status": "segment",
      "details": "Defender for Office 365 is a product inside Microsoft's Security portfolio, which is not a standalone reported segment — it is split across all three of Microsoft's reported segments (Productivity and Business Processes, Intelligent Cloud, More Personal Computing). No dollar figure specific to Defender for Office 365 is disclosed anywhere in Microsoft's SEC filings."
    },
    "footing": {
      "latestQuarter": {"period": "Q4 FY2026, ended 2026-06-30", "releaseDate": "2026-07-29", "companyRevenue": "$90.0 billion, +18% YoY (quarter)", "source": "SEC 10-K filed 2026-07-29, accession 0001193125-26-323660", "ladderRung": 1, "retrievedDate": "2026-09-25"},
      "fullYearFY2026Revenue": {"figure": "$331,839 million, +18% YoY vs FY2025's $281,724 million", "source": "FY2026 10-K", "ladderRung": 1, "retrievedDate": "2026-09-25"},
      "priorQuarterComparisonNote": "Segment-level YoY figures for FY2026 vs FY2025: Productivity and Business Processes +16%, Intelligent Cloud +30%, More Personal Computing -1% — Security revenue is embedded across all three and not separable from these",
      "securityBusinessFigure": {"figure": "\"security business surpassed $20 billion in revenue\" (trailing 12 months)", "date": "2023-01-24 (FY2023 Q2 earnings call)", "source": "Microsoft's own official earnings call transcript", "ladderRung": 2, "note": "Last time Microsoft cited an aggregate Security revenue figure; all 13 subsequent quarterly transcripts through FY2026 Q4 checked, none repeated it. Defender for Office 365-specific figure: not disclosed separately."},
      "nextEarningsDate": "not found"
    },
    "distress": [
      {"category": "Layoffs", "finding": "Company-wide Washington State WARN filings in the period, not Security-specific: 40 employees (2025-10-03), 42 employees (2025-11-07), 605 employees (2026-07-06, part of a reported ~4,800 global cut affecting Commercial and Xbox organizations)", "date": "2025-10-03 to 2026-07-06", "source": "secondary WARN aggregator and trade coverage; primary WA state WARN database not directly reachable this session", "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "Restructuring charges (8-K Item 2.05)", "finding": "none found among 9 Microsoft 8-Ks filed 2025-09-30 through 2026-09-02", "date": null, "source": "SEC EDGAR", "ladderRung": 1, "retrievedDate": "2026-09-25"},
      {"category": "Debt raised or refinanced", "finding": "none in FY2026 — proceeds from issuance of debt were $0 in both FY2026 and FY2025; long-term debt declined from $40,152M to $31,067M", "date": "FY2026 (ended 2026-06-30)", "source": "FY2026 10-K cash flow statement", "ladderRung": 1, "retrievedDate": "2026-09-25"},
      {"category": "Credit ratings actions", "finding": "not verified — Moody's/S&P sites blocked direct access this session", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "Going-concern language", "finding": "none found — full-text search of FY2026 10-K", "date": "2026-09-25", "source": "FY2026 10-K", "ladderRung": 1, "retrievedDate": "2026-09-25"},
      {"category": "CEO or CFO departures", "finding": "none — Satya Nadella (CEO) and Amy Hood (CFO) both presented the FY2026 Q4 call. No Security-division-specific leadership change found (the three Item 5.02 8-Ks in the period concern board directors, not executive officers)", "date": "2026-07-29 (latest call)", "source": "earnings call transcript and SEC 8-K filings", "ladderRung": 1, "retrievedDate": "2026-09-25"},
      {"category": "Divestitures", "finding": "none found, company-wide or Security-specific", "date": null, "source": "SEC 8-K filings", "ladderRung": 1, "retrievedDate": "2026-09-25"},
      {"category": "Shutdown", "finding": "none — actively documented and updated (Microsoft Learn content updated 2026-08-12; Security blog post 2026-09-24)", "date": "2026-09-24", "source": "Microsoft Learn / Microsoft Security blog", "ladderRung": 2, "retrievedDate": "2026-09-25"}
    ]
  },
  {
    "supplier": "Check Point Harmony Email & Collaboration",
    "legalName": "Check Point Software Technologies Ltd.",
    "publicPrivate": "public",
    "ticker": "CHKP",
    "cik": "0001015922",
    "filerType": "Foreign private issuer, 20-F (annual) / 6-K (interim)",
    "fiscalYearEnd": "December 31",
    "irUrl": "https://www.checkpoint.com/press-releases/ (ir.checkpoint.com unreachable this session — DNS failure)",
    "ownership": {
      "status": "segment",
      "details": "Harmony Email & Collaboration originated from Avanan, acquired by Check Point. Deal announced ~2021-08-30/31, price $250-300 million (secondary, corroborated by multiple outlets dated the same week). Not a separately reported revenue line; Check Point reports Products and Licenses, Security Subscriptions, and Software Updates and Maintenance, with Harmony as one of three qualitative product pillars (Quantum, CloudGuard, Harmony)."
    },
    "footing": {
      "latestQuarter": {"period": "Q2 2026, ended 2026-06-30", "releaseDate": "2026-07-30", "totalRevenue": "$674 million, +1% YoY", "securitySubscriptionsRevenue": "$333 million, +12% YoY", "source": "https://www.checkpoint.com/press-releases/check-point-software-reports-2026-second-quarter-financial-results/", "ladderRung": 2, "retrievedDate": "2026-09-25"},
      "priorQuarter": {"period": "Q1 2026, ended 2026-03-31", "totalRevenue": "$668 million, +5% YoY", "securitySubscriptionsRevenue": "$323 million, +11% YoY", "source": "SEC 6-K filed 2026-04-30, https://www.sec.gov/Archives/edgar/data/1015922/000117891326002310/a2635159.htm", "ladderRung": 1, "retrievedDate": "2026-09-25"},
      "comparisonNote": "Total revenue growth decelerated from +5% YoY (Q1 2026) to +1% YoY (Q2 2026); Security Subscriptions growth held roughly steady (+11% to +12%)",
      "harmonyEmailSpecificFigure": "not disclosed separately — both quarters' filings mention only qualitative \"strong demand\" for email security within Security Subscriptions, with no dollar figure or growth rate",
      "nextEarningsDate": "not found"
    },
    "distress": [
      {"category": "Layoffs", "finding": "none found", "date": null, "source": "Bing News search, no results", "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "Restructuring charges", "finding": "none found in press releases reviewed (May-September 2026)", "date": null, "source": "https://www.checkpoint.com/press-releases/", "ladderRung": 2, "retrievedDate": "2026-09-25"},
      {"category": "Debt raised or refinanced", "finding": "none found", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "Credit ratings actions", "finding": "not found — not independently checked against Moody's/S&P directly (site access blocked); no news coverage found either", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "Going-concern language", "finding": "none found (expected — large, profitable, cash-generative company)", "date": null, "source": "n/a", "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "CEO or CFO departures", "finding": "none found — Nadav Zafrir confirmed as current CEO as of the Q2 2026 earnings release", "date": "2026-07-30", "source": "https://www.checkpoint.com/press-releases/check-point-software-reports-2026-second-quarter-financial-results/", "ladderRung": 2, "retrievedDate": "2026-09-25"},
      {"category": "Divestitures", "finding": "none found", "date": null, "source": null, "ladderRung": 5, "retrievedDate": "2026-09-25"},
      {"category": "Shutdown", "finding": "none — actively expanding; board approved a $2.0 billion share-repurchase-authorization expansion on 2026-05-11, a sign of financial strength rather than distress", "date": "2026-05-11", "source": "https://www.checkpoint.com/press-releases/", "ladderRung": 2, "retrievedDate": "2026-09-25"}
    ]
  }
]
```

**Suppliers considered and left out.** Cisco Secure Email was considered and left out — it sits inside Cisco's Security division the same way Defender for Office 365 sits inside Microsoft and Harmony Email sits inside Check Point, and this domain already has two "segment inside a larger vendor" examples with even less separate disclosure than Check Point gives Harmony. Fortra/Agari was also considered and left out: Agari is one of six roughly equal-sized product categories inside Fortra's much broader GRC and security portfolio, Fortra is owned by a four-firm PE consortium (TA Associates, Harvest Partners, Charlesbank Capital Partners, HGGC), and it is less likely to be named first by a security leader than the six included here; Fortra also discloses essentially nothing product-specific about Agari's financial performance.

---

## Summary

Fourteen public and private companies across four domains, each checked against SEC EDGAR, company press releases, and — where the sourcing ladder required it — labelled trade press. Network/SASE and cloud security are the most current: Zscaler, Palo Alto, Fortinet, Cloudflare, Netskope, Cato, and Check Point all have quarters within the last four months, with confirmed distress events at Zscaler (restructuring, workforce cut) and Cloudflare (a $150.7M charge, ~1,100 roles, tied to an AI-first shift) sitting alongside genuinely clean records at Fortinet and Cato. Cloud security surfaced two corrections to prior assumptions: Sysdig remains private, and Palo Alto has quietly renamed Prisma Cloud to Cortex Cloud, folding both it and Prisma AIRS into one undisclosed "Next-Gen Security ARR" figure.

Identity and email security are structurally thinner on footing data, because most of the market has gone private. Okta and SailPoint are the only two identity suppliers still filing with the SEC; CyberArk stopped filing in February 2026 after Palo Alto closed its $25B acquisition, cutting an estimated 500-700 jobs within days. Ping Identity, BeyondTrust, and Delinea are all PE-owned with no revenue figure newer than March 2025 at best, and none of their credit ratings could be located this pass — a genuine gap, not a confirmed absence. Email security is almost entirely private: Proofpoint, Mimecast, and Barracuda have disclosed no revenue since their take-privates (2021-2022), though all three show fresh CEO changes in the last twelve months. Abnormal Security is the one clean, fast-growing independent in that domain, still running on an August 2024 funding round with no newer disclosure.

Every figure above traces to a dated source URL and a rung on the five-level sourcing ladder; anything not verified is marked so rather than smoothed over. The weakest spots for anyone editing this into the site are the PE-owned identity and email names, where ratings data especially needs a follow-up pass with direct Moody's/S&P access rather than search-engine workarounds.
