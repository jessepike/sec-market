# T1-6 — First-screen and information design craft

## What I looked at and what I could not reach

I fetched the live marketing pages at linear.app, zed.dev, vercel.com, railway.com, and
resend.com. Four of the five (Vercel, Railway, Resend, and to a lesser extent Zed) served
WebFetch a stripped, agent-oriented rendering of the page rather than the visual layout a
human sees — Resend's fetch literally returned a section addressed "For AI agents and
automation, use the tools below," and Vercel's returned marketing copy with no colour or
spacing information at all. That is itself a small data point for the companion piece on
agent-readable pages, but it means I could not measure real pixel layout, colour count, or
type scale directly from the live HTML for those four sites. To compensate I used
third-party CSS scrapers — DesignMD, Fudge, and Refero Styles — which read a live site's
computed styles and report the actual hex values, font stacks, and spacing scale in use,
plus the companies' own design-system or blog pages where those exist (Vercel's Geist docs,
Linear's own "Now" posts). Where a number below comes from one of these scrapers rather
than the vendor's own words, I say so; I could not independently verify any scraped hex
value against the live rendered CSS this run.

For the editorial and data comparisons I used Hacker News (fetched directly, plain HTML, no
agent-markdown substitution) and researched Axios's Smart Brevity format and TradingView's
charting layout through web search rather than direct fetch, since both are script-heavy
products a fetch would not render faithfully. Line-length and tabular-figure claims come
from an academic literature review and a reputable trade article, both cited with URL and
quote below; I did not find one canonical Nielsen Norman Group page with a numeric
line-length recommendation, so mentions of NN/g below are through secondary summaries of
its position, marked as weaker evidence than a direct fetch. The WCAG 2.2 quotes came
directly from the W3C's own Understanding pages for each success criterion, fetched this
run, so those are first-hand and exact.

## Findings per product

**Linear (linear.app).** Linear's own post about its latest visual refresh states its
intent plainly: "Linear is designed to surface exactly what you need, when you need it. The
challenge was preserving that rich density of information without letting the interface
feel overwhelming." (https://linear.app/now/behind-the-latest-design-refresh). The same
post gives two rules worth carrying forward as design inputs: "Don't compete for attention
you haven't earned," meaning navigation chrome is dimmed relative to content, and
"Structure should be felt not seen," meaning dividers use soft contrast and rounded corners
instead of hard rules. DesignMD's scrape of linear.app (https://designmd.cc/benchmarks/linear)
reports eight named type sizes from a 64px display down to a 12px caption, a 4px-based
spacing scale (4, 8, 12, 16, 20, 24, 32), and seven core colours across light, dark, and
accent families, with one indigo (#5e6ad2) as the single accent and everything else
neutral. Linear's docs and third-party shortcut references (fastshortcuts.com,
keycombiner.com) describe an app built to run almost entirely from the keyboard: single
letters for common actions (C to create an issue, S for status, P for priority, L for
labels), G-prefixed chords for navigation, and Cmd+K / Ctrl+K opening a command palette that
jumps to any section by typed name.

**Zed (zed.dev).** Zed's blog states its interface goal is to stay "out of your face,"
unlike editors with more chrome competing for attention (framing drawn from a search
summary of https://zed.dev/blog/between-editors-and-ides — I did not fetch that page
directly, so this line is softer evidence than a direct quote). Zed supports separate light
and dark themes with automatic OS-based switching and ships a Theme Builder
(https://zed.dev/docs/appearance, https://zed.dev/blog/theme-builder) that lets a user click
any element to see the named colour token controlling it — a system of small, named,
swappable tokens rather than one fixed brand palette, so "how many hues does Zed use" has
no single answer the way it does for a marketing site. As a text editor, Zed's whole surface
runs on a monospace family for code with a separate UI sans for menus and labels, the same
split Vercel and Resend make deliberately.

**Vercel (vercel.com).** Vercel's Geist introduction page describes its colour system in
one line, "A high contrast, accessible color system," and points to sub-pages for colours
and typography rather than stating numbers on the landing page itself
(https://vercel.com/geist/introduction). DesignMD's scrape of vercel.com
(https://designmd.cc/benchmarks/vercel) and a separate design write-up both describe the
same system: a near-white #fafafa canvas, near-black #171717 for body text and most UI
chrome, a 200-step neutral grey scale for every border and divider, and exactly one
functional accent, blue (#0070f3), reserved for links, primary buttons, and active states.
The write-up states the principle directly: "There is no brand-blue or marketing accent —
the ink IS the brand... You could remove [the blue] entirely and the site would still look
like Vercel. That's the test of a truly neutral design system: the accent is optional."
Vercel pairs Geist Sans for reading with Geist Mono for code, terminal output, and technical
labels; both typefaces are open-sourced and now used broadly across other developer tools,
a sign this pairing has become a category default rather than a one-off choice.

**Railway (railway.com).** Railway is the one product here that stays on a dark canvas, and
a design write-up (design.withfudge.com) states this plainly: dark is the default "with no
light mode implementation planned without a full color system redesign." Its scraped tokens
show a near-black navy canvas (#0B0D17), a purple primary action colour (#7C3AED) used as a
gradient into a lighter purple, and a secondary blue action colour (#3B82F6) — two
functional accents plus a gradient, where Linear and Vercel use one flat accent. Railway
pairs Inter with JetBrains Mono, the same sans/mono split as the other four. Because this
project is light-theme-only, Railway is the weakest direct style match, but it is a useful
negative case: a dark, gradient-accented, two-hue system reads as more "product," less
"instrument," than Vercel's single-accent light system.

**Resend (resend.com).** A search-based inventory of Resend's tokens (oh-my-design.kr,
VoltAgent's DESIGN.md scrape) describes a black canvas (#000000) with near-white (#f0f0f0)
body text, a five-hue numbered accent system (orange, green, blue, yellow, red, each with
its own numbered scale), and an ambitious type pairing: an oversized serif (Domaine
Display, 76–96px) for hero display type, a humanist sans (ABC Favorit) for body, Inter for
UI chrome, and Commit Mono for code blocks, badges, and inline technical labels. Resend is
the only one of the five running a display serif at all. Its actual page content, as
fetched, is a dense, vertically stacked list of developer-facing sections (API reference,
CLI, MCP server, SDKs, changelog, handbook, pricing), each a short heading followed by
links — closer to a documentation index than a marketing hero.

**Hacker News.** Fetched directly. Above the fold on a normal desktop window, roughly eight
to ten full story rows are visible, each about 40–50 pixels tall, single column, no images
anywhere in the list. Every row is a title plus one line of grey metadata — points,
submitter, age, comment count — in the exact order "187 points by username 3 hours ago |
hide | 82 comments." There is effectively one type size for titles and one smaller size for
metadata, black on white, with orange reserved for the upvote triangle and blue for links.
This is close to the density ceiling for pure text: no imagery, no whitespace beyond what
keeps rows apart, and a metadata line that gives every fact a reader needs before clicking.

**TradingView and Axios (researched, not fetched).** Search summaries describe
TradingView's layout — "chart centre, tools left, context right" — as the reference layout
for the charting-dashboard category, with colour "reserved strictly for direction"
(red/green) against a near-monochrome dark surface, and extra data folded into existing
elements (sparklines, background fills, tile sizing) rather than added columns. Axios's
Smart Brevity format is a text-density strategy: the stated goal is that "key elements fit
on one screen," achieved through short paragraphs, bolding as visual anchor points, and
bullet lists, claimed to cut typical length by roughly 40 percent while keeping the same
information. TradingView shows how a data-dense screen keeps colour disciplined by giving it
one job; Axios shows how an editorial product engineers scannability through sentence-level
formatting rather than layout alone.

## Patterns that repeat across products

Every product here separates a humanist sans for reading from a monospace for anything
numeric, technical, or code-shaped — Inter, Geist Sans, or ABC Favorit for prose, paired
with Berkeley Mono, Geist Mono, JetBrains Mono, or Commit Mono for data and code. None mixes
more than one sans and one mono at a time; Resend's serif appears only in oversized hero
type, never in body or data.

Every light-themed product (Linear, Vercel) runs on one functional accent colour against a
near-monochrome neutral scale, and both frame this as a discipline rather than a limit —
Linear's "don't compete for attention you haven't earned" and Vercel's "the accent is
optional" are the same idea stated two ways. The dark-themed products (Railway, and by
category convention TradingView) allow a second accent or a gradient, which reads as more
permissible on a dark canvas than a light one — another argument for restraint given this
project's light-only mandate.

Every product with real density (Linear's issue list, Hacker News, TradingView) treats
whitespace, not font size, as the variable that separates rows — density comes from tight
vertical rhythm, not small type. None of the five drops body text below roughly 13–14px; the
12px sizes that appear (Linear's caption, Vercel's caption) are reserved for metadata and
labels, never for continuous reading.

Keyboard-first interaction is a developer-tool convention in this set, not a Linear-only
trait: Cmd+K command palettes are described as now standard across Linear, Vercel, GitHub,
Raycast, and Slack, and Linear layers single-letter shortcuts and chorded navigation on top.
None of the editorial or data products researched here (Hacker News, Axios, TradingView)
documents an equivalent keyboard layer — keyboard-first looks like a developer-tool
convention, not a publishing one, which matters for a project sitting between the two
categories.

## What transfers, and what does not

The single-accent, near-monochrome palette transfers directly and is probably the highest-
value visual decision available: it costs nothing to build and reads as calm and
trustworthy rather than promotional. Vercel's ink-plus-one-accent system is the closer model
of the two light-themed examples, since Linear still carries marketing chrome (repeated
hero statements, case studies) that a single-author evidence site does not need.

The sans-plus-mono split transfers directly and is cheap: dates, prices, percentages, and
verdict labels (hold/strengthen/weaken/no-call) should run in a monospace or tabular-figure
face so a returning reader can scan a column of numbers without them jumping around week to
week — exactly the case the tabular-figures literature makes.

Hacker News's density model — one line of title, one line of grey metadata, no imagery —
transfers well to an issues index or a signal list, and is a better model here than any of
the five developer-tool marketing pages, which sell a product rather than present a feed of
dated, judged items. Axios's Smart Brevity discipline transfers as a writing constraint more
than a visual one: a signed weekly verdict is exactly the content that benefits from "key
elements fit on one screen," and bolding as anchor points is cheap to apply to a draft.

What does not transfer: Railway's dark-plus-gradient system, since the project is
light-theme-only by house rule. TradingView's chart-dashboard layout, since this site is a
periodic judgment with supporting evidence, closer to Hacker News's list-of-dated-items
shape than to a trading terminal. Resend's oversized display serif, since it is a
brand-personality choice for a product company, and a site whose credibility depends on
reading as evidence-first should not adopt a decorative display face that signals
"marketing" over "instrument." Full keyboard-first navigation (chorded shortcuts,
single-letter actions) is also heavier than a single-author static site justifies right
now — a command palette is real engineering, not a CSS change, and none of the editorial or
data comparisons here use one either, so it is not a competitive gap worth closing yet.

## Design or product moves

- Do give every dated fact — issue date, verdict, price, percentage — a tabular-figure or
  monospace treatment so that a reader can compare this week's numbers against last week's
  without the digits shifting width or position.
- Do reduce the site's palette to one functional accent colour against a near-black-on-white
  neutral scale, following Vercel's rule that the accent should be removable without the
  site losing its identity, so that a reader reads the page as an instrument, not a
  marketing site.
- Do put the standing thesis and this week's verdict inside the first roughly 600 vertical
  pixels of the desktop layout, in a single block with no scroll required, so that a reader
  with ten seconds still leaves knowing where the thesis stands.
- Do adopt Hacker News's title-plus-one-metadata-line row pattern for any list of issues or
  signals, so that a reader can scan a full week's or month's worth of items in the time it
  takes to scroll past them once.
- Do keep body-text line length inside the 50–75 characters researchers keep converging on
  (roughly 60–66 as the most-cited middle), so that a reader's eye does not have to re-find
  the start of the next line on a wide desktop column.
- Do reserve any second colour, if one is ever added, for exactly one meaning — direction,
  as TradingView does with red and green — rather than letting it drift into decoration, so
  that colour keeps carrying information a reader can act on.
- Do give the phone layout a single first-viewport block that states the thesis and verdict
  in the same order as desktop, sized to fit inside roughly 650–700 usable pixels once
  Safari's address-bar chrome is accounted for, so a phone reader is not asked to scroll
  before learning anything.
- Do run a contrast check specifically on small monospace metadata (dates, prices, verdict
  labels) against SC 1.4.3, since small monospace figures are exactly the low-weight,
  small-size text that quietly fails 4.5:1 contrast on a light background even when body
  text passes.
- Do treat 320 CSS pixels, not 390, as the real floor for layout testing under SC 1.4.10,
  because a design that only reflows cleanly at 390 will visibly break on the narrower
  devices the criterion exists to protect.
- Do size every clickable verdict pill, table-row action, and navigation control to at least
  24 by 24 CSS pixels under SC 2.5.8, since a dense information layout is exactly the
  pattern most tempted to shrink targets below that floor to fit more onto the screen.

## WCAG 2.2 inputs, quoted

- SC 1.4.3 Contrast (Minimum), Level AA: "The visual presentation of text and images of
  text has a contrast ratio of at least 4.5:1," with large-scale text needing only 3:1, and
  exceptions for incidental or inactive text and for logotypes.
  (https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)
- SC 1.4.11 Non-text Contrast, Level AA: "The visual presentation of the following have a
  contrast ratio of at least 3:1 against adjacent color(s): User Interface Components...
  [and] Graphical Objects." This is the rule dense designs most often miss, since it covers
  borders, icons, and chart elements, not just body text.
  (https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html)
- SC 1.4.10 Reflow, Level AA: "Content can be presented without loss of information or
  functionality, and without requiring scrolling in two dimensions for: Vertical scrolling
  content at a width equivalent to 320 CSS pixels," with an exception only for content that
  genuinely requires two-dimensional layout, such as a data table or a map.
  (https://www.w3.org/WAI/WCAG22/Understanding/reflow.html)
- SC 2.4.7 Focus Visible, Level AA: "Any keyboard operable user interface has a mode of
  operation where the keyboard focus indicator is visible." This is the rule a dense,
  low-chrome design most often violates by hiding default browser focus rings without
  replacing them.
  (https://www.w3.org/WAI/WCAG22/Understanding/focus-visible.html)
- SC 2.4.11 Focus Not Obscured (Minimum), Level AA, new in 2.2: "When a user interface
  component receives keyboard focus, the component is not entirely hidden due to
  author-created content." A sticky header or footer, which a dense layout is tempted to
  add for constant access to filters, is exactly the pattern this criterion targets.
  (https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html)
- SC 2.5.8 Target Size (Minimum), Level AA, new in 2.2: "The size of the target for pointer
  inputs is at least 24 by 24 CSS pixels," with exceptions for spacing, an equivalent
  control elsewhere on the page, inline targets constrained by line-height,
  user-agent-controlled targets, and essential presentations. Dense layouts routinely
  shrink tap targets below 24 pixels to fit more rows on screen, which is the exact case
  this criterion forbids unless one of the five exceptions applies.
  (https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html)
