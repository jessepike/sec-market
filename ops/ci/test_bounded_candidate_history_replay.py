"""Offline tests for replaying immutable schema-2 diagnostics after plan changes."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'web/scripts/pipeline'))
sys.path.insert(0, str(ROOT / 'ops/ci'))

from contracts import canonical, digest
from onboarding import (PersistentProbeBudget, _verify_bounded_candidate_result,
                        probe_sources, replay_bounded_candidate_diagnostic)
from test_bounded_candidate_traversal import (BoundedCandidateTraversalTests,
                                               CandidateFetcher)


class BoundedCandidateHistoryReplayTests(unittest.TestCase):
    def setUp(self):
        self.fixture = BoundedCandidateTraversalTests()
        self.fixture.setUp()

    def tearDown(self):
        self.fixture.doCleanups()

    def _archived_run(self, report):
        fixture = self.fixture
        record = {'schemaVersion': 1, 'checkpointProfile': 'source_probe',
                  'githubRunId': '99001', 'githubRunAttempt': 1,
                  'githubEventName': 'workflow_dispatch', 'githubRef': 'refs/heads/main',
                  'appRevision': 'a' * 40, 'contractSha256': digest(fixture.policy),
                  'diagnostic': report, 'executionCompleted': report['executionCompleted'],
                  'outcome': 'completed_diagnostic' if report['executionCompleted'] else 'budget_denied',
                  'modelCalls': 0, 'apiFallback': False, 'semanticAdmission': False,
                  'coverageCredit': False, 'sourceChecksCredited': 0, 'qualifiedSources': 0,
                  'publication': {'published': False, 'reason': 'SOURCE_PROBE_DIAGNOSTIC_ONLY'}}
        raw = canonical(record)
        key = 'ci/source-probe-runs/99001-1.json'
        fixture.store.write_once(key, raw)
        return {'key': key, 'sha256': digest(raw), 'bytes': len(raw)}

    def _report(self, *, deadline_after_first=False):
        fixture = self.fixture
        fixture.plan()
        clock = fixture.clock

        class Fetcher(CandidateFetcher):
            def fetch(self, source, url):
                result = super().fetch(source, url)
                if deadline_after_first and len(self.calls) == 1:
                    clock.elapsed = 1200
                return result

        fetcher = Fetcher(fixture.store, clock=clock)
        budget = PersistentProbeBudget(fixture.store, fixture.policy, clock=clock.now,
                                       monotonic=clock.monotonic, maximum_seconds=1200)
        auth, observation = fixture._authenticated_test_authority()
        with auth, observation:
            return probe_sources(fixture.policy, fixture.store, fetcher,
                reservation_context=budget, qualification_plan_path=fixture.path)

    def test_historical_replay_survives_live_plan_change_while_live_check_rejects_it(self):
        report = self._report()
        run_ref = self._archived_run(report)
        plan_ref = report['planReference']
        result = replay_bounded_candidate_diagnostic(self.fixture.policy, self.fixture.store,
                                                    run_ref, plan_ref)
        self.assertEqual(result['report'], report)
        self.assertEqual(result['plan']['rawSha256'], report['planRawSha256'])

        live_plan = dict(result['plan'], path=str(self.fixture.path))
        self.fixture.path.write_bytes(b'{"schemaVersion":1}')
        with self.assertRaisesRegex(ValueError, 'BOUNDED_CANDIDATE_CURRENT_PLAN_CHANGED'):
            _verify_bounded_candidate_result(self.fixture.policy, self.fixture.store,
                                             live_plan, report)
        # Historical replay has no dependency on that mutable path.
        self.assertEqual(replay_bounded_candidate_diagnostic(self.fixture.policy,
            self.fixture.store, run_ref, plan_ref)['report'], report)

    def test_valid_partial_run_is_replayed_without_becoming_complete(self):
        report = self._report(deadline_after_first=True)
        self.assertFalse(report['executionCompleted'])
        self.assertTrue(report['budgetDenied'])
        result = replay_bounded_candidate_diagnostic(self.fixture.policy, self.fixture.store,
            self._archived_run(report), report['planReference'])
        self.assertFalse(result['report']['executionCompleted'])
        self.assertEqual(result['report']['sources'][0]['observations'][0]['url'],
                         result['plan']['sources'][0]['indexUrl'])

    def test_outer_collector_completion_denial_is_replayed_as_unreserved_partial_evidence(self):
        report = self._report()
        report['checkedAt'] = '2026-10-23T12:20:01Z'
        report['executionCompleted'] = False
        report['budgetDenied'] = True
        report['completionDenial'] = 'SOURCE_PROBE_DEADLINE_EXCEEDED'
        report['reservationContext']['reservationDenials'] = {
            'SOURCE_PROBE_DEADLINE_EXCEEDED': 1}
        replay = replay_bounded_candidate_diagnostic(self.fixture.policy, self.fixture.store,
            self._archived_run(report), report['planReference'])
        self.assertFalse(replay['report']['executionCompleted'])
        self.assertEqual(replay['report']['completionDenial'], 'SOURCE_PROBE_DEADLINE_EXCEEDED')

    def test_rejects_alternate_plan_reference_and_wrong_original_contract(self):
        report = self._report()
        run_ref = self._archived_run(report)
        alternate = self.fixture.store.put(self.fixture.path.read_bytes() + b' ')
        with self.assertRaisesRegex(ValueError, 'BOUNDED_CANDIDATE_HISTORICAL_PLAN_JOIN_INVALID'):
            replay_bounded_candidate_diagnostic(self.fixture.policy, self.fixture.store,
                                                run_ref, alternate)
        wrong_contract = copy.deepcopy(self.fixture.policy)
        wrong_contract['model'] = 'different'
        with self.assertRaisesRegex(ValueError, 'BOUNDED_CANDIDATE_HISTORICAL_RUN_ENVELOPE_INVALID'):
            replay_bounded_candidate_diagnostic(wrong_contract, self.fixture.store,
                                                run_ref, report['planReference'])

    def test_historical_replay_rejects_wrong_source_observation_wrapper(self):
        report = copy.deepcopy(self._report())
        source = report['sources'][0]
        page = source['observations'][0]
        wrapper = json.loads(self.fixture.store.get(page['observation']))
        wrapper['sourceId'] = 'other-source'
        forged_ref = self.fixture.store.put(wrapper)
        original_ref = page['observation']
        page['observation'] = forged_ref
        for request in source['requestReservations']:
            if request.get('observation') == original_ref:
                request['observation'] = forged_ref
                break
        with self.assertRaisesRegex(ValueError, 'BOUNDED_CANDIDATE_OBSERVATION_SOURCE_BINDING_INVALID'):
            replay_bounded_candidate_diagnostic(self.fixture.policy, self.fixture.store,
                self._archived_run(report), report['planReference'])

    def test_rejects_wrong_run_envelope_and_nonzero_credit(self):
        report = self._report()
        for field, value in (('githubRef', 'refs/heads/preview'), ('githubEventName', 'push'),
                             ('modelCalls', 1), ('coverageCredit', True)):
            with self.subTest(field=field):
                run_ref = self._archived_run(report)
                record = json.loads(self.fixture.store.get(run_ref))
                record[field] = value
                # Immutable-key collision prevents replacing the original object; use a fresh run key.
                key = f"ci/source-probe-runs/{99002 + len(field)}-1.json"
                record['githubRunId'] = key.split('/')[-1].split('-')[0]
                raw = canonical(record)
                self.fixture.store.write_once(key, raw)
                altered_ref = {'key': key, 'sha256': digest(raw), 'bytes': len(raw)}
                with self.assertRaisesRegex(ValueError, 'BOUNDED_CANDIDATE_HISTORICAL_RUN_ENVELOPE_INVALID'):
                    replay_bounded_candidate_diagnostic(self.fixture.policy, self.fixture.store,
                                                        altered_ref, report['planReference'])


if __name__ == '__main__':
    unittest.main()
