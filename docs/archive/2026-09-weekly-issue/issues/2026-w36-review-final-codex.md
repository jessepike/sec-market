1. **Blocker — [verify-issue.ts:200](/Users/jessepike/code/projects/sec-market/web/scripts/verify-issue.ts:200)**  
   **What:** A blank or whitespace-only HTTP 200 body is converted to `{}` and accepted as a valid network anchor.  
   **Why:** In a depth-1 protected build, the git anchor is unavailable; this poisoned response becomes an available zero-entry anchor, allowing rewritten history to pass.  
   **Smallest fix:** Reject an empty body before `JSON.parse`, classify it as a network error, and add a protected/shallow perturbation test.

   All other named lock cases are closed: depth-1 is unavailable; merge parents are checked separately; 404/skipped/errors are unavailable; network failure passes only with a readable git anchor; malformed non-empty responses and redirects are rejected; production may safely omit preview-only additions.

2. **Should-fix — [verify-dist.ts:256](/Users/jessepike/code/projects/sec-market/web/scripts/verify-dist.ts:256)**  
   **What:** The new parser balances tags but still accepts XML-invalid documents, including multiple roots, non-whitespace text outside the root, bare entity references, and malformed attributes.  
   **Why:** `feed.xml` can pass while not being well-formed XML.  
   **Smallest fix:** Enforce one `rss` root, reject non-whitespace root-level text and illegal entities/attributes, and add corresponding perturbations.

Tokenizer: **closed** — [issueHelpers.ts:154](/Users/jessepike/code/projects/sec-market/web/src/data/issueHelpers.ts:154) rejects `1Password` without breaking M/B/K figures, with targeted tests.

Dist identity: **evidence-body, archive-row, GUID/date, and real-pipeline fixture checks are closed**; XML well-formedness remains incomplete as Finding 2 describes.

I could not execute the tests because the managed read-only environment prevented OrbStack from rotating its daemon log; this verdict is based on source and commit-diff inspection.

**Verdict: do not merge.**  
**The empty-HTTP-200 lock-anchor bypass must be closed first.**
