# Blind review of the four front-page designs

The scores follow the brief's weights. A clear breach of a hard constraint caps the constraints score at 4.

| Design | First screen | Look | Density | Constraints | Phone | Weighted total / 110 |
|---|---:|---:|---:|---:|---:|---:|
| A | 9 | 8 | 9 | 3 | 7 | 82 |
| B | 8 | 6 | 8 | 3 | 6 | 70 |
| C | 6 | 9 | 7 | 8 | 6 | 81 |
| D | 5 | 8 | 6 | 8 | 8 | 75 |

## A

The first screen gives a reader a usable picture quickly: six kinds of activity with 12-month counts and 30-day counts, a dated change feed, and a timeline that shows when each kind occurred. The owner-read slot is plainly reserved, and the source buttons sit beside the change statements. The restrained type, spacing, and light blue marks make the dense desktop view easier to scan than a table of mostly empty cells.

The page becomes very long on a phone because it puts the full change feed, timeline, funding list, public-company table, and all twelve domains in one scroll. The domain cards also compress unlike measures into the same small right-hand column; a growth rate, a funding round, and an ownership statement can look like comparable entries. The timeline's small, crowded dots are hard to distinguish even on desktop.

There are clear constraint breaches. In **The twelve domains**, `renderDomains()` prints a computed "Median reported revenue growth" chip without a linked source or a reporting period; it also mixes companies' latest quarters. The same section labels every supplier without a selected fact "Private, no published figures," although the tracker only establishes that this page has no selected figure, and those suppliers are not all necessarily private. In **Twelve months of tracked events**, each SVG dot is an 8-pixel circle with mouse-only hover and a click that opens a supplier drawer, so it misses the 24-pixel tap target and keyboard requirements and does not take the reader straight to that event's source. The **Public suppliers** sparklines have the same source-access problem for their individual quarter figures.

## B

The first screen pairs a dated event ledger with reported revenue growth for public suppliers. Alphabetical ordering is the default in the growth chart, and value sorting is a reader choice. The chart's latest and previous-quarter marks give a useful comparison, while the ledger keeps event type, supplier, date, and a source link on each row.

The page resembles a dense research worksheet more than a calm product page: the long introduction, collection warning, category chips, event ledger, and 17-row growth plot compete at the top. At 390 pixels, the chart comes after the full event list, so a reader must scroll far to reach the cross-company financial view. The supplier board collapses every domain on the phone, which makes the rest of the market hard to discover.

There are clear constraint breaches in **Reported revenue growth, latest quarter**. The prior-quarter hollow dots display their exact figures and periods only through a hover tooltip; they are not keyboard-focusable, are much smaller than 24 pixels, and do not link to the prior source. The latest-quarter dots have the same hover and target-size problem, although their percentages also appear as source-linked text at the row end. In **The board**, `factLine()` shortens some company facts to a month or omits an ownership as-of date, so the visible fact does not always retain the exact period it covers.

## C

The visual system is the calmest of the four: large, readable type, a soft background, clear teal links, and enough white space around each fact. The opening card shows two recent reported results and two other recent events, each with a source link and source date. The domain browser sorts domains and suppliers alphabetically, and its fact cells keep the source one click away.

The first screen tells the reader how many records, results, and acquisitions were collected, but gives little sense of how the market is moving across domains or companies. The four opening items are deliberately split into two results and two other events, so they are neither a chronological four-item feed nor a cross-market comparison. On a phone, the large hero takes most of the first screen, and the complete 25-record list later makes the page long.

I found no clear hard-constraint breach in the visible design or prototype. The **Results and other changes** card should still say more plainly that its four items are a mechanically chosen sample, since the split can look like an editorial judgment about what matters.

## D

The desktop and phone layouts are orderly. The phone turns the change-type filter into a full-width select, shows three readable change records, and keeps a supplier search and domain selector close to the supplier list. The supplier rows give a figure, its reporting period, and a way to open the underlying record without filling empty cases with dashes.

The first screen is too narrow a market picture for the stated reader: it shows four recent company changes on desktop and three on the phone, with no cross-company results or domain comparison until farther down. The headline and short deck take prominent space but add little beyond the page name. The desktop supplier view begins with Endpoint and XDR, while the navigation itself is alphabetical, which makes that domain seem preferred without saying why.

I found no clear hard-constraint breach in the visible design or prototype. The **Explore a security domain** default should be neutral or follow the alphabetical domain list so its first selection cannot be read as an implicit priority.

## Choice

**Winner: A.** Its first screen does the best job of showing both what changed and the shape of activity across the market. It wins as a direction for the rebuild only if the source, date, and interaction breaches above are corrected.

**Runner-up: C.** Its typography, colour, and source treatment make it the strongest visual reference. Its opening view needs a more useful comparison across suppliers or domains before it can serve as the main market instrument.

## What to borrow for A

- From **B**, borrow the alphabetical, reader-sortable latest-quarter growth comparison. It puts actual reported company performance beside A's event counts.
- From **C**, borrow the larger type, quieter spacing, and fact cells that show the period and keep the source link attached to the value.
- From **D**, borrow the phone's compact change-type select and its one-domain-at-a-time supplier browser, which make the long record manageable.

## Five fixes before A ships

1. Remove the unlinked median chips in **The twelve domains**, or give each calculation a clear set of linked inputs and their distinct reporting periods. Do not present mixed-quarter growth as a single current domain figure.
2. Rebuild **Twelve months of tracked events** so every event has a keyboard-focusable target of at least 24 pixels and its source is reachable in one tap or click. Apply the same source and keyboard rule to the quarter values behind the **Public suppliers** sparklines.
3. Replace "Private, no published figures" in **The twelve domains** with a precise tracker-gap statement for each supplier. Keep public, segment, acquired, and private classifications accurate.
4. Shorten the 390-pixel route through the page. Keep the initial change feed brief, add an explicit way to see the rest, and show one domain at a time while preserving access to all twelve domains and all 25 recent records.
5. Keep exact source periods and dates on compact facts. In **The twelve domains**, `oneFact()` reduces some company metrics and ownership dates to a month; the visible fact or its one-tap detail must retain the actual period and source.
