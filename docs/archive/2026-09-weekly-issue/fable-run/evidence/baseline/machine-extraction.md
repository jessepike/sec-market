# Machine Extraction Test — securitymarketpulse.com

Cold run: one URL, curl only (`-A "MachineExtractionTest/1.0"`), no browser, no repo access.
21 HTTP requests total, well under the 60-request budget. Full request log kept in the
run's scratch directory (not committed).


> **Coordinator correction, 2026-09-20.** Two status codes in the T1 section below are wrong and
> were re-checked with `curl -s -o /dev/null -w "%{http_code}"` against production:
> `/issues/index.json` returns **200** (341 bytes, `application/json`), not 404, and `/index.json`
> returns **404**, not a misleading 200. `/issues/lock.json` also returns 200 (85 bytes) and the
> cold agent never found it. The finding that matters is unchanged and slightly stronger: three
> working JSON surfaces exist and nothing on the site links to any of them.

## Scorecard

| Task | Succeeded | Source | Requests |
|---|---|---|---|
| T1 Discovery | Yes | structured + HTML + guessed | 6 |
| T2 Publisher/author | Yes | structured (JSON-LD) | 1 |
| T3 Standing thesis | Partly | HTML (headline in JSON-LD, thesis text HTML-only) | 1 |
| T4 This week's verdict | Yes | structured (guessed JSON endpoint) + HTML | 2 |
| T5 Verdict history | Partly | none (only one issue exists yet) | 3 |
| T6 One claim, precise citation | Yes | structured (guessed JSON) + JS bundle cross-check | 4 |
| T7 Archive | Yes | structured + HTML, 3 surfaces agree | 3 |
| T8 Immutability/freshness | Partly | HTTP headers + JSON-LD + footer text | 0 (reused) |
| T9 Licence/permissions | Partly | HTTP headers + robots.txt + HTML disclaimer | 2 |
| T10 Alternate representations | Yes | HTTP negotiation + guessed suffixes | 5 |
| T11 JSON quality | Yes | structured (guessed endpoint) | 1 |
| T12 HTML parse quality | Yes | HTML | 0 (reused) |

## T1 — Discovery

Found without guessing anything site-specific:

- `/robots.txt` — 200. Body: `User-agent: *` / `Allow: /` / `Sitemap: https://securitymarketpulse.com/sitemap.xml`
- `/sitemap.xml` — 200, `application/xml`. Lists exactly three URLs: `/`, `/issues/`, `/issues/2026-w36/`, each with `lastmod`, `changefreq`, `priority`.
- `<link rel="alternate" type="application/rss+xml" ... href="https://securitymarketpulse.com/feed.xml">` on the home page — a real feed autodiscovery link.
- One `<script type="application/ld+json">` block per page (schema.org `Report` on the home page, `Article` on the issue page, `CollectionPage` on `/issues/`).
- Standard meta tags: `author`, full Open Graph set, Twitter card.

Checked and absent: `/llms.txt` (404), `/llms-full.txt` (404), `/.well-known/security.txt` (404). No JSON Feed autodiscovery link, no HTTP `Link:` header on any response, no `<link rel="alternate" type="application/json">`.

Found only by guessing a site-specific pattern:

- `/issues/2026-w36.json` — 200, `application/json`, 43,612 bytes. Guessed by taking the issue id from the sitemap and appending `.json`. This is the single biggest find of the run and nothing on the site points to it.
- `/evidence/W36-14` — an evidence id seen inside the JSON above. Guessing this as a URL gets a 308 redirect to `/evidence/W36-14/`, which then 404s. That is Vercel's generic trailing-slash redirect, not a real route — evidence ids are not dereferenceable.
- `/issues.json`, `/issues/index.json`, `/index.md`, `/issues/2026-w36.md`, `/issues/2026-w36/index.md` — all guessed, all 404. `/index.json` returned HTTP 200 with `content-type: application/json` but a body of plain text `"The page could not be found / NOT_FOUND"` — a misleading 200 that is actually Vercel's error page, not a real endpoint.

## T2 — Publisher and author

From the home page JSON-LD (`schema.org/Report`):

```
"author": { "@type": "Person", "name": "Jesse Pike" },
"publisher": { "@type": "Organization", "name": "Security Market Pulse", "url": "https://securitymarketpulse.com/" },
"description": "An evidence-linked read on the cybersecurity market for security leaders. Every number links to a public source, and the page makes no call where the evidence is thin."
```

Neither the `Person` nor the `Organization` carries its own `@id`. Only the `Report` itself has a stable `@id` (`https://securitymarketpulse.com/#report`). So there is a stable id for the document, not for the publisher or the author as reusable entities.

## T3 — Standing market thesis

Structured data gives a headline and an abstract, but not a labeled "thesis" field. From the JSON-LD: `headline`: "Infrastructure is running ahead. Security is splitting, not booming." and `abstract`: "Use infrastructure activation as an account qualification trigger — not as proof of a broad cybersecurity boom. A stable lag is still not measurable."

The page itself labels the thesis explicitly in HTML, in a block with the class `we-think__thesis`:

> Thesis — holds: Every prints-lane figure this window is a strong beat with accelerating or steady growth (CrowdStrike net new ARR +51% YoY, Palo Alto Next-Gen Security ARR +63% YoY, Rubrik subscription ARR +33% YoY, NVIDIA Data Center revenue +117% YoY). ... No M&A or funding item this window is large or structurally unusual enough to move it on its own.

I could tell this was the thesis rather than the week's headline only because the HTML uses the literal word "Thesis" as a label directly in the markup (`Thesis — holds:`), distinct from the `<h2>` headline text above it ("Infrastructure is running ahead. Security is splitting, not booming."). Nothing in the JSON-LD makes that distinction — a machine reading only structured data would have the headline and abstract but no explicit "this is the thesis, separate from this week's read" signal. The guessed JSON endpoint (T4/T6) does carry a `thesis` object with a `thesis: "episode-002"` id, which is the cleanest confirmation that the thesis is a standing, separately-tracked object rather than this week's headline.

## T4 — This week's verdict

Once the JSON endpoint `/issues/2026-w36.json` was found (by guessing), the verdict is fully structured, at `issue.weThink.thesis`:

```json
{
  "thesis": "episode-002",
  "verdict": "holds",
  "confidence": "medium",
  "evidenceIds": ["W36-14", "W36-19", "W36-18", "W36-22"]
}
```

and at `issue.weThink`: `"signedBy": "Jesse Pike", "signedOn": "2026-09-19"`.

The same facts are present in the HTML as visible text (`Thesis — holds`, `CONFIDENCE · MEDIUM`, `Signed by Jesse Pike · 19 Sep 2026`), but only the JSON gives them as named fields. Without the guessed JSON endpoint, a machine would have to parse prose to get the verdict, and would have no reliable way to know "medium" is a confidence enum rather than a passing adjective.

## T5 — History of past verdicts

There is exactly one published issue (`2026-w36`, published 2026-09-19), confirmed identically by the sitemap, the RSS feed, and the `/issues/` archive page. The home page's running-score line — "Holds in 1 of 1 issues since 19 Sep 2026" — confirms the count directly. There is no history array anywhere: the per-issue JSON only carries that one issue's own verdict, not a log of prior verdicts on the same standing thesis. If more issues are published later, a machine could reconstruct history only by fetching each issue's JSON individually (assuming the same guessable `.json` suffix keeps working) — there is no single "thesis history" endpoint today, so this could not be verified as a machine-readable capability, only inferred as a plausible pattern from what exists.

## T6 — One claim, traced to source, with a precision citation

Claim: CrowdStrike net-new ARR grew 51% year over year, part of the thesis basis.

From `/issues/2026-w36.json`, the thesis cites evidence id `W36-14`, which resolves (in the same JSON payload, under `evidence`) to:

```json
{
  "id": "W36-14",
  "title": "CrowdStrike Q2 FY2027 Financial Results",
  "organization": "CrowdStrike",
  "publicationDate": "2026-08-26",
  "canonicalUrl": "https://www.sec.gov/Archives/edgar/data/1535527/000153552726000029/crwd-20260826xex991.htm",
  "excerpt": "... Delivers record net new ARR of $333 million, accelerates growth to 51% year-over-year",
  "sourceClass": "FILING",
  "retrievedAt": "2026-09-03",
  "retrieval": {
    "sha256": "55bfc3ec3d51b325dcc39a3b1d23a2ef7a56d9b9d216c456a3d39b50083fdfcb",
    "fetchedAt": "2026-09-04T16:31:56Z",
    "locator": "EX-99.1, revenue and net-new-ARR paragraph"
  }
}
```

That is a real SEC EDGAR exhibit URL, with a publication date, a retrieval date, a sha256 of the fetched content, and a plain-English locator ("EX-99.1, revenue and net-new-ARR paragraph"). This is the most precise citation obtainable, and it is precise about the primary source, not about the site's own page.

For a citation back to securitymarketpulse.com itself: the site gave no anchor id for this claim. The issue page's HTML has zero `<a href>` elements pointing anywhere (0 external links in 31KB of markup) — every "View evidence" control is a plain `<button>` with no `href` and no `data-*` attribute, meaning the citation only opens via a JavaScript modal whose data comes from the shipped JS bundle, not from anything in the static HTML. I confirmed the same evidence record is duplicated verbatim inside the JS bundle (`/assets/index-CW2_skVJ.js`, fetched directly) as an inline object literal, which is how a non-rendering fetcher can still recover it by grepping the bundle text — but that only works because the data happens to leak into client-side JS, not because the site publishes it as a citable resource. The most precise stable citation I could produce for a human is the bare issue page URL (`https://securitymarketpulse.com/issues/2026-w36/`) with no fragment, since there is no anchor id and the site does not supply a text-fragment link (`#:~:text=`) itself — a machine would have to construct one by hand from the claim text, with no guarantee that the browser fragment will actually match the rendered DOM text (the visible text is broken up by React comment nodes, e.g. `Thesis — <!-- -->holds<!-- -->:`).

## T7 — Archive

Three independent surfaces list the archive, and they agree:

- `sitemap.xml`: 1 issue URL, `/issues/2026-w36/`, `lastmod` 2026-09-19.
- `feed.xml` (RSS): 1 `<item>`, same URL, `pubDate` Sat 19 Sep 2026.
- `/issues/` (HTML): 1 row, id `2026-w36`, "week ending 6 Sep 2026", "Signed by Jesse Pike · 19 Sep 2026".

All three agree on the id, the URL, and the publication date. None of the three surfaces gives the issue's `weekEnding` (2026-09-06) and `published` (2026-09-19) dates as clearly separated fields except the JSON endpoint, which does distinguish them explicitly (`weekEnding`, `windowStart`, `published`).

## T8 — Immutability and freshness

Response headers on the home page: `last-modified: Sun, 20 Sep 2026 03:23:13 GMT`, `etag: "258d7b856f11051fc9785215727faec3"`, `cache-control: public, max-age=0, must-revalidate` (always revalidate, never blindly cache). The hashed JS asset, by contrast, is `cache-control: public, max-age=31536000, immutable` — standard content-hashed-filename caching, not evidence about the article content itself.

The JSON-LD `dateModified` (2026-09-19) matches `datePublished`, so nothing says this issue has been edited since it went live. The page footer states outright: "Frozen from SEC-MARKET-SIG-002 v0.2 (2026-08-15T19:03:08-07:00). Public sources only. Not investment advice." — a human-readable freeze/provenance statement, not a machine-checkable one.

There is no site-wide hash manifest and no stated "next issue" date anywhere I found. What does exist, and is the closest thing to an integrity mechanism, is per-evidence-record data inside the guessed JSON endpoint: every one of the 23 evidence entries carries its own `retrieval.sha256` and `retrieval.fetchedAt`. That proves the collector hashed the specific source document it read at collection time — it does not prove the issue page itself hasn't changed since publication, since there's no manifest tying the rendered page's content to those hashes.

## T9 — Licence and permissions

No licence file, no terms page, no Content-Signal or TDM-related header, no `X-Robots-Tag` on any response. `robots.txt` is a blanket `Allow: /` for `User-agent: *` with no named-crawler rules at all — GPTBot, ClaudeBot, CCBot, Google-Extended are neither singled out nor restricted; the default line covers everyone identically.

Relevant response headers (home page): `cache-control: public, max-age=0, must-revalidate`, `access-control-allow-origin: *`, `permissions-policy: geolocation=(), microphone=(), camera=()`, `referrer-policy: strict-origin-when-cross-origin`, `strict-transport-security: max-age=63072000`, `x-content-type-options: nosniff`, `x-frame-options: SAMEORIGIN`. No `content-security-policy` header on any page. The only human-readable usage statement anywhere on the site is the footer disclaimer: "Public sources only. Not investment advice." — not a licence, and it says nothing about reuse, redistribution, or AI training.

## T10 — Alternate representations

`Accept: text/markdown` on both the home page and the issue page returned identical `text/html` bodies at identical byte sizes to the plain request — the server does not content-negotiate on `Accept` at all. `/index.md`, `/issues/2026-w36.md`, and `/issues/2026-w36/index.md` all returned 404.

Byte sizes: home page HTML is 216,418 bytes (~54,100 estimated tokens at 4 bytes/token). The per-issue JSON (`/issues/2026-w36.json`, found only by guessing) is 43,612 bytes (~10,900 estimated tokens) and contains the full issue — all four lanes, the thesis, the signed verdict, and all 23 evidence records with their source URLs. Reading the JSON instead of the HTML would cost an agent roughly a fifth as many tokens for the same substantive content, but nothing advertises that the JSON exists.

## T11 — JSON quality

One JSON endpoint found (by guessing): `/issues/2026-w36.json`. Top-level shape is `{"issue": {...}, "evidence": [...]}`.

Self-describing: field names are plain English and need no separate documentation (`weekEnding`, `windowStart`, `published`, `status`, `sections`, `weThink`, `evidenceIds`, `canonicalUrl`, `sourceClass`, `retrievedAt`). Not self-describing in one respect: there is no `$schema` link, no version field, and no declared content-type contract beyond the HTTP header — an agent has to infer the shape by reading it.

Ids: issue sections use ids like `2026-w36-formation-1`; evidence records use ids like `W36-14`. These ids are stable-looking (structured, not random) but not dereferenceable — I tested `/evidence/W36-14` directly and it resolves only to a generic 404 after a redirect, confirming there is no real per-id route.

Evidence quality is high: every one of the 23 evidence records carries `canonicalUrl` (a real external source — SEC EDGAR filings, investor-relations press releases, or named publications), `organization` (the publisher), `sourceClass` (`FILING`, `IR`, `INDEPENDENT`), `publicationDate`, `retrievedAt`, and a `retrieval` object with `sha256`, `fetchedAt`, and a plain-English `locator` describing where in the source document the number came from. The JSON is also honest about its own gaps — it includes a `sources` field listing which upstream sources were `readable` (21) versus `unreadable` (3, named URLs that the collector apparently couldn't fetch).

## T12 — HTML parse quality

| Page | Bytes | Headings (empty) | ids (dup) | `<time datetime>` | main / article / section |
|---|---|---|---|---|---|
| Home | 216,418 | 108 (0 empty) | 46 (0 dup) | 92 | 1 / 66 / 19 |
| Issue (2026-w36) | 31,482 | 6 (0 empty) | 15 (0 dup) | 25 | 1 / 0 / 7 |
| Archive (/issues/) | 5,941 | 1 (0 empty) | 5 (0 dup) | 2 | 1 / 0 / 1 |

No empty headings and no duplicate ids on any of the three pages — the markup is clean by those two measures. All three pages wrap their content in exactly one `<main>` landmark, with heavy, correctly-nested use of `<section>` (all carrying `aria-labelledby`) and, on the home page, `<article>` for each individual card. Dates are consistently marked up with `<time dateTime="...">`. The one parsing wrinkle: visible text is frequently interrupted by React hydration comment markers (e.g., `Thesis — <!-- -->holds<!-- -->:`), which is invisible to a rendered browser but means a naive text-extraction pass that doesn't strip HTML comments first will see broken-up words.

## What a cold agent could not do

- Get a machine-readable history of past thesis verdicts — only one issue exists, so this is unverified rather than confirmed absent.
- Get any anchor, id, or text-fragment link from the site itself that points at one specific claim inside an issue page; the only working citation granularity is the whole issue page URL.
- Dereference an evidence id (`W36-14`) as a URL — it looks like a stable identifier but has no matching route.
- Discover the JSON endpoint (`/issues/2026-w36.json`) from anything the site itself publishes — no link, no sitemap entry, no `Link` header, no JSON Feed autodiscovery pointed at it; it only exists because the issue id follows a guessable pattern.
- Get any citation-precision help for AI agents specifically — no `llms.txt`, no `llms-full.txt`, no named-crawler robots rules, no licence or TDM signal of any kind.
- Negotiate a lighter representation via `Accept` headers — the server ignores `Accept: text/markdown` entirely and there are no `.md` fallback routes.
- Confirm, from anything machine-readable, whether a published issue can be edited after the fact — only a prose disclaimer ("Frozen from ... v0.2") addresses this, and per-evidence hashes exist but aren't tied to a whole-page manifest.
