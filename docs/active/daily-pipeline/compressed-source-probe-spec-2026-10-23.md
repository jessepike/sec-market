# Bounded compressed input for candidate source probes

Prepared October 23, 2026. The candidate-source probe reads publisher HTML and robots text
before examining advertised feed and sitemap endpoints. Its parsing view must use the same
bounded gzip decoder as discovery and document reading. This repair grants no qualification,
source coverage, semantic admission, active registration or publication authority.

## Implementation boundary

In `web/scripts/pipeline/onboarding.py`, pass fetched root HTML and fetched robots bytes through
`discovery.decoded_discovery_body` before parsing text. Compressed text must be valid UTF-8;
uncompressed text keeps its existing replacement decoding behavior. Parse robots text once
for both its access rules and advertised sitemap URLs. Do not implement a separate decoder.
`discovery.xml_links` already calls the same bounded decoder for XML responses and retains
its XML entity prohibition; leave that implementation unchanged.

Malformed, truncated, oversized or invalid UTF-8 compressed root input stops before the robots
request. The same failures in fetched robots input stop before advertised or fallback endpoint
requests. Invalid XML endpoint input remains a failed endpoint response under the existing
probe outcome rules. No parse failure may produce a successful endpoint finding from that body.

All original observation objects, content-addressed body bytes and source times remain intact.
The existing bound reservation context must still reserve each logical request before transport.
Failed parsing keeps every fetch charge, preserves existing calls/documents/additional counters,
and cannot reset, refund or bypass the current-day cap, runtime, day-change or worker limits.

Keep existing endpoint selection, robots exclusions, allowed-host checks, the eight-candidate
bound and the fallback sitemap rule. Do not follow XML items or child indexes, arbitrary HTML
links, disallowed endpoints or newly observed hosts. Endpoint responses remain candidate-only
diagnostics requiring separate entity, scope and history review. Existing zero-credit fields and
coverage/latest-run/source-registration behavior remain unchanged.

## Verification

Use fictional transport and temporary state in OrbStack. Cover compressed HTML feed advertising,
compressed robots sitemap advertising and exclusions, compressed XML endpoint parsing, ordinary
input equivalence, malformed/truncated/oversized/invalid-UTF-8 root and robots failures, retained
raw observations and charges, charged-cap and last-unit budget behavior, and absence of model,
qualification or source coverage credit. Run the focused tests and relevant existing operational
tests. No real onboarding, source/model request, ledger/archive write, active-source edit or
publication is authorized by this implementation.

## Candidate verification results

The probe now applies the existing bounded decoder to fetched root and robots bodies. Both
compressed parsing views require strict UTF-8, while ordinary inputs keep replacement decoding.
Robots parsing and sitemap extraction share one decoded text value. The XML parser was confirmed
to already bounded-decode its input and prohibit entity declarations; it required no edit.

All 15 dedicated tests passed in OrbStack. The combined run with the existing persistent probe
budget, discovery-repair and compressed-article suites passed 83 tests with zero skips:

```text
python3 -m unittest ops.ci.test_compressed_probe_input ops.ci.test_onboarding_budget ops.ci.test_discovery_repairs ops.ci.test_compressed_article_input -q
```

Fictional compressed roots advertised feeds, compressed robots files advertised sitemaps and
denied disallowed endpoints, and compressed XML retained its existing feed/index parsing. Host
restrictions, the eight-endpoint bound and the prohibition on following discovered items or child
indexes held. Ordinary and compressed inputs chose the same endpoints and access rules; ordinary
invalid UTF-8 kept its prior replacement behavior.

Malformed, truncated, oversized, invalid-UTF-8 and nested gzip root/robots inputs stopped before
any subsequent request. Every issued request retained its fetch reservation and exact archived
observation/body/time. The full 5,500-fetch ledger allowed zero requests and retained its bytes;
the final available fetch at 5,499 was charged before transport and prevented the robots request.
Existing calls, documents and additional counters remained intact. All results retained candidate
registration, zero qualified sources, zero source checks credited, no facts and no semantic or
coverage admission. No real transport, model, source registration, coverage/latest-run mutation
or actual ledger/archive write occurred. Entity scope and history qualification remain separate.
