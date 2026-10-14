#!/bin/bash
# One actual refresh pipeline; parent orchestration should inspect its receipt, not duplicate collection.
set -euo pipefail
task_repo="$(cd "$(dirname "$0")/.." && pwd)"
cd "$task_repo"
if ! mkdir .refresh-lock 2>/dev/null; then echo 'A refresh is already running.'; exit 3; fi
trap 'rmdir .refresh-lock' EXIT
mkdir -p .collect
export SMP_BRIEF_PATH=docs/active/auto/full-refresh-brief.md
(cd web && npx tsx --tsconfig tsconfig.app.json scripts/export-live-inventory.ts ../.collect/baseline-inventory.json)
node -e "const fs=require('fs');fs.writeFileSync('.collect/baseline-suppliers.json',JSON.stringify(JSON.parse(fs.readFileSync('.collect/baseline-inventory.json')).suppliers))"
# Clear only transient receipts from an earlier run; source data and history remain intact.
rm -f .collect/supplier-checks.json .collect/failed-sources.json .collect/candidates.json .collect/summary.txt
npm --prefix web run refresh:edgar
npm --prefix web run refresh:filing-events
bash scripts/collect.sh
unset CLAUDE_CODE_OAUTH_TOKEN
(cd web && npx tsx --tsconfig tsconfig.app.json scripts/verify-collector-edits.ts)
(cd web && npx tsx --tsconfig tsconfig.app.json scripts/refresh-coverage.ts)
(cd web && npx tsx --tsconfig tsconfig.app.json scripts/export-live-inventory.ts ../.collect/live-inventory.json)
python3 scripts/check-live-sources.py .collect/live-inventory.json .collect/source-bodies .collect/supplier-checks.json
python3 scripts/audit-supplier-receipts.py .collect/supplier-checks.json .collect/source-bodies/source-checks.json
(cd web && SMP_REQUIRE_ALL_ATTEMPTS=1 npx tsx --tsconfig tsconfig.app.json scripts/refresh-coverage.ts)
npm --prefix web run lint
npm --prefix web run test:data
npm --prefix web run build
npm --prefix web run test:e2e
# A caller may publish only to preview after reviewing the fixed data diff.
# This runner has no production promotion path and never grants credentials.
git add web/src/data/generated web/src/data/tracker/suppliers.ts web/src/data/tracker/events.ts web/src/data/evidence.ts
git diff --cached --binary > .collect/data-patch.diff
node -p "require('./web/src/data/generated/refreshCoverage.json').checkedAt" > .collect/expected-coverage-time.txt
echo 'Full refresh attempts and gates finished. Validated data patch prepared for preview-only release; coverage receipt states any failed fields.'
