"""Fictional completion fixtures exercise a dormant seed; no actual activation."""
import ast
import copy
import json
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'web/scripts/pipeline'))
sys.path.insert(0, str(ROOT / 'ops/ci'))

from contracts import canonical, digest, instant
import html_qualification_seed as seed
from storage import LocalStore
import test_source_qualification_origin as origin_fixtures

LATER = origin_fixtures.LATER


class HtmlQualificationSeedTests(unittest.TestCase):
    def setUp(self):
        # Reuse the clearly fictional, source-bound complete proof collaborator.
        # The real origin resolver/transition/inventory/authority checks still run.
        self.fixture = origin_fixtures.QualificationOriginTests('test_no_origin_is_dormant_and_does_not_read_transition')
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.store = self.fixture.store
        self.original = self.fixture.original
        self.contract = self.fixture.activate()
        self.authority = self.fixture.authorities[-1]
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / 'repo'
        self.runtime_root = Path(self.temp.name) / 'runtime'
        self.bundle = self.repo / 'contracts/html-qualification-seeds/fictional'
        self.bundle.mkdir(parents=True)
        self.packages = []
        self.addCleanup(patch.stopall)
        patch('html_qualification_seed.SEED_PACKAGES', self.packages).start()
        sid = next(s['id'] for s in self.original['sources'] if s['id'] not in seed.SOURCE_IDS)
        item = {'sourceId': sid, 'items': ['https://example.invalid/old-one', 'https://example.invalid/old-two']}
        manifest = self.store.put(item)
        fact = self.store.put({'factId': 'fictional-old-fact', 'retrievedAt': '2026-10-19T00:00:00Z'})
        binding = {'url': item['items'][0], 'originalTime': '2026-10-19T00:00:00Z'}
        receipt = {'sourceId': sid, 'retainedInventoryManifest': manifest,
                   'retainedAuditBindings': [binding], 'validatedFacts': [fact]}
        old_coverage = {'contractSha256': digest(self.original), 'receipts': [receipt],
                        'runId': 'fictional-original-run', 'inventorySha256': '1' * 64,
                        'requiredTasks': 1, 'successfulTasks': 0, 'supplierCount': len(self.original['suppliers']),
                        'tasks': [{'fictional': True}], 'checkedAt': '2026-10-19T00:00:00Z'}
        coverage = self.store.put(old_coverage)
        queue = [{'reason': 'FICTIONAL_HELD', 'originalTime': '2026-10-19T00:00:00Z'}]
        snapshot = {'contractSha256': digest(self.original), 'reviewQueue': queue,
                    'runId': old_coverage['runId'],
                    'coverage': {k: v for k, v in old_coverage.items() if k != 'receipts'},
                    'checkedAt': '2026-10-19T00:00:00Z'}
        snapshot['snapshotSha256'] = digest(snapshot)
        protected = sorted([self.store.put({'fictionalQuarantine': i}) for i in range(4)], key=digest)
        summary = {'inventoryPairs': 2, 'inventoryPairsSha256': digest(sorted((sid, url) for url in item['items'])),
                   'retainedInventoryPairs': 2, 'retainedInventoryPairsSha256': digest(sorted((sid, url) for url in item['items'])),
                   'retainedBindings': 1, 'retainedBindingsSha256': digest([binding]),
                   'factReferences': 1, 'factReferencesSha256': digest([fact]),
                   'reviewQueueEntries': 1, 'reviewQueueSha256': digest(queue),
                   'snapshotSha256': snapshot['snapshotSha256'], 'protectedReferencesSha256': digest(protected)}
        preservation = {'coverage': coverage, 'snapshot': self.store.put(snapshot),
                        'protectedReferences': protected, 'summary': summary}
        h = digest(self.contract)
        files = {}
        for source in self.contract['sources']:
            if source['id'] in seed.SOURCE_IDS:
                ref = source['qualificationOrigin']['inventoryManifest']
                files[ref['key']] = self.store.get(ref)
        ref = self.authority['transition']
        files[ref['key']] = self.store.get(ref)
        ref = preservation['snapshot']
        files[ref['key']] = self.store.get(ref)
        files['contracts/' + h + '.json'] = canonical(self.contract)
        pointer = 'source-qualification-transitions/' + h + '.json'
        files[pointer] = canonical(self.authority['transition'])
        self.manifest = {'schemaVersion': 1, 'kind': seed.KIND, 'activatedContractSha256': h,
                         'transition': self.authority['transition'], 'proofArchive': {'commit': 'd' * 40, 'manifestSha256': 'e' * 64},
                         'preservation': preservation, 'files': []}
        for i, (key, body) in enumerate(sorted(files.items())):
            path = self.bundle / (str(i) + '.json')
            path.write_bytes(body)
            self.manifest['files'].append({'key': key, 'path': path.relative_to(self.repo).as_posix(),
                                           'sha256': digest(body), 'bytes': len(body)})
            old = self.store.root / key
            if old.exists():
                old.unlink()
        self.write_manifest()
        self.session = {'role': 'collector', 'executionMode': 'github_subscription',
                        'sessionId': 'github-123-1', 'appRevision': 'a' * 40,
                        'startedAt': LATER, 'restored': {'commit': 'b' * 40}}
        runtime = LocalStore(self.runtime_root)
        runtime.write_once('session.json', self.session)
        self.store.compare_and_swap('cloud-lease', None, {'sessionId': 'github-123-1', 'expiresAt': '2030-01-01T00:00:00Z'})
        event = Path(self.temp.name) / 'event.json'
        event.write_bytes(canonical({'repository': {'full_name': 'jessepike/sec-market', 'private': True},
                                    'inputs': {'source_probe': 'false'}}))
        self.env = {'GITHUB_ACTIONS': 'true', 'GITHUB_REPOSITORY': 'jessepike/sec-market',
                    'GITHUB_REF': 'refs/heads/main', 'GITHUB_EVENT_NAME': 'workflow_dispatch',
                    'GITHUB_SHA': 'a' * 40, 'GITHUB_RUN_ID': '123', 'GITHUB_RUN_ATTEMPT': '1',
                    'GITHUB_EVENT_PATH': str(event)}
        patch.dict(os.environ, self.env, clear=True).start()
        self.checkpoints = []
        def lease(store, session, at):
            value = store.read('heads/cloud-lease.json')
            if not value or value.get('releasedAt') or value.get('sessionId') != session['sessionId'] or instant(value['expiresAt']) <= instant(at):
                raise ValueError('fictional lease denied')
        def checkpoint(root, store, session, phase, result):
            self.checkpoints.append((phase, result))
            self.assertTrue(all((store.root / row['key']).exists() for row in self.manifest['files']))
            archive = {'commit': 'f' * 40, 'parentCommit': 'b' * 40,
                       'manifestSha256': '1' * 64, 'files': 7, 'ref': 'refs/archive/market-evidence'}
            local = LocalStore(root)
            local.compare_and_swap('remote-archive', local.read('heads/remote-archive.json'), archive)
            return {'archive': archive, 'receipt': {'phase': phase, 'result': result, 'contractSha256': h,
                'sessionId': session['sessionId'], 'appRevision': session['appRevision'], 'role': 'collector'}}
        self.runtime = SimpleNamespace(utcnow=lambda: LATER, require_lease=lease, checkpoint=checkpoint)

    def write_manifest(self):
        path = self.bundle / 'seed.json'
        raw = canonical(self.manifest)
        path.write_bytes(raw)
        self.packages[:] = [{'contractSha256': digest(self.contract),
                            'manifest': {'path': path.relative_to(self.repo).as_posix(),
                                         'sha256': digest(raw), 'bytes': len(raw)}}]

    def validate(self):
        return seed.validate_seed(self.repo, self.store, self.contract, LATER)

    def execute(self):
        return seed.seed_before_collection(self.repo, self.runtime_root, self.store, self.session,
                                           self.contract, self.runtime)

    def test_current_candidate_contract_is_noop_without_io(self):
        denied = SimpleNamespace(__getattr__=lambda *_: self.fail('unexpected access'))
        with patch('html_qualification_seed._payload', side_effect=AssertionError('no read')):
            self.assertIsNone(seed.validate_seed(None, denied, self.original, LATER))
            self.assertIsNone(seed.seed_before_collection(None, None, denied, {}, self.original, denied))

    def test_active_contract_needs_both_positive_registries(self):
        with patch('html_qualification_seed.SEED_PACKAGES', ()):
            self.assertRaisesRegex(ValueError, 'NOT_TRUSTED', self.validate)
        with patch('source_qualification_origin.ACTIVATION_AUTHORITIES', ()):
            self.assertRaisesRegex(ValueError, 'NOT_EXTERNALLY_AUTHENTICATED', self.validate)

    def test_overlay_replays_all_origins_and_preserves_old_evidence_without_writes(self):
        before = sorted(p.relative_to(self.store.root).as_posix() for p in self.store.root.rglob('*') if p.is_file())
        with patch.object(self.store, 'write_once', side_effect=AssertionError('preflight wrote')):
            checked = self.validate()
        self.assertEqual(len(checked['files']), 7)
        self.assertEqual(set(checked['qualificationInventory']), set(seed.SOURCE_IDS))
        self.assertEqual(checked['preservation']['inventoryPairs'], 2)
        self.assertEqual(before, sorted(p.relative_to(self.store.root).as_posix() for p in self.store.root.rglob('*') if p.is_file()))

    def test_missing_extra_duplicate_payload_and_type_drift_reject(self):
        for change in ('missing', 'extra', 'duplicate', 'boolean'):
            with self.subTest(change=change):
                old = copy.deepcopy(self.manifest)
                if change == 'missing': self.manifest['files'].pop()
                if change == 'extra': self.manifest['files'][0]['key'] = 'heads/budget-2026-10-24.json'
                if change == 'duplicate': self.manifest['files'].append(copy.deepcopy(self.manifest['files'][0]))
                if change == 'boolean': self.manifest['schemaVersion'] = True
                self.write_manifest()
                self.assertRaises(ValueError, self.validate)
                self.manifest = old
                self.write_manifest()

    def test_corrupted_raw_payload_and_noncanonical_payload_reject(self):
        path = self.repo / self.manifest['files'][0]['path']
        body = path.read_bytes()
        path.write_bytes(body + b' ')
        self.assertRaisesRegex(ValueError, 'INTEGRITY_DIFFERS', self.validate)
        self.manifest['files'][0].update(sha256=digest(body + b' '), bytes=len(body) + 1)
        self.write_manifest()
        self.assertRaisesRegex(ValueError, 'NOT_CANONICAL', self.validate)

    def test_unsafe_payload_path_and_symlink_reject(self):
        self.manifest['files'][0]['path'] = 'contracts/html-qualification-seeds/../escape.json'
        self.write_manifest()
        self.assertRaisesRegex(ValueError, 'PIN_INVALID', self.validate)
        self.manifest['files'][0]['path'] = 'contracts/html-qualification-seeds/link.json'
        (self.repo / self.manifest['files'][0]['path']).symlink_to(self.bundle / '0.json')
        self.write_manifest()
        self.assertRaisesRegex(ValueError, 'PATH_ESCAPES', self.validate)

    def test_wrong_proof_archive_and_preservation_counts_reject(self):
        self.manifest['proofArchive']['commit'] = '0' * 40
        self.write_manifest()
        self.assertRaisesRegex(ValueError, 'PROOF_ARCHIVE_DIFFERS', self.validate)
        self.manifest['proofArchive']['commit'] = 'd' * 40
        self.manifest['preservation']['summary']['inventoryPairs'] = 1
        self.write_manifest()
        self.assertRaisesRegex(ValueError, 'SUMMARY_DIFFERS', self.validate)

    def test_rehashed_empty_or_other_original_coverage_does_not_match_snapshot(self):
        old_ref = self.manifest['preservation']['coverage']
        for coverage in ({'contractSha256': digest(self.original), 'receipts': []},
                         {**json.loads(self.store.get(old_ref)), 'runId': 'different-original-run'}):
            self.manifest['preservation']['coverage'] = self.store.put(coverage)
            self.write_manifest()
            self.assertRaisesRegex(ValueError, 'COVERAGE_SNAPSHOT_JOIN_DIFFERS', self.validate)

    def test_missing_old_quarantine_reference_and_old_fact_bytes_reject(self):
        ref = self.manifest['preservation']['protectedReferences'][0]
        (self.store.root / ref['key']).unlink()
        self.assertRaises(FileNotFoundError, self.validate)

    def test_no_immutable_import_until_third_origin_passes(self):
        real = seed.origins.resolve_inventory_origin
        def fail_third(origin, contract, sid, store, at):
            if sid == seed.SOURCE_IDS[-1]: raise ValueError('fictional third source denied')
            return real(origin, contract, sid, store, at)
        with patch.object(seed.origins, 'resolve_inventory_origin', side_effect=fail_third), \
             patch.object(self.store, 'write_once', side_effect=AssertionError('premature import')):
            self.assertRaisesRegex(ValueError, 'third source', self.execute)

    def test_seed_ack_and_repeated_retry_are_idempotent_and_zero_credit(self):
        budget = {'fetches': 1438, 'calls': 80, 'documents': 40}
        self.store.compare_and_swap('budget-2026-10-24', None, budget)
        result = self.execute()
        self.assertFalse(result['coverageCredit'])
        self.assertFalse(result['semanticAdmission'])
        self.assertEqual(result['sourceChecksCredited'], 0)
        self.assertEqual(self.execute(), result)
        self.assertEqual([phase for phase, _ in self.checkpoints], ['qualification_seeded'] * 2)
        self.assertEqual(self.store.read('heads/budget-2026-10-24.json'), budget)

    def test_no_ack_or_ack_head_mismatch_stops_after_import(self):
        self.runtime.checkpoint = lambda *_: (_ for _ in ()).throw(RuntimeError('fictional remote failure'))
        self.assertRaisesRegex(RuntimeError, 'remote failure', self.execute)
        self.assertTrue(all((self.store.root / row['key']).exists() for row in self.manifest['files']))
        self.runtime.checkpoint = lambda *_: {'archive': {'commit': 'f' * 40, 'sha256': '1' * 64}}
        self.assertRaisesRegex(ValueError, 'REMOTE_ACK_REQUIRED', self.execute)

    def test_legacy_sha_only_and_missing_manifest_ack_reject_even_when_head_matches(self):
        original = self.runtime.checkpoint
        for change in ('legacy_sha_only', 'missing_manifest'):
            def checkpoint(*args):
                result = original(*args)
                archive = result['archive']
                manifest = archive.pop('manifestSha256')
                if change == 'legacy_sha_only':
                    archive['sha256'] = manifest
                local = LocalStore(self.runtime_root)
                local.compare_and_swap('remote-archive', local.read('heads/remote-archive.json'), archive)
                return result
            self.runtime.checkpoint = checkpoint
            with self.subTest(change=change):
                self.assertRaisesRegex(ValueError, 'REMOTE_ACK_REQUIRED', self.execute)

    def test_real_checkpoint_and_real_archive_push_acknowledgement_interface(self):
        import collect
        from archive import GitArchive
        runtime = collect.session_runtime
        self.runtime = runtime
        (self.repo / 'contracts/market.json').write_bytes(canonical(self.contract))
        mirror = Path(self.temp.name) / 'fictional-archive-mirror'
        mirror.mkdir()
        archive = GitArchive(mirror, str(Path(self.temp.name) / 'fictional-remote'))
        def fake_git(*args, **kwargs):
            return SimpleNamespace(returncode=1 if args[0] == 'diff' else 0,
                stdout=(('f' * 40).encode() if args[0] == 'rev-parse' else b''))
        # Exercise the production push/checkpoint return and ACK-head writes;
        # only the Git transport boundary is fictional and never starts Git.
        with patch.object(runtime, 'REPO', self.repo), patch.object(runtime, 'utcnow', return_value=LATER), \
             patch.object(runtime, 'archive_for', return_value=archive), \
             patch.object(archive, '_open', return_value='b' * 40), patch.object(archive, '_git', side_effect=fake_git):
            result = self.execute()
        ack = result['archive']
        self.assertEqual(set(ack), {'commit', 'parentCommit', 'manifestSha256', 'files', 'ref'})
        self.assertEqual(ack['manifestSha256'], digest(json.loads((mirror / 'archive-manifest.json').read_bytes())))
        self.assertEqual(ack, LocalStore(self.runtime_root).read('heads/remote-archive.json'))
        self.assertTrue(all((mirror / 'state' / row['key']).exists() for row in self.manifest['files']))

    def test_context_and_expired_or_profiled_lease_reject_before_import(self):
        for env in ({'GITHUB_REF': 'refs/heads/preview'}, {'GITHUB_SHA': 'c' * 40}):
            with patch.dict(os.environ, env), patch.object(self.store, 'write_once', side_effect=AssertionError('premature write')):
                self.assertRaisesRegex(ValueError, 'PRIVATE_REVIEWED_MAIN', self.execute)
        lease = self.store.read('heads/cloud-lease.json')
        self.store.compare_and_swap('cloud-lease', lease, {**lease, 'checkpointProfile': 'source_probe'})
        self.assertRaisesRegex(ValueError, 'ORDINARY_LEASE', self.execute)

    def test_expired_or_released_lease_rejects_before_import(self):
        for mutation in ({'expiresAt': '2020-01-01T00:00:00Z'}, {'releasedAt': LATER}):
            old = self.store.read('heads/cloud-lease.json')
            self.store.compare_and_swap('cloud-lease', old, {**old, **mutation})
            with patch.object(self.store, 'write_once', side_effect=AssertionError('expired write')):
                self.assertRaisesRegex(ValueError, 'lease denied', self.execute)
            self.store.compare_and_swap('cloud-lease', self.store.read('heads/cloud-lease.json'), old)

    def test_rehashed_old_snapshot_date_cannot_replace_original_seal(self):
        ref = self.manifest['preservation']['snapshot']
        row = next(row for row in self.manifest['files'] if row['key'] == ref['key'])
        path = self.repo / row['path']
        value = json.loads(path.read_bytes())
        value['checkedAt'] = LATER
        value['coverage']['checkedAt'] = LATER
        raw = canonical(value)
        row.update(key='objects/' + digest(raw), sha256=digest(raw), bytes=len(raw))
        path.write_bytes(raw)
        self.manifest['preservation']['snapshot'] = {k: row[k] for k in ('key', 'sha256', 'bytes')}
        self.manifest['files'].sort(key=lambda row: row['key'])
        self.write_manifest()
        self.assertRaisesRegex(ValueError, 'OLD_SNAPSHOT_SEAL_DIFFERS', self.validate)

    def test_existing_immutable_payload_collision_is_not_replaced(self):
        row = self.manifest['files'][0]
        self.store.write_once(row['key'], {'fictional': 'different existing bytes'})
        before = (self.store.root / row['key']).read_bytes()
        self.assertRaises(ValueError, self.validate)
        self.assertEqual((self.store.root / row['key']).read_bytes(), before)

    def test_current_collector_hook_precedes_reuse_auth_and_models(self):
        tree = ast.parse((ROOT / 'ops/ci/collect.py').read_text())
        execute = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'execute')
        calls = [(node.lineno, ast.unparse(node.func)) for node in ast.walk(execute) if isinstance(node, ast.Call)]
        line = next(line for line, name in calls if name == 'seed_before_collection')
        for name in ('reuse_scheduled_collection', 'keeper.restore', 'SubscriptionAgent', 'BoundedPipeline'):
            self.assertLess(line, next(n for n, call in calls if call == name))


if __name__ == '__main__':
    unittest.main()
