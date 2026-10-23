import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from contracts import digest
from rollback_drill import drill
from storage import LocalStore


class RollbackDrillTests(unittest.TestCase):
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
