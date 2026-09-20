# T1-1 — Thesis-driven publications

Research for Security Market Pulse (https://securitymarketpulse.com), a weekly, signed,
evidence-first cybersecurity market publication that scores a standing thesis each issue (holds,
strengthens, weakens, no-call). This note studies how other publications make a standing argument
visible over time, and what a small single-author weekly site can actually copy.

## What I looked at and what I could not reach

I fetched the homepage, about/membership page, and (where one existed) a concepts or archive page
for Stratechery, SemiAnalysis, The Information, Platformer and Latent Space. I added two
publications that publicly score their own past calls: Astral Codex Ten's annual prediction
contest, and Nate Silver's Silver Bulletin pollster ratings, since the brief asked for exactly this
pattern and none of the five main sites do it in a pure form.

I could not reach exact, first-party subscription pricing for SemiAnalysis, The Information, or
Latent Space. Their subscribe/pricing pages render the dollar figures with client-side JavaScript,
and the fetched HTML came back as a bare "Subscribe" button with no price text — the tool that
converts a page to text never saw the number. Search results surfaced numbers attributed to these
sites (SemiAnalysis institutional tiers behind a sales email; The Information around $399 to $749
a year depending on tier, from a 2023 Digiday piece and a 2026 pricing-recap blog rather than
theinformation.com itself; Latent Space around $150 a year from a general "Substack pricing"
roundup). None of those is a quote I pulled from the publisher's own page today, so I am marking
every number in this note that did not come with a direct URL and quoted line as "from general
knowledge, not verified this run." Stratechery's price is the one exception: its membership page
rendered as static text and gave me a directly quoted figure.

## Findings per product

**Stratechery (Ben Thompson).** The homepage leads with a tagline ("On the business, strategy, and
impact of technology"), a "This Week in Stratechery" roundup with short editorial framing, and the
latest podcast episode — not a bare list of headlines. The standing thesis is not stated fresh on
the homepage; it lives at a separate page, `/concepts/`, organized under six headings (AI,
Aggregation Theory, Disruption Theory, Incentives, Technology and Society, Evolution of Technology).
Aggregation Theory, the site's central and most cited framework, gets its own subtitle and a curated
set of articles that built and later extended it. This is the clearest answer in this set to "can a
reader see the current state of the argument without reading years of posts": yes, on a page built
for exactly that, kept separate from the flow of daily writing. On corrections, the about page
states Thompson's own rule directly: "While I will make mistakes, I will always strive to correct
them quickly and publicly, and take active steps to ensure I don't make similar mistakes in the
future" (stratechery.com/about/). I found no dedicated corrections log or changelog; the commitment
is a stated norm, not a visible record. Free versus paid: "Weekly Articles are free, while three
Daily Updates a week are for subscribers only" (same page). Pricing, confirmed on
stratechery.com/membership/: "$15 / month or $150 / year" for Stratechery Plus, with team
subscriptions sold separately at an unlisted price. The fixed-day habit is the twice-daily Update
cadence plus a Friday roundup, which is frequency as a hook rather than a single flagship day.

**SemiAnalysis.** The homepage commits to a mission line — "Bridging the gap between the world's
most important industry, semiconductors, and business" — and cites "Over 180,000+ subscribers,"
which functions as social proof rather than a thesis statement. There is no visible page that states
a standing argument the way Stratechery's Concepts page does; the site reads as a research shop with
a newsletter front end, and its authority comes from named modeling work (a wafer fab cost model,
GPU cluster cost breakdowns, chip supply forecasts) rather than a tracked, revisable thesis. Free
versus paid is present as a general split ("Free and paid analysis" per the FAQ) plus a distinct
"Institutional" tier for data products, but I could not confirm dollar figures for any tier this
run — mark unverified. What repeats and returns readers is depth and specificity of the modeling,
not a fixed publishing day.

**The Information.** The homepage today opens with a product pitch for an AI research tool ("In-depth
insights in seconds. Ask Deep Research" and "We didn't build a better AI. We just built one with
over a decade of The Information behind it.") before dropping into a conventional section-based
river (Exclusive, Dealmaker, Weekend, Applied AI). There is no standing-thesis surface here at all;
the product is scoops and access to a proprietary archive, not an argument that develops. Catching a
new reader up means browsing by section, not reading a synthesis page. Pricing did not render for me
today; secondary sources describe roughly $399 to $749 a year across an individual and a "Pro" data
tier, with a discounted under-30 rate — unverified this run.

**Platformer (Casey Newton).** The homepage states a plain thesis line — "Independent reporting on
AI, social platforms, and the people shaping technology" — with a byline promise ("Original
reporting and analysis from Casey Newton, delivered to your inbox"). Paid pieces carry a lock icon
next to the headline in the list view, which is a cheap, legible way to show the free/paid line
without a paywall wall. The site states its own cadence directly: "At least one free edition comes
out every week. Paid subscribers receive at least one additional update each week" — a fixed-day
promise stated as policy, not just observed behavior. The about page points corrections to
casey@platformer.news but shows no visible corrections log or "we got this wrong" archive. Price is
commonly cited as $10/month, which I could not confirm on-page this run — unverified.

**Latent Space (swyx and Alessio).** The homepage frames itself as "The AI Engineer newsletter + Top
technical AI podcast," anchored to guest credibility (Greg Brockman, Andrej Karpathy) rather than a
standing argument of its own. There is no thesis page; the product is curated access to how frontier
labs build, delivered through interviews. This is closer to a beat than a thesis, and it is the
weakest fit in this set for "a standing argument developed over time" — its strength is guest access
and technical density, not an evolving position a reader can track. Pricing unverified this run.

**Astral Codex Ten (Scott Alexander) — added.** This is the cleanest example in the set of a public
calibration record, and it runs on a fixed annual cycle rather than a weekly one. The methodology is
stated in one line: "At the beginning of every year, I make predictions. At the end of every year, I
score them" (astralcodexten.com/p/2020-predictions-calibration-results). The scoring post plots
predicted confidence against realized frequency and names the result plainly — for 2020, Alexander
was "consistently overconfident (below the green line of perfect calibration) in every bin," with
bin-level numbers given (his 50%-confidence predictions came true only 22% of the time that year,
his 90%-confidence predictions 84% of the time). He attributes part of the miss to a genuinely
unusual year (extended pandemic lockdowns, an unrelated controversy) rather than smoothing it over.
A separate, related post, "Who Predicted 2022?", scores 71 yes/no questions across pundits using
log-loss and opens by naming a specific and visible failure ("Pundits, politicians, and economists
were caught flat-footed") before showing who did better. This is a self-imposed public scorecard with
a consistent, comparable methodology across years, not a single dramatic mea culpa post.

**Silver Bulletin / Nate Silver — added.** Silver's pollster ratings page is a standing, dated
scorecard, but it scores other people's forecasts (pollsters), not his own model, which is a useful
distinction for this project. The rating combines "historical accuracy and its transparency/
disclosure standards" into a single letter grade, with named sub-metrics (Simple Average Error,
Advanced Plus-Minus, a mean-reverted bias score) and a stated update cadence tied to real election
cycles: "Because 2025 was an off-year, we've only added about 40 polls since the last update"
(natesilver.net/p/pollster-ratings-silver-bulletin). The ratings database goes back to 1998, with
more recent results weighted more heavily. Separately and by general knowledge (not fetched this
run), Silver has written directly about his own model's 2024 miss rather than only rating others,
which matters for this project's kind of self-scoring.

## Patterns that repeat across products

A standing thesis, when it exists at all as a visible artifact, lives on a page separate from the
flow of new posts — Stratechery's Concepts page and ACX's annual scoring post are both destinations
a reader goes to on purpose, not something dropped into the normal feed. None of the five main sites
keeps a visible, dated corrections log; corrections are handled as a stated personal norm (Stratechery)
or an email address (Platformer), which is a promise rather than a record. The sites with the
clearest fixed-day habit state their cadence as an explicit policy sentence ("at least one free
edition... every week") rather than leaving it to be inferred from observed posting. Free-versus-paid
is marked cheaply and visibly at the list level (a lock icon, a "Daily Update" versus "Weekly
Article" label) rather than hidden until a click. Calibration and scorecard behavior is rare and,
where it exists, is annual rather than weekly, plotted rather than narrated, and paired with an
explicit admission when the number is bad. Pricing pages across every commercial site here are
either static and quotable (Stratechery) or dynamically rendered and effectively invisible to a
plain fetch — worth noting for anyone doing this kind of research again.

## What transfers to a small, single-author, weekly, evidence-first site, and what does not

What transfers: a single dedicated page that states the current thesis in one place, separate from
the weekly issues, the way Stratechery's Concepts page does for Aggregation Theory — this site's
market thesis and its four-state verdict already gives it the raw material for exactly this kind of
page. A one-line, prominent cadence promise ("a signed issue every week, thesis scored holds,
strengthens, weakens, or no-call") does real work per Platformer's example, and the lock-icon pattern
translates directly to marking which sections are free versus paid once the site ever gates content.
The ACX-style calibration record transfers well in spirit: publish the scoring methodology once,
apply it every issue, and show the miss plainly when the call is wrong, rather than only celebrating
the hits. What does not transfer: The Information's scoop-and-access model assumes a large reporting
staff and a proprietary information edge this project does not have and does not need; SemiAnalysis's
authority-through-proprietary-modeling approach assumes a research team building named cost models,
which is a different kind of asset than a signed weekly verdict; and Latent Space's guest-access
model assumes a beat with famous interview subjects, which does not fit a site whose credibility
comes from evidence and sourcing rather than access.

## Design and product moves

1. Build one page, separate from the weekly issue stream, that states the market thesis's current
   posture in plain language, so a first-time reader can see where the standing argument stands
   without reading back issues.
2. Put the weekly verdict label (holds, strengthens, weakens, no-call) in the same visible spot on
   every issue and on the thesis page itself, so a returning reader can scan the history of verdicts
   as a sequence rather than reconstructing it from prose.
3. Publish the scoring methodology once, on its own page, in plain declarative sentences like ACX's
   "at the beginning of every year I make predictions, at the end I score them," so the standard is
   fixed before any individual verdict is judged against it.
4. Keep a dated, append-only corrections log as a real page, not a promise in an about section, so a
   reader can verify the site does what its ethics statement claims rather than take it on faith.
5. State the publishing cadence as an explicit sentence on the homepage ("a signed issue every
   Friday") rather than letting a reader infer it from timestamps, so a lapsed reader knows exactly
   when to come back.
6. When the thesis is wrong, write the miss as its own short, named event on the thesis page (what
   was predicted, what happened, why it missed) rather than letting a "weakens" label stand alone,
   so a reader can see the reasoning behind a reversal and not just its result.
7. Mark any future paid content with a single, consistent visual signal at the list level (Platformer's
   lock icon is a good model) so the free/paid line is visible before a click, not discovered after
   one.
8. If a data or citation API is ever built, publish it from a static, plain-HTML pricing or access
   page rather than a JavaScript-rendered one, since a crawler, an agent, or even a simple fetch tool
   cannot read a client-rendered price — this matters doubly for a site that wants to be agent-cited.
9. Give the market thesis a name and a short definition the way Stratechery names "Aggregation
   Theory," so it can be referenced, linked, and cited as a concept rather than only described anew
   in every issue.
10. Consider an annual (not only weekly) scored-recap post in the ACX style, summarizing every verdict
    issued that year against what actually happened, since a single annual reckoning is a stronger,
    more legible trust signal than the same information scattered across fifty-two individual issues.

## What I could not verify

Exact current subscription prices for SemiAnalysis, The Information, Latent Space, and Platformer —
their pricing pages did not render dollar figures to the fetch tool, and the figures attributed to
them in search results came from third-party blogs and older news coverage rather than the
publishers' own pages today. Also unverified: whether Nate Silver has published a self-scoring page
for his own election model comparable to the pollster-ratings page (I only confirmed the
pollster-rating scorecard directly; his own-model self-scoring is noted from general knowledge).
