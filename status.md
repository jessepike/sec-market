---
project: Security Market Pulse
stage: Operate
updated: 2026-10-16
---

# Status

Current state only. The full session log up to 2026-10-16 is in
[docs/archive/2026-10-auto-002/status-history.md](docs/archive/2026-10-auto-002/status-history.md).

## Now

- **Live:** https://securitymarketpulse.com at `54590be` (2026-10-18): the certified tracker, the
  first automatic data change (a SentinelOne 8-K filed 2026-10-16) and the debt-quote fix.
- **Owner's position (2026-10-18):** no outreach to readers until the site shows sustained, fresh and
  accurate operation with no human fixes. The bar for "sustained" is open (below).
- **Automation (D-103, on `preview`, not yet live):** `promote.yml` replaces `promote-certified.yml`.
  Every change that passes the checks goes live on its own; major changes wait for the owner. The
  freshness probe now watches promotion success, data lag and deploy lag; machine-written event text
  passes an accuracy gate. Until this is promoted, the old promotion workflow (now fixed) moves
  data-only changes, and `preview` holds non-data commits, so nothing moves on its own.
- **Branches:** `main`, `preview` and `archive/history-before-2026-10-14` (earlier history, kept).
- **Traffic:** 38 visitors since launch, all direct. Not a goal until the burn-in is passed.

## Waiting on the owner

1. **Promote D-103** once. It changes the promotion rules, which are a protected path, so it needs
   the owner by its own rules. After it, routine changes go live without the owner.
2. **Set the burn-in bar** (recommended: 30 consecutive days with every scheduled run green, every
   new filing live within 48 hours, and no manual data fix).
3. **Scope of the live site:** 58 of 74 suppliers have no automated refresh. Options: show only what
   refreshes (16 SEC filers), keep all with visible fact ages, or rebuild collection (D-95 deferred).
4. **Confirm `intent.md` v1.5** text.
5. **Email inputs** (SEC-060) and **account items** (SEC-061), when outreach is back on.

## Next for an agent

1. After D-103 is live, confirm the first `promote` run ends green and the probe stays clear.
2. Track the burn-in: count consecutive clean days from the Actions history.
3. SEC-063 (retire the frozen AUTO-001 data from the build) as routine work.

## Health checks

| Check | How |
|---|---|
| Site up and certified | `curl -s https://securitymarketpulse.com/app-release.json` shows `releaseKind: certified` |
| Refresh running | Actions tab: `certified refresh` ran within the last 10 hours |
| Promotion running | Actions tab: `promote` succeeded within the last 30 hours |
| No open alerts | No open issue titled "Site freshness", "Automatic promotion failed" or "Certified refresh held" |
| Tests | `cd web && npm test` |
| Push guard installed | `test -x .git/hooks/pre-push` (install with `./.githooks/install`) |
