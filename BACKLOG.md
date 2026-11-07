# Backlog

Open work only, in priority order. Completed and retired items, SEC-002 to SEC-059, are in
[docs/archive/2026-10-auto-002/backlog-history.md](docs/archive/2026-10-auto-002/backlog-history.md).
Nothing here is authorized just by being listed; the authorization line on each item says where it
stands. New items continue from SEC-090.

## Next

### SEC-081 · P1: cost and resource review on November 9

Look back on the first days of automatic operation and check costs before coverage grows.
1. Automation health: run success rate, missed or late runs, watchdog alerts, repairs needed.
2. Actual cost against expectations: GitHub Actions minutes and spend against the $5/month budget
   shared with securitythreatpulse.com (SEC-078), Vercel usage including the Cron timer, and
   ChatGPT subscription limits for the AI step.
3. Extra resources for the 11 companies in the coverage expansion, per company and in total,
   including collector timeout headroom.

Measured data only; flag anything unverified with the check that would settle it. Baseline:
[docs/active/cost-review/baseline-2026-11-05.md](docs/active/cost-review/baseline-2026-11-05.md).
**Authorization:** requested by the owner 2026-11-06; read-only review.

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

### SEC-084 · Weekly funding-rounds feed: follow-ups

Built 2026-11-06 (D-140). Open: measure the confirmation rate and minutes per run over four weeks
(first run: 13 of 23 rounds confirmed, 32 fetches, about 1.5 runner minutes); Forgepoint's paginated
list read 24 companies against 76+ in August, so check its page links; let the weekly data reach
production without waiting for a code promotion; add the rounds to the agent files (D-139); the
"Lead investor" column also takes a grant body ("from X"); data commits by the weekly job skip web CI
(GITHUB_TOKEN pushes do not trigger workflows).
**Authorization:** owner-approved (D-140).

### SEC-086 · Carry the Cyber resilience domain into the contract

D-144 moved Rubrik, Commvault, Cohesity and Veeam to a new `resilience` domain at display time
(`displayDomainIds`). At the next contract transition, set their `domainIds` in `contracts/market.json`
and the supplier originals, then delete `domainReassignments`. The evaluation scorecard groups by the
contract's domainIds until then.
**Authorization:** owner-approved (D-144).

### SEC-083 · Additive roster transition for onboarding suppliers

Build one reusable contract transition that only adds suppliers and their sources, proved by
inversion to the current contract (`47b9f226…`), and restamp the Q4 authority and the correction
policy stamp. First use: the eight D-138 suppliers, Check Point's SEC sources (SEC-080) and the Optiv
source link (SEC-076). Then a graduation check moves a supplier from `onboarding.json` into the
tracker after three clean daily runs. Waits for daily collection to fit under its timeout with
headroom. Plan: [coverage-expansion-2026-11-06.md](docs/active/coverage-expansion-2026-11-06.md).
**Status (2026-11-07, D-141):** on main. The first collection under it (run 42369492488, 2026-11-07)
passed and published; no fact for the eight reached a page. Every new source was attempted. Working:
the Optiv closing citation, five onboarding citations, and the F5, Akamai and Check Point
`sec_documents` sources. Not yet working, listed in `ops/watchdog/known-gaps.json`: the eight
`official:1` sources (binding unverified, like the existing 23), the Lumos, Secuvy and Skyflow
Business Wire citations (HTTP 403), and `sec_facts`/`sec_submissions` for F5, Akamai and Check Point
(`sec-adapter.mjs` only accepts suppliers in `edgarRegistry.ts`). Adding F5 and Akamai to the
registry also changes what the gate's `refresh:edgar` writes to `generated/edgarFacts.json`, so it needs
a render check and Akamai needs a labeling decision (total company revenue, not a security figure).
Check Point's `sec_facts` cannot pass, because it is a 20-F filer; SEC-080 owns its route. At the next transition, drop
`checkpoint-sase:sec_facts` and `:sec_submissions` and keep `:sec_documents` (agreed with the SEC-080 thread). F5 and
Akamai join `edgarRegistry.ts` when they graduate into the tracker, not before: `verify-tracker` cross-checks the
registry against tracker public suppliers, and `sec-adapter.mjs` stays unchanged. **2026-11-07 later:** 19 workaround sources added as additions to the same transition: verified
newsroom sitemaps for F5, Aikido, 7AI, Straiker, Lumos, Skyflow and Secuvy (`<id>:official:2`), second
copies of the three blocked onboarding citations, and alternate copies on reachable hosts for nine
blocked or rate-limited tracker citations (BeyondTrust, BigID, Cohesity, Delinea x2, Tines, Axonius x3;
`-alt` ids, original sources kept). Akamai's newsroom and the Sophos rating actions still have no
reachable copy. Left: binding verification for the eight official sources, the Optiv correction request
group, and the graduation check.
**2026-11-07 (D-146):** the transition now also adds Checkmarx, Black Duck, Semgrep, Endor Labs and Noma
(87 suppliers, 337 sources) and drops `checkpoint-sase:sec_facts` and `:sec_submissions`. Their
`official:1` sources start as unverified bindings like the other onboarding ones.
**Authorization:** owner-approved (D-138, D-146).

### SEC-080 · Roll company-reported quarters for non-XBRL public suppliers

**Check Point: built 2026-11-06, on preview.** `web/scripts/release-refresh.ts` (run at the end of
`refresh:edgar`) reads Check Point's 6-K results releases from its EDGAR submissions index and takes
the income statement's "Total revenues" row with a fixed parser (`web/src/data/sixKLogic.ts`, no
model). It refuses any other shape and keeps the last good record. Figures go to
`generated/companyReleases.json`, stay outside the certified cohort and keep the "not re-checked
automatically" label. The committed baseline, parsed from five saved 6-Ks
(`web/tests/fixtures/sec-6k`), shows the quarter ended 2026-09-30 ($669.8 million, -1.1%). In the
release gate it only sees SEC responses the collector archived, so new quarters roll automatically
once SEC-083 adds `checkpoint-sase:sec_*` sources; until then the baseline holds.

Trend Micro is not an SEC filer and still has no automated path; it needs a TSE/newsroom source.
**Authorization:** owner said yes 2026-11-04.

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

### SEC-085 · Sharpen the tagline and event labels for a CISO reader

Future, low priority. The owner wants to revisit the "who grew, who raised, who bought, who cut"
line and the event tile labels (reported revenue, funding, acquisitions, restructuring) and
"clean that up a little bit or sharpen it", angled toward a CISO or security leader. The owner is
happy with the current preview direction and does not want to focus on this now (2026-11-06).
**Authorization:** not authorized. Page wording is a major change and needs the owner's wording
and review of a preview.

### SEC-087 · Watch list: a leader tracks their own partners and vendors

Future, low priority. Owner's reasoning (2026-11-06): "If I'm a CISO, I'm going to want to track my
partners." In a fast-moving, volatile space a security or business leader doing business with
these companies wants to keep an eye on them. Someone logs in and sees the partners and companies
they follow. Focus on value first; the owner is "not interested in the monetization just yet" and
will discuss charging only once there is enough value. Overlaps the digest work in SEC-060.
**Authorization:** not authorized. Logins and per-user lists need stored user data, which the
constraints do not allow today (no database), plus a new owner decision.

### SEC-088 · Map coverage to the owner's own partner companies

Future, low priority. Show which covered suppliers are the owner's partner companies, as a first,
private use of the SEC-087 watch list. From the 2026-11-06 product brainstorm ("mapping to Jess's
partner companies later"). **Authorization:** not authorized. The partner list is the owner's to
supply; nothing about it appears on the public site without approval.

### SEC-089 · Explore a third-party risk assessment angle

Future, low priority, exploration only. The owner asked whether the watch list "could evolve into
some type of third-party risk assessment kind of component" and sees value in scenarios like that
(2026-11-06). Any such view must show sourced facts only: a machine-written risk rating is a
judgment and is not authorized (D-76). **Authorization:** not authorized. Explore and report back
before any design.

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
