import os
import tempfile
import unittest
from unittest.mock import Mock, patch

from collect import reuse_scheduled_collection, archive_collection_result, verified_scheduled_source
from contracts import digest
from storage import LocalStore


class ScheduledReuseTests(unittest.TestCase):
    def install_v2(self):
        from test_coverage_summary import separated_coverage
        from coverage_summary import coverage_details
        from contracts import canonical
        self.coverage.update(separated_coverage())
        head = self.state.read('heads/latest-run.json')
        self.reference = self.state.put(self.coverage)
        self.state.compare_and_swap('latest-run', head, {'runId': self.coverage['runId'], 'receipt': self.reference})
        details = coverage_details(self.coverage)
        self.clock.update({k: self.coverage[k] for k in ('successfulTasks', 'requiredTasks', 'complete')}, **details)
        (self.state.root/'ci/collection-runs/123-1.json').write_bytes(canonical(self.clock))
        old = self.state.read('heads/cloud-collector.json')
        self.state.compare_and_swap('cloud-collector', old, {'coverage': {
            **{k: self.coverage[k] for k in ('runId', 'successfulTasks', 'requiredTasks', 'complete')}, **details}})

    def test_v2_reuse_preserves_and_archives_separate_review_boundaries(self):
        self.install_v2()
        before = {p.name: p.read_bytes() for p in (self.state.root/'heads').glob('*.json')}
        result = self.reuse()
        self.assertTrue(result['intake']['complete'])
        self.assertFalse(result['processing']['complete'])
        self.assertFalse(result['historicalReview']['complete'])
        self.assertEqual(result['sourceCheckedAt'], self.coverage['checkedAt'])
        retained = archive_collection_result(self.state, result, self.contract, '1')
        self.assertEqual(retained['processing'], self.coverage['processing'])
        self.assertEqual(before, {p.name: p.read_bytes() for p in (self.state.root/'heads').glob('*.json')})

    def test_v2_reuse_rejects_clock_with_different_review_summary(self):
        from contracts import canonical
        self.install_v2()
        self.clock['processing']['pendingDocuments'] = 0
        (self.state.root/'ci/collection-runs/123-1.json').write_bytes(canonical(self.clock))
        self.assertIsNone(self.reuse())

    def test_actual_v2_checkpoint_summary_roundtrips_into_scheduled_reuse(self):
        from collect import session_runtime
        self.install_v2()
        session = {'sessionId': 'github-real-checkpoint', 'role': 'collector', 'appRevision': 'a'*40,
                   'executionMode': 'github_subscription', 'startedAt': self.coverage['checkedAt']}
        entry = session_runtime.collection_checkpoint(self.state, session, 'finish',
                    {'executionCompleted': True}, '2026-10-23T06:31:00Z')
        self.assertEqual(self.state.read('heads/cloud-collector.json')['coverage'], entry['coverage'])
        self.assertEqual(entry['coverage']['intake'], self.coverage['intake'])
        result = self.reuse()
        self.assertEqual(result['processing'], entry['coverage']['processing'])
        self.assertEqual(result['historicalReview'], entry['coverage']['historicalReview'])
        self.assertEqual(result['sourceCheckedAt'], self.coverage['checkedAt'])

    def test_actual_legacy_checkpoint_summary_remains_identical(self):
        from collect import session_runtime
        self.assertEqual(session_runtime.summary(self.state), {
            'runId': self.coverage['runId'], 'successfulTasks': 244, 'requiredTasks': 557, 'complete': False})

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.state=LocalStore(self.temp.name)
        self.contract={'schedule':{'overdueHours':30}}
        self.coverage={'runId':'real-source-run','contractSha256':digest(self.contract),
                       'checkedAt':'2026-10-23T06:30:00Z','successfulTasks':244,'requiredTasks':557,
                       'complete':False,'gapTaskIds':['gap'],'receipts':[]}
        self.reference=self.state.put(self.coverage)
        self.state.compare_and_swap('latest-run',None,{'runId':'real-source-run','receipt':self.reference})
        self.state.compare_and_swap('cloud-collector',None,{'coverage':{k:self.coverage[k] for k in
                                   ('runId','successfulTasks','requiredTasks','complete')}})
        self.state.write_once('runs/real-source-run/plan.json',{'runId':'real-source-run'})
        self.clock={'githubRunId':'123','githubRunAttempt':1,'githubEventName':'schedule',
                    'githubRef':'refs/heads/main','appRevision':'a'*40,'contractSha256':digest(self.contract),
                    'runId':'real-source-run','executionCompleted':True,'successfulTasks':244,
                    'requiredTasks':557,'complete':False}
        self.state.write_once('ci/collection-runs/123-1.json',self.clock)
        self.state.compare_and_swap('budget-2026-10-23',None,{'calls':80,'documents':40,'fetches':5500})
        self.github={'id':123,'run_attempt':1,'repository':{'full_name':'jessepike/sec-market','private':True},
                     'path':'.github/workflows/subscription-collector.yml','status':'completed','conclusion':'success',
                     'event':'schedule','head_branch':'main','head_sha':'a'*40,'created_at':'2026-10-23T06:07:00Z'}
        self.environment=patch.dict(os.environ,{'GITHUB_EVENT_NAME':'schedule','GITHUB_REF':'refs/heads/main',
                            'GITHUB_RUN_ID':'456','SMP_EVENT_SCHEDULE':'7 7 23 10 *'},clear=True)
        self.environment.start()
        self.addCleanup(self.environment.stop)

    def reuse(self, lookup=None):
        with patch('collect.reconcile',side_effect=lambda _p,_r,_c,at,_s:{**self.coverage,'checkedAt':at}), \
             patch('collect.session_runtime.git',return_value='b'*40):
            return reuse_scheduled_collection(self.state,self.contract,'2026-10-23T07:07:00Z',
                                             lookup or Mock(return_value=self.github))

    def test_reuse_preserves_original_source_age_and_all_budget_and_latest_bytes(self):
        before={p.name:p.read_bytes() for p in (self.state.root/'heads').glob('*.json')}
        result=self.reuse()
        self.assertEqual(result['outcome'],'source_work_reused')
        self.assertEqual(result['sourceCheckedAt'],self.coverage['checkedAt'])
        self.assertEqual(result['sourceReceiptSha256'],self.reference['sha256'])
        self.assertEqual(result['reusesScheduledCollectionRunId'],123)
        self.assertFalse(result['complete'])
        self.assertEqual(result['modelCalls'],0)
        self.assertEqual(result['fetches'],0)
        self.assertEqual(before,{p.name:p.read_bytes() for p in (self.state.root/'heads').glob('*.json')})
        retained=archive_collection_result(self.state,result,self.contract,'1')
        self.assertEqual(retained['sourceCheckedAt'],self.coverage['checkedAt'])

    def test_forged_manual_upstream_cannot_supply_schedule_proof(self):
        self.assertIsNone(self.reuse(Mock(return_value={**self.github,'event':'workflow_dispatch'})))

    def test_shared_verifier_supplies_same_proof_to_publisher_callback(self):
        os.environ['GITHUB_EVENT_NAME']='workflow_run'
        with patch('collect.reconcile',side_effect=lambda _p,_r,_c,at,_s:{**self.coverage,'checkedAt':at}):
            source=verified_scheduled_source(self.state,self.contract,'2026-10-23T07:07:00Z',
                                             Mock(return_value=self.github))
        self.assertEqual(source['githubRunId'],123)
        self.assertEqual(source['clock'],self.clock)
        self.assertEqual(source['coverage']['checkedAt'],self.coverage['checkedAt'])

    def test_regular_daily_and_manual_requests_do_not_take_reuse_route(self):
        for event,cron in [('schedule','17 5 * * *'),('workflow_dispatch','7 7 23 10 *')]:
            os.environ.update(GITHUB_EVENT_NAME=event,SMP_EVENT_SCHEDULE=cron)
            lookup=Mock()
            self.assertIsNone(self.reuse(lookup))
            lookup.assert_not_called()

    def test_reconciliation_is_replayed_at_original_time_without_relabeling_freshness(self):
        with patch('collect.reconcile',side_effect=lambda _p,_r,_c,at,_s:{**self.coverage,'checkedAt':at}) as reconcile, \
             patch('collect.session_runtime.git',return_value='b'*40):
            result=reuse_scheduled_collection(self.state,self.contract,'2026-10-23T07:07:00Z',
                                             Mock(return_value=self.github))
        self.assertEqual([c.args[3] for c in reconcile.call_args_list],
                         [self.coverage['checkedAt'],'2026-10-23T07:07:00Z'])
        self.assertEqual(result['sourceCheckedAt'],self.coverage['checkedAt'])
