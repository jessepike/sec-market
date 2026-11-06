# Coverage expansion: 8 new suppliers and an onboarding gate (2026-11-06)

Owner request (Jess, 2026-11-06): add Cyera, Secuvy, Straiker, F5, Akamai, Lumos, Aikido, 7AI,
Rubrik, Cohesity and Skyflow. "What I don't want is half done companies there." New companies go
through the full pipeline. Status: **owner chose the onboarding gate (D-138). Seed records and the preview-only section are built. The contract transition (SEC-083, D-141) is built and on preview: 82 suppliers in the contract, collected but held off the public pages until graduation.**

## Already covered

Cyera (`cyera`, data), Rubrik (`rubrik`, data, certified) and Cohesity (`cohesity`, data) are in the
74 today. That leaves 8 new suppliers.

## The 8 new suppliers

| Company | Kind | Domain (proposed) | Data route | Coverage tier it lands in | Latest public fact found |
|---|---|---|---|---|---|
| F5 (FFIV) | public, 10-Q/10-K XBRL filer | network-sase (app delivery and WAF; no exact domain) | SEC XBRL, same as the 16 certified filers | 1, revenue checked against SEC filings | Q4 FY26 results, 13% total revenue growth ([8-K ex. 99.1](https://www.sec.gov/Archives/edgar/data/0001048695/000104869526000074/ex991-q426earningsreleasef.htm)) |
| Akamai (AKAM) | public, 10-Q/10-K XBRL filer | network-sase (security is a reported solution line) | SEC XBRL for company revenue; security revenue from the earnings release | 1 | Q3 2026 results ([8-K ex. 99.1](https://www.sec.gov/Archives/edgar/data/0001086222/000108622226000097/exhibit991-q32026.htm)) |
| Aikido Security | private, venture | appsec | Company newsroom plus citations | 3, funding | $60M Series B at $1B, Jan 14 2026 ([SecurityWeek](https://www.securityweek.com/aikido-security-raises-60-million-at-1-billion-valuation/amp/)) |
| 7AI | private, venture | secops | Company blog/newsroom plus citations | 3 | $130M Series A, Dec 2025 ([SecurityWeek](https://www.securityweek.com/agentic-security-firm-7ai-raises-130-million/)) |
| Straiker | private, venture | ai-security | Company newsroom plus citations | 3 | $64M Series A, June 2026 ([SecurityWeek](https://securityweek.com/straiker-raises-64-million-for-ai-security-platform)) |
| Lumos | private, venture | identity | Company blog press posts plus citations | 3 | $35M Series B, May 2024 ([Business Wire](https://www.businesswire.com/news/home/20240523314788/en)) |
| Skyflow | private, venture | data | Company press page plus citations | 3 | $30M led by Khosla, Mar 28 2024 ([Business Wire](https://www.businesswire.com/news/home/20240328765469/en)) |
| Secuvy | private, venture | data | Company news plus citations | 4 likely: last round found is March 2023 with no amount disclosed ([Business Wire](https://www.businesswire.com/news/home/20230310005374/en/Secuvy-Announces-New-Investments-from-Dell-Technologies-Capital-and-WestWave-Capital-to-Modernize-Data-Privacy-and-Security)) | thin public record |

No new provider is needed. F5 and Akamai use the SEC route already in place; the six private
companies use the official-site discovery and citation sources every private supplier uses today.

Domain caveat: the site has no "application and API security / edge" domain. F5 and Akamai fit
network-sase best today (Cloudflare sits there). A new domain would be a major change of its own.

## Why this is not a quick data edit

Measured on 2026-11-06: adding one supplier and one source to `contracts/market.json` makes 40 of
1,064 `ops/ci` tests fail (`CYERA_EXACT_REVIEWED_PLAN_REQUIRED`, `PRN_EXACT_REVIEWED_PLAN_REQUIRED`,
`Q4_TRANSITION_NOT_AUTHORIZED` and others). The contract is a chain of exact-hash authorities
(`q4_qualification_origin.is_successor`). On a changed contract the daily collector would take the
older seeding path and stop. `originals.json` is also hash-pinned by `contracts/factual-baseline.json`.
So a roster change on its own would break the daily run. It must ship as a formal contract transition.

The same blocker holds SEC-076 (Optiv source link) and SEC-080 (Check Point SEC sources). They
should ride on the same transition.

Check Point inputs for the transition (from the SEC-080 thread): add `checkpoint-sase:sec_facts`,
`:sec_submissions` and `:sec_documents` (CIK 0001015922), copied from the `cloudflare:sec_*` entries,
and append them to the supplier's `sourceIds`. The transition restamps both the Q4 authority and the
correction policy stamp. The 6-K results parser and site wiring stay with the SEC-080 work and must
not join the certified cohort.

## Proposed onboarding gate

1. **One reusable "additive roster transition" (J to K).** A transition type that only adds
   suppliers and their sources, proved by inversion: removing the added rows must give back the
   exact current contract. Built once, so every later addition is a data change, not new hash code.
2. **Onboarding status in the contract.** New suppliers carry `status: "onboarding"`. The collector
   collects them with the same budget, validator and review step as the other 74.
3. **Shown on preview only.** The site build renders onboarding suppliers only when
   `VERCEL_ENV=preview`. The publisher's production artifact excludes them, so nothing half-done
   reaches securitymarketpulse.com.
4. **Automatic graduation.** A supplier flips to live after 3 consecutive clean daily runs: every
   required source bound, its seed facts pass the site invariants, and (for F5 and Akamai) the SEC
   claims replay at 100%. The flip is one commit through the normal preview to main route.
5. **Seed records.** Each supplier starts with a sourced seed record (identity, ownership, latest
   round or quarter) researched the same way the original 74 were, with retrieval hashes.

Runtime precondition (cost review, 2026-11-06): daily collection already hits its 35-minute timeout
with 74 suppliers and the November 5 run failed. Eight more add roughly 3 to 4 minutes. No new
supplier is collected in the production run until the timeout fix lands and collection fits with
headroom.

Adding suppliers is a major change under AGENTS.md: it carries `Owner-Review: required` and a
decision entry.

## Other companies worth adding (not added; needs approval)

Chosen for scale and fresh public activity, and to fill thin domains:

| Company | Domain | Why | Evidence |
|---|---|---|---|
| Saviynt | identity | $700M at about $3B, KKR-led, Dec 2025 | [SecurityWeek](https://www.securityweek.com/identity-security-firm-saviynt-raises-700-million-at-3-billion-valuation/) |
| Island | network-sase (enterprise browser) | $250M Series E at about $4.8B, Mar 2025; a later $400M at $6.4B is reported but unconfirmed | [Island press](https://island.io/press/island-secures-250-million-as-valuation-continues-to-soar-to-nearly-5-billion) |
| Cyberhaven | data | $100M Series D at $1B, Apr 2025 | [SecurityWeek](https://www.securityweek.com/cyberhaven-banks-100-million-in-series-d-valuation-hits-1-billion/amp/) |
| Noma Security | ai-security | $100M Series B, Jul 2025 | [SecurityWeek](https://www.securityweek.com/noma-security-raises-100-million-for-ai-security-platform/amp/) |
| Huntress | managed-security | $150M led by Kleiner Perkins, over $1.5B valuation | [fintech.global](https://fintech.global/?p=164350) |

Unverified: the Island $400M round and Noma's reported $132M total come from aggregator pages only.
The test that settles each one is the company's own press release.
