---
project: Security Market Pulse
stage: Operate
updated: 2026-10-16
---

# Status

Current state only. The full session log up to 2026-10-16 is in
[docs/archive/2026-10-auto-002/status-history.md](docs/archive/2026-10-auto-002/status-history.md).

## Now

- **Live:** https://securitymarketpulse.com serves the certified tracker. Production is at `9b63a07`:
  the cleanup (D-102) plus the first automatic data change (a SentinelOne 8-K filed 2026-10-16,
  published to `preview` by the bot at 22:52 UTC on 2026-10-16 and promoted with the cleanup).
- **Known defect on production:** that SentinelOne debt event quotes the filing's reference line
  ("Current Report on Form 8-K is incorporated herein by reference.") instead of its description. The
  fix (`06664cf`) is on `preview` and waits for the owner's promotion.
- **Automation:** `certified-refresh.yml` every 4 hours, `promote-certified.yml` daily at 15:23 UTC.
  The full automatic path has now run once: the refresh found a new filing, certified 80/80 and
  pushed to `preview`. GitHub starts scheduled runs late and sometimes skips slots.
- **Branches:** only `main`, `preview` and `archive/history-before-2026-10-14` remain. 28 stale
  branches were deleted on 2026-10-17 at the owner's request. The trunk was restarted on 2026-10-14,
  so the earlier commit history lived only in those branches; the archive branch joins their tips so
  every earlier commit is kept. Two unpublished weekly-issue pull requests (#2, #3) were closed.

## Waiting on the owner

1. **Promote the debt-quote fix** (`preview`, one visible change: the SentinelOne event text).
2. **Confirm `intent.md` v1.5** text (the revision was authorized; the wording is for review).
3. **Email workstream inputs** (SEC-060): Buttondown API key as a GitHub secret, a postal address.
4. **Account items** (SEC-061): Cloudflare DMARC Management for jessepike.dev, DNSSEC and CAA for
   both domains, Vercel plan check.

## Next for an agent

1. After the fix is promoted, confirm the SentinelOne event on production quotes the description.
2. SEC-062: confirm `promote-certified.yml` promotes a data-only change on its own (the first data
   change went out with an owner promotion instead).
3. SEC-060 as soon as the owner's inputs exist.

## Health checks

| Check | How |
|---|---|
| Site up and certified | `curl -s https://securitymarketpulse.com/app-release.json` shows `releaseKind: certified` |
| Refresh running | Actions tab: `certified refresh` ran within the last 10 hours |
| Nothing held | No open GitHub issue titled "Certified refresh held" |
| Tests | `cd web && npm test` |
| Push guard installed | `test -x .git/hooks/pre-push` (install with `./.githooks/install`) |
