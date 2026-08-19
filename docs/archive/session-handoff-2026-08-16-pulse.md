# Wrap — Pulse local / GitHub / Vercel sync

**Date:** 2026-08-16  
**Status:** Wrapped. Sync closed. This is not a continuation handoff.

## Outcome

Local `main`, GitHub `main`, and Vercel production are the same commit: `8b35e45`.  
Live: https://securitymarketpulse.com — `Security Market Pulse | Episode 002`, bundle `index-TqDCQide.js`.  
Vercel built it from GitHub (`source: git`), not a CLI upload.

## Standing rule (D-31 / D-32)

The only production path is **local → GitHub → Vercel**.

1. Preview on OrbStack: `orb run -m dev npm run dev --prefix web -- --host 0.0.0.0 --port 5173 --force`
2. Commit a clean tree on `main` as `jesse@keatingpike.com` (not `jesse@pikeholdings.co`).
3. `git push origin main`.
4. Confirm the Vercel deploy is **Ready** (not UNKNOWN / BLOCKED).
5. Curl https://securitymarketpulse.com before calling it shipped.

Never CLI-upload a dirty working tree.

## Lessons

- First public ship was a CLI upload of a dirty tree. That made live ≠ GitHub ≠ laptop. Do not do that again.
- A Vercel row appearing after `git push` is not a ship. `jesse@pikeholdings.co` deploys sit at `BLOCKED` / `COMMIT_AUTHOR_REQUIRED` because GitHub cannot map the committer. Inspect `readyState` and the git SHA.
- This repo’s `user.email` must stay `jesse@keatingpike.com`.
- Do not treat `origin/main` as live until that SHA is the Ready production deployment and the live host returns the new bundle.
- Comparison screenshots (`web/scripts/shot-*.png`) and `shot-compare.mjs` are disposable. Do not commit them.

## Product notes still true

- First screen is the scorecard. Judgment memo stays off the fold.
- Prints are cards. Network / SASE is PREPARE.
- Evidence drawer has no `github.com/jessepike/sec-market` artifact links.
- Do not invent ARR. Do not push weekly news as a refresh.

## Next session (product, not sync)

Recurring signals job. Owner critique of the startup section is the next owner gate. Do not reopen the three-copy deploy problem unless live, GitHub, and local SHA diverge.
