"""Exact three-row policy, authenticated capture closure and inventory seed tests."""
import copy
import json
import os
from types import SimpleNamespace
from pathlib import Path
import socket
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "web/scripts/pipeline"), str(ROOT / "ops/ci")]
from contracts import canonical, digest, validate_contract
from storage import LocalStore
import q4_intake_fixtures as fixtures
import three_source_qualification_seed as seed
import three_source_qualification_origin as three
import source_qualification_origin as origins

AT = "2026-10-27T16:00:00Z"

class Empty:
    def get(self, ref): raise FileNotFoundError(ref["key"])
    def read(self, key): return None

class Committed:
    def __init__(self):
        old = fixtures.CommittedSeed(ROOT)
        self.files = dict(old.files)
        manifest = json.loads(seed._payload(ROOT, seed.PACKAGE))
        for row in manifest["files"]:
            self.files[row["key"]] = seed._payload(ROOT, {k: row[k] for k in ("path", "bytes", "sha256")})
    def get(self, ref):
        raw = self.files[ref["key"]]
        assert digest(raw) == ref["sha256"] and len(raw) == ref["bytes"]
        return raw
    def read(self, key): return json.loads(self.files[key]) if key in self.files else None

class QualificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.current = json.loads((ROOT / "contracts/market.json").read_bytes())
        cls.store = Committed()
        cls.original = json.loads(cls.store.get(three.AUTHORITY["originalContract"]))
        cls.transition = json.loads(cls.store.get(three.AUTHORITY["transition"]))
    def setUp(self):
        self.no_network = patch.object(socket.socket, "connect", side_effect=AssertionError("NO_NETWORK"))
        self.no_network.start(); self.addCleanup(self.no_network.stop)
    def test_exact_positive_three_rows_and_inverse_preserve_74_557_and_all_other_fields(self):
        validate_contract(self.current)
        self.assertEqual(three.validate_rows(self.original, self.current, self.transition), self.original)
        self.assertEqual(len(self.current["suppliers"]), 74)
        changed = [i for i, pair in enumerate(zip(self.original["sources"], self.current["sources"])) if pair[0] != pair[1]]
        self.assertEqual(changed, [7, 8, 19])
        for i in changed:
            for key in ("id", "supplierId", "family", "allowedHosts", "seedEvidenceUrls", "maxPages", "required"):
                self.assertEqual(self.original["sources"][i][key], self.current["sources"][i][key])
    def test_active_K_probe_plan_is_exact_disabled_with_zero_requests(self):
        from onboarding import validate_qualification_probe_plan
        class NoRead:
            def get(self, *_): raise AssertionError('disabled plan cannot read source proof')
            def read(self, *_): raise AssertionError('disabled plan cannot read state')
        value = validate_qualification_probe_plan(self.current, NoRead(), ROOT / 'contracts/source-qualification-probes.json')
        self.assertEqual(value['maxRequests'], 0)
        self.assertEqual(value['plan']['sources'], [])
        self.assertEqual(len((ROOT / 'contracts/source-qualification-probes.json').read_bytes()), 173)

    def test_unknown_policy_extra_row_and_transition_mutations_denied(self):
        for mutate in (lambda x: x["sources"][0].update(required=False),
                       lambda x: x["sources"][7].update(maxPages=8),
                       lambda x: x.update(version="unreviewed")):
            altered = copy.deepcopy(self.current); mutate(altered)
            self.assertFalse(three.is_successor(altered))
            with self.assertRaises(ValueError): three.inverse_policy(altered, self.store)
        bad = copy.deepcopy(self.transition); bad["changes"].reverse()
        with self.assertRaises(ValueError): three.validate_rows(self.original, self.current, bad)
    def test_actual_capture_full_proof_and_known_union_are_inventory_only(self):
        proof = three._proof(self.original, self.store)
        self.assertEqual([len(row["items"]) for row in proof["streams"]], [127, 47, 56])
        self.assertEqual(proof["authority"], "inventory_only")
        self.assertEqual([row["acceptedSamples"] for row in proof["captures"]], [1, 2])
        self.assertEqual([row["outerIdentity"]["githubRunId"] for row in proof["captures"]], ["40529776219", "40533017666"])
        self.assertEqual(proof["facts"], []); self.assertEqual(proof["modelCalls"], 0)
        for sid, n in zip(three.SOURCE_IDS, (127, 47, 56)):
            prior = origins.qualification_predecessors(self.current, sid, self.store, AT)
            self.assertEqual(len(prior), 1)
            self.assertTrue(origins.is_qualification_predecessor(prior[0]))
            result = origins.resolve_inventory_origin(prior[0], self.current, sid, self.store, AT)
            self.assertEqual(result["authority"], "inventory_only"); self.assertEqual(len(result["items"]), n)
        with self.assertRaises(ValueError): three.predecessors(self.current, three.SOURCE_IDS[0], self.store, "2026-10-27T00:00:00Z")
    def test_portable_union_payloads_keep_old_J_bytes_and_only_pinned_immutable_keys(self):
        manifest = json.loads(seed._payload(ROOT, seed.PACKAGE))
        self.assertEqual(manifest['originalJPackage'], seed.q4seed.PACKAGE)
        committed = Committed()
        self.assertTrue(set(fixtures.CommittedSeed(ROOT).files).issubset(committed.files))
        self.assertTrue(all(not key.startswith(('heads/', 'budgets/', 'sessions/', 'leases/')) for key in committed.files))
        self.assertEqual(len([key for key in committed.files if key.startswith('observations/')]), 17)
        for entry in manifest['files']:
            ref = {key: entry[key] for key in ('key', 'sha256', 'bytes')}
            self.assertEqual(len(committed.get(ref)), entry['bytes'])
        # Full old-HTML semantic/preservation closure requires the restored J archive,
        # matching the existing external Q4 test. Never pretend an empty store is that archive.
        with self.assertRaises(FileNotFoundError):
            seed.validate_seed(ROOT, Empty(), self.current, AT)

    def test_retained_date_overlay_preserves_all_original_pairs_without_fresh_clock(self):
        from selection import date_partitions
        proof = three._proof(self.original, self.store)
        for sid, n in zip(three.SOURCE_IDS, (127, 47, 56)):
            row = next(s for s in self.current['sources'] if s['id'] == sid)
            prior = three.predecessors(self.current, sid, self.store, AT)[0]
            retained = three.resolve(prior, self.current, sid, self.store, AT)
            self.assertEqual(len(retained['itemDates']), n)
            stream = next(s for s in proof['streams'] if s['sourceId'] == sid)
            expected = {r['url']: r['calendarDay'] for r in stream['stream']['records'] if r.get('calendarDay')}
            expected.update({s['url']: s['shape']['publicationCalendarDay'] for s in stream['stream'].get('knownSeedsOutsideObservedList', [])})
            self.assertEqual(retained['itemDates'], expected)
            self.assertEqual(retained['originalAsOf'], stream['originalAsOf'])
            fresh_urls = stream['items'][:25]
            fresh = {'items': fresh_urls, 'itemModified': {u: expected[u] for u in fresh_urls},
                     'itemDates': {u: expected[u] for u in fresh_urls}}
            before = copy.deepcopy(fresh)
            joined = three.scheduling_view(fresh, self.current, row, self.store, AT)
            self.assertEqual(joined['itemModified'], expected)
            self.assertEqual(fresh, before)
            self.assertEqual(joined['itemDates'], before['itemDates'])
            self.assertFalse(date_partitions(retained['items'], joined['itemModified'], self.current['collection'], AT)[2])
            url = fresh_urls[0]; fresh['itemModified'][url] = '2026-10-26'
            self.assertEqual(three.scheduling_view(fresh, self.current, row, self.store, AT)['itemModified'][url], '2026-10-26')
            fresh['itemModified'].pop(url)
            self.assertNotIn(url, three.scheduling_view(fresh, self.current, row, self.store, AT)['itemModified'])
        cato = proof['streams'][0]['stream']['knownSeedsOutsideObservedList']
        self.assertEqual({s['shape']['publicationCalendarDay'] for s in cato}, {'2026-02-24', '2026-07-27'})

    def test_two_cycle_off_prefix_cursor_uses_retained_day_without_claiming_fresh_signature(self):
        from selection import select_documents
        sid = three.SOURCE_IDS[0]
        row = next(s for s in self.current['sources'] if s['id'] == sid)
        retained = three.resolve(three.predecessors(self.current, sid, self.store, AT)[0], self.current, sid, self.store, AT)
        url = sorted(retained['items'])[-1]
        fresh = {'items': [], 'itemModified': {}, 'itemDates': {}}
        view = {**three.scheduling_view(fresh, self.current, row, self.store, AT), 'items': [url]}
        wrong = {url: {'modified': '', 'checkedAt': AT}}
        right = {url: {'modified': view['itemModified'][url], 'checkedAt': AT}}
        self.assertEqual(select_documents(view, wrong, self.current['collection'], AT)[0], [url])
        self.assertEqual(select_documents(view, right, self.current['collection'], AT), ([], []))
        self.assertEqual(fresh['itemModified'], {})

    def test_K_seed_keeps_ordinary_lease_ack_and_existing_heads_guards(self):
        import collect
        checked = {'files': self.store.files, 'manifestSha256': seed.PACKAGE['sha256'],
                   'contractSha256': digest(self.current), 'preservation': {}, 'qualificationInventory': {}}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); state = LocalStore(root / 'state')
            session = {'sessionId': 'github-123-1', 'role': 'collector', 'appRevision': 'a' * 40,
                       'executionMode': 'github_subscription', 'startedAt': AT,
                       'restored': {'commit': 'b' * 40}}
            LocalStore(root).write_once('session.json', session)
            state.compare_and_swap('cloud-lease', None, {'sessionId': session['sessionId'],
                'expiresAt': '2026-10-27T18:00:00Z'})
            event = root / 'event.json'
            event.write_bytes(canonical({'repository': {'full_name': 'jessepike/sec-market', 'private': True},
                                         'inputs': {'source_probe': 'false'}}))
            env = {'GITHUB_ACTIONS': 'true', 'GITHUB_REPOSITORY': 'jessepike/sec-market',
                   'GITHUB_REF': 'refs/heads/main', 'GITHUB_EVENT_NAME': 'workflow_dispatch',
                   'GITHUB_SHA': session['appRevision'], 'GITHUB_RUN_ID': '123', 'GITHUB_RUN_ATTEMPT': '1',
                   'GITHUB_EVENT_PATH': str(event)}
            calls = []
            def checkpoint(root, store, current, phase, result):
                # Synthetic remote acknowledgement; real seed/context/lease checks execute.
                calls.append(result)
                archive = {'commit': 'c' * 40, 'manifestSha256': 'd' * 64}
                local = LocalStore(root); previous = local.read('heads/remote-archive.json')
                local.compare_and_swap('remote-archive', previous, archive)
                return {'archive': archive, 'receipt': {'phase': phase, 'sessionId': current['sessionId'],
                    'appRevision': current['appRevision'], 'role': 'collector',
                    'contractSha256': digest(self.current), 'result': result}}
            frozen_repo = root / 'exact-k-repo'
            (frozen_repo / 'contracts').mkdir(parents=True)
            (frozen_repo / 'contracts/market.json').write_bytes(canonical(self.current))
            runtime = SimpleNamespace(REPO=frozen_repo, utcnow=lambda: AT,
                require_lease=collect.session_runtime.require_lease, checkpoint=checkpoint)
            before = copy.deepcopy(state.read('heads/cloud-lease.json'))
            with patch.dict(os.environ, env, clear=True), \
                 patch.object(seed, 'validate_seed', return_value=checked):
                one = seed.seed_before_collection(frozen_repo, root, state, session, self.current, runtime)
                two = seed.seed_before_collection(frozen_repo, root, state, session, self.current, runtime)
                self.assertEqual(one, two)
                self.assertEqual(state.read('heads/cloud-lease.json'), before)
                self.assertEqual(len(calls), 2)
                self.assertEqual(one['contractSha256'], digest(self.current))
                self.assertFalse(one['coverageCredit']); self.assertFalse(one['semanticAdmission'])
                for key, raw in checked['files'].items(): self.assertEqual((state.root / key).read_bytes(), raw)
                for key in ('heads/latest-run.json', 'heads/dailySnapshot.json', 'heads/production.json'):
                    self.assertIsNone(state.read(key))
                runtime.checkpoint = lambda *_: {}
                with self.assertRaises(ValueError):
                    seed.seed_before_collection(frozen_repo, root, state, session, self.current, runtime)
                runtime.checkpoint = checkpoint
                lease = state.read('heads/cloud-lease.json')
                state.compare_and_swap('cloud-lease', lease, {**lease, 'releasedAt': AT})
                with patch.object(state, 'write_once', side_effect=AssertionError('denied before import')):
                    with self.assertRaises(ValueError):
                        seed.seed_before_collection(frozen_repo, root, state, session, self.current, runtime)

    def test_missing_corrupt_or_foreign_payload_pin_rejected(self):
        manifest = json.loads(seed._payload(ROOT, seed.PACKAGE))
        entry = manifest["files"][0]
        for delta in ({"sha256": "0"*64}, {"bytes": True}, {"path": "contracts/market.json"},
                      {"path": seed.PACKAGE["path"].rsplit("/",1)[0]+"/../escape"}):
            with self.subTest(delta=delta), self.assertRaises((ValueError, FileNotFoundError)):
                seed._payload(ROOT, {**{k:entry[k] for k in ("path","sha256","bytes")}, **delta})
        overlay = Committed(); overlay.files.pop(three.AUTHORITY["proof"]["key"])
        with self.assertRaises((KeyError, ValueError)): three._proof(self.original, overlay)
        overlay = Committed(); overlay.files[three.AUTHORITY["proof"]["key"]] = b"{}"
        with self.assertRaises((AssertionError, ValueError)): three._proof(self.original, overlay)

if __name__ == "__main__": unittest.main()
