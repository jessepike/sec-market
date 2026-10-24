# Independent review: bounded candidate traversal

Status: no outstanding actionable findings in the final reviewed scope. This is an offline implementation review, not source qualification or activation.

The final caller and verifier fix the concrete counterexamples reported during review. Nineteen independently constructed adversarial/producer cases pass, the 12 focused tests pass, and unpatched validation accepts the actual three-source start plan while rejecting five altered historical run envelopes. Exact code pins, cases, original observations and archive seals are retained in the JSON companion at `/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/bounded-candidate-traversal-independent-review-2026-10-24.json`.

## Reviewed boundary

Final `onboarding.py` SHA-256: `4ebe29043e7241bfafefdc3b408e5bdc1de397c5a3c4b946b715aa8eebc21cb9`. The parser, contracts, focused tests, unchanged market, operational plan and separate candidate schema-2 plan are independently pinned in the JSON. Every pin remained unchanged through the final verification.

The proposed schema-2 plan has raw hash `fd0ab3821699d577782754cfb1ddc7ba7e4d4f9c2a7c6fd626d4b1f12c6644f7` and canonical hash `7cf3f9b2e3314c930ca5d8c482551fc015fbe4a819f151df9f1dc42f333488e1`. It binds exactly Ping, Delinea and Sonatype under the current whole policy. After the initial review, the integrator replaced the operational schema-1 plan (prior raw hash `62385a674edf896b479dc4fb9330e3e269afcbdc0b6715dd44f9b18608adbf4f`) with byte-identical schema-2 candidate bytes. Independent whole preflight at the operational path passes all three sources under the current contract, with zero requests or writes. This plan selection is not an actual traversal or qualification result.

Whole-plan validation precedes transport. The operation returns before generic and SEC fanout. It follows the source parser's literal sequential continuation, enforces 60 index pages and one sample per source, and remains bounded by 183 logical reservations plus the unchanged shared daily cap. A 60-page boundary without terminal proof remains incomplete. Unknown Delinea card dates stay unknown. A complete index and a failed primary sample remain separate evidence; the report never qualifies or admits a source.

## Concrete findings and final retests

| Previously demonstrated defect | Independent final result |
|---|---|
| Schema-2 start proofs bypassed schema-1's enclosing main/manual/profile/zero-credit provenance checks. | Rehashed actual records with the wrong profile, preview branch, push event, nonzero model count or source-check credit all reject. Original records still validate. |
| Page/sample references could carry a foreign source context. | New wrappers bind the immutable raw response to exact candidate source, proposed adapter and URL. A wrong-source wrapper rejects. |
| Replay stopped at a terminal without rejecting subsequent listed rows. | Every page row must be consumed. Appending a duplicate after Ping's terminal rejects. |
| Fetch counters could omit charges or declare a higher cap; model/document ledger drift and row credit fields were unchecked. | Interval gaps, shifted 5,500→5,518 charges under a forged 9,999 cap, nonfetch drift, injected row facts/credit and Boolean report counters reject. |
| A denial after durable reservation omitted its request/reservation join. | It returns explicit incomplete evidence with one charge and zero transports. Exhaustion before reservation retains zero charges and zero transports. |
| A primary redirect or future timestamp caused the final replay to discard the diagnostic result through an exception. | Both retain their original response, charge and explicit invalid-primary reason with no valid sample shape. |
| Final-response deadline/day handling did not retain a consistent replayable denial. | The last-response deadline and a final sample crossing 23:59:59→00:00:01 both return incomplete with all 18 fictional charges preserved. Sample time failure and completion denial remain separate. |

Additional independent checks reject tampered body references and forged terminal flags. Plan values `true`, `1.0`, `60.0` and `183.0` in integer-only bounds reject before any charge or transport. The producer tests use disposable fictional stores and patched fixture start authority; the actual historical proof checks below use the real unpatched validator.

## Actual retained evidence replay

Archive `21a4f7be073d30cef4547e1bbafcfea413024c12` has manifest SHA-256 `77a402e1335e23e7cb42a6c0bb7aecc841f1bec07684ecc9b70d5c1708b2c7eb`. All 35,148 manifest entries passed exact byte-length/hash checks. The read-only store rejected writes, and an audit guard prohibited network connections and archive writes; no prohibited operation was attempted.

The actual start proofs join diagnostic `40069462824-1`, record SHA-256 `e737f0436db33a783f3e583cb316865357017b4122d5a9c07474b160e89da4f7`, its original paid plan and original observations. All three root-canonical disclosures validate. All seven original response bodies were then parsed independently, with their original requested/final URLs and original fetch times:

| Retained page | Actual result |
|---|---|
| Ping `?o=30`, `?o=40`, `?o=50` | Pages 4, 5 and 6; ten dated cards each; highest advertised page25; literal next offsets40,50,60. No terminal credit. |
| Delinea `/news/page/2`, `/news/page/5` | Twelve undated cards each; advertised highest pages5 and7 respectively; literal next pages3 and6. Terminal unproved. |
| Sonatype `?page=2` | Sixteen dated cards; next3; highest13; nonterminal. |
| Sonatype `?page=13` | Thirteen dated cards; proved page13 terminal with no next request. |

The JSON pins each original observation/body, exact timestamp and derived inventory hash. These isolated historical pages do not prove a complete consecutive actual walk. No requested URL, fetch date or old body was relabeled as a fresh response.

All 35,152 archive files and 1,309 directories have identical before/after content and file/directory modification-time fingerprints. Content fingerprint: `221f84165362669fd84247df60b79baad3cd91b801f1ae04639ae76d09d8ecb0`; file-time fingerprint: `b637e994d3560bf125b7714c03bbf6e80da9486b0572f58122810e20a3c28c7f`; directory-time fingerprint: `33d6edcffa3cd1716296e4b83483478a4aaa922401f61415ab60ee559ce3014d`.

## Remaining operational requirements

No actual source, network or model request, registration, policy, state, archive, allowance, Git or publication change was made. All three remain candidates and the full 557 obligations remain.

A later actual bounded walk must still prove every consecutive index response and its current primary shape sample under the real lease. Eventual activation also needs immutable original-plan replay, inventory-only qualification origins, the explicit closed diagnostic operation and coordinated correction stamp described in `/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/scoped-source-qualification-transition-spec-2026-10-24.md`. Passing this review grants none of that operational credit.
