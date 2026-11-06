# Backlog

Open work only, in priority order. Completed and retired items, SEC-002 to SEC-059, are in
[docs/archive/2026-10-auto-002/backlog-history.md](docs/archive/2026-10-auto-002/backlog-history.md).
Nothing here is authorized just by being listed; the authorization line on each item says where it
stands. New items continue from SEC-082.

## Next

### SEC-072 · Make the current site consistently accurate, fresh and durable

The current priority (D-110 to D-112). The daily pipeline publishes on its own; this item is about
making what it publishes accurate and fresh every day without a person.

As of November 2: intake 262 of 557 source checks (295 gaps: 254 missing bindings, 23 candidates,
16 transport, 2 schema). Processing 83 of 11,671 reviewed; the backlog cut (D-130) shrinks that
denominator once real runs record it. All 80 SEC claims pass and all public files match.

Open:
- Close the 254 missing source bindings and 23 unverified candidates (SEC-071).
- Measure precision after the review step, not only extraction (SEC-077).
- Measure actual Actions minutes and cost against the $5 budget (SEC-078) and the full-day Vercel cost.
- Keep the 557 obligations, original dates, holds and queues intact; no transient failure becomes a pass.

Dated checkpoints up to November 3 are in
[docs/archive/2026-11-backlog-checkpoints.md](docs/archive/2026-11-backlog-checkpoints.md).
**Authorization:** D-110 through D-112 and the owner's continuing reliability instruction.

### SEC-081 · Public company request box

Built 2026-11-06 (D-136). A "Want a company tracked?" link under the company search opens a one-field
box. The name goes to `ops/timer/api/request.js`, which adds it to one private GitHub issue
("Company requests from the site", label `company-request`) with a count. Only a new name comments
and notifies; at most 10 new names a day. Honeypot, a minimum fill time, an origin check and a
name filter (no links) block spam. The token is issues-only. Nothing publishes from a request.
Goes live when `main` advances (the timer project deploys from `main`; the site CSP allows the
timer host). Open: confirm the first real request lands in the issue.
**Authorization:** owner request 2026-11-06; credential choice confirmed by the owner (D-137).

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

Prove the actual chain runs clean for a sustained period with no human fixes: the Vercel Cron
timer and watchdog (D-127), `subscription-collector.yml`, `subscription-publisher.yml`, the
independent `market-release-gate.yml`, rollback acceptance and `freshness.yml`. Count clean days
from the first real timer start (05:17 UTC, November 4). Track late starts, manual fixes, alerts
and certified filing delivery within 48 hours. The owner has not set the acceptance duration;
recommendation: 30 days. History: [checkpoints](docs/archive/2026-11-backlog-checkpoints.md).
**Authorization:** D-104 through D-110, D-127.

### SEC-071 · Complete and disclose full-roster source coverage

Bounded daily collection for all 74 suppliers is authorized and running. Resolve source
registration, blocks (HTTP 403/429/504), dated evidence and typed ownership and financial adapters
within existing budgets, so intake moves from 262 toward 557. Keep task and field ages visible and
leave unsupported facts held. No supplier expansion is authorized by this work.
**Authorization:** D-104 through D-110. A successful run is not full coverage.

## Soon

### SEC-080 · Roll company-reported quarters for non-XBRL public suppliers

Check Point (a foreign private issuer filing 6-K/20-F) and Trend Micro (not an SEC filer) have no
automated path to a new quarter. Certified suppliers roll when their 10-Q's XBRL facts appear; the
document pipeline deliberately writes only private suppliers' headline metric
(`web/scripts/pipeline/snapshot.py`, the `kind not in ("public", "segment")` guard), so these two
stay on the quarter in `originals.json`. Example: Check Point reported Q3 2026 (quarter ended
2026-09-30, $670 million, down 1 percent) on 2026-11-02; the site still shows the quarter ended
2026-06-30. Build a reviewed path that admits period, period end, revenue and reported growth from
the company's own release or 6-K, keeps the "not re-checked automatically" label, and never
overwrites certified SEC fields. Test with Check Point Q3 2026 and Trend Micro Q3.
**Authorization:** found 2026-11-04 answering the owner's question about the 2026-06-30 date.
Changes what the pipeline may publish, so it needs the owner's go-ahead before build.

### SEC-076 · Optiv source-link correction

Re-point Optiv's 2026-05-08 closing record from the March 16 announcement to the May 8 closing
release, as a dated correction. Needs the closing URL registered as a citation source in the locked
contract and a real run to admit it. Do it with the next accepted contract change.
**Authorization:** owner-approved (D-132).

### SEC-077 · Score the review step in the extraction eval

The first eval (`ops/evaluation/extraction_eval.py`, 30 cases) scored extraction only: recall 95.8%,
precision 45.1%, date accuracy 66.7%. Most false positives are background facts the production review
step may reject. Add the review step so the score matches what can publish, then improve date
accuracy. [Report](docs/active/daily-pipeline/evaluations/2026-11-03/extraction-eval.md).
**Authorization:** within the automated checks D-76 relies on.

### SEC-078 · Watch GitHub Actions spend against the $5 budget

Measure actual monthly minutes per workflow (forecast about 59 Linux minutes a day for this site)
against the $5/month budget shared with the owner's other sites (D-129). Alert before the budget
stops workflows, as happened October 28 to 31. **Authorization:** D-129.

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

## Later (implementation authority noted per item)

### SEC-075 · Capped API-key fallback when the ChatGPT login fails

Deferred by the owner on 2026-11-03 (D-128). The subscription login stays primary because it is the low-cost route.

**Problem.** The AI step runs the Codex CLI on a GitHub runner, using the owner's ChatGPT login file stored as the secret `SMP_CODEX_AUTH_JSON`. Refreshed logins are written back by `ops/ci/auth_store.py`. If the login expires or is revoked, model work stops until the owner signs in again. That could take days. OpenAI's docs recommend API keys for CI ([Codex authentication](https://learn.chatgpt.com/docs/auth)).

**Design.**
1. Detection. `web/scripts/pipeline/agents.py` already recognises a dead login ("Please sign in again", refresh-token errors, 401). On that error, and only that error, switch the rest of the run to the fallback. Rate limits keep today's rule: hold and notify.
2. Key. A separate OpenAI API project and key, stored as a new GitHub secret. Codex uses it through API-key authentication.
3. Pinned model. Pass an explicit `--model` for fallback calls only. The subscription path keeps its default.
4. Caps. $5 a day and $30 a month, enforced in the collector's existing budget escrow (`maxAdditionalMonthlyUsd`). The OpenAI project budget is a second limit. When a cap is reached, model work stops and the run reports the gap.
5. Eval gate. Before activation, the fallback model must pass the extraction accuracy eval (golden set) at the subscription model's level. Facts extracted by the fallback carry `apiFallback: true` in their receipts.
6. Alert. The first fallback call opens a GitHub issue, "Model login expired: API fallback in use". It names the day's spend and how to refresh the login (`ops/ci/bootstrap.py`). The issue closes when a run succeeds on the subscription again.
7. Contract change. In `contracts/market.json`, set `apiFallback: true`, set `maxAdditionalMonthlyUsd: 30`, and add a model field for the fallback. This changes the contract hash, so it goes through the normal reviewed release.

**Cost estimate.** Estimated at about 80 calls a day, each with up to 30,000 characters of input (about 0.8M input tokens), and an assumed 0.3M output tokens. Prices are [OpenAI list prices](https://developers.openai.com/api/docs/pricing) read on 2026-11-03.

| Model | Estimated cost per fallback day |
| --- | --- |
| gpt-6.1-terra | about $2 |
| gpt-5.3-codex | about $6 |
| gpt-6-astra | about $24 |

One measured test day replaces the output-token assumption.

**Authorization.** Not authorized. Building it needs a new owner decision that names OpenAI API billing as a new paid vendor and the API key as a new credential (D-83).


### SEC-073 · Search the sourced market records

Company name, ticker and alias search shipped to production in November 2026 as an always-visible
field in the header (D-124, D-125). [Spec and checks](docs/active/company-search-2026-11-02.md).

Broader event/evidence search remains open. Find companies by
name, ticker or alias, and search their market events and supporting sourced records. Let readers combine
search with company-type navigation (SEC-074), open the matching company/event and its evidence,
and see the source date and freshness status. Define representative search cases, useful empty
results and clear/reset behavior when this work is picked up. Do not use search to mask missing
or stale underlying facts.
The current front-page name/ticker filter is a limited starting point; this item adds search across
the underlying market records and their evidence.
**Authorization:** owner requested the backlog item October23 and explicitly requested company
search implementation November2. Ownership/funding navigation stays separate SEC-074; broader
record search is unfinished. No supplier expansion or completeness claim follows from search.

### SEC-074 · Navigate companies by ownership, funding and stage

Let readers browse public companies, privately held companies, private-equity-backed companies,
startups and venture-funded companies, with room for other useful groupings such as bootstrapped
companies or subsidiaries. Connect these views to search (SEC-073), company records and sourced
events; expose named investors/owners and their portfolio relationships where evidence supports
them.

Ownership, funding and company stage overlap: a venture-funded startup can also be privately held.
Keep these as separate attributes rather than forcing each company into one exclusive category.
Show dated supporting sources and an explicit unknown/unclassified state when evidence is missing.
Define classification rules and test representative overlaps and ownership changes before build.
Keep the current supplier roster unchanged unless expansion is separately approved.
**Authorization:** owner requested this navigation capability as a backlog item on October 23:
"public companies, private equity, startups, venture funded, etc." Queue after current reliability
work and coverage expansion; implementation has not started.

### SEC-067 · Quarterly signed note per domain

One short, dated, signed note per domain each quarter, marked "awaiting review" when a certified fact
under it changes. The owner writes it. From the old SEC-059 (D-94).

### SEC-068 · Wider certified coverage

Bring private companies and segment-reporting suppliers into a certified tier using AI extraction
with a verification gate. Deferred by the owner (D-95).

### SEC-069 · Coverage statement and buyer brief

`/coverage/` (D-131) now lists every supplier and its tier. Still open: a declared list of how suppliers are chosen, and an owner-written note on what a development means
for a buyer. Both are judgment and the owner's wording. From the old SEC-046 and SEC-048.

Also parked by the owner and kept only in the history file: publishing under Pike Holdings (old
SEC-056), monetization (old SEC-042), distress signals beyond SEC filings (old SEC-047).
