# Issue 2026-w38 draft

## Gate exit codes (failures first — none failed)

- `npm run verify:edition` — 0
- `npm run verify:panel` — 0
- `npm run verify:integrity` — 0 (5 pre-existing unreferenced-evidence warnings, unrelated to this change)
- `npm run verify:issue` — 0 (all 15 checks pass, including numeral-token check 12)
- `npm run test:data` — 0 (154 tests, 0 failures)

## Read

Eight AI-security funding rounds land, led by Exein's $270 million raise, as S&P Global agrees to acquire OpenZeppelin.

## Lane items

- **Formation (8):** AIUC $40M Series A (AI-risk underwriting) · Eve Security $7.5M extended seed (AI-agent runtime security) · Exein $270M at $1.7B valuation (physical-AI security) · StrikeReady Aramco-backed investment, $29M total (Composite AI SecOps) · MIND $72M Series B, $112M total (AI-era DLP) · Comp AI $34M Series A (agentic compliance) · QueryLift seed round (GEO brand protection, Japan) · TigerByte Cyber $3M seed, stealth exit (cyber hardening for AI/edge)
- **Absorption (1):** S&P Global agrees to acquire OpenZeppelin (smart-contract security standard-setter)
- **Prints (0):** none found this week
- **Capital (0):** none found this week

## Scorecard changes

None this week. No `prints.ts`-tracked issuer disclosed a new, in-window figure this week (EDGAR sweep across the SEC-filing issuers in `prints.ts` and `panelRaw.ts` found no in-window 8-K/10-Q results), so `web/src/data/prints.ts` was not touched and `npm run verify:prints` was not run — there is nothing in that file for it to check this week.

## Proposed posture deltas

None proposed. No prints or capital evidence entered this window to move any domain posture, and eight early-stage formation rounds are not by themselves grounds to move one.

## Sources that could not be read

- Hackuity's own funding announcement (a reported $19 million raise per the URL slug) — 3 failed fetches: two attempts at the BusinessWire release (`http://www.businesswire.com/news/home/20260916319331/en/Hackuity-Raises-%2419-Million-to-Help-Enterprises-Prepare-for-the-AI-Driven-Vulnerability-Explosion`, both Akamai 403 "Access Denied"), and one attempt at `https://www.hackuity.io/` (returned the site's generic Webflow 404 page, not the press release). Dropped — no primary document was readable to confirm the figure or date.

## What was left out and why

- **Yige Cloud** — fetched, but only a secondary-source mention was found; no primary company or investor release, so it was dropped rather than dated from an aggregator.
- **Dark Sky Technology, Spectra, CounterMeasure Security** — candidate formation items surfaced during the sweep but not pursued once the 8-item Formation lane cap was already reached by higher-confidence, fully-sourced items.
- **SecurityWeek feed** (`https://www.securityweek.com/feed/`) — fetched successfully, but its rolling window did not reach back into this issue's gather window (2026-09-14 to 2026-09-20); the one SecurityWeek-hosted item that made the cut (TigerByte Cyber) was found by fetching the article page directly, not via the feed.

## Going stale

```
# Going stale

As of 2026-09-21: 0 judged claim(s) older than 45 days, 19 scorecard print(s) whose period ended more than 150 days ago, 0 print(s) with a period not understood.

## Judged claims older than 45 days

None found.

## Scorecard periods more than 150 days old

- `print-secuvy` — Secuvy — last disclosed raise (Seed) — period ended 2023-12-31, 995 days ago
- `print-aqua` — Aqua Security — Series E extension ($1B+) — period ended 2024-01-31, 964 days ago
- `print-lumos` — Lumos — last disclosed raise ($35M) — period ended 2024-12-31, 629 days ago
- `print-tines` — Tines — private valuation ($1.125B) — period ended 2025-02-28, 570 days ago
- `print-sentra` — Sentra — Series B ($50M) — period ended 2025-04-30, 509 days ago
- `print-protect-ai` — Protect AI — inside Palo Alto ($634.5M) — period ended 2025-08-29, 388 days ago
- `print-lakera` — Lakera — Check Point deal (Undisclosed) — period ended 2025-09-30, 356 days ago
- `print-cato` — Cato Networks — 2025 ARR (+43%) — period ended 2025-12-31, 264 days ago
- `print-bigid` — BigID — company-stated revenue (>$100M) — period ended 2025-12-31, 264 days ago
- `print-securiti` — Securiti — acquired by Veeam ($1.725B) — period ended 2025-12-31, 264 days ago
- `print-upwind` — Upwind — private valuation ($1.5B) — period ended 2026-01-31, 233 days ago
- `print-torq` — Torq — private valuation ($1.2B) — period ended 2026-01-31, 233 days ago
- `print-witnessai` — WitnessAI — strategic round ($58M) — period ended 2026-01-31, 233 days ago
- `print-cyberark` — CyberArk — inside Palo Alto ($25B) — period ended 2026-02-23, 210 days ago
- `print-crwd-cloud` — CrowdStrike Falcon Cloud — cloud ending ARR (>35%) — period ended 2026-03-03, 202 days ago
- `print-netskope` — Netskope — ARR (annual) (+31%) — period ended 2026-03-11, 194 days ago
- `print-wiz` — Wiz — inside Google Cloud ($32B) — period ended 2026-03-11, 194 days ago
- `print-sailpoint` — SailPoint — ARR (annual) (+28%) — period ended 2026-03-18, 187 days ago
- `print-veza` — Veza — inside ServiceNow (Closed) — period ended 2026-03-31, 174 days ago
```

## Commands run

```
npm ci --prefix web
npm run verify:edition --prefix web
npm run verify:panel --prefix web
npm run verify:integrity --prefix web
npm run verify:issue --prefix web
npm run test:data --prefix web
npm run report:stale --prefix web
```
