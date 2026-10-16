# Phase 1 dispatch specs — SEC-MARKET-FABLE-001

Written by the coordinator on 2026-09-20 so the research prompts survive a dead session. Each task
below is dispatched as one subagent with the model named in its heading, passed explicitly. All
eight are independent and go out in a single message. Every prompt is the shared preamble followed
by the task's own section.

## Shared preamble (goes at the top of every prompt)

You are a research worker for Security Market Pulse, https://securitymarketpulse.com, a public
site that publishes a signed weekly issue on the cybersecurity market (funding, M&A, vendor prints,
capital) and scores a standing market thesis against each issue. The owner wants it to become a
site that chief information security officers, investors and security leaders visit weekly, that
AI agents can read and cite, and that can eventually be paid for. Your research feeds a scoring
rubric and a design spec.

Rules. You are read-only on the repository at `/Users/jessepike/code/projects/sec-market` except
for the one output file named in your task. Do not edit, stage or commit anything. Do not install
anything. Do not read `docs/archive/`. Do not touch `lessons.md`.

Evidence standard. Every factual claim about another product carries the URL you fetched and, for
any price, number or policy, the quoted line it came from. If you could not fetch a page (paywall,
bot block, timeout), say so and mark what you wrote about it as "from general knowledge, not
verified this run". Never present a remembered number as a fetched one. Today is 2026-09-20; prefer
what the page says today over what you remember.

Output. Write one Markdown file at the path given, 150 to 250 lines, plain full sentences, with
these sections: what you looked at and what you could not reach; findings per product; patterns
that repeat across products; what transfers to a small, single-author, weekly, evidence-first
site and what does not; and five to ten concrete, testable design or product moves, each written
as "do X so that a reader can Y". Your final reply is short: the file path, the three things the
coordinator most needs to know, and anything you could not verify. No file dumps.

## T1-1 — Thesis-driven publications — claude-sonnet-5

Output: `docs/archive/2026-09-weekly-issue/fable-run/research/01-thesis-publications.md`

Study Stratechery, SemiAnalysis, The Information, Platformer and Latent Space. Add one or two
others if they do this better, for example a forecasting or macro publication that scores its own
past calls publicly. The question is how a standing argument is made visible and developed over
time. For each: what the home page commits to versus the archive; whether a reader can see the
current state of the author's thesis anywhere, or only infer it from posts; how history,
reversals, corrections and "I was wrong" are handled; how a new reader is caught up; what is free
versus paid and where the line sits; and what brings a reader back on a fixed day. Look
especially for any public calibration record or scorecard of past calls, since this site already
scores its thesis each week (holds, strengthens, weakens, no-call) and wants to show that history.

## T1-2 — Data-dense public intelligence products — claude-sonnet-5

Output: `docs/archive/2026-09-weekly-issue/fable-run/research/02-data-dense-products.md`

Study Cloudflare Radar above all, then Our World in Data, FRED, Trading Economics, Public Comps
and Sacra. For each: what the first screen commits to at desktop width; how a dense page is made
scannable (grouping, type scale, tables versus cards, sparklines, monospace figures); how
freshness is shown (as-of dates, update cadence, "last updated"); how provenance is shown (source
lines, methodology links, downloadable data); how a chart or number is cited or embedded by
someone else; what API or data download exists and on what terms. Note what each does badly.

## T1-3 — Security-market peers and the price umbrella — claude-haiku-4-5

Output: `docs/archive/2026-09-weekly-issue/fable-run/research/03-peers-and-pricing.md`

Study Return on Security, CB Insights, PitchBook, Gartner and Forrester security research,
Cyberstarts and other specialist security venture research pages, Momentum Cyber and similar
market maps, plus any weekly security-industry business newsletter you find (for example
Software Analyst Cyber Research, Strategy of Security, Venture in Security). For each: what it
publishes, how often, who it is for, what is free, what is paid, and the published price with the
URL and quoted line. Where no price is published, say "not published" and do not estimate. Finish
with a table of the price umbrella from free to enterprise, and a plain statement of where a
weekly, evidence-first, signed read with named sources is differentiated and where it is not.

## T1-4 — Monetization mechanics — claude-haiku-4-5

Output: `docs/archive/2026-09-weekly-issue/fable-run/research/04-monetization-mechanics.md`

For each model below, find real published numbers from operators who have written about their own
results (Substack, beehiiv, Ghost and Stratechery-style write-ups, sponsorship rate cards, public
revenue posts): free weekly plus paid archive; paid data layer; team and corporate licences;
sponsorship; lead-magnet reports; custom research; metered API or agent access. For each: the
audience size at which it starts to work, the typical free-to-paid conversion rate with source,
typical price points with source, what it demands of a single author each week, how quickly it
can start from a list of zero, and what it requires technically (payment provider, accounts,
email provider). Mark every number as fetched or as unverified general knowledge.

## T1-5 — Agent-readable web — claude-sonnet-5

Output: `docs/archive/2026-09-weekly-issue/fable-run/research/05-agent-readable-web.md`

Current practice as of September 2026, not 2024 practice. Cover: `llms.txt` and `llms-full.txt`
and the evidence on whether any major crawler or agent actually reads them; Markdown variants of
HTML routes and `Accept: text/markdown` content negotiation, including what Cloudflare and Vercel
ship for this; the schema.org types that matter for evidence and claims (`Article`, `Report`,
`Dataset`, `ClaimReview`, `Organization`, `Person`, `Claim`) and which consumers use them; stable
citation anchors and text fragments; remote MCP servers as a distribution surface for a
publication and any real examples; pay-per-crawl and similar metering schemes; and the named AI
crawler user agents and how sites declare policy for them (robots.txt, Content Signals, headers).
Then give both sides of the argument about letting AI crawlers in or blocking them, for a small
publication that wants citations and may later sell access. Do not recommend a side; that is an
owner decision. The site is a static prerender on Vercel with no backend, so say for each
technique whether it works on a static host. What already exists on the site is listed in section
F of `docs/archive/2026-09-weekly-issue/fable-run/reading-summary.md`; read that first.

## T1-6 — First-screen and information design craft — claude-sonnet-5

Output: `docs/archive/2026-09-weekly-issue/fable-run/research/06-first-screen-craft.md`

Study Linear, Zed, Vercel, Railway and Resend (product sites, changelogs and docs) for restraint
and density, plus two or three editorial or data products that carry real information on the
first screen. The house style target is the simplicity of Linear with the density and clarity of
Zed, light theme only. Answer: what earns the first 600 vertical pixels of a desktop information
product; what a 390 by 844 phone screen can carry before the first scroll; how type scale, line
length, tabular and monospace figures and metadata rows affect scanning speed, with sources where
research exists; how these sites use colour (how many hues, where accent colour is allowed); and
how keyboard movement is offered. Treat WCAG 2.2 AA as a design input: contrast minimums for
small monospace metadata, target sizes, focus appearance, reflow at 320 CSS pixels, and what
those rules forbid that dense designs commonly do.

## T1-7 — Current-site teardown — claude-sonnet-5, with screenshots delegated to claude-haiku-4-5

Output: `docs/archive/2026-09-weekly-issue/fable-run/research/07-site-teardown.md`
Images: `docs/archive/2026-09-weekly-issue/fable-run/evidence/baseline/`

Render https://securitymarketpulse.com/ , `/issues/` and `/issues/2026-w36/`, and the same three
paths on https://security-market-pulse-git-preview-pikeholdings.vercel.app , at 1440 and 390.
Read `web/scripts/shot.mjs` first to see how it is run and do not modify it. All Node work runs
in the OrbStack dev VM (`orb run -m dev ...`, repo at
`/mnt/mac/Users/jessepike/code/projects/sec-market`), never on the Mac. Besides the full-page
captures, produce a first-viewport capture at 1440 by 900 and at 390 by 844; if `shot.mjs` cannot
do that, write a throwaway script inside the evidence folder, not in `web/scripts/`. Spawn a
`claude-haiku-4-5` subagent for the capture step, passing the model explicitly. Report image file
sizes; do not commit anything.

Then look at the images and read the prerendered markup (`curl` the live HTML) and describe,
bluntly, what a chief information security officer experiences in the first five seconds, the
first thirty seconds and the first three minutes, separately for desktop and phone. State what
the first screen says the site is, whether the standing thesis is visible without scrolling, how
far down the signed judgment sits in pixels, what is confusing, what is buried, what is repeated,
what gives no reason to return next week, and what a returning reader could tell had changed.
Also record, as facts for the later baseline: the live `robots.txt` text, response headers for
`/`, whether `/feed.xml`, `/issues/index.json`, `/issues/2026-w36.json` and `/sitemap.xml`
return 200 and their content types, the heading outline of the front page, and the count and
types of JSON-LD blocks. Say whether production and preview differ visibly at all.

## T1-8 — Thesis history already in the repository — claude-haiku-4-5

Output: `docs/archive/2026-09-weekly-issue/fable-run/research/08-thesis-history-inventory.md`

Added by the coordinator; not in the brief's list. The site will show how its thesis has developed
over time, but only one issue is signed, so a history built from issues alone has one row. Find
what dated, already-published thesis history exists in the repository that a history surface
could honestly draw on without anyone writing new judgments. Read `web/src/data/` (especially
the market call, `edition.ts`, `domains.ts`, `issues`, `meta.ts` and any evidence or falsifier
data), `docs/archive/2026-08-gate-chain/episode-002/`, `docs/archive/2026-08-signals/signals-week-2026-08-16.md`,
`docs/archive/2026-08-signals/signals-week-2026-08-19.md` and `decisions.md`. List every dated event that changed
or tested the thesis: the original call and its date, its stated confidence, its falsifiers and
alternatives, each appended edition record, each posture per domain with its date, and each
weekly verdict. For each, give the file path and line, whether it is already rendered on the live
site, and whether it is signed by a person. Do not propose new judgments and do not read
`docs/archive/`.
