# PR Newswire historical-policy test delta review

PASS. The single test setup change is safe for integration with current J. The original parser review and worker receipts remain unchanged.

The test now reads the existing committed 204,449-byte H fixture and checks both its raw and canonical SHA-256, `8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db`. Historical diagnostic evidence therefore keeps its original policy when the active market contract is J. The parser, retained verifier, descriptor and policy are unchanged.

The reviewed test SHA moves from `96f47e4056eb03e3dbaf4a5cf2445696d6ac7c92c50e83ec090330cc8c12cd2d` to `f059f6b45732ef935dbed9a30dc6e5e8f38f41dae8a183e8dd6a08019bfd888e`. The diff changes only the historical contract load and its two digest assertions.

Independent checks used the fresh combined application from current J commit `40fe14bb41f6b10c8edc8527ef7f78d7b4d0dcf8` with exactly six PRN overlays. All 2,602 base Git blob files were checked; only the accepted build-spec overlay differs among tracked base files. The active contract remains canonical J `47b9f22636f0e6ea79cf830ae90aab844d8f554d44110a5bb08f29f00266593a`.

| Check | Result |
|---|---|
| Independent retained archive present | 26 passed, no skips |
| Independent archive absent before discovery | 13 portable parser tests passed; 13 retained-evidence tests explicitly skipped; zero frozen-read attempts |
| Current J supplied as original historical H | Rejected in both modes |
| Missing or corrupt historical H fixture | Rejected in both modes before retained proof |
| Worker combined-J full suite | 961 passed, no skips; raw log authenticated |

The absence run denied frozen reads, sockets, subprocesses and LocalStore construction. Portable calendar/date/order/URL/metadata/structure checks continue to execute. Real-body and original-graph checks retain their explicit external-fixture boundary and pass in the separate present run.

No runtime guard or H/J authority boundary was relaxed. This separate test delta provides no source qualification, intake, acknowledgement, freshness or publication credit. No source/model request, frozen write or checkout write occurred. Copying remains root-controlled.
