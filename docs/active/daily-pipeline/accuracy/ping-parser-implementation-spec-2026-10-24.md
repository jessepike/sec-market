# Ping release parser preview candidate

The current request authorizes implementation and offline proof only. The source registration, candidate identity, market contract, allowances, and production remain unchanged.

Implement `ping-release-pagination-v1` only for `ping-identity:official:1`, supplier `ping-identity`, family `official_announcements`, HTML index `https://press.pingidentity.com/news-releases`, exact host `press.pingidentity.com`, and at most 60 pages. Read static `wd_newsfeed_releases` / `ul.wd_item_list` / `li.wd_item` cards and their title links and strict day dates. Dated root paths, including literal commas, are allowed only through these cards. Card dates are scheduling signatures, never article publication metadata or effective event dates.

Follow only literal `wd_page_links` controls. Require the active marker to match the requested ten-item offset, validate sequential numbered links and ellipsis gaps, previous/next destinations and agreement, and retain the highest advertised page. Canonical root metadata does not collapse page 2. Reject ambiguous structure, unsafe URLs, duplicates, date conflicts, future dates against one immutable traversal time, loops, skipped controls, and cap exhaustion.

The observed article-path alphabet permits letters, numbers, underscores, hyphens and literal commas. Percent escapes, decoded separator/dot-segment tricks, literal separators, dots, backslashes and controls are unqualified and held. The captured heads have no `link rel=next` or `rel=prev`; any such unqualified head signal holds discovery, including a same-index signal. No head pagination URL is ever queued.

Only actual pages 1 and 2 are qualified for parsing. No terminal or empty layout has been observed. Every otherwise valid page without a next link therefore returns an explicit unproved-terminal hold, preserving its items. Missing page 3 after the retained two pages preserves exactly 20 items with incomplete discovery. Page 25 is an observed advertisement, not a hard-coded maximum or terminal proof.

Use the independently verified b9f1208b archive, manifest `5480056315f07d6c6be4e66d5f9a643437d020eb039f2d51fe378ad70803c9bb`, only as read-only input. Dedicated tests replay exact body hashes and observations, deny network and state writes, exercise structural/date/URL/paging counterexamples, and run existing Orca/general regressions in OrbStack. Generic article parsing is unchanged. This candidate grants no semantic admission, registration, source freshness, or coverage credit.
