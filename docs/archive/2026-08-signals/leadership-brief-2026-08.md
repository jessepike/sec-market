# Leadership brief — Security Market Pulse

**For:** Jesse Pike → security leadership  
**Date:** 2026-08-16  
**Live site:** https://securitymarketpulse.com  
**Read time:** 5 minutes

---

## What this is (say this out loud)

We built a **public website** that answers: *What is happening in the cybersecurity market, what changed, and can I verify it?*

It is **not** investment advice. It is **not** Crunchbase. It is **not** a daily news feed.

It joins four things on one page:

1. **Top headline / market read** — our published research conclusion (infrastructure is ahead; security is splitting; we do not claim a broad boom)
2. **Vendor table** — who is actually printing revenue or ARR, by domain, with a source link on every row
3. **Tempo** — six domains with a simple action: PREPARE or WATCH
4. **Activity** — funding and M&A this window, with five lead stories and sources

---

## What’s live today

| Piece | What leadership sees |
|---|---|
| Site | https://securitymarketpulse.com on our domain |
| Vendor table | **40+ rows** across Network, Cloud, Data, Identity, SecOps, AI runtime, Platform, Infrastructure |
| Cloud domain | Wiz, Falcon Cloud, Upwind, Orca (2026 TD SYNNEX deal + last equity), Aqua (last equity), Prisma AIRS customers |
| Data domain | Rubrik, Varonis, Cyera, BigID, Sentra, Securiti/Veeam close |
| Identity | Okta, SailPoint, Oak, Hush, Veza/ServiceNow, plus PE/bundled names |
| SecOps | SentinelOne, CrowdStrike, Cisco, XSIAM, Torq, Tines |
| AI runtime | Zenity, Onyx, WitnessAI, Lakera/Check Point |
| Activity | Zenity, Oak, Hush, Cyera/Oasis, Onyx — Jul 6–Aug 10 window |
| Ops docs | Where we pull funding, M&A, and vendor data; how often; what decisions it drives |

---

## Plain English on the confusing parts

### “Orca and Aqua silent” — what we meant vs what we did

**Old (bad) message:** we had no row for them.

**Truth:** Neither company published **2025–2026 revenue or ARR** on official pages we checked. That is normal for private vendors.

**What we put on the site instead (sourced):**

- **Orca** — Apr 2026 TD SYNNEX distribution deal (2026 go-to-market signal) + last disclosed equity Oct 2021 ($1.8B Series C)
- **Aqua** — Jan 2024 Series E extension ($60M, valuation above $1B, $325M total raised)

We label these **capital / coverage**, not buyer spend. We do not invent ARR.

### “Market call frozen” — what that actually means

The **big headline at the top** comes from a completed research project (Episode 002, August 2026):

> Infrastructure spending is way up. Security is mixed, not booming. We will **not** claim a stable “infrastructure leads security by X quarters” lag — the evidence does not support it.

**Frozen** = we do **not** rewrite that headline every time a startup raises money.

**It changes only when:** buyer budget data, vendor prints across the board, or other macro evidence force a new conclusion — and **you** sign off on the new call.

Weekly funding news updates the **Activity board**, not the top headline.

### “Decision proof” — what we need to do

Success for this project is **not** “we shipped a site.” Success is: **someone made a better account or GTM decision because of it.**

**Concrete next step:**

1. Use the site in **two** account or leadership conversations in the next two weeks.
2. For each, write one line: *what you looked at, what you decided differently (or confirmed), which source you clicked.*
3. Log it in `docs/archive/2026-08-web-mvp/decision-impact-log.md`.

That is the proof. Without it, we have a product but not evidence of value.

---

## Where we pull information (multi-source)

Return on Security is **one** weekly newsletter among many. We also use:

| Signal type | Examples | How often |
|---|---|---|
| Funding / startups | Return on Security, Cybersecurity Ventures, VC portfolio pages (SYN, Forgepoint, YL, etc.) | Weekly gather |
| M&A | Return on Security M&A section, SecurityWeek, SEC 8-K filings, TechCrunch | Weekly + event-driven |
| Public vendor prints | Company IR, SEC filings, earnings calls | Each earnings season |
| Private vendor context | Company press when they disclose raises or deals | Event-driven |

Full source lists: `intelligence-funding-ops.md`, `intelligence-ma-ops.md`, `intelligence-domains-ops.md`.

---

## Honest gaps (still true)

| Gap | Plain language |
|---|---|
| Manual process | A person runs the weekly gather (~2 hours). No scraper yet. |
| Activity cadence | Monthly edition, not daily news — by design. |
| Private vendor ARR | Many vendors never publish revenue. We show last disclosed equity or GTM moves instead. |
| Top headline | Stays on Episode 002 until macro evidence changes — not a bug. |
| Decision proof | Not collected yet — see above. |

---

## What to tell leadership (30 seconds)

“We have a live market intelligence site that joins macro research, vendor revenue prints, domain guidance, and sourced funding/M&A — with evidence on every claim. Cloud, data, identity, SecOps, and AI runtime vendor tables are populated from official sources. The top headline is our published research call and does not swing on every funding round. Next: prove it changes real account decisions in two conversations, keep the weekly multi-source gather running, refresh Activity monthly or when the window moves.”

---

## Optional ask

Use the site in **two conversations** and log what changed in `decision-impact-log.md`.
