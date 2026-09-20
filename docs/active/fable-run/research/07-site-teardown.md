# T1-7 — Current-site teardown

Scope: this file covers only the "Current-site teardown" task from
`docs/active/fable-run/phase1-dispatch.md`. It renders and reads
`https://securitymarketpulse.com/`, `/issues/`, and `/issues/2026-w36/`, and the same three paths
on the preview deployment, and describes what a reader actually experiences.

## What was captured and how

`web/scripts/shot.mjs` was read first and was not modified. It launches Playwright with
`chromium.launch({ channel: 'chrome' })`, full-page only, at 1440 and 390 px. Run inside the
OrbStack dev VM (`orb run -m dev node scripts/shot.mjs ...` from `/mnt/mac/.../web`), it fails
immediately:

```
browserType.launch: Chromium distribution 'chrome' is not found at /opt/google/chrome/chrome
Run "npx playwright install chrome"
```

The VM has Playwright's own chromium builds installed (`~/.cache/ms-playwright/chromium-1234`
etc.) but no actual Google Chrome binary, and installing one was out of scope for this task. So,
per the dispatch's own fallback instruction, a throwaway script was written at
`docs/active/fable-run/evidence/baseline/capture.mjs` — not in `web/scripts/` — that mirrors
`shot.mjs`'s logic with plain `chromium.launch()` (no channel) instead, and adds the
first-viewport-only capture (no scrolling) at 1440x900 and 390x844 that `shot.mjs` doesn't
support at all.

One more wrinkle: that script needs `web/node_modules`, which only Node resolves for a file whose
own directory is inside or under `web/`. Since the script must live outside `web/`, it was run as
an eval string with the working directory set to `web/`, which makes Node resolve bare imports
from `web/node_modules` without touching anything under `web/`:

```
cd /mnt/mac/Users/jessepike/code/projects/sec-market/web && \
  node --input-type=module -e "$(cat .../evidence/baseline/capture.mjs)" -- dummy "<URL>" "<out-prefix>"
```

A `claude-haiku-4-5` subagent ran this command for all six (URL, prefix) pairs and reported back.
All six runs exited 0. All 24 expected PNGs are present in
`docs/active/fable-run/evidence/baseline/`, none under 5 KB:

| Prefix | 1440 full | 1440 viewport | 390 full | 390 viewport |
|---|---|---|---|---|
| prod-home | 1,431,630 B | 94,880 B | 1,005,012 B | 61,745 B |
| prod-issues | 41,774 B | 41,774 B | 34,845 B | 34,845 B |
| prod-issue-w36 | 452,082 B | 94,880 B | 430,727 B | 61,745 B |
| preview-home | 1,431,630 B | 94,880 B | 1,005,012 B | 61,745 B |
| preview-issues | 41,774 B | 41,774 B | 34,845 B | 34,845 B |
| preview-issue-w36 | 452,082 B | 94,880 B | 430,727 B | 61,745 B |

Every prod file is byte-identical in size to its preview counterpart. The `prod-issues` full and
viewport files are also identical to each other, because that page is shorter than one screen —
there is nothing to scroll to.

I opened and looked at the images directly (viewport captures at both widths, the full-page
captures, and cropped sections of the tallest full-page captures cut with Pillow to see the
signed-judgment region clearly) rather than inferring the page from markup. I also fetched the
live HTML for `/`, `/issues/`, and `/issues/2026-w36/` with `curl` to check headings, JSON-LD, and
structural detail the images can't show (what's inside a collapsed disclosure widget, for
instance).

## The first five seconds — desktop

A CISO landing on `securitymarketpulse.com/` at 1440px sees, top to bottom: a thin black
provenance bar ("AS OF 19 SEP 2026" and a two-item legend distinguishing "TRACKED" prints from
"JUDGED" calls), a plain white nav bar with seven links (Issue, Archive, Thesis, Landscape,
Scorecard, Evidence, Method), and then a large black headline: "Record earnings from CrowdStrike,
Zscaler, Palo Alto, Rubrik and NVIDIA meet thin VC and quiet M&A — the infra-to-security lag call
holds." Below that, immediately, a "Formation" section starts listing individual funding rounds as
cards (Socure $156M, KAZIMI $2.6M, CYBERA $2.5M), each with a date, one sentence, and a "Return on
Security" source-link chip.

In five seconds the honest read is: this is a dense, text-forward market newsletter with a strong
opinionated headline, not a dashboard and not a landing page that explains what the site is or who
it's for. There is no strapline, no "what is this" line, no visible thesis statement, and no
scorecard in view — just the current week's headline and the start of a long list of financing
events. A reader has to already know what "the infra-to-security lag call" refers to; nothing
above the fold defines it.

## The first thirty seconds — desktop

Scrolling through the first screen or two, the reader hits "Formation" (funding rounds), then
"Absorption," "Prints" (earnings), and "Capital and backdrop" — four consecutive card-list
sections, each structured identically: bold one-line headline, date, one-sentence gloss, a source
chip. This is where thirty seconds actually goes: repetitive card scanning with no summary framing
above it to say why these particular items matter. Nothing in the first thirty seconds tells the
reader what to do with this information or where the site's own judgment about it lives.

## The first three minutes — desktop

Only around the three-minute mark, after Formation/Absorption/Prints/Capital and backdrop, does
the page reach a section headed "What we now think" — a single paragraph of synthesis, a
grey-boxed "Thesis — holds" callout, one bullet on what the site refuses to call, and finally the
line "Signed by Jesse Pike · 19 Sep 2026." I measured this directly: the full-page desktop capture
is 15,022px tall, and the signature sits at roughly y=5,150–5,250 — about 34% of the way down the
page, or close to six full 1440x900 screens of scrolling. Immediately after it comes the actual
headline verdict, "Infrastructure is running ahead. Security is splitting, not booming," with
"Holds in 1 of 1 issues since 19 Sep 2026" and three stat tiles (+92%, +4%, NO-CALL). That is the
first point in the whole page where the site states its own standing argument in its own words. Up
to that point, everything the reader has seen is raw, ungraded evidence.

Past the verdict, the page keeps going for another roughly 9,800px (65% of the total page) — four
domain-posture cards (Network/SASE, Data/AI Security, Cloud Security, Identity), a vendor-pressure
table ("Who is holding, who is buying in, who is being outrun"), a "Tracked hypotheses" grid, an
"Infrastructure" tempo section, and then six collapsed disclosure sections in a row: "What moved:
edition delta," "Domain tempo and M&A activity," "Market layers," "Watch next," "How this is
built," and "Research & evidence." None of those six is open by default. In three minutes, a fast
reader reaches the verdict and the domain cards; a normal reader does not reach the collapsed
sections at all without deliberately clicking each one open.

## The first five seconds, thirty seconds, three minutes — phone

At 390px the structure is the same but stretched further: the full page is 17,715px tall, and the
signed line sits at roughly y=7,200 — about 41% down, or 8.5 phone screens (844px viewport) of
scrolling. The first five seconds show the same black provenance bar (now wrapped to two lines),
a "Menu" button instead of the nav links, and the same headline, now wrapping across six lines
instead of three. The card-based Formation/Absorption/Prints/Capital sections stack full-width one
under another, so the "thirty seconds" experience is even more purely a scroll of single-column
cards — there's no way to scan several at once the way the desktop grid allows. Reaching the
signed judgment and the actual thesis headline on phone realistically takes longer than three
minutes of continuous scrolling for anyone who isn't deliberately hunting for it.

## Is the standing thesis visible without scrolling — no

At both widths, nothing above the fold states the site's actual argument. The eyebrow line above
the H1 gives the issue number and date; the H1 itself is this week's news headline, not the
thesis. The thesis text ("Infrastructure is running ahead. Security is splitting, not booming.")
and the "Holds in 1 of 1 issues" scoring line are both roughly a third of the way down a very long
page. A reader who does not scroll past the news headline never learns what the site is actually
arguing.

## What's confusing

- The homepage (`/`) and the sole issue permalink (`/issues/2026-w36/`) are pixel-identical —
  same HTML byte-for-byte in the parts that matter, same screenshot file sizes at every width. A
  reader who bookmarks or is sent the permalink cannot tell it apart from the front page, and
  there is nothing that marks one as "current" and the other as "archived."
- The page's own methodology copy, buried inside the collapsed "How this is built" section, reads:
  "Refresh is manual: earnings clusters, material closes or raises, and Watch-next falsifiers. Not
  a weekly news cycle." That line directly undercuts any expectation of a fixed publishing day,
  even though the project brief and the site's outward framing describe it as a weekly issue.
- The black provenance legend ("TRACKED · public prints, no judgment" / "JUDGED · signed and dated
  by a person") is the right idea — it tells a reader how to read the colour coding before they hit
  it — but it appears once, in a thin bar most readers will skim past, and the coding itself never
  reappears as a visible legend lower on the page where the tracked/judged distinction actually
  matters (the domain cards, the vendor table).

## What's buried

The front page has 41 native HTML `<details>` disclosure elements, and not one of them is open by
default (`grep -c '<details'` = 41, `grep -c '<details[^>]*open'` = 0). That includes the six major
sections named above (edition delta, domain tempo and M&A activity, market layers, watch next,
methodology, evidence library), roughly 19 individual "activity row" toggles inside the tempo
section, 8 per-vendor toggles inside the domain-landscape cards, and a "View data table
(accessible alternative)" toggle for at least one chart. All of that content is present in the
static HTML — a crawler or an AI agent parsing the page sees everything — but a human scrolling the
rendered page sees only the closed summary line unless they click each one. Given how much of the
page's actual reasoning (what changed, the falsifier list, the method) sits inside these, the
disclosure pattern is doing a lot of the work of hiding the site's depth from a first-time human
reader while still making it available to a fetcher.

## What's repeated

The four evidence sections (Formation, Absorption, Prints, Capital and backdrop) use one
unvarying card template — bold headline, date, one sentence, one source chip — for what are
substantively different kinds of events (an early-stage raise and NVIDIA's data-center print get
the same visual weight). Nothing distinguishes a $2.5M pre-seed round from a $96.2B NVIDIA print
except the words in the sentence; there's no size cue, icon, or type distinction. The same
"Return on Security" / named-source chip pattern repeats dozens of times across the page.

## What gives no reason to return next week

There is no email capture, subscribe form, or sign-up prompt anywhere in the fetched HTML
(`grep -i 'subscribe\|newsletter\|email.{0,30}sign'` matches nothing on the page itself — the only
related hits are the word "rss" and the `feed.xml` link). The only mechanism to be notified of a
new issue is RSS. The `/issues/` archive page, screenshotted at both widths, shows one row (issue
2026-w36) and then a large blank area — full-page and viewport-only captures at 1440px are
byte-identical because the page is shorter than one screen. There is no "next issue expected"
date, no streak counter, no visible cadence promise on the page, and — as noted above — the site's
own method copy explicitly says it does not run on a weekly cycle. A returning reader who checks
back has nothing to compare against except re-reading the same single issue.

## What a returning reader could tell had changed

Almost nothing, right now, because there is only one signed issue in the archive. The one
comparison surface that does exist is the "thesis-running-score" line ("Holds in 1 of 1 issues
since 19 Sep 2026"), which would start compounding meaning once a second and third issue publish.
The per-domain posture cards each carry a "JUDGED 16 AUG 2026" date stamp, so a future edition
that moves a posture would show a new date — but there is no visible "last time we said X, now we
say Y" diff on the page today; a reader would have to remember the prior wording themselves.

## Facts for the baseline record

**`robots.txt`** (production):
```
User-agent: *
Allow: /

Sitemap: https://securitymarketpulse.com/sitemap.xml
```

**Response headers for `/`** (production, `curl -s -D - -o /dev/null`): `HTTP/2 200`,
`content-type: text/html; charset=utf-8`, `cache-control: public, max-age=0, must-revalidate`,
`x-vercel-cache: HIT`, `strict-transport-security: max-age=63072000`, `x-frame-options:
SAMEORIGIN`, `x-content-type-options: nosniff`, `permissions-policy: geolocation=(), microphone=(),
camera=()`, `access-control-allow-origin: *`, `content-length: 216418`. No `x-robots-tag` header on
production.

**Response headers for `/`** (preview): same security headers, plus `x-robots-tag: noindex` (the
preview correctly tells crawlers not to index it), `x-vercel-cache: MISS` on the request I made,
and `strict-transport-security` additionally sets `includeSubDomains; preload`.

**Endpoint status and content type** (identical on production and preview except where noted):

| Path | Status | Content-Type |
|---|---|---|
| `/feed.xml` | 200 | `application/xml` |
| `/issues/index.json` | 200 | `application/json; charset=utf-8` |
| `/issues/2026-w36.json` | 200 | `application/json; charset=utf-8` |
| `/sitemap.xml` | 200 | `application/xml` |
| `/issues/` | 200 | `text/html; charset=utf-8` |
| `/issues/2026-w36/` | 200 | `text/html; charset=utf-8` |

**Heading outline** (front page, production, in document order — abbreviated where a section
repeats the same pattern many times): H1 (the week's headline) → H2 Formation → H2 Absorption → H2
Prints → H2 Capital and backdrop → H2 What we now think → H2 Infrastructure is running ahead
(thesis headline) → H2 The read → H3 What changed / Do / Avoid / We will not call / What would
change the call → H2 Where the security market is going, not where it has been → four unlabelled H2
domain cards → H2 Who is holding, who is buying in, who is being outrun → repeated H3 vendor names
→ H2 Tracked hypotheses → H2 This period → repeated H3 vendor names → H2 What moved → H2 Tempo → H3
Since 17 August 2026 → H2 M&A and startups → H2 Market layers → H2 Watch next → six H3 watch items
→ H2 How this is built → H3 How editions age / Signals we use / How we turn that into a call → H2
Research & evidence library → H2 If a figure is wrong, send it. One H1 total; the four domain cards
under "Where the security market is going" render as empty-text H2 elements (heading level present,
visible label rendered separately in markup — worth a note for the agent-readable-web research
track, not fixed here).

**JSON-LD**: exactly one `<script type="application/ld+json">` block on the front page, type
`Report`.

## Production versus preview — no visible difference

I diffed the raw HTML for `/` on both hosts. The only difference in the entire document is one
extra line on preview: a Vercel Live feedback-widget script tag
(`vercel.live/_next-live/feedback/feedback.js`), which renders nothing visible. Every screenshot
file size matches exactly between the production and preview versions of the same page and width.
Preview additionally sends `x-robots-tag: noindex`, which is correct and invisible. I opened the
preview home viewport image directly to confirm rather than relying on the header/size match alone
— it is pixel-for-pixel the same layout as production. Production and preview do not differ
visibly in any way a reader would notice.

## What I could not reach

Nothing in the assigned scope was blocked. Both hosts returned normal 200 responses with no
Vercel authentication or protection gate. The one limitation worth naming: exact pixel offsets for
the signed-judgment line were measured by cropping the full-page PNGs with Pillow and reading the
crop coordinates, not by querying the DOM for a bounding rectangle, so the reported figures
(roughly 34% down desktop, 41% down phone) are visual measurements with normal PNG-crop precision,
not exact-to-the-pixel DOM measurements.
