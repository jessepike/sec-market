# PR Newswire issuer window parser: proposed offline build

Accepted for the separate offline build on October 25, 2026, under the owner's continuing source-qualification instruction. This unit builds a pure parser and a retained-proof verifier for two existing issuer distribution streams. The retained pages contain the list, ordering, pagination and primary sample evidence needed to test it without another request. Root will assign the isolated build separately; operational activation and normal-intake integration remain a later reviewed unit.

## Scope and activation boundary

The only sources are `cato:official:1` and `chainguard:official:1`, both existing candidate `release_distribution` bindings on `www.prnewswire.com`. Their exact index roots are `https://www.prnewswire.com/news/cato-networks/` and `https://www.prnewswire.com/news/chainguard/`. These streams do not satisfy official announcement, independent reporting or investor/acquirer obligations by substitution.

The build is offline only. It changes no operational caller, market contract, source registry, diagnostic plan, seed, baseline, correction stamp, admission, cache or policy. It makes no source or model requests and supplies no qualification, freshness, coverage or publication credit. Root owns any later activation and normal-intake specification after the separately reviewed J transition. That later unit must preserve exact forward/inverse policy equality and original evidence joins. Acceptance of this proposal, passing parser tests and a positive retained proof do not activate either source.

## Actual evidence and immutable joins

Use acknowledged archive `9e4a9806fdcc1b7cd6f91314b8b4ff4bb4ef2174`, manifest SHA-256 `148842177a7e7d9a5fd5c2ea4574576264a957b41958ee4cdf5effa80ea029c2`, with 48,420 authenticated entries. The frozen VM extraction is `/var/tmp/smp-listing-pagination-actual-40193925490-20261025/extracted`. Every body below is an immutable file at `<extraction>/state/objects/<body SHA-256>`.

Actual run `40193925490`, application `5debbd9e3ed855d9c6f5bda25468dac1371532d6`, retains the original 8,977-byte `ac7393` plan and charged observations. Its artifact is `12599212414`, ZIP SHA-256 `bbeebd3b706d01c21c6631b20e9f50afa36b74de3cb847ea706d6f82a9b0132c`. The two first pages retain their earlier actual run `40190857026` records, `3077` raw plan, charged rows and original clocks. Replay both complete original records and their original raw plans with the unchanged verifier. Current disabled operational bytes must never replace an archived raw plan during replay.

The accepted actual audit is `/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/narrow-listing-pagination-actual-source-review-2026-10-25.json`. Its companion Markdown and the 49 sealed receipts under `accuracy/receipts/narrow-listing-pagination-actual-2026-10-25/` remain unchanged. Derive a distinct, versioned proposal proof from those inputs. The relevant receipts are `listing-card-pagination-inspection.json`, `primary-supplied-jsonld-and-reuse.json`, `retained-primary-detail-reuse.json` and the original report/observation graph. Authored proof JSON cannot replace those external actual inputs.

| Retained page | Body SHA-256 | Bytes | Original response clock on 2026-10-25 UTC |
|---|---|---:|---|
| Cato root | `b061ee4f5831e2f53cb4b2f19708f225160a6a932ee6c18f93b5d15fb5edb7a8` | 225,773 | 11:59:13.911738 |
| Cato page 2 | `f1aec25583e4165a460cdd8704dcfa3756d7cfd8d0ab6a106966332dc5a99d6c` | 223,473 | 12:41:50.008505 |
| Cato page 3 | `8da8bbadc370c91fa843fb8b08c0659aba81dd564d891a6a00346416ebfd996a` | 219,907 | 12:41:56.591188 |
| Cato page 4 | `e0a46b24bd18b9de944654df18ad3bd3b9d5eea5b160feef615fae0b6d5cdafb` | 222,633 | 12:42:01.067330 |
| Cato page 5 | `2ba79bd09d90877cb1d147234eddde48ede5162da7722392854c553cbf93761e` | 230,402 | 12:42:07.614477 |
| Chainguard root | `eebdec361111f3a6c7d53ec34f0c9a314e7e2a8fce74086ea0bb7dd409e68c0f` | 243,971 | 11:59:15.734685 |
| Chainguard page 2 | `13e00b76b06ee3e9a42b2e1660bd827ee8bfdf300104bc6df979211bdef399a1` | 236,549 | 12:42:16.928575 |

## Recognized publisher layout and ordering evidence

The parser must recognize this closed layout in the actual bytes, rather than search arbitrary document text for an issuer or the word Latest:

- There is one `main#main.headline-listing[role="main"][tabindex="-1"]` and one issuer `h1` inside its `section.container`. The heading's direct text, excluding its one `small` boilerplate child, is exactly `News from Cato Networks` or `News from Chainguard` for the declared source.
- The same main region contains one `section.container > div.row > div.col-md-8.col-sm-12 > div.card-list.card-list-hr.nativo-section`. Its one `h2.section-header` has the direct heading `Latest` and an empty `small` child.
- Each list row is `div.row.newsCards[lang] > div[role="group"][aria-label="News Release"].card`, with the two observed card class variants `card col-view` and `col-sm-12 card`. Within that same card, one `a.newsreleaseconsolidatelink.display-outline.w-100[href]` contains one `h3` and one date `small`. The exact URL, title and written date must bind to that card. Keep correction titles and localized release paths intact.
- The pager path under the same main is `section.container > div.row > div.col-sm-12 > div.toolbar-container > div.pagination-bar > div.page-list.pull-right > nav[aria-label="pagination"] > ul.pagination`. Read its active page, numbered links and previous/next controls as one closed region. A terminal next control requires the actual `li.disabled` containing `»` with no link.

These are byte-backed paths. The following zero-based offsets identify the literal opening tokens in the body files above. They are fixture locators, not fixed offsets required of future responses. The Latest offset points to the literal text; card and pager offsets point to their identifying attribute text.

| Body | `<main` | `<h1` | `Latest` | First `newsCards` | `aria-label="pagination"` |
|---|---:|---:|---:|---:|---:|
| Cato root | 153143 | 153298 | 157176 | 157351 | 197327 |
| Cato page 5 | 153282 | 153437 | 157315 | 157490 | 201946 |
| Chainguard root | 153131 | 153286 | 157160 | 157335 | 216675 |
| Chainguard page 2 | 153138 | 153293 | 157167 | 157342 | 209253 |

The recognized issuer, explicit Latest heading, connected pager and observed nonincreasing card dates together support a bounded publisher-list ordering contract for these exact two streams. This is an inference about the recognized stream and declared daily window. It does not establish universal website recall or guarantee that an unseen page can never change ordering. A changed layout or observed ordering violation must leave the proof incomplete. The actual body class includes `page-404`; that class alone does not override the retained HTTP 200 observation.

## Separate daily-window completion from historical enumeration

Use an explicit source-bound dated-window mode. Existing terminal-based HTML modes keep their behavior. Expose `dailyWindowComplete` separately from `historicalEnumerationComplete`.

Cato pages 1 through 5 contain 125 unique same-card URLs with valid nonincreasing written dates, from July 5, 2022 through October 7, 2026. The current window contains October 7 and October 6, followed by September 8, 2026 as the first strictly older boundary; the other 123 observed cards are older. Cato page 5 remains nonterminal. Its retained controls disclose pages 6 through 8, and older unseen history remains unknown.

Chainguard pages 1 and 2 contain 47 unique URLs, with valid nonincreasing written dates from June 2, 2022 through October 14, 2026. Five cards fall in the current calendar window. Page 2 has active page 2 and an explicit disabled next control without an href, giving a structural end to the captured issuer stream.

A verified ordered prefix that reaches a strictly older calendar day can complete the declared daily window under this recognized ordering contract. Retain all 125 Cato and 47 Chainguard known historical URLs in the proposal inventory. A daily-window stop must never be relabeled as full historical enumeration. Additional Cato page requests solely to exhaust older history are outside this build and are not a prerequisite silently added to D-112.

## Pure parser and proof contract

Accept explicit source identity, exact requested page URL, original response bytes and an as-of clock. Return every observed card with its source/page/card position, exact URL, headline, raw written date, parsed calendar day if available, and unresolved issues. Expose the observed pager and pending literal continuations separately. Bound input size and page/card counts using reviewed constants derived from these fixtures; no network traversal belongs in this unit.

Require safe same-host issuer navigation with the exact supported `page=N&pagesize=25` form. The first observation is the nonquery root. Its literal query page 1 backlink is navigation evidence only. Active page must match its transport URL. First-page canonical metadata points to the issuer root. Numbered-page canonical metadata is exactly the same issuer root plus `?page=N`, without `pagesize`. Head previous/next metadata uses that same metadata-only page-number form (or the root for a previous page 1). Bind its page numbers to the body pager while retaining every literal value. Body pager request destinations remain exactly `?page=N&pagesize=25`; metadata-only URLs grant no request authority. Preserve exact request/final transport identity and all ordinary primary canonical checks. Do not normalize arbitrary URLs, queries, locales or redirects.

Require written dates to be NONINCREASING within each page and across connected pages: each next parsed written date/time must be less than or equal to the preceding one. Equal written dates and equal timestamps are legal, including across a page boundary. Duplicate dates alone are never a rejection reason. Reject duplicate URLs, conflicting dates for the same identity, issuer/scope crossover and any increasing date order. Reject hidden, inert, decoy or ambiguous card/pager structures and conflicting identity/metadata rather than selecting a convenient variant.

A daily-window proof must cover the complete preceding card sequence and a positive strictly older boundary. Validate all supplied pages and preserve their complete inventory even if the sufficient boundary is on page 1. Unknown or unresolved dates cannot establish order or an older boundary. An omitted card, unresolved ordering, changed layout, missing continuation/terminal evidence, or an interrupted input sequence leaves completion false. An empty shell or missing count cannot certify quiet. Structural rejection may retain the raw observation plus diagnostic inventory; it must never silently discard an unresolved URL.

## Calendar dates, boundaries and future records

Match the accepted Q4 date-only behavior. Let `day` be the explicit as-of instant's UTC calendar day and `cutoff = day - 30 days`. Retain original strings and literal `ET`; do not infer an index UTC offset from that abbreviation or copy a primary sample's supplied offset onto index cards. The result has calendar-day precision and unknown index timezone.

Classify valid dates inclusively: `cutoff <= calendarDay <= day` belongs in `currentWindowItems`; dates strictly before cutoff belong in `historicalItems`; every valid future day belongs in `undeterminedWindowItems`. Mark cutoff day, as-of day and next calendar day in `boundaryAmbiguousItems`, while keeping cutoff/as-of items in the inclusive current list. A date later than the next day also carries `FUTURE_PUBLICATION_CALENDAR_UNRESOLVED` in `sourceDateAnomalies`. A valid future calendar date is retained, never dropped or rejected merely because it is future. Impossible calendar values fail validation; missing or unrecognized dates remain represented in unresolved inventory and make the ordering/window proof incomplete.

No boundary marker silently removes an item. Unknown/future items remain explicit candidates or holds and prevent a quiet claim. Quiet requires a complete recognized daily window, no current items, no undetermined or unresolved items, and a positive older boundary. The actual September 25 through October 25, 2026 calendar window has no supplied boundary-day ambiguity in these two retained lists. These are calendar-window results, without a claim of exact UTC interval recall.

## Existing primary samples: reuse original evidence

Use the retained same-issuer primary bodies. Recompute the canonical/request/final join, unique heading, readable article container and supplied metadata from frozen bytes. Require the exact index card URL and written publication-day join. Preserve all supplied identity/publication/modification fields and any disagreement. A modification date may legitimately differ from publication; that difference alone is not a conflict or a replacement publication date. The limited older shape guard's empty `dateMetadata` array did not inspect all JSON-LD; the later actual inspection retains those supplied fields and must remain separately attributed.

Chainguard's sample is `https://www.prnewswire.com/news-releases/chainguard-announces-280-million-growth-financing-from-general-catalyst-to-usher-in-next-era-of-trusted-open-source-software-302592279.html`, source `chainguard:citation:TR-chainguard-2`, body `f9629a0df62bacd7ae19421dbcb95edcd79d1dfb306e9d240514e15bc299a6a3`. Its original full HTTP 200 clock is `2026-10-25T06:46:06.412965Z`. Supplied JSON-LD `datePublished` is `2025-10-23T11:00:00-04:00`, matching the October 23, 2025, 11:00 ET card.

Cato's sample is `https://www.prnewswire.com/news-releases/cato-networks-raises-359-million-at-a-valuation-of-more-than-4-8-billion-302494283.html`, source `cato:citation:TR-cato-1`, body `2fe0e900031f29fcc0cbf1a8fbc371f48e57bcb59aaa42aa3dbbe7af54728173`. Its original full HTTP 200 clock is `2026-10-24T18:29:41.178689Z`. Supplied JSON-LD `datePublished` is `2025-06-30T06:00:00-04:00`, matching the June 30, 2025, 06:00 ET card.

Those offsets come from the primary bodies themselves. Preserve actual HTTP 304 revalidation and its older full-body origin as separate observations, with every original clock unchanged. No repeat GET is needed for this offline proof. Primary shape proof supplies no financial claim validation, new fact/event or independent semantic admission.

## Required verification and tests

Expose a pure page parser and retained-proposal derive/verify interface. Verify the original actual run/raw plan/report/reservation/observation/body graph and external audit identity before accepting a positive retained proposal. Bind complete known inventory, source role, ordering evidence, pager paths, primary samples, clocks and output schema. All archive reads use read/get-only adapters with sockets and frozen `LocalStore` construction denied. No writer, model client or lease/budget mutation belongs in the test harness.

Required positive tests include both actual sources, equal written dates within one page, equal timestamps, and equal dates across a connected page boundary. These positives must preserve both distinct URLs and titles. Required negative tests include duplicate URLs even when dates agree; conflicting dates for one URL; increasing dates within/across pages; wrong issuer/source/host/path/query/page/page size; crossed card title/date; hidden/inert/decoy cards; omitted boundary/card/known historical URL; active-page mismatch; false disabled-next/terminal; scope crossover; unsafe localized-path normalization; altered original record/raw plan/reservation/clock; and rehashed self-authority.

Test missing/unknown dates as retained unresolved inventory with incomplete proof. Test impossible calendar values as validation failures that retain diagnostic evidence. Test inclusive cutoff/as-of membership, next-day boundary marking, farther-future anomaly retention and every case's inability to create false quiet. Test that a daily-window stop leaves Cato history incomplete, while the actual Chainguard page 2 terminal can establish its captured finite enumeration. Conflicting primary publication/modification metadata must stay visible and fail a claimed consistent sample join when it is inconsistent.

Run the appropriate existing old-mode and six-admission regression checks without changing H's 557 obligations, four fact references, 38 holds, ordinary source clocks, transport acceptance or caps. Preserve the sealed actual report and raw diagnostic outputs. The resulting proposal can be reviewed; any operational qualification and normal receipt remain dependencies of root's later activation unit.

## Strongest countercase

A Latest heading and observed nonincreasing sequence do not prove every unseen page's behavior. The proposed source-bound contract accepts that bounded publisher-layout inference for daily discovery and fails closed on changed structure, identity, ordering or unresolved dates. Independent review must assess those exact retained issuer/Latest/card/pager bytes and the stated inference. If they are insufficient, name the missing source-specific ordering proof. Do not replace that question with a universal requirement to exhaust the entire website or invent an undisclosed API.


## Observed layout refinements accepted during the isolated build

Root accepted the following corrections to the proposal's layout shorthand. All are read from the seven pinned retained bodies above. The implementation receipt `observed-layout-refinements.json` records every original canonical/previous/next opening tag with its byte offset and length, all card variant counts and every language/path pair per page. These corrections grant no operational authority.

The two card wrapper class sets are exactly `card col-view` and `col-sm-12 card`; unknown variants fail. A localized heading may place its title in one leaf `span.langspan[lang]` after the date `small`; the span language must equal its row language, and a second or conflicting title location fails. Plain direct heading text remains the other observed title variant.

For Cato, the observed language/path pairs are: `en-US` with `/news-releases/`; `il` with `/il/news-releases/`; `fr` with `/news-releases/` or `/fr/communiques-de-presse/`; `de`, `no`, `fi`, `sv` and `da` with `/news-releases/`; and `nl` with `/nl/persberichten/`. For Chainguard they are `en-US` with `/news-releases/` and `in` with `/in/news-releases/`. These are inventory-only literal paths. Unknown source-specific pairs fail; no locale translation, URL rewriting or primary document-fetch permission follows.

Cato's exact retained funding primary also contains a self-closing `ul` language-menu token with `class="dropdown-menu" role="menu" aria-labelledby="langauge-dropdown"` inside `div.dropdown.lang-switch` in the release header, beside the heading. Only the offline primary structural reader recognizes this exact retained token/context. It changes no global HTML reader or browser behavior; it cannot hide publication metadata or supply the inspected heading/body. Self-closing script/inert/critical structural tags remain rejected. All retained primary body pins still bind before positive proposal proof.

The known-seed union contains 127 Cato URLs: all 125 observed list URLs plus two separately retained `/il/` ARR seeds absent from that list. Their supplied primary publication dates are February 24, 2026 (`2026-02-24T15:30:00+02:00`) and July 27, 2026 (`2026-07-27T15:30:00+03:00`). Both precede September 25, 2026 and supply no observed current-window counterexample. Preserve their actual full-body origins and real HTTP 304 chains. Cato's source-scope gap remains explicit. Chainguard's observed 47-URL list contains its one known seed. Operational readiness is pending separate scope review and normal-intake activation; incomplete older history alone is not a new permanent prohibition under D-112.
