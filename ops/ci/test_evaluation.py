import copy
import json
from pathlib import Path
import tempfile
import unittest
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'ops/evaluation'))
from scorecard import digest, evaluate, load_pinned, markdown, plan_run


class ScorecardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.contract = json.loads((ROOT / 'contracts/market.json').read_text())
        self.plan = plan_run(self.contract, '2026-10-23T12:00:00Z')
        self.manifest = dict(schemaVersion=1, evaluatedAt='2026-10-23T13:00:00Z', appRevision='a' * 40, inputs={})
        self.pin('contract', self.contract)
        receipts = []
        sources = {s['id']: s for s in self.contract['sources']}
        required = [t for t in self.plan['tasks'] if t['required']]
        sec = [t['taskId'] for t in required if sources.get(t['sourceId'], {}).get('kind') in ('sec_facts', 'sec_submissions', 'sec_documents')]
        other = [t['taskId'] for t in required if t['sourceId'] and t['taskId'] not in sec]
        good = set(sec + other[:73])
        for task in self.plan['tasks']:
            ok = task['taskId'] in good
            receipts.append(dict(taskId=task['taskId'], runId=self.plan['runId'], sourceId=task['sourceId'], supplierId=task['supplierId'], completedAt='2026-10-23T11:59:00Z', outcome='checked_no_change' if ok else 'not_checked', discoveryComplete=ok, observationIds=['observation'] if ok else []))
        self.coverage = dict(checkedAt='2026-10-23T12:00:00Z', contractSha256=digest(self.contract), runId=self.plan['runId'], inventorySha256=self.plan['inventorySha256'], supplierCount=len(self.contract['suppliers']), requiredTasks=len(required), successfulTasks=len(good), complete=False, gapTaskIds=sorted({t['taskId'] for t in required} - good), receipts=receipts)
        self.pin('coverage', self.coverage)

    def pin(self, name, value):
        raw = json.dumps(value).encode()
        path = self.base / (name + '.json')
        path.write_bytes(raw)
        self.manifest['inputs'][name] = dict(path=path.name, sha256=digest(raw))

    def report(self):
        return evaluate(self.manifest, self.base)

    def measure(self, name):
        return next(m for m in self.report()['measures'] if m['id'] == name)

    def gate(self):
        gate = dict(runId=self.coverage['runId'], appRevision='a' * 40, contractSha256=digest(self.contract), collectionReceiptSha256=self.manifest['inputs']['coverage']['sha256'], githubRunId=123, artifactSha256='b' * 64, result='pass', executedTests=389, checks={name: dict(result='pass', logSha256='c' * 64) for name in ['certify:sec', 'refresh:edgar', 'refresh:filing-events', 'test']})
        self.pin('gate', gate)
        return gate

    def test_baseline_coverage_and_sec_have_separate_denominators(self):
        coverage = self.measure('coverage.required_tasks')
        self.assertEqual((coverage['numerator'], coverage['denominator'], coverage['status']), (121, 557, 'fail'))
        sec = self.measure('coverage.sec_tasks')
        self.assertEqual((sec['numerator'], sec['denominator'], sec['status']), (48, 48, 'pass'))

    def test_missing_precision_and_value_stay_unmeasured_not_zero_or_pass(self):
        for name in ['accuracy.claim_precision', 'accuracy.eligible_event_recall', 'value.observed_use', 'durability.sustained_operation']:
            row = self.measure(name)
            self.assertEqual(row['status'], 'unmeasured')
            self.assertIsNone(row['numerator'])
            self.assertIsNone(row['denominator'])
        self.assertNotIn('overallScore', self.report())

    def claim_audit(self, verdicts=('supported', 'contradicted', 'insufficient')):
        counts = {key: verdicts.count(key) for key in ('supported', 'contradicted', 'insufficient', 'primary_source_missing')}
        pin = dict(path='review.json', sha256='e' * 64)
        report = dict(schemaVersion=1, kind='published_claim_review_binding_report', appRevision='a' * 40,
                      evaluatedAt='2026-10-23T12:30:00Z', bindingChecksPassed=True,
                      inventoryCount=len(verdicts), reviewedCount=len(verdicts), verdictCounts=counts,
                      inputPins=dict(inventory=pin, reviews={key:pin for key in ('events_a_m', 'events_n_z', 'supplier_fields')}),
                      records=[dict(id=f'event:{i}', partition='events_a_m', verdict=verdict) for i, verdict in enumerate(verdicts)])
        self.pin('claimAudit', report)
        return report

    def test_known_factual_contradiction_fails_even_when_release_tests_pass(self):
        self.gate()
        self.claim_audit()
        self.assertEqual(self.measure('accuracy.known_release_checks')['status'], 'pass')
        known = self.measure('accuracy.known_contradictions')
        self.assertEqual((known['status'], known['numerator'], known['maximumCount']), ('fail', 1, 0))
        self.assertEqual(known['recordIds'], ['event:1'])
        self.assertEqual(self.measure('accuracy.reviewed_records')['numerator'], 3)
        self.assertEqual(self.measure('accuracy.claim_precision')['status'], 'unmeasured')
        self.assertIn('1 / maximum 0', markdown(self.report()))

    def test_no_known_contradiction_does_not_estimate_precision_or_recall(self):
        self.claim_audit(('supported', 'insufficient'))
        self.assertEqual(self.measure('accuracy.known_contradictions')['status'], 'pass')
        for identifier in ('accuracy.claim_precision', 'accuracy.eligible_event_recall'):
            self.assertEqual(self.measure(identifier)['status'], 'unmeasured')

    def test_missing_claim_audit_is_unmeasured(self):
        self.assertEqual(self.measure('accuracy.known_contradictions')['status'], 'unmeasured')

    def test_claim_audit_cannot_cover_another_revision_or_future_time(self):
        for key, value in [('appRevision', 'b' * 40), ('evaluatedAt', '2026-10-23T14:00:00Z')]:
            audit = self.claim_audit()
            audit[key] = value
            self.pin('claimAudit', audit)
            with self.assertRaises(ValueError):
                self.report()

    def test_claim_audit_rejects_changed_counters_duplicates_and_missing_bindings(self):
        mutations = [
            lambda audit: audit['verdictCounts'].update(contradicted=0),
            lambda audit: audit['records'].append(copy.deepcopy(audit['records'][0])),
            lambda audit: audit.update(reviewedCount=2),
            lambda audit: audit.update(bindingChecksPassed=False),
            lambda audit: audit['inputPins']['reviews'].pop('events_n_z'),
            lambda audit: audit['records'][0].update(verdict='accurate'),
            lambda audit: audit['inputPins']['inventory'].update(sha256='not-a-hash'),
        ]
        for mutate in mutations:
            audit = self.claim_audit()
            mutate(audit)
            self.pin('claimAudit', audit)
            with self.assertRaises(ValueError):
                self.report()

    def test_stale_check_fails_even_with_fresh_evaluation(self):
        self.manifest['evaluatedAt'] = '2026-10-25T13:00:00Z'
        self.assertEqual(self.measure('freshness.collection_receipt')['status'], 'fail')
        self.assertEqual(self.measure('coverage.required_tasks')['numerator'], 121)

    def test_future_check_refused(self):
        self.manifest['evaluatedAt'] = '2026-10-23T11:00:00Z'
        with self.assertRaisesRegex(ValueError, 'future'):
            self.report()

    def test_bad_bytes_refused_before_scoring(self):
        (self.base / 'coverage.json').write_text('{}')
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            self.report()

    def test_changed_denominator_refused_even_if_repinned(self):
        self.coverage['requiredTasks'] -= 1
        self.pin('coverage', self.coverage)
        with self.assertRaisesRegex(ValueError, 'denominator'):
            self.report()

    def test_false_success_count_and_complete_refused(self):
        for field, value in [('successfulTasks', 557), ('complete', True)]:
            original = copy.deepcopy(self.coverage)
            self.coverage[field] = value
            self.pin('coverage', self.coverage)
            with self.assertRaises(ValueError):
                self.report()
            self.coverage = original

    def test_unsupported_success_and_wrong_identity_refused(self):
        good = next(r for r in self.coverage['receipts'] if r['discoveryComplete'])
        good['observationIds'] = []
        self.pin('coverage', self.coverage)
        with self.assertRaisesRegex(ValueError, 'Unsupported success'):
            self.report()
        good['observationIds'] = ['observation']
        good['supplierId'] = 'someone-else'
        self.pin('coverage', self.coverage)
        with self.assertRaisesRegex(ValueError, 'identity'):
            self.report()

    def test_gate_only_scores_known_checks_not_precision(self):
        self.gate()
        self.assertEqual(self.measure('accuracy.known_release_checks')['status'], 'pass')
        self.assertEqual(self.measure('accuracy.claim_precision')['status'], 'unmeasured')

    def test_gate_wrong_collection_proof_refused(self):
        gate = self.gate()
        gate['collectionReceiptSha256'] = '0' * 64
        self.pin('gate', gate)
        with self.assertRaisesRegex(ValueError, 'raw coverage'):
            self.report()

    def test_gate_failed_check_is_not_pass(self):
        gate = self.gate()
        gate['checks']['test']['result'] = 'fail'
        self.pin('gate', gate)
        self.assertEqual(self.measure('accuracy.known_release_checks')['status'], 'fail')

    def test_missing_gate_check_refused(self):
        gate = self.gate()
        del gate['checks']['certify:sec']
        self.pin('gate', gate)
        with self.assertRaisesRegex(ValueError, 'checks missing'):
            self.report()

    def test_missing_publication_cannot_accept_rollback(self):
        self.pin('rollback', {'passed': True})
        with self.assertRaisesRegex(ValueError, 'requires publication'):
            self.report()

    def test_operational_success_does_not_imply_data_continuity(self):
        self.gate()
        self.assertEqual(self.measure('durability.data_continuity')['status'], 'unmeasured')
        audit = dict(runId=self.coverage['runId'], appRevision='a' * 40, checkedAt='2026-10-23T12:30:00Z', sourceSnapshotSha256='d' * 64, publishedSnapshotSha256='e' * 64,
                     measures=[dict(id='held_claims', expected=28, retained=14, passed=False)], limitations=['Historical facts held under old policy.'])
        self.manifest['inputs'].pop('gate')
        self.pin('continuity', audit)
        self.assertEqual(self.measure('durability.data_continuity')['status'], 'fail')
        audit['measures'][0]['passed'] = True
        self.pin('continuity', audit)
        with self.assertRaisesRegex(ValueError, 'False continuity pass'):
            self.report()

    def test_rollback_binds_release_and_full_restoration(self):
        self.gate()
        publication = dict(appRevision='a' * 40, publication=dict(githubRunId=123, published=True, releaseId='release', deploymentId='deployment'))
        self.pin('publication', publication)
        rollback = dict(passed=True, drill=dict(current=dict(releaseId='release', deploymentId='deployment'), completedAt='2026-10-23T12:30:00Z', phase='passed', currentBytesVerified=True, productionHeadRemains='release', baselineByteInventoryAvailable=False))
        self.pin('rollback', rollback)
        self.assertEqual(self.measure('durability.rollback_restoration')['status'], 'pass')
        self.assertEqual(self.measure('durability.data_continuity')['status'], 'unmeasured')
        rollback['drill']['currentBytesVerified'] = False
        self.pin('rollback', rollback)
        self.assertEqual(self.measure('durability.rollback_restoration')['status'], 'fail')
        rollback['drill']['current']['releaseId'] = 'other'
        self.pin('rollback', rollback)
        with self.assertRaisesRegex(ValueError, 'release mismatch'):
            self.report()

    def test_breakdowns_preserve_denominator_and_distinguish_registration(self):
        report = self.report()
        overview = report['coverageOverview']
        self.assertEqual((overview['requiredTasks'], overview['verifiedRegisteredBindings'], overview['candidateBindings'], overview['missingBindings']), (557, 275, 28, 254))
        for axis in ('family', 'supplier', 'reason'):
            self.assertEqual(sum(row['requiredTasks'] for row in report['coverageBreakdowns'][axis]), 557)
            self.assertEqual(sum(row['successfulTasks'] for row in report['coverageBreakdowns'][axis]), 121)
        self.assertEqual(len(report['coverageBreakdowns']['supplier']), 74)
        self.assertEqual(len(report['coverageBreakdowns']['domain']), 12)

    def test_markdown_keeps_unknown_and_pins(self):
        output = markdown(self.report())
        self.assertIn('121 / 557', output)
        self.assertIn('unmeasured', output)
        self.assertIn(self.manifest['inputs']['coverage']['sha256'], output)


if __name__ == '__main__':
    unittest.main()
