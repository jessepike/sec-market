"""Offline actual fixtures. The archive is always read-only; overlays stay in memory."""
import json
from pathlib import Path

from contracts import digest

ARCHIVE = Path('/var/tmp/smp-next-seven-actual-40190857026-20261025/extracted')
MANIFEST = '8da12977648ce0f6ed62f16de0b52c2257977f41404145adbecb363069e037e1'
H = '8b44bcbec679c178836408c4d98c7230a85572784b0257ef21d21d3b03b445db'


class ReadOnlyArchive:
    def __init__(self):
        raw = (ARCHIVE / 'archive-manifest.json').read_bytes()
        assert digest(raw) == MANIFEST and len(raw) == 9979636
        self.entries = {r['key']: r for r in json.loads(raw)['files']}
        assert len(self.entries) == 48245
        self.touched = {}

    def raw(self, key):
        path = ARCHIVE / 'state' / key
        entry = self.entries.get('state/' + key)
        if entry is None:
            assert not path.exists()
            return None
        raw = path.read_bytes()
        assert digest(raw) == entry['sha256'] and len(raw) == entry['bytes']
        self.touched[str(path)] = (digest(raw), len(raw), path.stat().st_mtime_ns)
        return raw

    def read(self, key):
        raw = self.raw(key)
        return json.loads(raw) if raw is not None else None

    def get(self, ref):
        raw = self.raw(ref['key'])
        if raw is None:
            raise FileNotFoundError(ref['key'])
        assert digest(raw) == ref['sha256'] and len(raw) == ref['bytes']
        return raw

    def assert_unchanged(self):
        for name, seal in self.touched.items():
            path = Path(name)
            raw = path.read_bytes()
            assert (digest(raw), len(raw), path.stat().st_mtime_ns) == seal


class Overlay:
    def __init__(self, base, files=None):
        self.base, self.files = base, dict(files or {})

    def read(self, key):
        return json.loads(self.files[key]) if key in self.files else self.base.read(key)

    def get(self, ref):
        raw = self.files.get(ref['key'])
        if raw is None:
            return self.base.get(ref)
        assert digest(raw) == ref['sha256'] and len(raw) == ref['bytes']
        return raw
