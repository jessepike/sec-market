---
project: Security Market Pulse
stage: Operate
updated: 2026-10-16
---

# Status

Current state only. The full session log up to 2026-10-16 is in
[docs/archive/2026-10-auto-002/status-history.md](docs/archive/2026-10-auto-002/status-history.md).

## Now

- **Live:** https://securitymarketpulse.com at `d4ff8f6` (2026-10-18): the certified tracker, the
  cleanup (D-102), the first automatic data change (a SentinelOne 8-K filed 2026-10-16) and the
  debt-quote fix. The SentinelOne event now quotes the filing's description.
- **Automation:** `certified-refresh.yml` every 4 hours (runs late but regularly; last checked
  18:37 UTC 2026-10-18, 80/80). `promote-certified.yml` has failed every scheduled run: its check job
  fetched `origin/main` without credentials on a private repo. Fixed in `6a2128f` on `preview`;
  waits for the owner's promotion. Until then certified data reaches production only when the owner
  promotes.
- **Branches:** `main`, `preview` and `archive/history-before-2026-10-14` (earlier history, kept).
- **Traffic:** Vercel Web Analytics shows 38 visitors and 73 page views since launch, all with no
  referrer (direct visits).

## Waiting on the owner

1. **Promote the workflow fix** (`6a2128f`, no visible change).
2. **Confirm `intent.md` v1.5** text (the revision was authorized; the wording is for review).
3. **Email workstream inputs** (SEC-060): Buttondown API key as a GitHub secret, a postal address.
4. **Account items** (SEC-061): Cloudflare DMARC Management for jessepike.dev, DNSSEC and CAA for
   both domains, Vercel plan check.

## Next for an agent

1. After the fix is promoted, check the next `promote certified data` run ends green.
2. SEC-062: confirm a data-only change promotes on its own.
3. SEC-060 as soon as the owner's inputs exist.

## Health checks

| Check | How |
|---|---|
| Site up and certified | `curl -s https://securitymarketpulse.com/app-release.json` shows `releaseKind: certified` |
| Refresh running | Actions tab: `certified refresh` ran within the last 10 hours |
| Nothing held | No open GitHub issue titled "Certified refresh held" |
| Tests | `cd web && npm test` |
| Push guard installed | `test -x .git/hooks/pre-push` (install with `./.githooks/install`) |
