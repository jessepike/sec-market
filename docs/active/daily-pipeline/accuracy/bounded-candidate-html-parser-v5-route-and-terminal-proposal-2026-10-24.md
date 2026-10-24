# Bounded candidate HTML parser V5 route and terminal proposal

Status: proposal only. I recommend a new Delinea V5 mode for its evidenced terminal layout and a Sonatype V5 mode containing one exact literal lead exception. Keep Ping V3 and all original V1–V4 interpretations unchanged. This document changes no code, source registration, policy, plan, quota, or state.

## Actual evidence and limits

Actual run `40079036392`, application revision `4b5e5ec1669ddad052c6320ddf4a4dffdb9c1f5e`, checked at `2026-10-24T08:45:25.560536Z`, charged 63 fetches, moving the daily ledger from 1,375 to 1,438. Calls remained 80 and documents remained 40. Its report records Ping complete at 25 pages/242 URLs, Delinea terminal unproved at 25 pages/290 URLs, and Sonatype incomplete at 10 pages/144 accepted URLs. There is no model, source-check, qualification, semantic, or publication credit.

The retained artifact is `docs/active/daily-pipeline/receipts/bounded-traversal-v4-source-probe-result-2026-10-24.json`, SHA-256 `e9df8e17a8beab4bac96e5d242d704c6217bacaa7e37c5884d712940e509c6b8`. Root authenticated the full archive `e467ab000b8225931d6684eb6d0aa39bbba1f6c9`, manifest `ce989f357ecda7ef5a460ad96ceededf6a8f4b1cd566a408eb6ba79f3a4fad70`, with 35,790 entries, all 35,592 preceding entries retained, 198 additions, zero immutable changes, and unchanged protected heads/seals. The full actual replay is a separate audit. This proposal independently recomputed the target body/observation hashes and inspected their parsed card and pagination regions.

| Original observation | Wrapper SHA-256 | Raw observation SHA-256 | Body SHA-256 / bytes |
|---|---|---|---|
| Delinea `https://delinea.com/news/page/25`, `2026-10-24T08:45:20.525288Z` | `554019de06c09188a3baff39908e70b34bc88e05e28a0f2358789d8363ba41fe` | `c9b0f83b5fa526f234a30d697638a97db1a1a7cc52b2ae358f574160109115f1` | `2cbb9f7c9da6ecbe9205efd1212833d77b7344b8766891d4a545728cf677526d` / 116,667 |
| Sonatype `https://www.sonatype.com/press-releases?page=10`, `2026-10-24T08:45:25.132878Z` | `dc9976331735f1c33d9381c615bab23d2918bd3b7b294b02b9a971a1f3383c4e` | `06448daa708f46af60aad6f15f27ca45268846fafc730134a1c00fe406ba14a8` | `9b94a74c28bfee4c52761c5730c567e0fd61b64604c6f4df8e8851afb05abf74` / 139,090 |

Both are nonredirected HTTP 200 observations from the exact source-bound index request. Their original objects, times, and failure interpretation remain unchanged.

## Delinea: positive terminal grammar

The final body has two recognized official title/image cards. Its single `nav.blog-pagination` has `role="navigation"` and `aria-label="Pagination"`. The numbered window is exactly 21, 22, 23, 24, 25; 25 alone is active with `aria-current="true"`. The visible previous link and head `rel="prev"` both point to `https://delinea.com/news/page/24`. There is no head next link. The terminal control has this structure, with its decorative SVG omitted:

```html
<a class="blog-pagination__link blog-pagination__next-link blog-pagination__next-link--disabled">
  <span class="blog-pagination__link-text">Next</span>
</a>
```

V5 may return `terminalProved=true` only after all existing exact source, host, canonical, card, title/image, duplicate, raw URL, and pagination checks pass, plus these positive terminal checks:

1. Exactly one scoped next anchor has the exact three classes above, label `Next`, and no `href` attribute. Missing next, an empty `href`, contradictory classes, duplicate controls, a hidden extra destination, or unknown interactive descendants remain incomplete.
2. No head-next signal exists. The non-disabled visible previous and the sole head-previous agree on `currentPage - 1` under the existing safe index grammar.
3. The active page is the last numbered page. For this evidenced multi-page terminal layout, the five numbered controls are exactly `currentPage - 4` through `currentPage`, with the same active and safe destination checks. Do not invent a one-page or arbitrary empty terminal layout.
4. The current page equals the highest advertised page retained across the entire traversal. An earlier advertised higher page cannot be forgotten when the numbered window moves.
5. The recognized card region contains 1–12 nonempty, valid cards. Empty markup, JavaScript shells, malformed cards, or navigation text cannot establish quiet completion.

This is a structural rule, not a hard-coded page number, inventory size, body hash, or daily qualification hash. At the captured page 25 it recognizes the positive terminal control. Other unobserved terminal layouts remain incomplete. Source-level completion still requires every consecutive page from the index root with no missing, duplicated, unsafe, or conflicting response, followed by the existing primary-sample and final time/day/budget checks. V4 must continue to replay this exact page as terminal unproved.

## Sonatype: one exact raw-lead exception

The failing URL is genuinely the `a.pr_link` of a recognized `listing__grid-card`; its first earlier appearance in a debug list outside the card is not the evidence. Its literal URI is:

`https://www.sonatype.com/press-releases/resources/state-of-the-software-supply-chain-2022/establishment-and-expansion-of-software-supply-chain-regulation-standards`

The card title is “Sonatype Nexus Delivers Advanced Staging; Further Simplifying DevOps-Native Software Development” and its displayed date is `July 9, 2018`. The URI's `2022` component does not establish a primary publication date or prove that the card points to the intended article. The card-to-target identity is unresolved. Exact requested-URL and final-URL observation searches in the authenticated immutable object store identified no retained primary response for this target.

In Sonatype V5 only, allow this exact path through the existing exact-host, HTTPS, raw-literal, no-query/fragment, card-region, duplicate, and date-order checks. Preserve the literal URL unchanged. Do not accept a general `/press-releases/resources/` subtree, arbitrary deeper paths, nearby report sections, encoded equivalents, or guessed replacement URLs. Keep the complete V4 direct/two-segment grammar unchanged for every other URL.

This adds the publisher-advertised URL to raw discovery inventory only. Existing index dates become `itemModified` scheduling signatures; they are not semantic event dates. Preserve the displayed `2018-07-09` scheduling value without replacing it with `2022` or a guessed date. The URL stays unreviewed/pending processing under existing D-112 behavior. This proposal creates no new implemented hard hold, contradiction count, model prohibition, or semantic authority.

I recommend a V5-only pure-parser diagnostic annotation for this exact card, containing the literal URL, observed card title, displayed index date, and a fixed reason such as `PUBLISHER_CARD_LINK_REQUIRES_PRIMARY_REVIEW`. If implemented, the bounded caller and historical verifier must serialize and independently reconstruct that annotation from the original body; otherwise it must not be described as durable report evidence. Existing typed normal inventory retains URL/provenance and scheduling signatures, not this proposed annotation. Blocking future model processing on the annotation would require separate engine integration; no such block is claimed here.

The agent-owned follow-up is to obtain the exact literal target's primary bytes through the existing reviewed leased diagnostic path, then compare its canonical, heading, readability, and actual date metadata. That work must preserve the publisher card claim separately and cannot silently substitute another URL. There is no owner policy decision needed to inspect that evidence.

## Earlier page 13 is feasibility evidence only

The authenticated original Sonatype page-13 start-proof body is `7af5acbbd1aa77e6d5819b03d682e1c41ad692583516f24a573806e0e25fec8d`, 137,035 bytes, fetched at `2026-10-24T06:18:06.058227Z`. Pure V4 parsing at that original clock recognizes 13 cards, no additional unsafe article routes, current/highest page 13, no next URL, and the existing positive Sonatype terminal. All 13 displayed dates are `2018-07-02`; they remain scheduling metadata.

This historical isolated page cannot complete the current page-10 failure, stand in for current pages 11/12/13, or renew any source date. It only shows that another route expansion is not justified by that retained page. A future V5 run must traverse its own complete current sequence and retain its own observed terminal.

## Version selection and required acceptance

Use explicit integer `parserRevision: 5` with the exact tuple Ping V3 / Delinea V5 / Sonatype V5 and new derived adapter hashes only for the changed sources. Primary shape reuses revision 3. Add the exact fixed tuple to both main origin binding and sparse explicit-page adapter validation; preserve complete adapter-context equality and the empty activation authority registry. Unknown, Boolean, floating-point, downgraded, mixed-mode, or altered-context plans must reject before transport. Do not widen the D-112 policy bridge or change any actual source declaration.

Required offline acceptance includes the two exact hash-pinned bodies, unchanged full actual V1–V4 reports, all earlier partial inventories and original dates, and the prior page-13 check above. Negative cases must include Delinea's disabled flag with an href, an omitted or duplicated next control, false active/last numbering, a previously advertised higher page, head/visible conflicts, empty cards, and missing intermediate pages. Sonatype must reject adjacent resources paths, unsafe URI syntax, an outside-card-only occurrence, and any inferred primary date or credit. If the diagnostic annotation is added, test omitted, altered, or self-reported annotations against body replay and keep prior report schemas unchanged.

The live diagnostic remains bounded by 60 index pages and one primary sample per source, 183 total logical requests, the shared mutation lease, reservation-before-fetch, current-day/deadline guards, archive compare-and-swap, and the unchanged 5,500-fetch cap. Calls/documents remain 80/40; no model allowance is created. No extra primary sample or different sample-selection rule is authorized by this proposal. A later exact primary-body diagnostic must fit its own reviewed existing operation and budget.

The strongest case against the Sonatype exception is that the publisher link is wrong: retaining it can complete a URL inventory while leaving the intended 2018 announcement unidentified. The narrow exception is preferable to discarding known evidence because it preserves the exact lead and unresolved processing state. It cannot support a claim that the linked article, historical event, or its date has been validated. Delinea's stronger positive terminal markup supports its own bounded structural rule; it supplies no authority over Sonatype or article facts. The 74 suppliers, 557 obligations, original review verdicts, registrations, correction groups, and published coverage remain unchanged.
