"""Pinned six-group historical mechanics. Never truncate the current request inventory."""
from contextlib import contextmanager
import json
from pathlib import Path
import shutil
import tempfile
from contracts import digest
FIXTURES=Path(__file__).parent/'fixtures'
def historical_requests():
 raw=(FIXTURES/'accepted-six-correction-requests-2026-10-25.json').read_bytes()
 assert digest(raw)=='9c9fbe0d3d40ece11e1407ce9460086c732f62da88d3b0f220ab9d6f8757da00'
 value=json.loads(raw);assert len(value['groups'])==6
 return value
def historical_stamp():
 raw=(FIXTURES/'accepted-six-correction-stamp-J-2026-10-25.json').read_bytes()
 assert digest(raw)=='365058911a182610cde401307fb30cc1855930b7940969440a618441cbbef9b2'
 return json.loads(raw)
@contextmanager
def historical_repo(root):
 with tempfile.TemporaryDirectory(prefix='synthetic-historical-six-') as temporary:
  repo=Path(temporary)
  for rel in ('contracts/factual-baseline.json','web/src/data/tracker/originals.json'):
   p=repo/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/rel,p)
  requests=repo/'contracts/factual-corrections.json'
  requests.write_bytes((FIXTURES/'accepted-six-correction-requests-2026-10-25.json').read_bytes())
  stamp=repo/'web/src/data/tracker/factualCorrectionPolicy.json'
  stamp.write_bytes((FIXTURES/'accepted-six-correction-stamp-J-2026-10-25.json').read_bytes())
  historical_requests();historical_stamp()
  yield repo
