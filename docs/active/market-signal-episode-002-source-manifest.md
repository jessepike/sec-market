# Market Signal Episode 002 — Source and Claim Manifest

## Control

- **Manifest ID:** `SEC-MARKET-SIG-SRC-002`
- **Version:** `0.2`
- **Lifecycle state:** `sealed — independently reviewed`
- **Episode:** `SEC-MARKET-SIG-002`
- **Research freeze:** `2026-08-15T19:03:08-07:00`
- **Review correction:** `2026-08-15T19:17:24-07:00`
- **Retrieval status:** retrieved on or before the correction time; no post-freeze market event included

## Capture contract

Each load-bearing claim below records:

- publication date;
- economic period end;
- source class and canonical URL;
- exact short excerpt or table locator;
- interpretation;
- confound or limitation; and
- decision relevance.

Full external pages were not redistributed. Git history plus the final packet hashes preserve the local claim record. A later source or claim change requires a new packet version.

## Atomic claim index

### A1a — NVIDIA compute-cycle opening

- **Publication:** 2023-05-24
- **Period end:** 2023-04-30
- **Class:** IR
- **Source:** [NVIDIA Q1 FY24](https://investor.nvidia.com/news/press-release-details/2023/NVIDIA-Announces-Financial-Results-for-First-Quarter-Fiscal-2024/)
- **Exact excerpt:** “The computer industry is going through two simultaneous transitions — accelerated computing and generative AI… We are significantly increasing our supply to meet surging demand.”
- **Table locator:** quarterly Data Center revenue, $4.28 billion
- **Interpretation:** earliest compute-supply impulse
- **Confound:** Data Center includes non-GenAI workloads
- **Decision relevance:** establishes the before-state

### A1b — NVIDIA latest frozen compute print

- **Publication:** 2026-05-20
- **Period end:** 2026-04-26
- **Class:** FILING / IR
- **Sources:** [10-Q](https://www.sec.gov/Archives/edgar/data/1045810/000104581026000052/nvda-20260426.htm), [IR release](https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-Announces-Financial-Results-for-First-Quarter-Fiscal-2027/)
- **Exact excerpt:** “Data Center revenue was $75.2 billion, up 92% from a year ago and up 21% sequentially.”
- **Interpretation:** compute demand remains elevated in absolute dollars
- **Confound:** China restrictions and product transitions affect quarter-to-quarter comparability
- **Decision relevance:** infrastructure-cycle state

### A2 — Cisco AI and networking acceleration

- **Publication:** 2026-08-12
- **Period end:** 2026-07-25
- **Class:** IR
- **Source:** [Cisco Q4/FY26](https://investor.cisco.com/news/news-details/2026/CISCO-REPORTS-FOURTH-QUARTER-AND-FISCAL-YEAR-2026-EARNINGS/default.aspx)
- **Exact excerpt:** “$4 billion of orders taken in Q4, bringing the total for FY 2026 to $9.3 billion. Delivered approximately $4 billion of revenue in FY 2026; $7.5 billion expected in FY 2027.”
- **Table locator:** Networking revenue $9.791 billion, +28 percent; Q4 networking product orders +40 percent
- **Interpretation:** networking joined the cycle after the compute impulse
- **Confound:** orders are concentrated and are not revenue
- **Decision relevance:** infrastructure breadth

### A3 — Arista networking breadth

- **Publication:** 2023-05-01 / 2026-08-04
- **Period end:** 2023-03-31 / 2026-06-30
- **Class:** FILING / IR
- **Sources:** [Arista Q1 2023](https://www.sec.gov/Archives/edgar/data/1596532/000159653223000101/ex991q123-earningsrelease.htm), [Arista Q2 2026](https://investors.arista.com/Communications/Press-Releases-and-Events/Press-Release-Detail/2026/Arista-Networks-Inc--Reports-Second-Quarter-2026-Financial-Results/default.aspx)
- **Exact table locators:** revenue $1.351 billion and $3.036 billion, respectively; latest YoY growth 37.7 percent
- **Interpretation:** cloud and AI networking broadened the supplier cycle
- **Confound:** total revenue is not an AI-only series
- **Decision relevance:** fixed supplier-cohort breadth

### A4 — Dell order, shipment, and backlog gap

- **Publication:** 2026-05-28
- **Period end:** 2026-05-01
- **Class:** IR
- **Source:** [Dell Q1 FY27](https://investors.delltechnologies.com/news-releases/news-release-details/dell-technologies-delivers-first-quarter-fiscal-2027-financial)
- **Exact excerpt:** “We booked $24.4 billion in AI orders and recognized $16.1 billion of AI server revenue. We’re increasing our AI server revenue expectations for FY27 to $60 billion.”
- **Table locator:** AI-server backlog $51.3 billion
- **Interpretation:** demand is still converting into capacity
- **Confound:** memory cost and supply affect dollars and timing
- **Decision relevance:** deployment lag between capex and live workload

### A5 — Vertiv power and thermal inflection

- **Publication:** 2026-02-11 / 2026-07-29
- **Period end:** 2025-12-31 / 2026-06-30
- **Class:** IR / FILING
- **Sources:** [Q4 2025](https://investors.vertiv.com/news/news-details/2026/Vertiv-Reports-Strong-Fourth-Quarter-with-Organic-Orders-Growth-of-252-and-Diluted-EPS-Growth-of-200-Adjusted-Diluted-EPS-37/), [Q2 2026](https://www.sec.gov/Archives/edgar/data/1674101/000162828026050323/q22026exhibit991vrt07292026.htm)
- **Exact excerpts:** “organic orders up approximately 252%”; “book-to-bill ratio was ~2.9x and backlog increased to $15.0 billion.”
- **Table locator:** Q2 2026 sales growth 24 percent: 18 percent organic, 5 percent acquisitions, 1 percent FX
- **Interpretation:** physical support infrastructure inflected after compute
- **Confound:** quarterly order disclosure later changed
- **Decision relevance:** staggered infrastructure sequence

### A6 — Broadcom custom-silicon corroboration

- **Publication:** 2026-03-04 / 2026-06-03
- **Period end:** 2026-02-01 / 2026-05-03
- **Class:** IR
- **Sources:** [Q1 FY26](https://investors.broadcom.com/news-releases/news-release-details/broadcom-inc-announces-first-quarter-fiscal-year-2026-financial), [Q2 FY26](https://www.broadcom.com/company/news/financial-releases/64371)
- **Exact excerpts:** “Q1 AI revenue of $8.4 billion grew 106% year-over-year”; “Q2 semiconductor revenue from AI of $10.8 billion grew 143% year-over-year.”
- **Interpretation:** custom AI silicon accelerated alongside merchant compute
- **Confound:** short company-defined series
- **Decision relevance:** supplier breadth

### B1 — Microsoft capacity investment

- **Publication:** 2026-07-29
- **Period end:** 2026-06-30
- **Class:** IR / TRANSCRIPT
- **Sources:** [release](https://www.microsoft.com/en-us/Investor/earnings/FY-2026-Q4/press-release-webcast), [official call](https://www.microsoft.com/en-us/investor/events/fy-2026/earnings-fy-2026-q4)
- **Exact excerpts:** cash-flow table “Additions to property and equipment (35,802)… (115,948)”; “Customer demand continues to exceed available capacity.”
- **Interpretation:** capex breadth and continuing constraint
- **Confound:** finance-to-operating-lease reclassification changes reported capex
- **Decision relevance:** hyperscaler demand context

### B2 — Amazon cash capex and deployment lead time

- **Publication:** 2026-07-30
- **Period end:** 2026-06-30
- **Class:** IR / TRANSCRIPT
- **Sources:** [release](https://ir.aboutamazon.com/news-release/news-release-details/2026/Amazon-com-Announces-Second-Quarter-Results/), [call transcript](https://stockanalysis.com/stocks/amzn/transcripts/657334-q2-2026/)
- **Exact excerpt from release:** “Free cash flow decreased to an outflow of $7.6 billion… driven primarily by a year-over-year increase of $66.1 billion in purchases of property and equipment… primarily reflects investments in artificial intelligence.”
- **Table locator:** Q2 purchases of property and equipment $54.208 billion
- **Interpretation:** investment remains elevated
- **Confound:** company capex includes non-AWS uses; the secondary transcript is context, not the numeric source
- **Decision relevance:** demand context, not security spend

### B3 — Alphabet capacity acceleration

- **Publication:** 2026-07-22
- **Period end:** 2026-06-30
- **Class:** FILING / TRANSCRIPT
- **Sources:** [SEC exhibit](https://www.sec.gov/Archives/edgar/data/1652044/000165204426000066/googexhibit991q22026.htm), [call transcript](https://www.roic.ai/quote/GOOG/transcripts/2026-year/2-quarter)
- **Exact table locator:** purchases of property and equipment $44.924 billion for Q2 2026 and $80.598 billion for H1 2026
- **Exact excerpt:** “The increase in the range is primarily due to an acceleration in the delivery of capacity to meet growing demand.”
- **Interpretation:** broad capacity acceleration
- **Confound:** transcript source is secondary; cash-flow table is load-bearing
- **Decision relevance:** hyperscaler breadth

### B5 — Oracle contracted-capacity step

- **Publication:** 2026-06-10
- **Period end:** 2026-05-31
- **Class:** IR
- **Source:** [Oracle FY2026](https://investor.oracle.com/investor-news/news-details/2026/Oracle-Announces-Record-Q4-and-FY-2026-Results-Driven-by-Cloud-Infrastructure--Cloud-Applications/)
- **Exact excerpts:** “RPO… $638 billion, up 363%”; “prepaid and customer supplied hardware portions of our large AI contracts now total $75 billion.”
- **Table locator:** FY2026 capital expenditures $55.663 billion
- **Interpretation:** large contracted-capacity demand
- **Confound:** concentration and customer-supplied hardware
- **Decision relevance:** strongest alternative to diversified-enterprise demand

### C1 — CrowdStrike re-acceleration

- **Publication:** 2026-06-03
- **Period end:** 2026-04-30
- **Class:** FILING
- **Source:** [CrowdStrike Q1 FY27](https://www.sec.gov/Archives/edgar/data/1535527/000153552726000022/crwd-20260603xex991.htm)
- **Table locator:** revenue $1.39 billion; ending ARR $5.51 billion, +24 percent; net-new ARR $255.8 million
- **Interpretation:** selected platform-vendor acceleration
- **Confound:** recovery from a vendor-specific outage and platform share capture
- **Decision relevance:** not sufficient for category breadth

### C2 — Palo Alto acquisition bridge

- **Publication:** 2026-06-02
- **Period end:** 2026-04-30
- **Class:** FILING / IR
- **Sources:** [release](https://www.paloaltonetworks.com/company/press/2026/palo-alto-networks-reports-fiscal-third-quarter-2026-financial-results), [investor deck](https://investors.paloaltonetworks.com/static-files/67ce9226-4fe0-43cd-b83e-42efb035f38c)
- **Exact excerpt:** “Total revenue… grew 31%… This includes $388 million from CyberArk and Chronosphere.”
- **Table locator:** approximately 14 percent revenue, 28 percent NGS ARR, and 22 percent RPO growth excluding those acquisitions; headline NGS ARR approximately 60 percent
- **Interpretation:** positive organic demand with acquisition-heavy headline growth
- **Confound:** platformization and M&A
- **Decision relevance:** category-versus-share discipline

### C3 — Fortinet realized network-security acceleration

- **Publication:** 2026-07-29
- **Period end:** 2026-06-30
- **Class:** IR
- **Source:** [Fortinet Q2 2026](https://investor.fortinet.com/news-releases/news-release-details/fortinet-reports-strong-second-quarter-2026-financial-results)
- **Exact excerpt:** “Revenue grew 26%… Product revenue grew 52%… Billings grew 33%.”
- **Interpretation:** current network/firewall demand is real
- **Confound:** refresh, pricing, and share shift
- **Decision relevance:** current momentum, not AI-causality proof

### C4 — Zscaler organic split

- **Publication:** 2026-05-26
- **Period end:** 2026-04-30
- **Class:** FILING
- **Source:** [Zscaler Q3 FY26](https://www.sec.gov/Archives/edgar/data/1713683/000171368326000095/zs-04302026_991.htm)
- **Exact excerpt:** “ARR grew 25%, or 21%, excluding the contribution from the Red Canary acquisition.”
- **Interpretation:** sustained SASE demand
- **Confound:** acquisition and subscription timing
- **Decision relevance:** domain momentum without a new inflection claim

### C5 — Cloudflare non-pure platform corroboration

- **Publication:** 2026-08-06
- **Period end:** 2026-06-30
- **Class:** IR
- **Source:** [Cloudflare Q2 2026](https://www.cloudflare.com/en-gb/press/press-releases/2026/cloudflare-announces-second-quarter-2026-financial-results/)
- **Exact excerpt:** “Second quarter revenue totaled $696.1 million, representing an increase of 36% year-over-year… Delivered Current RPO year-over-year growth of 35%.”
- **Interpretation:** edge, connectivity, and SASE-related platform momentum improved
- **Confound:** consolidated revenue includes developer and compute activity and is not security-pure
- **Decision relevance:** corroboration only; cannot carry a security-category or lag claim

### C6 — Cisco security mix

- **Publication:** 2026-08-12
- **Period end:** 2026-07-25
- **Class:** IR
- **Source:** [Cisco Q4/FY26](https://investor.cisco.com/news/news-details/2026/CISCO-REPORTS-FOURTH-QUARTER-AND-FISCAL-YEAR-2026-EARNINGS/default.aspx)
- **Exact table locator:** Security revenue $2.226 billion, +14 percent for Q4; $8.232 billion, +2 percent for FY2026
- **Interpretation:** quarterly momentum improved, but full-year breadth remained weak
- **Confound:** Splunk is embedded in the segment, so the series is not an organic Cisco-security measure
- **Decision relevance:** blocks a uniform-category acceleration call

### C7 — Okta identity deceleration

- **Publication:** 2026-05-28
- **Period end:** 2026-04-30
- **Class:** FILING
- **Source:** [Okta Q1 FY27](https://www.sec.gov/Archives/edgar/data/1660134/000166013426000050/okta-4302026_ex991.htm)
- **Table locator:** revenue $765 million, +11 percent; cRPO $2.499 billion, +12 percent; DBNRR 107 percent
- **Interpretation:** identity demand positive but not broadly accelerating
- **Confound:** contract duration and sales-cycle effects
- **Decision relevance:** identity market call remains coverage-limited

### C8a — Rubrik data-security signal

- **Publication:** 2026-06-04
- **Period end:** 2026-04-30
- **Class:** IR
- **Source:** [Rubrik Q1 FY27](https://ir.rubrik.com/news-events/press-releases/news-details/2026/Rubrik-Reports-First-Quarter-Fiscal-Year-2027-Financial-Results/default.aspx)
- **Exact excerpt:** “Subscription ARR was up 32% year-over-year, growing to $1.57 billion.”
- **Interpretation:** selected data-security acceleration
- **Confound:** short public history and material-rights accounting
- **Decision relevance:** one of two financial contributors

### C8b — Varonis organic SaaS signal

- **Publication:** 2026-07-28
- **Period end:** 2026-06-30
- **Class:** FILING
- **Source:** [Varonis Q2 2026](https://www.sec.gov/Archives/edgar/data/1361113/000117184326004948/exh_991.htm)
- **Exact excerpt:** “SaaS ARR excluding conversions growth of 25%.”
- **Interpretation:** selected data/AI-security demand
- **Confound:** headline 52 percent SaaS ARR includes conversions
- **Decision relevance:** second financial contributor for the limited data-security call

### D1 — Buyer-budget response

- **Publication:** 2023-09-26 / 2024-09-05 / 2025-08-05
- **Economic periods:** 2023 / 2024 / 2025
- **Class:** INDEPENDENT
- **Sources:** [IANS 2023](https://www.prnewswire.com/news-releases/new-research-from-ians-and-artico-search-reveals-cybersecurity-budgets-increased-just-6-for-2022-2023-cycle-301938338.html), [IANS 2024](https://www.iansresearch.com/resources/press-releases/detail/new-research-reveals-security-budgets-only-increased-2-points-in-2024--while-12--of-cisos-faced-reductions), [IANS 2025](https://sf-cdn.iansresearch.com/sitefinity/docs/default-source/reports/2025-security-budget-benchmark-summary-report_08_05_2025.pdf?sfvrsn=43097214_2)
- **Exact excerpts:** “average security budget increase of 6%”; “risen from 6% in 2023 to 8%”; “average annual security budget growth plunged to 4%.”
- **Table locator:** 2025 report historical share-of-IT series: 11.6 percent in 2023, 11.9 percent in 2024, 10.9 percent in 2025
- **Interpretation:** no simultaneous broad security-budget acceleration
- **Confound:** 2024 contemporaneous report said 13.2 percent; 2025 restated the methodology
- **Decision relevance:** strongest buyer-spend counterweight

### D2 — AI-protection intent

- **Publication:** 2026-04-01 / 2026-04-29
- **Economic period:** 2026 planned spending
- **Class:** INDEPENDENT
- **Sources:** [enterprise priorities](https://research.etr.ai/etr-data-drop/what-are-enterprise-security-priorities-in-2026), [budget analysis](https://research.etr.ai/etr-data-drop/why-genai-protection-just-overtook-cloud-security-budgets)
- **Exact excerpts:** “Fifty-nine percent… plan to increase spending… up from 50% in 2025”; “already spending on AI security tools reached 32% in 2026, up from 23% in 2025.”
- **Interpretation:** category intent strengthened later in the sequence
- **Confound:** intent and self-reported tool use are not realized market spend
- **Decision relevance:** delayed domain-intent evidence

### D3 — Deployment remains behind use

- **Publication:** 2025-11
- **Economic period:** 2025
- **Class:** INDEPENDENT
- **Source:** [McKinsey State of AI 2025](https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai)
- **Exact excerpt:** “88 percent report regular AI use in at least one business function… the majority are still in the experimenting or piloting stages.”
- **Interpretation:** workload activation can trail capex and broad AI use
- **Confound:** self-reported definitions
- **Decision relevance:** transmission mechanism remains incomplete

### B4 — Meta first-party build corroboration

- **Publication:** 2026-07-29
- **Period end:** 2026-06-30
- **Class:** IR
- **Source:** [Meta Q2 2026](https://investor.atmeta.com/investor-news/press-release-details/2026/Meta-Reports-Second-Quarter-2026-Results/default.aspx)
- **Exact excerpt:** “Capital expenditures, including principal payments on finance leases, were $31.08 billion.”
- **Interpretation:** first-party AI infrastructure remains elevated
- **Confound:** internal ads and AI infrastructure is a weak enterprise-cloud demand proxy
- **Decision relevance:** infrastructure breadth only; excluded from the comparable quarterly cash panel

### D4 — Security hiring did not lead

- **Publication:** 2024-09-11
- **Economic period:** 2024
- **Class:** INDEPENDENT
- **Source:** [ISC2 Workforce Study 2024](https://www.prnewswire.com/news-releases/growth-of-cybersecurity-workforce-slows-in-2024-as-economic-uncertainty-persists-302244585.html)
- **Exact excerpt:** the workforce was “holding at an estimated 5.5 million people (a 0.1% year-on-year increase).”
- **Interpretation:** security headcount did not accelerate with 2024 infrastructure investment
- **Confound:** workforce estimates do not measure software or services bookings
- **Decision relevance:** supports tooling/skills rather than hiring as the likely response form

### D6 — Domain-specific regulatory and insurance floors

- **Publication:** 2023-07-26 / 2025-01-17 application
- **Class:** OFFICIAL / INDEPENDENT
- **Sources:** [SEC cyber-disclosure rule](https://www.sec.gov/files/rules/final/2023/33-11216.pdf), [DORA](https://www.eiopa.europa.eu/digital-operational-resilience-act-dora_en), [Marsh market update](https://www.marsh.com/en/services/cyber-risk/insights/cyber-insurance-market-update.html)
- **Exact excerpts:** SEC requires disclosure of material cyber incidents and risk-management governance; DORA “entered into application on 17 Jan 2025”; Marsh reported US cyber-insurance rates declined while twelve hygiene controls were treated as essential.
- **Interpretation:** governance, identity, resilience, and third-party requirements can move independently of infrastructure
- **Confound:** requirements and insurance controls do not establish product spending
- **Decision relevance:** strongest common/independent-driver alternative

### D7 — Cloud and AI incidents

- **Publication:** 2024-06 / 2025-01-29
- **Class:** VENDOR-RESEARCH
- **Sources:** [Mandiant on Snowflake](https://cloud.google.com/blog/topics/threat-intelligence/unc5537-snowflake-data-theft-extortion), [Wiz on DeepSeek](https://www.wiz.io/blog/wiz-research-uncovers-exposed-deepseek-database-leak)
- **Exact excerpts:** Mandiant tied tenant compromise to stolen customer credentials and absent MFA; Wiz found a “publicly accessible ClickHouse database” containing chat history, secret keys, and backend details.
- **Interpretation:** identity, posture, and data-security need can be incident-driven
- **Confound:** vendor-authored research and selected incidents are not a representative loss series
- **Decision relevance:** discriminates independent incident demand from infrastructure causality

### D5a — Cloud-security capital allocation

- **Publication:** 2025-03-18
- **Class:** FILING
- **Source:** [Alphabet/Wiz 8-K](https://www.sec.gov/Archives/edgar/data/1652044/000165204425000027/goog-20250318.htm)
- **Exact locator:** approximately $32 billion all-cash transaction
- **Interpretation:** strategic capital moved into cloud security
- **Confound:** platform share strategy is an alternative to category expansion
- **Decision relevance:** strategic signal, not buyer spend

### D5b — Identity-security capital allocation

- **Publication:** 2025-07-30
- **Class:** FILING
- **Source:** [Palo Alto/CyberArk 8-K](https://www.sec.gov/Archives/edgar/data/1327567/000119312525168821/d67702d8k.htm)
- **Exact locator:** approximately $25 billion equity value
- **Interpretation:** identity became a platform priority
- **Confound:** acquisition does not establish organic category demand
- **Decision relevance:** supports readiness, not a market-growth claim

## Assurance limit

This manifest preserves the decision-bearing claims. The exact sparse-panel cells have their own column and period source map in `SEC-MARKET-SIG-PANEL-002`; they remain descriptive unless a claim above promotes them into the decision basis.

## Packet integrity

SHA-256 before final gate disposition:

```text
6fb310d094dc4b61a34fa2e1db49e175a4cfe3b151e504cbd9cca1eb11a76a59  docs/active/market-signal-episode-002.md
5151fc7efead9d19a75d993348bfe78e2818fe854692b1152bad44d0f1a56fdd  docs/active/market-signal-episode-002-evidence.md
e2736c464647e612d73f7ef59f79ae95a4aa9280225e75dfb39d2b9850695e45  docs/active/market-signal-episode-002-baseline.md
e2134c606764ccbde3ef13076f0d23ff48b1b5bb4132ea796b93890cec903760  docs/active/market-signal-episode-002-panel.md
9c974a021c77c67ab20f7621d3244bed8e80c516af33b3d26f01b49f9872e252  docs/active/market-signal-episode-002-brief.md
b2c5abf4c08786b22a5a5d1a8a8a7c986a70cbe91df74488f0531ea91505f3c5  docs/active/intent-reconciliation-2026-08-15.md
```

Any change to a hashed file requires recomputing this block and recording whether the research freeze itself changed.

