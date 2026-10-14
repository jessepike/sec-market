#!/bin/bash
# One actual refresh pipeline; parent orchestration should inspect its receipt, not duplicate collection.
set -euo pipefail
task_repo="$(cd "$(dirname "$0")/.." && pwd)"
cd "$task_repo"
if ! mkdir .refresh-lock 2>/dev/null; then echo 'A refresh is already running.'; exit 3; fi
trap 'rmdir .refresh-lock' EXIT
mkdir -p .collect
# A failed run never leaves partial candidate facts in the active checkout.
# Refuse pre-existing edits, and preserve the attempt outside the publishable tree.
if [ -n "$(git status --porcelain --untracked-files=normal)" ]; then echo 'Refresh requires a clean isolated checkout.'; exit 2; fi
attempt_dir=".collect/attempt-$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$attempt_dir/baseline"
python3 - "$attempt_dir/baseline" <<'PYBASE'
import pathlib,sys,shutil,json
root=pathlib.Path('.');dest=pathlib.Path(sys.argv[1])
paths=['web/src/data/tracker/suppliers.ts','web/src/data/tracker/events.ts','web/src/data/evidence.ts']+[str(p) for p in pathlib.Path('web/src/data/generated').glob('*.json')]
for name in paths:
 p=root/name;target=dest/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
(dest/'paths.json').write_text(json.dumps(paths))
PYBASE
finish_attempt() {
  attempt_rc=$?
  if [ "$attempt_rc" -ne 0 ]; then
    python3 - "$attempt_dir" <<'PYHOLD'
import pathlib,sys,shutil,json
root=pathlib.Path('.');dest=pathlib.Path(sys.argv[1]);base=dest/'baseline'
for name in json.loads((base/'paths.json').read_text()):
 p=root/name;held=dest/'held-candidate'/name;held.parent.mkdir(parents=True,exist_ok=True)
 if p.exists(): shutil.copy2(p,held)
 shutil.copy2(base/name,p)
for name in ['supplier-checks.json','refresh-attempt.json','receipt.json']:
 p=root/'.collect'/name
 if p.exists(): shutil.copy2(p,dest/name)
(dest/'blocked.json').write_text(json.dumps({'state':'blocked','publishedDataRetained':True,'lastCompleteDateAdvanced':False,'reason':'Pipeline failed; inspect preserved attempt receipt/log.'},indent=2)+'\n')
PYHOLD
    echo "Refresh held; previous data retained. Attempt: $attempt_dir"
  fi
  rmdir .refresh-lock
  exit "$attempt_rc"
}
trap finish_attempt EXIT
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
(cd web && SMP_REQUIRE_COMPLETE=1 SMP_REQUIRE_ALL_ATTEMPTS=1 npx tsx --tsconfig tsconfig.app.json scripts/refresh-coverage.ts)
node web/scripts/prepare-refresh-publication.mjs
node web/scripts/refresh-publication-gate.mjs
npm --prefix web run lint
npm --prefix web run test:data
npm --prefix web run build
npm --prefix web run test:e2e
# A caller may publish only to preview after reviewing the fixed data diff.
# This runner has no production promotion path and never grants credentials.
git add web/src/data/generated web/src/data/tracker/suppliers.ts web/src/data/tracker/events.ts web/src/data/evidence.ts
git diff --cached --binary > .collect/data-patch.diff
node -p "require('./web/src/data/generated/refreshCoverage.json').checkedAt" > .collect/expected-coverage-time.txt
echo 'Full refresh attempts and gates finished. 100% verified data patch prepared; delivery notification is in .collect/refresh-attempt.json.'
