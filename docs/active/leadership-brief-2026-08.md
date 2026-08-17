# Leadership brief — Security Market Pulse

**For:** Jesse Pike → security leadership  
**Date:** 2026-08-16  
**URL:** https://securitymarketpulse.com  
**Read time:** 5 minutes

---

## What this is

A **public, evidence-linked cybersecurity market intelligence site** — not a research PDF, not Crunchbase, not investment advice.

**Governing intent:** Help security leaders, account teams, and clients time GTM, account, and technology decisions using **sourced** market signals they can verify in two minutes.

---

## Vision

A **living scorecard** that joins:

- **Macro call** — what the market is doing (frozen research edition today)
- **Vendor prints** — who is actually printing revenue/ARR
- **Domain tempo** — where to PREPARE vs WATCH
- **Capital activity** — funding and M&A, labeled as capital not buyer spend

One page. Progressive disclosure. Every headline opens to source + excerpt.

---

## What’s done (shippable today)

| Deliverable | Status |
|---|---|
| Public site on custom domain | **Live** |
| Infrastructure-lag market call (NO-CALL) | **Live** — Episode 002 |
| Judgment layer (Read: Do/Avoid/confidence) | **Live** |
| Vendor prints table (20+ rows, 6 domains) | **Live** — incl. Cato, Netskope, Falcon Cloud |
| Tempo board (6 domains) | **Live** |
| Activity edition — platform absorption read | **Live** — Zenity, Oak, Hush, Oasis, Onyx |
| Multi-source research catalogs (funding, M&A, domains) | **Done** — operator docs |
| Weekly desk runbook + first gather packet | **Done** |
| Deploy path (local → GitHub → Vercel) | **Proven** |

---

## Why it isn’t “there” yet (honest)

| Gap | Why it matters | Path |
|---|---|---|
| **Manual gather** — no scrapers/schedulers yet | Refresh depends on operator cadence, not a machine | Weekly loop ~2 hr; prove value before automation |
| **Monthly Activity edition** vs daily news | By design — not a ticker | Weekly gather; ship when window moves |
| **Multi-source not fully exercised every week** | Catalogs exist; habit still forming | Tuesday gather across 10+ sources per ops docs |
| **Cloud vendor bench** — Orca, Aqua silent | Can’t invent prints | NO-PRINT until public signal |
| **Market call frozen** | Correct governance — no auto-publish | Changes only with falsifier + owner sign-off |
| **No “did this change a decision?” proof yet** | Success = decision impact, not ship count | Use in 2–3 account conversations; record what moved |

**We are not waiting on one newsletter.** Return on Security is the **spine**, not the only source. SecurityWeek, EDGAR, VC portfolios, and company IR run on their own schedules — documented in the ops artifacts.

---

## How intelligence is organized (four ops docs)

| Doc | Covers |
|---|---|
| [intelligence-funding-ops.md](intelligence-funding-ops.md) | Startup/funding sources, cadence, questions, decisions |
| [intelligence-ma-ops.md](intelligence-ma-ops.md) | M&A sources, cadence, questions, decisions |
| [intelligence-domains-ops.md](intelligence-domains-ops.md) | Per-domain vendors, earnings cycles, postures |
| [intelligence-dashboard-ops.md](intelligence-dashboard-ops.md) | How the live page ties together |

---

## Operating cadence (no babysitting)

| When | What | Who |
|---|---|---|
| **Every Tuesday** | Gather funding + M&A from 10+ sources | Lead (autonomous) |
| **Monthly or material** | Ship Activity edition refresh | Lead → Vercel |
| **Each earnings season** | Update vendor prints + Tempo copy | Lead |
| **Rare** | Change published market call | **Owner sign-off** |

---

## What to tell leadership

1. **We have a live product** — not a deck — at securitymarketpulse.com.
2. **It joins macro, vendor, domain, and capital signals** with evidence on every claim.
3. **It is intentionally not a boom ticker** — capital is labeled; market call is frozen until evidence forces change.
4. **Next 30 days:** run the weekly multi-source loop, use in account conversations, fill cloud bench when signals appear, prove decision value before building automation.

---

## One-line ask (optional)

Use this site in **two client or internal account conversations** in the next two weeks and tell us whether the Activity read or Tempo postures changed how you qualified the account.
