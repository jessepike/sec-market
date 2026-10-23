"""Synthetic archive/build/release mechanics; no real admissions or publication."""
import copy
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'web/scripts/pipeline'))
import test_correction_admission as fixtures
from contracts import digest
from gate import prepare_corrections
from publication import verify_correction_publication, verify_acknowledgement, publish, recover_publication
from release import preflight_corrections


class CorrectionReleaseTests(unittest.TestCase):
    def fixture(self):
        f = fixtures.CorrectionAdmissionTests()
        f.setUp()
        self.addCleanup(f.doCleanups)
        (f.repo / 'web/src/data/generated').mkdir(parents=True, exist_ok=True)
        return f

    def head(self, f, outcome):
        value = {'runId': 'fixture-run', 'checkedAt': f.now, **outcome}
        f.store.compare_and_swap('correction-collection', None, {'runId': 'fixture-run', 'outcome': f.store.put(value)})

    def proof(self, **changes):
        return {'schemaVersion': 1, 'fileSha256': 'a' * 64, 'policySha256': 'b' * 64,
                'groupIds': ['example'], 'targetIds': ['event:EV-example'],
                'newGroupIds': ['example'], 'publicationDate': '2026-10-23', **changes}

    def test_gate_replays_archive_and_binds_exact_full_public_projection(self):
        f = self.fixture()
        outcome = f.process()
        self.head(f, outcome)
        before_calls = f.agent.calls
        seal = prepare_corrections(f.repo, f.store, f.market, {'runId': 'fixture-run'}, now=f.now)
        target = f.repo / 'web/src/data/generated/factualCorrections.json'
        data = json.loads(target.read_bytes())
        self.assertEqual(seal['fileSha256'], digest(target.read_bytes()))
        self.assertEqual(seal['groupIds'], [f.group['id']])
        self.assertEqual(seal['newGroupIds'], [f.group['id']])
        self.assertEqual(len(seal['targetIds']), len(f.group['targets']))
        self.assertEqual(data['groups'][0]['targets'], f.group['targets'])
        self.assertEqual(f.agent.calls, before_calls)
        self.assertEqual(json.loads(target.with_suffix('.seal.json').read_bytes()), seal)

    def test_pending_or_missing_current_collection_cannot_build_enabled_projection(self):
        f = self.fixture()
        with self.assertRaisesRegex(ValueError, 'CURRENT_CORRECTION_COLLECTION_REQUIRED'):
            prepare_corrections(f.repo, f.store, f.market, {'runId': 'fixture-run'}, now=f.now)
        self.head(f, {'policySha256': f.policy, 'admitted': [], 'pending': [{'groupId': f.group['id'], 'reason': 'held'}]})
        with self.assertRaisesRegex(ValueError, 'pending'):
            prepare_corrections(f.repo, f.store, f.market, {'runId': 'fixture-run'}, now=f.now)
        self.assertFalse((f.repo / 'web/src/data/generated/factualCorrections.json').exists())

    def test_wrong_collection_run_or_policy_fails_before_build(self):
        f = self.fixture()
        self.head(f, {**f.process(), 'policySha256': '0' * 64})
        for run in ['fixture-run', 'different-run']:
            with self.subTest(run=run), self.assertRaises(ValueError):
                prepare_corrections(f.repo, f.store, f.market, {'runId': run}, now=f.now)

    def test_later_gate_retains_original_publication_date_and_original_records(self):
        f = self.fixture()
        self.head(f, f.process())
        raw_before = copy.deepcopy(f.raw)
        prepare_corrections(f.repo, f.store, f.market, {'runId': 'fixture-run'}, now=f.now)
        previous = json.loads((f.repo / 'web/src/data/generated/factualCorrections.json').read_bytes())
        seal = prepare_corrections(f.repo, f.store, f.market, {'runId': 'fixture-run'}, previous_bundle=previous, now='2026-11-23T12:00:00Z')
        after = json.loads((f.repo / 'web/src/data/generated/factualCorrections.json').read_bytes())
        self.assertEqual(after['groups'], previous['groups'])
        self.assertEqual(seal['newGroupIds'], [])
        self.assertEqual(f.raw, raw_before)
        self.assertEqual(f.agent.calls, 1)

    def test_first_publication_refuses_utc_rollover_but_history_does_not_expire(self):
        verify_correction_publication(self.proof(), '2026-10-23T23:59:59Z')
        with self.assertRaisesRegex(ValueError, 'ROLLED_OVER'):
            verify_correction_publication(self.proof(), '2026-10-24T00:00:00Z')
        verify_correction_publication(self.proof(newGroupIds=[]), '2026-11-24T00:00:00Z')
        for change in [{'fileSha256': 'bad'}, {'groupIds': ['example', 'example']}, {'targetIds': []}, {'newGroupIds': ['forged']}]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                verify_correction_publication(self.proof(**change), '2026-10-23T23:59:59Z')

    def test_detached_acknowledgement_must_bind_same_corrections(self):
        manifest = {'appRevision': 'a', 'releaseId': 'r', 'snapshot': {'sha256': 's'},
                    'artifact': {'sha256': 't'}, 'contractSha256': 'c', 'factualCorrections': self.proof()}
        receipt = {'ready': True, 'appRevision': 'a', 'dataReleaseId': 'r', 'snapshotSha256': 's',
                   'artifactSha256': 't', 'contractSha256': 'c', 'factualCorrections': self.proof()}
        verify_acknowledgement(manifest, receipt)
        with self.assertRaisesRegex(ValueError, 'correction projection'):
            verify_acknowledgement(manifest, {**receipt, 'factualCorrections': self.proof(fileSha256='f' * 64)})

    def test_expired_first_publication_never_reaches_stage_or_budget(self):
        f = self.fixture()
        adapter = unittest.mock.Mock()
        with patch('contracts.utcnow', return_value='2026-10-24T00:00:00Z'), self.assertRaisesRegex(ValueError, 'ROLLED_OVER'):
            publish(f.store, {'publication': {'enabled': True}}, {'factualCorrections': self.proof()}, adapter)
        adapter.stage.assert_not_called()
        self.assertIsNone(f.store.read('heads/publication-budget-2026-10-24.json'))

    def test_pending_preflight_preserves_scarce_gate_allowance(self):
        f = self.fixture()
        self.head(f, {'policySha256': f.policy, 'admitted': [], 'pending': [{'groupId': f.group['id'], 'reason': 'held'}]})
        with self.assertRaisesRegex(ValueError, 'pending'):
            preflight_corrections(f.repo, f.store, f.market, 'fixture-run', None, f.now)
        self.assertIsNone(f.store.read('heads/gate-budget-2026-10-23.json'))
        self.assertIsNone(f.store.read('heads/publication-budget-2026-10-23.json'))

    def test_crashed_promotion_crossing_midnight_rolls_back_instead_of_acknowledging(self):
        f = self.fixture()
        previous = {'releaseId': '0' * 64, 'sequence': 1, 'deploymentId': 'old-deployment'}
        manifest = {'sequence': 2, 'parentReleaseId': previous['releaseId'], 'appRevision': 'a' * 40,
                    'snapshot': {'sha256': 's'}, 'artifact': {'sha256': 't'}, 'contractSha256': 'c',
                    'factualCorrections': self.proof()}
        release_id = digest(manifest)
        manifest['releaseId'] = release_id
        f.store.compare_and_swap('production', None, previous)
        f.store.write_once('release-attempts/' + release_id + '.json', manifest)
        f.store.write_once('deployment-attempts/' + release_id + '.json', {'deploymentId': 'new-deployment'})
        adapter = unittest.mock.Mock()
        adapter.probe_production.side_effect = [
            {'ready': True, 'appRevision': 'a' * 40, 'dataReleaseId': release_id, 'snapshotSha256': 's',
             'artifactSha256': 't', 'contractSha256': 'c', 'factualCorrections': self.proof()},
            {'ready': True, 'dataReleaseId': previous['releaseId']},
        ]
        with patch('contracts.utcnow', return_value='2026-10-24T00:00:01Z'), self.assertRaisesRegex(ValueError, 'ROLLED_OVER'):
            recover_publication(f.store, adapter)
        adapter.rollback.assert_called_once_with('old-deployment')
        self.assertEqual(f.store.read('heads/production.json'), previous)
        self.assertIsNone(f.store.read('releases/' + release_id + '.json'))
