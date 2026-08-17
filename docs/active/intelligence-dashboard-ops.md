# Dashboard — how the live page ties together

One page for leadership. Product contract: [web-mvp-product-contract.md](web-mvp-product-contract.md).

| Field | Value |
|---|---|
| **ID** | `SEC-MARKET-INT-DASH-001` |
| **Updated** | 2026-08-16 |
| **URL** | https://securitymarketpulse.com |

---

## Question the full page answers

**What is happening in cybersecurity markets, what changed, why it matters, what to prepare for — and can I verify it in two minutes?**

---

## Components → intelligence type → refresh

| # | Section (nav) | Intelligence | Primary sources | Refresh |
|---|---|---|---|---|
| 1 | **Call** (hero) | Frozen macro market call — infra vs security lag | Episode 002 research freeze | **Rare** — human escalate only |
| 2 | **Read** | Judgment: what changed, Do/Avoid, no-call boundaries | Same + current prints | When market call changes |
| 3 | **Prints** | Public vendor revenue/ARR table by domain | IR, SEC, company press | **Quarterly** + event-driven |
| 4 | **Tempo** | Domain posture: PREPARE / WATCH + why | Prints + domain vendor pass | **Monthly** review; tags need decision |
| 5 | **Activity** | Funding + M&A capital window | [Funding ops](intelligence-funding-ops.md) + [M&A ops](intelligence-ma-ops.md) | **Monthly edition** + weekly gather |
| 6 | **Layers** (depth) | Infra vs hyperscaler vs security vs buyer panel | Episode 002 panel data | Frozen with research edition |
| 7 | **Watch next** (depth) | Falsifiers and triggers | Governance docs | When call or domain posture changes |
| 8 | **Research** (depth) | Full evidence library | All cited records | Each ship |

---

## How signals aggregate (the story, not a ticker)

```text
Infrastructure panel (NVIDIA, hyperscaler capex)
        ↓
   Market call: infra ahead, security split, NO-CALL on lag
        ↓
Prints (who is actually printing revenue/ARR)
        ↓
Tempo (domain-level PREPARE / WATCH)
        ↓
Activity (private capital — formation, M&A, not buyer spend)
        ↓
Account question: prepare where exposure matches; don't boom-claim
```

**Join rule:** Prints and Activity must not contradict. Example: Wiz/CyberArk on Activity background; Avoid line says don’t treat **announcements** as demand. Cyera on Activity = capital; Rubrik on prints = revenue.

---

## What “good” looks like on first screen (~2 min)

1. **Call** — one headline + context stats (NVIDIA +92%, budgets +4%, NO-CALL).
2. **Read** — three what-changed bullets, Do/Avoid, confidence.
3. **Prints** — scannable table; green/red/yellow values; source link every row.
4. **Tempo** — six domains, one action tag each.
5. **Activity** — five leads + collapsed more/background.

**Not on first screen:** 58-row dump, judgment memo essay, auto-refresh ticker.

---

## Aggregate insight (today’s edition)

| Layer | Message |
|---|---|
| Macro | Infrastructure accelerating; 2025 security budgets did not follow; stable lag not measurable |
| Vendor | Network iron hot; SASE split; data selected vendors up; identity/SecOps mixed |
| Capital | Platforms that bought identity now funding/buying agent control; capital ≠ spend |
| Action | Qualify on exposure; prepare network refresh where in flight; falsifier = agentic-identity revenue |

---

## Decisions the dashboard drives

| Audience | Use |
|---|---|
| **Security leadership / CSPs** | Where to allocate attention; what not to over-claim in market narrative |
| **Account teams** | Qualification questions; named events for client conversations |
| **Clients** | Timing context for tech/partner choices — with evidence to drill into |

**Not for:** Investment picks, vendor selection from prints alone, or replacing pipeline/CRM data.

---

## Honest gaps (why it’s not “finished”)

| Gap | Mitigation |
|---|---|
| Manual multi-source gather — no automation yet | Weekly desk loop documented; ~2 hr/week |
| Activity edition lags real time by design (monthly) | Weekly gather; ship when material |
| Cloud bench short (Orca, Aqua) | NO-PRINT until public signal |
| Market call frozen on Episode 002 | Correct — changes need human gate |
| No regional tuning | Core is national/global per intent |

---

## Operating loops (autonomous — no owner babysitting)

| Loop | Trigger | Action |
|---|---|---|
| **A — Weekly gather** | Every Tuesday | Funding + M&A sources per ops docs → packet |
| **B — Activity ship** | Material new window OR monthly | Update Activity → `main` → Vercel |
| **C — Prints pass** | Earnings season | Update vendor rows + Tempo copy |
| **D — Live honesty** | Contradiction found | Fix prints/Tempo/Avoid/Activity join → ship |
| **E — Market call** | Watch-next falsifier hit | **Escalate to owner** — only human gate |

Owner ping: **Loop E only.**
