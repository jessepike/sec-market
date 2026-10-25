# Actual scheduled publisher attempt, 2026-10-25

The genuine scheduled publisher **failed** with `DAILY_GATE_BUDGET_EXHAUSTED`. Its state and alert audit passed. It reserved no new gate and produced no new publication.

## Actual result

[Run 40190348786](https://github.com/jessepike/sec-market/actions/runs/40190348786) was created at `2026-10-25T11:47:37Z`, event `schedule`, on main `900a51f9875838417dfd3a189457595ba19d578f`. The safe publication artifact reports `published:false`, `reason:DAILY_GATE_BUDGET_EXHAUSTED`, `errorType:ContractError`. The actual workflow conclusion is failure. H remains `8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db`; the execution revision carried the exact disabled qualification plan.

The post-run Git archive is `496ad86ade09969edab9d79d96f24bbab0a8e3e0`. Manifest SHA256 is `a4cf620a0c8b2f66a8031ecc05c0f7a23be979a9572a41e03eada8b4137d1018`, 9,945,099 bytes, Git blob `ecd621e0bb75eabc84ab733332c523b11aada753`. All 48,060 entries passed byte-size and SHA256 checks.

Compared with the authenticated pre-run archive `d2efafcb8a68d7330e4b700613b29f18b9892346`, the run changed only the cloud-governance, cloud-lease and worker-heartbeat heads and added three session records. All earlier immutable entries remain exact. The shared lease for `github-publisher-40190348786-1` was released at `2026-10-25T11:51:27.283082Z`.

## Unchanged ordinary state

Fetches remain **869**, model calls **80**, documents **38**, independent gate attempts **2/2**. No source/model call, document charge, gate reservation, refund or reset resulted from this publisher attempt.

The ordinary snapshot, every original event/evidence/date row, four fact-provenance references, six admission objects and 38 held queue rows remain exact. Intake stays 264/557. Processing is 40/10,655 reviewed, 10,615 pending and 11 held; historical review is 41/10,655 reviewed, 10,614 pending and 11 held. The private source expiry remains `2026-10-26T15:55:27.307096+00:00`.

Four product-public GETs confirm the existing release `fc8bf0984dbeacbe79519574911837d8b638f42215f6547e31ae8968b29951e4`, sequence 4, code `6d5e87feba4ffbc75e50f35cb564cb8fd91708ca`, snapshot `8ba13011b9d29b875082a551800d57e265238fd7ffd649ff7b99f7072ab25a89`. Public coverage matches its accepted 1,337,257-byte inventory entry and SHA256 `ac8068379c6c79760331711bfb7bb6387fbc639f9ab6f921713502c6982d47fc`; all six public correction groups remain. The accepted public expiry stays **2026-10-26T12:45:29.479727+00:00**. The private expiry has not become a public freshness claim.

[Issue 14](https://github.com/jessepike/sec-market/issues/14) remains open and assigned to jessepike. Its body was updated at `11:51:44Z` with this actual run link. Automatic drill `40190672082` was skipped. No successful publisher or drill outcome is inferred from the audit.

## Retained proof and reuse

The full authenticated immediate post-publisher baseline remains read-only at `/var/tmp/smp-scheduled-monitor-acceptance-20261025/scheduled-publisher-40190348786/post-publisher-extracted` in the OrbStack dev VM. Unchanged entries were hardlinked from the frozen d2ef baseline; changed and new exact-commit files were hash checked. Frozen baseline content, file mtime and directory mtime seals remained unchanged. No LocalStore constructor or archive write was used by the verifier.

Safe receipts, archive metadata, raw public output, exact execution policy/plan, issue metadata, full seals and read-only harnesses are indexed at `/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/receipts/scheduled-publisher-attempt-2026-10-25/receipt-index.json`. The companion JSON distinguishes audit PASS from actual publisher FAILURE. This evidence is separate from the still-pending genuine scheduled-monitor acceptance. A later publisher must use ordinary available daily capacity and normal gates.
