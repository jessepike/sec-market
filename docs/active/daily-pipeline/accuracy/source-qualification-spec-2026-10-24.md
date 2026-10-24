# Bounded source qualification after the actual probe

## Approved seven-target implementation details

The root reviewer approved only the bounded diagnostic extension. The implementation adds
`contracts/source-qualification-probes.json` with exactly seven unique target IDs and URLs,
the unchanged canonical market hash, expected HTML/RSS format, existing candidate source ID,
and exact retained disclosure records, observation and body hashes, byte counts and original
retrieval times. The five Ping targets use the archived immutable diagnostic run and its
source-bound observation references. The two company feeds use their original registered
same-supplier citation observations. No arbitrary URL argument is added.

The whole plan is checked before fetch escrow or any request. The validator checks every record and body
against its retained hash/size, the observation/source/supplier/host join, original timestamp,
HTTP 200 status, and the target's literal HTML link, advertised feed, recognized canonical
link or RSS item link. Entity decoding and relative URL resolution are allowed; constructed
endpoints and inferred publisher paths are not. Missing, malformed or tampered proof rejects
the whole explicit plan before generic or explicit transport. This validator only reads state.

The existing main `source_probe` path remains the caller. Its acknowledged lease, fetch-only
escrow, actual UTC-day guard, reservation-before-request and expected-commit finish/failure
checkpoints remain in force. Existing generic candidate probes may run, followed by at most
the seven exact planned requests. The explicit loop never follows newly discovered links.
It retains each charged result, full response/body references and explicit block, redirect,
format, deadline and allowance failures. It reports the plan's raw and canonical hashes and
all retained proof references. Every result remains unqualified, with zero source checks,
coverage credit, models, semantic admission and publication.

Synthetic tests cover every proof type, literal recognition, all-or-nothing preflight,
duplicate/extra targets, wrong source/supplier/host/timestamp/hash/body joins, blocked and
redirected responses, malformed XML/HTML, full allowance, day/deadline change, and a maximum
of seven explicit reservations. Existing leased-run tests use a fictional committed
plan and proofs while preserving their escrow, current-day, archive CAS and protected-head
assertions. The actual pinned plan was also validated read-only against the verified
archive, without fetching a target or changing state. No source adapter, parsing rule,
registration, market contract or workflow changes are included.

The cap is seven logical, reserved `Fetcher.fetch` calls, matching the existing budget
contract. The existing transport can retry selected server errors or follow redirects on
an allowed host. Those wire attempts are not new logical budget reservations. The explicit
loop adds no retry or continuation, and any changed final URL remains an unqualified
redirect result. The root reviewer confirmed this boundary; transport behavior is unchanged.

## Offline implementation verification

All 444 ops tests pass in OrbStack, including 13 focused diagnostic tests and 22 leased-run
tests, with zero skips. Invalid or missing final-row proof stops the whole plan before any
generic or explicit transport. Tests also preserve lease acknowledgement, fetch-only escrow,
UTC-day and deadline handling, failed archive CAS, original budget metadata and normal
collector heads. Malformed bodies, HTTP 403/429, transport errors and empty feeds remain
charged and unqualified.

The exact committed plan passed a read-only replay against archive
`4b325ab62385379c9d76b585ee3c3575ba8cab4d`, whose independently verified GitArchive manifest
is `3bebbef137b62f331b218fbf947bff25ca00a5bebf45bb3441dace9fd1fe619e`.
The plan raw SHA-256 is `163e439adf2d383d9aa47d7a8c3a00ba4d75e31149a20b012c2a8772211496cf`;
its canonical SHA-256 is `f66db4b9a9f97542136c000f1c660036de38b5a77fbd0dcb3ea958edc54f04ba`.
The unchanged market hash is `de1932f7698d6b5ec86c23da52e77b1440c34d368e101c2aaabcbae6b39abfbe`.

| Planned target | Actual retained literal recognition |
|---|---|
| `ping-index` | The Ping root HTML advertises the canonical news index. |
| `ping-rss` | The Ping root HTML advertises the exact RSS URL. |
| `ping-next` | The Ping root HTML advertises the exact next-page URL. |
| `ping-october-release` | The retained Ping RSS has the exact item link. |
| `ping-september-release` | The retained Ping RSS has the exact item link. |
| `delinea-rss` | The retained registered Delinea citation HTML advertises the feed. |
| `sonatype-rss` | The retained registered Sonatype citation HTML advertises the feed. |

All 30,823 state files have identical before/after content, size and modification time.
The replay content-manifest hash is `c47e33e88b4a7da5be706b01d6154e3f9ce8ae772af8de12640cdd560c2bc575`;
the size/mtime/content seal is `c5a6a7a993edfb5b5154c2a4ebaac09ecb5933a0789d8fe249f846c6aa26f33c`.
These replay seals use sorted relative file paths and are distinct from the GitArchive
manifest. The companion JSON retains the exact definition, both seals, all seven proof
records/body references and original retrieval times. Replay created no observations,
made no network or model request, changed no registration and credited no source check.

The implementation is ready for root review and atomic integration. A later real leased
diagnostic must obtain the seven new responses before any adapter or registration proposal.
The source qualification and history requirements below remain open.

## Original qualification proposal and historical probe state

The following proposal was prepared `2026-10-24T00:37:30.279502Z`. The actual leased diagnostic `40044528648` spent 117 fetch reservations, preserved 64 model calls and 33 documents, and left all 28 sources unqualified. Coverage at that receipt was 244/557. I would qualify the official Ping release stream first, then obtain the advertised Delinea and Sonatype RSS bodies. The later approval authorized only the seven-target diagnostic implementation above; it authorized no registration or source promise change.

## Actual probe evidence

Archive `c4650c2bf8ed2de87476deab6af5b572a8988e01`, manifest `42c1960c03056a34cc7acef864f4201bb6550d9424fb84f425c5e070bdf0bcc7`. All 29,776 files passed hash/size verification and retained their size/mtime seal. The ordinary collector, heartbeat, coverage, both snapshot heads, correction head and all prior collection-run records remain byte-identical to cc898. The ledger moved from 377 to 494 fetches, with exactly contiguous charged reservations 378–494. Remaining at this archive only: 5,006 fetches, 16 calls and seven documents. A newer collector archive supersedes those figures.

Twenty-four candidate results require scope/history review; two roots returned HTTP 403 and two stopped with ContractError. The latter two retain no error-specific response observation, so this audit does not invent their transport cause. Successful broad sitemaps and empty comment feeds do not establish supplier coverage. The JSON pins all 28 rows and their actual diagnostic observation objects.

## Ping: a working RSS body with qualification still pending

The official root was fetched `2026-10-24T00:23:18.322865Z` with body SHA-256 `d06c171a9aa6c5150e47355692dbdecdaacc544a15ce7fd01bbc6812883007be`. Its canonical index is `https://press.pingidentity.com/news-releases`. The dated item list has ten release cards in descending date order: October 6, September 29, September 1, July 28, June 16, May 27, May 5, April 28, April 22 and March 24, 2026.

The exact advertised RSS `https://press.pingidentity.com/news-releases?pagetemplate=rss` was fetched `2026-10-24T00:23:19.389251Z` with body SHA-256 `906b1656404e95d8ed52082ecfd40d738e2ff24368ab6638cda810d4e38055a8`. It identifies “Ping Identity Press Releases” and has five unique link/guid items with zoned pubDate fields. Its five URLs and publication days exactly match the first five HTML cards. Two fall in the current September 24–October 24 window; September 1 and the earlier cards bracket the old side.

| Publication day | Current-window literal primary article |
|---|---|
| 2026-10-06 | `https://press.pingidentity.com/2026-10-06-Ping-Identity-Survey-Finds-AI-Trust-Changes-When-Assistance-Turns-to-Action` |
| 2026-09-29 | `https://press.pingidentity.com/2026-09-29-Ping-Identity-Launches-Identity-Agents-on-Google-Cloud-Marketplace` |

The root literally advertises `https://press.pingidentity.com/news-releases?o=10` as both page 2 and the next page, and offset `?o=240` as page 25. Neither the next-page body nor these two primary article bodies was fetched by this diagnostic. The one-item Google sitemap points only to the news index. A five-item RSS response does not prove complete retained history by itself.

Current code prevents safe URL-only activation: the registered generic prefixes exclude Ping’s dated root article paths; RSS parsing discards pubDate; and generic HTML paging expects rel=next while the actual next control is class wd_page_next. These are concrete adapter/scope requirements, not owner choices. No quiet day can be inferred from zero items under the existing mismatched prefixes.

## Delinea and Sonatype

| Binding | Actual retained result | Literal RSS still needing a body |
|---|---|---|
| `delinea:official:1` | 7106 sitemap loc items; 281 under `/news/`. | `https://delinea.com/news/rss.xml` |
| `sonatype:official:1` | 6849 sitemap loc items; 205 under `/press-releases/`. | `https://www.sonatype.com/press-releases/rss.xml` |

Their current homepages did not lead this probe to those RSS feeds. The RSS addresses remain literally advertised in retained earlier company releases, with body/observation pins in the JSON. Broad sitemap lastmod values are modification signatures. They do not establish release publication dates, full feed retention or a quiet current window. Obtain each actual feed body before proposing its exact adapter or source change.

## Minimal next diagnostic proposal

Extend the existing guarded main source_probe path with a small committed qualification plan containing the following seven exact literal targets. Reuse the acknowledged mutation lease, fetch-only escrow, current-day reservations and expected-commit checkpoint. Accept no arbitrary URL input. Validate each target against the unchanged source’s existing allowed host and retained disclosure proof. Keep all diagnostics unqualified and non-admitting. Wait for the current normal collector’s terminal archive before another writer.

| Existing source | Exact next literal URL | Purpose |
|---|---|---|
| `ping-identity:official:1` | `https://press.pingidentity.com/news-releases` | Capture canonical dated index root; validate root response/canonical identity. |
| `ping-identity:official:1` | `https://press.pingidentity.com/news-releases?pagetemplate=rss` | Refresh exact official RSS and join pubDates/guids to root cards. |
| `ping-identity:official:1` | `https://press.pingidentity.com/news-releases?o=10` | Capture actual disclosed next page; prove monotonic ordering/continuation across the window boundary. |
| `ping-identity:official:1` | `https://press.pingidentity.com/2026-10-06-Ping-Identity-Survey-Finds-AI-Trust-Changes-When-Assistance-Turns-to-Action` | Capture exact current-window primary release; verify issuer/title/publication metadata. No automatic event admission. |
| `ping-identity:official:1` | `https://press.pingidentity.com/2026-09-29-Ping-Identity-Launches-Identity-Agents-on-Google-Cloud-Marketplace` | Capture exact current-window primary release; verify issuer/title/publication metadata. No automatic event admission. |
| `delinea:official:1` | `https://delinea.com/news/rss.xml` | Capture exactly advertised press/news RSS before any adapter or registration change. Missing body, retention and publication dates remain unproved. |
| `sonatype:official:1` | `https://www.sonatype.com/press-releases/rss.xml` | Capture exactly advertised press/news RSS before any adapter or registration change. Missing body, retention and publication dates remain unproved. |

The initial batch cap is seven logical requests. Any later continuation must be literally disclosed by a captured response and match the reviewed exact host, item and page structure, with a separately bounded cap. Keep blocked, redirected, malformed and missing responses explicit and charged. This proposal's bounded diagnostic extension has now been implemented and tested offline as recorded above. It has not been run against the seven real targets.

## Exact acceptance contract to prepare

For Ping, extract only real wd_item_list/wd_item release cards with a title link and nonempty wd_date. Require safe unique dated root release paths, date/path agreement and a stable publisher identity. Keep index and article paths separate. Parse RSS pubDate with timezone, retain it for selection and join feed items to the HTML prefix. Preserve existing event-date semantic review.

Validate actual next-page controls, active-page/offset agreement, a stable highest advertised page, nonincreasing dates across captured pages, no loops or duplicate conflicting items, and strict missing/unsafe/page-cap failures. Until an ordered current-window boundary is independently proved and reviewed, use conservative full traversal. Unknown or empty layouts stay incomplete. Quiet requires a complete proved traversal of recognized dated releases outside the window; a blank shell or empty filtered result cannot supply it.

The two current article bodies need actual publisher/date/subject joins before positive collection proof. Those body checks do not admit financial or other facts automatically. Delinea and Sonatype need their own actual feed/body/retention evidence before mode design. Preserve all existing historical pending items, 557 obligations and the full source meaning; never drop audit history to turn coverage green.

## Why the 17 existing tasks remain pending

The actual receipts schedule 33 documents across 17 sources: two each except eSentire, which schedules one. Overall usage was only 64/80 calls and 33/40 documents. These receipts do not report global allowance exhaustion. Their pending manifests contain 9,897 references: 9,259 with older lastmod, 637 with lastmod in the September 24–October 24 window, and one undated. Those are modification dates, not proved publication dates. Per-source limits and item-level review/redirect failures account for genuine deferred work.

| Existing source | Pending refs | Current lastmod | Older lastmod | Undated |
|---|---|---|---|---|
| `proofpoint:official:1` | 211 | 1 | 210 | 0 |
| `veeam:official:1` | 726 | 3 | 723 | 0 |
| `exabeam:official:1` | 636 | 25 | 611 | 0 |
| `hiddenlayer:official:1` | 87 | 0 | 87 | 0 |
| `optiv:official:1` | 179 | 2 | 177 | 0 |
| `aqua:official:1` | 448 | 1 | 447 | 0 |
| `mimecast:official:1` | 137 | 137 | 0 | 0 |
| `arctic-wolf:official:1` | 1296 | 14 | 1282 | 0 |
| `witnessai:official:1` | 241 | 23 | 218 | 0 |
| `expel:official:1` | 329 | 83 | 246 | 0 |
| `ivanti:official:1` | 428 | 2 | 426 | 0 |
| `reliaquest:official:1` | 90 | 76 | 14 | 0 |
| `upwind:official:1` | 974 | 176 | 797 | 1 |
| `sophos:official:1` | 636 | 25 | 611 | 0 |
| `snyk:official:1` | 54 | 54 | 0 | 0 |
| `esentire:official:1` | 170 | 0 | 170 | 0 |
| `dragos:official:1` | 3255 | 15 | 3240 | 0 |

There is also a separate selection-contract defect to review: `/Users/jessepike/code/projects/sec-market-finish-20261022/web/scripts/pipeline/selection.py:59` returns every inventory item except this run’s selected set, including already-audited items that are not due. Three actual pending entries already have audit stamps: one Exabeam and two Sophos entries. Their exact URLs, stamps and pending-manifest hashes are in the JSON. Therefore “historical pending” is not solely the count of unprocessed due work. Preserve their evidence and history while correcting that distinction; this report makes no runtime change or new coverage claim.

The broad counterparty inventories contribute 3,255 Dragos/Accenture references and 636 each Exabeam and Sophos references from the same Thoma press sitemap. A supplier-name work-order hint is not an entity filter. Any future narrower current-news stream must prove the complete supplier obligation and retain the original audit queue, rather than silently discarding unrelated-looking history.

## Limits and files

This review made zero source/network/model requests, admissions, real archive writes, code or market edits, registrations or publication attempts. The actual 117 reservations belong to the recorded diagnostic run, not this audit. No owner input is currently required.

Detailed proof and proposed rules: `/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/source-qualification-spec-2026-10-24.json`.
