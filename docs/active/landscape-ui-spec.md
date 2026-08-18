# SEC-MARKET-LANDSCAPE-UI-002 — The landscape page

**Status:** draft, awaiting owner authorization
**Task two of two.** Do not start until [landscape-data-spec.md](landscape-data-spec.md) is merged.
Everything below consumes data that task produces. If a figure you need is not in the data model,
stop and say so rather than typing it into a component.

## Reference

The accepted design is **Option D**, desktop and phone, in `/.design/`:

- `Landscape.dc.html` — 1440px
- `LandscapeMobile.dc.html` — 390px
- `out/option-d-desktop.png`, `out/option-d-mobile-1of2.png`, `out/option-d-mobile-2of2.png`

These are the visual contract. Open the HTML files in a browser and match them. They are already
written against the app's real tokens, so lift values from them directly rather than
re-deriving. The three other boards in that directory (`Main`, `Record`, `Calibration`) were
rejected directions. Ignore them.

## Design system — no new values

Everything comes from `web/src/index.css`. Do not add a colour, a font, or a radius.

- Display `Archivo` 600/800, body `IBM Plex Sans` 400/500/600, mono `IBM Plex Mono` 400/500/600
- `--radius: 0`. There are no rounded corners on this site.
- `--color-accent: #0b6b5e`, `--color-alert: #8e2f5e`, `--color-warning: #6b5c28`,
  `--color-context: #1b2430`, `--content-max: 1280px`
- The dark-band-only values `#e7ebf0 #8b97a6 #aab5c2 #5fd4c0 #e8a0c4 #f3d48a` appear **only** on a
  `#12161c` or `#1b2430` background. Never on a light surface.
- Light theme only. Do not add a dark mode or a `prefers-color-scheme` block.

## What changes on the page

The site stops presenting itself as an edition to be read and starts presenting a landscape to be
checked. Order, top to bottom:

1. **Provenance rail.** New, full width, `#12161c`. Brand, `AS OF <date>`, and the three-state
   legend: TRACKED refreshed weekly, JUDGED signed and dated by a person, NEEDS A SOURCE. Render
   all three states even when nothing currently carries the third; the legend is a statement about
   how the page behaves, and the weekly loop will populate it.
2. **Header.** Existing `Header.tsx`, nav relabelled to Landscape, This week, Platforms,
   Hypotheses, Method, Evidence.
3. **The landscape.** `h1`, one supporting paragraph, then four domain cards in a
   `repeat(4, minmax(0, 1fr))` grid. Each card carries name, direction glyph, posture chip, the
   one-line read, a TRACKED block with the prints, and a JUDGED block with `asOf`, `horizon`, and
   confidence. Extend `DomainBoard.tsx` rather than replacing it.
4. **What moved this week.** New `WhatMoved.tsx` on `#1b2430`. Two columns: TRACKED left, JUDGED
   right. A week with no posture change renders as a week with no posture change; do not hide the
   section and do not pad it.
5. **Platform pressure.** New `PlatformPressure.tsx`. A four-column table at 1440, four labelled
   groups of stacked rows at 390. Reads `platformPressure` from the data task.
6. **Tracked hypotheses.** New `Hypotheses.tsx`. Four rows: state chip, claim, note.
7. **Method and corrections.** Reuse `MethodologyNote.tsx` content. Replace `NextEdition.tsx` per
   the removal below.

Sections not named here (`ChartsPanel`, `MarketLayersChart`, `BuyerBudgetChart`, `EvidenceLibrary`,
`WatchList`, `PrintGrid`, `ActivityBoard`, `JudgmentBoard`) keep working and move below the
landscape. **Do not delete any component on the strength of static analysis.** `AGENTS.md` is
explicit: prove it with a before and after render or leave it alone.

## Removals

`NextEdition.tsx` currently says editions publish when the evidence moves rather than on a fixed
schedule. That trains a reader not to come back, which is the opposite of what a weekly landscape
needs. Keep the two mailto links, which are honest and have no form behind them, and replace the
heading and body copy so they invite corrections rather than announce an edition cadence. There is
no "read the edition" call to action anywhere on the page, because the page is the product.

## Mobile, at 390px

Deliberate and load-bearing: **the four posture cards come before the positioning line.** An account
team member opening this on a phone is checking status, not reading a pitch. Do not "fix" this back
to a conventional hero.

- The platform pressure table becomes four labelled groups of stacked rows. A four-column table does
  not survive 390px.
- Every link, button, and tappable row clears 44px.
- The three legend states wrap onto their own line in the rail.
- No horizontal scroll at any width between 320 and 1440.

## Acceptance criteria

1. `npm run build`, `npm run lint`, and `npx tsc --noEmit` pass in the OrbStack dev VM.
2. No component reads a figure from anywhere but the data model. A grep of the new components for
   `%`, `$`, and vendor names returns nothing.
3. Every rendered claim shows its provenance. A `judged` claim without a visible date, or a
   `tracked` claim without a reachable evidence link, is a defect.
4. Existing evidence-drawer links still open and still resolve.
5. Accessibility holds: one `h1`, heading levels in order, the skip link works, focus outlines
   intact, contrast unchanged from the tokens.
6. **Render it and look at it.** `node scripts/shot.mjs <preview-url> /tmp/preview` and
   `node scripts/shot.mjs https://securitymarketpulse.com/ /tmp/prod`. Attach all four images and
   state plainly what moved. A passing build is not a page that looks right.

## Out of scope

The weekly collection loop. Any change to `intent.md`, to Episode 002 tags, to the evidence library,
or to the published market call and its NO-CALL. New sources. Auto-publishing anything. Traffic,
analytics, or SEO work beyond keeping what already exists.

## Deploy

Branch only. `main` is the live site and a push to it publishes with nobody in between. No merge
without a Vercel preview, the four screenshots, and the owner's explicit yes. Commit email must be
`jesse@keatingpike.com` or the Vercel deploy is rejected. See `AGENTS.md` § Production deploy and
§ Visual review before publish.
