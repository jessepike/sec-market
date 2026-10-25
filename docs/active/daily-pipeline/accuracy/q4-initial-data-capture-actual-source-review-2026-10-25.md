# Actual Q4 initial-data capture review, 2026-10-25

The actual two-request diagnostic passed. Both approved GETs returned HTTP 200 JSON, both bodies were retained, and the existing report verifier accepted the complete archived proof. Qualification, coverage credit, semantic admission, and new facts remain zero.

## Actual run and archive

- GitHub run [40184027106](https://github.com/jessepike/sec-market/actions/runs/40184027106) was a manual run on main commit `ab6a7c68f5d8deeb3dfbe56f2ad32dfa71577bc4`. It completed successfully at `2026-10-25T10:19:59Z`.
- Artifact `12595119064`, `source-probe-receipt`, is 1,934 bytes with SHA256 `ff0706e1e6c8c759364012b802a937f0a90a2e2089b95ef7d8251ed74741866f`. Its sole ZIP member exactly matches the retained receipt.
- The acknowledged archive is `d6606a4f5dd1e1afc5f16dea6d91bc422347f8aa`. Its 9,941,943-byte manifest has SHA256 `40873bfd2dca9836b58ac325a3afb32919fb463b2082752cb72fc785a2d7239d` and Git blob `48e46986a0ea5117dddd983ba64a6c646c8d98a9`. Every one of its 48,045 entries passed SHA256 and size checks.
- The read-only materialization is `/var/tmp/smp-q4-initial-data-actual-40184027106-20261025/extracted` in the OrbStack dev VM. It reused 48,031 unchanged files from the authenticated immediate baseline and retrieved only 14 changed or new files from the exact acknowledged Git commit. Changed destination links were removed before writing. No frozen archive was opened through LocalStore.

The immediate baseline was post-publisher archive `6708f37f73822d411d5ec771b307cd829c22e31d`, manifest `8f7ae5e95610aba19ff68be30053bd4e0703a288b9482d0b9118f61cbf85350d`. Its ledger already included the genuine scheduled collection. The earlier six-script capture archive `9634b916c15b18f38605a168f7642de764670aab` was used only for ancestral preservation and source-proof joins.

## Actual responses

| Source | Source response time | Status and type | Retained body |
|---|---|---|---|
| JFrog | `2026-10-25T10:19:17.166772Z` | `200`, `application/json; charset=utf-8` | 282,783 bytes, `f7d84b288a6665280f4b8ade996b0bf64fe9c3fa0ea7a8a15b1adfb0826ccc19` |
| Rapid7 | `2026-10-25T10:19:17.492289Z` | `200`, `application/json; charset=utf-8` | 414,550 bytes, `cf3c57d1c2080d65656e9f291eca371aefd99909476d413bb5c90155bc742db8` |

Both final URLs exactly match their approved URLs. Both actual transport-error and denial fields are null. The artifact retains the original request, response, and source clocks. The JSON companion includes exact URLs, wrappers, raw observation references, response fields, and lossless body retention metadata.

## Budget and preservation

The ledger moved from 865 to 867 fetches. Model calls stayed at 80, documents at 38, and gate attempts at 2. The retained escrow first reserved the existing 5,500-fetch ceiling and the final checkpoint restored the actual 867 count. The complete authenticated parent chain is baseline → bootstrap `0e7075cf4e2ddb267634c2d75b72ef9f5d723b93` → escrow `531728e140108669f9b04d20784c9ca74f8463cb` → acknowledged final archive. The diagnostic lease was released at `2026-10-25T10:19:17.929709Z`.

All 39,426 immutable baseline entries and 36,700 immutable entries from the earlier 9634 archive remain exact. Only the current-day budget head and cloud lease changed among existing baseline files. All 8,605 other normal heads remain exact. The snapshot, four fact references, eight event/evidence pairs, and 38 held queue items stayed unchanged. Intake remains 264/557. Processing remains 40/10,655 reviewed with 11 held; historical review remains 41/10,655 reviewed with 11 held. The private source expiry stays `2026-10-26T15:55:27.307096+00:00`.

All six existing admissions and their group policy hashes replayed unchanged. The archived production head remains release `fc8bf0984dbeacbe79519574911837d8b638f42215f6547e31ae8968b29951e4`, sequence 4. Root owns the separate live public checks; this audit issued no publication or gate attempt. Actual publisher callback `40184332299` skipped its publish job, and rollback callback `40184352939` skipped rollback and restore.

## Cold JSON inspection

Each envelope contains only `GetPressReleaseListResult`. JFrog returned 206 records, from literal `10/21/2026 03:00:00` through `09/16/2020 02:13:00`. Rapid7 returned 323 records, from literal `10/21/2026 09:00:00` through `07/06/2015 00:00:00`. Both lists are ordered by descending literal date. The dates contain no timezone, so this inspection assigned none.

Neither envelope contains TotalRecords, an error field, a paging token, or an explicit terminal field. Every returned Body field is null. All records have detail links and distinct workflow IDs. The retained cold-inspection JSON lists five primary detail leads per source, including the October 21 JFrog AI-SEC and DevGovOps announcements and the October 21 Rapid7 threat report. Those links and PDFs were not fetched. I recommend a separate scoped design using the exact returned primary detail leads; `pageSize=-1` alone does not establish complete source traversal.

## Verification and retained proof

The actual hosted runner discovered 877 tests, skipped 23 tests requiring VM-local retained fixtures, and executed 854 successfully in 67.534 seconds. Its complete 226,623-byte raw log is retained as deterministic gzip, with raw SHA256 `a86ce7114673373998e63250c5590cbfd6f05a625be741ed5c84f9b2b3e07b9c` and gzip SHA256 `55f247bc1be44bccb8a1ec7a8d76d559ddb0d5009161c1d36280fd296bf18715`; byte-exact decompression was checked.

The separate local replay ran in OrbStack with network socket connections and LocalStore initialization denied. It accepted the actual complete report, replayed all six admissions, and rechecked 77 consumed archive seals plus the baseline seals. The audit harness, exact input metadata, budget parent proof, raw artifact, gzip source bodies, cold JSON inspection, and complete log are retained under `/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/receipts/q4-initial-data-capture-actual-2026-10-25/`. The companion JSON inventories their exact hashes and sizes. No JavaScript was executed and no source or model request was made by the verifier.

The archived active plan has raw SHA256 `a316e39658c2e9b5872adeb6008ef138618c8b20a080ca78ee458bd3e51f0ddc` and canonical SHA256 `5ec3a0fc8588e64af13f8caeec32f3c4327f3b60c2526123ff49b41d219a8dae`. Report replay uses that immutable archived plan and remains valid after the operational plan is disabled by root.
