# T1-5 — Agent-readable web, current practice as of September 2026

Prepared for Security Market Pulse (https://securitymarketpulse.com). Section F of
`docs/active/fable-run/reading-summary.md` is treated below as ground truth for what the site
already ships, read first as instructed and not re-derived except where a live check was needed.

## What I looked at and what I could not reach

I used web search and web fetch only, plus a live `curl` against
`https://securitymarketpulse.com/robots.txt` and `/llms.txt` to confirm current state rather than
trust the summary alone. I fetched Vercel's content-negotiation blog post and its "Markdown and
Agent Discovery" docs page, schema.org's ClaimReview page, MDN's text fragments reference, a
robots.txt AI-crawler reference, Cloudflare's Monetization Gateway blog post, a secondary write-up
of Cloudflare's Content Signals policy, and the MCP project's 2026 roadmap post. Everything else is
from web search snippets, marked as such below; where a snippet had no directly quotable line, I
say so and treat the claim as reported, not verified.

I could not reach Cloudflare's own contentsignals.org page — the fetch returned no body, so that
syntax is sourced secondhand. Confirmed live: `robots.txt` returns `User-agent: *`, `Allow: /`, and
a `Sitemap:` line, nothing naming AI crawlers or any Content-Signal line; `/llms.txt` returns 404.
Both match section F.

## Findings per technique

**llms.txt / llms-full.txt.** The evidence that crawlers read it is consistently negative for this
site's purpose. From [Does llms.txt Do Anything Yet](https://mecanik.dev/en/posts/does-llms-txt-do-anything-yet/)
and related coverage: "AI search crawlers are almost never fetching /llms.txt. GPTBot, ClaudeBot,
PerplexityBot, OAI-SearchBot, and Google-Extended overwhelmingly skip the file and crawl HTML
directly," and a 137,000-domain study found "97% of those files received zero requests in May
2026." A separate ~300,000-domain analysis reportedly found no statistically significant
correlation between having the file and being cited, and dropping it as a variable improved a
predictive model's accuracy. I read these numbers in aggregator write-ups, not the underlying
studies, so treat them as reported-not-verified, though several sources converge. The one place
adoption looks real is developer tooling — coding assistants like Cursor reading a project's
llms.txt when a person points them at it, a pull a developer invokes, not something a crawler
fetches unprompted. Works on a static host: yes, trivially — one more static text file.

**Markdown variants and Accept: text/markdown negotiation.** Vercel ships this for its own docs.
[Its blog post](https://vercel.com/blog/making-agent-friendly-pages-with-content-negotiation)
states "content negotiation requires no site-specific knowledge. Any agent that sends the right
header gets markdown automatically," reports "many agents already send Accept: text/markdown," and
gives a size figure: "The HTML version of this page is around 500KB. The markdown version is 3KB, a
99.37% reduction." [Vercel's docs page](https://vercel.com/docs/agent-resources/markdown-access)
(dated 2026-09-17) confirms Vercel "confirmed (February 2026) that Claude Code and OpenCode send
Accept: text/markdown headers," and describes two surfaces: true negotiation on the canonical URL
using `Vary: Accept`, and a durable explicit `.md` suffix (`/docs/functions.md`) needing no header
at all. It also lists a broader discovery surface: `llms.txt`, `llms-full.txt`, `sitemap.md`,
`graph.json`, `taxonomy.json`, an OpenAPI file, and `.well-known/ai-catalog.json`.

The two mechanisms split on static-host fit. An explicit `.md` copy per route is pure build output
— the prerender step can write a markdown file next to each HTML file, the same way
`generate-feed.ts` already writes JSON copies. That needs no server. True per-request negotiation
on one URL needs something to inspect the Accept header at request time; on Vercel that is normally
Edge Middleware — lightweight, no database or persistent process, but not "purely static," and a
different code path from the current build. I found no comparably clean Cloudflare feature for this
specific technique and did not verify one exists.

**schema.org types for evidence and claims.** [schema.org](https://schema.org/ClaimReview) defines
`ClaimReview` as "A fact-checking review of claims made (or reported) in some creative work
(referenced via itemReviewed)," under Thing > CreativeWork > Review > ClaimReview, with a
`claimReviewed` text property plus inherited `itemReviewed`, `reviewRating`, `author`,
`datePublished`, `publisher`. `Claim` is a separate, narrower type for the assertion itself. One
source claimed "AI Mode treats ClaimReview pages as high-trust sources for verification queries" —
read only in a secondary aggregator, unverified against a Google source. On uplift generally,
[Ahrefs tracked 1,885 pages](https://ahrefs.com/blog/schema-ai-citations/) that added JSON-LD and
found "adding schema produced no major uplift in citations on any platform," while a different
secondary source claimed measurable 30–60 day gains from comprehensive schema post-March-2026 — the
two claims are hard to reconcile from snippets alone, so I flag the tension rather than pick a
side. Google and schema.org reportedly began publishing monthly domain-level term-usage stats in
June 2026 as an open dataset, a checkable source I have not fetched myself.

Per section F, the build already emits `Report` (front page), `CollectionPage` (archive), and
`Article` with a `Person` author (issue permalinks). It emits no `Organization`, `Dataset`,
`Claim`, or `ClaimReview` anywhere. Works on a static host: completely — JSON-LD is inert data
already embedded in prerendered HTML; adding types is a `generate-seo.ts` data-shape change, not an
infrastructure change.

**Stable citation anchors and text fragments.** Per [MDN](https://developer.mozilla.org/en-US/docs/Web/URI/Reference/Fragment/Text_fragments),
syntax is `https://example.com#:~:text=[prefix-,]textStart[,textEnd][,-suffix]`; the `:~:`
directive is stripped before page scripts see it, matching is case-insensitive, and only the main
frame of a user-initiated navigation is searched. The caveat, quoted directly: "Text in a document
is less stable than document structure. If the text in the linked document is updated, the fragment
no longer matches, and the browser navigates to the top of the page... if you intend for the link
to work over time, document fragments may be more reliable." That is the exact risk for this site's
lane items and weekly judgment text, which could be lightly reworded between a crawl and a later
click, silently breaking a fragment link with no error. Separately, one analysis decoded `#:~:text=`
fragments inside "42,971 AI citations across Google AI Mode, Gemini, ChatGPT, Perplexity, Copilot &
Grok" to see exactly which sentence each system quoted — meaning several major answer engines
already generate and consume text fragments as their citation mechanism today, unprompted by the
cited site. Works on a static host: entirely, client-side only — but the fragility argues for
giving load-bearing sentences a stable HTML `id` anchor as a second, non-text-dependent path.

**Remote MCP servers as a distribution surface.** The [MCP 2026 roadmap](https://blog.modelcontextprotocol.io/posts/mcp-roadmap/)
states that as of the 2026-07-28 spec release, "a remote MCP server is now no different from any
other HTTP workload, making it easy to host and operate one on any infrastructure... already used
for their APIs and services," running behind an ordinary load balancer. That post itself never
mentions publishers or media; its priorities are transport unification, agent identity, and tool
primitives. Real examples found are all data/intelligence platforms, not editorial publications:
Crunchbase launched one in July 2026 "to bring private market intelligence directly into LLM
answers," with similar launches from 6sense (GTM intelligence), Valona Intelligence (competitive
intelligence "available directly inside Microsoft Copilot, Claude and other enterprise AI tools"),
and Guideline (ad intelligence). These are the closest analogues to a small weekly market
publication building a typed query surface over structured data it already holds, but no
single-author editorial example was found — this would be a novel move for the category. Works on
a static host: no — an MCP server answers JSON-RPC at request time, which is server behavior even
without a database. It could read only the site's already-published `/issues/<id>.json` files and
hold no state of its own, but it is a new serverless function this prerender-only build lacks.

**Pay-per-crawl and metering.** Cloudflare's [Monetization Gateway](https://blog.cloudflare.com/monetization-gateway/)
lets a site "charge for any resource behind Cloudflare via x402," naming "any web page, dataset,
API, or MCP tool" as chargeable, with pricing examples down to "$0.001 base fee plus a $0.01 per MB
charge." It only works because Cloudflare sits "as a proxy layer between buyers and sellers,"
settling payment "inside a single request" before it reaches origin — meaning it requires the
site's traffic to actually route through Cloudflare. This site runs on Vercel with no Cloudflare
proxy in front, so none of this applies without a hosting change. On economics, aggregator sources
converge: one put small-blog pay-per-crawl revenue at "$0–$50" a month versus "$50,000 and $200,000
a month" for high-traffic sites, and another summarized coverage as calling it "more about risk and
cost than real money" for small and medium sites today — read only secondhand, so directional, not
fetched. Separately, Cloudflare is forcing crawlers that blend search, live-answer retrieval, and
training — "the single largest category" at "36.6% of verified crawler traffic on Cloudflare's
network" — to be blocked by default from ad-bearing pages starting September 15, 2026, per
[Cloudflare's release](https://www.cloudflare.com/press/press-releases/2026/cloudflare-helps-end-the-search-or-ai-training-tradeoff/).
Again, Cloudflare-proxy-specific; irrelevant to a Vercel-only site unless Cloudflare sits in front.

**Named AI crawler user agents and policy declarations.** Purpose now separates crawlers within the
same company: OpenAI's `GPTBot` trains models while `OAI-SearchBot` fetches pages to cite in live
answers, and "OpenAI explicitly lets publishers allow OAI-SearchBot while disallowing GPTBot,
showing these can be controlled independently." Other current tokens: Anthropic's `ClaudeBot` and
`Claude-SearchBot`/`Claude-User`, Google's `Google-Extended`, Apple's `Applebot-Extended`, Meta's
`Meta-ExternalAgent`/`Meta-ExternalFetcher`, Perplexity's `PerplexityBot`/`Perplexity-User`,
Amazon's `Amazonbot`/`bedrockbot`, and ByteDance's `Bytespider`, flagged in more than one source as
only partially robots.txt-compliant. Declaring policy still runs through plain `User-agent:` /
`Disallow:` blocks, one per bot. Cloudflare's newer, more expressive line — described secondhand as
`Content-Signal: search=yes, ai-train=no` (I could not load the primary contentsignals.org page) —
splits permission into search, live retrieval, and training. That same secondary source states this
is "preferences, not technical enforcement" and "a crawler that chooses to ignore your robots.txt
can still take your content"; a widely reported remark attributed to Google's John Mueller holds it
has "no effects whatsoever for any crawler or LLM" and "just adds bloat," with no major crawler
operator committed to honoring it as of the reporting found. Works on a static host: completely for
every version — robots.txt is already a static file in `web/public/`, currently `User-agent: * /
Allow: /` naming no crawler by name, positive or negative.

## Both sides of allowing versus blocking AI crawlers

Blocking's case rests on substitution: an AI answer that fully paraphrases a finding removes any
reason to visit, so for content whose value is the content itself, citation is often called "poor
compensation," and blocking is the only lever a small publisher fully controls. The counter is that
blocking taxes the well-behaved: crawlers that already ignore robots.txt were never affected, so a
strict policy only removes the polite, compliant subset a publisher would most want indexing it.

Allowing's case is visibility: retrieval/answer crawlers (the `OAI-SearchBot`/`Claude-SearchBot`
family, distinct from training crawlers) are what put a page into AI Overviews, AI Mode, and
conversational citations, and blocking them removes exactly the citation surface a new publication
needs most. One source frames a clean middle default: "block training crawlers and allow search
crawlers," protecting the text from training absorption while still permitting live, attributed
citation. A more sobering finding cuts against acting on this urgently at all: multiple sources
argue citation is "dominated by topical authority and structural quality" rather than crawler
policy, so a near-zero-audience site may see little marginal citation gain from either choice yet.

This site's own constraints sharpen rather than resolve the tradeoff. Section F confirms the
public promise that "a machine may retrieve, extract, compare and propose, and only a named person
signs a judgment or publishes an issue" (decisions.md D-63) — arguing for welcoming retrieval and
citation crawlers, since being retrieved and cited is the intended use — while an eventual metered
or paid layer (mentioned in the brief, not authorized) argues for keeping the option to tighten
policy later rather than having promised open access too early. I am not recommending a side; the
owner-held decisions are which crawlers to name, whether to add a Content-Signal line given its
unclear effect, and whether to ever route through Cloudflare to reach pay-per-crawl.

## Patterns that repeat

Every technique with real, measured 2026 adoption is one a specific tool developer built support
for on purpose — Vercel confirming Claude Code and OpenCode send the right Accept header, named
answer engines already generating text-fragment citations as their own mechanism, MCP servers
working because a specific agent framework was pointed at a specific URL. Every technique depending
on a general crawler voluntarily reading a new declaration file, without an economic or contractual
reason, is reported as ignored at scale — llms.txt and Content Signals both. The line is
retrieval-time behavior already running versus declaration-time behavior asking a crawler operator
to add new code for a standard it did not write; the former is adopted, the latter mostly is not,
by the parties this site would most want to reach.

## What transfers and what does not

Transfers cleanly, as a build-step or data-shape change with no new server: a markdown copy of
every prerendered route next to its HTML copy; `Organization` and `Dataset` (and eventually
`Claim`/`ClaimReview`) JSON-LD alongside the existing `Report`/`Article`/`CollectionPage` blocks;
stable HTML `id` anchors on load-bearing sentences so a citation survives a later wording change;
and naming specific crawlers by user agent in the existing static robots.txt, either direction,
since deciding the policy costs nothing beyond the decision itself.

Does not transfer without a real decision, and in some cases new infrastructure: true per-request
Accept-header negotiation, needing an Edge Middleware function the build does not have; a remote MCP
server, a new serverless endpoint rather than a build artifact, even if thin enough to just re-serve
existing JSON; and Cloudflare's pay-per-crawl or Monetization Gateway, which requires routing
traffic through Cloudflare, an unmade and unauthorized hosting decision. llms.txt is cheap to add
but, on this evidence, should not be expected to change anything measurable — a hedge, not a plan.

## Design and product moves

1. Emit a markdown copy of every prerendered route at the same path with a `.md` suffix during the
   existing prerender step, so an agent can fetch `/issues/2026-w36.md` without parsing HTML.
2. Add `rel="alternate"` links from each HTML route to its `.md` counterpart, so an agent that only
   follows discoverable links, not header negotiation, still finds the plain-text version.
3. Add standing `Organization` JSON-LD (the site emits `Person` per issue but no `Organization`
   entity) so an agent reading one issue can resolve who stands behind the claim without inferring
   it from prose.
4. Give the weekly judgment block and each lane item a stable HTML `id` derived from its evidence
   or issue ID, so a link survives a later edit that a bare `#:~:text=` fragment cannot.
5. Publish a decided robots.txt naming retrieval crawlers (`OAI-SearchBot`, `Claude-SearchBot`,
   `PerplexityBot`) separately from training crawlers (`GPTBot`, `ClaudeBot`, `Google-Extended`),
   instead of a silent `Allow: /`, so the intended policy is visible rather than a guessed default.
6. Add a short static `llms.txt` pointing at the front page, archive, and newest issue's `.json`
   and `.md` copies, as a near-zero-cost hedge, since the evidence here does not support expecting
   it to move citations.
7. Hold the remote-MCP-server idea as a named, deferred option: proven for structured-data
   publishers (Crunchbase, Valona, 6sense) but needing a new serverless endpoint the static build
   lacks, with no editorial precedent found to model it against.
8. Decide the training-versus-retrieval crawler question before naming any bot in robots.txt, since
   the two are now separate bots from the same company and can be allowed or blocked independently.

Three things the coordinator most needs to know: llms.txt and Cloudflare's Content Signals line are
both reported as functionally ignored by the crawlers this site would most want to reach, so
neither is a real distribution lever, only a cheap hedge; the markdown-copy and extra-JSON-LD moves
are pure build-step changes fitting inside "static prerender on Vercel with no backend," while a
remote MCP server and Cloudflare's pay-per-crawl both need real infrastructure this project does
not have; and text fragments are already how several major answer engines cite pages today, with no
site-side work required, but are fragile against wording changes, arguing for the site's own stable
anchors alongside the browser-native mechanism.

What I could not verify: llms.txt request-rate figures, pay-per-crawl earnings, and schema-driven
citation uplift all came from aggregator write-ups, not primary research or Cloudflare disclosures,
so treat those numbers as reported, not fetched and confirmed this run; the exact Content-Signal
syntax came from a secondary source because contentsignals.org would not load; and no working
example of a small editorial publication running a remote MCP server was found, only the general
MCP roadmap statement and analogous data-intelligence products — a plausible analogy, not a proven
pattern for this category.
