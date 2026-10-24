# Bounded candidate HTML parser V4 route proposal

Status: implemented parser specification. The V4 parser modes are available for an explicit reviewed plan transition. This work does not change the market contract, source binding, qualification plan, or registration.

## Evidence

The authenticated V3 run `40077375424` retained 57 fetches, moving the daily fetch ledger from 1,318 to 1,375. It recorded zero model calls and zero source credit. Ping reached its advertised terminal page after 25 pages and retained 242 URLs; its primary sample passed. Delinea and Sonatype each retained their successful primary sample but stopped on one article URL.

The supplied target bundle pins each page through its report wrapper, source adapter, raw observation, body object, requested URL, final HTTP 200 response, and fetch time. The full authenticated archive is commit `c112ffb8b924d227e1ce3064b9c8de9edf4986b1`: 35,592 files, all 35,412 prior paths retained, 180 additions, and zero immutable changes. V3 replay matched exactly; protected heads and before/after seals were unchanged. The local body SHA-256 values match the target bundle pins:

| Source and requested page | Body SHA-256 | Rejected title-card URL |
|---|---|---|
| Delinea `https://delinea.com/news/page/21`, fetched `2026-10-24T08:19:08.905115Z` | `2d71b1e6366129e1ca17c9436764e4091d5d1a91c44bdf073cf5ad72f664dc28` | `https://delinea.com/news/company/blog/2020/06/02/thycotic-extends-pam-cloud-leadership-with-acquisition-of-onion-id` |
| Sonatype `https://www.sonatype.com/press-releases?page=8`, fetched `2026-10-24T08:19:12.070060Z` | `eb3c8166d0bcf3924f2992af9c32a1d64cc817ba24e9778d4038f0c6b1b9eb6a` | `https://www.sonatype.com/press-releases/sonatypes-2019-nexus-user-conference-` |

The Delinea URL is in the recognized title-card region and uses an exact historical path shape: `/news/company/blog/YYYY/MM/DD/<slug>`. The Sonatype URL is in the recognized press-release card region and is the existing direct slug form with one trailing hyphen. These observations establish literal route shapes only. They do not prove article-body readability, current factual content, or source qualification. V3 traversal was complete for Ping and incomplete for Delinea and Sonatype.

## Bounded grammar

Keep V1, V2, and V3 interpretation immutable. Do not revise the live plan implicitly. Select these additions only under an explicit new parser revision and new source-mode hashes in a reviewed plan transition. The Ping V3 behavior remains unchanged; Ping already reached its terminal page in this run.

For Delinea, add only `/news/company/blog/YYYY/MM/DD/<slug>`. Require exactly the fixed `news/company/blog` prefix, four digits for the year, two digits each for month and day, a real calendar date, and one nonempty lower-case ASCII slug made from letters and digits separated by single hyphens. Keep exact HTTPS host, no credentials or non-default port, no query or fragment, and all raw literal path checks. The route date is not a source publication date and must not populate or refresh one. Continue requiring title and image links to resolve to the exact same URL. Keep Delinea terminal pagination unproved unless a retained final-page body independently proves it.

For Sonatype, retain the V3 direct and two-segment routes and add one optional trailing hyphen to the final slug segment. No other character or depth changes. Apply the existing reserved-segment and numeric-only guards after removing that single allowed terminal hyphen; reject an empty slug, a second trailing hyphen, reserved controls, and every route deeper than two slug segments. Keep the exact HTTPS host, no credentials or non-default port, no query or fragment, raw empty-segment and dot-segment checks, and card-region scoping.

This accepts the two observed routes while limiting each change to one route family. It grants no article-body, semantic, intake, or registration status. The normal retained article processor must still evaluate each discovered URL under its own current rules and hold articles it cannot process.

## Strongest case against broadening

One retained page per source cannot show that every URL in either namespace follows the proposed shape or that the route semantics are stable. The Delinea path is a historical company-blog archive and its encoded date could be mistaken for source evidence. The Sonatype trailing hyphen may be a malformed publisher link. If either pattern does not recur in the authenticated page inventory, preserving those entries as incomplete may be safer than accepting the broader route family.

Implementation is in `web/scripts/pipeline/discovery.py` and `web/scripts/pipeline/contracts.py`; focused regressions are in `ops/ci/test_html_archive_v4.py`. The tests replay the two hash-pinned V3 page bodies under V4, confirm V3 rejects those same links, check invalid dates and slugs, and validate exact V4 contract bindings. The Delinea parser still does not prove terminal pagination. Article-body handling and any source transition remain separate review gates.
