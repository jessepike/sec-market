# M&A intelligence — how we operate

One page for leadership and operators. Detail lives in [ma-source-catalog.md](ma-source-catalog.md).

| Field | Value |
|---|---|
| **ID** | `SEC-MARKET-INT-MA-001` |
| **Updated** | 2026-08-16 |
| **Live surface** | Same Activity board as funding (five shared lead slots) |

---

## Question we answer

**Which cybersecurity companies are being bought, by whom, at what disclosed value — and what does that say about platform consolidation vs. buyer demand?**

We do **not** give investment advice. We answer: *what deals happened, with sources, and whether they are capital events or proof customers are spending.*

---

## Insight we provide

| Output | What it tells leadership |
|---|---|
| **Shared lead slots** | M&A competes with funding for five headlines — mega-deals and strategic acquirers can take a slot |
| **Deal note** | Announced vs closed; LOI vs completion; value disclosed or not |
| **Platform pattern** | e.g. identity buyers now seeding agent control; raise-then-acquirer (Cyera → Oasis) |
| **Evidence drawer** | SecurityWeek, 8-K, or RoS link per deal |

**Decision it drives:** Account teams watch **consolidation** (who owns the category now), **partner risk** (portfolio company acquired), and **timing** (announce ≠ close ≠ spend). Do **not** treat 2025 announce dates as this month’s demand signal.

---

## Sources we pull (10 primary — multi-source)

| # | Source | URL | What we get | How often |
|---|---|---|---|---|
| 1 | **Return on Security** — M&A section in Security, Funded | https://www.returnonsecurity.com/ | Weekly M&A block: acquirer, target, value, category | **Weekly** (same post as funding) |
| 2 | **SecurityWeek — M&A category** | https://www.securityweek.com/category/cybersecurity-funding-news/ma/ | Breaking deals + context | **2×/week scan** |
| 3 | **SecurityWeek — monthly roundup** | New URL each month (e.g. July 2026 roundup) | 15–25 named deals, “other deals” long tail | **Monthly** (~1st week) |
| 4 | **SecurityWeek RSS** | https://www.securityweek.com/feed/ | Filter: acquire, M&A, merger | **Daily filter** (automated read OK; no scrape of full site) |
| 5 | **TechCrunch** — cyber acquisition search | https://techcrunch.com/?s=cybersecurity+acquisition | Large and mid-market deals | **Weekly search** |
| 6 | **SEC EDGAR 8-K** | https://efts.sec.gov/LATEST/search-index | Public acquirer filings; definitive agreement / close | **Weekly search** (declared User-Agent) |
| 7 | **Cyberstarts portfolio (Exited)** | https://www.cyberstarts.com/portfolio/ | Confirms exit + buyer name | **Weekly spot-check** |
| 8 | **Forgepoint (Acquired filter)** | https://forgepointcap.com/companies | Exit confirmation; no dates/values | **Weekly spot-check** |
| 9 | **SYN Ventures (Acquired)** | https://www.synventures.com/portfolio | Same | **Weekly spot-check** |
| 10 | **SiliconANGLE / The Record** | Manual | Mega-deal second source | **Event-driven** |

**Optional:** Mergr individual deal pages (manual, one URL at a time). **Not authorized:** Crunchbase, PitchBook, Signal API without paid terms.

---

## Refresh cycle

| Cadence | Action | Who |
|---|---|---|
| **Weekly (Tue)** | Read RoS M&A section + SecurityWeek category since last check | Lead gather |
| **Monthly (~1st week)** | Read SecurityWeek M&A roundup; reconcile against Activity background | Lead gather |
| **Event-driven** | Deal >$500M or strategic (PANW, Google, Cisco-class) | Same-day capture + headline review |
| **On Activity ship** | M&A rows in same five lead slots as funding | Lead synthesize |

**We do not wait** for RoS alone — SecurityWeek and EDGAR run on their own schedule.

---

## How we aggregate

1. Same Activity surface as funding — one board, shared five headlines.
2. **Status field:** announced / LOI / completed / rumored.
3. **Value:** disclosed amount, `undisclosed`, or filing-confirmed.
4. **Demote** Feb/Mar mega-closes (Wiz, CyberArk) to background when newer window leads exist.
5. **Avoid collision** with market call Avoid line: announcements ≠ demand; closes = capital, not spend.

---

## Signal quality (honest)

| Strength | Limitation |
|---|---|
| Good on **named cyber deals** in SecurityWeek + RoS | Private-only deals never in press |
| 8-K high confidence for **public filers** | Misses all-private acquirers |
| Monthly roundup catches **mid-market MSSP** tuck-ins | Gap between weekly RoS and monthly roundup |
| Platform pattern readable across deals | Undisclosed values common; do not invent |

**Comfort level:** High for “deal happened with a source.” Medium for completeness. Low for using M&A as **buyer spend** proxy.

---

## Next actions this intelligence drives

- **Account qualification:** Is the client exposed to a target being acquired or a acquirer’s bundle?
- **Partner conversations:** Portfolio exit → roadmap and support questions.
- **Category map:** Identity → agent control absorption (current read).
- **Do not:** Reframe infrastructure-lag market call from deal news alone.
