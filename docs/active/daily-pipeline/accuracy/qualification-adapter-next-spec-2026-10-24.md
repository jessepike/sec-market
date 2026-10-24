# Proposed next qualification adapters

Status: proposal only, October 24, 2026. This document authorizes no implementation,
registration, request, policy, allowance or workflow change. Keep all 74 suppliers and 557
obligations. Search/navigation work remains separately queued.

## Recommended scope

Use an explicit Ping HTML release-index adapter as the authoritative discovery path. Use
its RSS as retained agreement evidence. A five-item rolling feed cannot replace the full
advertised release history. Decide Delinea and Sonatype's smallest adapter only after their
actual feed bodies arrive. A successful diagnostic response alone qualifies none of them.

The committed `contracts/source-qualification-probes.json` has seven exact targets. Its raw
SHA-256 is `163e439adf2d383d9aa47d7a8c3a00ba4d75e31149a20b012c2a8772211496cf`; canonical
SHA-256 is `f66db4b9a9f97542136c000f1c660036de38b5a77fbd0dcb3ea958edc54f04ba`.
The seven logical reservations obtain evidence, not coverage. No new response from that
batch is assumed here.

## Existing proof and remaining responses

The read-only archive is `4b325ab62385379c9d76b585ee3c3575ba8cab4d`; independently verified
manifest `3bebbef137b62f331b218fbf947bff25ca00a5bebf45bb3441dace9fd1fe619e`.
Exact observation/run references, body sizes and original times are retained in the committed
plan and `source-qualification-spec-2026-10-24.json`.

| Targets | Retained evidence | Evidence the new response must supply |
|---|---|---|
| `ping-index`, `ping-rss`, `ping-next` | Ping root HTML body `d06c171a9aa6c5150e47355692dbdecdaacc544a15ce7fd01bbc6812883007be`, fetched `2026-10-24T00:23:18.322865Z`, literally advertises the canonical index, RSS and next page. | Exact canonical index response, refreshed RSS, and actual page 2 with matching page/card controls. |
| `ping-october-release`, `ping-september-release` | RSS body `906b1656404e95d8ed52082ecfd40d738e2ff24368ab6638cda810d4e38055a8`, fetched `2026-10-24T00:23:19.389251Z`, has both literal links and zoned publication dates. | Readable first-party article bodies joining supplier, title, canonical URL and publication metadata to those entries. |
| `delinea-rss` | Delinea citation body `40d3a81783abdf0af16f21d191d1b0e5e2393e7bf42bcc3e4147d87c271b2fb4`, fetched `2026-10-23T04:14:59.819592Z`, advertises `https://delinea.com/news/rss.xml`. | The actual feed body, its publisher/entry scope, publication fields, retention range and continuation disclosures. |
| `sonatype-rss` | Sonatype citation body `0797efe21e3568cbb309a739affe457a236ecc6de41c9752f5172f29bb32b7ea`, fetched `2026-10-23T04:14:51.574093Z`, advertises `https://www.sonatype.com/press-releases/rss.xml`. | The same feed-specific proof, restricted to Sonatype's official press stream. |

The retained Ping index has ten descending cards, October 6 through March 24, 2026. Its
five RSS items exactly match the first five cards. October 6 and September 29 fall within
the September 24–October 24 scheduling window. The root advertises page 2 at
`https://press.pingidentity.com/news-releases?o=10` and page 25 at `?o=240`. Page 2,
terminal pagination and the two new article bodies are absent from this retained evidence.
The seven-target batch therefore cannot alone prove the full advertised traversal.

## Smallest Ping change, conditional on the new bodies

Add one explicit `ping-release-pagination-v1` mode in `discovery.py`, with exact source/mode
validation in `contracts.py` and dedicated offline tests. A later reviewed binding would use
`ping-identity:official:1`, supplier `ping-identity`, family `official_announcements`, kind
`html_index`, host `press.pingidentity.com` and canonical index
`https://press.pingidentity.com/news-releases`. Preserve the current 60-page cap. Keep the
candidate registration inactive during code preparation.

1. Read only the observed `wd_newsfeed_releases` region and its `ul.wd_item_list` /
   `li.wd_item` cards. Require one nonempty `wd_title` link and one valid `wd_date` per
   recognized card. Accept dated root article paths only from those title links. Index URLs,
   navigation, footer links, RSS URLs, scripts and templates never become article items.
   This exact mode supplies the article-path contract; do not widen the generic prefix
   filter to `/` or add fallback extraction.
2. Read the actual `wd_page_links` navigation, its `wd_page_active` current marker and
   `wd_page_next` anchor. The next control belongs to the enclosing list item, not an
   anchor `rel=next`. Require numbered-page and next destinations to agree, advance by
   the observed ten-item offset, and stay on the exact canonical index path with only
   the qualified offset query. Follow literal links only. Page-size alternatives are not
   continuation. Reject loops, gaps, conflicting markers, foreign paths and unknown controls.
3. Retain the highest advertised page across traversal. Exhaust every advertised page;
   terminal success requires its actual qualified layout, no next or higher page/ellipsis,
   and the final current marker matching that retained maximum. The captured root only
   justifies the nonterminal rules. Qualify terminal rules from a real terminal body before
   registration; never hard-code 25 or a daily-changing terminal hash. Missing pages, cap
   exhaustion, empty/JavaScript layouts and unproved terminal layouts remain incomplete.
4. Parse card dates strictly as `%b %d, %Y`; reject invalid/future dates, conflicting duplicates
   and unproved ordering changes under an immutable traversal as-of time.
   Return them as `itemDates` and `itemModified` scheduling signatures, as the existing
   Orca adapter does. Preserve every discovered item. The existing 30-day collection window
   prioritizes work; it does not permit stopping pagination or discarding older inventory.

For qualification, compare the actual RSS entries with the corresponding HTML cards before
set deduplication: URL, title, GUID and zoned `pubDate` must be unambiguous. Detect conflicting
repeated entries. Retain the original time offset; compare a card's day with the publisher
calendar day, without inventing a timezone for day-only HTML. A truncated response, stale
disagreement or missing corresponding release holds qualification. The known five-item feed
may be a proper prefix of the longer HTML history. Do not change generic RSS parsing for Ping if
HTML remains the active discovery authority.

## Delinea and Sonatype: evidence-gated minimum

The current `xml_links` function keeps RSS/Atom URLs and explicit next links but drops entry
publication dates. It can also return complete after a rolling feed with no continuation.
Neither behavior proves complete supplier history. Broad sitemap `lastmod` is only a work-order
hint; Delinea's 7,106 sitemap URLs and Sonatype's 6,849 are not a complete official-release scope.

If actual bodies justify RSS/Atom collection, add a small explicitly bound dated-feed mode for
these exact source/host/endpoint identities. Read only the observed entry layout and publication
field: qualified RSS `pubDate` or Atom `published`, with strict timezone/date parsing. Preserve
`updated`/`lastmod` separately as modification hints. Missing publication fields must not acquire
inferred dates from slugs or retrieval time. Admit only actual official release entry paths;
Delinea's `/news/` and Sonatype's `/press-releases/` are leads requiring body confirmation.

Follow only actually disclosed, same-host continuation under an independently qualified page
contract and existing cap. If the feed rolls off history, obtain the literal official news-index
or archive links and their full traversal before selecting an authoritative endpoint. Never
invent page URLs or substitute the generic corporate sitemap. No terminal/empty-feed rule is
yet evidenced for either company. Retain their known historical seeds and pending inventory.

## Acceptance and holds

An actual source qualification receipt must retain every request/final URL, source/supplier join,
original observation time, raw body hash/size, exact parser version, complete continuation path,
publication-date provenance and terminal proof. A redirect or blocked/malformed response remains
explicitly held. Reuse never renews a source date. Synthetic success grants no registration credit.

Offline regressions must include card isolation, date/entry conflicts, timezone boundaries,
matching and conflicting pagination, missing/unsafe pages, loops, caps and actual archived
counterexamples. A synthetic quiet case uses a complete recognized older release inventory,
with every required document independently resolved. An arbitrary empty feed or page cannot
establish quiet. Replay new actual bodies unchanged, then run existing pipeline and ops checks.

Source qualification and task completion remain separate. Historical documents still require
the existing bounded audit, normal semantic evidence checks and available allowance. Retained
successful history remains held where its proof has not been independently rebound. Today the
recorded 80 model calls and 40 documents are exhausted; a fetch-only diagnostic cannot clear
those obligations. Do not discard history, alter the 557 denominator or label discovery alone
as a successful current check. All next evidence and parser actions are agent-owned; no owner
source choice is presently required.
