# SEC-009 execution plan

Steering page. Detail in the intelligence ops docs and [leadership-brief-2026-08.md](leadership-brief-2026-08.md).

| Field | Value |
|---|---|
| **Governs** | [intent.md](../../intent.md) `SEC-MARKET-001` v1.1 |
| **Owner loop** | Market call change only |

---

## Artifacts (leadership + operators)

| Artifact | Purpose |
|---|---|
| [leadership-brief-2026-08.md](leadership-brief-2026-08.md) | **Take to leadership** — vision, done, gaps, cadence |
| [intelligence-funding-ops.md](intelligence-funding-ops.md) | Startup/funding sources, refresh, decisions |
| [intelligence-ma-ops.md](intelligence-ma-ops.md) | M&A sources, refresh, decisions |
| [intelligence-domains-ops.md](intelligence-domains-ops.md) | Domain vendors, earnings, postures |
| [intelligence-dashboard-ops.md](intelligence-dashboard-ops.md) | How the live page joins signals |

Research depth: [startup-source-catalog.md](startup-source-catalog.md), [ma-source-catalog.md](ma-source-catalog.md), [domain-coverage-map.md](domain-coverage-map.md).

---

## One goal

Reader opens https://securitymarketpulse.com, sees what moved, verifies sources, decides what to prepare — **two minutes**.

**Done (2026-08-16):** Activity edition live (`160c29c`). Prints + Read + Tempo live. Ops artifacts above on `main`.

---

## Autonomous loops (no owner unless Loop E)

| Loop | When | Action |
|---|---|---|
| **A — Weekly gather** | **Every Tuesday** | [Funding ops](intelligence-funding-ops.md) + [M&A ops](intelligence-ma-ops.md) — 10+ sources, not RoS-only |
| **B — Activity ship** | Material window OR monthly | Update Activity → preview → `main` → Vercel |
| **C — Prints pass** | Earnings season | [Domain ops](intelligence-domains-ops.md) — IR/SEC → prints + Tempo |
| **D — Live honesty** | Contradiction | Fix join → ship |
| **E — Market call** | Falsifier | **Owner only** |

Return on Security is **one spine**, not a gate. SecurityWeek, EDGAR, VC portfolios, and company IR run on their own schedules in Loop A.

---

## Current state

| Surface | Live |
|---|---|
| Market call | Episode 002 NO-CALL — frozen |
| Read / Prints / Tempo | Yes |
| Activity | Zenity / Oak / Hush / Oasis / Onyx — window Jul 6 – Aug 10 |

**Next autonomous action:** Loop A on next Tuesday — full multi-source gather per ops docs.
