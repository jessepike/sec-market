# Independent watchdog repair review

PASS for controlled integration. Actual GitHub notification delivery remains unexercised.

The reviewed source is `/var/tmp/smp-watchdog-historical-contract-20261026/app`, based on `f59d9ec2eee8da6a23031dc640d3d51bbcadb8a7`. All four payloads authenticate against the worker index `c57a6a86529d7fd16ec8d2e4c168b7af33afb3517f09f1144be7cbf04940101d`. Only the freshness workflow and historical coverage test change among tracked files; all 3,057 others, including the production probe, all operations tests, web and contracts, remain byte-exact.

## Historical fixture

The gzip contains exactly the existing 284,062-byte H contract, raw SHA-256 `24221c946781559c0ff3626e4e479c4647da915d0f2d7559ea88046982532c3c`. Every original assertion node in the 16 historical methods remains exact; the other original watchdog test file is unchanged. The temporary root gives the historical main-loop test its own H contract. The production J contract still fails the original H receipt bindings, and the new read trap proves that this historical loop does not read that mutable contract.

I independently reproduced the unrepaired historical test module: 16 tests, four failures and three errors, no skips, with sockets denied. The repaired complete watchdog suite passes all 55 tests, no skips, in 0.947 seconds with sockets denied. The complete mocked notify loop retains unhealthy intake, pending/held processing, history and held-claim reasons and an open health issue response.

## Observer notification

The exact inline programs are exercised by the new tests. Named tests gate the unchanged production probe. The wrapper preserves exit 2 for unhealthy results and requires a strict, bounded JSON result whose health, reasons, exit code and acknowledged notification agree. An invalid or missing result cannot turn the probe green.

The separate reporter runs after the observer job without checkout or untested source execution. Dynamic run and outcome values enter through environment data, are validated, and are passed to gh as argument arrays. It creates or updates only its distinct observer-failure issue, refuses issue 10, and cannot close the health issue. Recovery requires successful tests and a trusted acknowledged probe result; an honestly unhealthy but reported probe can recover the observer alert while the actual health alert stays open. Missing setup outputs, skipped/cancelled probe, invalid receipts or failed API acknowledgements retain failure. Owner assignment occurs only on creation. The legacy job, all operational budgets, source clocks, production guards and existing five-minute timeouts are unchanged.

No finding requires a code change. Local mocks prove program behavior, not actual GitHub delivery or phone/email delivery. Root must retain the actual final-preview workflow revision, job outcomes, probe receipt and GitHub issue acknowledgement. A platform failure that prevents the reporter job from starting remains unreported by this job.

## Exact pins

- `.github/workflows/freshness.yml`: `54522c20d51ff154bc2481599bd40d09ea203467d5de7d260577de48c54b355a`
- `ops/watchdog/test_coverage_reader.py`: `cb8db2e3fe1b318a665e893d682317a6b947db70e41c60f0742514ba21b19557`
- `ops/watchdog/test_freshness_workflow.py`: `b6589bab97b668e46fb1279a45e582cc375b512bf118a7a31667481e196e9483`
- `docs/active/daily-pipeline/accuracy/receipts/coverage-monitor-inventory-bound-read-2026-10-25/current-original-contract.json.gz`: `eafdee51b2141d881efa8fd6b9716283ff29555fc75654e57a3ab882ee52895e`

No finish file, real archive state, source/model endpoint, issue, Git ref or workflow run was mutated by this review. This disjoint watchdog unit can inherit a passing ancestor canary only after the final descendant diff and the full canary dependency closure are authenticated as unchanged. This review does not claim that future proof.
