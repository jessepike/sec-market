import hashlib
import io
import json
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

import preview_data

GATE = 4242


def bundle(files):
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w') as z:
        for name, raw in files.items():
            z.writestr(name, raw)
    return out.getvalue()


def world(files=None, receipt=None, run=None, digest=None, generated=None):
    files = files or {'dailyMarket.json': b'{"runId":"r"}\n', 'dailyMarket.seal.json': b'{}'}
    inner = generated if generated is not None else bundle(files)
    rec = {'result': 'pass', 'githubRunId': GATE, 'appRevision': 'a' * 40, 'runId': 'r',
           'generatedSha256': hashlib.sha256(inner).hexdigest()}
    rec.update(receipt or {})
    outer = bundle({'gate-receipt.json': json.dumps(rec).encode(), 'generated.zip': inner})
    meta = {'id': 7, 'name': 'daily-market-gate', 'expired': False,
            'digest': digest or 'sha256:' + hashlib.sha256(outer).hexdigest()}
    gate = {'path': '.github/workflows/market-release-gate.yml', 'head_branch': 'main',
            'status': 'completed', 'conclusion': 'success', 'head_sha': 'a' * 40}
    gate.update(run or {})

    def api(path, binary=False):
        if path == f'actions/runs/{GATE}':
            return gate
        if path.startswith(f'actions/runs/{GATE}/artifacts'):
            return {'artifacts': [meta]}
        if path == 'actions/artifacts/7/zip':
            return outer
        raise AssertionError(path)
    return api, files


class AcceptedFilesTests(unittest.TestCase):
    def test_passed_gate_bundle_is_returned(self):
        api, files = world()
        got, receipt = preview_data.accepted_files(GATE, api)
        self.assertEqual(got, files)
        self.assertEqual(receipt['runId'], 'r')

    def test_refuses_anything_but_a_passed_main_gate(self):
        for run in ({'head_branch': 'preview'}, {'conclusion': 'failure'}, {'path': '.github/workflows/web.yml'}):
            api, _ = world(run=run)
            with self.assertRaises(RuntimeError):
                preview_data.accepted_files(GATE, api)

    def test_refuses_transport_or_receipt_mismatch(self):
        cases = ({'digest': 'sha256:' + '0' * 64}, {'receipt': {'generatedSha256': '0' * 64}},
                 {'receipt': {'result': 'fail'}}, {'receipt': {'appRevision': 'b' * 40}})
        for case in cases:
            api, _ = world(**case)
            with self.assertRaises(RuntimeError):
                preview_data.accepted_files(GATE, api)

    def test_refuses_paths_outside_the_data_folder(self):
        for name in ('../x.json', 'sub/x.json', 'x.ts', '.hidden.json'):
            api, _ = world(generated=bundle({name: b'{}'}))
            with self.assertRaises(RuntimeError):
                preview_data.accepted_files(GATE, api)


class SyncTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.remote, self.repo = root / 'remote.git', root / 'work'
        run = lambda *a, cwd=root: subprocess.run(a, cwd=cwd, check=True, capture_output=True)
        run('git', 'init', '--quiet', '--bare', '--initial-branch=preview', str(self.remote))
        run('git', 'clone', '--quiet', str(self.remote), str(self.repo))
        (self.repo / 'web/src/data/generated').mkdir(parents=True)
        (self.repo / 'web/src/data/generated/dailyMarket.json').write_bytes(b'{"runId":"old"}\n')
        run('git', 'checkout', '--quiet', '-b', 'preview', cwd=self.repo)
        run('git', 'add', '.', cwd=self.repo)
        run('git', '-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '--quiet', '-m', 'base', cwd=self.repo)
        run('git', 'push', '--quiet', 'origin', 'preview', cwd=self.repo)

    def tearDown(self):
        self.tmp.cleanup()

    def remote_file(self):
        return subprocess.run(['git', '--git-dir', str(self.remote), 'show', 'preview:web/src/data/generated/dailyMarket.json'],
                              capture_output=True, check=True).stdout

    def test_commits_accepted_data_to_preview_once(self):
        api, files = world()
        with patch.object(preview_data, 'preview_accepts', return_value=True):
            first = preview_data.sync(self.repo, GATE, api)
            second = preview_data.sync(self.repo, GATE, api)
        self.assertTrue(first['synced'])
        self.assertEqual(self.remote_file(), files['dailyMarket.json'])
        self.assertEqual(second, {'synced': False, 'reason': 'PREVIEW_ALREADY_CURRENT'})
        author = subprocess.run(['git', '--git-dir', str(self.remote), 'log', '-1', '--format=%ae', 'preview'],
                                capture_output=True, text=True, check=True).stdout.strip()
        self.assertEqual(author, 'jesse@keatingpike.com')

    def test_skips_when_preview_checks_refuse(self):
        api, _ = world()
        with patch.object(preview_data, 'preview_accepts', return_value=False):
            result = preview_data.sync(self.repo, GATE, api)
        self.assertEqual(result, {'synced': False, 'reason': 'PREVIEW_CHECKS_REFUSE_THIS_DATA'})
        self.assertEqual(self.remote_file(), b'{"runId":"old"}\n')


if __name__ == '__main__':
    unittest.main()
