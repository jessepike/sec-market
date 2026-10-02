# Research: how good products present dense market data

Contestant: Claude Opus 5.5. Written 2 October 2026 before designing.

The question I was answering: how do the best data products put a lot of real information on one
screen, keep it calm, and keep every number traceable? I looked at the products the owner named, a
few market-data tools that handle many companies at once, and the standard references on small
graphics. Some sites block automated reading (Cloudflare Radar returned HTTP 403), so for those I
worked from the public write-ups and from long familiarity with the product, and I say so below.

## What I looked at

| Source | Link | Why it matters here |
|---|---|---|
| Cloudflare Radar (home) | https://radar.cloudflare.com/ | The closest analogue: a public, free, data-dense "state of the network" page with summary cards, time-range control and per-chart source notes. (Blocked to my fetcher; reviewed from the product itself and its write-ups.) |
| Cloudflare Radar 2025 Year in Review | https://radar.cloudflare.com/year-in-review and https://blog.cloudflare.com/radar-2025-year-in-review | How Radar states its time window ("January 1 to December 2, 2025"), its baseline and its data sources, and how it organises six sections each led by key findings. |
| Linear changelog | https://linear.app/changelog | The reference for a calm, dated, newest-first feed: date as the section divider, major items full width, minor items grouped densely under small all-caps labels, almost no colour. |
| Stripe design system write-ups and Stripe's annual letter page | https://stripe.com/annual-updates/2024 and https://design.hagicode.com/designs/stripe/ | Light canvas, deep ink headings, one accent colour, light-weight display type with tight tracking, tabular figures for financial numbers. |
| Koyfin screener and watchlists | https://www.koyfin.com/blog/find-best-stocks-with-screener/ | How a market-data tool shows many companies at once: user-chosen columns, sortable headers, a median summary row, and sparklines as a column type. |
| PitchBook company profiles | https://libraries.emory.edu/sites/default/files/migrated-documents/db-pages/pitchbook-viewing-company-profile.pdf and https://files.pitchbook.com/website/files/pdf/PitchBook_for_Dealmakers.pdf | For private companies: "last financing" (type, date, amount) as the headline fact, and a financing timeline with each round as a mark on a time axis. |
| Financial Times Visual Vocabulary | https://github.com/Financial-Times/chart-doctor/blob/main/visual-vocabulary/README.md | Nine chart families by the job the data does. Useful for being deliberate about which charts imply a ranking (ordered bars, dot strips) and which do not. |
| Edward Tufte, sparkline theory and practice | https://www.edwardtufte.com/notebook/sparkline-theory-and-practice-edward-tufte/ and https://en.wikipedia.org/wiki/Sparkline | "Data-intense, design-simple, word-sized graphics" that sit inside tables next to the number they explain. |
| Our World in Data, sourcing practice | https://ourworldindata.org/faqs | Every chart names its source and links to a "learn more about this data" layer, so provenance is always one click away without cluttering the chart. |

## Patterns I am taking

1. **Lead with the newest dated facts, laid out like a changelog (Linear).** The date is the row
   divider, the company name is the headline, the fact is the body, and the source sits at the end
   of the row. The current site buries "what changed" under twelve tables; Linear shows that a
   dated feed can be the first thing on the page and still read calmly.

2. **A strip of summary cards above the detail (Radar).** Radar opens with a few large numbers, each
   with a tiny trend, then the charts. Here that becomes six counts of tracked events over twelve
   months (acquisitions, funding, results, restructuring, debt and ratings, leadership), each with
   a twelve-bar monthly histogram. These are counts of facts, not scores, and each card doubles as
   a filter for the feed.

3. **State the window and the source on every chart (Radar, Our World in Data).** Every panel says
   which period it covers ("30 days to 26 Sep 2026", "12 months to 26 Sep 2026", "latest reported
   quarter") and where its numbers come from. Provenance is a click on the number or the source
   tag, never a separate column of "src" links.

4. **Sparklines inside the table (Tufte, Koyfin).** Each public supplier's row carries an
   eight-quarter revenue line drawn from its SEC filings, next to the reported growth figure. This
   is the densest honest picture available in the data, and it costs one table cell.

5. **One shared axis for growth bars, no colour judgement (FT deviation charts).** Reported
   year-over-year growth is shown as a thin bar from a visible zero line on one shared scale, in a
   single neutral colour. Negative growth extends left; it is not painted red. The table stays
   alphabetical unless the reader sorts it.

6. **A timeline of events in swim lanes (PitchBook financing timelines).** Twelve months on the
   horizontal axis, one lane per event type, one dot per tracked event. A reader sees the rhythm of
   the market (the acquisition lane is the busiest) without the page saying so. Position carries
   the type, so the dots need no category colours at all.

7. **The last financing round as the private company's headline fact (PitchBook).** For a private
   supplier the useful fact is the last round: stage, amount, month. For a PE-owned one it is the
   owner and the year. That gives every supplier one real fact to show instead of a row of dashes.

8. **Stripe's restraint.** Near-white canvas, one accent blue, deep ink, tabular figures, a
   geometric sans with tight tracking at display sizes, hairline borders instead of shadows.

9. **Detail on demand (Koyfin, PitchBook).** A side panel per supplier holds everything: every
   figure with its period and source, the SEC quarterly series as exact values, the full event
   history, and the list of source documents with excerpts. The front page stays short because the
   depth lives one click away.

## Patterns I am rejecting

1. **Radar's dark map-heavy hero and animated visualisations.** Beautiful for internet traffic, wrong
   for 74 companies. A map or an animated hero would cost the first screen and say nothing a
   security leader needs. Also the site is light-only.

2. **Leaderboards and ordered bar charts (FT "ranking" family, Koyfin default sorts).** A default
   order by growth reads as a ranking, which the hard constraints forbid. Ordering is alphabetical
   or chronological; sorting is the reader's choice.

3. **Red and green deltas.** Every finance product uses them, and they are exactly the "sentiment
   colour" the brief bans. Growth is a neutral bar; event types are distinguished by label and lane,
   not by warm and cold colours.

4. **Twelve wide tables with fixed columns.** That is what produced the dash-filled tables and the
   shifting column positions on the current page. Twelve compact domain cards, each listing its
   suppliers with one real fact apiece, replace them. Suppliers with nothing published are named
   once on one line instead of filling a row with dashes.

5. **A status banner at the top.** Radar and Stripe both keep operational notes out of the hero.
   Collection status becomes a small chip in the header that jumps to a full, honest disclosure at
   the bottom of the page.

6. **Stripe-style gradient hero and marketing copy.** The page is an instrument. Its first screen is
   data, with one sentence of framing.

7. **Inner scrolling panels.** Dense dashboards often put the feed in a scroll box. That breaks the
   phone and hides the end of the list; the feed is a normal part of the page.
