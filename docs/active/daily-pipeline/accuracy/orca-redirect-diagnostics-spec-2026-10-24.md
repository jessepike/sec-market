# Orca-only redirect response diagnostics

Status: accepted narrow reliability diagnostic, implemented after the parent confirmed the disabled-plan promotion. Current H, source registrations, source proof authorities, seeds, plan and workflow stay unchanged.

## Actual limit

Authenticated manual main run 40126516584 retained 26 successful index responses and 90 raw leads. Request https://orca.security/resources/news/page/27/ ended with HTTP 302 at 2026-10-24T19:47:09.867651Z. The immutable raw response has no final URL, Location or body. It cannot identify the destination, prove that any next request occurred, or establish a terminal page. Preserve that original report unchanged.

## Small opt-in change

Keep ContractRedirect and the default Fetcher behavior unchanged. Add an opt-in diagnostic subclass of ContractRedirect, selected only when collect.execute_source_probe has already selected the exact bounded_orca_qualification operation. Its HTTP 30x handler records a response before delegating to the existing urllib implementation; redirect_request records urllib's already-derived proposed target before the existing safe_url check and superclass request construction. Preserve all existing host/protocol/DNS checks, default handlers, max_repeats and max_redirections. Do not add a request or retry.

Store an optional redirectDiagnostics object on new observations only when a redirect response or terminal redirect HTTPError exists. Record bounded response URL, integer response status, first raw Location (or null), proposedTargetUrl (or null), and an explicit outcome category. A proposed target means only that a redirect request was considered; it never asserts that transport occurred. An empty Location remains empty, distinct from a missing header. If urllib uses its URI fallback, rawLocation remains null; only the already-derived proposed target may become visible. No URI or other header value is recorded. Record the last HTTPError URL, status, first raw Location and fixed category when relevant. No other response/request headers, cookies, authorization values, response bodies or inferred final URL are captured.

Bound the list at 64 events and each URL/header string at 4,096 characters. Retain explicit truncation flags and original lengths when truncation occurs. Default stdlib loop limits remain lower than this metadata ceiling. The diagnostic must not fail or loosen transport when metadata is truncated.

An unsafe or malformed redirect still cannot follow. On the opt-in path, retain an explicit failed observation with the observed response status/category and metadata when the existing policy or URL parser rejects a redirect; the default path continues to raise exactly as before. Existing HTTPError, network failure, success and retry behavior remain unchanged except optional metadata. Opt-in 304 results do not copy an earlier observation's redirect metadata into newly observed redirect evidence; the original remains available through its retained observation ID. Default 304 output remains unchanged. Failed/redirected results stay incomplete under the unchanged Orca verifier.

## Replay and acceptance

Do not change Orca replay or old observations. The verifier already reads the original immutable raw observation and validates its actual status/final URL/body; optional metadata cannot create completeness. Rehashing metadata cannot turn a 302 into 200 or supply a missing terminal/sample. Run the full original actual Orca report through MemoryStore unchanged and preserve all archive content/file/directory mtime seals.

Use mocked urllib handlers/transports only for regression tests. Compare complete default success/error/304 outputs and existing policy exceptions with the old behavior. Test same-host proposed redirects, exact raw relative Location versus urllib-derived target, empty/missing Location, URI fallback, unsupported scheme, denied host/private target, malformed target, redirect loops/default limits, bounded metadata, and network/HTTP failures after a proposal. Assert no extra transport and no unsafe target transport. Exercise the collector's exact Orca constructor opt-in and assert all other source-probe paths retain the default constructor.

Review and integrate only fetcher.py, the Orca Fetcher constructor call in collect.py, focused tests and this spec/handoff. The operational plan remains disabled until the parent independently elects one capped actual follow-up using the previously reviewed exact 93257fbf plan, followed by exact disabled ad1 restoration. The unit grants zero qualification, source checks, facts, model/doc calls, gates or publication.
