# Design bake-off brief — Security Market Pulse front page

**Artifact ID:** `SEC-MARKET-DESIGN-BAKEOFF-001` v0.1
**Requested by:** the owner, 2026-10-02: "it looks terrible ... let's do a bake-off ... each of the
models come up with their fresh redesign ... do some research ... something forward looking ... easy
on the eyes, easily digestible, and intelligence dense."
**Contestants:** GPT-6 Sol, GPT-6 Astra, Claude Opus 5.5. Each works alone. Do not read the other
contestants' directories under `docs/active/design-bakeoff/`.

## 1. The job

Design a fresh front page for https://securitymarketpulse.com, from first principles, and build it
as a working prototype on the real data. This is a redesign, not a fix pass. You are free to change
the information architecture, section order, what is on the first screen, the visual system, and how
the data is shown (tables, cards, small multiples, sparklines, charts, timelines, filters, anything).

The owner's reference points are the design-forward technology companies: Cloudflare, Stripe, and
the like (Linear, Vercel, Ramp and similar are fair game too). He wants it to be:

- **Easy on the eyes.** Calm, confident, modern. Nothing that looks like a spreadsheet dump or an
  error log.
- **Easily digestible.** A security leader should understand what is going on in the market within
  the first screen and the first thirty seconds.
- **Intelligence dense.** Real information per square inch. Density through good structure, not
  through cramming.
- **Forward looking.** It should feel like a 2026 product, not a 2015 research page.

## 2. Research first

Before designing, do real research and write it down. Look at how leading companies present dense
data and market intelligence well: for example Stripe's and Cloudflare's product and report pages
(Cloudflare Radar is directly relevant), Linear's changelog and marketing pages, financial and
market-data products that handle many companies at once (for example Koyfin, the Financial Times'
data pages, Pitchbook-style company lists), and well-regarded data journalism. Pull out the specific
patterns that would work here and the ones that would not. Cite what you looked at.

## 3. Who reads it and what it is for

Read `docs/active/product-core.md` in full. In short: written first for security leaders (chief
information security officers, security architects), then for the people who advise and sell to
them. It is a credibility asset for the owner and an instrument he uses to answer "in this domain,
which vendors are on solid footing, and what does the evidence say". Investors are not the audience.
No investment advice.

## 4. Hard constraints (non-negotiable)

1. **Facts only from the machine (decision D-76).** The page publishes sourced, dated facts:
   reported revenue growth, a company's own metrics, funding rounds, acquisitions, divestitures,
   layoffs, debt, filings, leadership changes. It must not publish machine-made judgments: no
   stances, scores, rankings, "winners/losers", forecasts, sentiment colours that imply good or bad,
   or interpretation of what a fact means. Sorting by a column the reader chooses is fine; a default
   order that implies a ranking is not (alphabetical is the safe default). You may reserve a clearly
   marked slot for a short read written and signed by the owner, but do not write its content.
2. **Every figure keeps its source and its date.** Every number links to its source document and
   states the period it covers. How you show that is a design question (it does not have to be a
   "src" text link on every cell), but it must be one click or one tap away and never lost.
3. **Honest about gaps.** Some suppliers are private and publish no comparable figures. Show that
   honestly without filling the page with dashes. Collection status (which sources could not be read)
   must be available but should not dominate the first screen.
4. **Light theme only.** No dark mode and no following the operating system's dark setting.
5. **Works at 1440 pixels and at 390 pixels (phone)**, with no horizontal page scroll, readable
   type, and tap targets of at least 24 pixels. Keyboard usable.
6. **No owner byline in the hero.** The owner removed "Run by Jesse Pike." Keep "Not a news site and
   not investment advice." somewhere visible.
7. **Real data.** Use the actual tracker data, not lorem ipsum or invented figures. Do not invent,
   round differently, or relabel any figure. If you show a subset to keep the prototype manageable,
   include at least four full domains and the complete "what changed" list.

## 5. The data

All of it is in the repository at `/Users/jessepike/code/projects/sec-market/web/src/data/`:

- `tracker/domains.ts` — the twelve domains and their descriptions.
- `tracker/suppliers.ts` — 74 suppliers: domain, public or private, ticker, revenue growth with
  period, filing date and source, prior quarter, the company's own metric, ownership or last round.
- `tracker/events.ts` — dated events (results, funding, acquisitions, divestitures, restructuring,
  leadership, debt) with sources.
- `tracker/derive.ts` — how the page derives counts, medians and the "what changed" window.
- `generated/edgarFacts.json`, `generated/collectState.json` — SEC filing facts and collection status.

The current page, for reference only (do not copy its design):
- Production: https://securitymarketpulse.com
- Current proposed version: https://security-market-pulse-git-mon-uifix-pikeholdings.vercel.app/

Problems the owner and the lead already see in the current version: tables that are mostly dashes,
column positions that change from table to table, source links wrapping onto their own lines, a
collection-failure notice as the first thing a reader sees, the most interesting content ("what
changed") buried at the bottom below twelve tables, and a phone page that is 30,000 pixels tall.

## 6. What to deliver

Write everything into your own directory, `docs/active/design-bakeoff/<your-model>/`, and nowhere
else. Do not modify anything under `web/` or anywhere else in the repository.

1. `research.md` — what you looked at, with links, and the patterns you are taking and rejecting.
2. `index.html` — a single self-contained, working prototype of the redesigned front page. Inline
   CSS and JavaScript; the real data embedded as a JSON block extracted from the files above. Fonts
   from Google Fonts are allowed; scripts only from cdnjs.cloudflare.com or cdn.jsdelivr.net if you
   truly need a library. It must open directly from disk in Chrome and look finished at both 1440
   and 390 pixels.
3. `rationale.md` — one page: the design idea in two or three sentences, the information
   architecture (what is on the first screen and why), the visual system (type, colour, spacing),
   how it meets each hard constraint in section 4, and what you would do next with more time.

Render your prototype and look at it at both widths before you finish. A design you have not seen is
not done.

## 6a. Carry-forward for whoever builds the winner (added 2026-10-02, after the contestants started)

The prototypes are for direction. The winning design is rebuilt in `web/` on top of fix pass 4,
which changes the data and fixes things the blind scorers measured. The rebuild must keep all of it.

On the data side (`mon/fitfix`, to be merged onto `preview` by itself):
- Growth is shown to one decimal, computed from reported revenue.
- Every own metric and ownership fact carries an as-of date, and a build gate fails if one is shown
  without it.
- Segment rows name their parent company.
- The status-line counts are derived from the data.
- `/tracker.json` is generated at build time.

On the accessibility side (`mon/uifix`):
- The keyboard order skips sort buttons the reader can't see.
- Every tap target is at least 24 pixels.
- Fonts are self-hosted.
- The desktop layout does not shift as the page loads.
- The first supplier row shows on the first phone screen.
- The archive pages no longer carry the live tagline.

## 7. How it will be judged

The owner picks. The lead will render all three at 1440 and 390 and put them side by side, and may
add blind scores against this brief. What matters, in order: does a security leader get the picture
in the first screen; is it a pleasure to look at; is it dense with real information; does it keep
every hard constraint; does it work on a phone.
