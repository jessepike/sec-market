# Agent surface specification — Security Market Pulse

**Artifact ID:** `SEC-MARKET-FABLE-AGENT` v0.1 (proposal, awaiting owner acceptance)
**Written by:** the run coordinator, 2026-09-20
**Built on:** `research/05-agent-readable-web.md`, `evidence/baseline/machine-extraction.md` (with
the coordinator's correction note), `codebase-map.md`, `site-rubric.md` v1.1 dimension D8

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

## 3. What gets added

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
  "statement": "Infrastructure is running ahead. Security is splitting, not booming.",
  "meaning": "<marketCall.meaning>",
  "since": "2026-08-15",
  "doesNotClaim": ["<marketCall.noCallBoundaries>"],
  "changeConditions": [
    { "id": "c1", "text": "<marketCall.changeTriggers[0]>", "status": "no-movement", "asOf": "2026-09-19" }
  ],
  "current": {
    "verdict": "holds", "confidence": "medium", "basis": "<weThink.thesis.basis>",
    "issueId": "2026-w36", "signedBy": "Jesse Pike", "signedOn": "2026-09-19",
    "url": "https://securitymarketpulse.com/issues/2026-w36/#we-think"
  },
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

`status` and `asOf` on the conditions appear only if the owner accepts design decision D-3. The
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

Serving the Markdown in answer to `Accept: text/markdown` is possible with a header-matched
rewrite in `vercel.json` and no function. It is a stretch item: verify on a preview that the CDN
does not serve the Markdown to a browser from cache before it goes near `main`.

### 3.5 JSON-LD

- `Organization` with `@id` `https://securitymarketpulse.com/#publisher` and `Person` with `@id`
  `https://securitymarketpulse.com/#author`, declared once and referenced from every route.
- `WebSite` on the front page.
- `author`, `datePublished` and `dateModified` added to the archive's `CollectionPage`, which is
  the one L3 test the JSON-LD fails today.
- `license` and `usageInfo` pointing at `/method/#terms` on every `Report` and `Article`.
- `/thesis/` is an `Article` whose `about` names the thesis, with `hasPart` linking the issues
  that judged it. No invented types.

### 3.6 Feed, sitemap, robots, llms.txt

- The feed gets a visible link in the navigation and in the follow line. Each entry's summary
  leads with the verdict word.
- The sitemap lists the JSON endpoints, the Markdown copies and the new routes.
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

**Recommendation: A.** The exposure denominator is one. The scarce thing is being read and cited
at all, and the monetization plan sells access to the author, never the text. A is also the only
option that needs no owner gate, only an acknowledgement. If the owner prefers B or C, that is an
owner-gated change and is parked until he says so.

## 5. Terms for content and data

D8 L5-4 needs a machine-discoverable licence or terms statement. Three options:

1. **Plain permissive terms, all rights reserved.** "© Jesse Pike. You may quote, cite, summarize
   and index this site, by hand or by machine, with attribution and a link to the permalink."
2. Creative Commons Attribution 4.0 for text and data.
3. Creative Commons Attribution-NonCommercial 4.0.

**Recommendation: 1 for now.** A Creative Commons grant cannot be withdrawn, the owner has an
unanswered question with his employer about this publication (see the monetization plan), and
NonCommercial is ambiguous for enterprise and agent use. Plain terms give agents the permission
they need and can be widened to CC BY later, after twelve issues. This is the owner's call and
the text is his to edit; it lives at `/method/#terms`.

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

D8 from 2 to 4 with the build alone, and to 5 once the owner has acknowledged a crawler policy
and approved the terms text. Ten points of weight, so four to six points of composite.

## 9. The strongest case against this surface

Written before the adversarial pass; section 10 records what that pass added.

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

## 10. Adversarial pass

To be completed after task T3-3.
