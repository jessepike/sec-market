import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from contracts import digest
from rollback_drill import drill, scheduled_upstream, automatic_target, automatic_preflight, scheduled_source_clocks, REPO
from storage import LocalStore


class RollbackDrillTests(unittest.TestCase):
    def test_automatic_preflight_skips_before_account_group_when_collector_pending(self):
        api=Mock(return_value={'workflow_runs':[{'status':'queued'}]})
        result=automatic_preflight(123,api,Mock(return_value={}),today='2026-10-23')
        self.assertFalse(result['allowed'])
        self.assertEqual(result['reason'],'DRILL_COLLECTOR_IS_QUEUED_OR_RUNNING')
        self.assertEqual(api.call_count,1)

    def test_actual_scheduled_collection_receipt_can_be_incomplete(self):
        run={'id':789,'run_attempt':1,'event':'schedule','status':'completed','conclusion':'success',
             'head_branch':'main','head_sha':'a'*40,'created_at':'2026-10-23T06:07:00Z'}
        receipt={'githubRunId':'789','githubEventName':'schedule','githubRef':'refs/heads/main',
                 'appRevision':'a'*40,'executionCompleted':True,'complete':False,
                 'contractSha256':digest(__import__('json').loads((REPO/'contracts/market.json').read_text()))}
        api=Mock(side_effect=[{'workflow_runs':[run]},{'object':{'sha':'b'*40}},None,
                              {'releaseId':'c'*64},receipt])
        result=automatic_preflight(123,api,Mock(return_value={'githubRunId':123}),today='2026-10-23')
        self.assertTrue(result['allowed'])
        self.assertFalse(result['scheduledCollectorReceipt']['complete'])

    def test_wrong_contract_scheduled_clock_is_held(self):
        run={'id':789,'run_attempt':1,'event':'schedule','status':'completed','conclusion':'success',
             'head_branch':'main','head_sha':'a'*40,'created_at':'2026-10-23T06:07:00Z'}
        receipt={'githubRunId':'789','githubEventName':'schedule','githubRef':'refs/heads/main',
                 'appRevision':'a'*40,'executionCompleted':True,'contractSha256':'wrong'}
        api=Mock(side_effect=[{'workflow_runs':[run]},{'object':{'sha':'b'*40}},None,
                              {'releaseId':'c'*64},receipt])
        result=automatic_preflight(123,api,Mock(return_value={'githubRunId':123}),today='2026-10-23')
        self.assertFalse(result['allowed'])
        self.assertEqual(result['reason'],'DRILL_SCHEDULED_COLLECTOR_ARCHIVE_BINDING_MISSING')

    def test_accepted_release_requires_same_run_policy_and_actual_scheduled_clock(self):
        manifest={'runId':'accepted-run','contractSha256':'accepted-policy'}
        good={'runId':'accepted-run','contractSha256':'accepted-policy','executionCompleted':True,
              'githubEventName':'schedule','githubRef':'refs/heads/main'}
        self.store.write_once('ci/collection-runs/1-1.json',good)
        for index,change in enumerate(({'contractSha256':'wrong'},{'runId':'wrong'},
                                       {'githubEventName':'workflow_dispatch'},{'executionCompleted':False}),2):
            self.store.write_once(f'ci/collection-runs/{index}-1.json',{**good,**change})
        self.assertEqual(scheduled_source_clocks(self.store,manifest),[good])

    def test_manual_collection_cannot_substitute_for_actual_scheduled_receipt(self):
        api=Mock(return_value={'workflow_runs':[{'event':'workflow_dispatch','status':'completed',
                    'conclusion':'success','head_branch':'main','created_at':'2026-10-23T06:07:00Z'}]})
        result=automatic_preflight(123,api,Mock(return_value={}),today='2026-10-23')
        self.assertFalse(result['allowed'])
        self.assertEqual(result['reason'],'DRILL_NO_COMPLETED_SCHEDULED_COLLECTOR')

    def test_automatic_acceptance_date_expires_before_remote_calls(self):
        api,lookup=Mock(),Mock()
        self.assertFalse(automatic_preflight(123,api,lookup,today='2026-10-24')['allowed'])
        api.assert_not_called()
        lookup.assert_not_called()

    def test_upstream_must_be_actual_successful_private_main_scheduled_publisher(self):
        import json
        good={'id':123,'repository':{'full_name':'jessepike/sec-market','private':True},
              'path':'.github/workflows/subscription-publisher.yml','head_branch':'main','head_sha':'a'*40,
              'status':'completed','conclusion':'success','event':'schedule'}
        runner=Mock(return_value=SimpleNamespace(returncode=0,stdout=json.dumps(good)))
        self.assertEqual(scheduled_upstream(123,runner)['event'],'schedule')
        for field,value in [('event','workflow_dispatch'),('head_branch','preview'),('conclusion','failure'),
                            ('path','.github/workflows/other.yml'),('head_sha','bad')]:
            runner.return_value.stdout=json.dumps({**good,field:value})
            with self.subTest(field=field),self.assertRaisesRegex(ValueError,'DRILL_UPSTREAM_NOT_TRUSTED_SCHEDULED_PUBLISHER'):
                scheduled_upstream(123,runner)

    def test_automatic_driver_derives_only_current_accepted_release_and_never_repeats(self):
        target,reason=automatic_target(self.store,{'appRevision':'b'*40})
        self.assertEqual(target,self.current['releaseId'])
        self.assertIsNone(reason)
        self.store.compare_and_swap('rollback-drill',None,{'phase':'intent_archived'})
        self.assertEqual(automatic_target(self.store,{'appRevision':'b'*40}), (None,'DRILL_ALREADY_RECORDED'))

    def test_legacy_head_and_different_upstream_cannot_start_automatic_drill(self):
        with self.assertRaisesRegex(ValueError,'DRILL_UPSTREAM_DOES_NOT_MATCH_CURRENT_RELEASE'):
            automatic_target(self.store,{'appRevision':'f'*40})
        self.store.compare_and_swap('production',self.current,self.baseline)
        self.assertEqual(automatic_target(self.store,{'appRevision':'a'*40}), (None,'DRILL_NO_ACCEPTED_DAILY_RELEASE'))

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store=LocalStore(self.temp.name)
        self.baseline={'sequence':0,'deploymentId':'https://old.vercel.app','legacyBaseline':True,
                       'legacyAppReceipt':{'appRevision':'a'*40}}
        self.baseline['releaseId']=digest(self.baseline)
        test={'actualMainGate':True}
        self.manifest={'parentReleaseId':self.baseline['releaseId'],'testProvenance':{'githubRunId':123},
                       'testReceiptSha256':digest(test),'artifact':{'sha256':'x'},'appRevision':'b'*40,
                       'snapshot':{'sha256':'s'},'contractSha256':'c'}
        self.manifest['releaseId']=digest(self.manifest)
        self.current={'releaseId':self.manifest['releaseId'],'sequence':1,'deploymentId':'https://new.vercel.app'}
        self.ack={'ready':True,'appRevision':'b'*40,'dataReleaseId':self.current['releaseId'],
                  'snapshotSha256':'s','artifactSha256':'x','contractSha256':'c'}
        self.store.compare_and_swap('production',None,self.current)
        self.store.write_once('releases/'+self.current['releaseId']+'.json',{'manifest':self.manifest,'acknowledgement':self.ack})
        self.store.write_once('production-baselines/'+self.baseline['releaseId']+'.json',self.baseline)
        self.store.write_once('gate-receipts/123.json',test)
        self.adapter=Mock(site='https://securitymarketpulse.com')
        self.adapter.production_paths_controlled.return_value=True
        self.adapter.probe.return_value=self.ack
        self.adapter.probe_production.return_value=self.ack
        self.adapter._get.return_value=self.baseline['legacyAppReceipt']
        self.phases=[]

    def run_drill(self):
        with patch('rollback_drill.verify_ready'), patch('rollback_drill.stage_files',return_value={'static/index.html':b'accepted'}):
            return drill(self.store,self.adapter,self.current['releaseId'],
                         lambda:self.phases.append(self.store.read('heads/rollback-drill.json')['phase']),Mock())

    def test_intent_is_remotely_acknowledged_before_first_alias_change(self):
        def rollback(_deployment):
            self.assertIn('intent_archived',self.phases)
        self.adapter.rollback.side_effect=rollback
        result=self.run_drill()
        self.assertEqual(result['phase'],'passed')
        self.assertEqual([call.args[0] for call in self.adapter.rollback.call_args_list],
                         [self.baseline['deploymentId'],self.current['deploymentId']])
        self.assertEqual(self.store.read('heads/production.json'),self.current)
        self.assertFalse(result['baselineByteInventoryAvailable'])
        self.adapter.promote.assert_not_called()

    def test_failed_baseline_live_probe_still_restores_latest(self):
        self.adapter._get.side_effect=[self.baseline['legacyAppReceipt'],{'appRevision':'wrong'}]
        with self.assertRaisesRegex(ValueError,'DRILL_BASELINE_LIVE_RECEIPT_DIFFERS'):
            self.run_drill()
        self.assertEqual(self.adapter.rollback.call_args.args[0],self.current['deploymentId'])
        self.assertEqual(self.phases[-1],'current_restored')

    def test_failed_remote_intent_performs_no_alias_changes(self):
        with patch('rollback_drill.verify_ready'), patch('rollback_drill.stage_files',return_value={}):
            with self.assertRaisesRegex(RuntimeError,'archive unavailable'):
                drill(self.store,self.adapter,self.current['releaseId'],Mock(side_effect=RuntimeError('archive unavailable')),Mock())
        self.adapter.rollback.assert_not_called()

    def test_different_current_release_is_held_before_any_alias_change(self):
        with self.assertRaisesRegex(ValueError,'DRILL_ACCEPTED_CURRENT_RELEASE_REQUIRED'):
            drill(self.store,self.adapter,'f'*64,Mock(),Mock())
        self.adapter.rollback.assert_not_called()
