# Coverage research — Group 3: Data security, Application security & supply chain, OT/IoT security, AI security

Prepared 2026-09-25 for Security Market Pulse (sourced facts only — no rankings, no judgments, no investment advice).
Sourcing method: the five-rung ladder from `docs/active/fable-run/research/11-distress-signal-sources.md` — (1) company's
own SEC filing, (2) rating-agency action republished by company/wire, (3) state WARN notice, (4) confirmed primary
corporate action (acquirer's own press release/8-K), (5) trade press including anonymous-sourced reporting, always
labeled "reported by X, unconfirmed." Every fact below carries a source URL and a rung where applicable. Anything the
research could not confirm against a primary source is marked UNVERIFIED rather than stated as fact. `existingId`
values point at the matching row in `web/src/data/prints.ts` for reuse; `null` means the supplier is not currently
tracked on the site.

This research was run by four parallel sub-agents, one per domain, each independently searching SEC EDGAR, company
newsrooms, and (where reachable) trade press. Two of the four sessions ran out of general web-search budget partway
through and fell back to direct EDGAR/company-site fetches, which is noted per domain below — this made those two
domains' sourcing skew more toward SEC primary documents (a good thing for reliability) but left some funding-history
and WARN-notice checks incomplete (flagged inline as UNVERIFIED or "none found given available tools").

---

## 1. Data security (DSPM, DLP, backup/resilience as security)

Suppliers researched: Rubrik, Varonis, Cyera, BigID, Veeam, Cohesity, Commvault. Sentra was dropped from the original
candidate list (see "Considered and left out" below).

### 1.1 Summary table

| Supplier | Public/Private | Latest footing figure | Last round / ownership | Distress (last 12 months) |
|---|---|---|---|---|
| Rubrik, Inc. (RBRK) | Public | Revenue $427.3M (+38% YoY), Subscription ARR $1.66B (+33% YoY) — Q2 FY2027, ended 2026-07-31 | Independent, NYSE-listed | CRO transition (Feb 2026); no layoffs, no restructuring charge found |
| Varonis Systems (VRNS) | Public | Revenue $180.0M (+18.3% YoY), SaaS ARR $726.0M (+52% YoY) — Q2 2026, ended 2026-06-30 | Independent, Nasdaq-listed | 5% headcount cut (~120 staff), Oct 2025, after an earnings miss; stock fell ~45-48% same day |
| Cyera | Private | No company-stated revenue/ARR found | $400M growth-equity extension from Goldman Sachs Alternatives, announced 2026-09-22, valuation "over $12B" | None found; company was an active acquirer (Oasis Security Sep 2026, Ryft Apr 2026) |
| BigID | Private | No verified company-stated ARR (a third-party 2026 profile cites ~$100M ARR, UNVERIFIED) | $60M round led by Riverwood Capital, March 2024, $1B valuation — no newer round found | None found (search coverage limited — see caveats) |
| Veeam Software | Private | No current ARR figure verified in this pass | Insight Partners majority stake, closed ~Jan 2020 (~$5B, secondary source); acquired Securiti AI (DSPM) for $1.725B, announced/closed 2025-12-11 | None found |
| Cohesity | Private | Wikipedia cites "$1.7B revenue (2025)" — UNVERIFIED, no primary source reached | Merged with Veritas's Enterprise Data Protection business, announced Feb 2024, closed Dec 2024 (ownership split not independently confirmed) | None found (see caveats) |
| Commvault Systems (CVLT) | Public | Revenue $314.1M (+11% YoY), Subscription ARR $1,054M (+22% YoY) — Q1 FY2027, ended 2026-06-30 | Independent, Nasdaq-listed | $32.2M restructuring charges in FY2026 (workforce reductions, tech transitions, office closures); $900M convertible notes issued FY2026 |

### 1.2 Full records (JSON)

```json
[
  {
    "supplier": "Rubrik, Inc.",
    "existingId": "print-rubrik",
    "publicPrivate": "public",
    "ticker": "RBRK",
    "cik": "0001943896",
    "filerType": "domestic (10-Q/10-K), Delaware incorporation",
    "fiscalYearEnd": "January 31",
    "irUrl": "https://ir.rubrik.com",
    "ownership": {
      "status": "independent, publicly traded (NYSE: RBRK)",
      "note": "No controlling PE/strategic owner found in this research pass. IPO commonly reported as April 2024; not re-sourced this pass, treat as UNVERIFIED in this record."
    },
    "publicFinancials": {
      "latestQuarter": {
        "periodEnd": "2026-07-31",
        "releaseDate": "2026-08-27",
        "label": "Q2 FY2027",
        "revenue": "$427.3 million",
        "revenueYoY": "+38%",
        "headlineMetric": "Subscription ARR",
        "headlineMetricValue": "$1.66 billion",
        "headlineMetricYoY": "+33%",
        "sourceUrl": "https://www.sec.gov/Archives/edgar/data/0001943896/000194389626000055/rubrikinc-991pressrelease7.htm"
      },
      "priorQuarter": {
        "periodEnd": "2026-04-30",
        "label": "Q1 FY2027",
        "revenue": "$387.1 million",
        "revenueYoY": "+39%",
        "headlineMetric": "Subscription ARR",
        "headlineMetricValue": "$1.565 billion",
        "headlineMetricYoY": "+32%",
        "sourceUrl": "https://www.sec.gov/Archives/edgar/data/0001943896/000194389626000047/rbrk-20260430.htm"
      },
      "nextReportDate": "Not yet announced as of 2026-09-25 (checked https://ir.rubrik.com/news-events/ir-calendar)"
    },
    "distressLast12Months": [
      {
        "category": "executive departure",
        "date": "2026-02-06",
        "description": "Brian McCarthy, President of Global Sales & Field Operations, resigned effective 2026-02-06; Jesse Green (previously President, Rubrik Americas) promoted to Chief Revenue Officer.",
        "sourceUrl": "https://ir.rubrik.com/news-events/press-releases/news-details/2026/Rubrik-Promotes-Jesse-Green-to-Chief-Revenue-Officer/default.aspx",
        "secondarySourceUrl": "https://www.sec.gov/Archives/edgar/data/1943896/000119312526037791/d52441d8k.htm",
        "ladderRung": 4
      },
      { "category": "layoffs/WARN", "description": "none found" },
      { "category": "restructuring charges (8-K Item 2.05)", "description": "none found" },
      { "category": "debt raised/refinanced", "description": "none found" },
      { "category": "ratings actions", "description": "none found" },
      { "category": "going-concern language", "description": "none found; company is FCF-positive" },
      { "category": "CFO departure", "description": "none found" },
      { "category": "divestitures/shutdown", "description": "none found" }
    ],
    "retrievedDate": "2026-09-25"
  },
  {
    "supplier": "Varonis Systems, Inc.",
    "existingId": "print-varonis",
    "publicPrivate": "public",
    "ticker": "VRNS",
    "cik": "0001361113",
    "filerType": "domestic (10-Q/10-K), Delaware incorporation",
    "fiscalYearEnd": "December 31",
    "irUrl": "https://ir.varonis.com",
    "ownership": {
      "status": "independent, publicly traded (Nasdaq: VRNS)",
      "note": "IPO 2014 per IR site metadata; HQ 801 Brickell Avenue, Miami, FL 33131 per SEC filer address."
    },
    "publicFinancials": {
      "latestQuarter": {
        "periodEnd": "2026-06-30",
        "releaseDate": "2026-07-28",
        "label": "Q2 2026",
        "revenue": "$180.0 million",
        "revenueYoY": "+18.3%",
        "headlineMetric": "Total SaaS ARR",
        "headlineMetricValue": "$726.0 million",
        "headlineMetricYoY": "+52% (total); +25% excluding conversions",
        "sourceUrl": "https://www.sec.gov/Archives/edgar/data/0001361113/000117184326004948/exh_991.htm"
      },
      "priorQuarter": {
        "periodEnd": "2026-03-31",
        "releaseDate": "2026-04-28",
        "label": "Q1 2026",
        "revenue": "$173.1 million",
        "revenueYoY": "+27%",
        "headlineMetric": "Total SaaS ARR",
        "headlineMetricValue": "$683.2 million",
        "headlineMetricYoY": "+69% (total); +29% excluding conversions",
        "sourceUrl": "https://www.sec.gov/Archives/edgar/data/0001361113/000117184326002774/exh_991.htm"
      },
      "nextReportDate": "Not confirmed this pass — IR press-release page returned HTTP 403 to automated fetch"
    },
    "distressLast12Months": [
      {
        "category": "layoffs",
        "date": "2025-10-28/29",
        "description": "5% headcount reduction (~120 employees) announced on the Q3 2025 earnings call. CEO Yakov Faitelson: \"a 5% reduction in headcount in order to reallocate our resources where we see the highest return on investment.\" Tied to weaker renewals in the federal vertical and non-Federal on-prem subscription business.",
        "sourceUrl": "https://www.fool.com/earnings/call-transcripts/2025/10/29/varonis-vrns-q3-2025-earnings-call-transcript/",
        "secondarySourceUrl": "https://www.sec.gov/Archives/edgar/data/1361113/000117184325006721/exh_991.htm",
        "ladderRung": 4
      },
      {
        "category": "market reaction (context, not a primary distress fact)",
        "date": "2025-10-28/29",
        "description": "Reported: shares fell approximately 45-48% intraday, wiping out roughly $3.8 billion of market capitalization, following the earnings miss and layoff announcement.",
        "sourceUrl": "https://www.bankinfosecurity.com/varonis-lays-off-5-staff-stock-plunges-as-renewals-drop-a-29881",
        "ladderRung": 5
      },
      {
        "category": "restructuring charges (8-K Item 2.05)",
        "description": "none found — the 10-Q for the quarter ended 2025-09-30 contains no restructuring/severance charge disclosure.",
        "sourceUrl": "https://www.sec.gov/Archives/edgar/data/1361113/000162828025047145/vrns-20250930.htm"
      },
      {
        "category": "acquisition made (context)",
        "date": "~August 2025 (per trade press; not independently reverified against a primary Varonis source date this pass)",
        "description": "SlashNext (email-security company) acquired for up to $150 million, roughly two months before the October 2025 layoff; cited by trade press as a contributing cost pressure.",
        "sourceUrl": "https://www.bankinfosecurity.com/varonis-lays-off-5-staff-stock-plunges-as-renewals-drop-a-29881",
        "ladderRung": 5
      },
      { "category": "debt raised/refinanced", "description": "none found" },
      { "category": "ratings actions", "description": "none found" },
      { "category": "going-concern language", "description": "none found" },
      { "category": "CEO/CFO departures", "description": "none found — Yakov Faitelson (CEO) and Guy Melamed (CFO) both active in 2026-era sources" },
      {
        "category": "divestiture/product sunset",
        "description": "Company announced end-of-life for its self-hosted (on-prem) product effective 2026-12-31, disclosed in Q3 2025 outlook commentary. A product decision, not a corporate divestiture.",
        "sourceUrl": "https://www.sec.gov/Archives/edgar/data/1361113/000117184325006721/exh_991.htm",
        "ladderRung": 4
      },
      {
        "category": "litigation",
        "description": "Reported/unconfirmed: a plaintiff-firm solicitation notice for a potential securities class action appeared after the stock drop. A law-firm advertisement, not confirmation of a filed or certified case.",
        "sourceUrl": "https://www.nasdaq.com/press-release/vrns-investor-notice-varonis-systems-inc-investors-substantial-losses-have",
        "ladderRung": 5
      }
    ],
    "retrievedDate": "2026-09-25"
  },
  {
    "supplier": "Cyera",
    "existingId": "print-cyera",
    "publicPrivate": "private",
    "ticker": null,
    "cik": "none found — no SEC filer entity located under \"Cyera\" in EDGAR company search",
    "filerType": null,
    "fiscalYearEnd": null,
    "irUrl": null,
    "companyUrl": "https://www.cyera.com",
    "ownership": {
      "status": "independent, venture/growth-equity backed",
      "ceo": "Yotam Segev (current as of 2026-09-25)",
      "headquarters": "UNVERIFIED",
      "foundingYear": "UNVERIFIED"
    },
    "fundingHistory": [
      {
        "date": "2026-09-22",
        "round": "Growth-equity investment (reported as a Series G extension)",
        "amount": "$400 million",
        "leadInvestor": "Growth Equity at Goldman Sachs Alternatives",
        "valuation": "\"over $12 billion\" (same headline valuation as the June 2026 round)",
        "sourceUrl": "https://www.cyera.com/press-releases/cyera-announces-400-million-investment-from-goldman-sachs-to-build-the-trust-layer-for-the-agentic-enterprise",
        "ladderRung": 4,
        "note": "Most recent raise found; treat as the current headline round."
      },
      {
        "date": "2026-06-10",
        "round": "Series F/G (not explicitly named in release)",
        "amount": "$600 million",
        "leadInvestor": "Evolution Equity Partners",
        "valuation": "$12 billion",
        "sourceUrl": "https://www.cyera.com/press-releases/cyera-raises-600-million-at-12-billion-valuation-to-continue-building-the-trust-layer-for-the-ai-era",
        "ladderRung": 4
      },
      {
        "date": "2026-01-08",
        "round": "Series F",
        "amount": "$400 million",
        "leadInvestor": "UNVERIFIED",
        "valuation": "$9 billion",
        "sourceUrl": "https://techcrunch.com/2026/01/08/data-security-startup-cyera-hits-9b-valuation-six-months-after-being-valued-at-6b",
        "ladderRung": 5
      },
      {
        "date": "2025-06-11",
        "round": "Series E",
        "amount": "$540 million (also reported as $300M elsewhere; amount needs reconciliation)",
        "leadInvestor": "UNVERIFIED",
        "valuation": "$6 billion",
        "sourceUrl": "https://www.cyera.com/press-releases/ai-native-security-leader-cyera-doubles-customer-base-in-six-months-reaching-6-billion-valuation",
        "ladderRung": 4
      }
    ],
    "companyStatedRevenue": "none found",
    "otherActivity": [
      { "date": "2026-09-03", "description": "Acquired Oasis Security (completed)", "sourceUrl": "https://www.cyera.com/press-releases/", "ladderRung": 4 },
      { "date": "2026-04-23", "description": "Acquired Ryft", "sourceUrl": "https://www.cyera.com/press-releases/", "ladderRung": 4 }
    ],
    "distressLast12Months": [
      { "category": "layoffs", "description": "none found" },
      { "category": "restructuring", "description": "none found" },
      { "category": "CEO/founder departure", "description": "none found" },
      { "category": "litigation", "description": "none found" },
      { "category": "divestitures/shutdown", "description": "none found" }
    ],
    "researchCaveat": "Web-search budget was exhausted partway through this company's research; findings lean on direct fetches of cyera.com and SEC EDGAR rather than a full trade-press sweep.",
    "retrievedDate": "2026-09-25"
  },
  {
    "supplier": "BigID",
    "existingId": "print-bigid",
    "publicPrivate": "private",
    "ticker": null,
    "cik": "0001668449",
    "filerType": "Form D (exempt offering) filer only, Delaware incorporation",
    "fiscalYearEnd": "December 31",
    "irUrl": null,
    "companyUrl": "https://www.bigid.com",
    "ownership": {
      "status": "independent, venture-backed",
      "ceo": "Dimitri Sirota (current as of 2026-09-25)",
      "headquarters": "New York, NY (641 Avenue of the Americas, Front 2, New York, NY 10011) — per SEC EDGAR filer address",
      "foundingYear": "2016"
    },
    "fundingHistory": [
      {
        "date": "2024-03",
        "round": "Growth round",
        "amount": "$60 million",
        "leadInvestor": "Riverwood Capital",
        "otherInvestors": "Silver Lake Waterman, Advent International",
        "valuation": "$1 billion",
        "sourceUrl": "https://tracxn.com/d/companies/bigid/__pHSLjAzI2aqF63ud9QosF69usdaBPTT49_kou_rHtgw/funding-and-investors",
        "ladderRung": 5,
        "note": "Aggregator source, not a company press release directly reached this pass. No newer round found as of 2026-09-25."
      }
    ],
    "companyStatedRevenue": "A third-party 2026 company profile cites approximately $100 million ARR; UNVERIFIED — not a company-primary source.",
    "distressLast12Months": [
      { "category": "layoffs/WARN", "description": "none found (checked layoffs.fyi: \"No layoff data found for this company\")", "sourceUrl": "https://layoffs.fyi/company/bigid/", "ladderRung": 5 },
      { "category": "restructuring", "description": "none found" },
      { "category": "CEO/CFO/founder departure", "description": "none found" },
      { "category": "divestitures/shutdown", "description": "none found" },
      { "category": "litigation", "description": "none found" }
    ],
    "researchCaveat": "BigID's own news/blog pages returned JavaScript-rendered content automated fetch could not read, and general web search returned no BigID-specific hits after the session's search budget was exhausted.",
    "retrievedDate": "2026-09-25"
  },
  {
    "supplier": "Veeam Software",
    "existingId": null,
    "publicPrivate": "private",
    "ticker": null,
    "cik": "none found",
    "filerType": null,
    "fiscalYearEnd": null,
    "irUrl": null,
    "companyUrl": "https://www.veeam.com",
    "ownership": {
      "status": "PE-owned",
      "owner": "Insight Partners (majority stake)",
      "dealDate": "Closed on or about 2020-01-09",
      "dealValue": "~$5 billion (reported)",
      "sourceUrl": "https://en.wikipedia.org/wiki/Veeam",
      "ladderRung": 5,
      "note": "Secondary source only — Veeam's own press release on the Insight Partners deal was not reachable this pass.",
      "ceo": "Anand Eswaran (appointed 2021; no departure found)",
      "headquarters": "Kirkland, Washington (widely reported; not independently reverified this pass)",
      "foundingYear": "2006"
    },
    "companyStatedRevenue": "Not independently reconfirmed. A secondary source (Wikipedia) cites \"$1.5B+ ARR as of March 2024\"; no more recent company-stated figure found. UNVERIFIED beyond that date.",
    "distressLast12Months": [
      {
        "category": "acquisition made",
        "date": "First reported 2025-10-21 (trade press); officially announced/closed by Veeam 2025-12-11",
        "description": "Acquired Securiti AI (DSPM/AI-governance company) for $1.725 billion. Securiti founder/CEO Rehan Jalil joins Veeam as President of Security and AI; approximately 600 Securiti employees integrated.",
        "sourceUrl": "https://www.veeam.com/news/veeam-acquires-securiti-ai.html",
        "ladderRung": 4
      },
      { "category": "layoffs/WARN", "description": "none found (checked layoffs.fyi and general search; not a full sweep)" },
      { "category": "restructuring", "description": "none found" },
      { "category": "debt raised/refinanced", "description": "none found" },
      { "category": "ratings actions", "description": "none found" },
      { "category": "CEO/CFO departures", "description": "none found" },
      { "category": "litigation", "description": "none found" }
    ],
    "researchCaveat": "Web-search budget also ran out partway through. Several distress-category checks rely on layoffs.fyi and general fetches rather than a full trade-press sweep.",
    "retrievedDate": "2026-09-25"
  },
  {
    "supplier": "Cohesity",
    "existingId": null,
    "publicPrivate": "private",
    "ticker": null,
    "cik": "none found",
    "filerType": null,
    "fiscalYearEnd": null,
    "irUrl": null,
    "companyUrl": "https://www.cohesity.com",
    "ownership": {
      "status": "private, post-merger structure — NOT independently confirmed against a primary source",
      "mergerAnnounced": "2024-02 (reported)",
      "mergerClosed": "2024-12 (reported)",
      "description": "Merged with Veritas's Enterprise Data Protection business, previously owned by The Carlyle Group. Reported deal value ~$3 billion; reported combined-company valuation ~$7 billion. Ownership split NOT independently confirmed — rests on a single secondary source.",
      "sourceUrl": "https://en.wikipedia.org/wiki/Cohesity",
      "ladderRung": 5,
      "ceo": "Sanjay Poonen (since August 2022, pre-merger and continuing)",
      "ipoStatus": "Reported to have filed confidentially for IPO in December 2021; remains private as of 2026-09-25 per the same secondary source."
    },
    "companyStatedRevenue": "A secondary source (Wikipedia) states \"$1.7 billion (2025)\" revenue. UNVERIFIED — no primary source reached.",
    "distressLast12Months": [
      { "category": "layoffs", "description": "none found on layoffs.fyi; could not independently confirm any Veritas-integration-related layoffs", "ladderRung": 5 },
      { "category": "restructuring", "description": "none found" },
      { "category": "CEO/CFO departures", "description": "none found — Sanjay Poonen remains CEO" },
      { "category": "litigation", "description": "none found" },
      { "category": "divestitures/shutdown", "description": "none found" }
    ],
    "researchCaveat": "No primary Cohesity source (own press release or SEC filing) was reached for the merger's ownership/valuation figures or the revenue figure. Recommend an independent pass on Cohesity's ownership percentages and current ARR before publishing anything from this record.",
    "retrievedDate": "2026-09-25"
  },
  {
    "supplier": "Commvault Systems, Inc.",
    "existingId": null,
    "publicPrivate": "public",
    "ticker": "CVLT",
    "cik": "0001169561",
    "filerType": "domestic (10-Q/10-K), Delaware incorporation",
    "fiscalYearEnd": "March 31",
    "irUrl": "ir.commvault.com (address confirmed from SEC filings; not independently re-rendered via automated fetch this pass)",
    "ownership": {
      "status": "independent, publicly traded (Nasdaq: CVLT)",
      "ceo": "Sanjay Mirchandani; no departure found",
      "headquarters": "1 Commvault Way, Tinton Falls, NJ 07724"
    },
    "publicFinancials": {
      "latestQuarter": {
        "periodEnd": "2026-06-30",
        "releaseDate": "2026-07-28",
        "label": "Q1 FY2027",
        "revenue": "$314.1 million",
        "revenueYoY": "+11%",
        "headlineMetric": "Subscription ARR",
        "headlineMetricValue": "$1,054 million",
        "headlineMetricYoY": "+22%",
        "sourceUrl": "https://www.sec.gov/Archives/edgar/data/1169561/000116956126000020/q1fy27pressrelease.htm"
      },
      "priorQuarter": {
        "periodEnd": "2026-03-31",
        "releaseDate": "2026-04-28",
        "label": "Q4 FY2026",
        "revenue": "$311.7 million",
        "revenueYoY": "+13%",
        "fullYearRevenue": "$1,183.7 million (FY2026 total, +19% YoY)",
        "headlineMetric": "Subscription ARR",
        "headlineMetricValue": "$989.3 million",
        "headlineMetricYoY": "+27%",
        "sourceUrl": "https://www.sec.gov/Archives/edgar/data/1169561/000116956126000013/q4fy26pressrelease.htm"
      },
      "nextReportDate": "Not confirmed this pass; cadence implies late October 2026 for Q2 FY2027 but no announced date found"
    },
    "distressLast12Months": [
      {
        "category": "restructuring charges (8-K Item 2.05 territory)",
        "description": "Two restructuring plans initiated in fiscal 2026 covering workforce reductions, technology transitions, office lease closures, and exit of operations in certain jurisdictions. Total FY2026 charges $32.2 million; Q1 FY2027 charges an additional $2.4 million. Both plans expected to be substantially completed during fiscal 2027.",
        "sourceUrl": "https://www.sec.gov/Archives/edgar/data/1169561/000116956126000013/q4fy26pressrelease.htm",
        "secondarySourceUrl": "https://www.sec.gov/Archives/edgar/data/1169561/000116956126000020/q1fy27pressrelease.htm",
        "ladderRung": 1
      },
      {
        "category": "debt raised/refinanced",
        "description": "$900 million in convertible notes issued during fiscal 2026 (plus $99.6 million spent on related capped-call purchases).",
        "sourceUrl": "https://www.sec.gov/Archives/edgar/data/1169561/000116956126000013/q4fy26pressrelease.htm",
        "ladderRung": 1
      },
      { "category": "ratings actions", "description": "none found" },
      { "category": "going-concern language", "description": "none found" },
      { "category": "CEO/CFO departures", "description": "none found" },
      { "category": "divestitures/shutdown", "description": "none found" },
      { "category": "litigation", "description": "none found" }
    ],
    "retrievedDate": "2026-09-25"
  }
]
```

### 1.3 Considered but left out

- **Sentra** (private, DSPM) — dropped. The other seven already fill the 4-7 slot with the vendors a security leader
  is most likely to name unprompted as backup/resilience-as-security or DSPM/DLP incumbents; Sentra is smaller and
  newer relative to the other DSPM players (Cyera, BigID) already covered, and this pass lacked budget to give it the
  same sourcing rigor.
- **Securiti** — not researched as a standalone entry since it was acquired by Veeam (confirmed: announced/closed
  2025-12-11, $1.725 billion). Its history is folded into the Veeam record above. The existing site id
  `print-securiti` was not assigned to any record in this file since Securiti is not being tracked as an independent
  supplier going forward.

### 1.4 Research gaps and caveats

- **Cohesity**: no primary source was reached for the Veritas-merger ownership split, combined valuation, or the
  ~$1.7B revenue figure — all rest on a single secondary source and should be independently reverified before
  publishing.
- **Veeam**: the Insight Partners deal date/value and the "Kirkland, WA" headquarters also rest on secondary sourcing
  only; the Securiti acquisition terms and close date ARE primary. No current ARR figure could be reconfirmed past a
  March 2024 secondary-sourced figure.
- **BigID**: no newer funding round than March 2024 was found, but coverage was constrained by JS-rendered pages and
  an exhausted search budget — this is "not found," not "confirmed absent."
- **Cyera**: headquarters and founding year could not be confirmed from the company's own site.
- **Commvault**: next earnings date not confirmed.

---

## 2. Application security and software supply chain security

All 8 candidates named in the brief were kept (exceeds the suggested 4-7 range deliberately — see "Considered and left
out" below).

### 2.1 Summary table

| Supplier | Public/Private | Latest footing figure | Last round / ownership | Distress items (one-line) |
|---|---|---|---|---|
| Snyk | Private, VC-backed | No audited figures; last disclosed valuation $8.5B (Sept 2021), reportedly marked down since | Last known round: $530M Series F, Sept 2021, $8.5B valuation (no confirmed round since) | Reported ~90 layoffs (Jun 2026, unconfirmed); CEO Peter McKay moved to advisor, Ken MacAskill named interim CEO (date unconfirmed); employee-share valuation reportedly marked down (Aug 2026, unconfirmed) |
| Checkmarx | Private, PE-owned (Hellman & Friedman + TPG) | No audited figures; UNVERIFIED | H&F acquired from Insight Partners for $1.15B, announced Mar 16 2020 / closed Apr 16 2020; TPG co-invested | None found in last 12 months |
| Veracode | Private, PE-owned (TA Associates, majority) | No audited figures; UNVERIFIED | Thoma Bravo bought from Broadcom for $950M (Nov 2018/Jan 2019); TA Associates took majority stake at $2.5B valuation, Mar 2022 | New CFO named Jun 5 2025, just outside window; no layoffs/ratings/restructuring found |
| Semgrep | Private, VC-backed | Third-party estimate only ($33.6M "revenue," unaudited/UNVERIFIED) | Series D, $100M, led by Menlo Ventures, 2025-02-05 (~$204M total raised) | None found; funding predates the 12-month window |
| JFrog Ltd. (FROG) | Public | Q2 2026 (period end Jun 30 2026): revenue $163.8M, +29% YoY; cloud revenue $87.5M, +53% YoY | N/A — public since 2020 IPO | None found; Feb 26 2026 8-K was a $300M buyback authorization (capital return, not distress) |
| Sonatype | Private, PE-owned (Vista Equity Partners, majority since Nov 2019) | No audited figures; UNVERIFIED | Vista majority stake, announced Nov 18 2019 (price undisclosed); prior TPG-led $80M round, Sept 2018 | CEO transition Jul 29 2025 (planned, just outside window); no layoffs found |
| Chainguard | Private, VC-backed | No audited figures; UNVERIFIED | $280M growth financing led by General Catalyst's Customer Value Fund, 2025-10-23 (~$892M total raised) — supersedes the Apr 2025 Series D | None found; the Oct 2025 growth round is a positive event inside the window, not distress |
| GitHub Advanced Security (segment inside Microsoft, MSFT) | Public (segment; GHAS not separately reported) | Not separately disclosed — GitHub revenue folded into "Azure and other cloud services" per Microsoft's FY2026 10-K | N/A | GitHub CEO Thomas Dohmke resigned Aug 11 2025 (effective end of 2025), no successor named; GHAS restructured into separate SKUs |

### 2.2 Full records (JSON)

```json
[
  {
    "supplier": "Snyk",
    "existingId": null,
    "legalName": "Snyk, Inc.",
    "publicOrPrivate": "private",
    "ticker": null,
    "secCik": null,
    "filerType": "none — does not file with the SEC",
    "fiscalYearEnd": "UNVERIFIED",
    "headquarters": "100 Summer St, Fl 7, Boston, MA 02110",
    "companyUrl": "https://snyk.io",
    "investorRelationsUrl": null,
    "ownership": {
      "type": "independent, VC-backed",
      "owner": "Multiple venture investors (Accel, Boldstart Ventures, Tiger Global, Sands Capital and others per public funding announcements); no PE control stake found",
      "notes": "No acquisition or PE buyout found."
    },
    "privateFinancials": {
      "lastFundingRound": {
        "date": "2021-09-09",
        "round": "Series F",
        "amount": "$530 million",
        "leadInvestor": "UNVERIFIED",
        "valuation": "$8.5 billion",
        "source": "https://www.crn.com/news/security/snyk-raises-530m-on-8-5b-valuation-to-protect-applications",
        "ladderRung": 5,
        "label": "reported by CRN, unconfirmed against a Snyk primary source"
      },
      "laterRoundCheck": "Searched for any funding round 2022-2026; none found. UNVERIFIED whether $8.5B/Sept 2021 remains the last priced round.",
      "companyStatedRevenueOrArr": "none found"
    },
    "distressAndChange12Months": [
      {
        "category": "layoffs",
        "description": "Reported ~90 jobs eliminated; company described as reorganizing leadership, go-to-market and research to accelerate AI strategy",
        "date": "2026-06-25 (publication date of report)",
        "sourceUrl": "https://www.govinfosecurity.com/snyk-reportedly-cuts-90-jobs-to-accelerate-ai-strategy-a-32081",
        "ladderRung": 5,
        "label": "reported by GovInfoSecurity, unconfirmed — no Snyk press release or WARN notice located"
      },
      {
        "category": "CEO/executive departure",
        "description": "Peter McKay (CEO for ~7 years) reported to have transitioned to an Advisor role; Ken MacAskill named interim CEO",
        "date": "UNVERIFIED exact date; confirmed in place by 2026-06-25 per trade-press headline",
        "sourceUrl": "https://www.govinfosecurity.com/snyk-reportedly-cuts-90-jobs-to-accelerate-ai-strategy-a-32081",
        "ladderRung": 5,
        "label": "reported/unconfirmed — no Snyk primary-source announcement located"
      },
      {
        "category": "valuation markdown / going-concern-adjacent signal",
        "description": "Reported that Snyk marked down employee share value; article states prior valuation was $8.5B and implies a much lower current mark",
        "date": "2026-08-28",
        "sourceUrl": "https://www.businessinsider.com/snyk-employee-share-value-drops-as-ai-rivals-surge-ahead-2026-8",
        "ladderRung": 5,
        "label": "reported by Business Insider, unconfirmed — this session could not directly fetch businessinsider.com; figures come from a search-result summary, not a direct read. Treat all specific numbers as UNVERIFIED pending direct confirmation."
      },
      { "category": "restructuring charges (8-K Item 2.05 equivalent)", "description": "N/A — private company, no SEC filing obligation" },
      { "category": "debt raised/refinanced", "description": "none found" },
      { "category": "ratings actions", "description": "none found" },
      { "category": "going-concern language", "description": "none found" },
      { "category": "divestitures / shutdown", "description": "none found" },
      { "category": "acquisitions made by Snyk", "description": "none found in the last 12 months" }
    ],
    "retrievedDate": "2026-09-25"
  },
  {
    "supplier": "Checkmarx",
    "existingId": null,
    "legalName": "Checkmarx Ltd.",
    "publicOrPrivate": "private",
    "ticker": null,
    "secCik": null,
    "filerType": "none — does not file with the SEC",
    "fiscalYearEnd": "UNVERIFIED",
    "headquarters": "Multi-regional (U.S. — Paramus, NJ per a 2026 company announcement — plus London, Frankfurt, Tel Aviv, Singapore, Sydney); founded 2006",
    "companyUrl": "https://checkmarx.com",
    "investorRelationsUrl": null,
    "ownership": {
      "type": "PE-owned",
      "owner": "Hellman & Friedman (majority), with TPG as co-investor",
      "dealDate": "announced 2020-03-16, closed 2020-04-16",
      "dealDetail": "Hellman & Friedman acquired Checkmarx from Insight Partners for $1.15 billion in cash; TPG co-invested.",
      "source": "search-result synthesis citing the original 2020 deal reporting; a direct primary-source H&F or Checkmarx press release URL was not captured this pass",
      "ladderRung": 5,
      "label": "reported/synthesized from search results, not read directly from an H&F or Checkmarx press release this session — treat deal date and price as UNVERIFIED pending a direct primary-source read, though consistent with widely repeated reporting"
    },
    "privateFinancials": {
      "lastFundingRound": "N/A — this was a PE buyout, not a venture round",
      "companyStatedRevenueOrArr": "none found"
    },
    "ceo": "Sandeep Johri, appointed February 2023, succeeding co-founder Emmanuel Benzaquen",
    "distressAndChange12Months": [
      {"category": "layoffs", "description": "none found"},
      {"category": "WARN notice", "description": "none found"},
      {"category": "restructuring charges", "description": "none found (private company, no 8-K obligation)"},
      {"category": "debt raised/refinanced", "description": "none found"},
      {"category": "ratings actions", "description": "none found (no Moody's/S&P/Fitch coverage located)"},
      {"category": "going-concern language", "description": "none found"},
      {"category": "CEO/CFO departures", "description": "none found in the 12-month window (CEO Johri has held the role since Feb 2023)"},
      {"category": "divestitures/shutdown", "description": "none found"},
      {"category": "funding/investment activity", "description": "none found since the 2020 H&F/TPG deal"}
    ],
    "retrievedDate": "2026-09-25"
  },
  {
    "supplier": "Veracode",
    "existingId": null,
    "legalName": "Veracode, Inc.",
    "publicOrPrivate": "private",
    "ticker": null,
    "secCik": null,
    "filerType": "none — does not file with the SEC",
    "fiscalYearEnd": "UNVERIFIED",
    "headquarters": "65 Blue Sky Drive, Burlington, MA",
    "companyUrl": "https://www.veracode.com",
    "investorRelationsUrl": null,
    "ownership": {
      "type": "PE-owned (majority: TA Associates)",
      "history": [
        {"event": "Thoma Bravo acquired Veracode from Broadcom (post CA Technologies acquisition)", "price": "$950 million cash", "announced": "2018-11-05", "closed": "2019-01-01", "sourceUrl": "search-result synthesis citing CRN and PE Hub reporting", "ladderRung": 5, "label": "reported/synthesized, not read directly from a primary Thoma Bravo/Broadcom press release this session"},
        {"event": "TA Associates took a majority growth-investment stake", "valuation": "$2.5 billion", "announced": "2022-03-15 (per Veracode's own press-release listing)", "closed": "reported elsewhere as completing around May 2022 — UNVERIFIED which date is operative", "sourceUrl": "https://www.veracode.com/newsroom/", "ladderRung": 4}
      ]
    },
    "privateFinancials": {
      "lastFundingRound": "N/A post-2022 — TA Associates deal above is the last ownership-changing transaction found",
      "companyStatedRevenueOrArr": "none found"
    },
    "ceo": "Brian Roche, appointed 2024-04-03",
    "cfo": "Simon Adell, appointed June 2025 — just outside the 12-month distress window",
    "acquisitionsMadeByVeracode": [
      {"target": "Phylum, Inc.", "date": "2025-01-06", "note": "outside the 12-month window"},
      {"target": "Longbow Security", "date": "2024-04-01", "note": "outside the 12-month window"},
      {"target": "Crashtest Security", "date": "2022-12-12", "note": "outside the 12-month window"}
    ],
    "distressAndChange12Months": [
      {"category": "layoffs", "description": "none found"},
      {"category": "WARN notice (Massachusetts)", "description": "none found — not separately queried against the MA WARN database directly"},
      {"category": "restructuring charges", "description": "none found (private company, no 8-K obligation)"},
      {"category": "debt raised/refinanced", "description": "none found"},
      {"category": "ratings actions", "description": "none found"},
      {"category": "going-concern language", "description": "none found"},
      {"category": "CFO appointment", "description": "Simon Adell named CFO", "date": "2025-06 (just before the 12-month window)", "sourceUrl": "https://www.veracode.com/newsroom/", "ladderRung": 1},
      {"category": "acquisitions made in window", "description": "none found (most recent, Phylum, was Jan 2025, before the window)"},
      {"category": "divestitures/shutdown", "description": "none found"}
    ],
    "retrievedDate": "2026-09-25"
  },
  {
    "supplier": "Semgrep",
    "existingId": null,
    "legalName": "Semgrep, Inc. (formerly r2c)",
    "publicOrPrivate": "private",
    "ticker": null,
    "secCik": null,
    "filerType": "none — does not file with the SEC",
    "fiscalYearEnd": "UNVERIFIED",
    "headquarters": "San Francisco, CA; founded 2017",
    "companyUrl": "https://semgrep.dev",
    "investorRelationsUrl": null,
    "ownership": {
      "type": "independent, VC-backed",
      "owner": "Lightspeed Venture Partners (led Series C), with Felicis Ventures, Redpoint Ventures, Sequoia Capital participating; no PE control stake found"
    },
    "privateFinancials": {
      "lastFundingRound": {
        "date": "2025-02-05",
        "round": "Series D",
        "amount": "$100 million",
        "leadInvestor": "Menlo Ventures",
        "otherInvestors": "Felicis Ventures, Harpoon Ventures, Lightspeed Venture Partners, Redpoint Ventures, Sequoia Capital",
        "totalRaisedToDate": "approximately $204 million",
        "sourceUrl": "https://siliconangle.com/2025/02/05/code-security-startup-semgrep-reels-100m-investors/",
        "corroboratingSourcesFound": ["finance.yahoo.com/news/semgrep-announces-100m-series-d-140000742.html", "pulse2.com/semgrep-application-security-company-raises-100-million-series-d/", "nasdaq.com/articles/application-security-startup-semgrep-locks-down-100m-series-d", "wsj.com/articles/semgrep-raises-100-million-to-develop-bug-hunting-software-4a8a63b9"],
        "ladderRung": 5,
        "label": "reported by SiliconANGLE and corroborated across multiple outlets, unconfirmed against a direct Semgrep primary-source release"
      },
      "priorRound": {"date": "2023-04-18", "round": "Series C", "amount": "$53 million", "leadInvestor": "Lightspeed Venture Partners", "sourceUrl": "https://techcrunch.com/2023/04/18/semgrep-formerly-r2c-lands-53m-investment-to-grow-code-security-platform/", "ladderRung": 5},
      "companyStatedRevenueOrArr": "NOT company-stated. Only third-party automated-estimate figures found ($33.6M per Latka/Growjo, 2025). UNVERIFIED."
    },
    "distressAndChange12Months": [
      {"category": "layoffs", "description": "none found"},
      {"category": "CEO/executive changes", "description": "none found — Isaac Evans remains listed as CEO"},
      {"category": "restructuring/debt/ratings/going-concern/divestitures/shutdown", "description": "none found across all categories checked"},
      {"category": "funding/investment", "description": "$100M Series D closed 2025-02-05 — predates the 12-month window (starts 2025-09-25); no round found inside the window"}
    ],
    "retrievedDate": "2026-09-25"
  },
  {
    "supplier": "JFrog Ltd.",
    "existingId": null,
    "legalName": "JFrog Ltd.",
    "publicOrPrivate": "public",
    "ticker": "FROG",
    "secCik": "0001800667",
    "filerType": "Domestic filer (10-K/10-Q/8-K) despite incorporation in Israel — confirmed by actual EDGAR filings",
    "fiscalYearEnd": "December 31",
    "headquarters": "270 E. Caribbean Drive, Sunnyvale, CA 94089 (also Israel operations); incorporated in Israel",
    "companyUrl": "https://jfrog.com",
    "investorRelationsUrl": "https://investors.jfrog.com",
    "ownership": {"type": "public company (Nasdaq: FROG)", "notes": "IPO 2020"},
    "publicFinancials": {
      "latestReportedQuarter": {
        "periodEnd": "2026-06-30",
        "releaseDate": "2026-08-06",
        "revenue": "$163.8 million",
        "yoyGrowth": "29%",
        "headlineMetricIfDifferent": {"metric": "Cloud revenue", "value": "$87.5 million", "yoyGrowth": "53%", "note": "53% of total revenue, up from 45% a year earlier"},
        "otherMetrics": {"nonGaapOperatingIncome": "$32.6 million (19.9% non-GAAP operating margin)", "netDollarRetention": "121% (trailing four quarters)", "customersOverOneMillionArr": "97, up 59% YoY"},
        "sourceUrl": "https://investors.jfrog.com/news/news-details/2026/JFrog-Announces-Second-Quarter-2026-Results/default.aspx",
        "ladderRung": 1
      },
      "priorQuarter": {"periodEnd": "2026-03-31", "releaseDate": "2026-05-07", "revenue": "$154.0 million", "yoyGrowth": "26%", "cloudRevenue": "$78.9 million", "cloudYoyGrowth": "50%", "sourceUrl": "https://investors.jfrog.com/news/news-details/2026/JFrog-Announces-First-Quarter-2026-Results/default.aspx", "ladderRung": 1},
      "nextExpectedReportDate": "Not yet announced as of 2026-09-25; inferred early November 2026 from historical cadence (Q3 2025 released 2025-11-06) — UNVERIFIED, not an announced date",
      "fy2026Guidance": {"revenue": "$648-652 million", "nonGaapOperatingIncome": "$116-120 million", "sourceUrl": "https://investors.jfrog.com/news/news-details/2026/JFrog-Announces-Second-Quarter-2026-Results/default.aspx", "ladderRung": 1}
    },
    "distressAndChange12Months": [
      {"category": "layoffs", "description": "none found"},
      {"category": "restructuring charges (8-K Item 2.05)", "description": "none found in 8-K filings reviewed"},
      {"category": "debt raised/refinanced", "description": "none found"},
      {"category": "ratings actions", "description": "none found"},
      {"category": "going-concern language", "description": "none found"},
      {"category": "CEO/CFO departures", "description": "none found. One board addition (non-executive): Sigal Zarmi appointed Class I director, effective 2025-11-01", "date": "2025-09-19 (8-K filing date)", "sourceUrl": "https://www.sec.gov/Archives/edgar/data/1800667/000119312525217487/frog-20250919.htm", "ladderRung": 1},
      {"category": "divestitures/shutdown", "description": "none found"},
      {"category": "capital allocation action (not distress)", "description": "Board approved a $300 million share repurchase program", "date": "2026-02-26", "sourceUrl": "https://www.sec.gov/Archives/edgar/data/1800667/000119312526073842/frog-20260226.htm", "ladderRung": 1},
      {"category": "acquisitions made", "description": "none found in window"}
    ],
    "retrievedDate": "2026-09-25"
  },
  {
    "supplier": "Sonatype",
    "existingId": null,
    "legalName": "Sonatype Inc.",
    "publicOrPrivate": "private",
    "ticker": null,
    "secCik": null,
    "filerType": "none — does not file with the SEC",
    "fiscalYearEnd": "UNVERIFIED",
    "headquarters": "8161 Maple Lawn Blvd #250, Fulton, MD 20759; additional offices London, Singapore, Hyderabad (India hub opened 2025-11-10)",
    "companyUrl": "https://www.sonatype.com",
    "investorRelationsUrl": null,
    "ownership": {
      "type": "PE-owned",
      "owner": "Vista Equity Partners (majority stake)",
      "dealDate": "2019-11-18",
      "dealDetail": "Vista Equity Partners acquired a majority stake; price not disclosed.",
      "sourceUrl": "https://www.sonatype.com/press-releases/vista-acquires-majority-interest-in-sonatype",
      "ladderRung": 1,
      "priorRound": {"event": "TPG-led $80 million minority investment", "date": "2018-09-07", "participants": "TPG (lead), Accel, Goldman Sachs Group, Hummer Winblad", "sourceUrl": "https://www.sonatype.com/press-releases/tpg-leads-80-million-investment-in-sonatype", "ladderRung": 1},
      "note": "TA Associates involvement was NOT found in Sonatype's own materials — an earlier project assumption conflating TA Associates with Sonatype appears incorrect (likely confused with Veracode's TA Associates deal)."
    },
    "privateFinancials": {
      "lastFundingRound": "N/A post-2019 — Vista deal above is the last ownership-changing transaction found",
      "companyStatedRevenueOrArr": "none found (company references an undated past \"Sonatype Exceeds $100M in ARR\" milestone — treat that date as UNVERIFIED)"
    },
    "ceo": "Bhagwat Swaroop, appointed 2025-07-29, succeeding founder E. Wayne Jackson III (moved to Executive Chairman)",
    "distressAndChange12Months": [
      {"category": "CEO transition", "description": "Wayne Jackson transitioned to Executive Chairman; Bhagwat Swaroop named CEO — a planned transition per the company", "date": "2025-07-29", "sourceUrl": "https://www.sonatype.com/press-releases/sonatype-appoints-bhagwat-swaroop-as-ceo", "ladderRung": 1, "note": "58 days before the window starts (2025-09-25) — context, not an in-window event"},
      {"category": "executive hires (additions, not departures)", "description": "Three new C-suite executives named: Casey Watson (CRO), Jason McClelland (CMO), Sherri Manning (CHRO)", "date": "2026-06-09", "sourceUrl": "https://www.sonatype.com/press-releases/sonatype-strengthens-leadership-team-for-ai-driven-growth", "ladderRung": 1},
      {"category": "layoffs", "description": "none found"},
      {"category": "WARN notice", "description": "none found"},
      {"category": "restructuring charges", "description": "none found (private company, no 8-K obligation)"},
      {"category": "debt raised/refinanced", "description": "none found"},
      {"category": "ratings actions", "description": "none found"},
      {"category": "going-concern language", "description": "none found"},
      {"category": "divestitures/shutdown", "description": "none found"},
      {"category": "acquisitions made", "description": "none found in window"}
    ],
    "retrievedDate": "2026-09-25"
  },
  {
    "supplier": "Chainguard",
    "existingId": null,
    "legalName": "Chainguard (legal suffix UNVERIFIED)",
    "publicOrPrivate": "private",
    "ticker": null,
    "secCik": null,
    "filerType": "none — does not file with the SEC",
    "fiscalYearEnd": "UNVERIFIED",
    "headquarters": "UNVERIFIED exact city (commonly reported as Kirkland, WA, not independently confirmed)",
    "companyUrl": "https://www.chainguard.dev",
    "investorRelationsUrl": null,
    "ownership": {
      "type": "independent, VC-backed",
      "owner": "General Catalyst's Customer Value Fund (lead, Oct 2025 growth round); Kleiner Perkins and IVP (co-led Apr 2025 Series D)",
      "founders": "Dan Lorenc (CEO), Ville Aikas, Matt Moore — all former Google employees"
    },
    "privateFinancials": {
      "lastFundingRound": {
        "date": "2025-10-23",
        "round": "Growth financing (no series letter disclosed)",
        "amount": "$280 million",
        "leadInvestor": "General Catalyst's Customer Value Fund",
        "totalRaisedToDate": "approximately $892 million",
        "sourceUrl": "https://siliconangle.com/2025/10/23/chainguard-secures-280m-expand-trusted-open-source-software-platform/",
        "ladderRung": 5,
        "label": "reported by SiliconANGLE, unconfirmed against a direct Chainguard primary-source release",
        "withinDistressWindow": true,
        "note": "Falls inside the 12-month window (starts 2025-09-25); supersedes the April 2025 Series D as the current last-round figure."
      },
      "priorRound": {"date": "2025-04 (day UNVERIFIED)", "round": "Series D", "amount": "$356 million", "leadInvestor": "Co-led by Kleiner Perkins and IVP", "valuation": "$3.5 billion", "sourceUrl": "https://www.forbes.com/companies/chainguard/", "ladderRung": 5},
      "companyStatedRevenueOrArr": "none found"
    },
    "distressAndChange12Months": [
      {"category": "layoffs", "description": "none found"},
      {"category": "CEO/executive departures", "description": "none found — Dan Lorenc remains CEO"},
      {"category": "acquisitions made", "description": "none found in window"},
      {"category": "restructuring/debt/ratings/going-concern/divestitures/shutdown", "description": "none found across all categories checked"},
      {"category": "funding/investment", "description": "$280 million growth financing closed 2025-10-23 — a positive event inside the window, not distress", "date": "2025-10-23", "sourceUrl": "https://siliconangle.com/2025/10/23/chainguard-secures-280m-expand-trusted-open-source-software-platform/", "ladderRung": 5}
    ],
    "retrievedDate": "2026-09-25"
  },
  {
    "supplier": "GitHub Advanced Security",
    "existingId": null,
    "legalName": "GitHub, Inc. (wholly owned subsidiary of Microsoft Corporation); GitHub Advanced Security is a product line, not a separate legal entity",
    "publicOrPrivate": "segment inside a public company",
    "ticker": "MSFT",
    "secCik": "0000789019",
    "filerType": "Domestic filer (10-K/10-Q/8-K) — Microsoft Corporation",
    "fiscalYearEnd": "June 30",
    "investorRelationsUrl": "https://www.microsoft.com/en-us/investor/default",
    "segmentDisclosureNote": "Confirmed directly against Microsoft's FY2026 10-K (filed 2026-07-29): GitHub is part of the 'Server products and cloud services' component of the Intelligent Cloud segment, with GitHub cloud services revenue folded into 'Azure and other cloud services.' No standalone GitHub or GHAS revenue is disclosed.",
    "sourceUrl": "https://www.sec.gov/Archives/edgar/data/789019/000119312526323660/msft-20260630.htm",
    "ladderRungForSegmentClaim": 1,
    "productRestructuringNote": {
      "description": "GHAS is currently sold as separate modular add-on SKUs — 'GitHub Secret Protection' and 'GitHub Code Security' — rather than as a single bundled 'Advanced Security' product",
      "sourceUrl": "https://github.com/pricing",
      "ladderRung": 1,
      "dateOfChange": "UNVERIFIED"
    },
    "distressAndChange12Months": [
      {
        "category": "CEO/leadership departure (GitHub, not Microsoft overall)",
        "description": "GitHub CEO Thomas Dohmke announced he was stepping down to become a founder again; no successor CEO named — GitHub's leadership folded further into Microsoft's CoreAI organization",
        "announcementDate": "2025-08-11",
        "effectiveDate": "through end of 2025",
        "sourceUrl": "https://github.blog/news-insights/company-news/goodbye-github/",
        "ladderRung": 1,
        "note": "Announcement is 45 days before the window starts (2025-09-25); the completion (end of 2025) falls inside the window."
      },
      {"category": "layoffs (GitHub-specific)", "description": "none found in this session's searches"},
      {"category": "restructuring charges (Microsoft-wide, GitHub-specific portion not broken out)", "description": "not checked at the Microsoft-wide level — out of scope for a GitHub-specific record; UNVERIFIED"},
      {"category": "divestitures/shutdown", "description": "none found"},
      {"category": "GHAS pricing/product restructuring", "description": "see productRestructuringNote above", "sourceUrl": "https://github.com/pricing", "ladderRung": 1}
    ],
    "retrievedDate": "2026-09-25"
  }
]
```

### 2.3 Considered and left out

All eight candidates named in the assignment were kept — this exceeds the suggested 4-7 deliberately:

- **GitHub Advanced Security** was kept despite being a segment, not a company: it is the highest-distribution
  SAST/secret-scanning product in the market by footprint (every GitHub repo), and it carried genuine news this
  window (the Dohmke departure and CoreAI reorganization).
- **Chainguard** sells hardened base images and build provenance — closer to the "software supply chain" half of the
  domain than the "application testing" half. Kept because the domain definition explicitly includes CI/CD
  supply-chain security, and dropping it would leave that side of the table represented only by JFrog and Sonatype.
- No candidate was dropped. If a ninth name were added under this domain definition, the two most likely candidates a
  security leader would ask about are **Endor Labs** (reachability-based SCA) and **Docker** (its 2026 move into free
  hardened images competes directly with Chainguard) — neither was researched, since they were outside the assigned
  candidate list.

### 2.4 Known gaps to verify before publication

- **Checkmarx's 2020 deal** terms were reconstructed from search-result summaries, not read directly from a primary
  press release — confirm before publishing as fact.
- **Snyk's Business Insider article** (employee share markdown) could not be fetched directly; figures come from a
  search-result summary only. This is the weakest-sourced and most consequential distress signal in this domain —
  re-verify via an alternate route before use.
- **Snyk's CEO transition date** has no confirmed date or Snyk-issued primary source.
- Several "none found" layoff/WARN checks used aggregated news search rather than querying individual state WARN
  databases directly — a true rung-3 WARN check was not performed for any private company in this file.
- Semgrep's and Chainguard's funding rounds were corrected mid-research after a cross-check found each record had
  stopped at an older round; both corrections are labeled inline above.

---

## 3. OT and IoT security

All six originally suggested candidates were retained — Claroty, Dragos, Nozomi Networks, Armis, Forescout, Xage
Security.

### 3.1 Summary table

| Supplier | Public/Private | Latest footing figure | Last round / ownership | Distress items (one-line) |
|---|---|---|---|---|
| Claroty | Private | Company-stated "hundreds of millions" ARR (exact figure undisclosed), Jan 2026 | $150M round, Jan 22 2026, led by Golub Growth, $3B valuation | None found — company reported it "expects to become profitable" |
| Dragos, Inc. | Private, majority stake being acquired by Accenture plc (NYSE: ACN) | UNVERIFIED (no standalone revenue figure found) | Accenture agreement to acquire majority stake, announced ~June 18 2026, deal (with runZero/NetRise) reported at ~$4.1-4.2B combined enterprise value | Ownership change (majority stake sale), not distress; no layoffs/restructuring found |
| Nozomi Networks, Inc. | Private | UNVERIFIED (no disclosed revenue/ARR figure found) | No new funding round found in the last 12 months; last known financing activity (Form D) was 2021 | None found |
| Armis Security Ltd. | Was private; acquired by ServiceNow, Inc. (NYSE: NOW), deal closed April 20, 2026 | Now a ServiceNow subsidiary; ServiceNow guided ~125bps of FY26 subscription revenue growth contribution from Armis (SEC-filed) | Acquired by ServiceNow — announced ~Dec 2025, closed April 20, 2026 | Acquisition (ownership change, not distress); ServiceNow guided integration headwinds to FY26 margins |
| Forescout Technologies, Inc. | Private, PE-owned | UNVERIFIED (no disclosed revenue figure found) | Co-owned by Advent International and Crosspoint Capital Partners; Advent take-private deal closed 2020 | None found |
| Xage Security, Inc. | Private | Company-stated 81% YoY revenue growth, 102% YoY customer growth, as of March 18 2026 (unaudited) | $15M equity round led by Piva Capital, closed December 2025 | None found |

### 3.2 Full records (JSON)

```json
[
  {
    "supplierName": "Claroty Ltd. (operating as Claroty)",
    "existingId": null,
    "publicPrivate": "private",
    "ticker": null,
    "secCik": null,
    "secCikNote": "No CIK found for the Claroty operating company via SEC EDGAR full-text search on 2026-09-25. Only related investor-fund vehicles were found (e.g. Team8 - Claroty, L.P., CIK 0001754014), not the issuer.",
    "filerType": "not an SEC reporting company",
    "fiscalYearEnd": "UNVERIFIED",
    "investorRelationsUrl": "https://claroty.com/newsroom",
    "ownership": {
      "status": "independent, private (venture-backed)",
      "notes": "Founded 2015 (Galina Antova, Amir Zilberstein, Benny Porat). Israel-headquartered. No PE ownership or acquisition found."
    },
    "latestFunding": {
      "date": "2026-01-22",
      "roundType": "growth equity",
      "amount": "$150,000,000",
      "leadInvestor": "Golub Growth (Golub Capital's growth-equity arm)",
      "postMoneyValuation": "$3,000,000,000 (reported as an ~80% increase from Claroty's prior valuation)",
      "sourceUrl": "https://siliconangle.com/2026/01/22/industrial-cybersecurity-startup-claroty-nabs-150m-funding-round/",
      "ladderRung": 5,
      "notes": "Trade press (SiliconANGLE, citing Calcalist), not a Claroty or Golub press release directly located. Article states Claroty 'expects to become profitable in the near future.' Revenue described only as 'hundreds of millions of dollars,' no exact figure given."
    },
    "companyStatedRevenue": {
      "figure": "hundreds of millions of dollars in annual revenue (no exact number disclosed)",
      "asOfDate": "2026-01-22",
      "label": "company-stated/unaudited",
      "sourceUrl": "https://siliconangle.com/2026/01/22/industrial-cybersecurity-startup-claroty-nabs-150m-funding-round/",
      "ladderRung": 5
    },
    "distressLast12Months": {
      "windowStart": "2025-09-25",
      "layoffs": "none found",
      "restructuringCharges": "none found; private, does not file 8-K Item 2.05",
      "debtRaisedOrRefinanced": "none found beyond the Jan 2026 equity round above",
      "ratingsActions": "not applicable — no public credit rating found",
      "goingConcernLanguage": "none found",
      "ceoCfoDepartures": "UNVERIFIED — could not confirm current CEO/CFO names via search this session",
      "divestitures": "none found",
      "shutdown": "none found"
    },
    "retrievedDate": "2026-09-25"
  },
  {
    "supplierName": "Dragos, Inc.",
    "existingId": null,
    "publicPrivate": "private (majority stake subject to acquisition by Accenture plc, NYSE: ACN)",
    "ticker": null,
    "secCik": "0001686560",
    "secCikNote": "Confirmed via data.sec.gov. Entity 'DRAGOS, INC.', Maryland-registered address, Delaware incorporation, fiscal year end 12/31.",
    "filerType": "Form D filer only (2016, 2017, 2018, 2019) — not an SEC reporting company",
    "fiscalYearEnd": "12/31",
    "investorRelationsUrl": "https://www.dragos.com/newsroom/",
    "ownership": {
      "status": "transitioning from independent private to Accenture-majority-owned",
      "acquirer": "Accenture plc (NYSE: ACN)",
      "dateAnnounced": "2026-06-18, per Accenture's own Q3 FY2026 earnings 8-K exhibit (accession 0001467373-26-000031): 'Our agreement to acquire a majority stake in Dragos and all of runZero and NetRise...'",
      "dateClosed": "Reported closing around August/September 2026 per trade press; not independently confirmed in an Accenture SEC filing this session — UNVERIFIED exact date, ladder rung 5 for the close date specifically",
      "priceDisclosed": "Combined enterprise value across Dragos (majority stake) + runZero (100%) + NetRise (100%) reported at approximately $4.1-4.2 billion by trade press; Dragos's own value within that reported at $3.25-3.3 billion. Accenture's own SEC exhibit confirms the deal's existence/scope (rung 1) but not the dollar price; price figures are rung 5.",
      "notes": "Dragos CEO Robert M. Lee reported to continue as CEO and become Chairman (rung 5). Combined Dragos+runZero+NetRise reported ARR ~$208M with 53% YoY growth as of June 2026 (rung 5)."
    },
    "latestFunding": null,
    "companyStatedRevenue": {
      "figure": "UNVERIFIED — no Dragos-only revenue/ARR figure found; only the combined Dragos+runZero+NetRise ~$208M ARR figure (rung 5)",
      "asOfDate": "2026-06",
      "label": "reported/unconfirmed (trade press)",
      "sourceUrl": "https://www.helpnetsecurity.com/2026/06/19/accenture-dragos-runzero-netrise-acquisition/",
      "ladderRung": 5
    },
    "distressLast12Months": {
      "windowStart": "2025-09-25",
      "layoffs": "none found",
      "restructuringCharges": "none found",
      "debtRaisedOrRefinanced": "none found at the Dragos level",
      "ratingsActions": "none found",
      "goingConcernLanguage": "none found",
      "ceoCfoDepartures": "none found — CEO Robert M. Lee reported to continue as CEO/become Chairman post-deal (rung 5)",
      "divestitures": "none found",
      "shutdown": "none found",
      "other": "Dragos itself made three acquisitions in this window: Phosphorus (closed ~June 1 2026, rung 5, price undisclosed), runZero and NetRise (100% acquisitions, completed ~September 2026, rung 5, prices undisclosed)."
    },
    "retrievedDate": "2026-09-25"
  },
  {
    "supplierName": "Nozomi Networks, Inc.",
    "existingId": null,
    "publicPrivate": "private",
    "ticker": null,
    "secCik": "0001689366",
    "secCikNote": "Confirmed via data.sec.gov. Address 575 Market Street, Suite 3650, San Francisco, CA; Delaware incorporation; fiscal year end 12/31.",
    "filerType": "Form D filer only (2016, 2017, 2018, 2021 x2; most recent 2021-12-03) — not an SEC reporting company",
    "fiscalYearEnd": "12/31",
    "investorRelationsUrl": "https://www.nozominetworks.com/company/leadership",
    "ownership": {
      "status": "independent, private (venture-backed)",
      "notes": "No ownership change found in the last 12 months."
    },
    "latestFunding": {
      "date": "UNVERIFIED — most recent primary-source (Form D) financing event found is 2021-12-03; no funding round in the last 12 months located",
      "sourceUrl": "https://data.sec.gov/submissions/CIK0001689366.json",
      "ladderRung": 1,
      "notes": "News search returned only product/award/partnership announcements (Gartner Magic Quadrant leader, Vantage IQ AI assistant launch Jan 2026, Google Cloud Marketplace availability, Nozomi Compass launch Sept 2026); no funding, revenue, or leadership-change coverage surfaced."
    },
    "companyStatedRevenue": {"figure": "UNVERIFIED — none found", "ladderRung": null},
    "distressLast12Months": {
      "windowStart": "2025-09-25",
      "layoffs": "none found",
      "restructuringCharges": "none found",
      "debtRaisedOrRefinanced": "none found",
      "ratingsActions": "none found",
      "goingConcernLanguage": "none found",
      "ceoCfoDepartures": "none found — current leadership per company site: CEO Andrea Carcano (co-founder), CTO Moreno Carullo (co-founder), CFO George Todd, CRO Kevin Isaac",
      "divestitures": "none found",
      "shutdown": "none found"
    },
    "retrievedDate": "2026-09-25"
  },
  {
    "supplierName": "Armis Security Ltd.",
    "existingId": null,
    "publicPrivate": "was private; now a wholly owned subsidiary of ServiceNow, Inc. (NYSE: NOW) as of April 20, 2026",
    "ticker": null,
    "secCik": null,
    "secCikNote": "No SEC CIK found for Armis itself via EDGAR full-text search; the only 'Armis' entities on EDGAR are unrelated (Armis Biopharma, Armis Advisers LLC).",
    "filerType": "not an SEC reporting company in its own right; now consolidated into ServiceNow, Inc.'s SEC filings (CIK 0001373715)",
    "fiscalYearEnd": "UNVERIFIED for Armis standalone; ServiceNow's fiscal year end is 12/31",
    "investorRelationsUrl": "https://www.servicenow.com/company/media/press-room.html (Armis now marketed as 'Armis from ServiceNow')",
    "ownership": {
      "status": "acquired",
      "acquirer": "ServiceNow, Inc. (NYSE: NOW)",
      "dateAnnounced": "ServiceNow's own Q4 FY2025 earnings 8-K exhibit (filed 2026-01-28) states intent to acquire Armis, expected to close in H2 2026; trade press separately reports the original announcement as December 2025.",
      "dateClosed": "2026-04-20 — confirmed via ServiceNow's own Q1 FY2026 earnings 8-K exhibit (filed 2026-04-22): 'ServiceNow closed its acquisition of Armis on April 20, 2026.' Ladder rung 1.",
      "priceDisclosed": "Not stated in the ServiceNow SEC exhibits retrieved. ServiceNow's 8-K (filed 2026-04-22) discloses a $4 billion unsecured Term Loan Credit Agreement, proceeds partly used to finance the Armis acquisition (rung 1). Trade press (rung 5) reports total deal value at approximately $7.75 billion.",
      "notes": "ServiceNow's Q1 FY2026 earnings exhibit discloses forward guidance: Armis expected to contribute ~125bps to Q2/FY2026 subscription revenue growth, with integration headwinds of ~25bps to subscription gross margin, ~75bps to operating margin, ~200bps to free cash flow margin (all rung 1)."
    },
    "latestFunding": null,
    "companyStatedRevenue": {
      "figure": "No standalone Armis revenue figure disclosed; see ServiceNow guidance impact figures above",
      "asOfDate": "2026-04-22",
      "label": "primary source (ServiceNow SEC filing) but no standalone Armis dollar figure given",
      "sourceUrl": "https://www.sec.gov/Archives/edgar/data/1373715/000137371526000054/erq1fy26.htm",
      "ladderRung": 1
    },
    "distressLast12Months": {
      "windowStart": "2025-09-25",
      "layoffs": "none found",
      "restructuringCharges": "not applicable at the Armis level; ServiceNow disclosed integration-related margin headwinds, not a distress signal at Armis",
      "debtRaisedOrRefinanced": "ServiceNow (acquirer) raised a $4B term loan (2026-04-17) and $3B revolving credit facility (2026-04-01) around the deal — the acquirer's balance sheet action, not Armis's",
      "ratingsActions": "none found for Armis specifically",
      "goingConcernLanguage": "none found",
      "ceoCfoDepartures": "UNVERIFIED — could not confirm whether Armis co-founder/CEO Nadir Izrael remains in an operating role post-acquisition",
      "divestitures": "none found",
      "shutdown": "none found",
      "other": "Post-acquisition, Armis reported (rung 5) to be the technical basis for six new ServiceNow autonomous security products announced alongside Veza (another ServiceNow acquisition, closed 2026-03-02 per SEC filing, rung 1)."
    },
    "retrievedDate": "2026-09-25"
  },
  {
    "supplierName": "Forescout Technologies, Inc.",
    "existingId": null,
    "publicPrivate": "private, PE-owned",
    "ticker": null,
    "secCik": "0001145057",
    "secCikNote": "This CIK is from Forescout's prior life as a public company (IPO 2017; NASDAQ: FSCT). Deregistered following its 2020 take-private; exact Form 15 deregistration date not confirmed this session.",
    "filerType": "formerly domestic 10-K/10-Q filer (2017-2020); not currently an SEC reporting company",
    "fiscalYearEnd": "UNVERIFIED (historically 12/31 as a public company)",
    "investorRelationsUrl": "https://www.forescout.com/company/leadership/",
    "ownership": {
      "status": "PE-owned",
      "peOwner": "Advent International (co-owner) and Crosspoint Capital Partners (co-owner) — both named on Forescout's own leadership page as of 2026-09-25",
      "dateOfDeal": "Advent International's original take-private acquisition closed 2020 (via tender offer, per SEC EDGAR SC TO-T/A filings, filed 2020-08-17). Timing of Crosspoint's addition as co-owner NOT independently dated this session.",
      "notes": "CEO Barry Mainz also holds the title of Operating Partner at Crosspoint Capital Partners per Forescout's own leadership page — the clearest signal of the Crosspoint relationship found."
    },
    "latestFunding": null,
    "companyStatedRevenue": {"figure": "UNVERIFIED — no revenue or ARR figure found this session", "ladderRung": null},
    "distressLast12Months": {
      "windowStart": "2025-09-25",
      "layoffs": "none found",
      "restructuringCharges": "none found; not applicable (private, no 8-K Item 2.05 filer)",
      "debtRaisedOrRefinanced": "none found",
      "ratingsActions": "none found",
      "goingConcernLanguage": "none found",
      "ceoCfoDepartures": "none found — current leadership per company site: CEO Barry Mainz, CFO Rob Gillespie, CRO Rob Amezcua, CPO Paul Kao, CMO Clarissa Horowitz, CLO Edward Brown, CIO Sloane Stricker",
      "divestitures": "none found",
      "shutdown": "none found"
    },
    "retrievedDate": "2026-09-25"
  },
  {
    "supplierName": "Xage Security, Inc.",
    "existingId": null,
    "publicPrivate": "private",
    "ticker": null,
    "secCik": "0001749043",
    "secCikNote": "Confirmed via SEC EDGAR. Address 445 Sherman Avenue, Suite 200, Palo Alto, CA; Delaware incorporation; fiscal year end 12/31.",
    "filerType": "Form D filer only (2018, 2018 amendment, 2021, 2023, and most recent 2026-03-18) — not an SEC reporting company",
    "fiscalYearEnd": "12/31",
    "investorRelationsUrl": "https://xage.com/newsroom/ (leadership page returned 403 Forbidden this session)",
    "ownership": {
      "status": "independent, private (venture-backed)",
      "notes": "No ownership change found in the last 12 months."
    },
    "latestFunding": {
      "date": "2025-12 (within the last 12 months)",
      "roundType": "equity financing",
      "amount": "$15,000,000",
      "leadInvestor": "Piva Capital",
      "valuationDisclosed": "not disclosed",
      "sourceUrl": "https://finance.yahoo.com/news/xage-security-hits-record-growth-120000615.html",
      "ladderRung": 5,
      "notes": "Trade-press-relayed company press release (dated 2026-03-18). The SEC Form D filed 2026-03-18 (rung 1) is dated the same day, consistent with — but not confirming the exact amount of — a Reg D raise around this period; the Form D primary document itself was not individually opened this session."
    },
    "companyStatedRevenue": {
      "figure": "81% year-over-year revenue growth; 102% year-over-year customer growth; also '50% rise in net new revenue between Q3 and Q4 2025' and 'over 100% increase from Q4 2025 into Q1 2026' in net-new revenue",
      "asOfDate": "2026-03-18",
      "label": "company-stated/unaudited (no absolute revenue dollar figure disclosed, only growth percentages)",
      "sourceUrl": "https://finance.yahoo.com/news/xage-security-hits-record-growth-120000615.html",
      "ladderRung": 5
    },
    "distressLast12Months": {
      "windowStart": "2025-09-25",
      "layoffs": "none found",
      "restructuringCharges": "none found",
      "debtRaisedOrRefinanced": "none found beyond the Dec 2025 equity round above",
      "ratingsActions": "none found",
      "goingConcernLanguage": "none found",
      "ceoCfoDepartures": "none found — CEO Duncan Greatwood quoted in multiple 2026 press releases in an ongoing capacity, most recently 2026-08",
      "divestitures": "none found",
      "shutdown": "none found"
    },
    "retrievedDate": "2026-09-25"
  }
]
```

### 3.3 Considered and left out

- No candidate was dropped from the original six.
- **Material change, not a drop:** Armis is no longer independent — acquired by ServiceNow (announced ~Dec 2025,
  closed April 20, 2026, confirmed via ServiceNow's own SEC filings). Kept in the roster (now marketed as "Armis from
  ServiceNow") since it remains a name a security leader would recognize; its ownership fields changed fundamentally.
- **Material change, not a drop:** Dragos is in the process of having a majority stake acquired by Accenture
  (announced June 18, 2026 per Accenture's own SEC-filed earnings exhibit). Dragos also itself acquired Phosphorus,
  runZero, and NetRise in the same window. Left in the roster since Accenture stated Dragos will operate as an
  independent business unit under current leadership.
- No additional candidate was added. Tenable.ot, Microsoft Defender for IoT, and Cisco Cyber Vision were considered
  but excluded because each sits inside a larger platform rather than being a standalone OT/IoT-focused supplier
  comparable to the six above.

### 3.4 Notable data gaps

- No standalone revenue/ARR figure was found for Dragos, Nozomi Networks, or Forescout this session.
- Forescout's exact date of Crosspoint Capital Partners joining as a co-owner is unverified.
- Claroty's and Armis's current CEO names/operating status were not independently re-confirmed this session.
- Exact closing date of the Dragos majority-stake sale to Accenture is unverified (only "around August/September
  2026" per trade press).
- No WARN Act database was queried directly this session; all "none found" layoff determinations rest on web/news
  search returning no coverage, not a WARN registry check.
- SEC EDGAR's browse-edgar company-search tool was down for large portions of this session, so additional non-Form-D
  filings (e.g. a possible Forescout Form 15 deregistration) may exist but were not checked.

---

## 4. AI security

All nine candidates named in the brief were kept — no candidate dropped or added (see 4.3).

### 4.1 Summary table

| Supplier | Public/Private | Latest footing figure | Last round / ownership | Distress (last 12 mo) one-liner |
|---|---|---|---|---|
| Palo Alto Networks — Prisma AIRS | Public (PANW); AI security is a product line, not a reported segment | FY2026 (ended 7/31/26) total revenue $11.48B, +24.5% YoY; Q4 FY26 $3.41B, +34% YoY; Next-Gen Security ARR $9.10B, +63% YoY (company headline metric, not Prisma-AIRS-specific) | N/A — internal product line | None found for PANW itself in the window |
| Protect AI | Was private; acquired by Palo Alto Networks | N/A — folded into PANW, no standalone disclosure | Acquired: announced 4/27/2025, closed ~7/22/2025, $700.0M cash + replacement awards | Acquired; last independent financing was an $80.8M equity round (SEC Form D), first sale 7/31/2024 |
| CalypsoAI | Was private; acquired by F5, Inc. | N/A — folded into F5's AI Guardrails / ADSP line | Acquired: announced 9/11/2025, closed September 2025, $180 million cash | Acquired; last funding round before acquisition UNVERIFIED |
| SurePath AI | Was private; acquired by F5, Inc. | N/A — folded into F5 AI Security Platform | Acquired: closed 6/15/2026, $50.1 million, $39.1M goodwill, "immaterial" to F5 results | Acquired; last independent financing was $5.2M equity round, first sale 5/24/2024 |
| Lakera | Was private; acquired by Check Point Software Technologies | N/A — folds into Check Point's AI Security Center of Excellence | Acquired: announced 9/16/2025, closed Q4 2025, ~$190 million net cash consideration | Acquired; last funding round before acquisition UNVERIFIED |
| Zenity | Private | Company-stated: "tripled revenue in each of the past two years," on track to triple again in 2026 (unaudited, 8/3/2026) | Series C, $125M, 8/3/2026, led by Norwest | None found in company's own newsroom for layoffs, exec departures, or restructuring |
| WitnessAI | Private | Company-stated: "500% ARR growth ... in the past 12 months," headcount up 5x (as of 1/13/2026) | $58M strategic round, 1/13/2026, led by Sound Ventures | None found in company's own site for layoffs, exec departures, or restructuring |
| HiddenLayer | Private | Company-stated: ARR "grew more than 10x year-over-year," 50+ new platform customers (as of 9/2/2026) | Series B, $100M, 9/2/2026, led by Delta-v Capital | None found in company's own newsroom |
| Robust Intelligence | Was private; acquired by Cisco Systems | N/A — folded into Cisco AI Defense | Acquired: closed in Cisco's Q1 FY2025 (quarter ended 10/26/2024); announcement date and price UNVERIFIED | Acquired; Cisco itself announced up to $1B restructuring on 5/13/2026 to fund reinvestment in "silicon, optics, security and AI" — a Cisco-wide charge, not Robust Intelligence-specific |

### 4.2 Full records (JSON)

```json
[
  {
    "supplierName": "Palo Alto Networks — Prisma AIRS",
    "existingId": "print-panw-cloud",
    "legalName": "Palo Alto Networks, Inc.",
    "publicPrivate": "public",
    "ticker": "PANW",
    "secCik": "0001327567",
    "filerType": "domestic large accelerated filer, 10-K/10-Q",
    "fiscalYearEnd": "July 31",
    "investorRelationsUrl": "https://investors.paloaltonetworks.com",
    "isSegmentOrProductLine": true,
    "segmentNote": "Prisma AIRS is a product line within Palo Alto Networks' Network & AI Security offerings, not a separately reported financial segment. PANW's own headline AI/next-gen-security metric is company-wide 'Next-Gen Security ARR' ($9.10B, +63% YoY, Q4 FY2026), not broken out to Prisma AIRS specifically.",
    "ownership": {"type": "independent (part of public company)"},
    "publicFinancials": {
      "latestQuarter": {
        "periodEnd": "2026-07-31",
        "releaseDate": "2026-09-01",
        "totalRevenue": "$3.41 billion (Q4 FY2026)",
        "yoyGrowth": "34%",
        "fullYearRevenue": "$11.48 billion (FY2026)",
        "fullYearYoyGrowth": "24.5%",
        "headlineMetric": "Next-Gen Security ARR $9.10 billion, +63% YoY (company-wide, not Prisma-AIRS-specific)",
        "sourceUrl": "https://www.sec.gov/Archives/edgar/data/1327567/000132756726000019/ex991q426earningsrelease.htm"
      },
      "priorQuarter": {"periodEnd": "2026-04-30", "totalRevenue": "$3.002 billion (Q3 FY2026)", "yoyGrowth": "31.1%", "sourceUrl": "https://www.sec.gov/Archives/edgar/data/1327567/000132756726000015/panw-20260430.htm"},
      "nextExpectedReportDate": "Not yet announced (Q1 FY2027, period ending ~10/31/2026, historically reported late November)"
    },
    "distressLast12Months": {
      "windowStart": "2025-09-25",
      "layoffsWarn": "none found",
      "restructuringCharges8K205": "none found (EDGAR full-text search of PANW 8-Ks for Item 2.05 in the window returned zero results)",
      "goingConcernLanguage": "not applicable, large accelerated filer with no going-concern doubt",
      "ceoCfoDepartures": "none found — Item 5.02 8-Ks in the window covered a board director retirement (Mary Pat McCarthy, effective 1/23/2026), a new director appointment, routine annual-meeting elections, and an executive change-in-control/severance policy approved 8/20/2026 — none are a CEO or CFO departure",
      "divestitures": "none found"
    },
    "notes": "Prisma AIRS description per PANW's own FY2026 10-K: 'a comprehensive AI security platform designed to help organizations discover, assess, and protect AI agents, applications, models and data across the AI lifecycle,' integrating AI Gateway, Agent Security, AI Red Teaming, AI Runtime Security, AI Model Security, and AI Posture Management.",
    "retrievedDate": "2026-09-25"
  },
  {
    "supplierName": "Protect AI",
    "existingId": "print-protect-ai",
    "legalName": "Protect AI, Inc.",
    "publicPrivate": "was private; now a wholly owned subsidiary/product line of Palo Alto Networks, Inc. (PANW)",
    "ticker": null,
    "secCik": "0002034085 (Form D filer only, pre-acquisition)",
    "filerType": "not an SEC reporting company; filed Form D as a private issuer",
    "ownership": {
      "type": "acquired",
      "acquirer": "Palo Alto Networks, Inc. (PANW)",
      "dateAnnounced": "2025-04-27",
      "dateClosed": "2025-07 (specifically ~2025-07-22, per PANW's XBRL tagging; PANW's FY2025 10-K states the acquisition completed 'in July 2025')",
      "priceDisclosed": "$700.0 million in cash and replacement awards, subject to adjustment",
      "sourceUrls": ["https://www.sec.gov/Archives/edgar/data/1327567/000132756725000017/panw-20250430.htm", "https://www.sec.gov/Archives/edgar/data/1327567/000132756725000027/panw-20250731.htm"]
    },
    "privateFinancingsBeforeAcquisition": {
      "lastRound": {"date": "2024-07-31 (first sale); Form D filed 2024-08-15", "amountRaised": "$80,795,490 (total sold, per SEC Form D)", "securityType": "equity", "leadInvestor": "not disclosed in Form D (18 accredited investors)", "sourceUrl": "https://www.sec.gov/Archives/edgar/data/2034085/000203360824000002/primary_doc.xml"},
      "companyStatedRevenueArr": "none found"
    },
    "distressLast12Months": {"windowStart": "2025-09-25", "layoffsWarn": "none found; company no longer files independently", "ceoCfoDepartures": "not checked — founder/CEO was Ian Swanson per Form D signatory; post-acquisition status not verified"},
    "retrievedDate": "2026-09-25"
  },
  {
    "supplierName": "CalypsoAI",
    "existingId": "print-calypsoai",
    "legalName": "CalypsoAI Corp.",
    "publicPrivate": "was private; now integrated into F5, Inc. (FFIV)",
    "ticker": null,
    "secCik": "UNVERIFIED — no Form D found under 'CalypsoAI Corp' or 'Calypso AI' in EDGAR full-text search",
    "filerType": "not an SEC reporting company",
    "ownership": {
      "type": "acquired",
      "acquirer": "F5, Inc. (FFIV)",
      "dateAnnounced": "2025-09-11",
      "dateClosed": "September 2025 (F5's FY2025 10-K, period ended 9/30/2025: 'In September 2025, we completed the acquisition of CalypsoAI Corp.')",
      "priceDisclosed": "$180 million in purchase consideration, financed primarily with cash",
      "sourceUrls": ["https://www.sec.gov/Archives/edgar/data/1048695/000104869525000143/ex991-item7019112025.htm", "https://www.sec.gov/Archives/edgar/data/1048695/000104869525000157/ffiv-20250930.htm"]
    },
    "privateFinancingsBeforeAcquisition": {
      "lastRound": "UNVERIFIED — no SEC Form D found; general web search and Wayback Machine were unreachable this session, so trade-press funding history could not be confirmed against a primary or labeled-secondary source. No figure stated.",
      "companyStatedRevenueArr": "none found"
    },
    "distressLast12Months": {"windowStart": "2025-09-25", "layoffsWarn": "none found; company no longer files independently", "ceoCfoDepartures": "not checked"},
    "retrievedDate": "2026-09-25"
  },
  {
    "supplierName": "SurePath AI",
    "existingId": "print-surepath",
    "legalName": "SurePath AI, Inc.",
    "publicPrivate": "was private; now integrated into F5, Inc. (FFIV)",
    "ticker": null,
    "secCik": "0002030853 (Form D filer only, pre-acquisition)",
    "filerType": "not an SEC reporting company; filed Form D, incorporated Delaware, HQ Denver, CO",
    "ownership": {
      "type": "acquired",
      "acquirer": "F5, Inc. (FFIV)",
      "dateAnnounced": "UNVERIFIED exact date (not separately disclosed in the F5 10-Q reviewed)",
      "dateClosed": "2026-06-15",
      "priceDisclosed": "$50.1 million; $39.1 million of goodwill recorded; F5 states 'immaterial' impact on operating results",
      "sourceUrl": "https://www.sec.gov/Archives/edgar/data/1048695/000104869526000067/ffiv-20260630.htm"
    },
    "privateFinancingsBeforeAcquisition": {
      "lastRound": {"date": "2024-05-24 (first sale); Form D filed 2024-08-27", "amountRaised": "$5,200,000", "securityType": "equity", "investors": "3 accredited investors", "executives": "Casey Bleeker (CEO), Randall Edgar Birdsall (Director), Andrew Loughlin (Director)", "sourceUrl": "https://www.sec.gov/Archives/edgar/data/2030853/000203085324000002/primary_doc.xml"},
      "companyStatedRevenueArr": "none found"
    },
    "distressLast12Months": {"windowStart": "2025-09-25", "layoffsWarn": "none found; company no longer files independently", "ceoCfoDepartures": "not checked"},
    "retrievedDate": "2026-09-25"
  },
  {
    "supplierName": "Lakera",
    "existingId": "print-lakera",
    "legalName": "Lakera AI (Lakera)",
    "publicPrivate": "was private; now integrated into Check Point Software Technologies Ltd (CHKP)",
    "ticker": null,
    "secCik": "UNVERIFIED — no Form D found under 'Lakera' (plausible: a Swiss company, may not have filed U.S. Reg D)",
    "filerType": "not an SEC reporting company",
    "ownership": {
      "type": "acquired",
      "acquirer": "Check Point Software Technologies Ltd (CHKP)",
      "dateAnnounced": "2025-09-16",
      "dateClosed": "Q4 2025 (Check Point's own FY2025 earnings 6-K: 'During the fourth quarter of 2025 we completed the acquisition of Lakera AI for approximately $190 million net cash consideration')",
      "priceDisclosed": "~$190 million net cash consideration",
      "sourceUrls": ["https://www.sec.gov/Archives/edgar/data/1015922/000117891325003335/exhibit_99-1.htm", "https://www.sec.gov/Archives/edgar/data/1015922/000117891326000437/zk2634351.htm"]
    },
    "privateFinancingsBeforeAcquisition": {
      "lastRound": "UNVERIFIED — no SEC Form D found; general web search and Wayback Machine unreachable. Check Point's release states Lakera was 'Founded in 2021 by AI experts from Google and Meta' with research centers in Zurich and San Francisco, but discloses no funding figures.",
      "companyStatedRevenueArr": "none found"
    },
    "distressLast12Months": {"windowStart": "2025-09-25", "layoffsWarn": "none found; company no longer files independently", "ceoCfoDepartures": "not checked"},
    "retrievedDate": "2026-09-25"
  },
  {
    "supplierName": "Zenity",
    "existingId": "print-zenity",
    "legalName": "Zenity (legal entity name UNVERIFIED)",
    "publicPrivate": "private",
    "ticker": null,
    "secCik": "UNVERIFIED — not found in EDGAR",
    "filerType": "not an SEC reporting company",
    "ownership": {"type": "independent, VC-backed", "notes": "Israeli-founded AI agent / low-code security company; CEO Ben Kliger per company press materials"},
    "privateFinancing": {
      "lastRound": {
        "stage": "Series C", "date": "2026-08-03", "amount": "$125 million", "leadInvestor": "Norwest",
        "otherInvestors": ["Qumra Capital", "SoftBank Vision Fund 2", "Hitachi Ventures", "LG Technology Ventures", "Vertex Ventures", "Third Point Ventures", "DTCP", "Intel Capital"],
        "sourceUrl": "https://zenity.io/company-overview/newsroom/company-news/zenity-raises-125-million-to-secure-the-era-of-1-billion-ai-agents"
      },
      "priorRounds": [
        {"stage": "Series B", "date": "2024-10-29", "amount": "$38 million", "sourceUrl": "https://zenity.io/company-overview/newsroom/company-news/zenity-raises-38m-series-b-funding-round-to-secure-agentic-ai"},
        {"stage": "Strategic investment", "date": "2024-07-30", "amount": "not disclosed", "investor": "M12 (Microsoft's venture fund)"},
        {"stage": "Series A", "date": "UNVERIFIED date", "amount": "$16.5 million"},
        {"stage": "Seed", "date": "UNVERIFIED date", "amount": "$5 million"}
      ],
      "companyStatedRevenueArr": {"statement": "\"Zenity has tripled revenue in each of the past two years and is on track to triple revenue again this year\" (unaudited)", "date": "2026-08-03", "sourceUrl": "https://zenity.io/company-overview/newsroom/company-news/zenity-raises-125-million-to-secure-the-era-of-1-billion-ai-agents"}
    },
    "distressLast12Months": {"windowStart": "2025-09-25", "layoffsWarn": "none found (company's own newsroom checked; no WARN database access)", "ceoCfoDepartures": "none found"},
    "retrievedDate": "2026-09-25"
  },
  {
    "supplierName": "WitnessAI",
    "existingId": "print-witnessai",
    "legalName": "WitnessAI (legal entity name UNVERIFIED)",
    "publicPrivate": "private",
    "ticker": null,
    "secCik": "UNVERIFIED — not found in EDGAR",
    "filerType": "not an SEC reporting company",
    "ownership": {"type": "independent, VC-backed", "notes": "CEO/co-founder Rick Caccia per company press materials"},
    "privateFinancing": {
      "lastRound": {
        "stage": "not a numbered series; described as 'strategic funding'", "date": "2026-01-13", "amount": "$58 million", "leadInvestor": "Sound Ventures",
        "otherInvestors": ["Fin Capital", "Samsung Ventures", "Qualcomm Ventures", "Forgepoint Capital Partners", "Silver Buckshot Ventures", "Google Ventures (existing)", "Ballistic Ventures (existing)"],
        "sourceUrl": "https://witness.ai/blog/witnessai-raises-58m-to-help-enterprises-move-faster-with-ai-safely/"
      },
      "priorRounds": "UNVERIFIED — release names Google Ventures/Ballistic Ventures as 'existing' investors implying an earlier round, but no dated source was located",
      "companyStatedRevenueArr": {"statement": "\"500% ARR growth — just in the past 12 months\"; headcount up 5x (unaudited)", "date": "2026-01-13", "sourceUrl": "https://witness.ai/blog/witnessai-raises-58m-to-help-enterprises-move-faster-with-ai-safely/"}
    },
    "distressLast12Months": {"windowStart": "2025-09-25", "layoffsWarn": "none found (company's own site checked; no WARN database access)", "ceoCfoDepartures": "none found"},
    "retrievedDate": "2026-09-25"
  },
  {
    "supplierName": "HiddenLayer",
    "existingId": null,
    "legalName": "HiddenLayer, Inc.",
    "publicPrivate": "private",
    "ticker": null,
    "secCik": "0001931200 (Form D filer only)",
    "filerType": "not an SEC reporting company; files Form D as a private issuer, Delaware incorporation, HQ Leander, TX",
    "ownership": {"type": "independent, VC-backed", "notes": "Earlier Form D equity filings on record: first sale 5/12/2022 ($4.75M of a $5.75M offering), plus amendments 7/26/2023, 9/22/2023, 2/20/2024."},
    "privateFinancing": {
      "lastRound": {"stage": "Series B", "date": "2026-09-02", "amount": "$100 million", "leadInvestor": "Delta-v Capital", "otherInvestors": ["Ten Eleven Ventures", "Morgan Stanley", "M12", "Booz Allen Ventures"], "sourceUrl": "https://hiddenlayer.com/newsroom/"},
      "companyStatedRevenueArr": {"statement": "ARR \"grew more than 10x year-over-year\"; 50+ new platform customers signed; customers include a 'leading frontier model provider' with 700M+ weekly users (unaudited)", "date": "2026-09-02", "sourceUrl": "https://hiddenlayer.com/newsroom/"}
    },
    "distressLast12Months": {"windowStart": "2025-09-25", "layoffsWarn": "none found (company's own newsroom checked; no WARN database access)", "ceoCfoDepartures": "none found"},
    "retrievedDate": "2026-09-25"
  },
  {
    "supplierName": "Robust Intelligence",
    "existingId": null,
    "legalName": "Robust Intelligence, Inc.",
    "publicPrivate": "was private; now integrated into Cisco Systems, Inc. (CSCO) as 'Cisco AI Defense'",
    "ticker": null,
    "secCik": "UNVERIFIED — no Form D found under 'Robust Intelligence, Inc.' in EDGAR full-text search",
    "filerType": "not an SEC reporting company",
    "ownership": {
      "type": "acquired",
      "acquirer": "Cisco Systems, Inc. (CSCO)",
      "dateAnnounced": "UNVERIFIED — no Cisco 8-K referencing Robust Intelligence found for the Jan-Aug 2024 window checked",
      "dateClosed": "During Cisco's fiscal Q1 2025 (between 2024-07-28 and 2024-10-26), per Cisco's own Q1 FY2025 earnings release (8-K, filed 2024-11-13), which lists 'Robust Intelligence, Inc., a privately held AI security solutions company' among that quarter's closed acquisitions (alongside DeepFactor, Inc.)",
      "priceDisclosed": "UNVERIFIED — not disclosed in the Cisco earnings-release exhibit reviewed",
      "sourceUrl": "https://www.sec.gov/Archives/edgar/data/858877/000119312524257224/d875468dex991.htm"
    },
    "privateFinancingsBeforeAcquisition": {
      "lastRound": "UNVERIFIED — no SEC Form D found; general web search and Wayback Machine unreachable this session. No figure stated.",
      "companyStatedRevenueArr": "none found"
    },
    "distressLast12Months": {
      "windowStart": "2025-09-25",
      "layoffsWarn": "none found specific to Robust Intelligence; company no longer files independently",
      "restructuringCharges8K205": "Not specific to Robust Intelligence, but parent Cisco Systems disclosed an Item 2.05 restructuring on 2026-05-13: up to $1.0 billion in pre-tax charges (~$450M in Q4 FY2026, remainder in FY2027), explicitly 'to invest in key growth opportunities including silicon, optics, security and artificial intelligence (AI)' — rung 1 (Cisco's own 8-K), but a company-wide charge, not Robust Intelligence/AI Defense-specific",
      "sourceUrl": "https://www.sec.gov/Archives/edgar/data/858877/000085887726000075/csco-20260513.htm"
    },
    "retrievedDate": "2026-09-25"
  }
]
```

### 4.3 Suppliers considered but left out

None of the nine candidates in the brief were dropped. All nine were researched and kept because they jointly tell
the consolidation story the brief asked for: one platform vendor's in-house AI-security line (Palo Alto Networks /
Prisma AIRS), four separate acquisitions by four different acquirers in roughly the last two years (Protect AI to
Palo Alto Networks; CalypsoAI and SurePath AI to F5; Lakera to Check Point; Robust Intelligence to Cisco), plus three
still-independent, actively funded specialists (Zenity, WitnessAI, HiddenLayer). No candidate was added beyond the
nine given — Prompt Security/SentinelOne and Noma Security are the two names most likely to round out the
consolidation picture in a future pass, flagged here rather than researched without being asked.

### 4.4 Key gaps to flag

- CalypsoAI's and Robust Intelligence's last funding round before acquisition (amount, lead investor, date) could not
  be verified — WebSearch was unavailable this session and Wayback Machine/Crunchbase were unreachable to the fetch
  tool. These are open lookups for a future session with search access, not confirmed absences.
- Robust Intelligence's acquisition announcement date and price are unverified for the same reason; only the closing
  quarter (Cisco fiscal Q1 2025) is confirmed from Cisco's own earnings release.
- SurePath AI's acquisition announcement date (as opposed to its 6/15/2026 close) is unverified.
- Zenity's Series A and seed-round dates are unverified (amounts are confirmed from press-release headlines only).
- WitnessAI's funding round(s) prior to the 1/13/2026 $58M raise are unverified.
- No state WARN-notice check, ratings-action check, or debt-action check was performed for the acquirers (PANW, F5,
  Check Point, Cisco) beyond an Item 2.05/5.02 EDGAR full-text sweep.

---

## 5. Suppliers considered across all four domains but left out, and why

- **Sentra** (data security) — dropped from the final data-security list; smaller/newer than the six other DSPM/data
  suppliers already covered, and this pass lacked budget for equal sourcing rigor.
- **Securiti** (data security) — not tracked standalone; folded into the Veeam record since Veeam acquired it
  (closed 2025-12-11, $1.725B, confirmed via Veeam's own press release).
- **Endor Labs, Docker** (application security/supply chain) — considered as possible ninth entrants in that domain
  but not researched; outside the assigned candidate list.
- **Tenable.ot, Microsoft Defender for IoT, Cisco Cyber Vision** (OT/IoT) — considered but excluded because each is a
  module inside a larger platform (Tenable, Microsoft, Cisco) rather than a standalone OT/IoT-focused supplier
  comparable to Claroty, Dragos, Nozomi, Armis, Forescout, and Xage.
- **Prompt Security (acquired by SentinelOne), Noma Security** (AI security) — flagged as candidates for a future
  pass but not researched this round; the brief named a specific nine-supplier list and asked for justification
  before adding to it.

No supplier was excluded from any domain for reasons other than those stated above — every domain kept between 6 and
9 suppliers (all above the suggested 4-7 range in three of the four domains), on the reasoning that a security leader
would notice the absence of any of the ones kept.
