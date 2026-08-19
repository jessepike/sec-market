# Security Market Pulse — External Review Brief

## Control

- **Brief ID:** `SEC-MARKET-WEB-REVIEW-001`
- **Version:** `0.1`
- **Product:** Security Market Pulse (`SEC-MARKET-WEB-001`)
- **Edition:** Episode 002 packet, research freeze `2026-08-15`, surface refresh `2026-08-16`
- **Audience:** independent model or human reviewers who do not have the build chat
- **Mode:** read-only product and evidence review
- **Not this review:** Vercel/deploy, shadow collection, lag-methodology rewrite, live data pipeline

Start here. Do not reconstruct product intent from `docs/inbox/` or `docs/archive/`.

## Paste-ready reviewer prompt

Copy everything in the block below into the other session.

```
You are doing a read-only product and evidence review of Security Market Pulse.

Start with docs/active/web-mvp-external-review-brief.md. Then open the local site
(http://localhost:5173/ or web/dist via npm run preview). Then read only the files
listed in that brief.

Review against the questions in the brief. Return P1/P2/P3 findings with exact
locations (UI copy or file:line) and a PASS / PASS-WITH-LIMITS / FAIL verdict.

Prioritize:
1. unsupported or overstated market claims
2. broken attribution, dates, excerpts, or metric definitions
3. disagreement with the accepted Episode 002 call
4. hidden NO-CALL or invented ARR / private-company financials
5. first-screen overwhelm vs the two-minute read
6. freshness mistakes (old data presented as current; closes vs intent)

Do not implement. Do not propose a live feed, database, or collector.
Do not review deploy/Vercel. Do not rewrite the lag thesis.
```

## What this product is

A static, evidence-linked briefing site. A security leader or account person should understand the current cybersecurity market position in under two minutes and inspect sources when they want.

Accepted call (do not relitigate unless the site contradicts it):

> Infrastructure is accelerating. A stable infrastructure-to-security lag is **NO-CALL**. Use infrastructure activation as an account qualifier, not proof of a security boom.

The site is a **frozen edition**, not a live feed.

## What to open

| Order | What | Why |
|---|---|---|
| 1 | This brief | Scope, questions, freshness rules |
| 2 | Local site at `http://localhost:5173/` (hard-refresh) | The actual user experience |
| 3 | [web-mvp-product-contract.md](web-mvp-product-contract.md) | Accepted MVP outcome and evidence UX |
| 4 | [market-signal-episode-002-brief.md](../episodes/002/market-signal-episode-002-brief.md) | Accepted call and postures |
| 5 | Files below | Only if the site and contract disagree |

### Run locally

From the repo root, in the OrbStack `dev` VM (do not install packages on the host Mac):

```bash
orb run -m dev npm run dev --prefix web -- --host 0.0.0.0 --port 5173 --force
```

Production check:

```bash
orb run -m dev npm run build --prefix web
orb run -m dev npm run preview --prefix web
```

If 5173 looks stale, curl `http://127.0.0.1:5173/src/App.tsx` and confirm it imports `ActivityBoard` and wraps How this is built in `<details id="method">`.

## Current surface (review this, not the inbox prototypes)

Visible without opening a disclosure:

1. **Call** — masthead + three context numbers (`+92%` / `+4%` / `NO-CALL`)
2. **This period** — current public prints by domain (Network, SecOps, Data, Identity, Platform, Infrastructure)
3. **Tempo** — RUN / PREPARE / WATCH table
4. **M&A and startups** — one read + five headlines; click a row for note and sources

Collapsed by default:

- Market layers
- Watch next
- How this is built
- Research & evidence

Evidence excerpts open in a drawer from any Sources control. They must not be required to understand the call.

## Freshness model (review against this)

| State | Meaning | Surface |
|---|---|---|
| **Current** | Latest comparable print, or an open event (intent not closed) | Cards / lead headlines |
| **Background** | Still in the argument, not this period’s news | Collapsed Background |
| **Superseded** | Replaced by a newer print of the same series | Evidence only |
| **Frozen entity** | Vendor absorbed (Wiz, CyberArk) | Last independent print stays labeled; do not fold into the acquirer |

Announce and close are different jobs. Wiz announce (Mar 2025) is background evidence. Wiz close (Mar 2026) is a current capital headline.

Refresh is **manual** until collection is authorized:

- prints after the next IR / 10-Q, or a monthly reprint in heavy months (Feb / May / Aug / Nov);
- M&A and funding when a close, intent, or named raise happens, reviewed monthly;
- buyer budgets when the source publishes;
- the call only when a Watch-next item would change it.

Do not treat weekly news as a refresh trigger.

## Capital-activity rules

- Raises and deal values are **not** ARR or buyer spend.
- Do not invent private-company financials.
- Cisco / Astrix terms are **undisclosed** on Cisco’s own post. Do not promote secondary price rumors.
- Zscaler / Symmetry is **intent**, not close.
- Lead headlines (must be visible): Google/Wiz, Palo Alto/CyberArk, Cyera, Onyx, Cisco/Astrix.
- More in this window: Portkey close, Symmetry intent.
- Background: Lumos 2024 raise, Secuvy 2023 seed.

## Files in scope

Read these if you need to check a claim:

- `web/src/App.tsx` — page structure
- `web/src/data/market.ts` — call and context numbers
- `web/src/data/prints.ts` — scorecard cards
- `web/src/data/domains.ts` — tempo
- `web/src/data/activity.ts` — M&A / funding headlines
- `web/src/data/evidence.ts` — D13–D18 and linked prints
- `web/src/data/method.ts` — signal-family rules
- `web/src/components/ActivityBoard.tsx` — headline / expand behavior
- `web/src/components/HowThisWorks.tsx` — edition and aging copy

Do not treat as implementation authority:

- `docs/inbox/`
- `docs/archive/`
- historical workflow/build specs

## Review questions

Answer each. Cite the page or file.

1. Can a new reader state the call and the NO-CALL in two minutes without opening Method or Research?
2. Does any visible number or headline overclaim (boom, lag timetable, invented ARR, close vs intent)?
3. Does every material claim on the first screen have a working Sources control that shows excerpt, date, period, and limitations?
4. Is old data handled correctly (background collapsed, superseded off the cards, acquired vendors not rewritten)?
5. Is Activity headline-first, or does it dump a card wall?
6. Are Method, Watch, Layers, and Research collapsed, and do they still work when opened?
7. Does the site contradict the accepted Episode 002 brief?
8. Anything on the surface a security leader would bounce off (jargon, coverage labels, process docs)?

`INSUFFICIENT COVERAGE` must not appear on the default surface. `NO-CALL` must remain visible.

## Out of scope

- Deploy / Vercel / DNS / CI (parallel session)
- Gate S1 shadow implementation
- Collectors, schedulers, databases, auth
- Account conversation prompts (parked)
- Changing `intent.md`
- Reopening the lag as a number of quarters

## Verdict format

```
Verdict: PASS | PASS-WITH-LIMITS | FAIL

P1
- [location] finding — why it matters — suggested fix (words only)

P2
- ...

P3
- ...

Question answers
1. ...
```

P1 = ships a false or overstated market claim, or breaks attribution.
P2 = first-screen usability or freshness error that would mislead a careful reader.
P3 = polish.

## Owner note for other-model sessions

GPT, Claude, and Gemini remain gated by project model-routing except where the owner explicitly authorizes a review pass. This brief is that authorization for **read-only review only**.
