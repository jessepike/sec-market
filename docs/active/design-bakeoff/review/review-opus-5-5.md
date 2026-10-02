# Blind review: Security Market Pulse front page (reviewer: Opus 5.5)

Read from the point of view of a chief information security officer opening the page for the first time. Every design was checked against its four screenshots and its `index.html` (markup, styles and script).

## Scores

| Design | First screen (×3) | Look (×3) | Density (×2) | Constraints (×2) | Phone (×1) | Weighted total (of 110) |
|---|---|---|---|---|---|---|
| A | 8 | 8 | 9 | 6 | 6 | **84** |
| B | 9 | 7 | 9 | 4 (capped) | 7 | **81** |
| C | 5 | 8 | 5 | 8 | 7 | **72** |
| D | 5 | 7 | 4 | 8 | 9 | **69** |

## Design A

**Strongest quality.** A gives the reader the shape of the market's activity before they scroll. The six-tile strip under the hero ("Acquisitions & divestitures 28 · 3 in last 30 days", "Funding rounds 11", "Leadership changes 18" and so on) carries a twelve-month bar per tile, and the tiles filter the feed. Next to "What changed" sits "Twelve months of tracked events", a dot timeline by event type with the 30-day window shaded, then "Private funding rounds" and "Changed owner". Further down, "Public suppliers, latest reported quarter" puts revenue, growth with a neutral grey bar on one shared scale, an EDGAR sparkline, period and reported date, and the company's own metric on one row per company, alphabetical by default. The twelve domain cards then cover all 74 suppliers with one sourced fact each. The visual system (Geist, warm off-white, one blue, mono for metadata) is the closest of the four to the Linear and Zed register, and the keyboard work is real: "/" opens a supplier finder, and a supplier drawer opens with a focus trap and a full source list.

**Biggest weakness.** The thing a security leader most wants to know, who is growing and who is not, sits below the fold in the public table, while the top-right of the first screen goes to an empty dashed "Owner's read · Reserved" box. "What changed" renders all 25 items in one card, so on desktop that left column runs to roughly 2,000 pixels and pushes everything else down. On a phone the page is 11,352 pixels tall, and all 25 feed items come before the first supplier row.

**Constraint issues.**
- In each card under "The twelve domains", the chip "Median reported revenue growth +26% · 3 public" (and "+27.5% · 6 public" for Network and SASE, "+9.8%" for Vulnerability and exposure management) is a machine-computed figure with no source link and no period. It mixes fiscal quarters (Palo Alto's Q4 FY2026 with others' Q2 2026) and is rounded in code to two decimals. This breaks "every figure keeps its source and its date" unless the chip gains a period and a method link.
- The section copy "with the one fact that best describes where it stands on the record" reads as editorial selection. The choice is actually a fixed rule in code (growth, then metric, then last round, then ownership), and the copy should say that.
- The supplier-name buttons (`.sup`, `all:unset`) render at about 21 pixels tall, under the 24-pixel tap minimum. The timeline dots are 8-pixel, mouse-only targets with no keyboard focus.
- Metric periods pass through in mixed formats: "Q2 2026, ended 2026-06-30" next to "Quarter ended July 31, 2026".
- I found no dark theme, no owner name, no good-or-bad colour and no default ranking. "Not a news site and not investment advice." sits in the hero.

## Design B

**Strongest quality.** B has the best market picture on the first screen. "Reported revenue growth, latest quarter" is a dot plot of the 17 public suppliers: a solid dot for the latest quarter, a hollow dot for the quarter before, a connecting line, the exact figure at the right edge linked to its source, A–Z by default, and "By value" only when the reader asks. A security leader sees who grew and who slowed in one glance, and in neutral ink. Beside it, "What changed" is a compact ledger (date, type tag, supplier with its domain, text, a "Filing ↗" link) with type chips and a 30-day or 12-month switch. Below it, "The board" lists all 74 suppliers in two balanced columns with revenue, growth, own metric, a sparkline and an "N events · date" count per row. The closing paragraph "What the machine does not do" is the clearest statement of the D-76 rule on any of the four pages.

**Biggest weakness.** It looks like a very good ledger rather than a product. Mono type, 12 to 13-pixel text and hairline rules make the board read like a spreadsheet at 1440, which is the "spreadsheet dump" register the owner asked to leave behind. The "COLLECTION INCOMPLETE" pill and its sentence sit in the first screen under the hero, which the owner named as a problem in the current site. Ledger text is clipped to two lines with an ellipsis ("EVP Raj Judge…"), so the first screen shows partial facts.

**Constraint breaches.**
- **Relabelled figure (clear breach, caps this score at 4).** `factLine()` replaces the valuation text "Unicorn status (>$1B implied)" with ">$1B". On the board this shows as, for example, Upwind "Series B $250M at >$1B Jan 2026". Dropping "implied" turns an implied valuation into what reads as a stated one.
- **Rounded figures.** `usd()` turns exact EDGAR dollar values into "$1.47B" or "$220.5M" in the sparkline hover text and in the expanded row's "Reported revenue by quarter, from EDGAR" line. The brief says not to round differently.
- **Probably incomplete "what changed".** The ledger counts 17 dated events for 27 Aug to 26 Sep. The other three designs show 25 for the same window, because they include the eight latest-quarter SEC filings. Check against `derive.ts`: if the filings are part of the canonical window, B does not show the complete list.
- The type chips are ordered by count, largest first ("Results 6, Acquisition 3, Leadership 3…"). This is not a supplier ranking, but alphabetical is the safe default.
- The dot-plot scale is hard-clamped to -5% to 40%, so any future value outside that range would be drawn pinned to the edge with no warning.
- The supplier-name buttons in the board (`.name`, `all:unset`) are about 18 pixels tall.

## Design C

**Strongest quality.** C is the most polished piece of graphic design. It pairs Plus Jakarta Sans headings with IBM Plex Sans body, uses a quiet teal palette, and gives every fact a three-line stack: label, value, then period ("Reported revenue / $3.41 billion / Q4 FY2026"). Figures appear verbatim with no abbreviation, so nothing can be rounded or relabelled. The domain browser is a proper keyboard tablist with arrow, Home and End keys, and tap targets are generous (domain buttons are 40 pixels, source links 27).

**Biggest weakness.** The first screen tells a security leader very little about the market. Most of the left half goes to a 56-pixel headline, "What security companies reported.", plus two buttons ("Explore the domains", "See every recent change") and three counts (25, 6, 3). The right card shows four events. "The market by domain" shows one domain at a time, so seeing the whole market takes twelve clicks. There is no growth comparison anywhere on the page. It reads as a well-made 2020 SaaS landing page rather than an intelligence-dense instrument.

**Constraint issues.**
- The hero card "Results and other changes" follows a "two latest results and two latest other events" rule, so its dates run Sep 10, Sep 3, Sep 24, Sep 23. That is editorial curation, and to a reader it looks like a sorting bug.
- "Not a news site and not investment advice." appears only inside "How to read this record" near the bottom. It is visible, but only just.
- Segment rows say "Company segment" but never name the parent. For segments without a metric, `renderSupplier()` skips ownership and the row falls back to "No comparable financial figure in this tracker." The carry-forward requires segment rows to name their parent company.
- The footer is a full-width dark band (`.site-foot{background:var(--ink)}`, #183136). This is not a dark mode, but it goes against the light-only direction.
- Filing rows mix formats: "Filed 10-Q for the quarter ended 2026-07-31." under a "Sep 10, 2026" date.

## Design D

**Strongest quality.** D is the best phone page and the most disciplined about judgment. At 390 pixels the whole page is 2,439 pixels. A select replaces the type filter, three events are followed by "Read all 25 changes", a select replaces the domain list, and the supplier cards show a large growth figure, its period ("Q2 FY2027 · ended 31 Jul 2026") and "Reported 26 Aug 2026". Every control has a minimum height of 28 pixels or more. The coverage dialog says outright: "No growth medians, sentiment scores, forecasts or supplier rankings are published here." Source links name the publisher and date ("Zscaler, Inc. ↗ 24 Sept 2026") instead of a generic "Source".

**Biggest weakness.** D is too thin for the brief's "intelligence dense". The 1440 page is only about 1,870 pixels tall: four events, a type-count sidebar, and eight suppliers per page from one domain. Everything else sits behind a modal, a pager or a domain click. A security leader leaves the first screen knowing four recent events and nothing about who is growing. The look is clean but generic, with large empty areas in the "In this record" sidebar and between sections.

**Constraint issues.**
- The default domain is hard-coded to Endpoint and XDR (`currentDomain='endpoint-xdr'`), not the alphabetical first (AI security). The coverage dialog discloses "no ranking implied", but a non-alphabetical default is the pattern the brief warns about.
- The complete "what changed" list exists only inside the "Read all 25 changes" dialog. It is there, but it is not on the page.
- The "Most recent first" pill is static text styled like a control.
- Filing rows use ISO dates ("quarter ended 2026-07-31").

## Winner and runner-up

**Winner: A.** It is the only design that is dense, calm and complete together: an activity picture on the first screen, a sourced public-company table with sparklines, all twelve domains visible without clicks, a real supplier drawer and keyboard finder, and a light, quiet visual system. Its constraint problems (the median chips, tap sizes) are local and quick to fix. B's are mistakes in how figures are written.

**Runner-up: B.** Its growth dot plot is the single best answer to "who is growing" on any page, and the board is the most information per square inch. It loses on look (ledger-like) and on a clear relabelling breach plus rounding of EDGAR figures.

## What to borrow for A

From B:
- The "Reported revenue growth, latest quarter" dot plot, with latest and prior quarter, A–Z default, a "By value" toggle and neutral ink. Put it in A's first screen in place of the empty owner's-read box, or beside the timeline, so growth reaches the first screen.
- The "What the machine does not do" paragraph, and the per-row "N events · last date" link that opens the supplier record.

From C:
- The label, value and period stack for every fact, with figures shown verbatim (for example "$3.41 billion" under "Reported revenue" and "Q4 FY2026" beneath).
- C's tap-target sizing (40-pixel domain buttons, 27-pixel source links) and its keyboard tablist pattern.

From D:
- The phone economy: three events plus "Read all 25", and selects for the type and domain filters.
- Source links labelled with the publisher and date instead of "Company ↗".
- The explicit coverage sentence that lists are alphabetical and that no medians, scores or rankings are published.

## Five fixes A needs before it ships

1. **Put reported growth on the first screen.** Add B-style growth dots (A–Z default) to the first screen. Shrink the empty "Owner's read · Reserved" box to a one-line slot until the owner writes something.
2. **Resolve the median chips in the domain cards.** Either remove "Median reported revenue growth …", or give each one an explicit period window, the list of constituent companies and a link to the method. As shipped, it is an unsourced machine figure that mixes fiscal quarters.
3. **Cap "What changed" on the page.** Show about eight items, then "Show all 25", and fold each SEC-filing row under its matching results row. This shortens the desktop column and brings the 11,352-pixel phone page down, with the first supplier row on the first phone screen as the carry-forward requires.
4. **Meet the tap and keyboard rules.** Supplier-name buttons need a minimum height of 24 pixels. Timeline dots need keyboard focus or a list equivalent. Sort buttons that are hidden on phone (`.ptable thead` is hidden at 760 pixels) must leave the tab order.
5. **Normalise the data presentation to the carry-forward.** Show growth to one decimal from reported revenue. Show every own-metric and ownership fact with an as-of date in one date format, not "2026-06-30" next to "July 31, 2026". Name the parent on segment rows in the drawer and table as well as the domain cards. Rewrite "the one fact that best describes where it stands" as the fixed rule it actually is.
