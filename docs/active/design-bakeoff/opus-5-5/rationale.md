# Rationale: Opus 5.5 front page

## The idea

The front page is an instrument panel for the business of the security market. It opens with what
changed in the last 30 days, laid out like a calm changelog, next to a twelve-month picture of every
tracked event. The densest evidence is one level down: one sparkline table for the public companies
and twelve compact domain cards that give every supplier one real, sourced fact. Everything else
(every source document, exact SEC values, the full event history) sits in a side panel one click
from any name.

## What is on the first screen, and why

At 1440 by 900 the reader sees, top to bottom:

1. A slim header with section links, a small "Checked 26 Sep 2026 · collection partial" chip, and a
   "Find a supplier" search box (press `/` or Cmd+K).
2. One headline ("The business of the security market, sourced and dated."), one sentence saying
   what is tracked, and "Not a news site and not investment advice." On the right is the reserved
   slot for the owner's signed read, clearly marked and left empty.
3. Six summary cards: acquisitions and divestitures 28, funding rounds 11, results 19, restructuring
   and layoffs 10, debt and credit ratings 8, leadership changes 18, each counted over the twelve
   months to 26 Sep 2026 with a monthly histogram and a 30-day count. Selecting a card filters the
   feed.
4. "What changed": all 25 items from the 30 days to 26 Sep 2026 (17 dated events and 8 SEC filings),
   grouped by date, newest first. Each item shows the company, the type of event, the fact, and a
   source tag.
5. "Twelve months of tracked events": a swim-lane chart with one lane per event type and one dot per
   event (94 dots). It shows the rhythm of the market at a glance, such as how busy the acquisition
   lane is and how results cluster in late August and early September. Hovering shows the fact, and
   selecting a dot opens the supplier.

Below the fold on the right are "Private funding rounds" (all 11 in twelve months, by date) and
"Changed owner" (the six tracked suppliers whose acquisition closed in twelve months: Dragos, SurePath
AI, Armis, Wiz, CyberArk, Nozomi).

The reasoning: a security leader's first question is "what happened in the market I buy from?" The
dated feed answers it in words, the swim lanes answer it in shape, and the cards give the totals.
The thesis panel, the collection notice and the twelve tables are all gone from the first screen.

On a phone the hero shrinks: the owner's slot becomes a one-line label and the cards become a
three-by-two grid with short labels. "What changed" starts on the first screen.

## The rest of the page

- **Public suppliers, latest reported quarter.** A table of 18 rows, alphabetical by default and
  sortable by revenue, growth or report date. Each row has an eight-quarter revenue sparkline from
  SEC EDGAR (each line on its own scale, with exact values on hover) and the revenue figure. It also
  shows reported growth as a thin neutral bar on one shared scale from -1.5% to +38%, the company's
  fiscal period, the report date, and the company's own headline metric. On a phone each row becomes
  a three-line card.
- **The twelve domains.** Twelve cards in the fixed domain order, three across. Each has the scope
  line, the median reported growth where at least two public suppliers report it, the ownership mix,
  and every supplier in alphabetical order with one fact. The fact is reported growth for a public
  company, the last round for a private one, the owner for a PE-owned one, the acquirer for an
  acquired one, and "Part of Microsoft · no separate revenue" for a segment. Private suppliers with
  nothing published are named once on a single line, so no row is filled with dashes. On a phone
  the cards collapse to their header plus the list of supplier names.
- **Coverage, method and collection.** What is covered and what is not, how a fact gets onto the
  page, and the full collection status. The 28 news sources that could not be read sit in a closed
  disclosure.
- **Supplier panel** (from any name, dot or search result). Every figure with its period and
  source, the SEC quarterly series as bars plus a table of exact dollar values with EDGAR links, all
  dated events, and every source document with publisher, date, period and the quoted excerpt.

## Visual system

- **Type:** Geist for text and Geist Mono for dates, periods and metadata, both from Google Fonts.
  Tabular figures are used wherever numbers line up. Display type is 38px with tight tracking, body
  text is 13.5 to 14px, and metadata is 11.5px mono.
- **Colour:** a light theme only. The page is near-white (#f7f7f5), cards are white with hairline
  borders, ink is near-black, and secondary text is two warm greys. There is one accent blue: #1f5fc8
  for links and #2a78d6 for data marks. Growth bars are slate. No colour means good or bad anywhere.
  Event types are told apart by lane and by label, never by hue. The collection state uses a
  half-filled circle and words, not an alert colour.
- **Spacing and shape:** a 1296px maximum width, 32px gutters on desktop and 16px on a phone, a 20px
  grid gap, 10px corner radius, and hairlines instead of shadows. Density comes from structure (date
  rails, two-line items, mono metadata) rather than small type.

## How it meets each hard constraint

1. **Facts only.** Everything published is a sourced, dated fact from the tracker, or a count or
   median of those facts (the same median `derive.ts` already computes). There are no stances,
   scores or forecasts, and no good or bad colours. Default orders are alphabetical, chronological,
   or the fixed domain order. Sorting by a figure happens only when the reader picks a column. The
   owner's read is a marked, empty slot.
2. **Source and date on every figure.** Every figure is a link to its source document, and the
   tooltip gives the title, publisher, publication date and period. Every row states the period it
   covers. Feed items carry a source tag named by kind (Filing, Company, IR release, Report, EDGAR).
   The supplier panel lists every source with its excerpt.
3. **Honest about gaps.** Each supplier shows the fact it does have. Six private suppliers with no
   published figures (Arctic Wolf, Expel, Aqua, Orca, Sysdig, Cohesity) are named on one line in
   their domain card. Segments say "no separate revenue",
   and Trend Micro and Check Point say why they have no SEC series. Collection status is a small
   header chip linked to a full disclosure at the bottom, which names all 28 unreadable sources and
   their reasons.
4. **Light theme only.** `color-scheme: light only`, with no dark-mode media query.
5. **1440 and 390 pixels.** Both were checked in Chrome with no horizontal scroll: scrollWidth equals
   the viewport at both widths. Body text is at least 13px, tap targets are at least 24px (source
   tags are 24px tall), and everything works from the keyboard. `/` or Cmd+K searches, arrow keys and
   Enter pick a result, Escape closes, sort headers and filter cards are buttons, and the panel traps
   focus and returns it on close. The phone page is about 11,350px tall, against 30,000px today.
6. **No owner byline in the hero.** "Not a news site and not investment advice." appears under the
   lede and again in the footer.
7. **Real data.** `index.html` embeds a JSON block extracted directly from `tracker/suppliers.ts`
   (all 74), `tracker/events.ts` (all 95), `tracker/domains.ts`, the 144 evidence records those cite
   from `evidence.ts`, `generated/edgarFacts.json` and `generated/collectState.json`. All twelve domains
   and the complete 30-day list are included. The only display changes are three. A "+" is added to
   positive growth figures. "billion" and "million" become B and M with no rounding, following
   `abbreviateDollar` in `derive.ts`. ISO dates are written as "26 Sep 2026". Funding amounts and
   valuations in the funding list are taken verbatim from the event text, including qualifiers such as
   "over".

## What I would do next with more time

- Give each domain its own page at the same density: a timeline per domain and every supplier's facts
  side by side. That is the "which two or three vendors are on solid footing" view the owner needs,
  with the judgment left to him.
- Add a reader-chosen comparison: pick three suppliers and see their SEC revenue on one indexed axis.
- Pair each results event with its SEC filing into one row, which would shorten the feed by about a
  third without losing an item.
- Move the hard-coded "16 SEC filers" count into the data export, so the status sentence is derived
  the same way `runStatus.ts` derives it.
- Run a proper accessibility audit, adding keyboard access to individual timeline dots and a
  table view of the swim-lane chart.
