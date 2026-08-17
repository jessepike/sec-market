# Handoff — Pulse local / GitHub / Vercel

**Date:** 2026-08-16  
**Status:** Sync authorized and executed. Standing deploy rule is D-31.

## Standing rule

The only production path is **local → GitHub → Vercel**.

1. Preview on OrbStack: `orb run -m dev npm run dev --prefix web -- --host 0.0.0.0 --port 5173 --force`
2. Commit a clean tree on `main` as `jesse@keatingpike.com` (not `jesse@pikeholdings.co`).
3. `git push origin main`.
4. Vercel builds that GitHub commit (`pikeholdings/security-market-pulse`, root `web`). If the deploy is BLOCKED with `COMMIT_AUTHOR_REQUIRED`, the commit email is wrong.
5. Curl https://securitymarketpulse.com before calling it shipped.

Never CLI-upload a dirty working tree. That is how the three copies drifted the first time.

## What this session shipped

- First screen is the scorecard: Hero (call + three numbers + Sources) → print cards → Tempo → Activity headlines → collapsed Layers / Watch / Method / Research.
- Judgment memo (`JudgmentBoard.tsx`) stays off the first screen.
- Prints are cards, not the comparison table. Identity no-series names stay cards.
- Activity: M&A + funding headlines; expand for notes/sources.
- Evidence drawer has no `github.com/jessepike/sec-market` artifact links.
- Network / SASE tag is PREPARE, not RUN.
- C6 split into C6a (Check Point) and C6b (Cisco). LAG-NO-CALL is OWN_ANALYSIS.
- Date display August 16, 2026. Content max 1000px.

## Do not commit

- `web/scripts/shot-*.png` (gitignored)
- `docs/inbox/sec-market-opus/`

## Next product work

- Recurring signals / first collection week (see `status.md`).
- Judgment layer: keep off the first screen; optional collapsed “The read”.
- Archive / back issues: CPO call, not started.
- Do not invent ARR. Do not push weekly news as a refresh.
