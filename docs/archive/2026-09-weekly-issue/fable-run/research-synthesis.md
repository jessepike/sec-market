# Research synthesis — SEC-MARKET-FABLE-001, Phase 1

**Written by:** the run coordinator, 2026-09-20
**Inputs:** nine research files under `docs/archive/2026-09-weekly-issue/fable-run/research/` (01 to 09), the reading
summary at `docs/archive/2026-09-weekly-issue/fable-run/reading-summary.md`, and the captures under
`docs/archive/2026-09-weekly-issue/fable-run/evidence/`.
**Status:** closes Phase 1. Feeds the rubric (Phase 2) and the three specs (Phase 3).

This document says what the evidence supports, where it is thin, what applies to this site and
what does not, and the strongest argument against the direction the run is about to take.

## 1. How good the evidence is

The research is uneven, and the plan should lean on it unevenly.

**Solid, first-hand.** The site teardown (file 07): rendered captures at both widths, the live
markup, headers and endpoints. The thesis history inventory (08): read from the repository with
paths and lines. Cloudflare Radar's layout and per-chart menu (09): captured in a real browser.
Prices for Stratechery, The Information, and Return on Security and its data product The Signal:
quoted from the publishers' own rendered pages. The six WCAG 2.2 AA criteria (06): quoted from W3C.
Vercel's Markdown-access documentation (05): fetched, dated 2026-09-17.

**Second-hand, directionally useful.** Newsletter conversion and sponsorship rates (04) come from
platform marketing reports and sponsorship-broker blogs. The claim that `llms.txt` and Content
Signals are ignored by major crawlers (05) comes from aggregator write-ups of studies nobody on
this run read; several sources converge, which is worth something, but no number from them should
appear in a plan as fact. Colour and type measurements for Linear, Vercel and the rest (06) came
from third-party style scrapers, because those sites serve a stripped page to fetch tools.

**Absent.** Prices for SemiAnalysis, Platformer, Latent Space and Software Analyst Cyber Research
did not render to an anonymous browser. No single-author publication publishes a team licence
price. No small editorial publication was found running a remote MCP server. Nobody found a
first-hand revenue account from a single-author security newsletter. Every one of these gaps sits
in the monetization plan's territory, which is where invented numbers do the most damage, so that
plan must label guesses as guesses.

## 2. What the evidence says

### 2.1 The site hides its own argument

This is the clearest finding of the run and it comes from looking at the page.

- At 1440 pixels the first screen is a news headline followed by three funding rounds, one per
  full-width card. The second item a reader sees is a $2.6M pre-seed. Nothing above the fold says
  what the site is, who it is for, or what it argues. The headline ends "the infra-to-security lag
  call holds", which only means something to a reader who already knows the call.
- The signed judgment and the thesis ("Infrastructure is running ahead. Security is splitting, not
  booming.") sit about 34 percent down a 15,022 pixel page on desktop, close to six screens of
  scrolling, and about 41 percent down a 17,715 pixel page on a phone, about eight and a half
  screens. Everything before them is tracked evidence in one repeated card template that gives a
  $2.5M round and NVIDIA's $96.2B print the same visual weight.
- Forty-one disclosure widgets, none open by default, hold the what-changed log, the falsifier
  list, the method and most per-vendor detail. A crawler sees all of it. A person sees summary
  lines.
- The home page and the only issue permalink are pixel-identical. The archive is one row over a
  blank page. There is no subscribe path, no stated publishing day and no next-issue date.
- Inside the collapsed method section the site says "Refresh is manual... Not a weekly news
  cycle." The product is a weekly issue. The page contradicts its own product model.

The project already knows the first of these. D-66 records that nobody had seen the page at full
height until the promotion render, and names the composition as the first thing this run should be
pointed at.

### 2.2 A public record of your own calls is rare, and this site already keeps one

Across five thesis-driven publications (01) and eleven security-market peers (03), none shows a
standing, dated record of its own past calls. Stratechery keeps its frameworks on a separate
concepts page and treats corrections as a stated habit with no visible log. Platformer gives an
email address. The only real examples of public self-scoring are outside the category: Astral
Codex Ten states its method in one sentence, plots predicted confidence against outcomes, and says
so plainly when the result is bad; Silver Bulletin keeps a dated scorecard, of other people's
forecasts.

This site already has the mechanism: a thesis, a four-state verdict signed each week, a running
score, an append-only lock manifest that makes each signed issue immutable, and four written
change triggers that would move the call. What it lacks is the presentation. The differentiator is
built and buried.

### 2.3 The honest history is short and flat, and that shapes the design

The inventory (08) found five dated events: the Episode 002 call accepted 2026-08-15, three frozen
editions on 2026-08-16, 2026-08-17 and 2026-08-28 that each record "no posture moved", and one
signed weekly verdict on 2026-09-19, "holds" at medium confidence. There are no reversals and no
confidence changes. A history surface built today shows an argument that has not moved.

Two consequences. The history surface must read well with one to five rows and must not pad
itself. And "holds" every week is not a reason to return unless something underneath it visibly
moves. The repository states four change triggers in `web/src/data/market.ts` (realized security
budget growth; organic acceleration across a majority of comparable vendors; AI pilots expanding
into production; a registered infrastructure impulse followed by a registered security response)
but records nothing about movement toward or away from them. A weekly status against each trigger
is the smallest addition that makes a quiet week worth reading. It needs a field in the issue
model and the owner's signature, so it is a proposal for the design spec, not something this run
builds on its own authority.

### 2.4 Dense products earn their density with structure, not with small type

- Radar (09, seen directly): one global time-range control governs every chart; one hero panel,
  then a three-column card grid; two data hues and one accent; big plain numerals with small
  labels; no monospace anywhere. Every chart carries the same two controls, share and a menu whose
  items are "Explain with AI", "View in Data Explorer", "Generate citation" and an alert
  subscription. It offers citation and alerting where one would expect download and embed.
- Sacra and Public Comps (02) label the evidentiary kind of a number where the number appears:
  estimate, filing, named document. Public Comps makes the trace interactive.
- Linear and Hacker News (06): density comes from tight vertical rhythm, one line of title and
  one line of grey metadata per row. Body text never drops below roughly 13 to 14 pixels; 12
  pixels is for metadata only.
- Every light-theme product studied runs one functional accent on a neutral scale.
- FRED and Our World in Data stamp freshness on the content unit. The site already does this well
  in its top bar ("AS OF 19 SEP 2026") and its tracked-versus-judged legend; the legend is the
  right idea shown once and never again where it matters.

The current site's lanes are the opposite of this: one item per full-width card, generous padding,
about three items per desktop screen. The same 23 items in title-plus-metadata rows would fit in
roughly a fifth of the height.

### 2.5 For agents, what works is what runs at retrieval time

The agent-web research (05) splits cleanly. Techniques that a specific tool already uses at
request time are adopted: `.md` copies of routes and `Accept: text/markdown` (Vercel documents
that Claude Code and OpenCode send that header), JSON-LD, and text-fragment links, which several
answer engines already generate as their citation mechanism. Techniques that ask a crawler
operator to honour a new declaration are reported as mostly ignored: `llms.txt` and Content
Signals. Those are cheap hedges.

Three points specific to this site:

- The warning that text-fragment citations break when wording changes does not apply to signed
  issues here. The lock manifest makes them immutable and publishes the proof at
  `/issues/lock.json`. "This text cannot change, and here is the manifest" is a claim few
  publications can make to a machine reader. Unsigned surfaces (the thesis page, the front page)
  do change, so they need stable `id` anchors and dated versions.
- The base is already better than most: per-issue JSON with the cited evidence, an index, RSS, a
  sitemap, one JSON-LD block per route. Missing: a thesis endpoint, claim-level anchors, Markdown
  copies, `Organization`, `Dataset` and claim markup, a decided crawler policy, and a data licence
  statement. All of these are build-step changes on a static host. The teardown also found four
  domain-card headings that render as empty `h2` elements, which hurts both screen readers and
  parsers.
- A remote MCP server and pay-per-crawl both need infrastructure the project does not have (a
  serverless endpoint; Cloudflare in front of Vercel) and fall under the brief's "no backend
  without a separate yes". Return on Security already markets a native MCP server as part of its
  $199 a month tier, so the idea is proven for a data product in this exact niche, and not proven
  for an editorial one.

Whether to admit or block AI crawlers stays an owner decision. The evidence supports separating
retrieval crawlers from training crawlers, since the vendors now run them as separate bots, and it
also says crawler policy matters little for a site with almost no audience yet.

### 2.6 The money: the data lane is taken, the list is zero, and subscriptions are slow

- The closest peer, Return on Security, is also one of this site's main sources. It gives the
  newsletter away (a voluntary $12 a month backer tier with no perks), sells sponsorship by
  email quote, and makes its product money from The Signal: free lookups, $199 a month Pro with
  MCP access, a $79 a month API add-on, custom enterprise. Anyone selling security funding data
  competes with the publisher whose data they cite. This site's asset is the signed judgment and
  its track record, not the rows.
- Above that sits an enterprise umbrella with no list prices (PitchBook, CB Insights, Gartner,
  Forrester) and The Information at $399 to $749 a year with proprietary databases and a
  newsroom. Stratechery, the single-author benchmark, is $15 a month or $150 a year.
- Reported median free-to-paid conversion is 0.62 percent (beehiiv's 2026 report, second-hand).
  At that rate a thousand free readers at $10 a month is about $62 a month. Reported time to first
  dollar for a typical newsletter is about six and a half months. Sponsorship in business
  niches is reported at $40 to $120 per thousand readers and starts to matter around two thousand
  readers.
- The list is zero. The exposure denominator is one. Public email is held by SEC-029 until four
  held issues and the owner's 2026-10-08 review. `intent.md` names security leadership, account
  teams and clients as beneficiaries, not a paying public, and excludes investment advice.

Read together: individual subscriptions are the slowest and smallest path and the data lane is
occupied. The plausible early money for a site like this comes from a small number of
organizations paying for something built on the judgment (a team licence, a briefing, a
sponsored issue), and none of it starts until the cadence holds and a list exists.

## 3. Where the sources disagree

- **Monospace.** The house style and file 06 favour monospace for metadata and figures. Radar,
  the brief's primary reference, uses none, including for identifiers and percentages. Resolution:
  the scanning benefit comes from tabular figures and alignment. Use monospace for metadata lines
  and identifiers as the house style asks, and tabular numerals everywhere numbers stack; do not
  treat monospace itself as a quality signal in the rubric.
- **Does structured data earn citations.** Ahrefs tracked 1,885 pages and found no major uplift
  from adding schema; other secondary sources claim gains. Resolution: build structured data for
  precision (an agent that does read the page can cite it exactly), not as a traffic bet, and
  score D8 on what a machine can extract, not on hoped-for referrals.
- **Front page as index or as argument.** Database products open with search and live tables;
  research products open with prose. This site is a signed judgment with evidence, so it opens
  with the argument, and takes from the index products only their row density and freshness
  discipline for the evidence underneath.
- **How fast money arrives.** File 04 says sponsorship can start "in months" and proposes a rate
  card on day one. Its own conversion and time-to-first-dollar figures, and this site's list of
  zero, say otherwise. The cautious reading governs.
- **Keyboard-first.** The house style wants fast keyboard movement; file 06 found it is a
  developer-tool convention that no editorial or data product offers, and a command palette is
  real engineering. Resolution: keyboard access to everything and a small set of documented
  shortcuts (next and previous issue, jump to thesis, jump to evidence) are in; a command palette
  is a backlog idea.

## 4. What applies here and what does not

**Applies.**

1. State the thesis, this week's verdict, the signature and the date inside the first screen at
   both widths, with one plain line saying what the site is and when it publishes.
2. Give the thesis a home of its own with a stable address: current statement, confidence by
   component, the verdict sequence, the change triggers with their status, the dated history, and
   a corrections record. This is the Stratechery concepts page and the Astral Codex Ten scoring
   page in one place.
3. Make "what changed since last issue" a first-class block, not a collapsed section.
4. Re-set the four lanes as dense rows with a size cue, so a reader scans a week in one screen.
5. Label the evidentiary kind next to figures, and repeat the tracked-versus-judged distinction
   where judgments appear.
6. State the cadence as a sentence and show the next expected issue date, once the cadence is
   real. Fix the "Not a weekly news cycle" copy.
7. Differentiate the home page (the current state of the argument plus the newest issue in brief)
   from the issue permalink (the full immutable record).
8. Machine surface: a thesis JSON endpoint, stable claim anchors, `.md` copies of every route with
   `rel="alternate"` links, `Organization` and `Dataset` markup, a licence line, a short
   `llms.txt` as a hedge, and a crawler policy the owner chooses.
9. One accent on a neutral scale, light only; 24 by 24 pixel targets; visible focus; reflow
   tested at 320 pixels; contrast checked on small metadata text.

**Does not apply.**

- Anything that makes a weekly signed read look like a live dashboard. A reader who checks the
  as-of date against a real-time look loses trust at once.
- Selling funding or deal data. Return on Security owns that lane and is a source.
- Gating the archive. Every weekly peer keeps it open, the archive is the track record, and the
  track record is the differentiator.
- Seat-metered or task-metered pricing, enterprise sales, a command palette, per-request content
  negotiation, an MCP server, pay-per-crawl. Each needs scale or infrastructure this project does
  not have; the last three need a separate owner yes.
- A public subscribe form before the 2026-10-08 review. A visible "follow by RSS" and a pilot
  list by hand are what the current rules allow.

## 5. The strongest argument against this direction

The run is about to spend most of its effort on presentation: a thesis surface, a denser first
screen, a machine layer, conversion plumbing. The case against is that presentation is not this
product's constraint.

The project's own scorecard says so in one line: the binding constraint is that almost nobody has
seen it. One person has had a real chance to use the intelligence. No decision is recorded as
changed. One issue has been signed, thirteen days after its week ended. The gather routine has
never run on schedule, and issue 2026-w37 was due on 2026-09-15 and does not exist. A redesign
raises none of those numbers. A beautiful thesis-history surface with one row, on a site that has
not published for two weeks, advertises the gap. Worse, a polished site that looks alive invites
the judgment that the work is done, which is the exact failure the scorecard was rebuilt to
prevent, and `intent.md` says in terms that completing a website does not constitute success.

There is a second edge. The thesis has never moved. If it keeps holding every week, the
"living thesis" is a flat line, and readers will learn that the verdict carries no news. If the
owner feels pressure to make it move so the page has something to show, the site has started
optimizing apparent certainty and output over trust, which `intent.md` forbids. The design can
make the underlying evidence visibly move; it must never create an incentive to move the call.

And a third. The brief widens the audience to investors and a paying public. The accepted intent
names neither, excludes investment advice, and tells the project not to optimize traffic. A site
redesigned around weekly return visits is a site being tuned for traffic. That may be the right
new direction, but it is a change of intent, and it should be decided as one, not arrived at
through a redesign.

What survives. The first-screen problem is real on the project's own evidence, and fixing it is
cheap, reversible and already asked for by D-66. A pilot reader who is sent the site today has to
scroll six screens to find the judgment, so the redesign directly serves the exposure problem the
moment a pilot list exists. The machine layer is build-step work on a static site and costs
little. The thesis surface is the one thing no peer has. None of that is wasted if the cadence
starts. All of it is decoration if the cadence does not. So the plan that follows must put the two
owner actions that are outside this run (choosing the gather runtime under SEC-039, naming the
pilot list) at the front of its sequence in plain words, must design every surface to be honest
at one issue and at two weeks stale, must keep commercial work to plumbing that ships switched
off, and must carry the audience question to the owner as a proposed intent amendment.

## 6. What this changes in the rubric and the specs

- The rubric needs a **cadence honesty** element inside D3: a site that looks fresher than it is
  scores lower than one that shows its real age and next expected date.
- D2 (thesis development) must be scorable at one issue. Its anchors should reward a visible
  mechanism and honest sparse history, and should not reward volume.
- D6 should anchor on information per screen against the Radar and Linear references, with a
  measured count, and should not treat monospace as a virtue in itself.
- D8 should be scored by a scripted extraction test: can a program with no site knowledge pull
  the current thesis, this week's verdict, the signer and date, a specific claim with its source,
  and the archive list.
- D11 (conversion) must be scored against what the project's rules allow today, or it will punish
  the site for obeying its own governance. Its weight should be low until the owner opens the
  list.
- D9 and D10 were not measured in Phase 1. The baseline needs a real performance trace and an
  accessibility tool pass plus a keyboard walk.
- The design spec should treat removal as a first-class deliverable: the page is 15,000 pixels
  and the collapsed sections need a decision each (promote, move to the thesis page or a method
  page, or remove with owner approval).
