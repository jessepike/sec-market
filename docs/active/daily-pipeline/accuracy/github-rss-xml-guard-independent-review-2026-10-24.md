# GitHub RSS XML guard: independent review

Verdict: clean within the reviewed scope. I recommend accepting the XML-only repair. No actionable correctness or security finding remains.

## Exact scope and pins

The runtime diff changes only the XML parser construction inside `xml_links`. A local `ET.TreeBuilder.doctype` callback rejects every actual document type declaration with the existing error. The parser handles grammar, rather than searching inert text for declaration-shaped bytes. It does not strip text, enable entity resolution, add a dependency or change discovery extraction, source registration, policy, authority, seed, budget or workflow.

- `/Users/jessepike/code/projects/sec-market-finish-20261022/web/scripts/pipeline/discovery.py`: SHA-256 `2611635de944f025e848d8a7b15dfff2a328ac67a11a122a774eb46b2e1e7f68`.
- `/Users/jessepike/code/projects/sec-market-finish-20261022/ops/ci/test_xml_doctype_guard.py`: SHA-256 `92835e6fa3b6e4bd4d510a84e4f62a12ae03a1816e4ce10330ed4cb4a1cdf887`.
- Reviewed retained replay receipt: `/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/github-rss-xml-guard-actual-retained-replay-2026-10-24.json`, SHA-256 `ef9d6e3b0958d2fde13d5fcd3f78cbe0d178cdcd3847e71311cc99f1fe61e465`.

Host source pins match the receipt. No runtime or operational-plan edits were made by this review.

## Independent execution

Fifty focused tests passed in OrbStack: the 20 new XML cases and 30 existing discovery-repair cases. Twelve additional adversarial cases also passed. Actual external/internal/parameter DTDs are rejected, including UTF-16 with BOM and explicit little/big-endian encodings, and gzip-decoded UTF-16. Declaration-shaped escaped text, comments, processing instructions and UTF-16 CDATA remain inert and accepted. Malformed declaration placement/case fails XML parsing. Existing decoded-byte limits remain ahead of parsing. The expansion regression confirms no entity-expanded document text reaches the tree builder. The independent audit guard recorded no network, subprocess or write attempts.

Direct read-only replay of the real 1,271,295-byte GitHub RSS body, SHA-256 `251d0a6b45ff8e4a1a40eba63b66781a7cfefbe6c1dd1151b2a1daae57107379`, yields exactly ten item URLs, no continuation and no derived modification dates. The original observation time remains `2026-10-24T06:17:55.346340Z`. The body hash, size and file modification time remain identical. An HTML DOCTYPE inside `content:encoded` CDATA is ordinary article text; it does not authorize a real outer DTD. No source qualification, current collection, semantic fact or completeness credit follows from parsing these historical bytes.

The focused command used a fresh Python cache prefix:

```sh
cd /mnt/mac/Users/jessepike/code/projects/sec-market-finish-20261022
PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/smp-xml-independent-guard \
PYTHONPATH=ops/ci:web/scripts/pipeline python3 -m unittest \
  test_xml_doctype_guard test_discovery_repairs -q
```

## H continuity and evidence limits

I reviewed the guarded replay script and final receipt rather than duplicating its heavy archive pass. It constructs the exact old declaration guard as its control, runs old and new parsers against separate memory stores, and requires complete equality of the results. The current code pins match that final receipt.

The comparison preserves all five original bounded HTML reports, all three fixed H origin inventories (Ping 242, Delinea 290, Sonatype 205), the seven immutable seed payloads and the seed preservation summary. Original inventory/proof completion times remain unchanged. H's fixed authority, original source/adapter digests, exact revision tuples, external diagnostic pins and whole-policy checks remain enforced. They do not pin the raw discovery module hash, so this behavior-preserving XML change needs no source-origin, seed or correction rebinding.

At the explicit offline as-of time `2026-10-25T00:23:00Z`, old and new normal reconciliation and snapshot outputs match: 264/557 intake, four exact ordinary fact references, 33 queue entries and snapshot SHA-256 `6feec3970cb598b8edf8cea93b4af3d51eb903dc5ba7bbfb2b767fc8d6eff846`. Original collection and validity dates remain unchanged. The receipt authenticates all 41,005 manifest entries of archive `3dcd8798c2e5261ded4dd8afea348168ce2224af`; full content and file/directory modification-time seals match across 41,009 files and 1,906 directories, with zero archive writes or audit-guard attempts.

That offline clock is a continuity test, not an actual timer, gate, publisher or production observation. A new code revision remains subject to the existing exact-code publication guards. The feed's ten items do not prove a full current window, Advanced Security segment identity, pagination exhaustion or safe source activation. This review performed zero source/model requests and granted zero coverage or qualification credit.
