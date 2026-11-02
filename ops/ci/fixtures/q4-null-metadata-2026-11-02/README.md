# November 2 Q4 parser regression inputs

These are the exact two actual first-party response bodies rejected by the scheduled November 2
collector, compressed for a portable offline regression test. The complete JFrog array has 207
rows and Rapid7 has 323. No rows were removed, rewritten or normalized. The paired observations
retain their exact original raw bytes. The tests run from a clean checkout without environment
variables, a full local archive, network access or credentials.

`provenance.json` pins the compressed files, decoded body hashes/sizes, raw observations, original
URLs/MIME/times and four selected archive-manifest entries. Before copying these fixtures, those
entries were independently checked against complete archive manifest SHA-256
`3cb739133b60e03d418480e53ee8c454dca616efa8d3585fde87c5eb9ac61438` at immutable commit
`52632a360f4099f142ed0e10e46338e1d91f1bc9`. The subset is not a Merkle proof and does not
independently authenticate the full archive. The optional external full-manifest test checks
that original binding when its complete bytes are available.

Gzip creation uses Python's standard-library `gzip.GzipFile`, an empty filename, mtime zero,
compression level 9 and the original complete response bytes. The test pins compressed size/hash,
limits compressed input and decoded output to 2,000,000 bytes each, then checks exact decoded
size/hash before parsing. Compression timestamps and fixture read time create no new source time.

These fixtures test parser compatibility only. They create no new HTTP observation, source
qualification, freshness, fact admission, scheduled-run result or production coverage credit.
