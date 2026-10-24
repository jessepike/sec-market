# Actual bounded traversal V3 response review

The actual V3 diagnostic proves a complete Ping index walk under the reviewed parser. Delinea and Sonatype remain incomplete at additional literal article routes. I recommend retaining Ping's complete result and reviewing a separately versioned, narrow route repair for the other two sources. No source is qualified or activated by this review.

## Actual run and independent replay

Run `40077375424`, attempt 1, executed `workflow_dispatch` on `refs/heads/main`, application revision `60b08b91f6ae24d59367df538d3dcc1860aa7409`. It started at `2026-10-24T08:18:37.234703Z` and checked at `2026-10-24T08:19:12.209226Z`. The retained record is `state/ci/source-probe-runs/40077375424-1.json`, 266,592 bytes, SHA-256 `af8f63ecf77ffa2ea00fdbc062661ddda3340b776d0ec7afdcda00048373cbb0`.

The downloaded artifact at `/Users/jessepike/Documents/Codex/2026-10-22/security-market-pulse/renewal-20261024/bounded-traversal-v3-40077375424/source-probe-receipt/smp-collection-receipt.json` has SHA-256 `a0122c151a70c87e5e4cee534d9b35be3a2eecd49d0d44f75ad48fbc9743118f`. Its diagnostic equals the retained record's diagnostic. Independent replay through `replay_bounded_candidate_diagnostic` reproduced the entire original report exactly, using its original contract and immutable revision-3 plan: raw `c4f70c5fdef811f15794c0c2c40fd5a20bdd652a13760523154d1210876f91a9`, canonical `5f345173b2c52b613d3776533eb2ec2d947eee4167ae4f5c74965391f9562bb1`.

The replay checked every source/adapter wrapper, raw observation, body, URL, original timestamp, page sequence, primary sample, and charge against retained bytes. All 57 transport observations are HTTP 200 and have 57 distinct requested URLs. The run charged 54 index requests and three primary samples, taking fetches from 1,318 to 1,375. Calls remained 80 and documents remained 40; reservation denials were empty. There were zero model calls, facts, qualification, semantic admission, source checks credited, or publication. The 5,500-fetch cap leaves 4,125 fetches; the model and document allowances remain exhausted.

| Source | Accepted inventory | Index responses | Actual result | Earlier accepted inventories preserved |
|---|---:|---:|---|---|
| Ping | 242 dated URLs | 25 | Complete diagnostic index; terminal proved. Dates span `2018-01-02` through `2026-10-06`. | All 170 V1 and 200 V2 URLs are included. |
| Delinea | 240 URLs; no index dates | 21 | Incomplete: `Unsafe HTML archive article path` on page 21. | All 96 V1 and 204 V2 URLs are included. |
| Sonatype | 112 dated URLs | 8 | Incomplete: `Unsafe HTML archive article path` on page 8. Accepted dates span `2019-11-27` through `2026-10-14`. | All 32 V1 and 96 V2 URLs are included. |

All 500 accepted V2 `(sourceId, URL)` pairs are included in the 594 accepted V3 pairs. All 298 accepted V1 pairs are also preserved. The failed Delinea and Sonatype pages remain retained evidence. Their cards are excluded from the accepted inventory rather than silently skipped or called quiet.

## Terminal and remaining route evidence

| Original observation | Wrapper / raw observation SHA-256 | Body SHA-256 |
|---|---|---|
| Ping `https://press.pingidentity.com/news-releases?o=240`, fetched `2026-10-24T08:19:02.011350Z` | `3834dd46fbc5cbda7ae0c91a26b3cd13e44f652c4a5bae90b2d28d165899c992` / `b06066428c2fb1b369baa9a46857db5b81cb264811d1c21d8003bf21c8b0fe1a` | `6617928b29729343652724672d74ba6b458aff67ee5df600718598b252f89c8a` |
| Delinea `https://delinea.com/news/page/21`, fetched `2026-10-24T08:19:08.905115Z` | `dde16738a0c6612b9d80270d5f69af707d0ec643e389dabc7de8cebd6df51a1d` / `b60528fca6b58b6cfc57378fbff4298dfc7d5ace3fac7990aa3eab88c53b7361` | `2d71b1e6366129e1ca17c9436764e4091d5d1a91c44bdf073cf5ad72f664dc28` |
| Sonatype `https://www.sonatype.com/press-releases?page=8`, fetched `2026-10-24T08:19:12.070060Z` | `40448866af95df2270aac7a3d61205f775e8b073e728a3f4b3530e04aa372004` / `10193d6f923ca4fcfdef2848d3b13ca01991bde309b80fcac5715c0438720c94` | `eb3c8166d0bcf3924f2992af9c32a1d64cc817ba24e9778d4038f0c6b1b9eb6a` |

Ping's final page has two recognized dated release cards, active page 25, highest advertised page 25, previous `?o=230`, and a disabled span next control with no next URL. Its card dates are `2018-01-17` and `2018-01-02`. Independent parsing returns `terminalProved=true`; full replay separately verifies all 25 consecutive pages.

Delinea's page has 12 cards. Its rejected title-card link is literally `https://delinea.com/news/company/blog/2020/06/02/thycotic-extends-pam-cloud-leadership-with-acquisition-of-onion-id`, titled “Delinea (formerly Thycotic) Extends PAM Cloud Leadership with Acquisition of Onion ID.” This supports reviewing only that fixed historical route form with strict calendar and URL checks. It does not prove any terminal layout.

Sonatype's page has 16 cards. Its rejected card is literally `https://www.sonatype.com/press-releases/sonatypes-2019-nexus-user-conference-`, with a trailing hyphen and displayed date `June 10, 2019`. This supports reviewing an optional terminal hyphen within its existing source-bound slug grammar, while keeping reserved, numeric-only, encoded, empty, and control routes rejected. Neither failure justifies changing V1/V2/V3 interpretation or broadening article scope.

## Primary samples and adversarial checks

All three primary samples pass exact canonical and readable-shape checks. Their date metadata remains unknown. The replay retains the original URLs and times; it derives no publication date from a URL prefix.

| Source and exact sample URL | Fetched at | Primary body SHA-256 / bytes |
|---|---|---|
| Ping `https://press.pingidentity.com/2018-01-02-KPMG-and-Ping-Identity-Deliver-Consumer-Identity-and-Access-Management-Solutions` | `2026-10-24T08:19:02.311406Z` | `2fb1a842e5c54ca4f4c822f8714b88da4b737953e09cbfc120445eefa310efd5` / 66,875 |
| Delinea `https://delinea.com/news/2021-gartner-peer-insights-customers-choice-privileged-access-management` | `2026-10-24T08:19:09.182883Z` | `3ea0fa34f5ba6008b509cd90d787ae875469f8479bc0461057a0dba56f20b341` / 115,618 |
| Sonatype `https://www.sonatype.com/press-releases/18000-new-malicious-packages-discovered-in-q1` | `2026-10-24T08:19:12.186783Z` | `05483f81194e6aa4f2b42c889c3e4a7e5d945f10916ddd5e6f2cc8711e1ecd37` / 113,095 |

Three independent rehashed-record counterexamples fail: omitting Ping's middle index page produces `BOUNDED_CANDIDATE_PAGE_SEQUENCE_INVALID`; forging Delinea completion/terminal flags produces `BOUNDED_CANDIDATE_INVENTORY_OR_COMPLETION_DIFFERS`; adding Ping qualification/credit produces `BOUNDED_CANDIDATE_SOURCE_REPORT_JOIN_INVALID`. These mutations existed only in memory.

## Archive seals and review limits

Archive root: `/var/tmp/smp-bounded-v3-probe-20261024/archive-c112ffb8/jessepike-sec-market-c112ffb8b924d227e1ce3064b9c8de9edf4986b1`. All 35,592 manifest entries authenticate under SHA-256 `92acb13705494a1453d8240c3f87f617dde22a07ec3ffc428cbb4deb22ea2d87`. All 35,412 preceding manifest paths remain, with 180 additions. The only changed preceding paths are the daily budget and lease heads. No immutable object or normal collection, correction, snapshot, or production head changed.

The independent pass sealed all 35,596 files and 1,325 directories before and after replay. Content SHA-256 remained `24ecd18c469e11e634cc797fed2d4be46970ca54eaaeddfba30ccf1e588ffbb1`; file-mtime seal remained `2e1fbe0fa7214633f8e0b92a361606f87abfe8ce7efaba171c66b65ba6930932`; directory-mtime seal remained `55253b6e4f6a3fbea7816d75933153fc77b56b3322b75278fe26effc3daf87b2`. Network, subprocess, and disk mutations were blocked, with no attempted violation. This audit made no source/model requests or actual state/archive writes.

Replay code matched the reviewed V3 pins: onboarding `76cb6dc13d487d00ba4ecadeddb7a4c08007a3e9944032bd9ea9be60f2e91af1`; discovery `2bd9650c36adb7b723acac1c2b87187cdf1b3bc8e4ff1f9b6c7e540a766154d5`; contracts `6ed3cc8aa7a8e826d96a8fe4db3758f170b7ffa4f44c68bbaf40beaf5c37476f`; origin `c3c060710dfda74eeda0bb180251e1e9fe2f77ca6ec04c1ddc14d8b666f98be2`. The activation authority registry remains empty. All three registrations remain candidates, the 74 suppliers and 557 obligations are unchanged, and no private diagnostic result is presented as published coverage.
