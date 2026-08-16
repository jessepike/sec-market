# Market Signal Episode 002 — Sparse Quarterly Panel

## Control

- **Panel ID:** `SEC-MARKET-SIG-PANEL-002`
- **Version:** `0.2`
- **Lifecycle state:** `sealed — independently verified`
- **Episode:** `SEC-MARKET-SIG-002`
- **Research freeze:** `2026-08-15T19:03:08-07:00`
- **Purpose:** expose the period-end series used to describe the sequence; not a fitted lag model

## Alignment rules

- Actual company `period_end` remains canonical in the evidence ledger.
- Reporting periods ending in January align to the preceding calendar Q4; April to Q1; July to Q2; and October to Q3.
- No interpolation, carry-forward, or zero substitution.
- `—` means unavailable, unreported by the freeze, or intentionally uncollected for this descriptive panel; it never means zero.
- Values are in USD billions unless the table says USD millions.
- Company-defined metrics remain separate and are not additive.
- No approximate marker is used; values are rounded from the cited source precision.

## Infrastructure-supplier panel

Only NVIDIA exposes a complete, stable quarterly AI/data-center revenue series across the full window.

| Aligned quarter | NVIDIA Data Center revenue |
|---|---:|
| 2023-Q1 | 4.28 |
| 2023-Q2 | 10.32 |
| 2023-Q3 | 14.51 |
| 2023-Q4 | 18.40 |
| 2024-Q1 | 22.56 |
| 2024-Q2 | 26.27 |
| 2024-Q3 | 30.77 |
| 2024-Q4 | 35.58 |
| 2025-Q1 | 39.11 |
| 2025-Q2 | 41.10 |
| 2025-Q3 | 51.22 |
| 2025-Q4 | 62.31 |
| 2026-Q1 | 75.25 |
| 2026-Q2 | — |

Supplemental irregular observations:

| Metric | Earlier observation | Latest frozen observation |
|---|---|---|
| Arista total revenue | $1.351B, period ended 2023-03-31 | $3.036B, period ended 2026-06-30 |
| Dell AI-server revenue | $2.026B, period ended 2025-01-31 | $16.132B, period ended 2026-05-01 |
| Dell AI-server shipments | $0.8B, period ended 2024-02-02 | not used as revenue |
| Vertiv sales | $1.865B, period ended 2023-12-31 | $3.274B, period ended 2026-06-30 |
| Cisco AI-infrastructure orders | cumulative >$1B by period ended 2024-07-27 | $9.3B FY2026; $4.0B in Q4 |
| Dell AI-server backlog | $2.9B, period ended 2024-02-02 | $51.3B, period ended 2026-05-01 |
| Vertiv backlog | $5.5B, 2023 year-end | $15.0B, 2025 year-end |
| Broadcom AI revenue | $8.4B, period ended 2026-02-01 | $10.8B, period ended 2026-05-03 |

## Hyperscaler cash-investment panel

Microsoft cash additions and Amazon/Alphabet gross purchases of property and equipment. Definitions remain company-specific. Meta is excluded from the quarterly grid because its reported-capex definition combines PP&E purchases with finance-lease principal and changed presentation during the window.

| Aligned quarter | Microsoft | Amazon gross | Alphabet |
|---|---:|---:|---:|
| 2023-Q1 | 6.61 | 14.21 | 6.29 |
| 2023-Q2 | 8.94 | 11.46 | 6.89 |
| 2023-Q3 | 9.92 | 12.48 | 8.06 |
| 2023-Q4 | 9.74 | 14.59 | 11.02 |
| 2024-Q1 | 10.95 | 14.93 | 12.01 |
| 2024-Q2 | 13.87 | 17.62 | 13.19 |
| 2024-Q3 | 14.92 | 22.62 | 13.06 |
| 2024-Q4 | 15.80 | 27.83 | 14.28 |
| 2025-Q1 | 16.75 | 25.02 | 17.20 |
| 2025-Q2 | 17.08 | 32.18 | 22.45 |
| 2025-Q3 | 19.39 | 35.10 | 23.95 |
| 2025-Q4 | 29.88 | 39.52 | 27.85 |
| 2026-Q1 | 30.88 | 44.20 | 35.67 |
| 2026-Q2 | 35.80 | 54.21 | 44.92 |

Oracle publishes a stable trailing-twelve-month capex series rather than a comparable standalone quarterly series:

| Period end | Oracle TTM GAAP capex |
|---|---:|
| 2024-05-31 | 6.87 |
| 2025-05-31 | 21.22 |
| 2026-05-31 | 55.66 |

## Cybersecurity revenue panel

USD millions. The panel exposes raw revenue; acquisition and transition interpretation remains in the evidence ledger.

| Aligned quarter | CrowdStrike | Okta | Fortinet | Zscaler | Check Point |
|---|---:|---:|---:|---:|---:|
| 2023-Q1 | 692.6 | 518 | 1,262.3 | 418.8 | 566 |
| 2023-Q2 | 731.6 | 556 | 1,292.8 | 455.0 | 589 |
| 2023-Q3 | 786.0 | 584 | 1,334.6 | 496.7 | 596 |
| 2023-Q4 | 845.3 | 605 | 1,415.1 | 525.0 | 664 |
| 2024-Q1 | 921.0 | 617 | 1,353.3 | 553.2 | 599 |
| 2024-Q2 | 963.9 | 646 | 1,434.3 | 592.9 | 627.4 |
| 2024-Q3 | 1,010.2 | 665 | 1,508.1 | 628.0 | 635.1 |
| 2024-Q4 | 1,059 | 682 | 1,660.1 | 647.9 | 704 |
| 2025-Q1 | 1,103 | 688 | 1,539.7 | 678.0 | 638 |
| 2025-Q2 | 1,169 | 728 | 1,630.0 | 719.2 | 665 |
| 2025-Q3 | 1,234 | 742 | — | — | 678 |
| 2025-Q4 | 1,305 | 761 | 1,905.0 | — | 745 |
| 2026-Q1 | 1,386 | 765 | — | 850.5 | 668 |
| 2026-Q2 | — | — | 2,047.9 | — | 673.6 |

Collection gaps rather than publication gaps: Fortinet 2025-Q3 and 2026-Q1; Zscaler 2025-Q3 and 2025-Q4. These cells are not used in a lag calculation, and their absence is one reason the panel fails the complete acquisition-adjusted security-series requirement.

Supplemental security observations:

| Metric | Latest frozen observation | Comparability warning |
|---|---|---|
| Palo Alto revenue | $3.00B, period ended 2026-04-30; +31% reported, ~+14% ex-CyberArk/Chronosphere | acquisitions materially affect growth |
| Cisco Security revenue | $2.23B, period ended 2026-07-25; +14% Q4, +2% FY2026 | Splunk embedded; not an organic Cisco-security series |
| Cloudflare revenue | $696.1M, period ended 2026-06-30; +36% | not security-pure |
| Rubrik subscription ARR | $1.57B, period ended 2026-04-30; +32% | short public history |
| Varonis SaaS ARR | $726M, period ended 2026-06-30; +52% headline, ~+25% ex-conversions | transition-distorted |

## Buyer-budget and deployment panel

Annual observations remain separate from quarterly financial data.

| Year | IANS average security-budget growth | IANS security share of IT | McKinsey/Flexera AI deployment context |
|---:|---:|---:|---|
| 2023 | 6% | 11.6% | approximately one-third regularly using GenAI |
| 2024 | 8% | 11.9% restated | 65% regularly using GenAI; 72% using AI |
| 2025 | 4% | 10.9% | 88% use AI somewhere; most still pilot/experiment |
| 2026 | unavailable at freeze | unavailable | Flexera: 81% GenAI use; ETR: 32% already spending on AI-security tools |

IANS’s contemporaneous 2024 report stated 13.2 percent; its 2025 report restated 2024 to 11.9 percent in the consistent historical series used here.

## Panel sufficiency

| Requirement | Result |
|---|---|
| Complete 2023-Q1 through 2026-Q1 supplier AI-specific panel | Fails — only NVIDIA is complete |
| Complete hyperscaler cash panel | Passes for Microsoft, Amazon, and Alphabet; Meta excluded for definition drift; Oracle remains TTM |
| Complete acquisition-adjusted security panel | Fails — raw revenue is broad, organic bridges are irregular |
| Ten or more complete paired observations at long lags | Fails |
| Two mature infrastructure impulses with downstream outcomes | Fails — second impulse right-censored |

The panel supports breadth and turning-point description. It does not support a stable lag estimate.

## Cell-source map

The panel is a descriptive appendix. No correlation, lag band, or posture is calculated directly from its cells. Load-bearing claims are promoted separately into `SEC-MARKET-SIG-SRC-002`.

The supplemental Arista, Dell, Vertiv, Cisco, and Broadcom observations map to evidence-ledger claims A2–A6 and their atomic source-manifest entries rather than duplicating those links below.

### NVIDIA

- 2023-Q1: [Q1 FY24](https://investor.nvidia.com/news/press-release-details/2023/NVIDIA-Announces-Financial-Results-for-First-Quarter-Fiscal-2024/)
- 2023-Q2: [Q2 FY24](https://investor.nvidia.com/news/press-release-details/2023/NVIDIA-Announces-Financial-Results-for-Second-Quarter-Fiscal-2024/default.aspx)
- 2023-Q3: [Q3 FY24](https://www.sec.gov/Archives/edgar/data/1045810/000104581023000225/q3fy24pr.htm)
- 2023-Q4: [Q4 FY24](https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-fourth-quarter-and-fiscal-2024)
- 2024-Q1: [Q1 FY25 10-Q market table](https://www.sec.gov/Archives/edgar/data/1045810/000104581024000124/R21.htm)
- 2024-Q2: [Q2 FY25](https://investor.nvidia.com/news/press-release-details/2024/NVIDIA-Announces-Financial-Results-for-Second-Quarter-Fiscal-2025/default.aspx)
- 2024-Q3: [Q3 FY25](https://investor.nvidia.com/news/press-release-details/2024/NVIDIA-Announces-Financial-Results-for-Third-Quarter-Fiscal-2025/default.aspx)
- 2024-Q4: [Q4 FY25](https://investor.nvidia.com/news/press-release-details/2025/NVIDIA-Announces-Financial-Results-for-Fourth-Quarter-and-Fiscal-2025/default.aspx)
- 2025-Q1 through 2026-Q1: [Q1 FY27 10-Q comparative table](https://www.sec.gov/Archives/edgar/data/1045810/000104581026000052/nvda-20260426.htm)

### Hyperscalers

- Microsoft: [FY2023 Q3](https://www.microsoft.com/en-us/investor/earnings/FY-2023-Q3/press-release-webcast), [FY2023 Q4](https://www.microsoft.com/en-us/investor/earnings/FY-2023-Q4/press-release-webcast), [FY2024 Q2](https://www.microsoft.com/en-us/investor/earnings/FY-2024-Q2/press-release-webcast), [FY2024 Q4](https://www.microsoft.com/en-us/investor/earnings/FY-2024-Q4/press-release-webcast), [FY2025 Q3](https://www.microsoft.com/en-us/investor/earnings/FY-2025-Q3/press-release-webcast), [FY2025 Q4](https://www.microsoft.com/en-us/investor/earnings/FY-2025-Q4/press-release-webcast), [FY2026 Q1](https://www.microsoft.com/en-us/investor/earnings/FY-2026-Q1/press-release-webcast), [FY2026 Q2](https://www.microsoft.com/en-us/investor/earnings/FY-2026-Q2/press-release-webcast), [FY2026 Q3](https://www.microsoft.com/en-us/investor/earnings/FY-2026-Q3/press-release-webcast), [FY2026 Q4](https://www.microsoft.com/en-us/Investor/earnings/FY-2026-Q4/press-release-webcast)
- Amazon: [2023 Q1 10-Q](https://www.sec.gov/Archives/edgar/data/1018724/000101872423000008/amzn-20230331.htm), [2023 Q2 exhibit](https://www.sec.gov/Archives/edgar/data/1018724/000101872423000010/amzn-20230630xex991.htm), [2023 Q3 exhibit](https://www.sec.gov/Archives/edgar/data/1018724/000101872423000016/amzn-20230930xex991.htm), [2025 Q3 comparative release](https://ir.aboutamazon.com/news-release/news-release-details/2025/Amazon-com-Announces-Third-Quarter-Results/), [2026 Q2 release](https://ir.aboutamazon.com/news-release/news-release-details/2026/Amazon-com-Announces-Second-Quarter-Results/)
- Alphabet: [2023 Q1](https://www.sec.gov/Archives/edgar/data/1652044/000165204423000041/googexhibit991q12023.htm), [2023 Q2](https://www.sec.gov/Archives/edgar/data/1652044/000165204423000067/googexhibit991q22023.htm), [2023 Q3](https://www.sec.gov/Archives/edgar/data/1652044/000165204423000088/googexhibit991q32023.htm), [2026 Q2 comparative table](https://www.sec.gov/Archives/edgar/data/1652044/000165204426000066/googexhibit991q22026.htm)

### Cybersecurity vendors

- CrowdStrike: quarterly SEC exhibits from the [investor-relations financials archive](https://ir.crowdstrike.com/financial-information/quarterly-results), with the latest values confirmed in [Q1 FY27](https://www.sec.gov/Archives/edgar/data/1535527/000153552726000022/crwd-20260603xex991.htm)
- Okta: quarterly SEC exhibits from the [investor-relations results archive](https://investor.okta.com/financial-information/quarterly-results), with the latest values confirmed in [Q1 FY27](https://www.sec.gov/Archives/edgar/data/1660134/000166013426000050/okta-4302026_ex991.htm)
- Fortinet: [2023 Q1](https://www.sec.gov/Archives/edgar/data/1262039/000126203923000013/ftntq1-2023ex991.htm), [2023 Q2](https://www.sec.gov/Archives/edgar/data/1262039/000126203923000027/ftntq2-2023ex991.htm), [2023 Q3](https://www.sec.gov/Archives/edgar/data/1262039/000126203923000035/ftntq3-2023ex991.htm), [2023 Q4](https://www.sec.gov/Archives/edgar/data/1262039/000126203924000006/ftntq4-2023ex991.htm), [2024 Q2](https://www.sec.gov/Archives/edgar/data/1262039/000126203924000034/ftntq2-2024ex991corrected.htm), [2026 Q2](https://investor.fortinet.com/news-releases/news-release-details/fortinet-reports-strong-second-quarter-2026-financial-results)
- Zscaler: [2023 Q1](https://www.sec.gov/Archives/edgar/data/1713683/000171368323000049/zs-05082023_991.htm), 2023 Q2 from the [quarterly-results archive](https://ir.zscaler.com/financial-information/quarterly-results), [2023 Q3](https://www.sec.gov/Archives/edgar/data/1713683/000171368323000156/zs-10312023_991.htm), [2023 Q4](https://www.sec.gov/Archives/edgar/data/1713683/000171368324000036/zs-01312024_991.htm), [2024 Q1](https://www.sec.gov/Archives/edgar/data/1713683/000171368324000072/zs-04302024_991.htm), [2024 Q2](https://www.sec.gov/Archives/edgar/data/1713683/000171368324000097/zs-07312024_991.htm), [2024 Q3](https://www.sec.gov/Archives/edgar/data/1713683/000171368324000143/zs-10312024_991.htm), [2024 Q4](https://www.sec.gov/Archives/edgar/data/1713683/000171368325000025/zs-01312025_991.htm), [2026 Q1](https://www.sec.gov/Archives/edgar/data/1713683/000171368326000095/zs-04302026_991.htm)
- Check Point: [2024 Q2](https://www.checkpoint.com/downloads/investor/check-point-software-2nd-quarter-2024-financial-results.pdf?v=1.3), [2024 Q3](https://www.sec.gov/Archives/edgar/data/1015922/000117891324003393/zk2432188.htm), and the company’s [investor-relations archive](https://www.checkpoint.com/about-us/investor-relations/)


