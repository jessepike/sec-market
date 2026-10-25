# Actual Q4 controller evidence and next requests

Date: 2026-10-25. This is a static evidence review and a recommendation for a future diagnostic operation. It is not an executable plan or source admission.

## Recommendation

Capture exactly two API responses, one for JFrog and one for Rapid7, using the GET requests below. The retained controller and each original HTML configuration establish these requests without guessing a Q4 convention. Stop after those two responses and review their raw bytes. Rubrik needs additional controller evidence before an API request can be specified.

The current six-script operation cannot execute this recommendation. Its closed path list permits only the two script filenames. The ordinary schema-1 qualification route requires a literal HTML link, feed, canonical, or RSS/Atom item; it does not derive API requests from JavaScript. Both proposed `/feed/` paths are also outside these candidates' ordinary discovery scope prefixes. A separately reviewed, closed diagnostic operation must bind the original HTML proof, actual controller observation and body, exact query, and unchanged source identity. Keep the shared writer lease, budget reservations, time/deadline/cancellation checks, response limits, and zero qualification, fact, model and coverage credit. No additional request is authorized by this document.

## Actual evidence

The actual capture ran on app revision `99617db0f0ef4c70bb6f0b563cac9a40c50e0385` in run `40179255547`. The acknowledged archive is `9634b916c15b18f38605a168f7642de764670aab`; its manifest SHA-256 is `600e58564c989206856ba48795bf4ce9f6fbbf73a604e806594e95327b53203a`. The authenticated extraction is `/var/tmp/smp-q4-controller-actual-20261025/extracted`.

All six captured responses were HTTP 200 JavaScript at their exact requested URLs. Each host returned the same API body, SHA-256 `2ce36889709b0c9ff34e2b657d5abe0600009604d7e5407d41198f9a9c72d5e7`, 25,534 bytes, and the same pager body, SHA-256 `4e9d26dabe182ce0694a7e892892b5dc24a502cf14ee1b251542c9b920796a79`, 7,642 bytes. These are observations of the scripts, not observations of the API responses proposed below.

An independent read/get-only replay of `q4_controller_capture.verify_report` passed with sockets and LocalStore construction denied. It returned six captures, zero qualifications, zero source checks, no facts, no semantic admission and no coverage credit. The focused replay preserved the original HTML proofs and their original October 24 clocks. The companion JSON retains every actual script request/response clock and all 30 consulted file seals. The implementation worker owns the complete 45,307-entry archive audit.

## Exact derived requests

Both requests use GET with no request body and the exact path `/feed/PressRelease.svc/GetPressReleaseList`. The controller declares `contentType: "application/json; charset=utf-8"` and expects JSON rather than JSONP. This declaration does not prove the response MIME or that either request succeeds.

| Query field | JFrog | Rapid7 |
|---|---|---|
| `LanguageId` | `1` | `1` |
| `bodyType` | `0` | `0` |
| `pressReleaseDateFilter` | `3` | `3` |
| `categoryId` | `00000000-0000-0000-0000-000000000000` | `1cb807d2-208f-4bc3-9133-6a9ad45ac3b0` |
| `pageSize` | `-1` | `-1` |
| `pageNumber` | `0` | `0` |
| `tagList` | empty string | empty string |
| `includeTags` | `true` | `true` |
| `year` | `-1` | `-1` |
| `excludeSelection` | `1` | `1` |

The exact target URLs, using one explicit query serialization, are:

```text
https://investors.jfrog.com/feed/PressRelease.svc/GetPressReleaseList?LanguageId=1&bodyType=0&pressReleaseDateFilter=3&categoryId=00000000-0000-0000-0000-000000000000&pageSize=-1&pageNumber=0&tagList=&includeTags=true&year=-1&excludeSelection=1
https://investors.rapid7.com/feed/PressRelease.svc/GetPressReleaseList?LanguageId=1&bodyType=0&pressReleaseDateFilter=3&categoryId=1cb807d2-208f-4bc3-9133-6a9ad45ac3b0&pageSize=-1&pageNumber=0&tagList=&includeTags=true&year=-1&excludeSelection=1
```

The query order is an explicit proposed serialization; no browser API wire request has been observed.

The original HTML defines `GetViewType()` as `'2'` and `GetLanguageId()` as `'1'` on both pages. The retained `_usePublic` test therefore selects the public branch. Each page invokes `.q4News` with its literal category above, `limit: 0`, `tags: [""]`, `fetchAllYears: false`, and `loadShortBody: 0`. The API defaults provide `getYearFilter: true`, `skip: 0`, `loadBody: false`, `url: ""`, and `excludeSelection: false`. `_getYears` first invokes `_fetchItems(-1)` when the year filter is enabled and the limit is zero. The empty tag is filtered out. These joins produce all ten query values above.

The initial operation does not call the separate year-list endpoint. Rapid7's `showAllYears: false` affects the displayed selection after data returns; it does not change this initial `year=-1` request. JFrog's `showAllYears: true` likewise introduces no additional request at this step.

All following offsets are zero-based byte offsets in the exact retained UTF-8 body; the companion JSON includes the literal excerpts and lengths.

| Evidence | Body SHA prefix | Byte offset |
|---|---|---:|
| Public-branch decision | `2ce36889709b` | 3686 |
| Initial year-filter request | `2ce36889709b` | 5667 |
| Language parameter | `2ce36889709b` | 6643 |
| GET/POST transport choice | `2ce36889709b` | 6991 |
| Item query construction | `2ce36889709b` | 7778 |
| News endpoint, result field and parser | `2ce36889709b` | 20638 |
| JFrog widget configuration | `ead58a93ed20` | 56217 |
| Rapid7 widget configuration | `9ece5b105eb6` | 40568 |

The pager contains local DOM item counting and `.slice(...)` display logic. It contains no `ajax`, `fetch(`, `XMLHttpRequest`, `/feed/`, or `/Services/` lexeme. JFrog's `perPage: 12` is display paging over returned items. It is not evidence of server pages of twelve. Rapid7's `perPage: 0` supplies no server-page contract either.

## Rubrik's missing join

Rubrik's retained HTML body is `c5a34d9cf87cd3e52f567fdf8883ca60e33f7e28a8923bc006469e91cd883a17`, 42,385 bytes. At byte 19407 it invokes `$('.module-news .module_container--widget').news(...)`. The captured evergreen API defines `evergreen.q4News`; it contains no `.news` implementation or legacy `q4.news` widget definition. Applying JFrog/Rapid7's request logic to this different call would be an unsupported assumption.

At byte 3956 the HTML literally discloses `https://widgets.q4app.com/widgets/q4.api.1.13.5.min.js`. That is a concrete dependency to inspect, but its `.news` implementation and request logic have not been captured here. Its host is outside Rubrik's unchanged `allowedHosts: ["ir.rubrik.com"]`. A future capture would need an explicitly scoped dependency-host allowance in its own reviewed diagnostic authority; the existing six-script operation cannot fetch it. No same-host substitute, proxy URL, Rubrik category, API method, request path, year or page parameters are established by the retained evidence.

## What the two API responses must resolve

The controller reads `GetPressReleaseListResult` and maps `Headline`, `LinkToDetailPage`, `PressReleaseDate`, `PressReleaseId`, `Category`, `TagsList`, and related attachment fields. It derives years through JavaScript date parsing. Raw response dates and any offset must remain explicit; this review supplies no missing timezone or date.

The code's `pageSize=-1` and `year=-1` values establish the request sentinels. They do not establish the server's cap, complete historical coverage, terminal paging, current-window completeness, ordering, successful JSON response shape, primary article validity, or a recurring adapter. Retain bounded raw response bytes, actual HTTP status/MIME/final URL and request/response clocks even on failure. A capped, truncated, malformed or refused response earns no completeness claim. Review actual item dates, scope, duplicates, total/terminal evidence and primary article links before selecting any subsequent sample request or proposing source qualification.

## Existing code boundaries

`web/scripts/pipeline/q4_controller_capture.py:16` fixes the six script paths; `validate_plan` at line 111 binds that closed operation to its original source and HTML proofs. `verify_report` at line 303 replays the actual retained capture. `web/scripts/pipeline/onboarding.py:529` through its literal-target check at line 551 require XML/HTML disclosure for schema 1. `web/scripts/pipeline/discovery.py:939` applies the normal source path scope. `ops/ci/collect.py:231` selects only the existing diagnostic routes. This review changes none of those surfaces, the operational plan, H, admissions, source clocks, budgets, or publication state.

Evidence companion: `/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/q4-controller-actual-code-next-requests-2026-10-25.json`.
