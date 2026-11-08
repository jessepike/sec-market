"""Exercise the exact checkout-independent workflow programs without remote writes."""
import copy
from contextlib import redirect_stdout
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import textwrap
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / '.github/workflows/freshness.yml'
REPO = 'jessepike/sec-market'


def program(marker):
    source = WORKFLOW.read_text()
    begin, end = '# BEGIN ' + marker, '# END ' + marker
    if source.count(begin) != 1 or source.count(end) != 1:
        raise AssertionError('Workflow program marker is ambiguous')
    block = textwrap.dedent(source.split(begin, 1)[1].split(end, 1)[0]).strip()
    prefix, suffix = "python3 - <<'PY'\n", '\nPY'
    if not block.startswith(prefix) or not block.endswith(suffix):
        raise AssertionError('Workflow program envelope changed')
    code = block[len(prefix):-len(suffix)]
    if '${{' in code:
        raise AssertionError('Workflow expressions must remain data in environment')
    namespace = {'__name__': 'workflow_program_under_test'}
    exec(compile(code, str(WORKFLOW) + '#' + marker, 'exec'), namespace)
    return namespace


def receipt(healthy=False):
    return {'healthy': healthy, 'checkedAt': '2026-10-26T05:41:00Z',
            'reasons': [] if healthy else ['DAILY_INTAKE_INCOMPLETE', 'HELD_CLAIMS_37'],
            'notification': {'delivery': 'workflow_annotation', 'title': 'pipeline-watchdog',
                             'state': 'closed' if healthy else 'open'}}


class ProbeReceiptTests(unittest.TestCase):
    def setUp(self): self.code = program('WATCHDOG_PROBE_RECEIPT')
    def valid(self, value, status):
        raw = value if type(value) is bytes else json.dumps(value).encode()
        return self.code['acknowledged'](raw, status)
    def run_probe(self, raw, status):
        with tempfile.TemporaryDirectory(prefix='synthetic-watchdog-wrapper-') as temporary:
            root = Path(temporary); output = root / 'github-output'; log = io.StringIO()
            def transport(args, **kwargs):
                self.assertEqual(args[1:], ['ops/watchdog/probe.py', '--notify'])
                self.assertEqual(set(kwargs), {'stdout'})
                kwargs['stdout'].write(raw)
                return subprocess.CompletedProcess(args, status)
            with patch.dict(os.environ, {'RUNNER_TEMP': str(root), 'GITHUB_OUTPUT': str(output)}), \
                 patch.object(self.code['subprocess'], 'run', side_effect=transport) as run, redirect_stdout(log):
                result = self.code['main']()
            self.assertEqual(run.call_count, 1)
            return result, output.read_text(), log.getvalue()
    def test_honest_unhealthy_receipt_keeps_exit_two_and_acknowledgement(self):
        result, output, log = self.run_probe(json.dumps(receipt()).encode(), 2)
        self.assertEqual(result, 2); self.assertEqual(output, 'acknowledged=true\n')
        self.assertEqual(json.loads(log)['notification']['state'], 'open')
        self.assertIn('HELD_CLAIMS_37', json.loads(log)['reasons'])
    def test_healthy_existing_issue_recovery_and_no_issue_needed_receipts(self):
        self.assertTrue(self.valid(receipt(True), 0))
        value = receipt(True); value['notification'] = {'delivery': 'no_alert_needed'}
        result, output, _ = self.run_probe(json.dumps(value).encode(), 0)
        self.assertEqual(result, 0); self.assertEqual(output, 'acknowledged=true\n')
    def test_wrong_exit_health_state_and_unacknowledged_results_cannot_ack(self):
        for value, status in [(receipt(), 0), (receipt(True), 2), (receipt(), 1), (receipt(True), True)]:
            self.assertFalse(self.valid(value, status))
        for mutation in [lambda p:p.pop('notification'), lambda p:p.update(healthy=1),
                         lambda p:p.update(reasons=[]), lambda p:p.update(reasons=['']),
                         lambda p:p.update(reasons=['x'*257]), lambda p:p.update(reasons=['x']*1001),
                         lambda p:p.update(checkedAt='tomorrow'), lambda p:p.update(checkedAt='2026-10-26'),
                         lambda p:p['notification'].update(state='closed'),
                         lambda p:p['notification'].update(title='other'),
                         lambda p:p['notification'].update(delivery='github_issue_updated'),
                         lambda p:p['notification'].update(extra=True),
                         lambda p:p.update(notification={'delivery':'no_alert_needed'})]:
            value = receipt(); mutation(value)
            with self.subTest(value=value): self.assertFalse(self.valid(value, 2))
    def test_bounded_strict_json_and_malformed_success_becomes_failure(self):
        for raw in [b'', b'{}', b'[]', b'\xff', b'{"healthy":false,"healthy":false}',
                    b'{"x":NaN}', b'x'*1_000_001]:
            self.assertFalse(self.valid(raw, 2))
        status, output, log = self.run_probe(b'not json', 0)
        self.assertEqual(status, 1); self.assertEqual(output, 'acknowledged=false\n')
        self.assertNotIn('not json', log)
    def test_failed_notification_or_oversized_receipt_cannot_be_green(self):
        for raw, status in [(b'',1),(b'x'*1_000_001,0),(json.dumps(receipt()).encode(),1)]:
            result, output, _ = self.run_probe(raw,status)
            self.assertNotEqual(result,0);self.assertEqual(output,'acknowledged=false\n')


class ObserverReporterTests(unittest.TestCase):
    def setUp(self):
        self.code = program('WATCHDOG_OBSERVER_REPORTER')
        self.env = {'REPOSITORY':REPO,'GITHUB_RUN_ID':'40273459773','TESTS_OUTCOME':'failure',
                    'PROBE_OUTCOME':'skipped','PROBE_ACKNOWLEDGED':'','OBSERVER_JOB_RESULT':'failure'}
    def run_reporter(self, changes=None):
        log=io.StringIO();errors=io.StringIO()
        with patch.dict(os.environ,{**self.env,**(changes or {})}),redirect_stdout(log), \
             patch.object(self.code['sys'],'stderr',errors):
            self.assertEqual(self.code['main'](),0)
        return json.loads(log.getvalue()),errors.getvalue()
    def test_failed_tests_raise_an_error_annotation_and_write_no_issue(self):
        self.assertNotIn('subprocess',self.code)
        result,annotation=self.run_reporter()
        self.assertEqual(result['delivery'],'workflow_annotation');self.assertEqual(result['state'],'open')
        self.assertFalse(result['observerRecovered']);self.assertFalse(result['healthIssueChanged'])
        self.assertTrue(annotation.startswith('::error title=pipeline-observer::'))
        self.assertIn('Tests: failure',annotation);self.assertIn('Probe: skipped',annotation)
    def test_checkout_setup_skipped_cancelled_and_missing_outputs_report_failure(self):
        for changes in [{'TESTS_OUTCOME':'','PROBE_OUTCOME':''},
                        {'TESTS_OUTCOME':'cancelled','OBSERVER_JOB_RESULT':'cancelled'},
                        {'TESTS_OUTCOME':'skipped','OBSERVER_JOB_RESULT':'skipped'},
                        {'TESTS_OUTCOME':'success','PROBE_OUTCOME':'skipped','PROBE_ACKNOWLEDGED':'true'},
                        {'TESTS_OUTCOME':'success','PROBE_OUTCOME':'failure','PROBE_ACKNOWLEDGED':'false'},
                        {'TESTS_OUTCOME':'success','PROBE_OUTCOME':'success','PROBE_ACKNOWLEDGED':'true','OBSERVER_JOB_RESULT':'cancelled'},
                        {'TESTS_OUTCOME':'success','PROBE_OUTCOME':'','PROBE_ACKNOWLEDGED':'true'},
                        {'TESTS_OUTCOME':'success'}]:
            with self.subTest(changes=changes):
                result,annotation=self.run_reporter(changes)
                self.assertFalse(result['observerRecovered']);self.assertTrue(annotation.startswith('::error'))
    def test_trusted_probe_recovers_observer_with_a_notice(self):
        for probe in ('success','failure'):
            result,annotation=self.run_reporter({'TESTS_OUTCOME':'success','PROBE_OUTCOME':probe,
                                                 'PROBE_ACKNOWLEDGED':'true','OBSERVER_JOB_RESULT':probe})
            self.assertTrue(result['observerRecovered']);self.assertEqual(result['state'],'closed')
            self.assertTrue(annotation.startswith('::notice title=pipeline-observer::'))
    def test_untrusted_inputs_reject_and_are_not_shell_programs(self):
        changes=[{'GITHUB_RUN_ID':'1;touch /tmp/invalid'},{'GITHUB_RUN_ID':'0'},
                 {'REPOSITORY':'evil/repo'},{'TESTS_OUTCOME':'$(id)'},
                 {'PROBE_ACKNOWLEDGED':'TRUE'},{'OBSERVER_JOB_RESULT':'unknown'}]
        for change in changes:
            with self.subTest(change=change),self.assertRaises(ValueError): self.run_reporter(change)


class WorkflowBindingTests(unittest.TestCase):
    def test_named_tests_gate_probe_and_checkout_independent_reporter_runs_always(self):
        source=WORKFLOW.read_text();daily=source.split('  daily-pipeline:',1)[1].split('\n  observer-alert:',1)[0]
        reporter=source.split('\n  observer-alert:',1)[1].split('\n  probe:',1)[0]
        self.assertIn('id: watchdog_tests',daily);self.assertIn('id: watchdog_probe',daily)
        self.assertIn("if: success() && steps.watchdog_tests.outcome == 'success'",daily)
        self.assertIn('needs: daily-pipeline',reporter);self.assertIn('if: always()',reporter)
        self.assertNotIn('actions/checkout',reporter);self.assertNotIn('probe.py',reporter)
        self.assertNotIn('issues: write',source.split('\n  probe:',1)[0])
        self.assertIn('permissions: {}',reporter)
        for name in ['tests_outcome','probe_outcome','probe_acknowledged']:
            self.assertIn('needs.daily-pipeline.outputs.'+name,reporter)
        self.assertEqual(source.count('timeout-minutes: 5'),3)
        program('WATCHDOG_PROBE_RECEIPT');program('WATCHDOG_OBSERVER_REPORTER')

    def test_legacy_job_skips_only_explicit_true_even_after_unhealthy_observer(self):
        source=WORKFLOW.read_text()
        daily=source.split('  daily-pipeline:',1)[1].split('\n  observer-alert:',1)[0]
        legacy=source.split('\n  probe:',1)[1]
        self.assertIn('legacy_retired: ${{ steps.publication_route.outputs.legacy_retired }}',daily)
        self.assertLess(daily.index('id: publication_route'),daily.index('id: watchdog_tests'))
        self.assertIn('needs: daily-pipeline',legacy)
        self.assertIn("if: always() && needs.daily-pipeline.outputs.legacy_retired != 'true'",legacy)
        # A legitimate coverage failure must not implicitly skip this dependency's fallback.
        self.assertNotIn('needs.daily-pipeline.result',legacy.split('runs-on:',1)[0])
        self.assertIn("if jq -e '.publication.enabled == true' contracts/market.json",legacy)


class PublicationRouteTests(unittest.TestCase):
    def setUp(self): self.code=program('WATCHDOG_PUBLICATION_ROUTE')

    def test_only_strict_boolean_activation_retires_legacy_checks(self):
        valid={'publication':{'enabled':True}}
        self.assertTrue(self.code['legacy_retired'](json.dumps(valid).encode()))
        for value in (False,1,0,'true','false',None,[],{}):
            self.assertFalse(self.code['legacy_retired'](json.dumps({'publication':{'enabled':value}}).encode()))
        for value in ({},{'publication':True},{'publication':[]},{'publication':{}},[]):
            self.assertFalse(self.code['legacy_retired'](json.dumps(value).encode()))

    def test_missing_malformed_duplicate_nonfinite_or_oversized_contract_preserves_fallback(self):
        for raw in (b'',b'{}',b'\xff',b'x'*1_000_001,
                    b'{"publication":{"enabled":false,"enabled":true}}',
                    b'{"publication":{"enabled":true},"publication":{"enabled":false}}',
                    b'{"publication":{"enabled":true},"other":NaN}',
                    b'{"publication":{"enabled":true},"other":Infinity}'):
            self.assertFalse(self.code['legacy_retired'](raw))

    def test_actual_route_output_is_bounded_and_unreadable_contract_is_explicit_false(self):
        for raw,expected in ((b'{"publication":{"enabled":true}}','true'),(b'bad','false'),(None,'false')):
            with tempfile.TemporaryDirectory(prefix='synthetic-publication-route-') as temporary:
                output=Path(temporary)/'github-output';log=io.StringIO();reads=[]
                original=Path.open
                def open_path(path,mode='r',*args,**kwargs):
                    if str(path)=='contracts/market.json':
                        if raw is None:raise OSError('synthetic missing contract')
                        stream=io.BytesIO(raw)
                        class BoundedSource:
                            def __enter__(self):return self
                            def __exit__(self,*args):stream.close()
                            def read(self,count):reads.append(count);return stream.read(count)
                        return BoundedSource()
                    return original(path,mode,*args,**kwargs)
                with patch.dict(os.environ,{'GITHUB_OUTPUT':str(output)}),patch.object(Path,'open',open_path),redirect_stdout(log):
                    self.code['main']()
                self.assertEqual(output.read_text(),'legacy_retired='+expected+'\n')
                self.assertEqual(reads,[] if raw is None else [1_000_001])
                self.assertNotIn('synthetic missing contract',log.getvalue())


if __name__=='__main__':unittest.main()
