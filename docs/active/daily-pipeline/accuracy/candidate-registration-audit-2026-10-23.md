# Candidate registration audit, October 23, 2026

All 28 candidate registrations remain unverified. Archived bytes identify 27 concrete replacement endpoints or adapter leads, but no configured homepage has a retained response and no candidate has a complete captured discovery traversal. The audit adds zero source checks. Production remains at 121/557, across the unchanged 74 suppliers.

I would repair the demonstrated parser failures and qualify the explicitly advertised single-supplier feeds first. Existing verified-source continuity stays ahead of source-family expansion. Every next fetch below is agent-owned after the natural allowance renews; no owner factual decision is needed.

## Scope and accounting

The supplied read-only archive is `/tmp/smp-coverage-baseline-20261023/state` inside OrbStack. The audit also reads the retained public evidence in `/Users/jessepike/code/projects/sec-market-finish-20261022/web/src/data/tracker/originals.json`. Raw primary bodies are checked against both their stored SHA-256 digest and byte count. Their original full-response observation times remain intact; later 304 receipts are recorded separately in JSON. This is offline evidence inspection, with no network requests, model calls, admission calls, source-date renewal, registration edits, source-family changes, gate attempts or publication.

October 23 remains charged at 5,500 fetches, 80 model calls and 40 documents, with both gate/publication attempts spent. The current 121 successes and all 436 gaps remain unchanged, including the 28 registration gaps.

The audit verified 39 distinct full-response body hashes. Twenty-seven candidates have some archived seed or listing body; Sysdig has only its retained evidence excerpt and URL. Seed articles establish identity or disclose a possible endpoint. They do not prove that an index works, covers the current window or stops safely.

## What the collector actually does

`/Users/jessepike/code/projects/sec-market-finish-20261022/web/scripts/pipeline/discovery.py:203` returns `SOURCE_BINDING_UNVERIFIED` before requesting any candidate URL. There is no implementation that walks a corporate homepage for `official_discovery`: after the registration guard, XML is accepted by content sniffing, while HTML requires `kind=html_index` and `htmlCompleteness=rel-next-exhaustion-v1`. Changing the registration flag would therefore reject an ordinary homepage rather than qualify it. The contract validator accepts this placeholder kind, but that is schema acceptance.

The XML parser collects item URLs and next links, but discards RSS/Atom publication fields. The selector uses `itemModified` for current-window scheduling; undated items go to the historical audit bucket. A future feed adapter must preserve validated metadata and prove the retained 30-day window, without treating sitemap modification time as a fact date. The October 23 audit anchor corresponds to a September 23 cutoff; no actual current index traversal is claimed.

Current prefixes are also mechanically wrong for two Cato `/il/news-releases/` seeds, the Check Point blog `/product-updates/` seed, and the date-prefixed Ping and Trend Micro releases. The JSON records every seed’s exact `withinCurrentScopePrefixes` result. Broadening a prefix without index and entity proof would only hide this defect.

## Concrete offline failures

### Orca

The retained `/resources/press-releases/` response redirects to `https://orca.security/resources/news/`. It contains `<link rel="next" href="https://orca.security/resources/news/page/2/">`, a `class="next page-numbers"` anchor to page 2, and a link to page 41. The current parser handles only `<a rel="next">`, so it ignores both genuine continuation controls.

A hypothetical, in-memory HTML-index replay using those bytes returned `complete=true` after one archived request and listed 35 URLs, including navigation, competitor comparisons, the feed link and pagination pages. Only two returned URLs were actual first-page official press releases. The audit did not activate this registration. The adapter must separate release cards from navigation and mixed third-party news, follow the evidenced next links, and fail when an expected page is absent. No page 2 body exists here.

### Barracuda

The retained `https://www.barracuda.com/company/news` body is raw gzip. Bounded decompression yields a newsroom shell with an empty `cardsContainer`, a fallback saying no articles were found, and `data-panel-endpoint="/content/barracuda-corp/us/en/company/news/jcr:content/root/container/container/news_room.news_room.json"`. The shell requires a captured data response before it can support a quiet day.

A hypothetical HTML-index replay of the raw body fails with `XML entity declarations prohibited`, because gzip is routed through XML parsing. A second replay of the decoded shell returns `complete=true` with 15 generic corporate/resource navigation URLs, without retrieving any newsroom records. Preserve raw hashes, use a bounded decoded view, and capture the disclosed JSON endpoint plus the first-party controller before specifying its request/filter/page schema. None of those replay results is a source check.

## Candidate-by-candidate findings

The replacement URLs below are literal disclosures in the bound primary bodies. They are fetch targets awaiting qualification. Full request/final URL mappings, observation paths, raw/decoded hashes, byte counts, original times, quoted markup, public evidence links and replay details are in the JSON companion.

### abnormal-security:official:1

Abnormal newsroom navigation is present in the 2024 funding release. No index body or pagination is archived.

Supplier boundary: Abnormal Security; archived funding release also uses current Abnormal AI host.

Proposed endpoint: `https://abnormal.ai/newsroom`.

Fetch the disclosed newsroom; identify press-release cards, actual publication dates and every pagination control. Keep corporate navigation and media links out of items.

- Archive proof: `dda855ec5afccc7a0ccaf17062e053e9b8e20a2774f2f13bfb0f1bed04c5ac95`; body `6b802c5d5907fc0b8f4f969b218ea420eab2c54ca56dc9dd080cdd888270afa5`; 307,169 raw bytes; fetched `2026-10-23T11:34:08.225870Z`. `https://abnormal.ai/newsroom/press-releases/series-d-5b-valuation`.

### aqua:official:2

The 2021 Aqua release links to its Aqua Security publisher page. The configured publisher homepage has no archive proof.

Supplier boundary: Aqua Security as issuer; a PR Newswire hostname alone supplies no entity binding.

Proposed endpoint: `https://www.prnewswire.com/news/aqua-security/`.

Fetch the exact Aqua publisher page and validate issuer label, result count, dates, language variants and pagination. Require Aqua entity support for each result.

- Archive proof: `e24720dfa44507d940f32466510b95493f8765e93123960c31b3ecbd93869212`; body `222e0e2f867e72220a4f2cf699cb03251fc3a54050170dda19801220b4954008`; 205,885 raw bytes; fetched `2026-10-20T21:12:01.289388Z`. `https://www.prnewswire.com/news-releases/aqua-security-announces-135-million-in-series-e-funding-at-a-1-billion-valuation-301243855.html`.

### barracuda:official:1

The retained news page is gzip-compressed HTML. Decoded markup has an empty cardsContainer and an explicit data-panel-endpoint. The visible no-results fallback supplies no quiet-day proof.

Supplier boundary: Barracuda newsroom; require press-release records, not in-the-news or generic corporate pages.

Proposed endpoint: `https://www.barracuda.com/content/barracuda-corp/us/en/company/news/jcr:content/root/container/container/news_room.news_room.json`.

Fetch the disclosed JSON endpoint and same-page first-party client script within the next natural allowance. Establish its request parameters, press-release filter, page/offset totals and empty-state schema before designing a bounded JSON adapter. Retain raw bytes and a bounded decoded representation.

- Archive proof: `ad9c16e190c51b55d7dac938c0fe1b4b6335c3c690d8e82041b75827da042b15`; body `340f5ce1d51d8b3ac8652ecd54eb52c84c4c7eddb8f40090ae52aa1012c6a130`; 22,363 raw bytes; fetched `2026-10-23T11:34:09.091727Z`. `https://www.barracuda.com/company/news`.

### beyondtrust:official:1

The 2021 transaction release discloses a BeyondTrust Corporation organization-search URL. Its result body and paging are absent.

Supplier boundary: BeyondTrust Corporation as issuer; shared publisher results about other companies remain outside this binding.

Proposed endpoint: `https://www.globenewswire.com/en/search/organization/BeyondTrust%2520Corporation`.

Fetch the exact encoded organization URL; validate organization identity, language, totals and paging. Retain encoding as disclosed until a captured redirect proves normalization.

- Archive proof: `e91c9514430ab19ce16c3a63e82e8589cb331d63da91aa62b7c154fa55946ffe`; body `026fe20117430e4ab0f7853ee65bbebbe854e4698f8d5cc2e65ea530fa01ae19`; 73,797 raw bytes; fetched `2026-10-20T21:41:23.316093Z`. `https://www.globenewswire.com/news-release/2021/08/17/2282045/0/en/BeyondTrust-Completes-Transaction-with-Clearlake-Capital-and-Francisco-Partners.html`.

### cato:official:1

All three Cato seed releases disclose its publisher page. Two seed article paths start /il/news-releases and fail the current /news prefix.

Supplier boundary: Cato Networks as issuer; unrelated PR Newswire articles do not qualify.

Proposed endpoint: `https://www.prnewswire.com/news/cato-networks/`.

Fetch the Cato publisher index; validate global and /il/ release variants, article issuer and date ordering. A future exact path policy must admit both evidenced language locations while excluding general publisher categories.

- Archive proof: `e8c1b77097e564528d69691dfb266ff243a890231d314bd3711a4af7c6d44952`; body `c389766a7bf74f990f0ac569f8c50f54f9f5c29ca21c11399564301ef16d4180`; 218,188 raw bytes; fetched `2026-10-20T21:11:45.910004Z`. `https://www.prnewswire.com/news-releases/cato-networks-raises-359-million-at-a-valuation-of-more-than-4-8-billion-302494283.html`.
- Archive proof: `fc301d29737b4cba1915f1093714f3ae3c7b517fbba828aba619032b542b5892`; body `470b5b0eb7906a00b66e586383497755b1d249452bde83b5c548155a69c61bce`; 70,629 raw bytes; fetched `2026-10-20T21:12:02.563879Z`. `https://www.prnewswire.com/il/news-releases/cato-networks-surpasses-350-million-arr-with-43-yoy-growth-in-2025-302694952.html`.
- Archive proof: `55d731214a87fc9eec9dea2436cb5ff8cc13dc63111f548b1996cc2633d5b6d6`; body `17b735244f28c1029a9b05250ed0fb5aa9c81696b0c4f4667b47617e2543784d`; 69,624 raw bytes; fetched `2026-10-20T21:41:18.084413Z`. `https://www.prnewswire.com/il/news-releases/cato-networks-exceeds-415m-in-arr-fueled-by-42-yoy-growth-and-enterprise-demand-302833667.html`.

### chainguard:official:1

The archived growth-financing release discloses the Chainguard publisher page. Related-story cards expose articles but supply no full index boundary.

Supplier boundary: Chainguard as issuer, independent of links through edge.prnewswire.com.

Proposed endpoint: `https://www.prnewswire.com/news/chainguard/`.

Fetch the exact Chainguard publisher page, validate issuer and pagination, and use result publication metadata for the 30-day queue. Do not treat the two related articles as a complete feed.

- Archive proof: `dac3117dee2ff9d43ccd71e5d727d1c120355883f400b8101062737b0630bbde`; body `7d8b539bddfc8d8fb62460541f1b04ce1f309277595a4482d535a9c942f4c282`; 219,070 raw bytes; fetched `2026-10-20T21:11:55.287485Z`. `https://www.prnewswire.com/news-releases/chainguard-announces-280-million-growth-financing-from-general-catalyst-to-usher-in-next-era-of-trusted-open-source-software-302592279.html`.

### checkpoint-email:official:1

The naming-change article explicitly advertises the Check Point blog RSS feed. Its own /product-updates path is outside the configured prefixes.

Supplier boundary: Check Point Email Security, including the evidenced former name Harmony Email & Collaboration; general Check Point threats are not segment announcements.

Proposed endpoint: `https://blog.checkpoint.com/feed/`.

Fetch the advertised feed and verify its retention floor, next links, item dates and entity filtering. Test the exact Email Security/Harmony Email and Collaboration naming relationship in the article body before admitting segment facts.

- Archive proof: `50ec3d4e779961d2ceb6a2d8f1f8143b417831aa62922ccf0a3aa344e5efbca8`; body `6d69cece87900607c32dd7c45af871362581f9c8542a94a0d6cb90cd1c32222a`; 112,616 raw bytes; fetched `2026-10-20T21:21:30.910132Z`. `https://blog.checkpoint.com/product-updates/introducing-check-point-email-security-a-new-name-aligned-with-our-ai-driven-strategy/`.

### checkpoint-email:official:2

The parent-company financial release links to the press-release index. That leaf proves a Check Point result, not a complete Email Security announcement stream.

Supplier boundary: Check Point Software as parent issuer, with a separate explicit Email Security entity link.

Proposed endpoint: `https://www.checkpoint.com/press-releases/`.

Fetch the disclosed index and qualify paging and per-entry publication dates. Require an explicit email-segment reference for any segment fact; parent revenue cannot silently become segment revenue.

- Archive proof: `823bdeb7978f9445b46cd456181b80329fcb2ced4dd40dac8cae6af492d6da35`; body `ad90c231db200ef3ca6909ed9ff62f08b037dd78be7fe85bc8c5011fae488593`; 110,102 raw bytes; fetched `2026-10-23T11:34:05.920028Z`. `https://www.checkpoint.com/press-releases/check-point-software-reports-2026-second-quarter-financial-results/`.

### checkpoint-sase:official:1

The same parent-company result body discloses the press-release index. No root or index response is archived.

Supplier boundary: Registered supplier is the public parent Check Point; do not reuse this binding as proof of an email-segment fact.

Proposed endpoint: `https://www.checkpoint.com/press-releases/`.

Fetch and qualify the shared Check Point index once under compatible policies; retain distinct source receipts and supplier bindings. Identify issuer/result dates and exhaust paging before completeness.

- Archive proof: `823bdeb7978f9445b46cd456181b80329fcb2ced4dd40dac8cae6af492d6da35`; body `ad90c231db200ef3ca6909ed9ff62f08b037dd78be7fe85bc8c5011fae488593`; 110,102 raw bytes; fetched `2026-10-23T11:34:05.920028Z`. `https://www.checkpoint.com/press-releases/check-point-software-reports-2026-second-quarter-financial-results/`.

### cyera:official:1

Five archived Cyera press releases disclose its newsroom and carry publication metadata. None is a captured newsroom index.

Supplier boundary: Cyera as issuer; acquisition targets Oasis Security and Ryft remain separate named entities.

Proposed endpoint: `https://www.cyera.com/newsroom`.

Fetch the disclosed newsroom and validate press-release tabs, date filters, pagination and a terminal state. Preserve all five known article URLs as audit seeds without claiming discovery completeness.

- Archive proof: `7676839a6e2c37a5670a6b74f6956e8283a4a350d6e1b5756e78550d15e2e1ef`; body `c7e1d3f5c6833dc9ed4633528dfd78a6c4b44996ffa183e6be5692d5d48ad117`; 267,390 raw bytes; fetched `2026-10-23T04:14:44.342902Z`. `https://www.cyera.com/press-releases/cyera-announces-400-million-investment-from-goldman-sachs-to-build-the-trust-layer-for-the-agentic-enterprise`.
- Archive proof: `3fb2300a948ed7fd028d2af9ccfe937fd91b33acd8ab9ca39a1906983fcdcc1c`; body `651da1d036563ce302610c41dd2f62ca9b58e769cf7c1157ea7304285a45a9f8`; 264,742 raw bytes; fetched `2026-10-23T04:14:51.233144Z`. `https://www.cyera.com/press-releases/cyera-completes-acquisition-of-oasis-security`.
- Archive proof: `15f535ccbaee9939b06ff3445d10ca7f4c05c4b5627f2d6ab673b1f3faa98a03`; body `8db492550825f8c21eb22c0fa64144dd1171bb78b95f878b22553d09566c3807`; 264,504 raw bytes; fetched `2026-10-23T04:15:00.595572Z`. `https://www.cyera.com/press-releases/cyera-acquires-ryft-to-extend-its-agentic-ai-security-platform`.
- Archive proof: `a589b1322c58232192bf3f73f7656ffe5e9bb272bf8b3d3bdcea3e751d3cf66e`; body `56f5aed04d9fec102e7d9e4688b86ec5f55fd7d6f68d1586555b908e84cf83ba`; 267,540 raw bytes; fetched `2026-10-23T04:14:46.413075Z`. `https://www.cyera.com/press-releases/cyera-raises-600-million-at-12-billion-valuation-to-continue-building-the-trust-layer-for-the-ai-era`.
- Archive proof: `cd5bfce7a2793cfa6e86df485937128eeb94c4629d3f32fdad1de286856a7f2f`; body `7f507d838faf136af0d10b68db116661226ae9cbd5dd6ecce969830daf1cf8f4`; 267,376 raw bytes; fetched `2026-10-23T04:14:43.150318Z`. `https://www.cyera.com/press-releases/cyera-raises-400m-to-meet-rapidly-growing-demand-for-ai-security-among-enterprises`.

### delinea:official:1

Both Delinea seed bodies explicitly advertise the news RSS URL; its bytes and retention/paging boundary are absent.

Supplier boundary: Delinea, with Thycotic/Centrify historical naming only where the source establishes it.

Proposed endpoint: `https://delinea.com/news/rss.xml`.

Fetch this exact feed, validate item URLs, pubDate/updated metadata, language and continuation. Prove the oldest retained date covers the current window or establish a companion bounded archive before a quiet result.

- Archive proof: `930a7e4fe4b3d44f1494824f179a38b4c34e40b4e5af0124c057dc2ba176d34f`; body `40d3a81783abdf0af16f21d191d1b0e5e2393e7bf42bcc3e4147d87c271b2fb4`; 126,986 raw bytes; fetched `2026-10-23T04:14:59.819592Z`. `https://delinea.com/news/delinea-strongdm-to-unite-redefine-identity-security-for-the-ai-era`.
- Archive proof: `207ee349245b34bda666f3d2c02f372290568d4c9fbcb46e5ea87beabaa98be3`; body `3e96a989035556903c39fac82fee9c89723f66fba143f0f96fe8ec693f17454e`; 116,118 raw bytes; fetched `2026-10-23T04:15:02.028006Z`. `https://delinea.com/news/thycotic-and-centrify-merge-to-become-a-leading-cloud-privileged-identity-security-vendor`.

### delinea:official:2

Both archived Delinea distribution releases disclose the exact Delinea organization search. It is a different discovery surface from its official RSS.

Supplier boundary: Delinea as issuer, including exact company identity on each distribution record.

Proposed endpoint: `https://www.globenewswire.com/en/search/organization/Delinea`.

Fetch the organization search, verify Delinea issuer, result dates and page totals, and preserve both existing source obligations. Do not qualify the publisher homepage.

- Archive proof: `a0a4401f1b56e922ad6d87139acd3bce1574b3554a2020569683adc685472a2a`; body `1ee7964205cbb0a6fd470e737643896fee9baa3dee0eeb49446b65c0bfc1d56a`; 72,075 raw bytes; fetched `2026-10-20T21:41:49.979213Z`. `https://www.globenewswire.com/news-release/2026/09/23/3367539/0/en/delinea-appoints-timothy-regan-as-chief-financial-officer.html`.
- Archive proof: `06845e12128160d4d58d99cdfba61335991c3ad39042bfdc2c7f3bcc63a57ab1`; body `a53d58b7dcdd45a4eb8120e2cc2b50277ba4266762c640c67e04c1f0bbcb3143`; 76,366 raw bytes; fetched `2026-10-20T21:41:27.583245Z`. `https://www.globenewswire.com/news-release/2026/03/05/3250113/0/en/delinea-completes-strongdm-acquisition-to-secure-ai-agents-with-continuous-identity-authorization.html`.

### forescout:official:1

The cited /company/leadership/ response redirects to /company/#leadership and discloses /company/news-press/. Leadership content supplies no announcement-list completeness.

Supplier boundary: Forescout as issuer; a leadership profile is not a dated appointment announcement.

Proposed endpoint: `https://www.forescout.com/company/news-press/`.

Fetch the disclosed news/press page, identify release cards and publication dates, and capture all paging or load-more behavior. Retain the leadership redirect as identity evidence only.

- Archive proof: `f776952ceeba4b4db5f75780b6a22279cf0f05f474b143ab2f2c292630384453`; body `3c18dd1d5f7825b0223724cc08c4e8beb4e31ed199e8453fa8989a6adb435287`; 552,326 raw bytes; fetched `2026-10-23T11:34:11.871916Z`. `https://www.forescout.com/company/leadership/` → `https://www.forescout.com/company/#leadership`.

### github-advanced-security:official:1

The GitHub CEO farewell article advertises the general blog feed plus a comments feed. Only the main blog feed is proposed.

Supplier boundary: GitHub Advanced Security is the registered segment; a GitHub-wide host or CEO article alone supplies no segment discovery boundary.

Proposed endpoint: `https://github.blog/feed/`.

Fetch the main feed and inspect retained date range and continuation. Bind each accepted fact explicitly to GitHub Advanced Security or the narrowly relevant parent event; do not count comments or unrelated product releases.

- Archive proof: `02fd456912024eae8fc8c48846c61aebd8df603064e6ad67570ceb0d529d0fae`; body `fc2072a68239d888ccd57a2aed52e140e9e271892fef6626ccb3529ba4085c64`; 168,580 raw bytes; fetched `2026-10-23T11:34:13.109967Z`. `https://github.blog/news-insights/company-news/goodbye-github/`.

### jfrog:official:1

The archived Q2 result links to View All News at the exact investor-news endpoint. No listing response or Q4 pagination API is retained.

Supplier boundary: JFrog Ltd. as issuer on its investor-relations host.

Proposed endpoint: `https://investors.jfrog.com/news/default.aspx`.

Fetch the exact listing, inspect server markup and any disclosed Q4 news API, and bind dates, page totals and terminal state. Do not assume the root investor page is an index.

- Archive proof: `0f9ed40d38d1aa5018d59bd08ed43e78f211775777de01ead66034b5adebae60`; body `d4b3f869f367be9e1195f49b15e6474a103ea45956cc5119dcdad6cbbfc7d2fc`; 415,271 raw bytes; fetched `2026-10-23T04:15:09.384404Z`. `https://investors.jfrog.com/news/news-details/2026/JFrog-Announces-Second-Quarter-2026-Results/default.aspx`.

### nozomi:official:1

Both acquisition seed bodies disclose the Nozomi Networks publisher page. Acquisition mentions alone cannot prove this page contains every acquirer-issued notice.

Supplier boundary: Nozomi Networks as issuer; Mitsubishi Electric as acquirer must remain explicitly attributed.

Proposed endpoint: `https://www.prnewswire.com/news/nozomi-networks/`.

Fetch the Nozomi publisher page and validate issuer, dates and paging. State the bounded issuer-based discovery scope, and leave any missing acquirer coverage visible under existing obligations.

- Archive proof: `11a5703b8e4ba55f4dcf414b38c23b0da6bea31556a81d0d3aaf094b59bc6ecd`; body `bd85066ce2738d5abb5e10a95788dfaa364db870af4766fac0a172dc3c74ad2d`; 216,268 raw bytes; fetched `2026-10-20T21:11:37.130662Z`. `https://www.prnewswire.com/news-releases/mitsubishi-electric-to-acquire-nozomi-networks-to-improve-industrial-cyber-defenses-and-power-operational-transformation-302550314.html`.
- Archive proof: `56b5343a6d1b50ca627202339d879f79faf3f360c80afe3c97fa698bbe1818bc`; body `1498446e40257eaeb95ca04d8839da8d2f09d0b7cc3f2a52e8700d9dec3d5355`; 215,123 raw bytes; fetched `2026-10-22T01:11:51.082894Z`. `https://www.prnewswire.com/news-releases/nozomi-networks-enters-next-phase-of-growth-as-mitsubishi-electric-completes-acquisition-302673652.html`.

### orca:official:1

An archived /resources/press-releases/ response redirects to the news listing. It advertises page 2 in head link rel=next and a next page-numbers anchor; page 41 is linked. The parser ignores both forms.

Supplier boundary: Orca Security official press-release cards only; the mixed news index also links to third-party reporting.

Proposed endpoint: `https://orca.security/resources/news/`.

Repair index parsing to honor evidenced head rel-next and approved next-page control, separate press-release item cards from navigation and independent-reporting cards, and reject unknown terminal states. Fetch pages 2 through terminal or a proven current-window floor on the next allowed run.

- Archive proof: `c324da09ef9dd91d85225f7e461548e3bc9239345c60a6dd493c2123d0f65835`; body `b64eab1ba8d74d6add4fd0fc69460a1cb6cc5399577c36d04e9c49f5a273035f`; 231,913 raw bytes; fetched `2026-10-23T04:14:52.879570Z`. `https://orca.security/resources/press-releases/orca-security-series-c-550-million-announcement/`.
- Archive proof: `b5d6182ff2fed713a7cc26fea913c63719a2f97c369ff420be7212b8a360be9a`; body `9f0503f9a7c15f5a6e4686ebd9d3a4cf6be13626d43746154af19a7d1f627e54`; 236,182 raw bytes; fetched `2026-10-23T04:14:41.172921Z`. `https://orca.security/resources/press-releases/` → `https://orca.security/resources/news/`.

### ping-identity:official:1

Both retained Ping releases advertise the exact RSS alternate link. Date-prefixed article URLs are outside all current scope prefixes.

Supplier boundary: Ping Identity on its dedicated press host; its past Thoma Bravo acquisition is historical seed evidence.

Proposed endpoint: `https://press.pingidentity.com/news-releases?pagetemplate=rss`.

Fetch the advertised RSS, verify retention, pagination and item dates, and use a validated date-and-title item path rule for this dedicated press host. Never silently broaden every host path to an article.

- Archive proof: `a26a1b029776a459b8601c93453b00e444210f2b42fa79e6c05246f0339cf8e7`; body `1bf9f1dc5c0a932bc29f39f9e04fec1956067f10596e39b18c0a9150e7ff1fab`; 66,779 raw bytes; fetched `2026-10-23T11:34:00.088224Z`. `https://press.pingidentity.com/2024-11-14-Ping-Identity-Surpasses-30-Annual-Growth-in-SaaS-Revenue-and-Approaches-800M-ARR-as-an-Enterprise-Identity-Market-Leader`.
- Archive proof: `82bacf00481ffadfe75ef5f117336d359be588c5b0304ff981f490e9f3095c70`; body `1f3e93a52a73df5edccdd0dbfb19a55f222c8d19a5f312e268d4d4fadec04cdf`; 69,909 raw bytes; fetched `2026-10-23T04:14:48.889657Z`. `https://press.pingidentity.com/2022-10-18-Thoma-Bravo-Completes-Acquisition-of-Ping-Identity`.

### ping-identity:official:2

The retained Keyless acquisition article discloses the Ping Identity publisher page. Its page body is absent.

Supplier boundary: Ping Identity as issuer; Keyless is an acquisition target, not a replacement supplier binding.

Proposed endpoint: `https://www.prnewswire.com/news/ping-identity/`.

Fetch the exact supplier page and validate issuer, dates, language and full pagination. Preserve this source separately from the Ping press feed.

- Archive proof: `46726cce109bfa0924641862c3a504c7dea4b2bba5e14a18010ab1f46401b11f`; body `b73bf013fabb83cfa9cb015c078c2c8bc7898d33b1575061dfaa1506dd80516d`; 214,480 raw bytes; fetched `2026-10-20T21:21:36.925585Z`. `https://www.prnewswire.com/news-releases/ping-identity-marks-digital-trust-milestone-with-zero-knowledge-biometrics-in-the-age-of-ai-302654492.html`.

### rapid7:official:1

The archived CEO announcement exposes View All News at the exact investor endpoint. No listing response exists.

Supplier boundary: Rapid7 as issuer on its investor-relations host.

Proposed endpoint: `https://investors.rapid7.com/news/default.aspx`.

Fetch the exact listing and qualify server/API pagination and explicit release dates. Exclude navigation, PDF duplicate links and tracking URLs from discovery items.

- Archive proof: `9f0ecf23e984c7bbb1e3a7a22cf192f6adeefae468e89abe90f3f8cf5707fc5d`; body `911cb36056eee61f355544d6323172db4650f6d0febbb20264c0fdfa79cac731`; 86,808 raw bytes; fetched `2026-10-23T04:15:06.208761Z`. `https://investors.rapid7.com/news/news-details/2026/Rapid7-Appoints-Wael-Mohamed-Chief-Executive-Officer-Corey-Thomas-to-Become-Executive-Chairman/default.aspx`.

### rubrik:official:1

The archived CRO release exposes its dedicated press-release listing. No index body or continuation is captured.

Supplier boundary: Rubrik as issuer; executive names alone do not identify a discovery stream.

Proposed endpoint: `https://ir.rubrik.com/news-events/press-releases/default.aspx`.

Fetch the exact press-release listing and validate card identity, release date, page totals and terminal state. Separate event-calendar links and duplicate PDF assets.

- Archive proof: `0436baf377955181e6f43f9825470f7dd39652842a333155407122bf187d84ad`; body `710d5be834f1c10951fabe47f1b71459efd1a426247346b4e71c8fe2e6cfbbb6`; 57,941 raw bytes; fetched `2026-10-23T04:14:57.340319Z`. `https://ir.rubrik.com/news-events/press-releases/news-details/2026/Rubrik-Promotes-Jesse-Green-to-Chief-Revenue-Officer/default.aspx`.

### sonatype:official:1

Both archived Sonatype releases explicitly advertise the press-release RSS endpoint. Its bytes, retained range and pagination remain unproved.

Supplier boundary: Sonatype as issuer; Vista is separately named as investor.

Proposed endpoint: `https://www.sonatype.com/press-releases/rss.xml`.

Fetch the exact feed; validate release paths, publication metadata and current-window coverage. Retain the 2019 investment article only as historical audit evidence.

- Archive proof: `ae28f598db53f607758766cf78b7f1360d6189c8076faeca1134f11d3776e7fe`; body `0797efe21e3568cbb309a739affe457a236ecc6de41c9752f5172f29bb32b7ea`; 112,635 raw bytes; fetched `2026-10-23T04:14:51.574093Z`. `https://www.sonatype.com/press-releases/vista-acquires-majority-interest-in-sonatype`.
- Archive proof: `7b455837fd85636b72d0408e86a26b87ef65f56f16a7ff46e02b428eea8d40a0`; body `87279d59840615160dace5c18b218b59ed16cb46b3c67fdda046868e0752dc0d`; 113,541 raw bytes; fetched `2026-10-23T04:14:55.174958Z`. `https://www.sonatype.com/press-releases/sonatype-strengthens-leadership-team-for-ai-driven-growth`.

### sysdig:official:1

No observation or body for the Sysdig host or exact seed URL exists in the supplied archive. The retained public evidence record is an excerpt and URL only.

Supplier boundary: Sysdig is the intended issuer; the current retained excerpt is insufficient primary-byte proof.

Proposed endpoint: None yet. The exact cited leaf must be captured first.

On the next natural allowance, fetch the already-cited CEO release first. Verify its final URL and issuer, then use only feed/index links disclosed by that response; a guessed /press-releases index remains unsupported.

### torq:official:1

Both archived Torq release pages disclose /news/. They do not show a news-index response or paging controls.

Supplier boundary: Torq as issuer; Jit is the acquisition target.

Proposed endpoint: `https://torq.io/news/`.

Fetch /news/ and identify release cards, publication dates and next/load-more behavior. Keep acquisition and financing leaf pages as audit seeds.

- Archive proof: `4880f86d0e86109acb01bf9cb056d689785309f8d101b2570b403e5ad506ba9f`; body `da004e0a404beb97ed38231d0bac53f2cb9d09feb7192c91f7edd0d5a55091ac`; 95,725 raw bytes; fetched `2026-10-23T11:34:05.860071Z`. `https://torq.io/news/torq-seriesd/`.
- Archive proof: `2958493750b22380863114ec2adbc4ba38f73d8e3498892c2a31875b4258eeb7`; body `27c3b2719d80607c98d0cc4d5aba1ef5e23a315cb5726e2e1eb35a983559fa42`; 91,835 raw bytes; fetched `2026-10-23T04:15:09.216495Z`. `https://torq.io/news/torq-acquires-jit/`.

### trend-micro:official:1

The archived results page exposes an anchor explicitly labelled rss at this exact endpoint. The feed body is absent, and date-prefixed release paths fail current prefixes.

Supplier boundary: Trend Micro on its dedicated newsroom host; retain reported financial period separately from publication date.

Proposed endpoint: `https://newsroom.trendmicro.com/rss?rsspage=20295`.

Fetch the disclosed RSS and verify its channel title, language, retained dates and continuation. Register a validated date-and-title path rule before article selection; an RSS link alone supplies no complete window.

- Archive proof: `a469145710c0baffff571d6f56b0ba7a3dc806114cceeb2ec4921ffc9dafdb11`; body `f22dbfeaf755a51c99e8a3a973add94ed94dd6f0405cffc9fa3226b571ac5f53`; 405,366 raw bytes; fetched `2026-10-23T04:14:54.588681Z`. `https://newsroom.trendmicro.com/2026-08-13-Trend-Micro-Reports-Earnings-Results-for-Q2-2026`.

### trustwave:official:1

The LevelBlue acquisition release explicitly advertises its press-release RSS. The feed covers a broader company than the registered Trustwave supplier.

Supplier boundary: Trustwave as acquisition target; LevelBlue as acquirer and publisher. Entity filtering must not rewrite this source into LevelBlue-wide supplier coverage.

Proposed endpoint: `https://www.levelblue.com/newsroom/press-releases/rss.xml`.

Fetch the exact feed and validate retention/pagination, then require an exact Trustwave reference and acquisition context for relevant items. Generic LevelBlue releases cannot earn a quiet Trustwave completeness result without a proven supplier-specific search boundary.

- Archive proof: `18e4527a442c56787cba05e2b9addcc9f25696f487135903bb33dbaf302d1e28`; body `56b10c4d252dd01f6bc5c6bc763d4d9f88d171e9f01a0b8d0851e90eb5d612b3`; 70,732 raw bytes; fetched `2026-10-23T04:14:52.443297Z`. `https://www.levelblue.com/newsroom/press-releases/levelblue-completes-acquisition-of-trustwave-to-form-the-worlds-largest-managed-security-services-provider`.

### veracode:official:1

The archived 2022 TA investment release links to /newsroom/. No listing body or pagination proof is retained.

Supplier boundary: Veracode as issuer; TA Associates is the named investor.

Proposed endpoint: `https://www.veracode.com/newsroom/`.

Fetch the disclosed newsroom, isolate press releases and capture publication metadata plus pagination/terminal state. Treat the old investment leaf as historical identity evidence only.

- Archive proof: `3c10d6a7037d92c6c3cba50c9119506e42fb156cc2ad096f612eabc99028647f`; body `7866723f913f5850dd23acadbc13050c497f74f76b98ab308ea500467e18da78`; 461,501 raw bytes; fetched `2026-10-23T04:15:08.094969Z`. `https://www.veracode.com/press-release/veracode-receives-major-growth-investment-from-ta-associates/`.

### zenity:official:1

The cited legacy company-overview path redirects to /press-release/... and discloses the new press-release listing. No listing body is retained.

Supplier boundary: Zenity as issuer; a route migration does not renew the source publication or retrieval date.

Proposed endpoint: `https://zenity.io/company/newsroom/press-releases`.

Fetch the disclosed listing, validate dates and pagination, and preserve the observed legacy-to-canonical URL mapping. Use /press-release/ article scope only after proving listing membership.

- Archive proof: `d9a84775382ee3561744c8d8d8009cdf810f087e877a4d7512252efed94f048a`; body `7ebb99ca7e35037dd1b5c0841df2f4082e63edc9eda6d33e3adc870bd6f9cbcd`; 916,389 raw bytes; fetched `2026-10-23T04:14:53.638385Z`. `https://zenity.io/company-overview/newsroom/company-news/zenity-raises-125-million-to-secure-the-era-of-1-billion-ai-agents` → `https://zenity.io/press-release/zenity-raises-125-million-to-secure-the-era-of-1-billion-ai-agents`.

## Qualification required for every endpoint

A positive result requires a captured, correctly bound index and a retained primary article with an explicit source publication date. Independent semantic admission still decides whether a statement can enter the site. A quiet result requires a complete supplier-specific traversal whose retained dates cover the registered window. Missing dates, an unknown page limit, an empty JavaScript shell or a truncated feed stays incomplete. A denied fetch, malformed body, wrong issuer, missing continuation or unproved entity filter produces a blocked or unresolved receipt.

The existing maximum is 60 discovery pages per candidate, with 30 days for current selection and two semantic documents per source, including at most one audit document. This audit changes none of those limits. If a feed has silently dropped current-window entries, or a listing cannot reach a known terminal state within its registered bound, it cannot establish quiet. Parent-company and shared-publisher indexes require explicit entity checks rather than a host-name shortcut.

## Proposed work, without activation

1. Repair Orca’s evidenced pagination forms and release-card extraction, with missing-page and mixed-navigation replay cases.
2. Preserve raw encoded evidence while parsing a bounded decoded view; retain Barracuda’s shell as incomplete until its data endpoint and controller establish real records and terminal behavior.
3. Fetch the exact disclosed endpoints after the natural allowance renews. Begin with Delinea, Ping Identity and Sonatype’s dedicated advertised feeds, then qualify the wider feeds and indexes with entity filters. Sysdig needs its exact cited leaf first.
4. Once captured, retain feed publication metadata and prove retention/pagination boundaries. Only then propose exact endpoint/kind/scope/completeness changes under the existing source IDs and families. Contract activation and the normal independent gate remain separate work.

No human decision is blocking these actions. The existing source obligations remain visible, and no unsupported endpoint is promoted into a working discovery source.

Machine-readable companion: `/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/candidate-registration-audit-2026-10-23.json`.

## Small adapter specifications for the next code repair

These are agent-owned repairs. They do not require an owner factual ruling and do not activate a source. The JSON companion holds the exact source and body binding for each specification.

For Orca, keep index URLs separate from article URLs. Accept continuation only on the exact `orca.security` host under `/resources/news/` or `/resources/news/page/<positive integer>/`. The archived head `rel=next` and the `next page-numbers` anchor must agree; request their shared page 2 once. Extract only official press-release cards under `/resources/press-releases/<slug>/`, excluding external news cards, pagination and navigation. A missing page, conflicting controls, a loop, unsafe destination, unknown continuation or the existing 60-page cap keeps the source incomplete. Page 41 is linked, but its terminal state is not archived.

The minimum archived replay should return two first-page release items, queue page 2 and remain incomplete because page 2 has no retained body. It must never reproduce the current 35-item navigation result. Full traversal comes first; a later current-window stop requires evidence that the complete release-card stream is ordered and dated. An old featured card alone cannot establish that boundary.

For Barracuda, preserve the raw object and its original observation time. A bounded decoder must enforce the existing 32,000,000-byte maximum and classify the decoded content before deciding between HTML and XML. The actual raw body is 22,363 bytes and decodes to 146,001 bytes. Capture the disclosed same-host JSON endpoint and relevant first-party controller on the next allowed run. The HTML exposes the filter value `barracuda:news-articles/press-release`; exact query names, record/date fields, totals and cursor/terminal schema remain unknown until their responses are captured.

The minimum replay must preserve both raw and decoded hashes and keep the empty static cards container incomplete. A validated JSON adapter may report quiet only when a captured, supplier-bound press-release result and all continuation states prove the registered window has no eligible entries. Missing data, ambiguous filters or a browser fallback message cannot supply that proof.
