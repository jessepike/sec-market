# Follow-up seven-target response review

Status: archived response review and proposed next request plan. No source is qualified or activated by this document.

## Recommendation

Use the existing leased, budgeted diagnostic path for the seven literal pagination URLs below. Then build narrowly bound pagination adapters from the retained responses. Keep Ping, Delinea and Sonatype as candidates until complete traversal and article/date validation have independent evidence. The seven next responses can settle important layout questions, but cannot themselves prove full history coverage.

This review makes no requests and adds no collection, qualification or semantic credit. The 74-supplier roster and all 557 obligations stay unchanged. The old policy's 244/557 report remains an old policy report. The diagnostic is separate from the regular v2 collector and does not prove a scheduled collection ran.

## Evidence and boundary

Actual diagnostic `40066513321`, attempt 1, ran on application revision `7e17e22a1ba2c88db5cb4ab2012b752cfd55da2c`. Its seven explicit requests returned HTTP 200 between `2026-10-24T05:33:09.399894Z` and `2026-10-24T05:33:11.050765Z`; requested and final URLs matched. The complete diagnostic charged 124 requests, including these seven: fetches moved 641 to 765, while model calls stayed 80 and documents stayed 40. Those are actual diagnostic counters, not requests made by this review. Every explicit result remains unqualified, with no facts or coverage credit.

The authenticated archive is:

`/var/tmp/smp-followup-probe-20261024/archive-892d9ffb/jessepike-sec-market-892d9ffb809173be57eaf2729272dc06b3be798d`

Its manifest hash is `2b43aebcb8fad6153a712f28793c1c86f253dc6ed23f2c69651d64dd40605f86`. Root independently verified all 31,266 entries and preservation of all 31,075 previous paths, with no immutable changes or removals. Root's verification receipt is `/var/tmp/smp-followup-probe-20261024/archive-verification.json`. This review separately matched all seven bundle observation/body files to their exact archive references and manifest hashes/sizes. It checked the bytes and modification times of the bundle and the 20 archive entries it used before and after guarded analysis. No archive or state was written.

The accompanying JSON records exact observation/body references, result-row hashes, retained RSS comparisons, literal anchors, current candidate bindings, code hashes and a fully specified proposed seven-target plan:

`/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/followup-seven-target-response-review-2026-10-24.json`

That JSON's `reviewSha256` hashes its canonical content with that field omitted. It is a review receipt, not a collection or admission receipt. Source HTML is untrusted content; this review inspected its structure and did not execute its scripts or follow instructions in it.

## Ping: terminal layout observed, middle traversal still missing

The page at `https://press.pingidentity.com/news-releases?o=20` is page 3. Its release list contains ten distinct cards, from August 18, 2025 through September 25, 2024, in descending date order. The exact static structure is `div.wd_newsfeed_releases`, `ul.wd_item_list`, `li.wd_item`, title link under `.wd_title`, and date under `.wd_date`. The active marker is 3, previous is `?o=10`, next is `?o=30`, and the numbered controls disclose pages 4–9 and 25. Each page intentionally declares the common canonical `https://press.pingidentity.com/news-releases`; that must not collapse distinct traversal request URLs.

The page at `https://press.pingidentity.com/news-releases?o=240` is page 25. It contains two cards dated January 17 and January 2, 2018. Its active marker is 25, previous is `?o=230`, and its `wd_page_start` control links to page 1 at `?o=0`. The `wd_page_next` child is a span containing `»`, with no href. This is concrete terminal-layout evidence. It is not evidence that pages 4–24 were traversed.

The source-bound Ping layout parser accepts page 3 when given an explicitly labelled, in-memory proposed HTML-index context. It rejects page 25 with `Unknown Ping page role`: `wd_page_start` is not allowed. Its later directional-control rule also does not yet accept this disabled next span, and discovery separately holds `PING_TERMINAL_LAYOUT_UNPROVED`. The actual contract remains a candidate `official_discovery` source at `https://press.pingidentity.com/`; passing the in-memory layout check does not change that declaration.

The retained earlier page-1 and page-2 bodies plus these new page-3 and page-25 bodies contain 32 distinct card URLs. There are still 21 missing intermediate pages, 4 through 24. The smallest adapter change is to extend the existing exact Ping mode for the observed start link and disabled terminal span, accepting completion only after a consecutive traversal reaches the independently advertised final page. Keep numeric-offset, date-order, card-size, canonical, host, duplicate and page-limit checks. Do not hardcode 25, accept a jump to the last page as traversal, or accept any missing next control as terminal.

## Delinea: an undated HTML archive with a moving page window

`https://delinea.com/news` has 12 article cards. Each authoritative card title/link is under `article.blog-index__post h2.blog-index__post-title a.blog-index__post-title-link`. A separate image-wrapper link repeats the same article URL; it must not become a second inventory entry. No card has a publication-date node. These card dates remain unknown.

The canonical is exactly the index URL, and the advertised RSS URL is `https://delinea.com/news/rss.xml`. Head `rel=next` and the `nav.blog-pagination` next link both name `https://delinea.com/news/page/2`. The active page-1 anchor has `aria-current=true`; numbered links disclose pages 2–5. The previous anchor has the disabled class and no href. Page 5 is the edge of the observed page window, not a proved terminal page; a later page may expose more numbers.

The retained RSS contains ten entries whose URLs are the exact ordered prefix of the HTML's twelve URLs. Five RSS titles differ from the corresponding HTML titles. For example, RSS calls the second entry `2026 Identity Security Report: The AI Enforcement Gap`, while both the HTML index and full article H1 use the longer report-findings title. Preserve both strings and their source references; do not silently turn one into the other or use the ten-entry feed as a complete archive.

The two fetched full articles have exact requested/final/canonical identity and H1s matching the HTML cards. Their visible opening datelines are October 21, 2026 and September 29, 2026. The generic article parser produces `published=null` for both. The datelines support a future source-bound date extractor with explicit text provenance; they do not themselves admit claim dates or make undated HTML cards dated. RSS timestamps, transport `Last-Modified`, and visible article datelines remain separate observations.

The smallest adapter is a Delinea-only HTML pagination mode: select the title anchors once, retain unknown card dates, require head/visible next agreement, validate active/numeric window controls, and traverse sequentially until a newly observed, validated terminal layout. Do not infer that missing structured publication metadata means old or quiet content. Article dateline extraction needs a separately tested, unambiguous primary-content rule, retaining the original day and evidence pointer.

## Sonatype: dated cards with a query-based archive

`https://www.sonatype.com/press-releases` contains 16 cards under `div.listing__grid-card`. Each has a title in `h3`, its article link at `a.pr_link`, and a displayed date in `div.card-content__meta p`. The observed dates descend from October 14, 2026 through October 15, 2025 and use full month names. These are index-date observations, not independently verified publication or effective dates for every article.

The canonical is the root index, and RSS is advertised at `https://www.sonatype.com/press-releases/rss.xml`. `div.pagination` has active page 1, literal numbered links for 2, 3 and 13, and a visible Next link to `?page=2`. There is no head `rel=next`. Page 13 is only an advertised terminal candidate until its actual response and the intervening traversal are checked.

The initial Prev link is `/press-releases?page=0#resource-grid`. It is an invalid backward request for this initial page, not a URL to fetch after stripping the fragment. A source-specific initial-layout rule may recognize and ignore this exact control; the request allowlist must continue rejecting fragments, page zero, loops and arbitrary query shapes.

The ten retained RSS URLs are the exact ordered prefix of the HTML's sixteen URLs. All ten RSS titles differ from the longer or differently worded HTML titles. The first full article has an exact canonical and an H1 matching the HTML card; its visible dateline is October 14, 2026. Its generic `published` is also null. The JSON retains each RSS title/timestamp and HTML title/date separately. A card date is not authority to overwrite a conflicting article dateline.

The smallest adapter is a Sonatype-only HTML query-pagination mode, with exact title/link/date regions, full-month calendar parsing, active/Next numeric agreement, a validated terminal layout and sequential traversal. Keep the current host, body, duplicate and maximum-page limits. A source-bound full-article date rule must reject ambiguous or conflicting publication evidence rather than borrowing a convenient index date.

## Proposed next bounded request batch

All seven URLs below appear literally as anchors in the successful new responses. The JSON binds each to the exact result index, result-row hash, original observation/body/time, immutable diagnostic record and the prior raw-plan object reference. It avoids copying a nested prior plan into every target.

| Proposed target | Literal URL | Disclosed by | Purpose |
|---|---|---|---|
| Ping page 4 | `https://press.pingidentity.com/news-releases?o=30` | New page 3 | Next sequential page |
| Ping page 5 | `https://press.pingidentity.com/news-releases?o=40` | New page 3 | Consecutive middle-page structure |
| Ping page 6 | `https://press.pingidentity.com/news-releases?o=50` | New page 3 | Consecutive middle-page structure |
| Delinea page 2 | `https://delinea.com/news/page/2` | New news index | First next-page structure |
| Delinea page 5 | `https://delinea.com/news/page/5` | New news index | Establish whether the numeric window moves |
| Sonatype page 2 | `https://www.sonatype.com/press-releases?page=2` | New press index | First next-page structure |
| Sonatype page 13 | `https://www.sonatype.com/press-releases?page=13` | New press index | Inspect advertised terminal layout |

I would choose this batch because it tests both immediate next-page behavior and the unresolved archive boundaries without repeating the seven successful requests or spending model capacity. The diagnostic remains fetch-only. Its full workflow also performs generic probes under the shared budget, so a plan with seven explicit targets does not mean the whole workflow costs seven requests. Existing budgets, runtime deadlines and reservations still govern every actual request.

The exact proposed plan passed the existing `validate_qualification_probe_plan` against a write-denying archive adapter and an in-memory plan path. All seven targets were recognized as literal HTML links under current market policy `79cdd19b962ee3adbb5d9e1a43cbc389b3c9196a6c0a2105ea455c8bd70f9f60`. This proves plan/provenance compatibility only. It did not write the committed plan, reserve a request, dispatch a workflow, fetch a URL, qualify a source or call a model.

## Qualification and activation prerequisites

Current candidate declarations are required `official_discovery` roots, with `maxPages=60`. The normal collector returns `SOURCE_BINDING_UNVERIFIED` before requesting them. Generic diagnostic probes do not implement these three complete archive traversals. Adding a proposed adapter or source row cannot manufacture its qualification evidence.

An agent-owned implementation must therefore supply the dedicated bounded qualification path first, using the existing lease, reservation and transport guards. It must retain actual root/next/terminal bodies, prove exact source and supplier scope, exercise full traversal and validate article identity/date handling. Only a separately justified verified declaration enables normal daily collection. A stopped traversal at a limit, failed page, undisclosed next URL, unexplained duplicate, changed layout or date conflict stays incomplete. Full archive discovery and current intake remain separate from historical document processing and full claim review under D112.

Any adapter/source registration change alters the market contract. The complete diagnostic root plan must move atomically to that new policy with a justified proof migration. The existing historical-probe bridge permits only the two-field D112 reporting separation; it cannot authorize substantive source, alias, adapter or policy changes. The associated factual-correction outer policy stamp and projection also need verification after a changed global contract, while all six existing group review hashes, rows, dates and admissions must replay unchanged or receive their own review. Do not repeat activation with a current root plan wrapping incompatible old proof policy.

Before implementation acceptance, cover the retained positive layouts and negative cases: Ping terminal start/disabled-next controls plus omitted intermediate pages; changing Delinea page windows and conflicting head/visible next links; Sonatype page-zero/fragment controls and false terminal pages; duplicate or foreign article links; missing or ambiguous card regions; title differences without URL substitution; unknown or future dates; and full-article canonical/dateline conflicts. Successful parser tests are mechanical evidence, not actual qualification or semantic admission.

No runtime, contract, source declaration, committed plan, model output, state head, archive or production artifact was changed for this review. Its only outputs are this document and its JSON evidence companion.
