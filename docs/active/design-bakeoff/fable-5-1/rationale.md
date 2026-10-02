# Rationale — Fable 5.1 entry

**Artifact:** `SEC-MARKET-DESIGN-BAKEOFF-001` / contestant `fable-5-1` · 2026-10-02
**Files:** `research.md`, `index.html`, this page, and the four renders `shot-1440.png`,
`shot-390.png`, `shot-fold-1440.png`, `shot-fold-390.png`.

## The idea

The front page is a dated ledger of what changed, next to one chart of the only figure that is
comparable across companies, with the full supplier board underneath. Every number on the page is
a link to its source and carries its period; nothing is coloured, ordered or scored to suggest
what a fact means. It should read like a changelog crossed with a filings index, in the register
of Linear or Vercel rather than a research report.

## Information architecture

**First screen at 1440 (see `shot-fold-1440.png`).** A one-line masthead with section anchors and
a mono status stamp ("Checked 26 Sep 26 · incomplete"). A two-line title, a three-line lede ending
in "Not a news site and not investment advice", a mono strip of derived counts (74 suppliers, 12
domains, 18 public, 22 private, 15 PE-owned, 9 segments, 10 acquired, 95 dated events, 144 source
documents), and a one-line collection status with a link to the detail. Then two columns:

- Left, **What changed**: 17 dated events in the 30 days to 26 Sep 2026, newest first, each with
  a date, a monochrome type tag, the supplier and its domain, one or two lines of the fact, and a
  link labelled by source class (Filing, Release, Company). A 30-day / 12-month switch and
  per-type chips with counts filter it. Ten rows are visible before scrolling.
- Right, **Reported revenue growth, latest quarter**: the 17 public reporters on one alphabetical
  dot plot. The solid dot is the latest reported year-over-year growth; the hollow dot is the
  quarter before, so the reader sees both the spread and the direction without a ranking. A
  "By value" button reorders at the reader's request. Trend Micro, which reports ARR but no
  comparable quarterly revenue, is named under the chart with what it does report.
- Under the chart, a dashed **owner's read** slot, stating plainly that none is published for
  this week. I did not write its content.

**Second screen onward.** **The board**: twelve domain groups in two balanced columns, each with
its scope sentence and a mix line ("7 suppliers · 2 public · 3 PE-owned · 2 acquired"), and one
row per supplier in alphabetical order. Each row has the same three regions: name with a kind
label, a fact line, and an event count with the latest date. The fact line is built from whatever
the supplier publishes, in a fixed priority: reported revenue and growth with its period (plus a
sparkline of filed quarterly revenue for the 14 SEC filers), the company's own stated metric, the
last funding round, then ownership. A private company with no figures reads "Private company; no
comparable public figures in our record" once, not as a row of dashes. Clicking a name opens the
full record: every figure with its period and release date, the ownership sentence, the dated
events for that supplier, a collection note if its news page failed this run, and the full EDGAR
quarter series. A filter box (press `/`) narrows the board by name. **Coverage and gaps** carries
the collection status, the 28 suppliers whose news pages could not be read with a plain reason
each, what is covered and what is not. **Sources and method** states where figures come from, how
to read one, and what the machine does not do, with counts of source documents by class.

**On a phone (390).** Same order. The board collapses to twelve domain headers so the page is
about 6,100 pixels, with the ledger and chart first; the first supplier appears in the first
ledger row on the first screen. No horizontal scroll at either width (verified by measuring
`scrollWidth`).

## Visual system

- **Type.** Inter for text with `cv01`, `ss03` and tabular figures; 14px base, 13px in the ledger
  and board, 26px title. JetBrains Mono at 11–12.5px for dates, tickers, figures, counts, tags and
  status, so anything that is data reads as data. Weights 400, 500 and 600 only.
- **Colour.** White ground, two greys for surfaces (`#f6f7f9`, `#eef0f3`), two hairlines, three
  text inks (near-black, slate, grey) and one accent blue (`#2457d6`) used only for links, the
  active window button and the latest point of a sparkline. No red, green, warm or cool colouring
  of any value. Tags are grey with text.
- **Spacing.** 32px gutters at desktop, 16px on a phone; 8px row padding with 1px dividers; 22px
  between sections. Density comes from small mono metadata and fixed column roles, not from
  cramming.
- **Decoration.** None. The only non-text marks are the dots, the sparklines and the disclosure
  chevrons.

## The hard constraints

1. **Facts only.** No stance, score, rank, forecast, sentiment colour or "why it matters" line
   anywhere. Default order is alphabetical in the board and the chart; the ledger is by date. The
   owner's read slot is marked and empty.
2. **Source and date on every figure.** Every figure is an `<a>` to its source document. Hover or
   focus shows the document title, publisher, publication date and period; click opens it. The
   period is printed inline next to each figure as well. Sparklines link to the latest filing and
   name the quarter range; each quarter in the expanded record links to its own filing.
3. **Honest about gaps.** Private and segment suppliers show the facts they do publish or one
   plain sentence. The collection state is one line under the lede, with the 28 failed reads and
   their reasons in a closed disclosure in the coverage section, and a note inside each affected
   supplier's record. A quiet company and a failed read never look the same.
4. **Light theme only.** `color-scheme: light only`, no dark-mode media query, explicit white
   background.
5. **1440 and 390.** Rendered at both; no horizontal scroll; 13px minimum body type (11px only
   for mono labels); every button, chip, link row and disclosure is at least 24px tall; the whole
   page works from the keyboard (tab order follows reading order, `/` focuses the filter, `Esc`
   closes the hover card and clears the filter, native `<details>` for the domains).
6. **No owner byline in the hero.** None. "Not a news site and not investment advice." is in the
   lede and the footer.
7. **Real data.** The page embeds the 74 suppliers, 12 domains, 95 events, 144 evidence records,
   the EDGAR quarter series for 14 filers, and the collection state, extracted from
   `web/src/data/` without edits. Figures are shown as recorded; dollar amounts are abbreviated
   (billion → B, million → M) as `derive.ts` already does, and a positive growth figure gets a
   leading plus sign for consistency. All twelve domains and the complete event list are present.

## With more time

- Render the EDGAR sparklines for the alphabetical dot plot too, so the chart carries eight
  quarters per filer rather than two points.
- A supplier page per record, reachable from the board, carrying the same fact line and events.
- Keyboard navigation between rows (j/k) and a command palette for jumping to a supplier.
- Self-hosted fonts and a build step that generates this page from `tracker.json`, in line with
  the carry-forward in the brief.
- Let the reader pick the ledger window by date, not only 30 days or 12 months.
