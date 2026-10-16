---
project: Security Market Pulse
stage: Operate
updated: 2026-10-16
---

# Status

Current state only. The full session log up to 2026-10-16 is in
[docs/archive/2026-10-auto-002/status-history.md](docs/archive/2026-10-auto-002/status-history.md).

## Now

- **Live:** https://securitymarketpulse.com serves the certified tracker (AUTO-002 Phase 2, D-101).
  The last certified change was 2026-10-16 10:12 UTC; all 80 claims passed, no drift.
- **Automation:** `certified-refresh.yml` runs every 4 hours and `promote-certified.yml` daily at 15:23
  UTC. The first scheduled refresh ran at 16:38 UTC on 2026-10-16: 80/80, no change, so nothing was
  published. GitHub starts scheduled runs late and sometimes skips slots; the freshness probe alarms
  only after 10 hours with no run.
- **Branches:** `preview` carries the cleanup and is ahead of `main` (`399cc78`) until the owner
  promotes. 28 merged or abandoned branches remain on GitHub (`auto/*`, `mon/*`, `issue/*`,
  `chore/cleanup` and others); agents in this setup cannot delete remote branches, so the owner
  deletes them in GitHub, Branches.

## Last session (2026-10-16)

- Shipped AUTO-002 Phase 2 to production after an independent review; five label and check defects
  fixed before promotion.
- Repo cleanup (D-102): retired docs archived by era with an index; retired code removed (frozen
  August snapshot, weekly-issue signing, laptop collector, 17 unreachable components, the unused
  `recharts` dependency); core documents rewritten; `intent.md` to v1.5 and the constraints updated
  with the owner's approval. One visible change: the RSS line on the front page read "Follow
  published records by RSS: follow by RSS" and now reads "Follow new records by RSS". Everything
  else renders pixel-identical to production on all five routes at 1440 and 390.
- Two fresh review agents checked the result; their findings were fixed before handover.

## Waiting on the owner

1. **Approve the cleanup.** It is on `preview` and the visual review is done: the only visible change
   is the RSS line. The owner says whether to promote. While non-data commits sit on
   `preview` ahead of `main`, automatic promotion of certified data waits.
2. **Confirm `intent.md` v1.5** text (the revision was authorized; the wording is for review).
3. **Email workstream inputs** (SEC-060): Buttondown API key as a GitHub secret, a postal address.
4. **Account items** (SEC-061): Cloudflare DMARC Management for jessepike.dev, DNSSEC and CAA for
   both domains, Vercel plan check.
5. **Delete stale branches** on GitHub (all but `main` and `preview`).

## Next for an agent

1. After promotion, confirm production renders the same as the preview and `app-release.json` is
   current.
2. SEC-062: watch the first real data change go through end to end.
3. SEC-060 as soon as the owner's inputs exist.

## Health checks

| Check | How |
|---|---|
| Site up and certified | `curl -s https://securitymarketpulse.com/app-release.json` shows `releaseKind: certified` |
| Refresh running | Actions tab: `certified refresh` ran within the last 10 hours |
| Nothing held | No open GitHub issue titled "Certified refresh held" |
| Tests | `cd web && npm test` |
| Push guard installed | `test -x .git/hooks/pre-push` (install with `./.githooks/install`) |
