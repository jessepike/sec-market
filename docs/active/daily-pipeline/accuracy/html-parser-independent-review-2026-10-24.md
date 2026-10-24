# HTML pagination parser review, October 24, 2026

The pure source-bound HTML index parser and its ordinary-discovery integration were reviewed against the retained fixtures and current parser tests. The focused Ping and archive-discovery suites pass 34 tests, including UTC-day checks for offset timestamps, Delinea's moving numbered window and unresolved terminal, Sonatype's active/next/hidden-terminal controls, Ping's page-start and terminal controls, duplicate/date conflicts, unsafe URLs, and missing intermediate pages.

The parser keeps source-specific behavior bound to the existing source ID, exact index URL, host, family, kind, and completeness mode. It follows only validated literal next URLs. Delinea remains incomplete when its terminal layout is unknown. Ping and Sonatype can report terminal only when their observed controls prove it. Card dates remain scheduling hints; Delinea dates remain unknown. Normal discovery still requires verified registration, so these parsers do not admit candidate sources.

The archived-response replay is structural evidence only. It does not create candidate observations, prove fresh transport, qualify a source, or establish semantic facts. A separate bounded caller must retain each actual request, response, timestamp, source identity, and charge, then independently replay the page chain before reporting complete diagnostic inventory.

Validation ran in the OrbStack dev VM:

```text
python3 -m unittest ops.ci.test_html_archive_discovery ops.ci.test_ping_discovery -q
Ran 34 tests ... OK
```

Integration pins for the reviewed parser files, recorded by root before the atomic commit:

| File | SHA-256 |
|---|---|
| `web/scripts/pipeline/discovery.py` | `01c9d384e8399abd8dbc2b04e77936b0d6f43b1bc2831470d67e80a9727eea22` |
| `web/scripts/pipeline/contracts.py` | `89a427b6daa20f7a0d5ea5c1316290e2058b1ca16dcc517a3d7dd6e1e317d4ef` |
