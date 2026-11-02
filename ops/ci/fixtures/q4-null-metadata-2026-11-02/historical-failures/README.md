# Original failed discovery records

These are the exact original November 2 failed JFrog and Rapid7 receipts and their
item manifests from archive commit `52632a360f4099f142ed0e10e46338e1d91f1bc9`.
They are public-source pipeline evidence; they contain no credentials.

The four entries were authenticated against the complete 69,873-entry archive
manifest with SHA-256
`3cb739133b60e03d418480e53ee8c454dca616efa8d3585fde87c5eb9ac61438`.
`provenance.json` retains the selected entries and hashes. The selected subset
preserves that earlier authentication and does not independently prove the
complete archive's hash. The full read-only archive replay is recorded separately.

The body and observation fixtures in the parent directory retain the original
source responses. Replaying these failed attempts must keep their original
failure, empty discovery, exact error cause and observation times. They cannot
gain source coverage from a later implementation change.
