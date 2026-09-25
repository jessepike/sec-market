# Autonomy and coverage plan

**Artifact ID:** `SEC-MARKET-AUTO-001` v0.1
**Date:** 2026-09-25
**Governs from:** D-76 and `intent.md` v1.3 — sourced, machine-validated facts publish on their own
with automated checks as the only gate; the machine publishes no judgments.
**Status:** proposed, waiting on the owner's word to start.
**Evidence behind it:** three read-only audits run on 2026-09-25 (the update job end to end, every
scorecard figure checked against what companies have published since, and coverage against
`docs/active/product-core.md`). Their full reports were working files; the findings that matter are
restated here.

## 1. Where things stand

### The update job

The weekly gather is real. Every Tuesday a scheduled job on macbook2014 runs a headless Claude
session over a fixed source list, fetches each source, writes a draft issue plus evidence, runs the
checks, and pushes a branch. After that it stops working:

- macbook2014 has been off the network since 2026-09-21, so nothing has run since.
- The week-38 run did finish before the machine dropped. Its branch `issue/2026-w38` passed every
  check, but the step that opens the pull request failed on a GitHub setting ("GitHub Actions is not
  permitted to create or approve pull requests"). Nobody was told.
- Publishing then needed the owner to approve the pull request, which signed the issue under his
  name. Only one issue, `2026-w36`, has ever been signed. The week-37 draft has sat unsigned since
  2026-09-20.
- The job refreshes a scorecard figure only when a company's results land inside that week's
  seven-day window. A missed week is never caught up. The domain stances, Platform pressure lines
  and other judged text are on a do-not-touch list for the job, so they are maintained by hand only.

### The scorecard figures

"Period ended" means the date the figure describes, not when the site collected it. A 2023 seed
round was already two years old when the page was built. Of the 45 figures on the scorecard:

- **Eleven are simply out of date.** A newer public figure exists and the pipeline missed it:
  Zscaler, Okta, CrowdStrike, SentinelOne, Rubrik, Netskope, SailPoint, Cato Networks, Palo Alto's
  XSIAM and Prisma AIRS lines, and Upwind (a new round at $3.8B on 2026-09-04). Most of these
  companies reported between 2026-08-26 and 2026-09-09. Several of them appear with their new numbers
  in the site's own signed week-36 issue, while the front-page table still shows the quarter before.
- **Six are no longer meaningful**, because the company was acquired: Wiz, CyberArk, Protect AI,
  Veza, Securiti, Lakera.
- **Eight are old because the company has published nothing newer**, mostly private companies whose
  only public fact is a funding round (Secuvy 2023, Aqua 2024, Lumos 2024, Tines, Sentra, BigID,
  Torq, WitnessAI). This is a limit of the metric chosen, not of the job.

### Coverage

- Six domains exist and four are on the front page. Endpoint, managed security services and MDR,
  vulnerability and exposure management, application security, email security and OT security have
  no home. That is roughly half of a normal security budget.
- Nothing collects distress signals: debt, layoffs, shutdowns, ratings actions, going-concern
  warnings. The sourcing method was researched on 2026-09-20
  (`docs/active/fable-run/research/11-distress-signal-sources.md`) and never wired in.
- The weekly issue swings on whatever happened that week. Week 36 was earnings-heavy; the week-38
  draft is eight seed-to-Series-B AI security funding rounds and one acquisition, with no earnings
  at all. Early-stage rounds are close to the news feed the product core says the site is not.

## 2. Is the value right, and do the intent and the value line up?

**The value is right, and the site does not deliver it yet.** The value in the product core is
specific and uncommon: for each security domain, which suppliers are on solid footing, on current
public evidence, for someone who buys from them or advises someone who does. Analyst firms sell
this behind a paywall and trade press does not do it at all. That is worth building.

The site today falls short in three ways that have nothing to do with the approval question. The
figures are a quarter behind. The figures cannot be compared, because each supplier shows a
different metric over a different period and the table refuses to put them side by side. And half
the market a security leader buys from is missing, along with the whole distress side, which is the
part a buyer most needs to see early.

**Facts only is workable if the facts are chosen and arranged to answer the question.** The owner's
test case was a vendor asking for time with the account team when the market was not talking about
it. A facts-only site answers that if it shows, for that domain, every tracked supplier's latest
growth on the same metric, the quarter before, the gap to the domain's middle, the last funding
round and its date, any layoffs, debt or ratings actions, and whether the company has been bought.
The reader draws the conclusion. The machine never says "solid" or "fading". Computed differences
(this supplier grew 12% against a domain median of 24%) are facts, not judgments.

What facts-only gives up is the "what this means for you as a buyer" layer that the outside review
called the missing centre. That is now the owner's to write when he wants to, and the site should
be useful without it.

**The intent does not yet match the value.** `intent.md` v1.3 now has the right rule on autonomy,
but its purpose, beneficiaries and scope are still the August wording: help account teams and
clients time GTM decisions, with the infrastructure-to-security thesis as the founding question and
success measured by logged decisions. The product core's seven amendments (section 9) were never
applied. Four of them still matter:

1. Purpose: a credibility asset for the owner's advisory work and a working instrument for supplier
   and domain decisions.
2. Readers: security leaders first; advisors, sellers and vendor partner teams second; investors
   not a designed-for reader.
3. Scope: add distress and consolidation explicitly, the three-to-six-month look back, and "not a
   security news site".
4. Success: replace "logged decisions within two quarters" with the product core's signals, led by
   freshness (every scheduled update happened, the newest fact is days old). The owner has said the
   decision log is not the priority now.

Amendments 3 (the founding thesis) and 6 (revenue) from the product core are already true in
practice and need no wording beyond one line each. Recommendation: apply all four above as
`intent.md` v1.4.

## 3. What the site becomes

- **A standing tracker, updated whenever a fact changes,** instead of a weekly issue that must be
  signed. Each domain lists its declared suppliers with the same footing facts for each.
- **A weekly "what changed" log,** generated by the machine: new results, rounds, acquisitions,
  layoffs, debt and ratings actions, each with its source. Its heading is a count ("4 results, 3
  rounds, 1 acquisition, 1 layoff"), never an interpretation.
- **An honest run status on the page:** "updated today", "no material change this week within our
  coverage", or "collection incomplete: these sources failed". A failed run and a quiet week never
  look the same.
- **Judged text leaves the live pages.** The 16 Aug stances (Prepare, Investigate), the Platform
  pressure interpretive lines, the issue headlines and "why it matters" lines come off the front
  page. Signed issue `2026-w36` and the `/thesis/` page stay as a dated archive, unchanged.
  Corrections keep working as they do now.

## 4. Coverage model

Twelve domains, matching how a security budget is actually spent:

| Domain | Example suppliers to track |
|---|---|
| Endpoint and XDR | CrowdStrike, SentinelOne, Microsoft (where disclosed), Sophos |
| Security operations (SIEM, SOAR) | Splunk inside Cisco, Palo Alto XSIAM, Google SecOps, Exabeam, Torq, Tines |
| Managed security and MDR | Arctic Wolf, Expel, Optiv, Trustwave, eSentire, ReliaQuest |
| Network and SASE | Fortinet, Palo Alto, Zscaler, Cloudflare, Netskope, Cato, Check Point |
| Cloud security | CrowdStrike Cloud, Palo Alto Prisma, Wiz inside Google, Upwind, Orca, Aqua |
| Identity | Okta, SailPoint, CyberArk inside Palo Alto, Ping, Saviynt |
| Data security | Rubrik, Varonis, Cyera, BigID, Sentra |
| Vulnerability and exposure | Tenable, Qualys, Rapid7, Axonius |
| Application security | Snyk, Checkmarx, Semgrep, Chainguard |
| Email security | Proofpoint, Mimecast, Abnormal |
| OT and IoT security | Claroty, Dragos, Nozomi, Armis |
| AI security | Prisma AIRS, Zenity, WitnessAI, HiddenLayer, plus acquisitions |

The final list is declared on the site, with what is not covered. About sixty suppliers. Adding or
dropping one is a data edit, not a code change.

**Footing facts per supplier.** Public companies: latest reported growth on one named metric per
supplier (revenue growth by default, ARR where that is what the company reports), the prior
quarter, the report date, and the next expected report date. Private companies: last round, amount,
date, lead investor, and valuation where disclosed. Everyone: acquired or acquiring, layoffs,
restructuring charges, debt and ratings actions, going-concern language, leadership exits at chief
executive or finance chief level.

**Funding rounds below Series B or under $25 million** are counted in the weekly log but do not
appear as tracker rows unless the company is on the declared list. This keeps the site off the
startup-news treadmill.

## 5. How it runs

### Runtime

Move the job off a single laptop. Two runners, both on GitHub Actions, on the existing private repo:

- **Public-company figures, daily, no model involved.** SEC EDGAR publishes structured financial
  data for every filer. A plain script reads it, computes growth, and checks company, metric, period
  and units together. It needs no subscription and cannot hallucinate. Foreign filers such as Check
  Point and Cato's private disclosures fall back to the model runner.
- **Everything unstructured, daily or twice weekly, with Claude.** Press releases, funding and
  acquisition announcements, state layoff notices (WARN), ratings actions, trade reports used only
  as leads to a primary document. This runs headless Claude Code under the owner's subscription,
  using a long-lived login token stored as a repository secret. No API key.

macbook2014 stays as a fallback only.

### Publishing

- Each run writes data files only, on a short-lived branch, and runs every existing automated check
  plus two new ones: every link still resolves, and no duplicate of an existing fact.
- If every check passes and the change touches only the declared data files, the job merges to
  `preview` and fast-forwards `main`. Vercel publishes. Nobody is asked.
- If a check fails, nothing publishes, the page shows "collection incomplete", and the failure is
  written to the run log. The owner is not paged for ordinary failures; a weekly one-line digest
  (sent through GitHub's own notifications) says what ran and what failed.
- Changes to the site's code and layout still reach `main` only on the owner's word, as `AGENTS.md`
  requires. That happens rarely once the tracker is built. `AGENTS.md` is updated to describe the
  data-only exception when this is built.

### What gets removed

The approve-to-publish workflow, signing, the `reconfirm` word, the lock on "one signed issue per
week" as a precondition, and the do-not-touch list that kept the job from the tracker. The checks
that confirm a figure means what its label says (SEC-044) stay and become the main safeguard.

## 6. Order of work

Time estimates are build work done by agents (Layer A in the owner's timeline rule): expect days,
not weeks. Nothing here depends on outside parties except the owner's one login step.

| Step | What | Visible to readers | Needs the owner |
|---|---|---|---|
| 0 | Refresh the eleven out-of-date figures, mark the six acquired suppliers as acquired with the date, and publish | Yes: figures change | No, under D-76 |
| 1 | Take the judged text off the live pages; add the run-status line | Yes | His word to promote the layout change |
| 2 | EDGAR daily runner on GitHub Actions; backfill every public supplier to its latest quarter | Figures stay current | No |
| 3 | Model runner on GitHub Actions for unstructured sources, including distress | New weekly log entries | One step: run `claude setup-token` on his own account, because the token is tied to his login |
| 4 | Auto-publish path (data-only merge to `main` on passing checks); retire the approval workflow | No | No |
| 5 | Expand to twelve domains and about sixty suppliers; comparable per-domain view with same-metric figures, prior quarter and domain median | Yes: the main new value | His word to promote the layout change |
| 6 | Apply the four intent amendments as v1.4 | No | His approval of the text |

Step 0 can start the moment he says go. Steps 2 and 4 together are what makes the site stay fresh
without him.

## 7. Deferred, not in this plan

- Disclosing on the site that the author works for a reseller of these suppliers (product core
  section 10). His decision; recommended, but not part of making the site work.
- Analytics, a newsletter, and monetization.
- The decision-impact log, at the owner's direction.
- Branch protection on `main` (SEC-051), which becomes more important once a job can push to it.
