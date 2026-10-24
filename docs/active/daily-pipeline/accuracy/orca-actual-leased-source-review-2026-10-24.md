# Orca leased diagnostic: actual run review

## Result

Run `40126516584` completed successfully as a GitHub `workflow_dispatch` on `main`, but its diagnostic evidence is incomplete. It fetched 26 index pages successfully, then received HTTP 302 for page 27. The report contains 90 leads from those pages, no primary sample, `indexComplete=false`, `evidenceComplete=false`, and `ORCA_RESPONSE_INCOMPLETE`. This does not prove a terminal page, a blocked request, or a complete Orca inventory.

The failed request was `https://orca.security/resources/news/page/27/` at `2026-10-24T19:47:09.867651Z`. Its immutable raw observation records `HTTP_302`, status `failed`, and the requested URL. It contains no final URL, `Location`, or body. The evidence cannot identify the redirect destination or establish that page 27 is terminal. No follow-up request was made.

The run used 27 fetch reservations, increasing the daily fetch count from 1,926 to 1,953. It used zero model calls, zero document calls, and zero source checks or qualification credit. The workflow-level execution completed; the evidence collection did not. The source remains unqualified and the run did not publish.

## Authentication and replay

The actual GitHub run is `40126516584`, attempt 1, event `workflow_dispatch`, ref `refs/heads/main`, app revision `53920fcb7312d593c1eff307a6ff5ae5393b3a9e`. The downloaded `source-probe-receipt` artifact is ID `12572678363`; its ZIP SHA-256 is `b539dbec2f42c456b1a631e2993c026a42c9a72a0163e1bf40542cdd2ab732b3`. The copied raw receipt SHA-256 is `7ec3ac7e07c935a506dccc7e33e6ecf5ba240ccf5cc52630609615beb4e1a386` at [orca-source-probe-40126516584-2026-10-24.json](/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/receipts/orca-source-probe-40126516584-2026-10-24.json).

The receipt pins contract H `8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db`, plan SHA-256 `93257fbffe11598ffff5ee7b890fdd0e992d59d4b276d0ad09aa8ddfe56f7d98`, and source `orca:official:1`. Its archive acknowledgement binds commit `3dcd8798c2e5261ded4dd8afea348168ce2224af`, parent `4af7a77efc32afcdfc2c32c6f81b5ad38c1471e4`, manifest SHA-256 `34c98107d3b35af79da17fbce9874e043bb18c326b9b34083904d8d91e0e934e`, 41,005 files, and `refs/archive/market-evidence`.

`GitArchive.verify` checked every entry in the downloaded archive against the acknowledged manifest, including content-addressed objects. The archive was extracted at `/var/tmp/smp-orca-40126516584-20261024/extracted/jessepike-sec-market-3dcd8798c2e5261ded4dd8afea348168ce2224af` in the OrbStack dev VM. I replayed `orca_qualification.replay_diagnostic` against the archived run record and immutable original plan SHA-256 `93257fbffe11598ffff5ee7b890fdd0e992d59d4b276d0ad09aa8ddfe56f7d98`. The live `contracts/source-qualification-probes.json` remained the exact disabled plan, SHA-256 `ad1c5cc234fe4fa69cbceb5370ac74825a37dc80b08528ca908d14b1352e53b4`, throughout the replay. The replay returned an incomplete index, incomplete evidence, the same 90-item inventory, and zero qualification or coverage credit. The memory-backed store recorded zero writes.

The full extracted archive seal was identical before and after replay: 41,009 files, content digest `eab114a22d66d2f8b5f5b0baa51e27092f391da999dcef331f7b0a106b86e405`, file-time digest `6cf088ea5f5d35a3af4c3e0d4043010102e5651e7bc35d0dc8600447cef48661`, 1,906 directories, directory-time digest `52d929d497e5266f25e7b5b7686cb87c482e85ddd022fbaceb2a6a08a43fabf6`.

## Continuity

Compared with the prior fully verified b78 archive (manifest SHA-256 `3971ae961442d6a18c5ed145c64660d68190d91f470acf27b74c3d136f6d6849`, 40,917 entries), the current archive retains every prior path. There are 88 additional paths. Only four shared paths have different bytes: `state/heads/budget-2026-10-24.json`, `state/heads/cloud-governance.json`, `state/heads/cloud-lease.json`, and `state/heads/worker-heartbeat.json`. The latest normal-run head and all other prior manifest entries, including correction, review-queue, and production evidence, remain byte-identical to b78.

The receipt binds immediate parent commit `4af7a77efc32afcdfc2c32c6f81b5ad38c1471e4`. Its `archive-manifest.json` was read from that exact GitHub commit and matched Git blob SHA-1 `9d4bb5866abe98d271fa5be41c783ec3cfe0c601` (8,373,848 bytes) and SHA-256 `59e24454032d40d23e573a97d85f3cbb626d67fc281fe431beefaa9e77dd90a8`. The parent manifest contains 40,923 paths, all present in the fully verified child; only the budget and cloud-lease heads differ, and 82 paths were added. Other parent-manifest entries, including the latest normal-run head, remain byte-identical. The previous b78 comparison above supplies the earlier H continuity check.

## Evidence files and limits

The exact failed response wrapper is `objects/2152210e10fd7b5bc4216a2194893ac367d1d427bcee5d0084d770224cb0418e` (382 bytes, SHA-256 equal to its object name); it points to raw observation `objects/cf0921321cdf3aea8399ae75c59cbba5b5266b2eb21063972eb3175e146e8290` (164 bytes, SHA-256 equal to its object name). The raw response records `HTTP_302`, requested URL, timestamp, and failure status only.

This run is diagnostic evidence only. It does not qualify the source, add verified coverage, prove complete pagination, or authorize source activation. The next decision depends on the existing fetcher's redirect policy and an independently reviewed bounded follow-up; this audit does not infer what lies behind the 302.
