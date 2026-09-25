# Coverage research — Group 1: Endpoint/XDR, SecOps (SIEM/SOAR), Managed security/MDR, Vulnerability & exposure management

Research pass for the twelve-domain coverage model in `docs/active/autonomy-coverage-plan.md` §4. Read-only research; no project files were edited. All retrieval dates are 2026-09-25 unless a source's own publish date is given. Sourcing follows the five-rung ladder from `docs/active/fable-run/research/11-distress-signal-sources.md` §5 (1 = company's own SEC filing, 2 = rating agency action as republished, 3 = state WARN notice, 4 = confirmed primary corporate action/press release, 5 = trade press report, labelled as such). "None found" means the category was searched and nothing turned up, not that it was skipped.

Two corrections to the brief itself, caught during research and worth flagging up front:
- **Expel was not acquired by CrowdStrike.** No primary source shows this. Expel remains independent.
- **Red Canary was acquired by Zscaler**, not CrowdStrike — confirmed directly against Zscaler's own SEC 10-Q (announced 2025-05-27, closed 2025-08-01, $651.4M cash + $20.2M restricted stock).
- **The Exabeam/LogRhythm merger closed 2024-07-17**, not 2025 as the domain model's shorthand implied — confirmed via Thoma Bravo's own press release.

---

## Domain 1: Endpoint and XDR

| Supplier | Public/Private | Latest footing figure (period) | Last round / ownership | Distress items (last 12 months) |
|---|---|---|---|---|
| CrowdStrike Holdings, Inc. | Public (CRWD) | Revenue $1.47B, +26% YoY; ARR $5.84B, +25% YoY (Q2 FY27, ended 2026-07-31) | Independent public company | None found in window. (May 2025 layoff/8-K falls just before the 12-month cutoff.) |
| SentinelOne, Inc. | Public (S) | Revenue $292M, +21% YoY; ARR $1.218B, +22% YoY (Q2 FY27, ended 2026-07-31) | Independent public company | 8% workforce cut + ~$25M charge, 8-K Item 2.05, 2026-05-28. CFO Barbara Larson departure reported (date unconfirmed, secondary). |
| Microsoft — Defender for Endpoint | Segment of public company (MSFT) | No current segment-specific figure disclosed; Microsoft does not break out Security/Defender revenue | Independent public company (parent) | Company-wide layoffs continuing into FY2026 (~300 China cloud roles, Xbox cuts, June 2026) — secondary, not endpoint-specific. |
| Trend Micro Incorporated | Public (Tokyo: 4704) — NOT an active SEC filer | ARR >$1.7B, +5% YoY (Q2 2026, ended 2026-06-30) | Independent public company | FY2026 operating-income guidance cut (¥56.4B→¥44.4B) on rising AI/cloud costs, disclosed with Q2 2026 results, 2026-08-13 (rung 1 for a non-SEC filer — company's own release). |
| Sophos Group (Sophos Ltd) | Private (Thoma Bravo, since Mar 2020) | No audited public figure; billings estimated >$1.2B (secondary, unverified) | Thoma Bravo since March 2020; acquired Secureworks (~$859M), closed 2025-02-03 | Material: Moody's downgrade to B3, March 2026; S&P affirmed B- Dec 2025; private-credit lenders passed on a $2.5B refinancing (May 2026); new refinancing structure reported Sept 2026 ahead of a March 2027 debt wall. |
| Palo Alto Networks — Cortex XDR | Segment of public company (PANW) | Company-wide: revenue $3.41B, +34% YoY; NGS ARR $9.10B, +63% YoY (Q4 FY26, ended 2026-07-31) | Independent public company (parent); acquired CyberArk (~$25B), closed 2026-02-11 | ~10% of CyberArk's ~4,000 staff cut the day after close (secondary, not a PANW release). |

<details><summary>Full JSON record — Domain 1</summary>

```json
{
  "retrieval_date": "2026-09-25",
  "domain": "Endpoint and XDR",
  "suppliers": [
    {
      "name": "CrowdStrike Holdings, Inc.",
      "ticker": "CRWD", "exchange": "Nasdaq", "public_private": "public",
      "sec_cik": "0001535527", "filer_type": "domestic (10-K/10-Q)", "fiscal_year_end": "January 31",
      "ir_url": "https://ir.crowdstrike.com",
      "ownership": "independent public company",
      "latest_quarter": {
        "period": "Q2 FY2027, ended 2026-07-31", "release_date": "2026-08-26",
        "revenue": "$1.47B, +26% YoY (subscription revenue $1.40B, +27%)",
        "headline_metric": "ARR $5.84B, +25% YoY; net new ARR $332.8M, +51% YoY; Falcon Flex ARR >$2.29B, +101% YoY",
        "source_url": "https://www.sec.gov/Archives/edgar/data/0001535527/000153552726000029/crwd-20260826xex991.htm"
      },
      "prior_quarter": {
        "period": "Q1 FY2027, ended 2026-04-30", "release_date": "2026-06-03",
        "revenue_yoy_growth": "+26%, revenue $1.39B",
        "headline_metric_yoy": "Net new ARR $256M, +32% YoY",
        "source_url": "https://www.sec.gov/Archives/edgar/data/0001535527/000153552726000022/crwd-20260603xex991.htm"
      },
      "next_expected_report": "Q3 FY2027, ~2026-12-01 estimated (secondary, not company-confirmed)",
      "distress_last_12mo": [
        {"item": "Workforce reduction ~500 roles/5%, $36-53M charges — 8-K Item 2.05", "date": "2025-05-06/07", "rung": 1, "note": "falls before the 2025-09-25 window start; context only, not counted in-window"},
        {"item": "Layoffs/restructuring within window", "finding": "none found"},
        {"item": "Ratings action", "finding": "none found"},
        {"item": "Going-concern language", "finding": "none found"},
        {"item": "WARN notice", "finding": "none found"},
        {"item": "CEO/CFO departure", "finding": "none found"}
      ]
    },
    {
      "name": "SentinelOne, Inc.",
      "ticker": "S", "exchange": "NYSE", "public_private": "public",
      "sec_cik": "0001583708", "filer_type": "domestic (10-K/10-Q)", "fiscal_year_end": "January 31",
      "ir_url": "https://investors.sentinelone.com",
      "ownership": "independent public company",
      "latest_quarter": {
        "period": "Q2 FY2027, ended 2026-07-31", "release_date": "2026-08-27",
        "revenue": "$292M, +21% YoY",
        "headline_metric": "ARR $1.218B, +22% YoY; net new ARR $56M, record for a Q2",
        "source_url": "https://www.sec.gov/Archives/edgar/data/0001583708/000158370826000052/sentineloneq227exhibit991.htm"
      },
      "prior_quarter": {
        "period": "Q1 FY2027, ended 2026-04-30", "release_date": "2026-05-28",
        "revenue_yoy_growth": "+21%, revenue $277M (vs $229M prior year)",
        "headline_metric_yoy": "ARR $1,163M, +23% YoY; net new ARR $44M, +55% YoY",
        "source_url": "https://www.sec.gov/Archives/edgar/data/0001583708/000158370826000039/sentineloneq127exhibit991.htm"
      },
      "next_expected_report": "Q3 FY2027, early Dec 2026 estimated (secondary)",
      "distress_last_12mo": [
        {"item": "Restructuring: 8% workforce reduction, ~$25M charge", "date": "2026-05-28", "rung": 1, "source_url": "https://www.sec.gov/Archives/edgar/data/0001583708/000158370826000039/s-20260528.htm"},
        {"item": "CFO Barbara Larson departure, interim CFO Barry Padgett named", "date": "unconfirmed exact date", "rung": 5, "note": "secondary, likely but not certainly within window"},
        {"item": "Ratings action / going-concern / WARN", "finding": "none found"}
      ]
    },
    {
      "name": "Microsoft Corporation (Defender for Endpoint — not a separately filed entity)",
      "ticker": "MSFT", "exchange": "Nasdaq", "public_private": "public (parent)",
      "sec_cik": "0000789019", "filer_type": "domestic (10-K/10-Q)", "fiscal_year_end": "June 30",
      "ir_url": "https://www.microsoft.com/en-us/investor",
      "ownership": "independent public company",
      "segment_note": "Microsoft does not report Defender or 'Security' as a distinct reportable segment; no current figure verified. Last public 'security >$20B/yr' claim dates to ~Feb 2023 and is stale/unverified for FY2026.",
      "distress_last_12mo": [
        {"item": "~300 China cloud-computing roles cut", "date": "2026-06-09", "rung": 5},
        {"item": "Xbox division workforce reductions", "date": "2026-06-10", "rung": 5},
        {"item": "Security leadership reshuffle reported after an earlier 4,800-person cut", "date": "unconfirmed", "rung": 5},
        {"item": "Going-concern / ratings / WARN", "finding": "none found / not applicable — investment-grade large-cap"}
      ]
    },
    {
      "name": "Trend Micro Incorporated",
      "ticker": "4704 (Tokyo Stock Exchange); OTC ADR TMICY/TMICF", "public_private": "public (Japan-listed)",
      "sec_cik": "0001089463",
      "filer_type": "NOT a current active SEC filer; last filing on record dated 2009-02-12 (third-party Schedule 13G/A); appears deregistered.",
      "fiscal_year_end": "December 31",
      "ir_url": "https://www.trendmicro.com/en_us/about/investor-relations.html",
      "ownership": "independent, publicly traded; founding Chang/Chen families held ~30% per dated 2012-2013 reporting (unverified current %)",
      "latest_quarter": {
        "period": "Q2 2026, ended 2026-06-30", "release_date": "2026-08-13",
        "headline_metric": "ARR exceeded $1.7B, +5% YoY",
        "source_url": "https://newsroom.trendmicro.com/2026-08-13-Trend-Micro-Reports-Earnings-Results-for-Q2-2026"
      },
      "prior_quarter": {
        "period": "Q1 2026, ended 2026-03-31", "release_date": "2026-05-14",
        "revenue_yoy_growth": "+9% YoY, net sales ¥73,856M (~$470M)",
        "source_url": "https://newsroom.trendmicro.com/2026-05-14-Trend-Micro-Reports-Earnings-Results-for-Q1-2026"
      },
      "full_year_2026_guidance": "Net sales held at ¥301,500M (~$1.93B); operating-income guidance CUT from ¥56.4B to ¥44.4B (~$284M) after Q2, on rising AI/cloud token costs",
      "distress_last_12mo": [
        {"item": "FY2026 operating-income guidance cut", "date": "2026-08-13", "rung": 1, "note": "company's own release — top rung available for a non-SEC filer"},
        {"item": "Workforce layoff within window", "finding": "none confirmed with an in-window date"},
        {"item": "Ratings action / CEO-CFO departure / WARN / going-concern", "finding": "none found"}
      ]
    },
    {
      "name": "Sophos Group (Sophos Ltd)",
      "public_private": "private", "sec_filer": false,
      "ownership": {
        "owner": "Thoma Bravo", "acquisition_date": "completed March 2020 (take-private)",
        "subsequent_acquisition": "Sophos acquired Secureworks Corp. for ~$859M all-cash; announced Oct 2024, closed 2025-02-03",
        "source_url": "https://www.thomabravo.com/press-releases/sophos-completes-secureworks-acquisition"
      },
      "ir_url": "https://www.sophos.com/en-us/press",
      "last_disclosed_financials": {"figure": "billings estimated >$1.2B as of ~2025", "source_quality": "SECONDARY, unverified"},
      "distress_last_12mo": [
        {"item": "S&P affirmed B-, citing expected need to refinance 2027 maturities", "date": "2025-12", "rung": 2},
        {"item": "Moody's downgraded to B3 from B2, outlook revised to stable", "date": "2026-03", "rung": 2},
        {"item": "Debt structure: $92.5M RCF due Dec 2026; ~$2.1-2.5B senior secured term loans due March 2027; leverage expected toward ~9x FY2026 from 6.3x FY2025 (S&P)", "date": "as of Dec 2025/Mar 2026", "rung": 2},
        {"item": "Private credit lenders passed on a $2.5B refinancing", "date": "2026-05-28", "rung": 5},
        {"item": "Thoma Bravo weighing lender concessions on a $2B refinancing", "date": "2026-08-18", "rung": 5},
        {"item": "New refinancing structure reported ahead of March 2027 deadline", "date": "2026-09-08", "rung": 5},
        {"item": "CEO/CFO departure", "finding": "none found — Joe Levy remains CEO since May 2024"}
      ]
    },
    {
      "name": "Palo Alto Networks, Inc. (Cortex XDR is a product line; figures below are company-wide)",
      "ticker": "PANW", "exchange": "Nasdaq", "public_private": "public",
      "sec_cik": "0001327567", "filer_type": "domestic (10-K/10-Q)", "fiscal_year_end": "July 31",
      "ir_url": "https://investors.paloaltonetworks.com",
      "ownership": "independent public company",
      "recent_acquisition": {"target": "CyberArk Software Ltd.", "announced": "2025-07-30", "closed": "2026-02-11", "value": "~$25B equity value ($2.3B cash + 112M shares)"},
      "latest_quarter": {
        "period": "Q4 FY2026, ended 2026-07-31",
        "revenue_company_wide": "$3.41B, +34% YoY",
        "headline_metric": "NGS ARR $9.10B, +63% YoY; RPO $21.2B, +34% YoY",
        "full_year_fy2026": "revenue $11.48B vs $9.22B FY2025 (~+25% YoY, inflated by CyberArk/Chronosphere acquisitions)",
        "source_url": "https://www.sec.gov/Archives/edgar/data/0001327567/000132756726000019/ex991q426earningsrelease.htm"
      },
      "prior_quarter": {
        "period": "Q3 FY2026, ended 2026-04-30", "release_date": "2026-06-02",
        "revenue_yoy_growth": "+31%, revenue $3.0B (incl. $388M from CyberArk/Chronosphere)",
        "source_url": "https://www.sec.gov/Archives/edgar/data/0001327567/000132756726000012/ex991q326earningsrelease.htm"
      },
      "fy2027_guidance": "revenue $14.1B-$14.2B; NGS ARR $11.075B-$11.175B",
      "distress_last_12mo": [
        {"item": "CyberArk deal closed", "date": "2026-02-11", "rung": 4},
        {"item": "~10% of CyberArk's ~4,000-person workforce cut day after close", "date": "2026-02-12", "rung": 5, "note": "trade press, not a PANW release"},
        {"item": "Founder/CTO Nir Zuk's retirement", "date": "2025-08-18", "note": "falls ~5 weeks before window start; context only"},
        {"item": "CFO departure / ratings / going-concern / WARN", "finding": "none found"}
      ]
    }
  ]
}
```
</details>

**Considered and left out (Domain 1):** Broadcom/Symantec Enterprise + VMware Carbon Black (deprioritized inside Broadcom, not broken out, not top-of-mind for endpoint leaders today); Cybereason (went through severe funding distress 2023-2024, now a distress case study rather than a footing comparison); Cisco Secure Endpoint (small piece of a much larger network-security portfolio); Elastic Security (SIEM/XDR-adjacent but not seen primarily as an EDR/XDR leader); Trellix — McAfee Enterprise + FireEye, private under Symphony Technology Group (genuinely relevant, financials essentially undisclosed, judged less consistently top-of-mind than the six chosen); Fortinet FortiEDR and Check Point Harmony Endpoint (endpoint is a smaller slice of each vendor's core network-security identity).

---

## Domain 2: Security operations — SIEM and SOAR

| Supplier | Public/Private | Latest footing figure (period) | Last round / ownership | Distress items (last 12 months) |
|---|---|---|---|---|
| Splunk (Cisco) | Public (Cisco, CSCO) | Cisco total revenue $17.3B, +18% YoY (Q4 FY26, ended 2026-07-25); Splunk not broken out | Acquired by Cisco, announced 2023-09-21, closed 2024-03-18, $157/share cash, ~$28B equity value | $1B restructuring charge (8-K, 2026-05-13); 2 CA WARN notices at Splunk's former SF HQ address (2025-08-13 and 2026-06-16) — employer of record is Cisco. |
| Google SecOps (Alphabet) | Public (Alphabet, GOOGL) | Alphabet revenue $119.8B, +24% YoY; Google Cloud $24.8B, +82% YoY (Q2 2026, ended 2026-06-30); SecOps not broken out | Wholly owned Google Cloud product (Chronicle 2019 + Mandiant, closed 2022) | Mandiant/Threat Intelligence Group layoffs reported ~2026-06-03/04, scale undisclosed (trade press only); no SEC-filed restructuring found. |
| Palo Alto Networks — Cortex XSIAM | Public (PANW) | Company-wide: revenue $3.41B, +34% YoY; NGS ARR $9.10B, +63% YoY (Q4 FY26); XSIAM not broken out | Product line inside PANW; company acquired CyberArk (closed 2026-02-11) and Chronosphere (2026-01-29) | No restructuring/workforce-reduction 8-Ks found. |
| Exabeam, Inc. | Private | No company-stated revenue/ARR figure found | Merged with LogRhythm, closed 2024-07-17 (corrects the brief's 2025 assumption); Thoma Bravo (LogRhythm's former owner) a named stakeholder; last funding Series F, June 2021, $200M at $2.4B | CEO change: Pete Harteveld replaced retiring Chris O'Malley, Oct 2025 (secondary, two outlets); no in-window WARN notices found. |
| Torq | Private | 2024: stated 300% revenue growth; 2026 ARR target $100M (no absolute $ figure found) | Series D, 2026-01-09, $140M at $1.2B valuation, led by Merlin Ventures | None found in any category. |
| Tines | Private | Secondary trade press: "on course" for $100M revenue "next quarter" as of 2026-07-28 | Series C, 2025-02-11, $125M at $1.13B valuation, led by Goldman Sachs and SoftBank | None found in any category, with access-limitation caveats (some state systems unreachable). |

<details><summary>Full JSON record — Domain 2</summary>

```json
{
  "retrieval_date": "2026-09-25",
  "domain": "Security operations (SIEM, SOAR)",
  "suppliers": {
    "splunk_cisco": {
      "product": "Splunk", "parent_legal_name": "Cisco Systems, Inc.", "public_private": "public (parent)",
      "ticker": "CSCO", "exchange": "NASDAQ", "sec_cik": "0000858877",
      "filer_type": "domestic, large accelerated filer (10-K/10-Q)", "fiscal_year_end": "last Saturday of July (FY2026 ended 2026-07-25)",
      "ir_url": "https://investor.cisco.com",
      "ownership": {
        "status": "wholly owned; acquired, not independently owned", "acquirer": "Cisco Systems, Inc.",
        "announced": "2023-09-21", "closed": "2024-03-18",
        "price": "$157/share cash; ~$28B equity value as announced, ~$27B merger consideration as closed",
        "source_announcement": "https://www.sec.gov/Archives/edgar/data/858877/000119312523239165/d464532dex991.htm",
        "source_close": "https://www.sec.gov/Archives/edgar/data/858877/000119312524070175/d783088dex991.htm"
      },
      "segment_disclosure": {
        "cisco_reportable_segments": "geographic only — Americas, EMEA, APJC; no product segments",
        "splunk_standalone_disclosure": "none on an ongoing basis",
        "where_splunk_revenue_lands": "folded into 'Security' and 'Observability' MD&A revenue categories and geographic segments/goodwill; only dollar figure ever attached to Splunk by name is the one-time FY2024 acquisition footnote ($1.4B stub-period revenue, $557M net loss attributable to Splunk, $82M transaction costs)",
        "source": "https://www.sec.gov/Archives/edgar/data/858877/000085887726000132/csco-20260725.htm"
      },
      "latest_quarter": {
        "period": "Q4 FY2026", "period_end": "2026-07-25", "release_date": "2026-08-12",
        "total_revenue": "$17.3B", "total_revenue_yoy": "+18%",
        "security_product_revenue_yoy": "+14% (dollar figure not disclosed quarterly)",
        "security_product_revenue_fy2026_annual": "$8,232M, +2% vs FY2025's $8,094M",
        "source": "https://s21.q4cdn.com/812015656/files/doc_earnings/2026/q4/earnings-result/Q4FY26-Press-Release.pdf"
      },
      "prior_quarter": {
        "period": "Q3 FY2026", "period_end": "2026-04-25", "release_date": "2026-05-13",
        "total_revenue": "$15.8B", "total_revenue_yoy": "+12%",
        "security_product_revenue": "$2,008M vs $2,013M prior year (flat)",
        "source": "https://www.sec.gov/Archives/edgar/data/858877/000085887726000075/exhibit991pressrelease-q3f.htm"
      },
      "next_expected_report": "~2026-11-11 for Q1 FY2027 (secondary estimate)",
      "distress_last_12_months": {
        "sec_filing_restructuring": {"found": true, "rung": 1, "detail": "8-K Item 2.05, 2026-05-13: up to $1B pre-tax restructuring to invest in 'silicon, optics, security and AI'; ~$450M in Q4 FY26, remainder FY27. Q4 FY26 income statement shows $511M restructuring charges vs $35M prior year. Not Splunk-specific by name.", "source": "https://www.sec.gov/Archives/edgar/data/858877/000085887726000075/csco-20260513.htm"},
        "layoffs_warn": {"found": true, "rung": 3, "detail": "CA WARN filings under 'Cisco Systems, Inc.' at Splunk's former SF HQ address: filed 2025-08-13, effective 2025-10-13, 64 employees (+157 Milpitas); filed 2026-06-16, effective 2026-07-13, 81 employees (+154 Milpitas, 236 San Jose)", "source": "https://edd.ca.gov/siteassets/files/jobs_and_training/warn/warn-report-for-7-1-25-to-6-30-26.pdf"},
        "ratings_actions": "none found (could not reach agency sites directly this session)",
        "going_concern_language": "none found",
        "ceo_cfo_departures": "none found tied to Splunk or Cisco Security org",
        "divestitures": "none found", "shutdown": "none found"
      }
    },
    "google_secops_alphabet": {
      "product": "Google SecOps (formerly Chronicle Security, merged with Mandiant)", "parent_legal_name": "Alphabet Inc.",
      "public_private": "public (parent)", "ticker": "GOOGL / GOOG", "sec_cik": "0001652044",
      "filer_type": "domestic 10-K/10-Q", "fiscal_year_end": "December 31",
      "ir_url": "https://abc.xyz/investor/",
      "ownership": "wholly owned Google Cloud product; Chronicle acquired 2019, Mandiant closed Sept 2022 (deal price not reverified this session)",
      "segment_disclosure": "none found; folded into aggregate Google Cloud segment revenue with no product-level breakout",
      "latest_quarter": {
        "period": "Q2 2026", "period_end": "2026-06-30", "release_date": "2026-07-22",
        "total_revenue": "$119.8B", "total_revenue_yoy": "+24% (+23% constant currency)",
        "google_cloud_revenue": "$24.8B", "google_cloud_revenue_yoy": "+82%",
        "source": "https://www.sec.gov/Archives/edgar/data/0001652044/000165204426000066/googexhibit991q22026.htm"
      },
      "prior_quarter": {
        "period": "Q1 2026", "period_end": "2026-03-31",
        "total_revenue": "$109.896B", "total_revenue_yoy": "+22% (+19% constant currency)",
        "google_cloud_revenue": "$20.028B", "google_cloud_revenue_yoy": "+63%",
        "source": "https://www.sec.gov/Archives/edgar/data/0001652044/000165204426000043/googexhibit991q12026.htm"
      },
      "next_expected_report": "2026-10-27 (secondary estimate)",
      "distress_last_12_months": {
        "sec_filing_restructuring": {"found": false, "rung": 1, "detail": "SEC full-text search for 'restructuring'/'workforce reduction' in Alphabet 8-Ks, 2025-09-25 to 2026-09-25, zero hits"},
        "layoffs_warn": {"found": true, "rung": 5, "detail": "Mandiant/Google Threat Intelligence Group layoffs reported starting ~2026-06-03, scale undisclosed; Google gave a general 'evaluating internal structures' statement", "source": "https://opentools.ai/news/google-cloud-cybersecurity-layoffs-mandiant-ai-2026 (secondary)"},
        "ratings_actions": "none found", "going_concern_language": "none found",
        "ceo_cfo_departures": "none found specific to Google SecOps", "divestitures": "none found", "shutdown": "none found"
      }
    },
    "palo_alto_cortex_xsiam": {
      "product": "Cortex XSIAM", "legal_name": "Palo Alto Networks, Inc.", "public_private": "public",
      "ticker": "PANW", "exchange": "NASDAQ", "sec_cik": "0001327567",
      "filer_type": "domestic 10-K/10-Q", "fiscal_year_end": "July 31",
      "ir_url": "https://investors.paloaltonetworks.com",
      "ownership": "N/A — XSIAM is a product line, not a separate entity",
      "segment_disclosure": "none found; company discloses company-wide NGS ARR only, no XSIAM-specific figure",
      "latest_quarter": {
        "period": "Q4 FY2026", "period_end": "2026-07-31", "release_date": "2026-09-01",
        "total_revenue": "$3.41B", "total_revenue_yoy": "+34%",
        "ngs_arr": "$9.10B", "ngs_arr_yoy": "+63%",
        "note": "growth partly inorganic: Q3 FY26 disclosed $388M revenue / $1.6B NGS ARR from CyberArk+Chronosphere",
        "source": "https://www.sec.gov/Archives/edgar/data/0001327567/000132756726000019/ex991q426earningsrelease.htm"
      },
      "prior_quarter": {
        "period": "Q3 FY2026", "period_end": "2026-04-30", "release_date": "2026-06-02",
        "total_revenue": "$3.0B (incl. $388M from CyberArk/Chronosphere)", "total_revenue_yoy": "+31%",
        "ngs_arr": "$8.1B (incl. $1.6B from acquisitions)", "ngs_arr_yoy": "+60%",
        "source": "https://www.sec.gov/Archives/edgar/data/1327567/000132756726000012/ex991q326earningsrelease.htm"
      },
      "distress_last_12_months": {
        "sec_filing_restructuring": {"found": false, "rung": 1, "detail": "SEC full-text search zero hits for the window"},
        "layoffs_warn": {"found": false},
        "major_corporate_actions": [
          {"action": "Acquisition of CyberArk Software Ltd.", "announced": "2025-07-30 (just before window start)", "closed": "2026-02-11", "price": "~$25B equity value", "rung": 4, "source": "https://www.sec.gov/Archives/edgar/data/1327567/000119312525168821/d67702dex991.htm"},
          {"action": "Acquisition of Chronosphere", "announced_and_closed": "2026-01-29", "price": "not disclosed", "rung": 4, "source": "https://www.sec.gov/Archives/edgar/data/1327567/000119312526029489/d884183dex991.htm"}
        ],
        "ratings_actions": "none found", "going_concern_language": "none found",
        "ceo_cfo_departures": "none found", "divestitures": "none found", "shutdown": "none found"
      },
      "related_note_outside_window": "Palo Alto acquired IBM's QRadar SaaS assets, announced 2024-09-04, closed 2024-08-31 — outside the 12-month window"
    },
    "exabeam": {
      "legal_name": "Exabeam, Inc.", "public_private": "private",
      "sec_status": "no 10-K/10-Q filer; only a 2015 Form D notice on file, CIK 0001654488",
      "ownership": {
        "merger": "LogRhythm (Thoma Bravo-owned) merged with Exabeam", "announced": "2024-05", "closed": "2024-07-17",
        "correction_note": "corrects the domain model's implied 2025 date; confirmed via Thoma Bravo's own press release",
        "current_ownership": "Thoma Bravo is a named stakeholder in the combined company; exact split with Exabeam's prior VC investors not disclosed",
        "source": "https://www.thomabravo.com/press-releases/exabeam-and-logrhythm-complete-merger-and-announce-new-company-details"
      },
      "last_funding_round": {"round": "Series F", "date": "2021-06", "amount": "$200M", "valuation": "$2.4B (some sources: $2.5B at merger time)", "source_quality": "secondary, not re-verified against a primary release this session"},
      "company_stated_revenue_arr": "none found this session",
      "distress_last_12_months": {
        "sec_filing": {"found": false, "rung": 1, "note": "private, no SEC filings"},
        "warn_notices": {"found_but_outside_window": true, "rung": 3, "detail": "4 WARN notices found, all 2023-2024, none in-window", "source": "https://laborcurrent.com/layoffs/company/exabeam (secondary aggregator)"},
        "leadership_departure": {"found": true, "rung": 5, "detail": "CEO transition: Pete Harteveld (former CRO) named CEO, succeeding retiring Chris O'Malley", "date": "reported Oct 2025", "sources": ["https://www.crn.com/news/security/2025/exabeam-promotes-pete-harteveld-to-ceo-for-ai-secops-push", "https://www.bankinfosecurity.com/exabeam-ceo-integrates-ai-agents-in-siem-push-a-29707"]},
        "restructuring_charges": "none found", "debt_raised_refinanced": "none found", "divestitures": "none found", "shutdown": "none found"
      }
    },
    "torq": {
      "legal_name": "Torq (entity suffix unconfirmed)", "public_private": "private",
      "hq": "Denver, CO", "founders": "Ofer Smadari (CEO), Leonid Belkind, Eldad Livni; founded 2020",
      "sec_status": "no SEC filer found",
      "last_funding_round": {
        "round": "Series D", "announced": "2026-01-09", "closed": "2026-01-12", "amount": "$140M", "valuation": "$1.2B",
        "lead_investor": "Merlin Ventures", "participating_investors": ["Evolution Equity Partners", "Notable Capital", "Bessemer Venture Partners", "Insight Partners", "Greenfield Partners"],
        "total_funding_to_date": "$332M", "source": "https://torq.io/news/torq-seriesd/ (company press release, primary)"
      },
      "company_stated_revenue_arr": {"detail": "Jan 2025 release: 300% revenue growth, 200% employee growth for 2024; target $100M ARR for 2026. No absolute dollar figure found.", "source": "https://torq.io/news/torq-announces-revenue-and-employee-growth/"},
      "distress_last_12_months": {"sec_filing": {"found": false}, "rating_agency_action": {"found": false}, "warn_notices": {"found": false, "caveat": "CA EDD has no name-search tool; weak negative"}, "layoffs": {"found": false}, "restructuring": {"found": false}, "debt_raised": {"found": false}, "leadership_departures": {"found": false}, "divestitures": {"found": false}, "shutdown": {"found": false}}
    },
    "tines": {
      "legal_name": "Tines (entity suffix unconfirmed)", "public_private": "private",
      "hq": "Dublin, Ireland / Boston", "founders": "Eoin Hinchy (CEO), Thomas Kinsella; founded 2018",
      "sec_status": "no SEC filer found",
      "last_funding_round": {
        "round": "Series C", "date": "2025-02-11", "amount": "$125M", "valuation": "$1.13B",
        "lead_investors": "Goldman Sachs and SoftBank",
        "confidence_note": "rests on Tines' own newsroom aggregation of Bloomberg/BBJ headlines (direct fetch blocked); valuation independently corroborated by the Irish Times, 2026-07-28",
        "sources": ["https://www.tines.com/newsroom/", "https://www.irishtimes.com/business/2026/07/28/tech-company-tines-takes-on-vibe-coding-with-new-platform/"]
      },
      "company_stated_revenue_arr": {"detail": "Trade press (The Currency, 2026-07-28) reported Tines 'on course to hit revenues of $100m in the next quarter' — forward-looking, not a dated company figure already reached.", "source_quality": "secondary"},
      "distress_last_12_months": {"sec_filing": {"found": false}, "rating_agency_action": {"found": false}, "warn_notices": {"found": false, "caveat": "MA DUA WARN system unreachable this session; inconclusive"}, "layoffs": {"found": false, "caveat": "layoffs.fyi could not be read (JS-rendered)"}, "restructuring": {"found": false}, "debt_raised": {"found": false}, "leadership_departures": {"found": false}, "divestitures": {"found": false}, "shutdown": {"found": false}}
    }
  }
}
```
</details>

**Considered and left out (Domain 2):** IBM QRadar — Palo Alto acquired IBM's QRadar SaaS assets (asset purchase, announced 2024-09-04, closed 2024-08-31, confirmed in Palo Alto's own 8-K), before the 12-month window; what IBM retained afterward (on-prem QRadar, full exit) not independently confirmed. Securonix — private, reportedly Vista Equity Partners-backed (date unverified), new CEO Toby Weiss appointed 2026-06-28; a real Gartner-recognized Leader but judged second-tier relative to the six chosen. LogPoint — appears to have rebranded to "GuardSix" (exact date unconfirmed); European sovereign-security positioning. Devo — private, VC-backed (Insight Partners, Georgian, TCV, General Atlantic, Bessemer, Kibo Ventures, Eurazeo), new CEO Ken Naumann appointed 2025-03-05. Swimlane — ownership/funding unverifiable this session, noted rather than omitted. Rapid7 InsightIDR — Rapid7 is public and InsightIDR is a real SIEM/XDR competitor, but the assignment specified the six above as today's recognized main players in SIEM/SOAR specifically.

---

## Domain 3: Managed security, MDR, and security services firms

Two corrections to the brief, confirmed during research: **Trustwave is no longer independently owned by The Chertoff Group** — LevelBlue (AT&T Cybersecurity's spun-off MSSP, backed by WillJam Ventures) completed its acquisition of Trustwave on 2025-08-19, about a year after Chertoff's MC² Security Fund bought it in January 2024. **Expel was not acquired by CrowdStrike** — no primary source supports this; Expel remains independent. **Red Canary was acquired — by Zscaler**, confirmed directly against Zscaler's own SEC 10-Q (period ended 2025-10-31): acquired 2025-08-01 for $651.4M cash plus $20.2M restricted stock, $544.5M goodwill.

| Supplier | Public/Private | Latest footing figure (period) | Last round / ownership event | Distress items (last 12 mo, since 2025-09-25) |
|---|---|---|---|---|
| Optiv Security Inc. | Private, PE-owned (KKR majority, announced Dec 2016) | No public financials; ~$1B long-term debt reported (secondary) | PE portfolio company; credit-facility amendment/extension March–May 2026 | Moody's downgrade to Caa2 from B3, 2025-04-24; S&P downgrades to CCC+ then CCC referenced but dates unverified (site blocked); credit-facility amendment closed 2026-05-07/08; sold ACT consulting division to Vobis Ventures, closed ~2026-06-01. |
| Trustwave Holdings, Inc. | Private — acquired by LevelBlue 2025-08-19 (was Chertoff Group Jan 2024–Aug 2025) | Combined LevelBlue+Trustwave "annual revenues exceeding $1 billion" (LevelBlue PR, Aug 2025) | Acquired by LevelBlue, completed 2025-08-19 (price not disclosed) | Ownership change is the headline item; no periodic SEC filer. |
| Arctic Wolf Networks, Inc. | Private, VC/PE-backed | No recent company-disclosed revenue found | Series F, $150M, 2021-07-19, $4.3B valuation (last confirmed primary round); reported acquisition of Sevco Security, 2026-02-23 (secondary, unconfirmed) | Cut ~250 jobs (<10% of workforce), reported ~2026-05-06 (trade press, not confirmed in a filing); no CA WARN record located. |
| Expel, Inc. | Private | Third-party estimate ~$142.2M ARR (secondary, unverified) | Series E extended to $171.3M total, valuation >$1B, last confirmed tranche 2022-10-03 | None found. Not acquired by CrowdStrike (verified false). No WARN/layoff record found. |
| eSentire, Inc. | Private, PE-backed (Warburg Pincus, majority since 2017) | No recent company-disclosed revenue found | $325M growth-equity round, announced 2022-02-22, Warburg Pincus-led with Georgian/CDPQ, valuation >$1.1B | CEO change to James C. Foster reported ~2026-03-19 — UNVERIFIED, could not confirm via eSentire's own newsroom. No WARN/layoff record found. |
| ReliaQuest, LLC | Private, PE/growth-equity-backed (KKR since 2020; EQT/FTV/KKR since 2025) | ARR "surpassed $300 million," >30% YoY, "operating profitably" (company PR, 2025-03-31) | $500M+ round, 2025-03-31, $3.4B valuation, led by EQT, KKR, FTV Capital | None found in filings or company newsroom. |
| Red Canary, Inc. | Now a Zscaler business unit (was private, VC-backed) | Not separately disclosed post-acquisition | Acquired by Zscaler: announced 2025-05-27, closed 2025-08-01, $651.4M cash + $20.2M restricted stock (Zscaler 10-Q) | Acquisition itself is the item (rung 1 — confirmed in acquirer's own SEC filing). No post-acquisition layoffs found. |

<details><summary>Full JSON record — Domain 3</summary>

```json
{
  "retrieval_date": "2026-09-25",
  "domain": "Managed security, MDR, and security services firms",
  "suppliers": [
    {
      "name": "Optiv Security Inc.", "legal_name": "Optiv Inc.", "public_private": "private", "ticker": null,
      "sec_cik": "0001637666",
      "sec_filer_status": "No current periodic filer. CIK exists from a 2016 IPO attempt: DRS filed 2015-10-30, S-1 filed 2016-11-18, Form D 2016-07-08, Registration Withdrawal (RW) 2018-01-03. No 10-K/10-Q on file.",
      "fiscal_year_end": "unverified",
      "investor_relations_url": "https://www.optiv.com/company/press-releases",
      "ownership": {"status": "PE-owned", "owner": "KKR (majority); Blackstone retained minority stake; Optiv management minority", "date_announced": "2016-12-06", "date_closed": "expected Q1 2017 per press release (not independently confirmed)", "price": "not disclosed", "source": "https://www.optiv.com/company/press-releases/optiv-security-be-acquired-kkr"},
      "public_debt_ratings": {
        "moodys": {"action": "Downgraded Optiv Parent Inc. CFR to Caa2 from B3, PDR to Caa2-PD from B3-PD, Senior Secured First Lien Term Loan to Caa2 from B3", "date": "2025-04-24", "source": "https://app.researchpool.com/index.php/provider/moodys-investors-service/moodys-ratings-downgrades-optivs-cfr-to-caa2-outlook-changes-to-negati-PmVj7AlYyb", "rung": 2, "note": "republished by a third party, not Optiv's own newsroom"},
        "sp_note": "S&P downgrades to 'CCC+' and later 'CCC' referenced in search snippets; spglobal.com pages returned HTTP 403 both times; exact dates unverified pending a readable source"
      },
      "last_reported_financials": "Not publicly disclosed; trade press (Bloomberg Law, Private Equity Insights) reports ~$1B long-term debt, ~$650M term loan debt originally maturing 2026 — secondary, not company-confirmed",
      "distress_last_12_months": [
        {"item": "Moody's downgrade to Caa2 (from B3), outlook negative", "date": "2025-04-24", "rung": 2, "source_url": "https://app.researchpool.com/index.php/provider/moodys-investors-service/moodys-ratings-downgrades-optivs-cfr-to-caa2-outlook-changes-to-negati-PmVj7AlYyb"},
        {"item": "S&P downgrades ('CCC+' then 'CCC') referenced", "date": "unverified", "rung": 2, "note": "access blocked (403); not republished on Optiv's own newsroom as far as found"},
        {"item": "Lender agreement amending/extending First Lien Credit Agreement to Aug 2028 and Second Lien to Aug 2029; covered >99% of First Lien and 100% of Second Lien Term Loan holders", "date": "2026-03-16 agreement, 2026-05-07/08 closing", "rung": 4, "source_url": "https://www.optiv.com/company/press-releases/optiv-strengthens-financial-position-lender-agreement-comprehensive"},
        {"item": "Sold Advisory, Consulting and Transformation (ACT) business (~800 clients, ~500 consultants) to Vobis Ventures", "date": "announced/closed 2026-06-01/02", "rung": 4, "source_url": "https://www.optiv.com/company/press-releases/optiv-sells-advisory-consulting-and-transformation-act-business-vobis"},
        {"item": "Reported exploration of a sale of Optiv's managed-services business (~$400M+), reported to have 'fizzled out'", "date": "reported through 2025-2026, precise date unverified", "rung": 5, "source_url": "https://news.bloomberglaw.com/private-equity/kkr-backed-optiv-seeks-asset-sale-ahead-of-2026-debt-maturity"},
        {"item": "WARN Act notice", "finding": "none found"},
        {"item": "Going-concern language", "finding": "none found (Optiv does not file SEC periodic reports)"},
        {"item": "CEO/CFO departure", "finding": "none found — CEO Kevin Lynch and CFO Marc Cabi both quoted in the March/May 2026 credit-facility releases"}
      ]
    },
    {
      "name": "Trustwave Holdings, Inc.", "public_private": "private", "ticker": null, "sec_cik": "0001518154",
      "sec_filer_status": "No current periodic filer. History: S-1/A amendments and an 8-A12B around 2011 (withdrawn IPO attempt, RW on file), plus Form D notices.",
      "fiscal_year_end": "unverified",
      "investor_relations_url": "https://www.levelblue.com/newsroom/press-releases (post-acquisition)",
      "ownership": {
        "status": "acquired",
        "history": "Singtel divested Trustwave to The Chertoff Group's MC² Security Fund, reported at $205M, completed January 2024",
        "current_owner_acquirer": "LevelBlue", "date_closed": "2025-08-19", "price": "not disclosed",
        "source": "https://www.levelblue.com/newsroom/press-releases/levelblue-completes-acquisition-of-trustwave-to-form-the-worlds-largest-managed-security-services-provider"
      },
      "last_reported_financials": "LevelBlue's own release states the combined LevelBlue+Trustwave entity serves 'over 30,000 customers with annual revenues exceeding $1 billion' — not broken out for Trustwave alone",
      "distress_last_12_months": [
        {"item": "Acquired by LevelBlue (ownership change)", "date": "2025-08-19", "rung": 4, "source_url": "https://www.levelblue.com/newsroom/press-releases/levelblue-completes-acquisition-of-trustwave-to-form-the-worlds-largest-managed-security-services-provider"},
        {"item": "WARN Act notice / ratings action / CEO-CFO departure", "finding": "none found"}
      ]
    },
    {
      "name": "Arctic Wolf Networks, Inc.", "public_private": "private", "ticker": null, "sec_cik": null,
      "sec_filer_status": "No SEC filer found (EDGAR company search returned zero matches)",
      "fiscal_year_end": "unverified",
      "ownership": {"status": "independent, VC/PE-backed", "notes": "no single controlling PE owner identified; syndicate of venture/growth investors"},
      "last_funding_round": {"date": "2021-07-19", "stage": "Series F", "amount": "$150M", "valuation": "$4.3B", "note": "secondary market data (Hiive) cited a valuation below $4B as of Q1 2025 — unconfirmed, secondary"},
      "stated_arr_revenue": "not found / unverified",
      "distress_last_12_months": [
        {"item": "Cut ~250 jobs (under 10% of workforce, which stood at 2,600+ as of Dec 2024), stated rationale: reallocating spend to AI/SOC platform investment", "date": "reported ~2026-05-06", "rung": 5, "source_url": "https://www.theregister.com/ai-and-ml/2026/05/06/arctic-wolf-cuts-250-jobs-in-ai-push/5231213", "note": "trade press, not confirmed via a WARN filing or Arctic Wolf's own newsroom"},
        {"item": "WARN Act notice (California)", "finding": "none found"},
        {"item": "Reported acquisition of Sevco Security", "date": "2026-02-23 (PitchBook, secondary)", "status": "unverified"},
        {"item": "Ratings action / CEO-CFO departure", "finding": "none found"}
      ]
    },
    {
      "name": "Expel, Inc.", "public_private": "private", "ticker": null, "sec_cik": "0001684049",
      "sec_filer_status": "No periodic filer; only Form D filings on record",
      "fiscal_year_end": "unverified",
      "investor_relations_url": "https://expel.com/resource/",
      "ownership": {"status": "independent, VC-backed", "acquisition_check": "VERIFIED FALSE — no evidence CrowdStrike acquired Expel, checked against CrowdStrike's own newsroom, SEC filings, and Expel's materials; CrowdStrike's 2025 M&A activity in its SEC filings includes Onum Technology Inc. (closed 2025-08-25), no mention of Expel"},
      "last_funding_round": {
        "date": "2021-11-18 initial Series E ($140.3M), extended 2022-10-03 to $171.3M total", "stage": "Series E (extended)", "amount": "$171.3M total",
        "lead_investors": "CapitalG and Paladin Capital Group co-led; also Cisco Investments, March Capital, Index Ventures, Scale Venture Partners, Greycroft",
        "valuation": ">$1B (unicorn status)",
        "source_url": "https://expel.com/resource/expel-investors-fuel-rapid-growth-with-additional-series-e-investment-bringing-total-funding-to-288-million/"
      },
      "stated_arr_revenue": "Third-party aggregator (Getlatka) estimates ~$142.2M ARR for 2025 — NOT company-disclosed, marked unverified/secondary",
      "distress_last_12_months": [
        {"item": "Acquisition by CrowdStrike or anyone else", "finding": "none found — explicitly checked and found false"},
        {"item": "WARN Act notice / ratings action / layoffs / CEO-CFO departure", "finding": "none found"}
      ]
    },
    {
      "name": "eSentire, Inc.", "public_private": "private", "ticker": null, "sec_cik": null,
      "sec_filer_status": "No SEC filer found",
      "fiscal_year_end": "unverified",
      "investor_relations_url": "https://www.esentire.com/company/newsroom",
      "ownership": {"status": "PE-owned", "owner": "Warburg Pincus, majority since an initial 2017 investment (secondary source describes a move from ~75% to just over 50% after the 2022 round)", "date": "2017-08-21 initial investment (secondary); 2022-02-22 most recent confirmed primary-sourced round", "source_url": "https://www.esentire.com/news-releases/global-cybersecurity-leader-esentire-raises-us-325m-and-achieves-unicorn-status"},
      "last_funding_round": {"date": "2022-02-22", "stage": "growth equity", "amount": "$325M", "lead_investor": "Warburg Pincus-led, with Georgian and CDPQ", "valuation": "$1.1B (unicorn status)"},
      "stated_arr_revenue": "not found / unverified",
      "distress_last_12_months": [
        {"item": "CEO change to James C. Foster", "date": "reported ~2026-03-19", "status": "UNVERIFIED — found only via a search-result snippet, could not confirm against eSentire's own newsroom listing", "rung": "unverified, do not treat as confirmed"},
        {"item": "WARN Act notice / ratings action / layoffs", "finding": "none found"},
        {"item": "Acquired a stealth-mode AI security startup", "date": "2026-09-15", "note": "acquisition BY eSentire, not distress; included for completeness"}
      ]
    },
    {
      "name": "ReliaQuest, LLC", "public_private": "private", "ticker": null, "sec_cik": null,
      "sec_filer_status": "No SEC filer found",
      "fiscal_year_end": "unverified",
      "investor_relations_url": "https://reliaquest.com/news-and-press/",
      "ownership": {"status": "PE/growth-equity-backed", "owner": "KKR since a 2020 round; EQT and FTV Capital co-led the March 2025 round, with Ten Eleven Ventures and Finback Investment Partners participating", "date": "2025-03-31", "source_url": "https://reliaquest.com/news-and-press/reliaquest-raises-more-than-500-million-in-funding-at-a-valuation-of-3-4-billion/"},
      "last_funding_round": {"date": "2025-03-31", "amount": "more than $500M", "valuation": "$3.4B", "lead_investors": "EQT, KKR, FTV Capital"},
      "stated_arr_revenue": {"figure": "ARR surpassed $300M, growing more than 30% YoY, described as 'operating profitably'; company states ARR grew more than 4x since its 2020 KKR-led round", "as_of_date": "2025-03-31", "source_url": "https://reliaquest.com/news-and-press/reliaquest-raises-more-than-500-million-in-funding-at-a-valuation-of-3-4-billion/"},
      "distress_last_12_months": [
        {"item": "WARN Act notice / ratings action / layoffs / CEO-CFO departure", "finding": "none found"}
      ]
    },
    {
      "name": "Red Canary, Inc.", "public_private": "acquired — now a Zscaler business unit", "ticker": null, "sec_cik": "0001680152",
      "sec_filer_status": "No periodic filer as standalone entity, only Form D pre-acquisition. Post-acquisition financials consolidated into Zscaler, Inc. (CIK 1713683, ticker ZS, NASDAQ).",
      "fiscal_year_end": "Zscaler's FY ends July 31",
      "investor_relations_url": "https://ir.zscaler.com (post-acquisition)",
      "ownership": {
        "status": "acquired", "acquirer": "Zscaler, Inc.", "date_announced": "2025-05-27", "date_closed": "2025-08-01",
        "price": "$651.4M cash plus $20.2M restricted stock (contingent on continued employment); $544.5M goodwill; $162.5M identified intangibles (customer relationships $90.8M, developed tech $61.1M, trademarks $10.6M)",
        "source_announcement": "https://www.zscaler.com/press/zscaler-accelerate-innovation-ai-powered-security-operations-acquisition-red-canary",
        "source_financials_primary": "Zscaler Inc. Form 10-Q for period ended 2025-10-31, https://www.sec.gov/Archives/edgar/data/1713683/000171368325000205/zs-20251031.htm",
        "confirmation_note": "cross-verified against Zscaler's own SEC 10-Q — rung 1"
      },
      "distress_last_12_months": [
        {"item": "Acquired by Zscaler (ownership change)", "date": "announced 2025-05-27, closed 2025-08-01", "rung": 1, "source_url": "https://www.sec.gov/Archives/edgar/data/1713683/000171368325000205/zs-20251031.htm"},
        {"item": "Post-acquisition layoffs / WARN notice", "finding": "none found"}
      ]
    }
  ]
}
```
</details>

**Considered and left out (Domain 3):** CDW — large IT reseller with a security practice, but security is a minority of a much broader hardware/software resale business; also publicly traded, which would make it an outlier among the private, PE-backed specialists chosen. GuidePoint Security — a strong, fast-growing VAR/MSSP, but materially less public financial/ownership disclosure than the seven selected. World Wide Technology (WWT) — very large systems integrator; security is one practice area among several, not the core identity. Presidio — PE-owned (BC Partners) broad IT solutions provider where security is one line of business among several. All four excluded for the same reason: general-purpose integrators/resellers where security is a practice line, not the core business, versus the seven MDR/managed-security specialists a security leader would name first.

---

## Domain 4: Vulnerability and exposure management

Two flags worth noting up front: **Rapid7's restructuring is confirmed** exactly as expected (8-K Item 2.05, 2026-08-07, ~12% workforce cut, ~$10-11M charges), and it is not the only change there — a new CEO took over 2026-06-01 and four directors resigned 2026-08-27. **Ivanti's S&P rating snippet is internally inconsistent** ("downgraded to CCC from CC" — CCC sits above CC on S&P's scale, so a downgrade cannot run that direction) and could not be independently verified against a readable S&P page; the prior rating is unverified and the whole item should be treated as unconfirmed pending a readable source.

| Supplier | Public/Private | Latest footing figure (period) | Last round or ownership | Distress items (last 12 months) |
|---|---|---|---|---|
| Tenable Holdings, Inc. | Public (TENB) | Revenue $268.5M, +8.6% YoY (Q2 2026, ended 2026-06-30) | Independent public company | None found in 8-Ks. Raised $800M of 0.25% convertible notes due 2031, closed 2026-09-15 (rung 1; a debt raise, not a distress signal). |
| Qualys, Inc. | Public (QLYS) | Revenue $182.2M, +11% YoY (Q2 2026, ended 2026-06-30) | Independent public company | None found. The only Item 5.02 filing was routine annual-meeting business, 2026-06-10. |
| Rapid7, Inc. | Public (RPD) | Revenue $210.9M, -1.5% YoY; ARR $824.0M, -2.0% YoY (Q2 2026, ended 2026-06-30) | Independent public company | Rung 1: restructuring approved 2026-08-07 (~12% of staff, $10-11M charges). Rung 1: CEO change 2026-06-01 (Wael Mohamed replaces Corey Thomas, who becomes executive chairman). Rung 1: four directors resigned 2026-08-27. Revenue and ARR both shrinking; Q3 guided -5% to -4%. |
| Axonius, Inc. | Private, VC-backed | ARR above $200M in Q1 of fiscal 2027, announced 2026-05-19; company states "100% growth in two years" | Series E, $200M, March 2024, $2.6B post-money (secondary; no newer round found) | Rung 4 (company statement): CEO change — Dean Sysman (co-founder) moved to executive chairman, Joe Diamond interim CEO Feb 2026, permanent CEO 2026-05-19. No layoffs, debt, or shutdown found. |
| Ivanti, Inc. | Private, PE-owned | Revenue $189M, -11% YoY; ARR $778M, -1% YoY (Q2 2026) — SECONDARY ONLY, one outlet, not company-confirmed | Owned by Clearlake, Charlesbank, and TA Associates since the Jan 2017 LANDESK–HEAT merger; $350M new capital from existing lenders, maturities pushed to 2029, 2025-05-02 (just before window) | Rung 2 (seen only in blocked-site search snippets, internally inconsistent, unverified): S&P downgrade to CCC, 2026-06-01. Rung 5: ~$1.8B loan reported trading near 36 cents on the dollar. Rung 5: Bloomberg-cited engineer cuts, Feb 2026. Rung 5, unconfirmed rumor: ~100 layoffs, 2026-09-02. Moody's: none found. No CEO change found. |
| CrowdStrike Holdings, Inc. (Falcon Exposure Management) | Public (CRWD) — segment | Company-wide, not the exposure product: revenue $1.47B, +26% YoY; ARR $5.84B, +25% YoY (Q2 FY27, ended 2026-07-31). No figures disclosed for the exposure product specifically. | Independent public company | None found. Item 5.02 filings in window were routine executive stock-award grants only. |

<details><summary>Full JSON record — Domain 4</summary>

```json
{
  "retrieval_date_all_sources": "2026-09-25",
  "domain": "Vulnerability and exposure management",
  "method_note": "SEC EDGAR filing lists and 8-K exhibits opened directly. S&P, Moody's and Crunchbase pages returned 403 or had no readable content for several items — flagged individually. California WARN spreadsheets were not parsed this session, so WARN is 'not checked' rather than 'none found' except where noted.",
  "suppliers": [
    {
      "supplier": "Tenable Holdings, Inc.", "status": "public", "ticker": "TENB (Nasdaq)", "sec_cik": "0001660280",
      "filer_type": "domestic, 10-K/10-Q; Delaware; SIC 7372", "fiscal_year_end": "December 31",
      "ownership": "independent public company",
      "latest_quarter": {
        "period_end": "2026-06-30", "release_date": "2026-07-29",
        "revenue_usd_m": 268.5, "revenue_yoy_pct": 8.6,
        "headline_metric_caveat": "extraction reported $1,026.1M +15.4% YoY under a muddled label (current billings vs RPO) — verify the label before using it",
        "subscription_revenue_usd_m": 248.3,
        "q3_2026_guidance": "revenue $270.0M to $273.0M", "fy2026_guidance": "revenue $1.075B to $1.081B",
        "source": "https://www.sec.gov/Archives/edgar/data/0001660280/000166028026000032/q22026financialresults-ear.htm"
      },
      "prior_quarter_yoy_pct": "unverified; Q1 2026 release not opened this session",
      "next_report_date": "~2026-10-28 (secondary estimate, not company-confirmed)",
      "distress_last_12m": {
        "layoffs": "none found in SEC filings; WARN not checked", "restructuring_2_05": "none found",
        "debt": {"item": "$800M of 0.25% convertible senior notes due 2031, upsized from $725M, closed 2026-09-15", "rung": 1, "note": "capital-markets transaction, not a distress signal", "source": "https://www.sec.gov/Archives/edgar/data/1660280/000166028026000039/tenb-20260910.htm"},
        "ratings_action": "not checked", "going_concern": "none found",
        "ceo_cfo_change": "none found; no Item 5.02 8-Ks since 2025-09-25", "divestiture_shutdown": "none found"
      }
    },
    {
      "supplier": "Qualys, Inc.", "status": "public", "ticker": "QLYS (Nasdaq)", "sec_cik": "0001107843",
      "filer_type": "domestic, 10-K/10-Q; Delaware; SIC 7372", "fiscal_year_end": "December 31",
      "ownership": "independent public company",
      "latest_quarter": {
        "period_end": "2026-06-30", "release_date": "2026-08-04",
        "revenue_usd_m": 182.2, "revenue_yoy_pct": 11, "gaap_net_income_usd_m": 52.4,
        "q3_2026_guidance": "revenue $185.5M to $187.5M (+9% to +10%)", "fy2026_guidance": "revenue $732.0M to $738.0M, raised",
        "source": "https://www.sec.gov/Archives/edgar/data/0001107843/000110784326000034/qlys-20260804xex991.htm"
      },
      "prior_quarter_yoy_pct": "unverified; Q1 2026 release not opened this session",
      "next_report_date": "~2026-11-03 (secondary estimate)",
      "distress_last_12m": {
        "layoffs": "none found in SEC filings; WARN not checked", "restructuring_2_05": "none found", "debt": "none found",
        "ratings_action": "not checked", "going_concern": "none found",
        "ceo_cfo_change": "none found; the 2026-06-11 Item 5.02 8-K covered only routine annual-meeting equity plan approval",
        "divestiture_shutdown": "none found"
      }
    },
    {
      "supplier": "Rapid7, Inc.", "status": "public", "ticker": "RPD (Nasdaq)", "sec_cik": "0001560327",
      "filer_type": "domestic, 10-K/10-Q; Delaware; SIC 7372", "fiscal_year_end": "December 31",
      "ir_url": "https://investors.rapid7.com",
      "ownership": "independent public company",
      "latest_quarter": {
        "period_end": "2026-06-30", "release_date": "2026-08-10",
        "revenue_usd_m": 210.9, "revenue_yoy_pct": -1.5, "headline_metric": "ARR $824.0M, -2.0% YoY",
        "product_subscriptions_revenue_usd_m": 205.1, "gaap_operating_income_usd_m": 3.0, "non_gaap_operating_income_usd_m": 28.9,
        "q3_2026_guidance": "revenue $208M to $210M (-5% to -4% YoY); ARR ~$812M (-3% YoY)",
        "fy2026_guidance": "revenue $837M to $841M (-3% to -2% YoY); FCF ~$130M",
        "source": "https://www.sec.gov/Archives/edgar/data/0001560327/000156032726000043/q22026rapid78-kex991.htm"
      },
      "prior_quarter": {"period_end": "2026-03-31", "revenue_usd_m": 210, "revenue_yoy_pct": -0.3, "arr_usd_m": 832, "arr_yoy_pct": -0.6, "source": "https://www.sec.gov/Archives/edgar/data/0001560327/000156032726000032/q12026rapid78-kex991.htm"},
      "next_report_date": "not announced as of 2026-09-25",
      "distress_last_12m": {
        "restructuring_2_05": {"rung": 1, "event_date": "2026-08-07 (board approval)", "detail": "Workforce cut ~12%. $10M-$11M charges, mainly cash severance, notice-period pay, benefits. Non-cash accelerated vesting not expected to be significant. Most charges land Q3/Q4 2026; substantially complete by end of Q4 2026.", "source": "https://www.sec.gov/Archives/edgar/data/0001560327/000156032726000043/rp-20260807.htm"},
        "ceo_change": {"rung": 1, "date": "2026-06-01", "detail": "Wael Mohamed (board member since April 2025, former Forescout CEO) named CEO. Corey Thomas, CEO 13+ years, became executive chairman.", "source_press_release": "https://investors.rapid7.com/news/news-details/2026/Rapid7-Appoints-Wael-Mohamed-Chief-Executive-Officer-Corey-Thomas-to-Become-Executive-Chairman/default.aspx"},
        "board_change": {"rung": 1, "event_date": "2026-08-27", "filed": "2026-08-31", "detail": "Directors Michael Burns, Benjamin Holzman, Thomas Schodorf and Reeny Sondhi resigned, no disagreement stated; each gets cash comp through 2027-06-30 plus full equity acceleration. Maria Barrett and Julian Waits joined the board 2026-09-01. Board set at 9 seats; J. Benjamin Nye replaced Marc Brown as lead independent director.", "source": "https://www.sec.gov/Archives/edgar/data/0001560327/000156032726000046/rp-20260827.htm"},
        "layoffs_warn": "not checked", "ratings_action": "not checked", "going_concern": "none found",
        "cfo_change": "none found in the filing list read", "divestiture_shutdown": "none found",
        "edgar_filing_list": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001560327&type=8-K&dateb=&owner=include&count=20"
      }
    },
    {
      "supplier": "Axonius, Inc.", "status": "private, VC-backed", "sec_cik": "none (does not file)",
      "ownership": "independent; investors include Lightspeed, Accel, Bessemer (secondary)",
      "last_round": {"date": "2024-03 (~2024-03-05)", "type": "Series E / extension", "amount_usd_m": 200, "post_money_valuation_usd_b": 2.6, "lead_investor": "unverified", "source_type": "secondary (Tracxn, Crunchbase, search summaries), not confirmed from a company release", "newer_round": "none found; low confidence"},
      "company_stated_metric": {
        "figure": "ARR above $200M in Q1 of fiscal 2027; '100% growth in two years'", "date": "2026-05-19",
        "source": "https://www.axonius.com/newsroom/press-release/axonius-surpasses-200m-arr-appoints-joe-diamond-ceo",
        "also_states": "on track to be free-cash-flow positive in the near term",
        "note": "A single-year 35% growth figure appeared only in a secondary Calcalist search summary; the company release gives no single-year rate"
      },
      "distress_last_12m": {
        "ceo_change": {"rung": 4, "detail": "Joe Diamond: President from Aug 2025, interim CEO from Feb 2026, permanent CEO 2026-05-19. Co-founder Dean Sysman moved to executive chairman.", "source": "https://www.axonius.com/newsroom/press-release/axonius-surpasses-200m-arr-appoints-joe-diamond-ceo"},
        "layoffs": "none found; WARN not checked", "debt_ratings": "none found", "divestiture_shutdown": "none found"
      }
    },
    {
      "supplier": "Ivanti, Inc. (rated entity: Ivanti Software, Inc.)", "status": "private, PE-owned", "sec_cik": "none (no SEC-registered equity)",
      "ownership": {"owners": "Clearlake Capital Group, Charlesbank Capital Partners, TA Associates — all named as backing investors in the 2025-05-02 release", "origin": "Ivanti formed 2017-01-23 when LANDESK (bought by Clearlake from Thoma Bravo) merged with HEAT Software (a Clearlake company)", "ta_associates_entry_date": "unverified", "source": "https://en.wikipedia.org/wiki/Ivanti (secondary)"},
      "last_ownership_or_capital_transaction": {"date": "2025-05-02 (just outside the 12-month window)", "detail": "$350M new capital from existing first- and second-lien lenders; maturities extended to 2029", "source": "https://www.ivanti.com/company/press-releases/2025/ivanti-announces-successful-refinancing-and-new-capital-infusion-to-support-key-strategic-initiatives"},
      "stated_financials": {"q2_2026": "revenue $189M (-11% YoY); adjusted EBITDA $72M (-21%); ARR $778M (-1%)", "q1_2026": "revenue $204M (-4% YoY); adjusted EBITDA $87M (-13%); ARR $785M (flat)", "source": "https://www.briefs.co/news/ivanti-s-profit-slips-21-as-cybersecurity-firm-wrestles-with/ (published 2026-08-24)", "source_type": "SECONDARY, one outlet only, not confirmed by a second source or a company document"},
      "distress_last_12m": {
        "ratings_action_sp": {"rung": 2, "date": "2026-06-01", "detail": "S&P downgraded Ivanti Software Inc. to CCC; rationale reported as 'increased likelihood of default'", "caveat": "snippet reads 'to CCC from CC', which is inverted on S&P's scale (CCC sits above CC); prior rating unverified; not republished in Ivanti's own newsroom", "sources": ["spglobal.com article IDs seen only in search snippets, pages blocked (403)", "https://www.briefs.co/news/ivanti-s-profit-slips-21-as-cybersecurity-firm-wrestles-with/ (secondary)"]},
        "ratings_action_moodys": "none found in window; last seen B3 affirmed stable outlook 2021-02 (secondary, outside window)",
        "loan_pricing": {"rung": 5, "detail": "$1.8B loan reported trading around 36 cents on the dollar; reported by Briefs Finance, not confirmed in a filing"},
        "layoffs": [
          {"rung": 5, "date": "2026-02", "detail": "Bloomberg reported cuts to engineers on the Connect Secure VPN product; seen only as a citation inside a secondary source, original not located"},
          {"rung": 5, "date": "2026-09-02", "detail": "~100 layoffs US/India; unconfirmed rumor from a layoff tracker, original source not found", "source": "https://www.teamblind.com/layoffs/company/ivanti"}
        ],
        "warn_notice": "not checked; WARNTracker and layoffs.fyi showed no Ivanti entries",
        "restructuring_or_debt": "none found in window (refinancing was 2025-05, just outside window)",
        "going_concern": "not applicable (no public filings)",
        "ceo_cfo_change": "none found in window; Dennis Kozak has been CEO since 2025-01-01; CFO Peter De Bock's start date unverified",
        "divestiture_shutdown": "none found",
        "newsroom_checked": "https://www.ivanti.com/company/press-releases (no rating/restructuring/leadership releases in 2025-2026 beyond those listed)"
      }
    },
    {
      "supplier": "CrowdStrike Falcon Exposure Management (product line inside CrowdStrike Holdings, Inc.)", "status": "public parent",
      "ticker": "CRWD (Nasdaq)", "sec_cik": "0001535527", "filer_type": "domestic, 10-K/10-Q; Delaware; SIC 7372", "fiscal_year_end": "January 31",
      "ownership": "independent public company",
      "segment_disclosure": "None. No revenue, ARR, or customer counts disclosed for Falcon Exposure Management specifically; sold as a Falcon platform module.",
      "latest_quarter_company_wide": {
        "label": "COMPANY-WIDE, NOT SEGMENT", "period_end": "2026-07-31 (Q2 FY2027)", "release_date": "2026-08-26",
        "revenue_usd_b": 1.47, "revenue_yoy_pct": 26, "subscription_revenue_usd_b": 1.40, "subscription_yoy_pct": 27,
        "headline_metric": "ending ARR $5.84B, +25% YoY; net new ARR $332.8M; Falcon Flex ending ARR $2.29B",
        "q3_fy27_guidance": "revenue $1,523.2M to $1,529.2M", "fy27_guidance": "revenue $5,991.1M to $6,011.1M",
        "source": "https://www.sec.gov/Archives/edgar/data/0001535527/000153552726000029/crwd-20260826xex991.htm"
      },
      "prior_quarter_yoy_pct": "unverified; Q1 FY2027 release not opened this session",
      "distress_last_12m": {
        "layoffs": "none found in SEC filings; WARN not checked", "restructuring_2_05": "none found", "debt": "none found",
        "ratings_action": "not checked", "going_concern": "none found",
        "ceo_cfo_change": "none found; Item 5.02 8-Ks in window (2025-12-22, 2026-04-16) are routine stock-award grants to George Kurtz and Michael Sentonas; the 2026-06-22 8-K is routine annual-meeting/charter business",
        "divestiture_shutdown": "none found"
      }
    }
  ]
}
```
</details>

**Considered and left out (Domain 4):** HCL BigFix — a real competitor on endpoint patching/compliance, but a product line inside HCLTech with no separate financial footing to report; closest miss, worth adding if the tracked list grows. Nucleus Security — real player in vulnerability aggregation/prioritization but smaller and less recognized than the six chosen. Wiz (Google) — cloud exposure-management platform, now part of Google (deal announced 2025, close status not independently checked this session); would be a segment row like CrowdStrike with no separate figures. Recorded Future — threat intelligence feeding vulnerability programs rather than exposure discovery itself; also owned by Mastercard (background knowledge, not checked this pass). Nozomi Networks — OT/industrial asset visibility, a specialized neighboring market rather than general vulnerability management.

---

## Cross-domain notes on gaps and unverified items

- Prior-quarter YoY figures for Tenable, Qualys, and CrowdStrike (Domain 4 context) were not independently pulled this session — flagged as unverified rather than stated.
- California WARN spreadsheets (XLSX/PDF downloads) were not parsed for several private companies (Arctic Wolf, Expel, eSentire, ReliaQuest, Torq, Tines, Axonius, Ivanti); absence there is "not checked," distinct from the "none found" used where a search was actually run and returned nothing.
- Several rating-agency claims (Moody's and S&P for Sophos, Optiv, and Ivanti) rest on secondary republication or search snippets because the agencies' own sites blocked automated fetches during this session — consistent with the sourcing-ladder research's own finding that Moody's/S&P pages return HTTP 403 to scripts.
- The Ivanti S&P rating direction is internally inconsistent in the source snippet found and should not be published as a confirmed fact until read directly from a working S&P page or a republication.

## 300-word summary

Across the four domains, twenty-five supplier records were built, each checked against SEC EDGAR, company press releases, or investor pages first, with trade press used only where labelled. Two claims in the original brief turned out to be wrong: Expel was never acquired by CrowdStrike, and the Exabeam/LogRhythm merger closed in July 2024, not 2025. One claim was confirmed at the strongest possible level: Red Canary really was acquired, by Zscaler, verified directly against Zscaler's own SEC 10-Q.

The clearest distress signals sit in managed security and vulnerability management. Optiv carries a Moody's downgrade to Caa2 and a 2026 lender amendment pushing its debt wall to 2028-2029. Sophos has taken two rating-agency actions and seen lenders pass on a $2.5 billion refinancing before a March 2027 maturity. Rapid7 disclosed a 12% workforce cut in an August 2026 8-K alongside a CEO change and four board resignations, while its revenue and ARR are both shrinking year over year. Ivanti shows the weakest sourcing: its S&P rating claim is internally inconsistent and its recent revenue figures rest on a single secondary outlet, so both are flagged unverified rather than published as fact.

Several suppliers in these domains are segments inside larger public filers (Splunk inside Cisco, Google SecOps inside Alphabet, Cortex XDR/XSIAM inside Palo Alto Networks) with no separate financial disclosure — the parent's company-wide figures are given and clearly labelled as not segment-specific. Private companies without SEC obligations (Arctic Wolf, eSentire, Torq, Tines, Axonius) mostly lack recent company-stated revenue figures; where a figure exists only in secondary press, it is marked as such. WARN Act checks were incomplete for most private companies since state spreadsheets weren't parsed this session — recorded as "not checked" rather than "none found," which matters for anyone reading this as a clean record of absence.
