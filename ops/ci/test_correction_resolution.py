"""Focused offline tests for the bounded current-remediation evaluator."""
import base64
import hashlib
import json
import sys
import tempfile
import unittest
import zipfile
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'ops/evaluation'))

import correction_resolution as evaluator


class CorrectionResolutionTests(unittest.TestCase):
    def test_pinned_mapping_is_exactly_five_and_historical(self):
        design, mapping, pins = evaluator.baseline(ROOT)
        self.assertEqual(len(mapping), 5)
        self.assertEqual(len({item['auditRecordId'] for item in mapping}), 5)
        self.assertEqual(pins['claimAudit']['sha256'],
                         '7aa72d2b75a39b10b17f557bd605fd7e5a2bfeef2d0f8f48a7bed302d5e74f76')
        self.assertEqual(design['baseline']['inventoryCount'], 177)

    def test_offline_observation_stays_unmeasured_and_preserves_history(self):
        result = evaluator.observation(ROOT, evaluated_at='2026-10-24T00:00:00Z')
        measure = result['measure']
        self.assertEqual(measure['status'], 'unmeasured')
        self.assertIsNone(measure['numerator'])
        self.assertEqual((measure['denominator'], measure['verifiedResolvedCount'],
                          measure['verifiedUnresolvedCount'], measure['unmeasuredCount']), (5, 0, 0, 5))
        self.assertTrue(result['historicalBenchmark']['immutable'])
        self.assertFalse(result['historicalBenchmark']['currentPrecision'])
        self.assertEqual(len(measure['records']), 5)

    def test_partial_states_keep_fixed_denominator_and_null_when_all_unknown(self):
        self.assertEqual(evaluator.measure_states(['unmeasured'] * 5), {
            'status': 'unmeasured', 'numerator': None, 'denominator': 5,
            'verifiedResolvedCount': 0, 'verifiedUnresolvedCount': 0, 'unmeasuredCount': 5,
        })
        self.assertEqual(evaluator.measure_states(['resolved', 'unresolved', 'unmeasured',
                                                    'unmeasured', 'unmeasured']), {
            'status': 'fail', 'numerator': 1, 'denominator': 5,
            'verifiedResolvedCount': 1, 'verifiedUnresolvedCount': 1, 'unmeasuredCount': 3,
        })
        self.assertEqual(evaluator.measure_states(['resolved'] * 5)['status'], 'pass')

    def test_old_global_policy_is_unmeasured_until_current_collection_matches(self):
        head = {'runId': 'current-run'}
        context = {'policySha256': 'b' * 64}
        evaluator._require_current_correction_policy(
            {'runId': 'current-run', 'policySha256': 'b' * 64}, head, context)
        with self.assertRaisesRegex(evaluator.Unavailable, 'does not match the published market policy'):
            evaluator._require_current_correction_policy(
                {'runId': 'current-run', 'policySha256': 'a' * 64}, head, context)
        with self.assertRaisesRegex(ValueError, 'head/run differs'):
            evaluator._require_current_correction_policy(
                {'runId': 'other-run', 'policySha256': 'b' * 64}, head, context)

    def test_publisher_join_requires_checkpoint_and_authenticated_artifact(self):
        release = 'a' * 64
        checkpoint_result = {'githubRunId': '123', 'githubEventName': 'workflow_dispatch',
                             'appRevision': 'b' * 40, 'activated': True,
                             'publication': {'published': True, 'releaseId': release}}
        manifest = {'files': []}
        manifest_sha = evaluator.digest(manifest)
        result = {**checkpoint_result, 'archive': {'commit': 'd' * 40,
                  'manifestSha256': manifest_sha, 'ref': 'refs/archive/market-evidence'}}
        checkpoint = {'sessionId': 'github-publisher-123-1', 'phase': 'finish',
                      'appRevision': 'b' * 40, 'contractSha256': 'c' * 64,
                      'result': checkpoint_result}
        with tempfile.TemporaryDirectory() as directory:
            state_root = Path(directory)
            (state_root / 'heads').mkdir()
            session_dir = state_root / 'cloud/sessions/session-hash'
            session_dir.mkdir(parents=True)
            (state_root / 'heads/cloud-governance.json').write_text(json.dumps({'sessionId': checkpoint['sessionId']}))
            (session_dir / 'checkpoint.json').write_text(json.dumps(checkpoint))
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
                archive.writestr('smp-publish-receipt.json', json.dumps(result))
            payload = zip_buffer.getvalue()

            class FakeAuthority:
                def _api(self, path, binary=False):
                    if path == 'actions/runs/123':
                        return {'id': 123, 'repository': {'full_name': evaluator.PROJECT, 'private': True},
                                'path': '.github/workflows/subscription-publisher.yml', 'status': 'completed',
                                'conclusion': 'success', 'head_branch': 'main', 'head_sha': 'b' * 40,
                                'event': 'workflow_dispatch', 'run_attempt': 1}
                    if path == 'actions/runs/123/artifacts':
                        return {'artifacts': [{'id': 456, 'name': 'daily-publication-receipt', 'expired': False,
                                               'workflow_run': {'id': 123},
                                               'digest': 'sha256:' + evaluator.hashlib.sha256(payload).hexdigest()}]}
                    if path == 'actions/artifacts/456/zip' and binary:
                        return payload
                    raise AssertionError(path)

            fake_state = type('State', (), {'root': state_root,
                                             'read': lambda self, key: json.loads((state_root / key).read_text())})()
            class FakeArchive:
                remote_ref = 'refs/archive/market-evidence'

                def is_ancestor(self, ancestor, descendant):
                    return ancestor == 'd' * 40 and descendant == 'e' * 40

                def manifest_at(self, commit):
                    if commit != 'd' * 40:
                        raise AssertionError(commit)
                    return manifest

            evidence = evaluator._authenticate_publisher(fake_state, {
                'releaseId': release, 'appRevision': 'b' * 40, 'contractSha256': 'c' * 64,
            }, FakeAuthority(), FakeArchive(), 'e' * 40)
            self.assertEqual(evidence['releaseId'], release)
            self.assertEqual(evidence['artifactId'], 456)

    def test_nested_review_acceptance_is_domain_data(self):
        # The evaluator does not recursively reject legitimate review result values.
        review = {'result': 'accepted', 'checks': ['claim matches retained source']}
        self.assertEqual(review['result'], 'accepted')

    def test_cached_admission_without_original_accepted_attempt_is_rejected(self):
        group = {'id': 'FC-test', 'sources': [{'id': 'S-test'}]}
        policy = 'a' * 64
        admission_ref = {'key': 'objects/admission', 'sha256': 'b' * 64, 'bytes': 10}
        review_ref = {'key': 'objects/review', 'sha256': 'c' * 64, 'bytes': 10}
        admission = {'groupId': group['id'], 'candidateSha256': evaluator.digest(group),
                     'evidenceSetSha256': evaluator.digest(group['sources']), 'policySha256': policy,
                     'admittedAt': '2026-10-24T00:00:05Z', 'review': review_ref}
        clock = {'corrections': {'admitted': [{'groupId': group['id'], 'admission': admission_ref}],
                                 'attempts': []}}

        class State:
            root = Path('/virtual')

            def get(self, reference):
                return json.dumps(admission if reference == admission_ref else {}).encode()

            def read(self, key):
                return None

        # This reproduces a cached-index collector receipt: it lists an
        # admission but has no model-review attempt that created it.
        with tempfile.TemporaryDirectory() as directory:
            state = State()
            state.root = Path(directory)
            (state.root / 'ci/collection-runs').mkdir(parents=True)
            (state.root / 'ci/collection-runs/123-1.json').write_text(json.dumps(clock))
            with self.assertRaisesRegex(ValueError, 'original authenticated accepted review attempt'):
                evaluator._original_attempt_for_admission(state, group, policy, admission_ref)

    def test_original_admission_requires_matching_accepted_attempt_and_reservation(self):
        group = {'id': 'FC-test', 'sources': [{'id': 'S-test'}]}
        policy = 'a' * 64
        review_ref = {'key': 'objects/review', 'sha256': 'c' * 64, 'bytes': 10}
        admission_ref = {'key': 'objects/admission', 'sha256': 'b' * 64, 'bytes': 10}
        admission = {'groupId': group['id'], 'candidateSha256': evaluator.digest(group),
                     'evidenceSetSha256': evaluator.digest(group['sources']), 'policySha256': policy,
                     'admittedAt': '2026-10-24T00:00:05Z', 'review': review_ref}
        started, completed = '2026-10-24T00:00:00Z', '2026-10-24T00:00:10Z'
        attempt = {'groupId': group['id'], 'candidateSha256': evaluator.digest(group),
                   'evidenceSetSha256': evaluator.digest(group['sources']), 'policySha256': policy,
                   'startedAt': started, 'completedAt': completed, 'review': review_ref,
                   'outcome': 'accepted', 'error': None}
        attempt_ref = {'key': 'objects/attempt', 'sha256': 'd' * 64, 'bytes': 10}
        index_key = 'correction-attempts/' + attempt_ref['sha256'] + '.json'
        reservation_key = ('correction-document-reservations/2026-10-24/'
                           + evaluator.digest({'group': group, 'policy': policy}) + '.json')
        reservation = {'groupId': group['id'], 'candidateSha256': evaluator.digest(group), 'reservedAt': started}
        clock = {'corrections': {'admitted': [{'groupId': group['id'], 'admission': admission_ref}],
                                 'attempts': [attempt_ref]}}

        class State:
            root = Path('/virtual')

            def get(self, reference):
                if reference == admission_ref:
                    return json.dumps(admission).encode()
                if reference == attempt_ref:
                    return json.dumps(attempt).encode()
                return b'{}'

            def read(self, key):
                if key == index_key:
                    return attempt_ref
                if key == reservation_key:
                    return reservation
                return None

        with tempfile.TemporaryDirectory() as directory:
            state = State()
            state.root = Path(directory)
            runs = state.root / 'ci/collection-runs'
            runs.mkdir(parents=True)
            (runs / '123-1.json').write_text(json.dumps(clock))
            matched = evaluator._original_attempt_for_admission(state, group, policy, admission_ref)
            self.assertEqual(matched['attempt'], attempt)
            self.assertEqual(matched['reservationKey'], reservation_key)

    def test_disabled_export_is_unresolved_only_with_verified_rollback_context(self):
        original = {'id': 'EV-test', 'supplierId': 'vendor', 'type': 'funding', 'rung': 'growth'}
        proposed = {'id': 'EV-test', 'supplierId': 'vendor', 'type': 'funding', 'rung': 'growth',
                    'date': '2026-10-24'}
        target = {'targetId': 'event:EV-test', 'operation': 'replace', 'original': original,
                  'originalSha256': evaluator.digest(original), 'proposedValue': proposed}
        mapping = [{'auditRecordId': 'event:EV-test', 'groupId': 'FC-test',
                    'targetId': 'event:EV-test', 'originalSha256': evaluator.digest(original),
                    'operation': 'replace', 'requiredProposedSha256': evaluator.digest(proposed)}]
        context = {'requests': {'groups': [{'id': 'FC-test', 'targets': [target]}]}}
        disabled = {'schemaVersion': 1, 'enabled': False, 'policySha256': None,
                    'checkedAt': None, 'groups': []}
        frozen = {'event:EV-test': original}
        self.assertEqual(evaluator._effective_mapped_states(mapping, context, disabled, None, frozen), {
            'event:EV-test': ('unmeasured', 'ORIGINAL_EFFECTIVE_STATE_WITHOUT_ROLLBACK_PROOF')})
        self.assertEqual(evaluator._effective_mapped_states(mapping, context, disabled,
                                                            {'verified': True}, frozen), {
            'event:EV-test': ('unresolved', 'VERIFIED_ROLLBACK_RESTORED_ORIGINAL')})

    def test_rollback_requires_restored_head_and_parent_attempt(self):
        restored = 'a' * 64
        failed_manifest = {'releaseId': 'b' * 64, 'parentReleaseId': restored,
                           'createdAt': '2026-10-24T01:00:00Z', 'artifact': {'sha256': 'c' * 64}}
        failed_manifest['releaseId'] = evaluator.digest({k: v for k, v in failed_manifest.items()
                                                          if k != 'releaseId'})
        failed_id = failed_manifest['releaseId']

        class State:
            def __init__(self, root):
                self.root = root

            def read(self, key):
                return {'release-attempts/' + failed_id + '.json': failed_manifest,
                        'deployment-attempts/' + failed_id + '.json':
                            {'deploymentId': 'https://failed-release.vercel.app'}}.get(key)

        with tempfile.TemporaryDirectory() as directory:
            state = State(Path(directory))
            events = state.root / 'rollback-events'
            events.mkdir()
            (events / (failed_id + '.json')).write_text(json.dumps({
                'failedReleaseId': failed_id, 'restoredReleaseId': restored}))
            matched = evaluator._verified_rollback(state, {'releaseId': restored})
            self.assertEqual(matched['failedReleaseId'], failed_id)
            self.assertIsNone(evaluator._verified_rollback(state, {'releaseId': 'd' * 64}))

    def test_vm_github_bridge_forwards_only_gh_argv_without_shell_or_credentials(self):
        command = ['gh', 'api', 'repos/jessepike/sec-market/actions/runs/123']
        with patch.object(evaluator.subprocess, 'run') as run:
            evaluator._orb_macos_gh_runner(command, capture_output=True, timeout=60)
        run.assert_called_once_with(['mac', *command], capture_output=True, timeout=60)
        with self.assertRaisesRegex(ValueError, 'Only existing gh CLI read calls'):
            evaluator._orb_macos_gh_runner(['sh', '-c', 'echo unsafe'])

    def test_extracted_archive_must_match_authenticated_current_ref_and_all_file_pins(self):
        commit, tree_sha = 'a' * 40, 'b' * 40
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = root / 'state'
            state.mkdir()
            body = b'{"release":"retained"}\n'
            (state / 'receipt.json').write_bytes(body)
            manifest = {'schemaVersion': 1, 'files': [{'key': 'state/receipt.json',
                        'sha256': evaluator.digest(body), 'bytes': len(body)}]}
            manifest_raw = evaluator.canonical(manifest)
            blob_sha = hashlib.sha1(b'blob ' + str(len(manifest_raw)).encode() + b'\0' + manifest_raw).hexdigest()
            (root / 'archive-manifest.json').write_bytes(manifest_raw)

            class FakeAuthority:
                def _api(self, path, binary=False):
                    if path == 'git/ref/archive/market-evidence':
                        return {'ref': 'refs/archive/market-evidence',
                                'object': {'sha': commit, 'type': 'commit'}}
                    if path == 'git/commits/' + commit:
                        return {'tree': {'sha': tree_sha}}
                    if path == 'git/trees/' + tree_sha:
                        return {'truncated': False, 'tree': [{'path': 'archive-manifest.json',
                                'type': 'blob', 'sha': blob_sha, 'size': len(manifest_raw)}]}
                    if path == 'git/blobs/' + blob_sha:
                        return {'encoding': 'base64', 'size': len(manifest_raw),
                                'content': base64.b64encode(manifest_raw).decode()}
                    raise AssertionError(path)

            archive = evaluator.AuthenticatedArchive(root, FakeAuthority())
            self.assertEqual(archive.commit, commit)
            archive.verify_unchanged()
            (state / 'receipt.json').write_bytes(b'{"release":"tampered"}\n')
            with self.assertRaisesRegex(ValueError, 'Remote content address differs|Remote archive integrity mismatch'):
                archive.verify_unchanged()


if __name__ == '__main__':
    unittest.main()
