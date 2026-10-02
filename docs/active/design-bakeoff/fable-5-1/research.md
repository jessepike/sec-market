# Research notes — Fable 5.1 entry, Security Market Pulse front page

**Artifact:** `SEC-MARKET-DESIGN-BAKEOFF-001` / contestant `fable-5-1`
**Date:** 2026-10-02
**Method:** I looked at each reference below on 2026-10-02 (fetched directly where the site allowed
it, otherwise through its own write-ups and third-party descriptions), read the project's
`product-core.md` and the tracker data, and wrote down the patterns before designing anything.

## 1. What I looked at

### Cloudflare Radar (directly relevant: many entities, one dense page)

- https://radar.cloudflare.com/ (the page itself returned HTTP 403 to a fetch, so I worked from the
  launch write-up and the changelog)
- https://blog.cloudflare.com/radar2/ — the Radar 2.0 redesign post
- https://developers.cloudflare.com/changelog/post/2026-06-05-radar-traffic-chart-granularity/

What Radar does well: a top filter bar that sets the time window for the whole page, "quick bytes"
(small glanceable cards that each state one fact and link to the deeper view), a sidebar by topic,
and reusable SVG chart components rather than one-off charts. The 2026 granularity change is a good
reminder that the time window is a first-class control, and that a chart should carry more points
when the window is longer. The stated goals were discoverability, more topics, and sharing, not
decoration.

What would not transfer: Radar's charts are continuous time series over millions of samples. Our
data is 74 companies with at most eight quarterly points each, and most companies have no series at
all. A Radar-style wall of line charts would be mostly empty.

### Linear (marketing pages and changelog)

- https://linear.app/
- https://linear.app/changelog
- https://www.buildmvpfast.com/blog/linear-aesthetic-tokens-density-keyboard-first-ux-2026 (a
  decoding of Linear's tokens: Inter with `cv01`/`ss03`, 13px as the working density, weight 510 as
  the signature emphasis, a Cmd+K palette)
- https://www.launchnotes.com/blog/release-notes-design-trends-product-teams-are-adopting-in-2026

Taking: the changelog is a dated, reverse-chronological ledger with a prominent date header, one
heading per entry, and dense bulleted sub-lists. Density comes from a small working size (13px),
restrained weights (regular, medium, semibold and nothing heavier), and a hierarchy built from
luminance (greys) rather than from colour. Whitespace is used between groups, not inside them.
A tab row at the top filters the ledger without scrolling.

Rejecting: Linear is a dark-first brand. The owner wants light only. Linear's marketing pages also
lean on product screenshots for rhythm, which we do not have.

### Vercel design system

- https://vercel.com/design

Taking, almost verbatim as rules: "use color only when it adds significant meaning to state, action,
or data, and pair it with a non-color cue"; Geist Mono only for identifiers and operational values,
never sentences; tabular numerals for comparison; table headers aligned with their columns (text
left, numbers right); "equivalent peers always share role, size, weight, line-height, and numeric
treatment; never resize one because its string is longer"; "every gap has one owner". The last two
are exactly the discipline the current page lacks (column positions drift between tables).

### Stripe

- https://stripe.com/annual-updates/2024 (landing page; the letter itself is a PDF)

Taking: Stripe's letters put a single large figure in a sentence and keep the paper calm, with one
accent colour. The landing page itself is a lesson in the opposite direction: a single unsourced
comparative figure with the detail locked in a PDF. For a page whose whole claim is "every figure
keeps its source and its date", that model is rejected.

### Koyfin, watchlists and screeners

- https://www.koyfin.com/features/watchlists/
- https://www.g2.com/products/koyfin/reviews

Taking: saved column configurations, one fixed row per company, right-aligned tabular numbers, and
the reader (not the publisher) choosing the sort. Rejecting: Koyfin's red/green colouring of change
values. On a site that must not imply good or bad, a red number is a judgment. Growth is shown in
one ink here.

### Financial Times visual journalism

- https://baryon.be/?p=3308 ("Small multiples can save your chart", describing the FT's switch
  from one tangled multi-country line chart to small multiples during 2020)
- https://eyemagazine.com/feature/article/conversation-with-john-burn-murdoch
- The FT Visual Vocabulary (ft.com and the GitHub mirror were unreachable from this host; I used
  the baryon write-up and my prior knowledge of the chart families)

Taking: when there are many series, show each on its own small panel with the same axes, and let
the reader find the one they care about. Taking also the FT habit of a visible source line under
every chart. Rejecting: FT's pink paper and serif display type; our owner's references are
technology companies, not newspapers.

### Tufte, sparklines in tables

- https://www.edwardtufte.com/notebook/sparkline-theory-and-practice-edward-tufte/

Taking: a sparkline is a "word-sized graphic" that sits in a table cell next to the number it
explains; mark the latest point and tie it to the printed value; no frames or axes; let the
positions of the numbers form the grid. This fits the EDGAR series exactly: fourteen SEC filers,
up to eight quarters each, one small line per row, nothing where no series exists.

### Ramp

- https://www.shadcn.io/design/ramp and https://kombai.com/gallery/design-systems/ramp-kombai/

Taking: an austere white canvas, monochrome type, and exactly one accent colour used sparingly.
Rejecting: the high-voltage chartreuse accent. The accent here is a quiet blue, used for links and
the latest point in a sparkline, nothing else.

### PitchBook-style company lists

- https://www.slidegenius.com/cm-faq-question/what-is-a-pitchbook-company-profile-and-how-can-it-help-in-investment-research
- https://www.cbinsights.com/company/pitchbook-data/financials

Taking: one profile record per company with a fixed set of fields (ownership, last round, lead,
valuation, date) and a dated event list, so a company with little public data still has a
complete, honest record ("private, last round Series D, Aug 2024") rather than blank cells.
Rejecting: the investor framing and anything that reads as a deal pipeline.

### Timelines and "what changed" patterns

- https://docs.appian.com/suite/help/26.8/event-timeline-pattern.html (a dated list of events,
  grouped and scannable, as a general interface pattern)
- https://www.cs.ubc.ca/group/infovis/software/TimeLineCurator/tlc-vast-2015.pdf

Taking: a flat, dated, filterable ledger beats a graphical timeline when events are text-heavy and
of mixed kinds. Group by date, tag by type, keep each entry to one or two lines with the full text
one click away.

### The current site

- https://securitymarketpulse.com/ (production) and the proposed version at
  https://security-market-pulse-git-mon-uifix-pikeholdings.vercel.app/

Confirmed the problems in the brief: twelve tables whose column order shifts, cells that are
mostly dashes, a collection-failure notice as the opening line, and "what changed" below the
tables. The production page also still carries posture tags ("PREPARE", "WATCH") and a "what we
now think" block, which D-76 does not allow a machine to publish.

## 2. Patterns I am taking

1. **Ledger first.** The dated "what changed" list is the first thing after the masthead, Linear
   changelog style: date in mono, a monochrome type tag, the supplier, one line of text, the source.
   A window control (30 days, 12 months) and type filters sit above it.
2. **One alphabetical dot plot for the comparable figure.** All eighteen public reporters on one
   panel, alphabetical, with a dot on a shared growth axis. The reader sees the spread without
   anyone ranking it. A sort control lets the reader reorder by value if they choose.
3. **Sparklines only where a filed series exists.** Fourteen SEC filers get a word-sized line of
   reported revenue by quarter, with the latest point marked. Nobody else gets an empty slot.
4. **A fact line, not a table of dashes.** Each supplier row carries the facts that exist for it,
   in a fixed priority order (revenue and growth, the company's own metric, ownership or last
   round), each a span with its own date and source. A private company reads "Private · Series D
   $250M at $5.1B, Aug 2024 · ARR over $200M (Aug 2024)", never "–  –  –".
5. **One ink for numbers, one accent for interaction.** No red or green anywhere. Type tags and
   kind tags are grey with text.
6. **Source as a hover card and a link.** Every figure is a link to its source document; hovering
   or focusing shows the source title, publisher, publication date and the period covered. Nothing
   wraps onto its own line.
7. **Fixed column roles.** Within the board every row has the same three regions (name and kind,
   fact line, event count), so nothing drifts between domains.
8. **Honest status, second screen.** The collection status is one line under the masthead with
   the detail in a closed disclosure, and a full "Coverage and gaps" section further down.

## 3. Patterns I am rejecting

- Red/green or any warm/cool colouring of values (implies good/bad; D-76).
- A default order by growth, size or any metric (implies a ranking; alphabetical throughout).
- Twelve separate tables with differing columns.
- Stat tiles with a single big number and no source.
- Dark theme, dark mode media queries, and any decorative gradient or illustration.
- Graphical timelines for text events.
- Hiding detail in a PDF or a secondary page; every source is one click from the figure.
