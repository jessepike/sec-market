# Backlog

Open work only, in priority order. Completed and retired items, SEC-002 to SEC-059, are in
[docs/archive/2026-10-auto-002/backlog-history.md](docs/archive/2026-10-auto-002/backlog-history.md).
Nothing here is authorized just by being listed; the authorization line on each item says where it
stands. New items continue from SEC-072.

## Next

### SEC-060 · Email workstream

Signup on this site and jessepike.dev, double opt-in, a digest of certified changes only, privacy
page, postal address, sender authentication. Ships as one unit. Spec:
[docs/active/email-workstream.md](docs/active/email-workstream.md).

**Authorization:** approved (D-92). **Blocked on the owner:** Buttondown API key as a GitHub secret,
a postal address for the footer.

### SEC-061 · Owner account and DNS items

- Turn on Cloudflare DMARC Management for jessepike.dev so DMARC reports arrive.
- Turn on DNSSEC and add CAA records for both domains.
- Confirm the Vercel plan permits commercial use (Hobby does not).

Record list: [docs/reference/dns-and-accounts.md](docs/reference/dns-and-accounts.md).
**Authorization:** owner actions in the owner's accounts (D-99).

### SEC-062 · Burn-in: prove sustained automatic operation

The owner requires fresh, accurate operation without human fixes (2026-10-18). Prove the actual
GitHub Actions chain: `subscription-collector.yml`, `subscription-publisher.yml`, the independent
`market-release-gate.yml`, controlled rollback acceptance and `freshness.yml`. The former certified
refresh and automatic main-promotion workflows are disabled. A successful bounded collector may
retain explicit source gaps; those gaps do not become fresh checks. Track actual scheduled runs,
exact-artifact production acknowledgements, certified filing delivery within 48 hours, manual fixes
and execution alerts. Sustained operation is still unproved; no clean-day count is claimed.
The owner has not set the acceptance duration (previous recommendation: 30 days).
**Authorization:** D-104 through D-110; [current activation record](docs/active/daily-pipeline/activation-2026-10-23.md).

### SEC-071 · Complete and disclose full-roster source coverage

Bounded daily collection for all 74 existing suppliers is authorized and implemented. The latest
completed source run checked 244/557 tasks; full source coverage remains incomplete, with 254
missing family bindings and 28 held claims. Resolve source registration, blocks, dated evidence,
typed ownership/financial adapters and retained historical audits within existing budgets. Keep
task and field ages visible and leave unsupported or unchecked facts held. General partial coverage
can accompany individually verified facts; the complete SEC certification requirement remains.
No supplier expansion is authorized by this work.
**Authorization:** D-104 through D-110. A successful runner or release is not full coverage.

## Soon

### SEC-063 · Retire the frozen AUTO-001 data from the build

The page still reads `refreshCoverage.json` and `collectState.json` (through `runStatus.ts`), the
feed still writes the frozen `/refresh-*.json` receipts, and the build still runs content gates
written for the weekly-issue era (`verify:panel`, `verify:prints`, parts of `verify:integrity`) over
data that no longer changes. Simplify to what the certified tracker needs. This changes page text
and public URLs, so it needs a render review and the owner's approval. Folds in the old SEC-053
(structured event dates on evidence) and SEC-058 (the unreferenced-evidence gate sits at its limit).
**Authorization:** needs owner approval of the preview.

### SEC-064 · Accessibility check in the build

Add axe (WCAG 2.2 AA) and a tab-order check at 1440 and 390 to the Playwright suite so a regression
fails the build. From the old SEC-057. **Authorization:** within the automated checks D-76 relies on.

### SEC-065 · Second oracle for certified figures

The verifier re-derives claims with the same XBRL rules as the producer, so the site may only say
"re-derived from SEC filings" (D-100). A second, independent source (for example the SEC frames API)
would allow a stronger claim. **Authorization:** proposed; the wording change needs the owner.

### SEC-066 · Dated maintenance

- Renew `/.well-known/security.txt` on both sites before it expires on 2027-10-15, and add a
  freshness-probe alert 30 days ahead.
- Move workflows and Vercel from Node 22 to Node 24 before Node 22 reaches end of life (April 2027).

**Authorization:** routine maintenance.

### SEC-070 · Dead source links

`npm run check:links` reports 21 of 286 external source links answering with something other than
200 (some are sites that block automated requests, some have moved). Re-point moved sources to a
working copy or an archived snapshot; leave the cited text unchanged. **Authorization:** routine
maintenance; any change to what a record says goes through a correction.

## Later (owner ideas, not authorized)

### SEC-067 · Quarterly signed note per domain

One short, dated, signed note per domain each quarter, marked "awaiting review" when a certified fact
under it changes. The owner writes it. From the old SEC-059 (D-94).

### SEC-068 · Wider certified coverage

Bring private companies and segment-reporting suppliers into a certified tier using AI extraction
with a verification gate. Deferred by the owner (D-95).

### SEC-069 · Coverage statement and buyer brief

A declared list of how suppliers are chosen, and an owner-written note on what a development means
for a buyer. Both are judgment and the owner's wording. From the old SEC-046 and SEC-048.

Also parked by the owner and kept only in the history file: publishing under Pike Holdings (old
SEC-056), monetization (old SEC-042), distress signals beyond SEC filings (old SEC-047).
