# M&A source catalog

## Control

| Field | Value |
|---|---|
| **ID** | `SEC-MARKET-MA-SRC-001` |
| **Date** | 2026-08-16 |
| **Status** | research — lead reviewed 2026-08-16 |
| **Scope** | M&A only (cybersecurity mergers and acquisitions). Startup funding out of scope except overlap with Return on Security weekly posts. |
| **Authority** | `SEC-MARKET-SIG-JOB-001` (D-33) |

---

## Verdict

The most useful **new-deal discovery** for cybersecurity M&A lives in three layers:

1. **Curated cyber deal intelligence** — Return on Security’s weekly **Security, Funded** posts include a dedicated **Mergers & Acquisitions** section (acquirer, target, security category, disclosed value, prior funding, source links). SecurityWeek publishes monthly **Cybersecurity M&A Roundup** articles plus breaking deal pieces on its M&A category page; these catch mid-market and MSSP deals that mega-tech recaps miss. The startup source catalog ranked Return on Security #1 for funding but **did not collect the M&A section** — that section is now in scope and verified (e.g., Security, Funded #256 lists BioCatch→Visa $2.4B, Clarity→Deel, Enkrypt→Anaconda, and nine other deals for the week of Aug 3, 2026).

2. **Trade press and search surfaces** — TechCrunch’s site search for “cybersecurity acquisition” surfaces major and mid-market cyber deals with dates and values when reported. SiliconANGLE and The Record cover large strategic deals with product context. SecurityWeek’s annual M&A report (426 deals in 2025) is recap/analysis, not a live feed, but anchors category taxonomy.

3. **Issuer filings and VC exit pages** — SEC **8-K** filings (Item 1.01 definitive agreement, Item 2.01 completion) via EDGAR full-text search catch public acquirers and targets with legal precision but miss private-only deals. Cyber VC portfolio pages (Cyberstarts, Forgepoint, SYN Ventures) flag **Acquired/Exited** portfolio companies with product blurbs but usually **without deal date or value** — useful as lagging confirmation, not primary discovery.

**This week (manual, no paid API, no ToS fight):** Return on Security weekly posts (M&A section), SecurityWeek M&A category + monthly roundups + individual deal articles, TechCrunch cybersecurity acquisition search, SEC EDGAR 8-K full-text search (with declared User-Agent), Cyberstarts / Forgepoint / SYN portfolio pages for exit confirmation, SiliconANGLE cyber M&A articles as they appear.

**Later:** The Signal dashboard and API (Return on Security; paid — Pro/Team + $79/mo add-on or Enterprise), Momentum Cyber and Windsor Drake full deal-list downloads (gated), Mergr bulk database (signup/paid), automated SecurityWeek/RoS RSS (Cloudflare blocks non-browser clients).

---

## Ranked sources (~25)

| Rank | Source | URL (verified 2026-08-16) | What we get | New-deal discovery? | Collection method | Freshness | Notes / blockers |
|---:|---|---|---|---|---|---|---|
| 1 | Return on Security — Security, Funded (M&A section) | https://www.returnonsecurity.com/ (e.g. https://www.returnonsecurity.com/p/security-funded-256) | Weekly **Mergers & Acquisitions** block: acquirer, target, one-line product/category, disclosed value, prior funding, `(more)` source links; market summary counts acquisitions by category | **High** | Newsletter + official public HTML posts | Weekly | Same publication as startup funding catalog #1. M&A was out of scope there; verified present in #256 (Aug 10, 2026). `/rss/` returns **403** to curl — treat RSS as unreliable for bots. References **The Signal** for live data. |
| 2 | SecurityWeek — M&A category | https://www.securityweek.com/category/cybersecurity-funding-news/ma/ | Monthly roundups + breaking deal articles; acquirer, target, value when known, product category in prose | **High** | Official public HTML / manual | Daily–monthly | Best dedicated cyber M&A feed among trade press. Individual articles cite internal tracker count (e.g., 230 deals YTD 2026 in Cyera/Oasis piece). `/category/ma-tracker/` and curl without browser sometimes hit **Cloudflare 403**; browser/WebFetch succeeded for category URL. |
| 3 | SecurityWeek — M&A Roundups | https://www.securityweek.com/cybersecurity-ma-roundup-21-deals-announced-in-july-2026/ | Named deals with acquirer, target, value (when disclosed), product description; “Other deals” list for long tail | **High** | Official public HTML | Monthly (~1st week) | Template repeats monthly (Jun/Jul 2026 verified). Catches Barracuda/Evo, Cribl/CardinalOps, Cyera/Oasis $1B, Okta/Permiso ~$200M, etc. |
| 4 | SecurityWeek — individual deal articles | https://www.securityweek.com/cyera-acquiring-oasis-security-in-1-billion-deal/ | Single-deal depth: value, strategic rationale, category, related deals | **High** | Official public HTML / RSS filter | As announced | RSS feed (https://www.securityweek.com/feed/) verified; M&A items appear (e.g., July roundup in feed). Filter general feed for “M&A”, “acquire”, “acquiring”. |
| 5 | TechCrunch — cybersecurity acquisition search | https://techcrunch.com/?s=cybersecurity+acquisition | Deal announcements with dates; values when verified by TC (Cyera/Oasis $1B, PAN/CyberArk $25B, Google/Wiz $32B, ServiceNow/Armis $7.75B) | **Med–High** | Official public HTML / manual search | Event-driven | `/category/security/` is mostly incidents/breach news, not M&A. Search is the usable surface (~532 results). Skews to larger deals. |
| 6 | SEC EDGAR — 8-K full-text search | https://efts.sec.gov/LATEST/search-index (forms=8-K; query e.g. `acquisition`) + https://www.sec.gov/cgi-bin/browse-edgar | Public-company definitive agreements and completions: acquirer CIK, target, date, material terms in filing body | **Med–High** (public issuers only) | Official API / filings HTML | Same-day to T+1 | **Requires declared User-Agent** (company name + email). Max **10 req/s**. Prohibits undeclared botnets. `data.sec.gov/submissions` JSON for per-company recent filings. Misses private-company-only deals. |
| 7 | The Signal (Return on Security dashboard) | https://signal.returnonsecurity.com/ | Landing describes funding, M&A, investors, categories; same dataset as newsletter | **Med–High** (if dashboard usable) | Manual browse | Per site copy: real-time | Free tier is **dashboard only, no API**. API docs at https://docs.returnonsecurity.com/ — paid add-on ($79/mo) or Enterprise. Do not assume free bulk access. |
| 8 | Cyberstarts portfolio (Exited) | https://www.cyberstarts.com/portfolio/ | Target name, product category blurb, **Acquired by** buyer (e.g., Wiz→Google, Oasis→Cyera, Dazz, Noname, Axis→CrowdStrike) | **Med** (lagging) | Official public HTML | Updated on exit | Strong for Israeli cyber exit map; **no deal dates or values** on index. Confirms VC-network exits after press. |
| 9 | Forgepoint Capital companies | https://forgepointcap.com/companies | 76+ companies; sector (Identity, AppSec, etc.), **Acquired** status, acquirer in name field (e.g., Attivo→SentinelOne, BehavioSec→LexisNexis) | **Med** (lagging) | Official public HTML | Filterable | robots.txt: `Crawl-delay: 3`, `Disallow: /*?`. Honor delay. No acquisition dates on listing. |
| 10 | SYN Ventures portfolio | https://www.synventures.com/portfolio | Product description, round/year for active; **Acquired** flag for exits (Adlumin, Boldend, Netography, Pangea, Phosphorus, Qwiet AI, Revelstoke, SecZetta) | **Med** (lagging) | Official public HTML | Updated as exits publish | Complements Forgepoint/Cyberstarts; **no deal value or date** on acquired entries. |
| 11 | Momentum Cyber — quarterly / H1 reviews | https://momentumcyber.com/cybersecurity-quarterly-review-q1-2026/ , https://momentumcyber.com/cybersecurity-mid-year-market-review-h1-2026/ | Public landing pages name recent deals with values (Check Point trio $150M combined, PAN/Koi $400M, Varonis/AllTrue.ai $126M); sector stats | **Med** | Official public HTML; **full deal lists gated** behind email download | Quarterly | CYBERcloud database is **proprietary / not public bulk**. SiliconANGLE covers their Almanac (Jan 2026). Good for validation and mega-deal context, weak for weekly long tail without download. |
| 12 | SiliconANGLE — cyber M&A articles | https://siliconangle.com/2026/01/07/record-cybersecurity-deal-activity-2025-sets-aggressive-tone-2026-says-momentum-cyber/ | Breaking coverage of large deals; Momentum Cyber stats; product/strategy context | **Med** | Official public HTML / search `?s=cybersecurity+acquisition` | Event-driven | Search returns ~1088 results but page is ad-heavy; article URLs verified for Wiz, PAN/CyberArk, Momentum 2026 Almanac. Cookie/consent banner on fetch. |
| 13 | The Record | https://therecord.media/ (e.g. https://therecord.media/servicenow-cyber-armis-acquisition) | Breaking cyber deal news: acquirer, target, value, product category, close timing | **Med** | Official public HTML / manual | Event-driven | `/tag/cybersecurity/` **404**. Site search `?s=acquisition` **timed out** once; individual articles verified. Not a systematic tracker — covers major stories (Armis $7.75B verified). |
| 14 | SecurityWeek — annual M&A report | https://www.securityweek.com/securityweek-report-426-cybersecurity-ma-deals-announced-in-2025/ | 426 deals in 2025; sector breakdown (GRC 82, data protection 63, identity 43, AI security 13); disclosed value $84B pure-play; methodology | **Med** (recap) | Official public HTML | Annual + referenced in roundups | Essential taxonomy and volume context; **not** for week-by-week new deals. Methodology: PR wires, Google, SecurityWeek tips; English-language bias. |
| 15 | Mergr — individual deal pages | https://mergr.com/transaction/sailpoint-acquires-entro-security (pattern) | Deal date, target description/category, buyer, deal type; buyer’s prior cyber deals | **Med–Low** | Manual per-deal HTML | Updated on indexing | Bulk search at `/transaction/cybersecurity` is **general M&A**, not cyber-filtered. Full database **224k+ transactions — signup/paid** for export. Individual cyber deal pages verified (SailPoint/Entro Jun 2026, Cisco/Astrix May 2026, Proofpoint/Acuvity Feb 2026). |
| 16 | Venture in Security | https://ventureinsecurity.net/ (RSS: https://ventureinsecurity.net/feed) | M&A **analysis** (exit quality, reported vs. real values, portfolio roll-ups) | **Low** | RSS / newsletter | Weekly-ish | Jul 2026 piece “Not all cyber acquisitions are created equal” — interpretive, not a deal feed. Useful for confidence calibration, not collection. |
| 17 | Cybersecurity Ventures — M&A Report hub | https://cybersecurityventures.com/mergers-and-acquisitions-report/ | Hub page + category archive | **Low** | Official public HTML | **Stale** | Hub shows **“Loading…”** widget (no live deal list). Category archive (https://cybersecurityventures.com/category/mergers-acquisitions-report/) latest numbered quarterly report is **2021** (Vol. 4). Wrong path `/cybersecurity-mergers-and-acquisitions/` **404**. Copyright warning against unauthorized reproduction. |
| 18 | Windsor Drake — Cybersecurity M&A Report 2026 | https://windsordrake.com/cybersecurity-ma-report/ | Executive summary, top 2025 deals table, valuation commentary | **Low** (recap) | **Gated download** — “Available exclusively to fintech founders, executives, and investors” | Annual / H1 | Public page has summary stats; **full report requires form**. Investment-bank marketing, not an open tracker. |
| 19 | Evolution Equity companies | https://www.evolutionequity.com/companies | Cyber portfolio; **Active / Exit** filter; theme, stage, description | **Low–Med** (lagging) | Official public HTML | Static | `/news` page **thin** (placeholder). Exit status without acquirer name or deal date on listing. |
| 20 | YL Ventures news | https://www.ylventures.com/news | Portfolio company news; occasional exit mentions | **Low** | Official public HTML | Frequent portfolio news | Current feed skews **funding/product** (Hush $30M Jul 2026). Weak primary M&A surface; pair with press for YL-backed exits. |
| 21 | Ballistic Ventures | https://www.ballisticventures.com/ | Portfolio carousel + https://www.ballisticventures.com/portfolio | **Low** | Official public HTML | Homepage posts | Portfolio lacks structured **Acquired** filter or exit dates. `/news` **404** (per startup catalog). |
| 22 | TechCrunch — Security category | https://techcrunch.com/category/security/ | General security news; occasional funding/M&A | **Low** | Official public HTML | Daily | Horizon3.ai $250M Series E visible; M&A sparse vs. search URL. |
| 23 | Paladin Capital Group portfolio | https://paladincapgroup.com/portfolio/ | 90+ cyber/deep-tech names; news posts | **Low** | Official public HTML | News 2025–2026 | Name + blurb; **no structured M&A fields**. |
| 24 | GlobeNewswire / Business Wire keyword search | https://www.globenewswire.com/ , https://www.businesswire.com/ | Issuer PR: acquirer, target, value when disclosed | **Med** (primary for some deals) | Manual search / RSS where allowed | Event-driven | No verified dedicated “cybersecurity acquisitions” list URL (PR Newswire list path **404**). Globe search **timed out** in research environment. Use for citation when SecurityWeek/RoS link to PR. ToS: manual lookup, not bulk scrape. |
| 25 | SYN / overlap note — Return on Security funding+M&A in one post | Same as rank 1 | Single weekly pass covers **both** funding and M&A | **High** | Newsletter + manual | Weekly | Startup collection work treated funding only; **M&A section is co-located** and should be read in the same weekly pass when both signals are needed. |

---

## Recommended first-week set (8–10)

Collect manually or via allowed public HTML/RSS **now**, without paid APIs or ToS violations:

| # | Source | URL | Method |
|---:|---|---|---|
| 1 | Return on Security — Security, Funded (M&A section) | https://www.returnonsecurity.com/ | Newsletter + manual read of weekly posts (e.g. `/p/security-funded-256`) |
| 2 | SecurityWeek — M&A category | https://www.securityweek.com/category/cybersecurity-funding-news/ma/ | Official public HTML |
| 3 | SecurityWeek — latest M&A Roundup | https://www.securityweek.com/cybersecurity-ma-roundup-21-deals-announced-in-july-2026/ | Official public HTML (refresh URL each month) |
| 4 | SecurityWeek RSS (M&A filter) | https://www.securityweek.com/feed/ | RSS — filter items for “M&A”, “acquir”, “merger” |
| 5 | TechCrunch — cyber acquisition search | https://techcrunch.com/?s=cybersecurity+acquisition | Manual HTML search |
| 6 | SEC EDGAR 8-K search | https://efts.sec.gov/LATEST/search-index | Official API — declare User-Agent; query 8-K + acquisition terms |
| 7 | Cyberstarts portfolio (Exited) | https://www.cyberstarts.com/portfolio/ | Official public HTML |
| 8 | Forgepoint companies (Acquired filter) | https://forgepointcap.com/companies | Official public HTML (honor crawl-delay 3) |
| 9 | SYN Ventures portfolio (Acquired) | https://www.synventures.com/portfolio | Official public HTML |
| 10 | SiliconANGLE — as major deals break | https://siliconangle.com/ | Manual — search or follow cyber M&A headlines |

**Optional 11th:** The Record — https://therecord.media/ — manual check when SecurityWeek/RoS flag a mega-deal for second source.

**Optional 12th:** Mergr individual deal page — when you need structured buyer history for a known deal (manual, one URL at a time).

---

## What we will miss with only the first-week set

- **Private-company-only deals** never filing 8-K and never picked up by SecurityWeek/RoS (especially non-English or regional MSSP tuck-ins).
- **Undisclosed values** — many RoS and SecurityWeek entries say “undisclosed”; VC portfolio pages never show value.
- **Real-time completeness** — SecurityWeek roundups are **monthly**; RoS is **weekly**; gap for deals announced between posts.
- **Structured machine-readable feed** — without The Signal API (paid) or Momentum/Windsor full reports (gated).
- **PE roll-ups and non-pure-play acquirers** underweighted unless SecurityWeek classifies the deal as cyber.
- **Completion vs. announcement** — press covers announcement; 8-K Item 2.01 covers close for public filers only; we may double-count or miss cancels.
- **Mergr/Crunchbase/PitchBook depth** — buyer league tables, earn-out terms, and long-tail deal history require paid or ToS-blocked sources.

---

## Do-not-scrape / paid-only / blocked list

| Source | Why |
|---|---|
| **Crunchbase** (https://www.crunchbase.com/) | Commercial data product; Terms restrict scraping/automated extraction. Manual lookup only. |
| **PitchBook** | Paid terminal; no public bulk access; Terms prohibit scraping. |
| **LinkedIn** | Login wall; Terms prohibit automated collection. |
| **The Signal API** (https://docs.returnonsecurity.com/) | **Paid** — Pro/Team + $79/mo add-on or Enterprise; includes `/top-acquisitions`, `/top-acquirers-by-volume`. Free tier is dashboard-only. |
| **Momentum Cyber CYBERcloud / full reports** | Proprietary database; complete deal lists behind email-gated PDF downloads on quarterly/H1 pages. |
| **Windsor Drake full report** | Gated download; marketing lead form required. |
| **Mergr bulk database** | 224k+ transactions; export and full search require **signup / paid** trial. Individual deal pages OK for manual citation. |
| **Return on Security RSS** | **403** to curl/non-browser clients; prefer newsletter/HTML posts. |
| **SecurityWeek** (some paths) | `/category/ma-tracker/` returned **Cloudflare 403** to curl; category URL `/category/cybersecurity-funding-news/ma/` fetched via WebFetch. Prefer allowed HTML/RSS, respect bot challenges. |
| **Cybersecurity Ventures** | Copyright warning against unauthorized reproduction; hub widget non-functional; cite linked articles only, do not republish body text. |
| **Forgepoint** | robots.txt crawl-delay 3; avoid query-string URLs. |

---

## Failed or weak verification (looked good, did not pass)

| Source | URL tried | Result |
|---|---|---|
| **Startup collection packet** | `/docs/active/startup-collection-packet-2026-08.md` | **File not found** in repo at research time. RoS M&A overlap confirmed directly via Security, Funded #256 instead. |
| **Cybersecurity Ventures (wrong path)** | https://cybersecurityventures.com/cybersecurity-mergers-and-acquisitions/ | **404** — use `/mergers-and-acquisitions-report/` (stale widget) or category archive. |
| **Cybersecurity Ventures M&A hub widget** | https://cybersecurityventures.com/mergers-and-acquisitions-report/ | Page loads but deal list shows **“Loading…”** only — no verifiable live deals in HTML. |
| **Cybersecurity Ventures M&A articles** | Category archive latest numbered report | **2021** (Vol. 4, No. 4) — not current for 2026 discovery. |
| **Return on Security RSS** | https://www.returnonsecurity.com/rss/ | **403** to curl. |
| **Return on Security (wrong slug)** | `/p/security-funded-256-full-byte-black-hat` | **404** — working slug is `/p/security-funded-256`. |
| **SecurityWeek M&A Tracker category (alt path)** | https://www.securityweek.com/category/ma-tracker/ | **Cloudflare 403** to curl; use `/category/cybersecurity-funding-news/ma/` instead. |
| **SecurityWeek funding category** | https://www.securityweek.com/category/funding/ | **404** (from startup catalog; still failing). |
| **The Record tag** | https://therecord.media/tag/cybersecurity/ | **404**. |
| **The Record search** | https://therecord.media/?s=acquisition | **Timeout** in one fetch; individual article URLs work. |
| **PR Newswire cyber acquisitions list** | https://www.prnewswire.com/news-releases/cybersecurity-latest-news/cybersecurity-acquisitions-list/ | **404**. |
| **GlobeNewswire tag search** | https://www.globenewswire.com/search/tag/cybersecurity%20acquisition | **Timeout** in research environment. |
| **Business Wire news portal** | https://www.businesswire.com/portal/site/home/news/ | **Timeout** — treat as unverified; use when linked from deal articles. |
| **SEC EDGAR company search (HTML)** | https://www.sec.gov/cgi-bin/browse-edgar?... | **Timeout** in one fetch; **efts.sec.gov** JSON search succeeded with User-Agent. |
| **Evolution Equity news** | https://www.evolutionequity.com/news | **Thin** — placeholder content. |
| **Ballistic /news** | https://www.ballisticventures.com/news | **404** (confirmed from startup catalog). |
| **Mergr cyber-only index** | https://www.mergr.com/transaction/cybersecurity | Returns **general** transactions, not cyber-filtered list. |

---

## Proposed deal record fields (for a later collection week)

Do **not** start collection until lead authorizes the manual week. When ready, each deal should capture:

| Field | Description |
|---|---|
| **acquirer** | Legal or trade name of buying entity |
| **target** | Legal or trade name of acquired company |
| **category** | Security domain (identity, cloud/CNAPP, data security, MSSP, OT/ICS, AI security, GRC, etc.) |
| **announce_date** | Date deal was announced as stated by source |
| **close_date** | Date completed if stated; blank if pending |
| **value** | Disclosed amount + currency; `undisclosed` if absent; note `reported` vs. `confirmed in filing` |
| **deal_status** | `announced`, `completed`, `terminated`, `rumored` |
| **source_url** | Canonical page cited |
| **excerpt** | Short verbatim or paraphrased quote of what the source says (quote marks if verbatim) |
| **why_it_might_matter** | One–two sentences on GTM/security-market relevance — provisional, not investment advice |
| **confidence** | `high` / `medium` / `low` based on source directness (8-K > TC > “reported”) |
| **collector** | Who captured it |
| **collected_at** | ISO date of capture |

---

## Research notes

- All URLs above were fetched, searched, or HEAD-checked on **2026-08-16** unless marked failed.
- **Return on Security overlap:** Weekly Security, Funded posts combine funding and M&A in one issue. The startup source catalog (`SEC-MARKET-STARTUP-SRC-001`) scoped funding only; the M&A section in the same posts was intentionally ignored — it is now the **primary rank-1 source** for this catalog.
- **SecurityWeek tracker:** Described internally (deal counts in articles) but **no separate public database UI** verified — discovery is via category page, roundups, and RSS.
- No scraper code, selectors, or collector implementations were written as part of this research packet.
