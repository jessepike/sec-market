# Blind review of the four front-page redesigns

Reviewer: Fable 5.1. Reviewed on 2026-10-02 against `brief.md` and `product-core.md`, from the seat of a
chief information security officer opening the page for the first time. Every design was checked at
1440 and 390 pixels in the renders provided, and each prototype's HTML and script were read to check
the data rules, the default orders, and the interactions.

## Scores

Weighted total is first screen × 3, look × 3, density × 2, constraints × 2, phone × 1, out of 110.

| Design | First screen | Look | Density | Constraints | Phone | Weighted total |
|---|---|---|---|---|---|---|
| A | 9 | 8 | 9 | 8 | 7 | 92 |
| B | 8 | 6 | 10 | 8 | 8 | 86 |
| C | 5 | 7 | 4 | 6 | 5 | 61 |
| D | 6 | 8 | 4 | 7 | 9 | 73 |

## Design A

Strongest quality. The first screen is the market picture the brief asks for. Under the headline sits a
six-lane strip of event counts (acquisitions and divestitures 28, funding rounds 11, results 19,
restructuring 10, debt 8, leadership 18) with a monthly mini histogram in each lane and the 30-day count
underneath, and every lane is a filter for the feed beside it. To the right is a twelve-month dot
timeline of all 94 events by type with the last 30 days shaded, and below the fold the public-supplier
table carries a quarterly revenue sparkline, revenue, growth on a shared grey bar with a zero line, the
period and the reported date, and the company's own metric with its own period. The twelve domain cards
give every supplier exactly one fact (reported growth, last round, or who owns it) with the period
beside it, and private suppliers with nothing publishable are named in a single line rather than given a
row of dashes. The type is Geist on a warm grey ground and the whole thing is calm.

Biggest weakness. The phone page is the tallest of the four at 11,352 pixels, because the full 25-item
feed, all 18 public-supplier cards and twelve domain summaries all render in one column. The feed also
doubles up filings and results: Zscaler, Netskope and SailPoint each appear as a "SEC filing: filed its
10-Q" receipt row and again as a results row on the same day, which pads the list and makes a reader
check whether something new happened. The timeline dots and the sparkline tooltips are hover-only, so a
keyboard or touch reader cannot reach the fact behind a dot without opening the supplier.

Constraint checks. One soft breach of constraint 2: the domain cards carry a chip such as "Median
reported revenue growth +26% · 3 public" (Endpoint and XDR) or "+13.9% · 2 public" (Identity). That is a
figure the machine computed, shown with no source link and no period, and in the two-supplier domains it
is the average of two numbers rather than a median. It also invites a domain-against-domain comparison
that no company reported. No judgment colours, no ranking, no default order by performance (the table is
alphabetical with reader-chosen sorts, `aria-sort` on the name column), light theme forced with
`color-scheme: light`, no owner name anywhere, "Not a news site and not investment advice" under the
lede and in the footer, no horizontal scroll at 390. Two things to watch rather than breaches: the
"Private funding rounds" panel pulls the amount, valuation and lead investor out of the event prose with
regular expressions (the `funds` block in the script), which is a route to a wrong figure if the prose
changes shape; and the domain cards run in tracker order rather than alphabetical, which does not imply a
ranking but is not the safe default the brief names.

## Design B

Strongest quality. It is the densest page of the four and the most explicit about its rules. The
first-screen dot plot, "Reported revenue growth, latest quarter", puts all 17 public suppliers that report
quarterly revenue on one axis, alphabetical by default, with a hollow dot for the quarter before so a
reader sees at a glance who moved and which way, and a "By value" toggle that is clearly the reader's
choice. The board below gives every supplier a one-line fact set with the period in mono, an inline
sparkline, and a count of dated events with the last date ("4 events · 1 Sep 26"), and a click opens the
record and the EDGAR quarters in place. The "Sources and method" block states plainly what the machine
does not do and counts the source documents by class.

Biggest weakness. It does not look like the companies the brief names. The headline is 26 pixels (20 on
the phone), the masthead facts are a mono string of numbers, and the ledger clamps every event to two
lines with an ellipsis ("EVP Raj Judge...", "closed on September 1...") so a reader scanning the first
screen gets half-sentences until they click. It reads like a good data terminal rather than a calm
product page, and the "COLLECTION INCOMPLETE" pill is the fourth line of the hero, which is closer to
dominating the first screen than the brief wants.

Constraint checks. No machine judgment anywhere, and the page says so in words. Two factual wording
risks. The status line says "SEC filings read for all 14 filers", derived from the length of the EDGAR
facts array, while the same board lists JFrog and Commvault as public with reported revenue and no SEC
series; design A describes the same data as 16 filers with two not yet collected, so B's "all" is
probably overstated. On the board, Upwind's last round is shown as "Series B $250M at >$1B", where the
script rewrites the data's "Unicorn status (>$1B implied)" into a valuation figure and drops the word
"implied" (the `factLine` function, `lastRound` branch). That is a small alteration of a figure's
qualifier and should be reversed. Otherwise clean: alphabetical defaults, hover card also opens on focus,
light only, no owner name, the not-advice line in the lede and footer, no horizontal scroll at 390, the
board collapses to domain summaries on the phone.

## Design C

Strongest quality. It is the most inviting at first glance. The teal palette, the generous white space,
and the "Results and other changes" card with a date badge, the supplier and type in bold, the sentence,
and a "Source" link with the period beside it ("Quarter ended July 31, 2026") is the clearest single
event row in the bake-off. The domain browser is a proper tab list with arrow-key navigation, and each
supplier gets labelled fact pairs (label, value, period) that are easy to read one at a time.

Biggest weakness. The first screen is a landing page, not an instrument. A security leader sees three
counts (25 dated records, 6 reported results, 3 acquisition events), two buttons, and four events, and
has to scroll or click to learn anything about who is growing or who was bought. The headline's letter
spacing of -0.067em collapses the word spaces in the render, so it reads "Whatsecurity companiesreported."
at 1440. Density is low throughout: one domain at a time, two-column facts with 16 to 20 pixel gaps,
and a 30-day list where each row is about a hundred pixels tall, so 25 rows take most of the page.

Constraint checks. At 390 the change list's date column is 62 pixels wide with `white-space: nowrap`,
so "Sep 24, 2026" runs into the type label and renders as "Sep 24, 2026Leadership" and "Aug 28, 2026EC
filing" on every row of "What changed in the last 30 days". That is a visible phone defect, though not a
horizontal page scroll. The footer is a dark navy band (`.site-foot{background:var(--ink)}`), which is not
a dark theme but is the one dark surface in the four designs. "Not a news site and not investment
advice" exists only as the last paragraph of "How to read this record" near the bottom, and is not in the
footer or hero, which is a weak reading of constraint 6. Supplier naming is inconsistent because the
suffix strip runs once: "Tenable Holdings" and "CrowdStrike Holdings" in the list, "Tenable" elsewhere.
No machine judgment, no ranking, sources and periods on every figure, no owner name.

## Design D

Strongest quality. It is the calmest and the most finished-looking page, and the best on the phone. The
Manrope type, the soft blue, the single rounded panel for "What changed" with a filter rail of counts
beside it, and the large "+26% revenue YoY / Q2 FY2027 · ended 31 Jul 2026 / Reported 26 Aug 2026"
treatment on each public supplier read well and leave no doubt about the period. Source links name the
publisher and its date ("Zscaler, Inc. ↗ 24 Sept 2026"). The 390 page is 2,439 pixels long, uses native
selects for the type and domain filters, and the supplier record is a native dialog.

Biggest weakness. It achieves its calm by hiding the information. The front page shows four of 25
changes and puts the rest behind a modal ("Read all 25 changes"), shows eight suppliers at a time with a
Previous and Next pager, offers no cross-company view of growth at all, and gives every private, PE-owned
and segment supplier the same two lines, "No financial figures collected. Ownership source available."
That is the dash problem in words: Sophos (Thoma Bravo), Microsoft Defender for Endpoint (part of
Microsoft) and Wiz (acquired by Google) all have a publishable fact that A, B and C show on the row and
D hides behind a chevron. A security leader cannot answer "who is on solid footing in this domain" from
D's first page.

Constraint checks. No machine judgment, and the coverage dialog states that no medians, scores,
forecasts or rankings are published. Sources and periods are present on every figure shown. The complete
"what changed" list is included only inside the dialog, which strains the brief's instruction to include
the complete list even in a subset prototype; the full-page render shows four items. Segment rows show
the parent only as a ticker ("Segment / MSFT") rather than naming it, which the carry-forward in brief
section 6a requires. Light only, no owner name, the not-advice line in bold in the footer, no horizontal
scroll at 390, tap targets at or above 28 pixels. The default domain is Endpoint and XDR while the
navigation is alphabetical; the coverage dialog says so, and it implies no ranking.

## Winner and runner-up

Winner: A. It is the only one of the four where a security leader gets the shape of the market in the
first screen, how much happened of each kind, when, and what the latest items are, and it keeps that
density through the public table and the domain cards without looking like a spreadsheet. Its breaches
are small and fixable.

Runner-up: B. It is the most rigorous page and its growth dot plot is the single best element in the
bake-off, but it is plain to the point of austerity and truncates the facts on the first screen. If the
owner wanted the instrument over the credibility asset, B would be the pick; the brief asks for both.

## What to borrow for A

From B: the growth dot plot with the quarter-before dot, placed where A's "Twelve months of tracked
events" chart sits or directly under the stat strip, because it answers "who is growing" faster than a
table of sparklines; and B's per-supplier "N events · last date" column in the domain cards, which tells
a reader at a glance which suppliers have been quiet.

From C: the event row's explicit period line under results and restructuring items ("Quarter ended July
31, 2026") rather than relying on the source chip's title attribute; and the labelled fact triplet
(label, value, period) for the supplier drawer, which is clearer than A's two-column fact grid.

From D: the publisher name and date on each source link in the feed ("Zscaler, Inc. · 24 Sept 2026")
in place of A's class label ("Filing", "Company"), and D's one-line note under the filter counts,
"Counts reflect this collection, not total market activity", which A's stat strip needs.

## Five fixes A needs before it ships

1. Remove the per-domain "Median reported revenue growth" chips, or replace them with a statement that
   carries no computed figure ("4 of 6 report quarterly revenue") and let each growth figure link to its
   own filing. A machine-computed, unsourced, period-free number is the one thing on the page that fails
   constraint 2, and in the two-supplier domains it is not even a median.
2. Cut the phone page length by at least a third. Show the first eight feed items with "Show all 25",
   keep the domain cards collapsed as they are, and collapse the public-supplier cards to name, growth
   and period with the rest in the drawer. Keep the first supplier row inside the first phone screen per
   brief section 6a.
3. Make the timeline dots and the sparkline hover facts reachable without a mouse: render each dot as a
   focusable element with the fact in its accessible name, or add a "list these events" control under the
   chart, and make the sparkline's quarterly values visible on focus.
4. Stop extracting the funding amount, valuation and lead investor from event prose with regular
   expressions in the "Private funding rounds" panel. Use the structured `lastRound` fields and show the
   event sentence when a field is missing, so no figure on the page is a parse of a sentence. Apply the
   same rule to the "Changed owner" labels.
5. Fold each SEC filing receipt into its results row when both exist for the same supplier and period
   (one row: results text, then "10-Q filed 10 Sep · EDGAR"), and show a filing on its own only when no
   results row exists. Strip the "(derived)" label from the 10-K text, order the domain cards
   alphabetically or state the order, and carry the section 6a items through the rebuild: growth to one
   decimal from reported revenue, an as-of date on every own metric and ownership fact with a build gate,
   and the parent company named on every segment row.
