# XML guard repair handoff

The parser repair is complete and stable. It accepts declaration-shaped text inside valid XML content while rejecting real DTDs through `TreeBuilder.doctype`, with the unchanged error `XML entity declarations prohibited`. No source qualification or current intake credit is granted.

## Exact implementation

| File | SHA-256 |
|---|---|
| `web/scripts/pipeline/discovery.py` | `2611635de944f025e848d8a7b15dfff2a328ac67a11a122a774eb46b2e1e7f68` |
| `ops/ci/test_xml_doctype_guard.py` | `92835e6fa3b6e4bd4d510a84e4f62a12ae03a1816e4ce10330ed4cb4a1cdf887` |

Host and OrbStack copies match. The runtime diff is four inserted lines and two removed lines inside `xml_links`; decoding, size limits, source policy, extraction and continuation logic are unchanged. No H contract, authority, seed, registration, correction stamp, request plan or other runtime was edited by this operator.

The new 20-test portable suite includes the 16 diagnosed cases plus expansion rejection before text delivery, decoded-size limits, gzip DTD rejection and unchanged RSS/Atom/sitemap extraction. Real external, internal, parameter and bare DTDs in UTF-8 and UTF-16 fail with the original error. Standalone or undefined entities, malformed CDATA and unsupported HTML still fail. The actual archive is not a dependency of these tests, and none is skipped.

```sh
PYTHONPATH=ops/ci:web/scripts/pipeline:web/tests PYTHONDONTWRITEBYTECODE=1 \
  PYTHONPYCACHEPREFIX=/tmp/smp-xml-doctype-focused-cache \
  python3 -m unittest test_xml_doctype_guard test_discovery_repairs -q

PYTHONDONTWRITEBYTECODE=1 PYTHONPYCACHEPREFIX=/tmp/smp-xml-doctype-fullops-cache \
  python3 -m unittest discover -s ops/ci -p 'test_*.py' -q
```

The focused run passed 50 tests; the full operations run passed 800 tests. The independent reviewer separately reported the same 50 tests and 12 additional encoding/CDATA/security checks passing without findings. Web and visual checks belong to the parent integration report.

## Actual retained proof

Receipt: `/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/github-rss-xml-guard-actual-retained-replay-2026-10-24.json`.

Raw SHA-256: `ef9d6e3b0958d2fde13d5fcd3f78cbe0d178cdcd3847e71311cc99f1fe61e465`, 11,935 bytes.

The replay authenticated all 41,005 manifest entries in acknowledged archive `3dcd8798c2e5261ded4dd8afea348168ce2224af`, manifest `34c98107d3b35af79da17fbce9874e043bb18c326b9b34083904d8d91e0e934e`. It compared the old and repaired XML functions in memory against the same original evidence. The results were exactly equal for all five bounded HTML reports, all three qualification origins, all seven seed payloads and their preservation projection. Ping retained 242 URLs, Delinea 290 and Sonatype 205, with original completion dates. Seed preservation retained 26,969 full inventory pairs, 9,914 retained pairs, 24 bindings, 52 fact references and 32 original queue entries.

Full normal reconciliation, collector continuity and snapshot construction at `2026-10-25T00:23:00Z` also remained exactly equal. Intake stayed 264/557; the four ordinary fact references, 33 queue entries, original collection time and validity time were preserved. The reconstructed snapshot hash stayed `6feec3970cb598b8edf8cea93b4af3d51eb903dc5ba7bbfb2b767fc8d6eff846`. Pending processing and historical-review work stayed explicit: 10,632 and 10,631 documents respectively, from the same 10,655-document inventory.

The actual GitHub RSS replay separately retained all ten exact item URLs and original item dates, ranging from October 12 through October 22. It found no next-page link. The 1,271,295-byte body and original `2026-10-24T06:17:55.346340Z` HTTP 200 observation remained unchanged. The feed's embedded HTML doctypes are CDATA article content, not outer XML declarations. Its candidate source still needs separate endpoint and scope qualification.

The archive's 41,009 files and 1,906 directories had identical before/after seals. Content inventory: `eab114a22d66d2f8b5f5b0baa51e27092f391da999dcef331f7b0a106b86e405`; file modification times: `6cf088ea5f5d35a3af4c3e0d4043010102e5651e7bc35d0dc8600447cef48661`; directory modification times: `52d929d497e5266f25e7b5b7686cb87c482e85ddd022fbaceb2a6a08a43fabf6`. There were zero archive writes or network/subprocess/write guard attempts. Seed and origin validation used zero MemoryStore mutations; snapshot-derived objects used memory only.

The reproduction script is the ignored `.ctx/replay_xml_guard_actual.py`. Its stdout was captured in `/tmp/smp-xml-actual-retained-replay.json` inside the dev VM before the new receipt was written to the repository. No actual source or model call occurred.

## Review-time configuration and handoff boundary

The operational plan was verified as the disabled plan `ad1c5cc234fe4fa69cbceb5370ac74825a37dc80b08528ca908d14b1352e53b4` during replay and again at completion. This records the review-time configuration. It makes no claim that a later independently approved request plan remains disabled.

The parent owns commits, CI, any later plan activation, promotion and actual diagnostic dispatch. This handoff does not claim an actual new qualification or publication result.
