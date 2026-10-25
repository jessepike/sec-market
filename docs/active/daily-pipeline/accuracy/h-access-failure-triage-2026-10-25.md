# Retained H access-failure triage

There is no proven endpoint or allowlist repair for the fourteen ordinary failures. I recommend preserving better failure diagnostics first, then a bounded, respectful Axonius host cooldown. Those code changes can stay within the existing source authority; they do not demonstrate recovered access.

This read-only investigation uses acknowledged archive `9e4a9806fdcc1b7cd6f91314b8b4ff4bb4ef2174`, manifest `148842177a7e7d9a5fd5c2ea4574576264a957b41958ee4cdf5effa80ea029c2`. The fourteen original H receipts remain untouched: nine bound HTTP403 observations, four bound HTTP429 observations and one Sysdig host-policy exception without an observation. All fourteen source rows remain identical under J.

## Exact ordinary failures

| Source | Retained result | Historical H task ID | Exact requested URL |
| --- | --- | --- | --- |
| delinea:citation:TR-delinea-5 | 403 | `8329235c3ad51562c00348887b3a87acaa4632d5409eb75a5df3a7dead4acab4` | https://www.globenewswire.com/news-release/2026/03/05/3250113/0/en/delinea-completes-strongdm-acquisition-to-secure-ai-agents-with-continuous-identity-authorization.html |
| sophos:citation:TR-sophos-3 | 403 | `84e2b0c59d7f4338d58b977b836599c4c1b1becb42308aa06fb63e5c122654c9` | https://app.researchpool.com/index.php/provider/moodys-investors-service |
| sysdig:citation:TR-sysdig-1 | host exception | `e7d0f3fc9640b07b25a184a2880f3108a7d6a1717aa25d5cd75d142811331ef7` | https://sysdig.com/press-releases/sysdig-names-hatem-naguib-as-ceo-to-lead-next-generation-of-ai-driven-cloud-security |
| axonius:citation:TR-axonius-2 | 429 | `80c74f6e91490f9f7d258a431d190a7ece12d1bb551c97cfa46bfa8d31410456` | https://www.axonius.com/newsroom/press-release/axonius-surpasses-200m-arr-appoints-joe-diamond-ceo |
| cohesity:citation:TR-cohesity-1 | 403 | `68695ad42c8b88b243f351c0557eacd32be4588813cfe402f0d49b5cbf3af571` | https://www.cohesity.com/newsroom/press/cohesity-becomes-worlds-largest-data-protection-provider-after-completing-combination-with-veritas-enterprise-data-protection-business/ |
| sophos:citation:TR-sophos-2 | 403 | `924e29253874d0d20447ba4cd6bbfc7a353e9e75b14b0fdcaa085e2f7ccb9413` | https://app.researchpool.com/index.php/provider/s-p-global |
| axonius:citation:TR-axonius-1 | 429 | `027dc868c7082e89d0ec110b517545a441681e90c7525220cb6e7afb45eb069b` | https://www.axonius.com/newsroom/press-release/axonius-surpasses-200m-arr-appoints-joe-diamond-ceo |
| beyondtrust:citation:TR-beyondtrust-1 | 403 | `9b0c53421fc260112caad0a7648fefb2f46a2503983cbdb9550759569b30e708` | https://www.globenewswire.com/news-release/2021/08/17/2282045/0/en/BeyondTrust-Completes-Transaction-with-Clearlake-Capital-and-Francisco-Partners.html |
| delinea:citation:TR-delinea-3 | 403 | `bad5585718e431590310b82a1fc693e3e18d7137a0194957aa13c61f9a04528f` | https://www.globenewswire.com/news-release/2026/09/23/3367539/0/en/delinea-appoints-timothy-regan-as-chief-financial-officer.html |
| axonius:citation:TR-axonius-3 | 429 | `cdb0043cddaf273245cf6509d97f0043fcb2bc1da893fae619b81fe22385ca61` | https://www.axonius.com/newsroom/press-release/axonius-closes-200m-series-e-funding-round |
| bigid:citation:TR-bigid-1 | 403 | `b883c61f24ab1597d9f1b64af8d98573efeb82a271b0505fae4da6db9798f032` | https://tracxn.com/d/companies/bigid/__pHSLjAzI2aqF63ud9QosF69usdaBPTT49_kou_rHtgw/funding-and-investors |
| tines:citation:TR-tines-1 | 403 | `9731a5870175e8e99cecf2c1efc16f7a1ad9c7540b477032a813b35839a2f386` | https://www.bloomberg.com/news/articles/2025-02-11/goldman-softbank-back-ai-startup-tines-valued-at-1-13-billion |
| cohesity:official:1 | 403 | `9709ff57e5b23d9ebebf9a75a5a6b381ba3cca1f09d0a40cd3446c98d7a982d1` | https://www.cohesity.com/sitemap.us.xml |
| axonius:official:1 | 429 | `b884fa4ed7d81998eb46e28fdb8525dc04f544f1546827c77823cf729ab055a1` | https://www.axonius.com/sitemap.xml |

The JSON preserves every original task receipt, observation ID/reference and source contract, plus dependencies and each available older successful download/reuse chain. The retained error responses have no denial body, final response host or Retry-After. A403 therefore cannot be attributed to a publisher rule, WAF, paywall or proxy from these bytes alone.

## Proposed bounded fixes

**Failure telemetry is the first fix I would choose.** Ordinary collection constructs `Fetcher(state)` without the existing redirect-diagnostic flag. The schema-1 generic probe enables unexpected-status diagnostics but also omits redirect diagnostics. A policy exception can escape without a response observation, and the generic probe retains only its class. Enable the existing bounded redirect diagnostics for an already-authorized request, and retain typed initial/final-URL rejection metadata. Keep the exact allowed-host checks. Assign an HTTP status only when a real response supplies it. Preserve a narrow denial-header set, especially Retry-After. This is an observability proposal; no runtime change or new request occurred here.

**All four429s are Axonius requests on `www.axonius.com`.** TR-axonius-1 and TR-axonius-2 use the same exact URL. The current shared transport cache reuses full200 responses only, so it does not suppress repeated failed requests. The retained check times span roughly35seconds; no Retry-After is available. A future shared host cooldown can respect the actual header and existing runtime/day limits. A deferred task must stay explicitly deferred/unknown, linked to the triggering observation; it must not fabricate another429, renew a source clock or refund a charge. No immediate retry or access workaround is supported by this evidence.

**The nine403s need access evidence, not a guessed route.** Keep all blocked receipts visible. The Cohesity sitemap and citation already use their approved host; the failures occur before parsing can help. Delinea's issuer inventory is a separate evidence route and does not erase blocked GlobeNewswire citations. ResearchPool's cited URLs are provider listings, so any document-specific replacement would need its own supported citation proposal. Tracxn and Bloomberg denial causes remain unknown. Do not silently swap an endpoint or citation, add credentials or claim that an older successful body repairs today's failed check.

## Sysdig stays unclassified where evidence is absent

The Sysdig citation starts at its approved `sysdig.com` URL and fails with `Unapproved source/redirect host`. Its receipt contains no observation, status, Location, final URL or rejected hostname. The guard is enforcing the declared boundary. The retained data cannot establish whether an alias or another target should be approved, so adding a guessed `www` host is unsupported.

The separate generic Sysdig root probe retains a charged reservation and `ContractError`, with zero observations. This exception class is **not an HTTP status** and does not prove a redirect,403 or429. The companion JSON retains every matching current-H generic row, including its exact run/revision/reservation. The candidate root probe is separate from the citation task and must not be counted as an extra HTTP access failure. No charged reservation is rebased or refunded.

A later already-authorized ordinary check can retain the missing redirect/final-URL diagnostic without following a forbidden host. A source-host policy change would require the actual target and ownership/scope proof, followed by separate review. The disabled J diagnostic plan remains disabled.

No network/source request, model request, repository edit, runtime/policy change, real archive/session/budget write or publication occurred. Every original failure and clock is preserved. The JSON includes consumed-input seals and exact code pins; all remained unchanged.
