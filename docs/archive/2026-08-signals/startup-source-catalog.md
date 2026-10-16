# Startup source catalog

## Control

| Field | Value |
|---|---|
| **ID** | `SEC-MARKET-STARTUP-SRC-001` |
| **Date** | 2026-08-16 |
| **Status** | research — lead reviewed 2026-08-16 |
| **Scope** | Startups only (new launches and funding). M&A out of scope. |
| **Authority** | `SEC-MARKET-SIG-JOB-001` |

---

## Verdict

The most useful **new-company discovery** for cybersecurity startups lives in three layers:

1. **Specialist cyber VC public surfaces** — SYN Ventures, Forgepoint, Team8, Ballistic, Cyberstarts, YL Ventures, Evolution Equity, and Paladin publish portfolio companies with descriptions; SYN and Forgepoint also expose round/stage or “first partnered” timing. These are the best lawful repeat sources for *their* bets, including 2025–2026 names (e.g., SYN lists Arcade Seed 2026, Nullify Seed 2026; Team8 lists Act, Fig, Jazz founded 2025).

2. **Curated funding intelligence** — Return on Security’s weekly **Security, Funded** posts and Cybersecurity Ventures VC blog posts aggregate cross-market rounds with dates and amounts. Funded Startups Daily tags ~55 cybersecurity raises with round, amount, and excerpt, but its Terms of Service forbid automated extraction.

3. **Launch surfaces** — Y Combinator’s cybersecurity industry list (44 companies, S2026 batch visible) surfaces very new companies with product descriptions; it is strong for *launch* discovery, weaker for round detail.

**This week (manual, no paid API, no ToS fight):** specialist VC portfolio pages, YL Ventures news, Return on Security weekly posts (subscribe/read), Cybersecurity Ventures VC articles, Y Combinator cybersecurity list (manual browse), SecurityWeek RSS (filter for funding headlines).

**Later:** The Signal dashboard/API/MCP (Return on Security; API tier referenced in posts), cross-VC generalist portfolios that require heavy JS (Insight, Greylock, Glilot), and any source with explicit anti-scraper ToS (Funded Startups Daily, Crunchbase bulk use).

---

## Ranked sources (~25)

| Rank | Source | URL (verified 2026-08-16) | What we get | New-company discovery? | Collection method | Freshness | Notes / blockers |
|---:|---|---|---|---|---|---|---|
| 1 | Return on Security — Security, Funded | https://www.returnonsecurity.com/ | Weekly posts listing cybersecurity funding rounds, amounts, categories, investors; market summary | **High** | Newsletter + official public HTML posts | Weekly | Main site fetchable without login. `/rss/` returned Cloudflare challenge to curl; treat RSS as unreliable for bots. Posts also reference **The Signal** dashboard/API. |
| 2 | SYN Ventures portfolio | https://www.synventures.com/portfolio | Company name, one-line product, **round + year** (e.g., Series A 2026, Seed 2026), active/acquired status | **High** | Official public HTML | Updated as investments publish | Best specialist VC page for round timing. robots.txt allows general crawl; standard WP rules. |
| 3 | Forgepoint Capital companies | https://forgepointcap.com/companies | 76+ companies; sector (Identity, AppSec, etc.), status, **first partnered year**, investor, location, description | **High** | Official public HTML | Filterable; 2026 entries visible (e.g., Arkenstone Defense) | robots.txt: `Crawl-delay: 3`, `Disallow: /*?` — respect delay; avoid query-string URLs. |
| 4 | Funded Startups Daily | https://fundedstartupsdaily.com/ | ~745 total raises; **55 tagged Cybersecurity** with company, stage, amount, founder, excerpt, source links | **High** | **Blocked** (ToS) / manual browse only | Daily | Site loads without login. **Terms explicitly prohibit** robots/scrapers/bulk copy without written permission; EU Database Rights claimed. Export CSV is paid. Not for automated collection. |
| 5 | Team8 portfolio | https://team8.vc/portfolio/ | Built/invested companies; domain filter (Cybersecurity); **founded year**; product tagline | **High** | Official public HTML | New 2025–2026 cyber builds visible (Act, Fig, Jazz, Frame Security) | Company-builder model → good stealth/launch signal. No round amounts on index. |
| 6 | Y Combinator — Cybersecurity | https://www.ycombinator.com/companies/industry/cybersecurity | 44 YC cyber startups; batch (e.g., S2026), employee count, location, product description | **High** | Official public HTML / **manual** | Current batch visible | robots.txt **`Disallow: /companies?*`** — automated fetch of this filtered URL is disallowed; manual citation OK. |
| 7 | YL Ventures news | https://www.ylventures.com/news | Portfolio funding announcements with dates (e.g., Hush Security $30M Jul 2026), product news | **High** | Official public HTML | Frequent portfolio news | Complements sparse portfolio page. Newsletter signup offered. |
| 8 | Cybersecurity Ventures — VC deal articles | https://cybersecurityventures.com/cybersecurity-venture-capital-vc-deals/ | VC deal-flow hub; linked blog posts list dated rounds with amounts (e.g., Glow $180M, Horizon3.ai $250M) | **High** | Official public HTML / manual | Weekly–monthly articles | Hub page shows “Loading…” widget; **actionable deal lists are in linked articles** (e.g., https://cybersecurityventures.com/extreme-heat-warning-summer-2026-cybersecurity-venture-capital-investments/). Footer warns against unauthorized reproduction — cite and link, do not republish body text. |
| 9 | Ballistic Ventures portfolio | https://www.ballisticventures.com/portfolio | Portfolio companies with product descriptions; private/acquired status | **Med–High** | Official public HTML | New names appear; blog posts on homepage for recent investments | Portfolio lacks round/date fields; “Why we invested” posts on homepage add context. |
| 10 | Cyberstarts portfolio | https://www.cyberstarts.com/portfolio | Israeli cyber portfolio; active/exited; short product descriptions | **Med** | Official public HTML | Active companies flagged | Heavy exit/acquired list; still surfaces active bets (Glow, Upwind, Blockaid, etc.). |
| 11 | Evolution Equity companies | https://www.evolutionequity.com/companies | Cyber portfolio with theme, stage, HQ, leadership, description | **Med** | Official public HTML | Filterable | Good for cyber-only VC; **no funding dates/amounts** on listing. Page timed out once; `/companies` succeeded. |
| 12 | Paladin Capital Group portfolio | https://paladincapgroup.com/portfolio/ | 90+ cyber/deep-tech companies; partial list; news posts mention portfolio rounds | **Med** | Official public HTML | News dated 2025–2026 | `paladincap.com` unreachable here; **`paladincapgroup.com` is correct**. Portfolio is name + blurb, not structured rounds. |
| 13 | Bessemer Venture Partners portfolio (cyber) | https://www.bvp.com/portfolio?sector=cybersecurity | Portfolio companies filterable to cybersecurity (Act Security, Bold Security, Axonius, etc.) with descriptions | **Med** | Official public HTML | Periodic updates | Sector filter works in static HTML. Atlas thought-leadership at `/atlas` is not a deal feed. |
| 14 | a16z investment list | https://a16z.com/investment-list/ | Searchable list of disclosed investments incl. cyber (Wiz, Adaptive Security, Morta Security, etc.) | **Med** | Official public HTML | Updated monthly (per page disclaimer) | Discovery biased to a16z deals; not cyber-filtered; many mature names. |
| 15 | GV portfolio | https://www.gv.com/portfolio | Alphabet VC portfolio alphabetically; many security names (Blockaid, Crash Override, Lacework, Snyk, Veza, Witness AI, etc.) | **Med–Low** | Official public HTML | Static list | No dates/rounds; useful as cross-check when a GV-backed security name appears elsewhere. |
| 16 | SecurityWeek | https://www.securityweek.com/ | Cyber news; **RSS at** https://www.securityweek.com/feed/ ; occasional funding pieces (e.g., Obsidian Security $85M, Team8 fund) | **Med–Low** | RSS / official HTML | Daily | `/category/funding/` **404**. Must filter general feed for funding keywords. Heavy breach/vuln mix. |
| 17 | TechCrunch — Security | https://techcrunch.com/category/security/ | Security news; some funding stories (e.g., Horizon3.ai $250M Series E) mixed with incidents | **Med–Low** | Official public HTML / RSS | Daily | `/tag/funding/` is general tech funding, not cyber-specific. |
| 18 | NightDragon portfolio | https://www.nightdragon.com/portfolio | Current portfolio (Horizon3.ai, HUMAN, Immuta, etc.) with descriptions | **Low–Med** | Official public HTML | Static | Broad security-adjacent (space, physical, cyber). **No round/date fields.** |
| 19 | YL Ventures portfolio | https://www.ylventures.com/portfolio | Israeli cyber portfolio by category (DLP, identity, cloud, etc.) | **Low–Med** | Official public HTML | Static grid | Thin metadata; pair with `/news`. |
| 20 | Accel companies | https://www.accel.com/companies | 772-company directory; theme filters include security-related names when browsed | **Low–Med** | Official public HTML (JS “Load more”) | Continuous | `?theme=security` renders shell with filters; company detail requires interaction. Not cyber-first. |
| 21 | Sequoia companies | https://www.sequoiacap.com/companies/ | Portfolio spotlight list (includes Vanta, etc.) | **Low** | Official public HTML | Periodic | No cyber filter; recap-heavy. |
| 22 | Venture in Security | https://ventureinsecurity.net/ | Substack on cyber business; **RSS:** https://ventureinsecurity.net/feed | **Low** | RSS / newsletter | Weekly-ish | Analysis and market structure; **not a systematic funding tracker**. RSS verified. |
| 23 | The Signal (Return on Security) | https://signal.returnonsecurity.com/ | Dashboard intro for funding, M&A, investors, categories | **Med** (if dashboard usable) | Manual / possible API later | Real-time (per site copy) | Landing page fetchable. Newsletter states dashboard + MCP/API for full data — **API likely paid/restricted**; do not assume free bulk access. |
| 24 | SiliconANGLE — funding search | https://siliconangle.com/?s=cybersecurity+funding | Search results (~1600) for “cybersecurity funding” | **Low–Med** | Official HTML search / manual | Ongoing | `/category/security/` is general security news, not funding-specific. Cookie banner on fetch. |
| 25 | DataTribe portfolio | https://www.datatribe.com/portfolio/ | Tagline only (“empowering… cybersecurity and data science companies”) | **Low** | Official public HTML | Unknown | **Extremely thin** — no company list in static HTML. Kept as placeholder VC family check; replace when/if they publish a list. |

---

## Recommended first-week set (8–10)

Collect manually or via allowed public HTML/RSS **now**, without paid APIs or ToS violations:

| # | Source | URL | Method |
|---:|---|---|---|
| 1 | SYN Ventures portfolio | https://www.synventures.com/portfolio | Official public HTML |
| 2 | Forgepoint companies | https://forgepointcap.com/companies | Official public HTML (honor crawl-delay 3) |
| 3 | Team8 portfolio | https://team8.vc/portfolio/ | Official public HTML |
| 4 | Ballistic portfolio | https://www.ballisticventures.com/portfolio | Official public HTML |
| 5 | Cyberstarts portfolio | https://www.cyberstarts.com/portfolio | Official public HTML |
| 6 | YL Ventures news | https://www.ylventures.com/news | Official public HTML |
| 7 | Evolution Equity companies | https://www.evolutionequity.com/companies | Official public HTML |
| 8 | Paladin portfolio | https://paladincapgroup.com/portfolio/ | Official public HTML |
| 9 | Return on Security — Security, Funded | https://www.returnonsecurity.com/ | Newsletter + manual read of weekly posts |
| 10 | Cybersecurity Ventures VC articles | https://cybersecurityventures.com/cybersecurity-venture-capital-vc-deals/ | Manual read of linked deal-flow posts |

**Optional 11th (manual only):** Y Combinator cybersecurity list — https://www.ycombinator.com/companies/industry/cybersecurity (robots disallow automated query URLs).

**Optional RSS add:** SecurityWeek feed https://www.securityweek.com/feed/ — filter items for funding keywords.

---

## What we will miss with only the first-week set

- **Non-portfolio rounds** — Companies funded by generalist VCs (Insight, Lightspeed, Sequoia, etc.) before appearing on a cyber VC site.
- **Stealth/pre-announcement** — Names that exist only in press or curated trackers until a VC publishes.
- **Structured round fields** — Many portfolio pages omit amount, lead investor, or exact date; SYN/Forgepoint are exceptions, not the rule.
- **Geographic blind spots** — Underweights APAC/LatAm unless covered by YC, SecurityWeek, or Return on Security that week.
- **Seed/long-tail** — Cybersecurity Ventures and Return on Security skew toward larger rounds; tiny seeds may be absent.
- **Funded Startups Daily coverage** — 55 tagged cyber raises exist there, but ToS blocks automated collection; manual spot-checks only unless licensed.

---

## Do-not-scrape / paid-only / blocked list

| Source | Why |
|---|---|
| **Crunchbase** (https://www.crunchbase.com/) | Commercial data product; Terms restrict scraping/automated extraction. robots.txt blocks `/search`, `/discover`, `/v4`. Use manual lookup only if needed. |
| **PitchBook** | Paid terminal; no public bulk access; Terms prohibit scraping. |
| **LinkedIn** | Login wall; Terms prohibit automated collection. |
| **Funded Startups Daily** | ToS §2: no robots/scrapers/bulk copy without written permission; EU Database Rights assertion. Manual browse OK; automation blocked. |
| **The Signal API/MCP** | Referenced as productized market intelligence; assume paid/restricted until terms reviewed. Dashboard browsing manual only for now. |
| **Return on Security RSS** | Cloudflare challenge on `/rss/` to non-browser clients; prefer newsletter/HTML posts. |
| **Cybersecurity Ventures** | Explicit copyright warning against unauthorized reproduction; cite with links, do not republish full text. |
| **Y Combinator filtered company URLs** | robots.txt `Disallow: /companies?*` — do not automate this URL pattern. |
| **Insight Partners portfolio** | https://www.insightpartners.com/portfolio/ — SPA shell with no portfolio data in static HTML (failed as collection target). |
| **CyberStartupFunding.com** | Could not verify live from research environment (503/timeout/DNS failure on 2026-08-16). Do not use until independently reachable. |

---

## Failed or weak verification (looked good, did not pass)

| Source | URL tried | Result |
|---|---|---|
| **Ten Eleven Ventures** | https://www.teneleven.vc/ , `/portfolio` | **503 Service Unavailable** on all attempts |
| **CyberStartupFunding** | https://cyberstartupfunding.com/ | **503 / unreachable** (WebFetch 503; curl DNS/connection failure). Indexed content describes a tracker, but live page not verified here. |
| **Glilot Capital portfolio** | https://www.glilotcapital.com/portfolio | Page loads but **company names not present in static HTML** (JS shell / “Acquired by” placeholders only) |
| **Insight Partners portfolio** | https://www.insightpartners.com/portfolio/ | **Empty portfolio content** without full JS render |
| **Greylock portfolio** | https://greylock.com/portfolio/ | **No company list** in fetched HTML (marketing shell only) |
| **Lightspeed — security filter** | https://www.lsvp.com/portfolio/?sector=security | **“No results”** for security sector filter |
| **S32 / Section 32** | https://s32.com/ | Marketing site only; **no public portfolio list** |
| **DataTribe** | https://www.datatribe.com/portfolio/ | **Thin** — tagline without company roster |
| **Paladin (wrong domain)** | https://www.paladincap.com/portfolio/ | **503/unreachable**; unrelated `paladin.com` resolves to Arkema industrial site |
| **FundedStartupsDaily category URL** | https://fundedstartupsdaily.com/?category=Cybersecurity | Query param does not server-filter; **745 raises returned** — cyber filter is client-side (55 cyber visible in UI) |
| **SecurityWeek funding category** | https://www.securityweek.com/category/funding/ | **404** |
| **Ballistic /news, /insights** | https://www.ballisticventures.com/news | **404** — use homepage carousel + portfolio instead |
| **Cybersecurity Ventures (wrong path)** | https://www.cybersecurityventures.com/cybersecurity-startup-funding/ | **404** — use `/cybersecurity-venture-capital-vc-deals/` and linked articles |

---

## Proposed event record fields (for a later collection week)

Do **not** start collection until lead authorizes the manual week. When ready, each event should capture:

| Field | Description |
|---|---|
| **company** | Legal or trade name |
| **category** | Security domain (identity, cloud, AppSec, AI security, OT, etc.) |
| **event_date** | Announcement or round date as stated by source |
| **event_type** | `launch`, `seed`, `series_a`, `series_b+`, `stealth_exit`, `other_funding` |
| **round** | Round label if stated |
| **amount** | Disclosed amount + currency; mark `undisclosed` if absent |
| **investors** | Lead and named participants when public |
| **source_url** | Canonical page cited |
| **excerpt** | Short verbatim or paraphrased quote of what the source says (with quote marks if verbatim) |
| **why_it_might_matter** | One–two sentences on GTM/security-market relevance — provisional, not investment advice |
| **confidence** | `high` / `medium` / `low` based on source directness |
| **collector** | Who captured it |
| **collected_at** | ISO date of capture |

---

## Research notes

- All URLs above were fetched or HEAD-checked on **2026-08-16** unless marked failed.
- No scraper code, selectors, or collector implementations were written as part of this research packet.
- M&A sources intentionally excluded per job scope.
