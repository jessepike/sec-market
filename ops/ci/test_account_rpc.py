import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from account_rpc import refresh_account


class OfficialRefreshProtocolTests(unittest.TestCase):
    def invoke(self, account_type='chatgpt', quiet=False, timeout=2):
        checkpoints, commands, requests = [], [], []
        with tempfile.TemporaryDirectory() as folder:
            home = Path(folder)
            record = home / 'requests.jsonl'
            worker = home / 'server.py'
            worker.write_text('''import json,sys,time
from pathlib import Path
record=Path(sys.argv[1]); kind=sys.argv[2]
for line in sys.stdin:
 value=json.loads(line)
 with record.open('a') as f:f.write(json.dumps(value)+'\\n')
 if kind=='quiet':time.sleep(10)
 if value.get('id')==1:print(json.dumps({'id':1,'result':{}}),flush=True)
 if value.get('id')==2:print(json.dumps({'id':2,'result':{'account':{'type':kind}}}),flush=True)
''')
            def popen(command, **kwargs):
                commands.append((command, kwargs['env']))
                return subprocess.Popen([sys.executable, str(worker), str(record), 'quiet' if quiet else account_type], **kwargs)
            keeper = SimpleNamespace(home=home, checkpoint=lambda:checkpoints.append(True))
            try:
                result = refresh_account(keeper, popen=popen, timeout_seconds=timeout)
            finally:
                if record.exists():requests.extend(json.loads(x) for x in record.read_text().splitlines())
                self.assertEqual(checkpoints, [True])
                self.assertEqual(commands[0][0], ['codex', 'app-server', '--listen', 'stdio://'])
                self.assertEqual(commands[0][1]['CODEX_HOME'], str(home))
        return result, requests

    def test_official_managed_refresh_request_and_checkpoint(self):
        result, requests = self.invoke()
        self.assertTrue(result['managedAccountConfirmed'])
        self.assertEqual(requests[-1], {'id':2,'method':'account/read','params':{'refreshToken':True}})

    def test_api_account_is_rejected_and_auth_still_checkpointed(self):
        with self.assertRaisesRegex(RuntimeError, 'OFFICIAL_MANAGED_ACCOUNT_REFRESH_FAILED'):
            self.invoke(account_type='apiKey')

    def test_timed_out_client_is_stopped_and_auth_still_checkpointed(self):
        with self.assertRaisesRegex(RuntimeError, 'OFFICIAL_REFRESH_CLIENT_TIMED_OUT'):
            self.invoke(quiet=True, timeout=0.1)


if __name__ == '__main__':
    unittest.main()
