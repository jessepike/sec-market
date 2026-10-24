# Bounded candidate HTML parser V5 implementation

Status: parser support implemented; no source plan or activation changed.

V5 adds two explicit parser modes: `DELINEA_HTML_MODE_V5` (`delinea-news-pagination-v5`) and `SONATYPE_HTML_MODE_V5` (`sonatype-press-pagination-v5`). Ping remains on V3. The V1–V4 branches retain their prior parsing behavior and result shape.

Delinea V5 recognizes the evidenced disabled-next control only when the exact classes, `Next` label, absent destination, and exact observed span/SVG/group/path subtree all agree with the retained page. The SVG attributes, group ID, and path-data character set are closed; scripts, inputs, event handlers, other tags, or extra attributes cannot be hidden below the disabled control. Head/visible navigation agreement, five-page active window, retained highest page, and nonempty 1–12-card inventory must also agree. An absent or ambiguous control stays unproved. Sonatype V5 permits one exact publisher-card URI in addition to the V4 route grammar. The recognized card emits `publisherLeadWarnings` with the literal URL, observed title, normalized displayed index date, and reason `PUBLISHER_CARD_LINK_REQUIRES_PRIMARY_REVIEW`. Other pages emit an empty list. This annotation is raw publisher-lead metadata; it does not establish article identity or semantic truth.

The optional actual-byte replay test reads the already available V4 bundle and archive, verifies body hashes, and checks that the page-25 Delinea terminal and page-10 Sonatype card parse only under V5 while the earlier V4 meaning remains unchanged. It is skipped when those local replay inputs are absent. Synthetic tests always run.

The V5 bindings are accepted by contract validation for the existing candidate source rows in an in-memory test only. This does not register or activate either source. A future plan revision must explicitly select V5 and independently replay the warning annotation from retained source bytes.

## Verification

OrbStack `unittest` suites passed:

- `test_html_v5_discovery.py`: 7 tests, including the local hash-pinned replay.
- `test_html_archive_discovery.py`: 19 tests.
- `test_ping_discovery.py`: 15 tests.
- `git diff --check` passed for the owned parser, contract, and test files.

SHA-256 pins at implementation review:

| File | SHA-256 |
|---|---|
| `web/scripts/pipeline/discovery.py` | `7e4af41f087786a656bb1bf5fe4aaa777eb6a3a8d08829aaccfbfc51df8b9885` |
| `web/scripts/pipeline/contracts.py` | `7a9dbf1c4a59391f79519b2aefe688ec572733e2223fd99fa352688b8d1c2d89` |
| `ops/ci/test_html_v5_discovery.py` | `34e0829d6bb36a5deafd6b66a44f0c0216b6739d3c77ffaa6a221a1719fd2e17` |

These parser checks establish only structural index interpretation. They do not establish a complete current traversal, primary-document identity, article facts, qualification, or source activation.
