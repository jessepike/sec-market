# Promote the read

**ID:** `SEC-MARKET-READ-001` · **Version:** v0.1 · **Opened:** 2026-08-28

## Why

The site's message layer is not on the page. `#read` — the market call, what changed, Do, Avoid, what
we will not call, and what would change the call — sits inside a closed `<details class="depth">`
labelled "The market read, domain tempo and M&A activity". So does the masthead carrying the headline
"Infrastructure is running ahead. Security is splitting, not booming."

Verified in a browser on production at 1561px, not from markup: `#read` is in the document and
`checkVisibility()` returns `false`. A reader sees a tagline, four domain cards, what moved, platform
pressure, hypotheses and forty-two vendor cards. All evidence, no read.

This is the same defect D-54 fixed for the vendor scorecard six days earlier, sitting on more
valuable content. Owner approved promoting the read on 2026-08-28.

## Change 1 — move the read to the top of the page

In `web/src/App.tsx`, move `<Hero />` and `<JudgmentBoard />` out of the `#research-depth` disclosure
and to the top of `<main>`, above `<DomainBoard />`. Final order inside `<main>`:

```
<Hero />                          {/* #overview */}
<JudgmentBoard />                 {/* #read */}
<DomainBoard />                   {/* #landscape */}
<WhatMoved />
<PlatformPressure />
<Hypotheses />
<PrintGrid />
<details className="depth" id="research-depth">
  <summary>Domain tempo and M&amp;A activity</summary>
  <DomainBoard surface="tempo" />
  <ActivityBoard />
</details>
... the remaining depth sections unchanged
```

The disclosure summary loses "The market read" because the read is no longer in it. Leaving that
wording would send a reader looking for something that has moved.

No component internals change in this step. No copy changes. Nothing is deleted.

## Change 2 — fix the heading outline, and mind the collision

Today `web/src/components/DomainBoard.tsx` holds the page's only `<h1>`
(`id="landscape-heading"`), and `web/src/components/Hero.tsx` holds an `<h2>`
(`id="market-call-heading"`). After Change 1 the `<h2>` would precede the `<h1>` in document order.

Swap the levels so the market call is the page's `<h1>` and the landscape tagline is an `<h2>`. This
is correct on the merits as well as mechanically: the page's primary statement is the market call.

**Both headings must look exactly as they do now. The only visible change on this page is position.**

Update the stylesheet with these precise selectors:

- `index.css` line ~305, `.masthead h2 { … }` becomes `.masthead h1 { … }`. The margin rule above it
  already lists both `.masthead h1` and `.masthead h2`; leave that rule alone.
- `index.css` line ~1989, `.landscape h1 { … }` becomes **`.landscape__intro h2 { … }`**.
- `index.css` line ~2541, the `.landscape h1` inside the media query becomes
  **`.landscape__intro h2`** as well.

**The collision, stated so it is not discovered by accident.** Every domain card renders its vendor
name as `<h2>` inside `.landscape`. A selector of `.landscape h2` would therefore restyle all four
domain card titles at masthead size. Scope both replacements to `.landscape__intro`, which contains
only the tagline. After the change, confirm by render that the four domain card titles are
pixel-identical to before.

## Change 3 — navigation

In `web/src/components/Header.tsx`, add `{ href: '#read', label: 'The read' }` as the **first** entry
in `navItems`. Change the brand link's `href` and both `scrollToHash('#landscape')` calls in the
brand click handler to `'#overview'`, so the logo returns a reader to the top of the page rather than
to a section that is now partway down.

Leave `scrollToHash` itself alone. Its `details.open = true` behaviour still matters for the sections
that remain collapsed.

## Change 4 — the market call carries the new finding

**This change alters a published, dated, human-signed judgment. It is separable from Changes 1 to 3
and the owner may reject it on its own without unpicking the promotion.**

In `web/src/data/market.ts`, on `marketCall`:

Append to `whatChanged`:

> Palo Alto paid $634.5M for Protect AI and F5 paid $145.2M for CalypsoAI, and both filings call the
> acquired revenue immaterial. Platforms are buying AI security ahead of any visible buyer spend.

Append to `actions.avoidItems`:

> Reading AI-security acquisition prices as evidence of AI-security demand. The filings say the
> acquired revenue was not material.

Append to `confidenceNote`, as a further sentence:

> High that platforms are acquiring AI security ahead of any disclosed revenue.

Add `D32`, `D33`, `D34` and `D35` to `marketCall.evidenceIds`.

Change nothing else in that file. `headline`, `subhead`, `meaning`, `noCallBoundaries` and
`changeTriggers` all stay exactly as they are.

Note for the record and do not act on it: `Hero.tsx` hard-codes the headline text that also lives in
`marketCall.headline`, so the two can drift. That is a real defect and it is out of scope here.

## Acceptance

1. `npm run build` passes, including `verify:edition`, `verify:panel`, `verify:integrity`, `tsc` and
   lint. All npm and tsx work runs through `orb run -m dev`; `node_modules` in `web/` is a Linux
   install and every one of those commands fails on the host with an esbuild platform mismatch.
2. Rendered at 1440 and 390 with `node scripts/shot.mjs`, which does run on the host. Capture before
   and after at both widths and report the pixel heights.
3. **In a real browser, `document.querySelector('#read').checkVisibility()` returns `true` at both
   1440 and 390 with no clicking.** This is the whole point of the change and a screenshot is not
   sufficient proof on its own. Report the boolean you actually observed.
4. Exactly one `<h1>` on the page, and it is the market call.
5. The four domain card titles are visually unchanged. Say how you confirmed it.
6. On the phone render at 390, describe in plain words what the first screen now contains, and flag
   it if the page opens on something a reader would not understand.
7. Report invisible work separately from visible work.

## Not authorized by this work

Rewriting `headline`, `subhead`, `meaning`, `noCallBoundaries` or `changeTriggers`. Moving any
posture, tag, horizon or hypothesis state. Adding or removing a domain card. Splitting or restyling
`JudgmentBoard` internally. Touching the Identity card's CyberArk watch item, which is SEC-026.
