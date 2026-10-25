# Seven-newsroom diagnostic closure

The local operational plan was restored byte-for-byte from `900a51f9875838417dfd3a189457595ba19d578f:contracts/source-qualification-probes.json`. The restored 173-byte plan has raw/canonical SHA256 `ad1c5cc234fe4fa69cbceb5370ac74825a37dc80b08528ca908d14b1352e53b4`, maxRequests=0 and no sources. The current H contract remains exact.

All 27 focused restoration, retained-proof and leased-route tests passed in OrbStack with sockets denied and no skips. Synthetic route tests use isolated temporary state; the retained proof uses its read-only frozen archive. Full raw output is retained in deterministic gzip with exact raw hashes, size and line count in restoration.json. No actual source/model request, archive/state write, staging, commit or push occurred. Root owns the closure commit and promotion.
