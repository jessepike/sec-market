"""Offline replay semantics, not a fresh source check or operational coverage."""
import copy
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'web/scripts/pipeline'), str(ROOT / 'ops/ci')]
from contracts import canonical, digest, plan_run
from discovery import discover, Q4_CURRENT_PROFILE, Q4_LEGACY_PROFILE
from engine import Pipeline
from retained_audit import discovery_replay_profile, original_discovery, replay_discovery
from storage import LocalStore
from test_q4_null_metadata import FIXTURES, bounded_gzip, null_row
from test_q4_press_list import AS_OF, encoded, row

FAILURES = FIXTURES / 'historical-failures'
FAILURE_PROVENANCE_SHA = 'a4f4a462bca0d50529c8e02eac8bb39a5f5fed15441822d99c858d012c8535f7'


class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.contract = json.loads((ROOT / 'contracts/market.json').read_bytes())
        self.source = next(s for s in self.contract['sources'] if s['id'] == 'jfrog:official:1')
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.store = LocalStore(self.temporary.name)
        self.socket = patch('socket.socket', side_effect=AssertionError('Offline replay forbids network'))
        self.socket.start()
        self.addCleanup(self.socket.stop)

    def synthetic(self, rows):
        raw = encoded(rows)
        observed = {'sourceId': self.source['id'], 'requestedUrl': self.source['url'],
                    'finalUrl': self.source['url'], 'status': 'fetched', 'httpStatus': 200,
                    'contentType': 'application/json; charset=utf-8', 'fetchedAt': AS_OF,
                    'observationId': digest({'fixtureBody': digest(raw)}), 'body': self.store.put(raw)}
        return observed, raw

    def manifest(self, found):
        return {'sourceId': self.source['id'], 'items': found['items'],
                'observations': [o['observationId'] for o in found['observations']],
                'itemDates': found.get('itemDates', {}), 'itemModified': found.get('itemModified', {}),
                **({'discoveryProfile': found['discoveryProfile']} if 'discoveryProfile' in found else {})}

    def test_legacy_positive_is_exact_and_new_attempt_of_old_shape_still_records_current_profile(self):
        observed, raw = self.synthetic([row()])
        request = lambda _: (observed, raw)
        old = discover(self.source, request, q4_profile=Q4_LEGACY_PROFILE)
        self.assertNotIn('discoveryProfile', old)
        self.assertTrue(old['complete'])
        self.assertEqual(replay_discovery(self.source, request, self.manifest(old), {}), old)
        current = discover(self.source, request)
        self.assertEqual(current.pop('discoveryProfile'), Q4_CURRENT_PROFILE)
        self.assertEqual(current, old)

    def test_future_positive_and_negative_replay_complete_output_and_exact_error_cause(self):
        for bad in (False, True):
            rows = [null_row()]
            if bad:
                rows[0]['UrlOverrideContentFileWorkflowId'] = 'unapproved-route'
            observed, raw = self.synthetic(rows)
            request = lambda _: (observed, raw)
            found = discover(self.source, request)
            self.assertEqual(found['complete'], not bad)
            manifest = self.manifest(found)
            receipt = {'errorCode': found.get('reason'), 'completedAt': AS_OF,
                       'discoveryComplete': found['complete'], 'itemManifest': self.store.put(manifest)}
            self.assertEqual(replay_discovery(self.source, request, manifest, receipt), found)
            self.store.write_once('observations/' + observed['observationId'] + '.json', observed)
            with patch('retained_audit.resolve_origin', return_value=receipt), \
                 patch('retained_audit.original_contract', return_value=self.contract):
                self.assertEqual(original_discovery({'origin': {}}, self.contract, self.source,
                                                    self.store, require_complete=False), found)
            if bad:
                self.assertEqual(found['reason'], 'Q4_INDEX_INCOMPLETE:Q4_LIST_NON_NULL_URL_OVERRIDE')
                stripped = {k: v for k, v in manifest.items() if k != 'discoveryProfile'}
                with self.assertRaisesRegex(ValueError, 'failure cause differs'):
                    replay_discovery(self.source, request, stripped, receipt)

    def test_unknown_malformed_and_explicit_downgrade_profiles_reject_before_request(self):
        def denied(_):
            raise AssertionError('Invalid profile must reject before any request')
        for value in (None, False, 0, [], {}, '', 'future-v3', Q4_LEGACY_PROFILE):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, 'PROFILE_INVALID'):
                replay_discovery(self.source, denied, {'discoveryProfile': value}, {})
        for value in (None, False, 0, [], {}, '', 'future-v3'):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, 'PROFILE_INVALID'):
                discover(self.source, denied, q4_profile=value)
        with self.assertRaisesRegex(ValueError, 'not valid for this source'):
            discovery_replay_profile({'kind': 'rss'}, {'discoveryProfile': Q4_CURRENT_PROFILE})

    def test_profile_is_hash_bound_and_tampering_cannot_reuse_original_reference(self):
        ref = self.store.put({'discoveryProfile': Q4_CURRENT_PROFILE})
        (self.store.root / ref['key']).write_bytes(canonical({}))
        with self.assertRaisesRegex(ValueError, 'integrity verification'):
            self.store.get(ref)

    def test_before_response_budget_or_transport_failure_keeps_incomplete_without_fabricated_cause(self):
        for profile in (Q4_LEGACY_PROFILE, Q4_CURRENT_PROFILE):
            for original in ('FETCH_BUDGET_EXHAUSTED', 'transport unavailable'):
                def failed(_):
                    raise ValueError(original)
                found = discover(self.source, failed, q4_profile=profile)
                manifest = self.manifest(found)
                receipt = {'errorCode': found['reason'], 'completedAt': AS_OF,
                           'discoveryComplete': False, 'itemManifest': self.store.put(manifest)}
                original_receipt = copy.deepcopy(receipt)
                def missing(_):
                    raise ValueError('Retained discovery observation missing')
                replay = replay_discovery(self.source, missing, manifest, receipt)
                self.assertFalse(replay['complete'])
                self.assertEqual((replay['items'], replay['observations']), ([], []))
                self.assertNotEqual(replay['reason'], receipt['errorCode'])
                self.assertEqual(receipt, original_receipt)
                with patch('retained_audit.resolve_origin', return_value=receipt), \
                     patch('retained_audit.original_contract', return_value=self.contract):
                    origin = original_discovery({'origin': {}}, self.contract, self.source,
                                                self.store, require_complete=False)
                self.assertFalse(origin['complete'])
                self.assertEqual(origin['observations'], [])

    def test_actual_old_failed_receipts_keep_original_negative_and_origin_clock(self):
        raw = (FAILURES / 'provenance.json').read_bytes()
        self.assertEqual(digest(raw), FAILURE_PROVENANCE_SHA)
        provenance = json.loads(raw)
        self.assertEqual(provenance['archive']['manifestSha256'],
                         '3cb739133b60e03d418480e53ee8c454dca616efa8d3585fde87c5eb9ac61438')
        self.assertEqual(provenance['archive']['manifestEntries'], 69873)
        entries = {e['key']: e for e in provenance['selectedManifestEntries']}
        self.assertEqual(len(entries), 4)
        for source in provenance['sources']:
            name = source['sourceId'].split(':')[0]
            saved = {}
            for kind in ('receipt', 'item-manifest'):
                pin = source[kind]
                data = (FAILURES / pin['file']).read_bytes()
                self.assertEqual((digest(data), len(data)), (pin['sha256'], pin['bytes']))
                entry = entries['state/objects/' + pin['sha256']]
                self.assertEqual((entry['sha256'], entry['bytes']), (pin['sha256'], pin['bytes']))
                saved[kind] = json.loads(data)
                self.store.write_once('objects/' + pin['sha256'], data)
            receipt, manifest = saved['receipt'], saved['item-manifest']
            self.assertEqual(json.loads(self.store.get(receipt['itemManifest'])), manifest)
            self.assertNotIn('discoveryProfile', manifest)
            self.assertFalse(receipt['discoveryComplete'])
            self.assertTrue(receipt['discoveryRecorded'])
            self.assertEqual(receipt['errorCode'], 'Q4_INDEX_INCOMPLETE:Q4_LIST_ROW_SCHEMA_INVALID')
            body = bounded_gzip((FIXTURES / (name + '.json.gz')).read_bytes())
            observation = json.loads((FIXTURES / (name + '-observation.json')).read_bytes())
            self.assertEqual(digest(body), observation['body']['sha256'])
            self.assertEqual(manifest['observations'], [observation['observationId']])
            self.store.write_once(observation['body']['key'], body)
            self.store.write_once('observations/' + observation['observationId'] + '.json', observation)
            original_source = next(s for s in self.contract['sources'] if s['id'] == source['sourceId'])
            request = lambda _: (observation, body)
            expected = {'complete': False, 'items': [], 'itemModified': {}, 'itemDates': {},
                        'observations': [observation], 'reason': receipt['errorCode']}
            self.assertEqual(replay_discovery(original_source, request, manifest, receipt), expected)
            # Only origin lookup is isolated here; manifest/body/observation,
            # literal error and original completion-clock checks execute normally.
            with patch('retained_audit.resolve_origin', return_value=receipt), \
                 patch('retained_audit.original_contract', return_value=self.contract):
                replay = original_discovery({'origin': {}}, self.contract, original_source,
                                            self.store, require_complete=False)
            self.assertEqual(replay, expected)
            self.assertEqual(replay['observations'][0]['fetchedAt'], observation['fetchedAt'])
            self.assertEqual(discover(original_source, request)['complete'], True)

    def test_engine_persists_profile_for_ordinary_success_and_failure(self):
        # Stop immediately after the real engine writes discovery's manifest.
        # This tests persistence only, without claiming downstream fact admission.
        class ManifestWritten(BaseException):
            pass
        for bad in (False, True):
            rows = [null_row()]
            if bad:
                rows[0]['UrlOverrideContentFileWorkflowId'] = 'unapproved-route'
            observed, raw = self.synthetic(rows)
            pipeline = Pipeline(self.contract, self.store, None, clock=lambda: AS_OF)
            pipeline.force_refresh, pipeline.replay = True, False
            pipeline.audit_index, pipeline.audit_compatibility = None, None
            plan = plan_run(self.contract, AS_OF)
            task = next(t for t in plan['tasks'] if t['sourceId'] == self.source['id'])
            original_put = self.store.put
            captured = []
            def capture(value):
                reference = original_put(value)
                if isinstance(value, dict) and value.get('sourceId') == self.source['id'] and 'observations' in value:
                    captured.append((value, reference))
                    raise ManifestWritten()
                return reference
            with patch.object(pipeline, '_fetch_transport', return_value=copy.deepcopy(observed)), \
                 patch.object(self.store, 'put', side_effect=capture):
                with self.assertRaises(ManifestWritten):
                    pipeline._task(plan, task)
            self.assertEqual(len(captured), 1)
            value, reference = captured[0]
            self.assertEqual(value['discoveryProfile'], Q4_CURRENT_PROFILE)
            self.assertEqual(json.loads(self.store.get(reference)), value)
            self.assertEqual(len(value['items']), 0 if bad else 1)
            self.assertEqual(len(value['observations']), 1)

    def test_unattempted_engine_profile_does_not_invent_source_observations(self):
        pipeline = Pipeline(self.contract, self.store, None, clock=lambda: AS_OF)
        pipeline.audit_index = SimpleNamespace(predecessors=lambda *_: [])
        receipt = {'sourceId': self.source['id'], 'runId': 'a' * 64, 'attemptId': 'b' * 64,
                   'startedAt': AS_OF, 'outcome': 'failed', 'observationIds': [], 'validatedFacts': []}
        with patch('engine.binding_changes', return_value=(set(), [], [])):
            pipeline._separate_history(receipt)
        manifest = json.loads(self.store.get(receipt['itemManifest']))
        self.assertEqual(manifest['discoveryProfile'], Q4_CURRENT_PROFILE)
        self.assertEqual((manifest['items'], manifest['observations']), ([], []))
        self.assertFalse(receipt['discoveryRecorded'])
        self.assertEqual(receipt['observationIds'], [])


if __name__ == '__main__':
    unittest.main()
