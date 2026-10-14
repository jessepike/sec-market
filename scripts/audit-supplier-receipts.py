#!/usr/bin/env python3
"""Use actual independent fetch metadata instead of model-provided hashes/dates."""
import json
import sys
from pathlib import Path

receipts_path, source_path = map(Path, sys.argv[1:3])
receipts = json.loads(receipts_path.read_text())
sources = {s['url']: s for s in json.loads(source_path.read_text())}
for receipt in receipts:
    receipt['sourceChecks'] = [sources.get(source['url'], {'url': source['url'], 'checkedAt': receipt['checkedAt'], 'status': 'failed', 'reason': 'No independent byte-fetch receipt for this source.'}) for source in receipt['sourceChecks']]
receipts_path.write_text(json.dumps(receipts, indent=2) + '\n')
