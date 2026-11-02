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


class CommittedSeed:
    """Authenticated committed inputs for portable Q4 tests, without archive heads."""
    def __init__(self, repo):
        import q4_qualification_seed as seed
        from contracts import canonical
        self.repo, self.touched, self.files = Path(repo), {}, {}
        raw = seed._payload(self.repo, seed.PACKAGE)
        self.manifest = json.loads(raw)
        assert canonical(self.manifest) == raw and len(self.manifest['files']) == 55
        self.manifest_sha256 = digest(raw)
        for entry in self.manifest['files']:
            pin = {key: entry[key] for key in ('path', 'sha256', 'bytes')}
            body = seed._payload(self.repo, pin)
            assert entry['key'] not in self.files
            self.files[entry['key']] = body
            path = self.repo / entry['path']
            self.touched[str(path)] = (digest(body), len(body), path.stat().st_mtime_ns)

    def raw(self, key):
        return self.files.get(key)

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
        for name, before in self.touched.items():
            path = Path(name)
            raw = path.read_bytes()
            assert (digest(raw), len(raw), path.stat().st_mtime_ns) == before


def frozen_j_asset(repo, name="market.json"):
    """The historical J test subject, never the mutable active policy."""
    pins = {'market.json': ('47b9f22636f0e6ea79cf830ae90aab844d8f554d44110a5bb08f29f00266593a', 206939), 'dailyMarket.json': ('7120790449e8a4427446e2a62d69889cf651692153e6624359c50daa0379197f', 7696749), 'dailyMarket.seal.json': ('6e0cec0115cd21a6165b901b91f563da5588e8e335147e05715d95ce1ba065d7', 276)}
    assert name in pins
    raw = (Path(repo) / "web/scripts/migration-proofs/three-source-j-original" / name).read_bytes()
    assert (digest(raw), len(raw)) == pins[name]
    return json.loads(raw)
