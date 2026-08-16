# Market Signal Episode 002 — Baseline and Lag Scorecard

## Control

- **Baseline ID:** `SEC-MARKET-SIG-BL-002`
- **Version:** `0.2`
- **Lifecycle state:** `accepted`
- **Episode:** `SEC-MARKET-SIG-002`
- **Evidence:** `SEC-MARKET-SIG-EV-002`
- **Research freeze:** `2026-08-15T19:03:08-07:00`
- **Window:** 2023-Q1 through latest public quarter before the freeze
- **Primary analysis endpoint:** 2026-Q1; 2026-Q2 is a ragged nowcast
- **Review correction:** `2026-08-15T19:17:24-07:00`

## Method

The public window is too short for a stable fitted lag. At most fourteen aligned quarters exist; an eight-quarter lag leaves six raw pairs before missing data, acquisitions, and autocorrelation.

The episode therefore uses:

1. exploratory turning points that describe the observed sequence but do not estimate a lag;
2. breadth across independent entities;
3. acquisition-adjusted vendor interpretation;
4. buyer-budget and deployment corroboration; and
5. cross-correlation only as a diagnostic when ten or more complete pairs exist.

No constant lag or causal coefficient is reported.

For the next test:

- **Fixed supplier cohort:** NVIDIA, Cisco, Arista, Dell, Vertiv
- **Fixed hyperscaler cohort:** Microsoft, Amazon, Alphabet, Meta, Oracle
- **Fixed security cohort:** Palo Alto Networks, CrowdStrike, Fortinet, Zscaler, Check Point, Okta
- **Supplier metric map:** NVIDIA Data Center revenue; Cisco Networking product revenue; Arista total revenue; Dell Servers and Networking revenue; Vertiv organic net sales
- **Hyperscaler metric map:** Microsoft cash additions to PP&E; Amazon gross purchases of PP&E; Alphabet purchases of PP&E; Meta gross purchases of PP&E excluding finance-lease principal; Oracle TTM GAAP capex reported at each quarter end
- **Security metric map:** GAAP total revenue for each fixed security company, with company-disclosed acquisition contributions removed when available
- **Flow transformation:** `g(i,t) = 100 × (x(i,t) / x(i,t-4) - 1)`
- **Acceleration:** `a(i,t) = g(i,t) - g(i,t-1)` in percentage points
- **Missing data:** no interpolation, carry-forward, or zero substitution
- **Definition-change rule:** quarantine an entity when the metric definition changes or acquired revenue is at least 5 percent of the metric or changes growth by at least 2 percentage points; restore it only with a company-disclosed comparable bridge or after a full YoY base exists
- **Quarterly quorum:** 4/5 suppliers, 4/5 hyperscalers, and 5/6 security vendors
- **Impulse condition:** positive median acceleration and strict-majority positive breadth in both supplier and hyperscaler cohorts for two consecutive aligned quarters
- **Security-response condition:** positive acquisition-adjusted median acceleration and strict-majority breadth for two consecutive aligned quarters, plus buyer corroboration
- **Buyer corroboration:** IANS must show both higher security-budget growth and higher security share of IT than its prior comparable report; alternatively, two independent method-consistent realized-spend sources must each improve by at least 2 percentage points from their prior reading. Planned-spend intent does not qualify.

Only observations published after the v0.2 correction can establish the prospective T0. The already observed late-2025/2026 sequence remains exploratory and cannot be promoted retroactively into the registered test.

The first prospective impulse-response pair can support only one-cycle sequencing. A stable lag requires a second prospective pair landing in the same broad band (`0`, `1–2`, `3–5`, or `6–8` quarters) under the same cohorts, metrics, and rules.

## Metric boundaries

| Layer | Primary quantitative signal | Secondary signal | Excluded from pooled series |
|---|---|---|---|
| Infrastructure suppliers | within-company YoY revenue growth and acceleration | orders, backlog, book-to-bill, guidance | mixed dollar levels and company-defined AI order totals; NVIDIA revenue, Cisco orders, Dell shipments/backlog, and Vertiv orders are not one comparable metric |
| Hyperscalers | within-company cash-capex growth | finance leases, cloud growth, RPO/backlog | a summed “hyperscaler capex” total |
| Cybersecurity | acquisition-adjusted revenue growth and breadth | ARR, RPO, cRPO, billings | pooled ARR/RPO/billings across vendors |
| Buyer demand | CISO budget growth and share of IT | category intent, deployment, hiring | analyst TAM spliced across definition changes |

## Infrastructure baseline

### Supplier layer

| Signal | Early baseline | Latest frozen observation | Direction |
|---|---|---|---|
| NVIDIA Data Center revenue | $4.28B, period ended 2023-04-30 | $75.25B, period ended 2026-04-26; +92% YoY, +21% sequential | Accelerating in absolute dollars |
| Cisco AI-infrastructure orders | cumulative >$1B by period ended 2024-07-27 | $9.3B FY2026; $4.0B in Q4 | Accelerating after destock |
| Arista revenue | $1.35B, period ended 2023-03-31 | $3.04B, period ended 2026-06-30; +37.7% YoY | Accelerating |
| Dell AI-server backlog | $2.9B, period ended 2024-02-02 | $51.3B, period ended 2026-05-01 | Accelerating; conversion constrained |
| Vertiv backlog | $5.5B, 2023 year-end | $15.0B, 2025 year-end; last comparable print | Accelerating; later disclosure incomplete |
| Broadcom AI-semiconductor revenue | $8.4B, period ended 2026-02-01 | $10.8B, period ended 2026-05-03; next-quarter guide $16B | Accelerating; short series |

### Hyperscaler demand context

| Company | 2023 own-metric baseline | 2024 | 2025 | Latest frozen direction |
|---|---:|---:|---:|---|
| Microsoft cash PP&E additions | $28.1B FY | $44.5B FY | $64.6B FY | $115.9B FY2026; accelerating |
| Amazon gross PP&E purchases | $52.7B FY | $83.0B FY | $131.8B FY | $98.4B H1 2026; accelerating |
| Alphabet cash PP&E purchases | $32.3B FY | $52.5B FY | ~$91.4B FY | $80.6B H1 2026; accelerating |
| Meta reported capex | $28.1B FY | $39.2B FY | $72.2B FY | $50.9B H1 2026; accelerating |
| Oracle GAAP capex | $6.9B FY2024 | — | $21.2B FY2025 | $55.7B FY2026; accelerating |

These measures are not additive. They establish breadth and direction only.

Fiscal calendars differ: Microsoft’s annual periods end in June, Oracle’s in May, and Amazon, Alphabet, and Meta use calendar years. “Latest” also mixes full-year Microsoft/Oracle observations with H1 Amazon/Alphabet/Meta observations. The table is a within-company direction check, not a cross-company level comparison.

## Cybersecurity baseline

### Representative forward and operating metrics

| Vendor | 2023–2024 pattern | Latest frozen pattern | Primary interpretation |
|---|---|---|---|
| CrowdStrike | ARR growth decelerated from 48% toward the low twenties; 2024 outage created a vendor-specific shock | Revenue ~+26%; ARR +24% | Platform demand re-accelerating |
| Palo Alto Networks | 2024 platformization deliberately reduced billings growth | +31% reported revenue, ~+14% ex-major acquisitions; RPO +22% ex-acquisitions | Positive demand plus substantial M&A/share effects |
| Fortinet | 2024 appliance digestion and billings pressure | Revenue +26%; billings +33%; product +52% | Strong network/firewall refresh and SASE momentum |
| Zscaler | Growth decelerated from ~40% to low twenties | Revenue +25%; ARR +21% ex-Red Canary | Sustained SASE demand, not a new broad inflection |
| Check Point | Low-to-mid single-digit growth | Revenue +1%; subscriptions +12%; products/licenses down | Mix shift; no broad acceleration |
| Cloudflare | Revenue growth slowed toward high twenties | Revenue +36%; cRPO +35% | Edge/SASE/developer demand accelerating; not security-pure |
| Cisco Security | Splunk acquisition broke comparability | Q4 revenue +14%, FY2026 +2% | Quarterly improvement with weak full-year breadth; Splunk remains embedded |
| Okta | cRPO growth decelerated from ~25% | cRPO +12%; revenue +11% | Identity positive but not accelerating broadly |
| Rubrik / Varonis | Short or transition-distorted histories | Subscription ARR +32% / SaaS ARR ex-conversions +25% | Selected data-security acceleration |

### Buyer-budget baseline

| Year | Average security-budget growth | Security share of IT | Read |
|---:|---:|---:|---|
| 2023 | 6% | 11.6% | Security already decelerating as GenAI demand emerged |
| 2024 | 8% | 11.9%* | Modest recovery during the common infrastructure upcycle |
| 2025 | 4% | 10.9% | Security lost share as AI/cloud IT spending rebounded |
| 2026 | Realized total unavailable at freeze | unavailable | Incremental intent shifted to GenAI protection, cloud, and identity |

\* IANS reported 13.2 percent contemporaneously in 2024, then restated 2024 to 11.9 percent in the consistent historical series published with its 2025 report. This baseline uses the restated series.

## Turning-point register

| Turning point | Evidence | Maturity for lag test |
|---|---|---|
| Compute impulse — 2023-Q2 | NVIDIA Data Center step-change | Not broad enough by itself |
| Common infrastructure impulse — 2024 | hyperscaler capex breadth, Dell AI-server series, Cisco destock ending | First mature broad episode |
| Security response through 2025 | buyer-budget growth falls to 4%; security share of IT falls | No broad total-budget response |
| Heterogeneous security strengthening — 2025–2026 | Fortinet realized momentum; selected data-security vendors; CrowdStrike recovery; non-pure Cloudflare growth; ETR category intent | Descriptive observations with different drivers; no lag inference |
| Second infrastructure impulse — late 2025 through 2026 | Vertiv orders, Dell/Cisco backlog, Microsoft/Amazon/Alphabet capex step | Right-censored at freeze |

## Lag scorecard

| Test | Result | Sufficiency | Disposition |
|---|---|---|---|
| Did a broad infrastructure acceleration occur? | Yes, beginning in 2024 and accelerating again in late 2025–2026 | High breadth | Evidenced |
| Did broad cybersecurity budgets accelerate at lag 0–4 quarters? | No; 2025 budget growth and share of IT weakened | Independent buyer series available | H1 not supported at short lag |
| Did security intent and selected vendor metrics strengthen later in the calendar sequence? | Yes, in 2025–2026 | Mixed vendor definitions; realized-spend evidence incomplete | Descriptive sequence only; no lag or causal inference |
| Did a majority of acquisition-adjusted core security vendors respond together? | No | Check Point, Cisco, Okta remain weak/mixed; PANW M&A-heavy | Broad category response not established |
| Do supplier and hyperscaler layers point in the same direction? | Yes | Strong | Infrastructure call robust |
| Are at least two mature infrastructure episodes observable through a complete security response? | No | Second impulse right-censored | Constant-lag estimate prohibited |
| Does negative-lag or contemporaneous evidence remain plausible? | Yes | Security had pre-existing growth and regulatory drivers | Causality unresolved |

## Hypothesis disposition

### H1 — Infrastructure leads cybersecurity demand

**Disposition: `NO-CALL — later sequence observed, not validated`.**

The calendar sequence places the common 2024 infrastructure impulse before 2025–2026 category intent and selected vendor strengthening. It does not establish a broad, acquisition-adjusted security-market response, a causal link, or a defensible lag band.

### H2 — The lag is domain-specific

**Disposition: `NO-CALL`.**

Observed momentum differs:

- network/firewall and SASE show realized financial momentum;
- cloud/CNAPP and identity show buyer priority and strategic capital allocation;
- data security shows selected-vendor acceleration;
- SecOps and broad platform results are heavily acquisition- or transition-distorted.

Those differences do not establish domain-specific infrastructure lags.

### H3 — AI compresses the historical lag

**Disposition: `NO-CALL`.**

AI, cloud, and regulatory concerns moved category intent and governance requirements earlier, but no comparable historical lag or broad realized security response establishes compression.

## Domain sufficiency, momentum, and causality

| Domain | Financial contributors | Independent demand signals | Coverage result | Current operating momentum | Category vs share / refresh | Infrastructure causality | Timing posture |
|---|---|---|---|---|---|---|---|
| Network / firewall | Fortinet, Check Point, Cisco; PANW as broad platform | buyer budgets, channel commentary | **PASS** | Strong at Fortinet and Cisco orders; mixed at Check Point | Refresh and competitive rotation materially contribute | **NO-CALL** | **PREPARE** only where refresh or SASE displacement is already observable |
| SASE / edge | Zscaler, Fortinet, PANW; Cloudflare as non-pure corroboration | IANS cloud priority, ETR cloud intent | **PASS with purity limitation** | Sustained to improving | Partial category expansion plus share competition | **NO-CALL** | **PREPARE** for accounts with active cloud/network change |
| Cloud / CNAPP | no clean three-company domain-specific financial series | IANS, IDC/Gartner category evidence, incidents, Wiz transaction | **INSUFFICIENT COVERAGE** | Strategic need visible; realized pure-play financial momentum not callable | Platform absorption and M&A dominate | **NO-CALL** | **INVESTIGATE** market; readiness conversation only for exposed accounts |
| Identity / NHI | Okta plus acquisition-dependent PANW/CyberArk context | ETR NHI, regulation/insurance, incidents | **INSUFFICIENT COVERAGE** | Okta positive but decelerating; NHI early | Hygiene bundling and platform capital allocation | **NO-CALL** | **INVESTIGATE** market; readiness conversation only for exposed accounts |
| Data / AI security | Rubrik, Varonis | ETR AI/data intent, incidents, funding | **PASS with short-history limitation** | Selected vendors accelerating | Category expansion possible; metrics and histories differ | **NO-CALL** | **PREPARE** selectively for sensitive-data/AI activation |
| SecOps / analytics | CrowdStrike broad platform; Cisco/Splunk, PANW/Chronosphere, Zscaler/Red Canary acquisition-distorted | IANS automation priority, constrained hiring | **INSUFFICIENT COVERAGE** | Mixed | Platformization and share shift dominate | **NO-CALL** | **INVESTIGATE** |
| AI runtime security | no comparable public financial panel | ETR intent, product formation, Episode 001 | **INSUFFICIENT COVERAGE** | Realized specialist spend unproven | Emerging and potentially native-absorbed | **NO-CALL** | **INVESTIGATE** |

## Data-sufficiency controls

- No exact-quarter correlation is reported because the paired sample is insufficient at medium and long lags.
- No interpolation, carry-forward, or zero substitution was used.
- No pooled ARR, RPO, billings, or capex total was calculated.
- Acquisition-heavy vendor quarters were interpreted using disclosed organic bridges or quarantined.
- The 2026-Q2 security layer remains incomplete because several companies had not reported by the freeze.

The next evidence version opens when any of these events occurs:

- all core 2026-Q2 security companies have reported;
- the next IANS security-budget benchmark is published;
- two complete post-impulse quarters satisfy the pre-registered supplier and hyperscaler breadth condition; or
- a material guidance cut, cancellation, or buyer-budget shock challenges the cycle state.

## What would change the disposition

### Support H1 for one prospective cycle

- a registered infrastructure impulse is followed by a registered security response under the fixed cohorts, metrics, formulas, quorums, and definition-change rules; and
- buyer corroboration passes either the IANS rule (both budget growth and security share of IT rise) or the two-source rule (two method-consistent realized-spend sources each improve by at least 2 percentage points).

One such pair supports a single sequence only. Stable-lag validation requires a second prospective pair in the same broad band.

### Weaken H1

- scaled AI/cloud deployment rises while security budgets remain flat or lose further share;
- native cloud and infrastructure controls absorb the incremental requirement;
- apparent security acceleration disappears after acquisition and refresh adjustments; or
- a future registered infrastructure impulse receives no registered security response inside eight quarters.

