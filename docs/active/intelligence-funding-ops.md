# Funding & startup intelligence — how we operate

One page for leadership and operators. Detail lives in [startup-source-catalog.md](startup-source-catalog.md).

| Field | Value |
|---|---|
| **ID** | `SEC-MARKET-INT-FUND-001` |
| **Updated** | 2026-08-16 |
| **Live surface** | Activity board → M&A and startups (lead / more / background) |

---

## Question we answer

**Where is private capital going in cybersecurity startups — and does it signal buyer spend or just category formation?**

We do **not** answer “should we invest?” We answer: *what names and categories are getting funded, at what stage, with what evidence — so account and GTM teams know what to prepare for and what not to over-read.*

---

## Insight we provide

| Output | What it tells leadership |
|---|---|
| **Section read** (one paragraph) | Pattern in the window — e.g. platform absorption, stage-spread, capital ahead of revenue |
| **Five lead headlines** | The five funding events worth account attention this edition |
| **More / background** | Context without drowning the first screen |
| **Evidence drawer** | Source, date, excerpt — every headline is checkable |

**Decision it drives:** Prepare for named categories (agent governance, AI-native identity, DSPM) in accounts with matching exposure. Do **not** treat raises as proof of enterprise buyer spend.

---

## Sources we pull (multi-source — not one newsletter)

### Tier 1 — primary weekly sources (dated rounds, amounts)

| Source | URL | What we get | How often |
|---|---|---|---|
| Return on Security — Security, Funded | https://www.returnonsecurity.com/ | Weekly cross-market rounds with amounts, investors, categories | **Weekly** (when Mike publishes — usually Monday) |
| Cybersecurity Ventures VC articles | https://cybersecurityventures.com/cybersecurity-venture-capital-vc-deals/ | Periodic deal roundups with amounts | **When a new linked article posts** (~weekly–monthly) |

### Tier 2 — discovery (names, stage, thin dates)

| Source | URL | What we get | How often |
|---|---|---|---|
| SYN Ventures portfolio | https://www.synventures.com/portfolio | Round + year labels; best VC timing signal | **Weekly spot-check** (~15 min) |
| Forgepoint companies | https://www.forgepointcap.com/companies | First-partnered year; sector tags | **Weekly spot-check** |
| Team8 portfolio | https://team8.vc/portfolio/ | Founded year; builder/launch signal | **Weekly spot-check** |
| YL Ventures news | https://www.ylventures.com/news | Dated portfolio announcements | **Weekly spot-check** |
| Ballistic / Cyberstarts / Evolution / Paladin portfolios | See catalog | Active bets; exit flags | **Weekly spot-check** (rotate 2–3 per week) |

### Tier 3 — garnish (event-driven)

| Source | URL | When |
|---|---|---|
| Y Combinator cyber list | https://www.ycombinator.com/companies/industry/cybersecurity | Manual browse when a launch story matters |
| SecurityWeek RSS | https://www.securityweek.com/feed/ | Filter for “raised”, “funding”, “seed” |
| Company press / Globe Newswire | Per deal | When RoS or VC page flags a name without amount |

**We do not use:** Crunchbase bulk, PitchBook, LinkedIn, Funded Startups Daily automation (ToS-blocked).

---

## Refresh cycle

| Cadence | Action | Who | Output |
|---|---|---|---|
| **Weekly (Tue AM)** | Read latest Security, Funded + 15-min VC spot-check | Lead gather | Working packet if anything new |
| **Weekly (Tue PM)** | Draft read + five headlines; top headline stays unless macro changes | Lead synthesize | Draft for lead check |
| **Monthly (or when material)** | Ship Activity edition to live site | Lead → push `main` | Updated https://securitymarketpulse.com |
| **Event-driven** | Mega-round ($100M+) or category-defining name | Same day gather | May promote one headline between editions |

**Current edition window:** Jul 6 – Aug 10, 2026 (RoS #252–#256). **Live leads:** Zenity, Oak, Hush, Oasis, Onyx.

---

## How we aggregate

1. **Capture** — one row per event: company, date, round, amount, source URL, excerpt, confidence.
2. **Dedupe** — same round from RoS + company PR → one headline, both sources linked.
3. **Resolve conflicts** — show both amounts (e.g. Zenity $115M + $10M vs $125M total framing).
4. **Rank surfaces** — five `lead`, rest `more` or `background`. No 58-row dump.
5. **Ship** — static data in repo → preview → `main` → Vercel.

---

## Signal quality (honest)

| Strength | Limitation |
|---|---|
| Strong on **dated rounds $10M+** in RoS window | Misses generalist-led seeds before press |
| Strong when **company PR confirms** amount | Portfolio pages often have name only, no $ |
| Conflicts shown, not flattened | APAC/LatAm under-covered unless RoS picks up |
| Capital ≠ buyer spend — always labeled | No ARR for private companies; survey intent ≠ bookings |

**Comfort level:** High for “what got funded this window with a source.” Medium for “complete long tail.” Low for “this equals enterprise demand.”

---

## Next actions this intelligence drives

- Qualify accounts in **named categories** (agent governance, AI identity, DSPM).
- **Do not** launch broad campaigns from funding noise alone.
- Watch for **first disclosed agentic-identity revenue** on the site before treating agent governance as buyer spend.
- Pair with **vendor prints** (public ARR) and the **published top headline** (Episode 002 macro read).
