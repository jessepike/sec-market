"""Font assets use the same exact-byte static artifact boundary as the application."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'web/scripts/pipeline'))
from artifacts import build_artifact, pack, stage_files, unpack
from contracts import ContractError
from storage import LocalStore


class FontArtifactTests(unittest.TestCase):
    def test_all_real_font_and_license_bytes_are_included_and_tampering_rejected(self):
        manifest = json.loads((ROOT / 'web/fonts/source-manifest.json').read_bytes())
        with tempfile.TemporaryDirectory() as temporary:
            dist = Path(temporary) / 'dist'
            dist.mkdir()
            (dist / 'index.html').write_text('<html>Font artifact fixture</html>')
            (dist / 'app-release.json').write_text('{}')
            for asset in manifest['assets'] + manifest['licenses']:
                path = dist / asset['localUrl'].lstrip('/')
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes((ROOT / asset['path']).read_bytes())
            store = LocalStore(Path(temporary) / 'state')
            artifact = build_artifact(store, dist, {'headers': []})
            receipt = {'artifactSha256': artifact['sha256']}
            files = stage_files(store, artifact, receipt)
            for asset in manifest['assets'] + manifest['licenses']:
                self.assertEqual(files['static' + asset['localUrl']], (ROOT / asset['path']).read_bytes())
            for asset in [manifest['assets'][0], manifest['licenses'][0]]:
                altered = unpack(store.get(artifact['archive']))
                altered['static' + asset['localUrl']] += b'changed after testing'
                bad = {**artifact, 'archive': store.put(pack(altered))}
                with self.assertRaisesRegex(ContractError, 'Build payload differs'):
                    stage_files(store, bad, receipt)


if __name__ == '__main__':
    unittest.main()
