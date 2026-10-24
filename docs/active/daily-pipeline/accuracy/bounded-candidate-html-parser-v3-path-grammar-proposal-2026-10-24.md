# Bounded candidate HTML parser V3 path grammar

Status: implemented parser specification. This work adds source-bound V3 parser modes only. It does not change the market contract, source binding, qualification plan, or runtime operation. V1 and V2 remain the interpretation for their original plans and receipts.

## Evidence from the current V2 run

The retained receipt for run `40075237236` records 49 charged requests, no source credit, and an incomplete traversal for all three sources. Each source's selected primary sample succeeded. The authenticated archive is commit `d161a23d80ea9e1756113644624cc2f646d2c3ed`, with manifest hash `09909886e98bd9f6be1ebe8da243f80b8af73352889a989a2093b96e89c92362`. Its 35,412 files include all 35,256 prior paths and 156 additions, with no immutable changes. The V2 diagnostic replayed exactly, the store had no mutations, protected heads were unchanged, and before/after file and directory seals match. The target-page bundle binds each page through the report wrapper, raw observation, and body reference. The three body hashes below were independently recomputed from that bundle.

| Source page | Body SHA-256 | Literal card link | Existing V2 rejection |
|---|---|---|---|
| Ping `https://press.pingidentity.com/news-releases?o=200` | `fb43c33de4629c766ac62e84895fa446e6d7d12513dfdaf6bb34fc7cff86cdef` | `https://press.pingidentity.com/2018-11-7-Global-Survey-from-Ping-Identity-Shows-Consumers-Are-Abandoning-Brands-After-Data-Breaches` | Date prefix uses a one-digit day; its card date is `Nov 07, 2018`. |
| Delinea `https://delinea.com/news/page/18` | `e4b5201c4f21e94415f203717ccc2f3000d68852fdef1c627bed9b84adf7e791` | `https://delinea.com/news/about-us/news/press-releases/2020/centrify-momentum-fueled-digital-transformation-including-secure` | Historical press-release route has fixed nested path segments and a year. The title and image links resolve to the same URL. |
| Sonatype `https://www.sonatype.com/press-releases?page=7` | `2e94dddf68d90a83fa76cb8bc264d5cb206ead4cf73a1358c2a884fc223ff7bf` | `https://www.sonatype.com/press-releases/sonatype-expands-solution-to-support-c/c-php-and-ruby` | The C/C++ article slug includes one literal slash. |

These examples establish that the current V2 path grammar rejects literal same-host links inside the existing source-specific card regions. They do not establish that a complete traversal is possible.

## V3 selection

Keep V1 and V2 behavior immutable. A future qualification plan must select the explicit parser revision and distinct source modes for all three bindings, and pin their adapter hashes. Only an absent revision uses the original V1 interpretation; an unknown revision must reject. No receipt is reinterpreted under V3.

The V3 parser must keep the existing exact source ID, supplier, family, index root, host, observed index pagination, card-region, title-link, duplicate, date-order, and control checks. Only source-specific article-path recognition changes. The article link must come from the existing recognized title-card region, never a pagination control. Delinea must continue to require its title and image links to resolve to the same literal article URL.

All three source grammars retain these shared URL checks:

- Resolve only the literal observed `href` against the observed index URL, then require HTTPS and the exact declared host.
- Reject credentials, non-default ports, query strings, fragments, control characters, whitespace, backslashes, percent escapes, empty path segments, and `.` or `..` segments.
- Keep index pagination URLs separate from article URLs. The article route grammar must reject reserved pagination/control path components and numeric-only page routes.
- An unrecognized path remains an incomplete parse. It is never accepted merely because its host is allowed.

The exact body examples do not require percent-encoded paths or other encoded punctuation. Keep percent escapes rejected unless a separately authenticated page demonstrates a legitimate encoded article URL and its decoding rules can be specified safely.

## Source-specific route rules to review

For Ping, retain the existing V1/V2 full-date and V2 compact-date forms. Add the observed form `/<YYYY>-<M>-<D>-<slug>`, where month and day use one or two digits and the slug uses the existing ASCII letters, digits, underscore, comma, and hyphen set. Parse the numeric prefix as a real calendar date and require it to equal the card's displayed date. Do not repair, normalize, or reconstruct the literal URL.

For Delinea, retain the existing single-segment `/news/<slug>` route and the V2 optional trailing hyphen. Add only the observed historical route form `/news/about-us/news/press-releases/<YYYY>/<slug>`, with the exact fixed path prefix, four-digit year segment, and one slug segment. This preserves the observed historical route without accepting arbitrary nested paths. Keep the existing same-URL title/image join.

For Sonatype, retain existing single-segment paths and the V2 `ai/ml` example. Add a strict two-segment article-slug form beneath `/press-releases/`, with each segment composed of lowercase ASCII letters and digits separated by single hyphens. Reject empty, numeric-only, and reserved control segments such as `page`, `pages`, `news`, and `press-releases`. This recognizes the observed literal `c/c-php-and-ruby` form without allowing arbitrary deeper paths or page controls.

If an authenticated page reveals a route outside these rules, retain that page as incomplete and add evidence before revising the grammar.

## Required validation before implementation

Before adding V3 code, verify the full archived commit and all unchanged archive seals. Then replay the three exact target bodies and confirm their report wrapper, raw observation, requested/final URL, timestamp, source adapter, and body hashes against the archived receipt. Tests should prove that V1 and V2 still reject these examples, V3 accepts only the documented route forms, and malformed dates, host changes, ports, credentials, encoded routes, query/fragment values, dot segments, empty segments, pagination controls, and arbitrary deeper routes remain rejected.

A V3 parse is only an index-page observation. It grants no source qualification, intake credit, semantic admission, registration change, or completeness by itself. A live V3 run must retain every request, response, timestamp, and reservation under the existing lease, and all three walks must independently prove terminal pagination before any activation review.

## Implemented checks

The V3 modes are `ping-release-pagination-v3`, `delinea-news-pagination-v3`, and `sonatype-press-pagination-v3`. `ping_article_date(path, mode)` supplies the exact full-path date parser used by the Ping adapter and may be reused by the V3 primary-shape check. It returns no date for malformed or unsupported values. V1/V2 parsing branches remain selected by their original mode strings.

Focused offline tests are in `ops/ci/test_html_archive_v3.py`. The suite checks the three authenticated example bodies when the VM-local target bundle is present, confirms that the old modes still reject those examples, and exercises malformed paths and exact contract bindings. The parser tests do not make network requests or change candidate registration.
