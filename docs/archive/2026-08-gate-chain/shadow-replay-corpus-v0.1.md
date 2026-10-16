# Shadow Collection Replay Corpus v0.1

## Control

- **Corpus ID:** `SEC-MARKET-SHADOW-CORPUS-001`
- **Version:** `0.1`
- **Lifecycle state:** `accepted for Gate S1 replay`
- **Source episode:** `SEC-MARKET-SIG-002` v0.2
- **Purpose:** Gate S1 replay oracle for the thin shadow slice
- **Authorization boundary:** accepted oracle only; does not authorize implementation or replay
- **Canonical oracle-manifest SHA-256:** `ca454cab21338d8569da835724a4183d64045cf6b63bd8acfb6d6c1af6de1755`
- **Definition-set SHA-256:** `0d46af448ade5d9c2dafa0ca2588d9924d591536894e5e500f88dc7e3ec6f9e4`
- **Replay cutoff:** `2026-08-15T19:17:24-07:00` — Episode 002 v0.2 review-correction boundary

The manifest hash is SHA-256 over these newline-terminated UTF-8 rows:

In `D` rows, `flow_reported` canonically serializes the two fields `flow_or_stock=flow` and `reported_or_adjusted=reported`.

```text
G|G-001|nvda|nvda|nvda.data_center_revenue.v1|82764702f44255a71d3d9c9f10201b8d69b226a458b57ce0ade7ba9fa502b308|2026-04-26|75246|millions|USD|10-q|sec_filing|0001045810-26-000052|2026-05-20|quarterly_results|https://www.sec.gov/Archives/edgar/data/1045810/000104581026000052/nvda-20260426.htm|market_platform_table_data_center|PROMOTE|PROMOTED|historical_raw_not_archived
G|G-002|msft|msft|msft.cash_ppe_additions.v1|41f0ee6c8f58da822d493c8a20888f504f6e3073c1e82a4262362a6925828fe3|2026-06-30|35802|millions|USD|ir_release|issuer_ir|msft-fy2026-q4-release|2026-07-29|quarterly_results|https://www.microsoft.com/en-us/Investor/earnings/FY-2026-Q4/press-release-webcast|cash_flow_ppe_additions_three_months|PROMOTE|PROMOTED|historical_raw_not_archived
G|G-003|amzn|amzn|amzn.gross_ppe_purchases.v1|d06bf9dd18135b4211c8d050eae233b02cb11162a2d18b8b3614fb22f60d3a68|2026-06-30|54208|millions|USD|ir_release|issuer_ir|amzn-q2-2026-release|2026-07-30|quarterly_results|https://ir.aboutamazon.com/news-release/news-release-details/2026/Amazon-com-Announces-Second-Quarter-Results/|cash_flow_gross_ppe_purchases_three_months|PROMOTE|PROMOTED|historical_raw_not_archived
G|G-004|goog|goog|goog.gross_ppe_purchases.v1|f6a5e5ecf43390dbbf6a1dbb8c0f9b978e1a20e072fdb9fd6a2461c5a374c514|2026-06-30|44924|millions|USD|sec_exhibit|sec_filing|0001652044-26-000066|2026-07-22|quarterly_results|https://www.sec.gov/Archives/edgar/data/1652044/000165204426000066/googexhibit991q22026.htm|cash_flow_ppe_purchases_three_months|PROMOTE|PROMOTED|historical_raw_not_archived
G|G-005|crwd|crwd|crwd.gaap_total_revenue.v1|b3ca1eeb21294a3bff7e62a43c7f2db33413c5dbf9f702ff9fcd55ae58c64210|2026-04-30|1386|millions|USD|sec_exhibit|sec_filing|0001535527-26-000022|2026-06-03|quarterly_results|https://www.sec.gov/Archives/edgar/data/1535527/000153552726000022/crwd-20260603xex991.htm|gaap_statement_total_revenue|PROMOTE|PROMOTED|source_rounded_usd_millions
G|G-006|ftnt|ftnt|ftnt.gaap_total_revenue.v1|b3ca1eeb21294a3bff7e62a43c7f2db33413c5dbf9f702ff9fcd55ae58c64210|2026-06-30|2047.9|millions|USD|ir_release|issuer_ir|ftnt-q2-2026-release|2026-07-29|quarterly_results|https://investor.fortinet.com/news-releases/news-release-details/fortinet-reports-strong-second-quarter-2026-financial-results|financial_highlights_total_revenue|PROMOTE|PROMOTED|historical_raw_not_archived
G|G-007|okta|okta|okta.gaap_total_revenue.v1|b3ca1eeb21294a3bff7e62a43c7f2db33413c5dbf9f702ff9fcd55ae58c64210|2026-04-30|765|millions|USD|sec_exhibit|sec_filing|0001660134-26-000050|2026-05-28|quarterly_results|https://www.sec.gov/Archives/edgar/data/1660134/000166013426000050/okta-4302026_ex991.htm|financial_highlights_total_revenue|PROMOTE|PROMOTED|source_rounded_usd_millions
D|nvda.data_center_revenue.v1|GAAP Data Center revenue|issuer_reported_quarterly_value|flow_reported|2023-04-30|82764702f44255a71d3d9c9f10201b8d69b226a458b57ce0ade7ba9fa502b308
D|msft.cash_ppe_additions.v1|Cash additions to property and equipment|cash_flow_line_three_month_period|flow_reported|2023-03-31|41f0ee6c8f58da822d493c8a20888f504f6e3073c1e82a4262362a6925828fe3
D|amzn.gross_ppe_purchases.v1|Gross purchases of property and equipment|cash_flow_before_proceeds_three_month_period|flow_reported|2023-03-31|d06bf9dd18135b4211c8d050eae233b02cb11162a2d18b8b3614fb22f60d3a68
D|goog.gross_ppe_purchases.v1|Purchases of property and equipment|cash_flow_line_three_month_period|flow_reported|2023-03-31|f6a5e5ecf43390dbbf6a1dbb8c0f9b978e1a20e072fdb9fd6a2461c5a374c514
D|crwd.gaap_total_revenue.v1|GAAP total revenue|issuer_reported_quarterly_value|flow_reported|2023-04-30|b3ca1eeb21294a3bff7e62a43c7f2db33413c5dbf9f702ff9fcd55ae58c64210
D|ftnt.gaap_total_revenue.v1|GAAP total revenue|issuer_reported_quarterly_value|flow_reported|2023-03-31|b3ca1eeb21294a3bff7e62a43c7f2db33413c5dbf9f702ff9fcd55ae58c64210
D|okta.gaap_total_revenue.v1|GAAP total revenue|issuer_reported_quarterly_value|flow_reported|2023-04-30|b3ca1eeb21294a3bff7e62a43c7f2db33413c5dbf9f702ff9fcd55ae58c64210
```

## Oracle boundary

Episode 002 preserved canonical URLs, exact values, locators, excerpts, and packet hashes. It did not archive full source-page bytes.

Replay therefore must match:

- entity;
- metric and definition version;
- economic period end;
- value, unit, and currency;
- canonical source origin;
- source locator or exact excerpt;
- primary-versus-context disposition; and
- expected limitation.

Replay does **not** require a raw-byte hash match to the historical Episode 002 retrieval. It records a new raw-artifact hash and fails if the canonical source no longer supports the known answer.

## Primary known-answer rows

All values use `currency=USD` and `unit=millions`.

| Gold ID | Publisher / entity ID | Metric ID | Period end | Value | Document type / source family | Origin ID | Published at | Event type | Canonical source | Exact excerpt or table locator | S1 action / state | Limitation |
|---|---|---|---:|---:|---|---|---:|---|---|---|---|---|
| G-001 | `nvda` / `nvda` | `nvda.data_center_revenue.v1` | 2026-04-26 | 75,246 | `10-q` / `sec_filing` | `0001045810-26-000052` | 2026-05-20 | `quarterly_results` | [NVIDIA Q1 FY27 10-Q](https://www.sec.gov/Archives/edgar/data/1045810/000104581026000052/nvda-20260426.htm) | market-platform revenue table: `Data Center = 75,246` USD millions | `PROMOTE` / `PROMOTED` | historical raw bytes were not archived |
| G-002 | `msft` / `msft` | `msft.cash_ppe_additions.v1` | 2026-06-30 | 35,802 | `ir_release` / `issuer_ir` | `msft-fy2026-q4-release` | 2026-07-29 | `quarterly_results` | [Microsoft FY2026 Q4](https://www.microsoft.com/en-us/Investor/earnings/FY-2026-Q4/press-release-webcast) | cash-flow statement: `Additions to property and equipment (35,802)` for three months | `PROMOTE` / `PROMOTED` | historical raw bytes were not archived |
| G-003 | `amzn` / `amzn` | `amzn.gross_ppe_purchases.v1` | 2026-06-30 | 54,208 | `ir_release` / `issuer_ir` | `amzn-q2-2026-release` | 2026-07-30 | `quarterly_results` | [Amazon Q2 2026](https://ir.aboutamazon.com/news-release/news-release-details/2026/Amazon-com-Announces-Second-Quarter-Results/) | cash-flow statement: `Purchases of property and equipment (54,208)` for three months | `PROMOTE` / `PROMOTED` | historical raw bytes were not archived |
| G-004 | `goog` / `goog` | `goog.gross_ppe_purchases.v1` | 2026-06-30 | 44,924 | `sec_exhibit` / `sec_filing` | `0001652044-26-000066` | 2026-07-22 | `quarterly_results` | [Alphabet Q2 2026 exhibit](https://www.sec.gov/Archives/edgar/data/1652044/000165204426000066/googexhibit991q22026.htm) | cash-flow statement: `Purchases of property and equipment (44,924)` for three months | `PROMOTE` / `PROMOTED` | historical raw bytes were not archived |
| G-005 | `crwd` / `crwd` | `crwd.gaap_total_revenue.v1` | 2026-04-30 | 1,386 | `sec_exhibit` / `sec_filing` | `0001535527-26-000022` | 2026-06-03 | `quarterly_results` | [CrowdStrike Q1 FY27](https://www.sec.gov/Archives/edgar/data/1535527/000153552726000022/crwd-20260603xex991.htm) | GAAP statement: total revenue, rounded to source-reported USD millions | `PROMOTE` / `PROMOTED` | source value rounded to nearest USD million |
| G-006 | `ftnt` / `ftnt` | `ftnt.gaap_total_revenue.v1` | 2026-06-30 | 2,047.9 | `ir_release` / `issuer_ir` | `ftnt-q2-2026-release` | 2026-07-29 | `quarterly_results` | [Fortinet Q2 2026](https://investor.fortinet.com/news-releases/news-release-details/fortinet-reports-strong-second-quarter-2026-financial-results) | financial highlights: total revenue `$2,047.9 million` | `PROMOTE` / `PROMOTED` | historical raw bytes were not archived |
| G-007 | `okta` / `okta` | `okta.gaap_total_revenue.v1` | 2026-04-30 | 765 | `sec_exhibit` / `sec_filing` | `0001660134-26-000050` | 2026-05-28 | `quarterly_results` | [Okta Q1 FY27](https://www.sec.gov/Archives/edgar/data/1660134/000166013426000050/okta-4302026_ex991.htm) | financial highlights: total revenue `$765 million` | `PROMOTE` / `PROMOTED` | source value rounded to nearest USD million |

## Metric-definition seeds

| Metric ID | Name | Formula | Class | Effective from | Definition hash |
|---|---|---|---|---:|---|
| `nvda.data_center_revenue.v1` | GAAP Data Center revenue | issuer-reported quarterly value | flow / reported | 2023-04-30 | `82764702f44255a71d3d9c9f10201b8d69b226a458b57ce0ade7ba9fa502b308` |
| `msft.cash_ppe_additions.v1` | Cash additions to property and equipment | cash-flow line, three-month period | flow / reported | 2023-03-31 | `41f0ee6c8f58da822d493c8a20888f504f6e3073c1e82a4262362a6925828fe3` |
| `amzn.gross_ppe_purchases.v1` | Gross purchases of property and equipment | cash-flow line before proceeds, three-month period | flow / reported | 2023-03-31 | `d06bf9dd18135b4211c8d050eae233b02cb11162a2d18b8b3614fb22f60d3a68` |
| `goog.gross_ppe_purchases.v1` | Purchases of property and equipment | cash-flow line, three-month period | flow / reported | 2023-03-31 | `f6a5e5ecf43390dbbf6a1dbb8c0f9b978e1a20e072fdb9fd6a2461c5a374c514` |
| `crwd.gaap_total_revenue.v1` | GAAP total revenue | issuer-reported quarterly value | flow / reported | 2023-04-30 | `b3ca1eeb21294a3bff7e62a43c7f2db33413c5dbf9f702ff9fcd55ae58c64210` |
| `ftnt.gaap_total_revenue.v1` | GAAP total revenue | issuer-reported quarterly value | flow / reported | 2023-03-31 | `b3ca1eeb21294a3bff7e62a43c7f2db33413c5dbf9f702ff9fcd55ae58c64210` |
| `okta.gaap_total_revenue.v1` | GAAP total revenue | issuer-reported quarterly value | flow / reported | 2023-04-30 | `b3ca1eeb21294a3bff7e62a43c7f2db33413c5dbf9f702ff9fcd55ae58c64210` |

## Pinned live document families

| Entity ID | S2/S3 pinned family | Start event |
|---|---|---|
| `nvda` | `10-q` | first NVIDIA 10-Q published after `2026-08-15T19:17:24-07:00` |
| `msft` | `ir_release` | first Microsoft quarterly IR release published after the cutoff |
| `amzn` | `ir_release` | first Amazon quarterly IR release published after the cutoff |
| `goog` | `sec_exhibit` | first Alphabet quarterly SEC earnings exhibit published after the cutoff |
| `crwd` | `sec_exhibit` | first CrowdStrike quarterly SEC earnings exhibit published after the cutoff |
| `ftnt` | `ir_release` | first Fortinet quarterly IR release published after the cutoff |
| `okta` | `sec_exhibit` | first Okta quarterly SEC earnings exhibit published after the cutoff |

## Expected replay outputs

- **Reporting events:** 7
- **Primary expected observations:** 7
- **Primary candidate facts:** 7
- **Secondary facts:** 0
- **Expected source omissions:** 0
- **Expected metric-definition changes:** 0
- **Expected acquisition quarantines:** 0
- **Expected human actions:** 7 `PROMOTE`
- **Expected terminal states:** 7 `PROMOTED`

## Permitted nondeterminism

- retrieval timestamp;
- retrieval-attempt ID;
- redirect chain where the canonical content remains identical;
- raw-artifact hash when the publisher changes non-substantive page bytes; and
- parser or agent attempt IDs.

Any difference in entity, metric definition, period, value, unit, source origin, locator meaning, or disposition fails replay.

## Excluded from S1–S3

- Broadcom, HPE, Cloudflare, Rubrik, Varonis, Cisco Security, and secondary Episode 002 context;
- orders, backlog, ARR, RPO, cRPO, billings, guidance, surveys, incidents, regulation, and acquisitions as candidate facts;
- derived lag, category, or posture judgments; and
- all client, ePlus, CRM, pipeline, or non-public data.

Acquisition and definition changes may be attached only as required blocking metadata on a primary fact.

