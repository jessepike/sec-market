# XML declaration guard repair

The accepted repair rejects actual XML document type declarations through the stdlib parser's `TreeBuilder.doctype` callback. It preserves the existing error, `XML entity declarations prohibited`, without scanning inert article text for declaration-shaped bytes.

The retained GitHub RSS body `251d0a6b45ff8e4a1a40eba63b66781a7cfefbe6c1dd1151b2a1daae57107379` has 1,271,295 bytes and ten HTML doctypes inside `content:encoded` CDATA. Its outer document is RSS 2.0, with ten item dates from October 12 through October 22, 2026, and no next-page link. The latest retained observation is `objects/23df935fbf8eaf2d7e31eb773622e1fd3601bc54e6bd5930969d8112ded39c3b`, 487 bytes, fetched at `2026-10-24T06:17:55.346340Z` with requested and final URL `https://github.blog/feed/` and HTTP 200. It belongs to original candidate source `github-advanced-security:official:1` in run `40069462824`, app revision `377043028e01301b3433790caddc7a7dd5aaebc5`, under original policy `79cdd19b962ee3adbb5d9e1a43cbc389b3c9196a6c0a2105ea455c8bd70f9f60`. This is historical transport evidence only.

## Implementation boundary

Change only `xml_links` parsing. Keep decoding and the 32 MB decoded-byte limit, XML format recognition, link extraction, continuation handling and all source gates unchanged. A local `ET.TreeBuilder` subclass rejects its `doctype` callback before document content or entity expansion is processed. `ET.XMLParser` continues to reject malformed XML, undeclared entities and standalone entity declarations. CDATA, comments and processing instructions remain ordinary XML content. No text is stripped or rewritten, no HTML parser is substituted and no dependency or network permission is added.

Portable tests must cover inert CDATA/comment/processing-instruction text; real external, internal, parameter and bare DTDs in UTF-8 and UTF-16; standalone and undefined entities; malformed CDATA; unsupported HTML; expansion rejection before text delivery; the existing decoded-size bound; and unchanged ordinary discovery formats. Actual retained RSS replay is separate from those tests and grants no source qualification or current intake credit.

## Required retained-proof checks

Before handoff, replay the authenticated RSS body with its ten exact links and original dates, with no continuation. Preserve body, observation and archive hashes and modification times. Replay H's three HTML qualification origins and all seeded inventories exactly, including their original historical reports, without changing H, source declarations, authority rows, seed objects or correction stamps. Reconcile and reconstruct the retained normal collection at `2026-10-25T00:23:00Z`, preserving facts, queue, collection dates and the expected current partitions. Use MemoryStore overlays only for derived objects, never LocalStore against actual archives. Run focused and full operations tests in OrbStack with a fresh Python cache path.

This unit is a parser repair. The GitHub source remains a candidate, and its endpoint/scope qualification is separate. No source, model, publication, Git or workflow action is included.

## Implementation result

The four-line parser change and 20 portable tests are implemented. The 50-test XML/discovery run and full 800-test operations suite passed in OrbStack. The actual retained replay receipt is `docs/active/daily-pipeline/accuracy/github-rss-xml-guard-actual-retained-replay-2026-10-24.json`, raw SHA-256 `ef9d6e3b0958d2fde13d5fcd3f78cbe0d178cdcd3847e71311cc99f1fe61e465`. It records exact old/new equality for all five original bounded reports, all three origins and seven seed payloads, and the full normal next-00:23 reconstruction. It also records the actual RSS's ten links and dates. All actual archive content and modification-time seals stayed unchanged. The disabled `ad1c5cc2...` plan was the review-time configuration; a later approved request plan is a separate change.
