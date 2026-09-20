# Agent surface specification — Security Market Pulse

**Artifact ID:** `SEC-MARKET-FABLE-AGENT` v0.2 (proposal, awaiting owner acceptance)
**Written by:** the run coordinator, 2026-09-20. v0.2 is v0.1 revised after the adversarial pass
(`consults/adversarial-pass.md`); section 10 lists what changed.
**Built on:** `research/05-agent-readable-web.md`, `evidence/baseline/machine-extraction.md` (with
the coordinator's correction note), `codebase-map.md`, `site-rubric.md` v1.2 dimension D8

## 1. The position

A program that reads this site should be able to do three things without rendering a page or
parsing prose: learn what the site currently believes, cite one claim by an address that will
never change, and check that the text it cited has not been altered. The site is unusually well
placed for the third. Signed issues are immutable and an append-only lock manifest proves it.
Almost no publication can say that to a machine.

Most of the work is linking and labelling things that already exist. The baseline found three
working JSON files and a lock manifest that nothing on the site links to, so a cold agent found
one by guessing and never found the others. D8 scores 2 of 5 today. Linking the files and
completing one JSON-LD block reaches 3 on its own.

The work is split the same way as the design. **Wave 1** is linking what exists: links from the
HTML and the sitemap to the three JSON files and the lock manifest, a visible feed link, and
`author` and dates on the archive JSON-LD. That alone takes D8 from 2 to 3. **Wave 2** is
everything else in section 3, and starts only after a second issue has been signed.

Everything in this specification is a static file produced at build time. There is no server, no
function, no database, no key and no account. The whole surface is free, and the monetization
plan recommends it stays free permanently, because being citable is distribution and distribution
is what this project lacks.

## 2. What exists today

| Surface | Address | State |
|---|---|---|
| Prerendered HTML | every route | All content in served HTML. Good. |
| Issue data | `/issues/<id>.json` | 200. Carries 23 evidence records with source URL, source class, retrieved date, hash and locator. Linked from nowhere. |
| Archive index | `/issues/index.json` | 200. Linked from nowhere. |
| Lock manifest | `/issues/lock.json` | 200. Linked from nowhere. |
| Feed | `/feed.xml` | Advertised by a `link` tag in the head only. No visible link. |
| JSON-LD | every route | `Report`, `CollectionPage`, `Article`. The archive block has no author and no dates. No `@id` anywhere. No licence. |
| Sitemap | `/sitemap.xml` | HTML routes only. |
| Robots | `/robots.txt` | Static default `Allow: /`. No stated policy. |
| Markdown | none | `.md` addresses and `Accept: text/markdown` return nothing. |

## 3. What gets added (wave 2, except where marked)

### 3.1 A site manifest: `/index.json`

The one address an agent needs. Every route advertises it with
`<link rel="alternate" type="application/json" href="/index.json">`, the footer carries a visible
"For machines" link to it, and the sitemap lists it.

```json
{
  "schemaVersion": 1,
  "name": "Security Market Pulse",
  "description": "<the same descriptor line the first screen shows>",
  "publisher": { "@id": "https://securitymarketpulse.com/#publisher" },
  "author": { "@id": "https://securitymarketpulse.com/#author", "name": "Jesse Pike" },
  "newestIssue": "2026-w36",
  "endpoints": {
    "thesis": "/thesis.json",
    "issues": "/issues/index.json",
    "issue": "/issues/{issueId}.json",
    "lock": "/issues/lock.json",
    "feed": "/feed.xml",
    "markdown": "{routePath}index.md"
  },
  "citation": {
    "itemUrlTemplate": "https://securitymarketpulse.com/issues/{issueId}/#{itemId}",
    "note": "Item ids are stable. Published issues do not change."
  },
  "immutability": {
    "statement": "A published issue is never edited. Corrections are published as dated entries.",
    "lock": "/issues/lock.json",
    "corrections": "/thesis/#corrections"
  },
  "terms": "/method/#terms",
  "crawlerPolicy": "/robots.txt",
  "generated": "<build date>"
}
```

### 3.2 A thesis endpoint: `/thesis.json`

The structured form of the `/thesis/` page. It answers D8 L5-1: the standing thesis, the current
verdict, confidence, signer and date, with no prose parsing.

```json
{
  "schemaVersion": 1,
  "id": "standing-thesis",
  "position": {
    "text": "Infrastructure is running ahead. Security is splitting, not booming.",
    "verdict": "holds",
    "confidence": "medium",
    "asOf": "2026-09-19",
    "signedBy": "Jesse Pike",
    "issueId": "2026-w36",
    "doesNotClaim": ["<marketCall.noCallBoundaries>"],
    "basis": "<weThink.thesis.basis>",
    "url": "https://securitymarketpulse.com/issues/2026-w36/#we-think",
    "restatement": "If you restate this position, carry its confidence, its date and its signer."
  },
  "meaning": "<marketCall.meaning>",
  "since": "2026-08-15",
  "changeConditions": [
    { "id": "c1", "text": "<marketCall.changeTriggers[0]>" }
  ],
  "history": [
    { "issueId": "2026-w36", "weekEnding": "2026-09-06", "published": "2026-09-19",
      "verdict": "holds", "confidence": "medium", "signedBy": "Jesse Pike",
      "url": "...", "json": "/issues/2026-w36.json" }
  ],
  "runningScore": { "issues": 1, "holds": 1, "strengthens": 0, "weakens": 0, "noCall": 0 },
  "earlierRecord": [ { "date": "2026-08-16", "kind": "unsigned-edition-record", "summary": "..." } ],
  "corrections": [],
  "generated": "<build date>"
}
```

**There is no bare `statement` field, on purpose.** Intent requires that claims keep their
uncertainty and that judgments carry their confidence and basis. A top-level one-sentence market
position is the easiest thing for an answer engine to quote with everything else stripped off. So
the smallest quotable unit is the `position` object, and the sentence cannot be read from it
without its verdict, confidence, date, signer and what it does not claim sitting beside it. The
terms ask any restatement to carry them. This does not force anyone to comply; it makes the
labelled form the easy form.

`position` is always built from the **newest published issue**, never from a draft. Each condition
gains `status` and `asOf` only once the owner has set them on the standing call in
`web/src/data/market.ts` (design decision D-3); until then the fields are absent, not invented. The
public id is `standing-thesis`. The internal id `episode-002` does not appear on any public
surface.

### 3.3 Stable claim citation

Every tracked item already has an id in the data (`2026-w36-formation-3`). The build gives each
row that id in the HTML, so one claim can be cited as
`https://securitymarketpulse.com/issues/2026-w36/#2026-w36-formation-3`. The judgment block keeps
`#we-think`. A text fragment (`#:~:text=`) may be added by the citing agent and is safe here in a
way it is not elsewhere, because the text of a published issue cannot change.

The issue JSON files are **not** changed to carry these addresses. `scripts/verify-dist.ts` checks
each file for exact equality with the issue data, and the lock manifest hashes that data. The
address is derivable from a rule, and the rule is published once in `/index.json`. This keeps the
immutability proof simple.

Citations point at the permalink, never at the front page, because the front page changes weekly.
The front page rows carry the same ids so in-page links work, and each row's "#" control copies
the permalink form.

### 3.4 Markdown copies of every route

At build time, one Markdown file per route, written from the same data the HTML is rendered from
(not converted from HTML): `/index.md`, `/thesis/index.md`, `/issues/index.md`,
`/issues/<id>/index.md`, `/method/index.md`. Each HTML route advertises its copy with
`<link rel="alternate" type="text/markdown" href="index.md">`. Each file starts with a short
front-matter block: title, canonical address, signer, signed date, verdict, and the lock address.

The site does not negotiate on `Accept: text/markdown`. A header-matched rewrite serves two bodies
from one address, the CDN caches by address, and a wrong cached body would reach browsers. The
files and the `rel="alternate"` links are what the rubric asks for, and they cannot fail that way.

### 3.5 JSON-LD

- `Organization` with `@id` `https://securitymarketpulse.com/#publisher` and `Person` with `@id`
  `https://securitymarketpulse.com/#author`, declared once and referenced from every route.
- `WebSite` on the front page.
- **Wave 1.** `author`, `datePublished` and `dateModified` added to the archive's `CollectionPage`, which is
  the one L3 test the JSON-LD fails today.
- `license` and `usageInfo` pointing at `/method/#terms` on every `Report` and `Article`.
- `/thesis/` is an `Article` whose `about` names the thesis, with `hasPart` linking the issues
  that judged it. No invented types.

### 3.6 Feed, sitemap, robots, llms.txt

- **Wave 1.** The feed gets a visible link in the navigation and in the follow line. Each entry's summary
  leads with the verdict word.
- The sitemap lists the JSON endpoints (wave 1: the three that exist and the lock manifest), then
  the Markdown copies and the new routes.
- `robots.txt` stops being a default and states a policy, section 4.
- `/llms.txt`: about twenty lines pointing at `/index.json`, `/thesis/index.md` and the archive.
  The research found that the large crawlers ignore this file today. It costs almost nothing and
  nothing is claimed for it.

## 4. Crawler policy: options and a recommendation

Blocking any crawler is an owner gate. Stating the policy is required by D8 L5-6 whatever the
policy is.

| Option | What it does | For | Against |
|---|---|---|---|
| **A. Allow everything, say so** | All crawlers allowed, including training crawlers. A comment block and a Content Signals line (`search=yes, ai-input=yes, ai-train=yes`) state it as a choice. | Maximum reach. Agent answers and future models can cite and recall the site. Matches "free forever". | Text may be absorbed into models with no attribution. Cannot be undone for crawls already made. |
| B. Allow search and answer-time retrieval, disallow training crawlers | Named training agents disallowed (for example GPTBot, CCBot, Google-Extended); retrieval agents allowed. | Keeps live citation. Holds back the corpus. | The list of agents goes stale. Compliance is voluntary. Costs recall in future models, which is where a standing thesis would most like to be remembered. |
| C. Block all AI crawlers | Disallow every known AI agent. | Maximum control. | Directly opposes one of the brief's three pillars. |

**Nothing here is decided or built until the owner has asked his employer the outside-activity
question (monetization plan, M-3).** Granting the public, and machine training, standing
permission over his judgments about a market his employer sells into is a decision to make after
that answer, not before. Wave 1 leaves `robots.txt` exactly as it is.

**Recommendation once M-3 is answered: A.** The exposure denominator is one. The scarce thing is
being read and cited at all, and the monetization plan sells access to the author, never the text.
The honest cost, stated plainly: A is the one choice on this page that cannot be taken back, since
text already crawled stays crawled. B and C are owner-gated changes and are parked until he says so.

## 5. Terms for content and data

D8 L5-4 needs a machine-discoverable licence or terms statement. Three options:

1. **Plain permissive terms, all rights reserved.** "© Jesse Pike. You may quote, cite, summarize
   and index this site, by hand or by machine, with attribution and a link to the permalink."
2. Creative Commons Attribution 4.0 for text and data.
3. Creative Commons Attribution-NonCommercial 4.0.

**Recommendation: match the terms to the crawler policy.** v0.1 recommended plain terms because a
Creative Commons grant cannot be withdrawn, while recommending crawler option A, which also cannot
be withdrawn. The adversarial pass was right that those two positions contradict each other, and
right that "all rights reserved" beside a robots file inviting training is a signal no crawler
resolves in the author's favour. The consistent pairs are:

- Crawler option A with **CC BY 4.0**, declared by its URL and SPDX identifier in the JSON-LD, so
  a machine can interpret it and not merely find it. This is the recommendation if the owner wants
  reach.
- Crawler option B with plain permissive terms, if the owner wants to hold the corpus back.

Either way the text lives at `/method/#terms`, is the owner's to edit, and waits for M-3.

## 6. Verification

Added to `scripts/verify-dist.ts`, so a stale or broken machine surface fails the build:

1. `/thesis.json` equals the value derived from the issues and the standing call at build time.
2. Every address in `/index.json` `endpoints` exists in `dist`.
3. Every `link rel="alternate"` target exists in `dist`.
4. Every route has a Markdown copy, and each issue's copy contains the read, the exact signature
   line and the same number of items as the data.
5. Every item id is unique across the site and appears as an `id` in the issue's HTML.
6. No empty headings and no duplicate ids on any route.
7. JSON-LD on every route parses, and every `@id` reference resolves within the page.

**Acceptance test.** Re-run the cold-agent extraction script from the baseline: a program given
only the home address and no rendering. It passes when it reaches the thesis, the verdict, the
confidence, the signer and the date from structured data, reaches every JSON file by following
links, and cites one item by address.

## 7. What is deliberately not built

| Not built | Why |
|---|---|
| A remote MCP server | Needs a backend, which is a separate owner yes. No demand exists to serve. The research found no small editorial publication running one. |
| A metered or keyed API | Same. The only fetched price anchor is an add-on to a product with a real database behind it. |
| Pay-per-crawl | Needs infrastructure in front of the site and an audience worth charging. Neither exists. |
| Changes to issue JSON bodies | They are covered by the lock. Addresses are derived by rule instead. |
| Agent analytics beyond server logs | Counting fetches of `/thesis.json` is the one number that would justify revisiting MCP later. Vercel's own logs can answer that without new code. Recorded for the backlog. |

## 8. What this should do to the score

D8 from 2 to 3 with wave 1, to 4 with wave 2, and to 5 once the owner has decided a crawler policy
and approved terms. Ten points of weight, so two, four and six points of composite.

## 9. The strongest case against this surface

No agent is asking for this. The research could not find evidence that Markdown copies, `llms.txt`
or a thesis endpoint cause any agent to cite a small publication more often, and the large
crawlers ignore the one file the community talks about most. The site has one issue. An agent
that finds `/thesis.json` finds a ledger with one row. This is building a loading dock for a shop
with no customers, and it could be a way of feeling productive while the real problem, cadence,
goes unsolved.

The answer: it is cheap, it is static, it adds no running cost and no new failure mode to the
weekly signing, and the immutability claim is a real difference worth stating to machines early.
It is sequenced after the first screen and the thesis page for exactly this reason, and nothing
in it is worth delaying an issue for.

## 10. Adversarial pass: what changed and what survived

Task T3-3, `claude-opus-5`, `consults/adversarial-pass.md`.

| Finding | Outcome |
|---|---|
| 1. A draft 2026-w37 exists; `current` assumed a signed newest issue | Accepted. `position` is built from the newest published issue |
| 3. The example showed condition statuses dated to a locked issue | Accepted. Statuses come from `market.ts`, set by the owner, absent until then |
| 12. Recommending irreversible crawler access while rejecting Creative Commons as irreversible; bespoke terms are findable but not interpretable; approving either before the employment question is the wrong order | Accepted in full. Sections 4 and 5 rewritten; nothing is decided before M-3; wave 1 leaves `robots.txt` alone |
| 13. A bare thesis string strips the labels intent requires | Accepted. The `position` object in 3.2. The sharpest catch of the pass |
| 15. A fail-closed build check bolted onto an `Accept` rewrite nobody has seen work | Accepted. No content negotiation; files and `rel="alternate"` only |
| 2. Build a quarter | Accepted as wave 1: links, sitemap entries, visible feed, archive JSON-LD |

**What the reviewer tried to break and could not:** leaving the issue JSON bodies untouched and
publishing the address rule once keeps the immutability proof simple; item ids on front-page rows
create no duplicate ids; `verify-dist` compares `JSON.parse(JSON.stringify(issue))` on both sides,
so nothing here disturbs the lock.
