"""Portable cross-day snapshot proof exercised through the public JS verifier."""
import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

import test_retained_audit_rebinding as fixtures
from contracts import canonical, digest
from reporting import inventory
from separation import MODE
from snapshot import build_snapshot

ROOT = Path(__file__).resolve().parents[2]


class CrossDaySnapshotInventoryTests(unittest.TestCase):
    def setUp(self):
        self.f = fixtures.RetainedAuditTests()
        self.f.setUp()
        self.addCleanup(self.f.doCleanups)
        self.f.contract['version'] = 'market-daily-v2'
        self.f.contract['collection']['mode'] = MODE
        self.f.contract['model']['maxDocumentsPerRun'] = 1
        self.f.contract['suppliers'][0]['requiredFamilies'].append('independent_media')
        self.f.time = '2026-10-24T23:50:00Z'
        other = 'https://example.invalid/releases/two'
        self.f.feed([fixtures.URL, other])
        self.f.fetcher.pages[other] = self.f.fetcher.pages[fixtures.URL] + b'<!--second-->'
        self.coverage = self.f.run_pipeline(fixtures.FakeAgent())
        self.plan = self.f.store.read('runs/' + self.coverage['runId'] + '/plan.json')
        self.day_snapshot = self.snapshot(self.f.time)

    def snapshot(self, at):
        return build_snapshot(self.f.contract, self.plan, self.coverage, self.f.store, at)

    def verify(self, snapshot):
        # Seal each fixture honestly so negative cases reach the real row verifier.
        data = copy.deepcopy(snapshot)
        data.pop('snapshotSha256', None)
        data['snapshotSha256'] = digest(data)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            web = root / 'web'
            generated = web / 'src/data/generated'
            generated.mkdir(parents=True)
            (root / 'contracts').mkdir()
            (root / 'contracts/market.json').write_bytes(canonical(self.f.contract))
            raw = canonical(data)
            (generated / 'dailyMarket.json').write_bytes(raw)
            (generated / 'dailyMarket.seal.json').write_bytes(canonical({
                'fileSha256': digest(raw), 'runId': data['runId'], 'contractSha256': data['contractSha256']}))
            script = ('import {verifyDaily} from ' + json.dumps((ROOT / 'web/scripts/verify-daily.mjs').as_uri()) +
                '; try { console.log(JSON.stringify(verifyDaily(process.argv[1]))) }'
                ' catch(e) { console.error(e.message); process.exitCode=2 }')
            return subprocess.run(['node', '--input-type=module', '-e', script, str(web)],
                                  text=True, capture_output=True)

    def test_cross_utc_snapshot_keeps_original_receipt_rows_and_passes_actual_js_verifier(self):
        original_observations = {oid: copy.deepcopy(self.f.store.read('observations/' + oid + '.json'))
            for receipt in self.coverage['receipts'] for oid in receipt.get('observationIds', [])}
        rebuilt = self.snapshot('2026-10-25T00:23:00Z')
        result = self.verify(rebuilt)
        self.assertEqual(result.returncode, 0, result.stderr)
        rows = rebuilt['coverage']['sources']
        self.assertEqual({r['taskId'] for r in rows}, {r['taskId'] for r in self.plan['tasks']})
        checked = [r for r in rows if r['required'] and r['outcome'] == 'checked']
        gaps = [r['taskId'] for r in rows if r['required'] and r['outcome'] != 'checked']
        self.assertEqual(len(checked), self.coverage['successfulTasks'])
        self.assertEqual(len(checked), 1)
        self.assertEqual(len(rows), 2)
        self.assertEqual(set(gaps), set(self.coverage['gapTaskIds']))
        self.assertEqual(rows, self.day_snapshot['coverage']['sources'])
        receipts = {r['taskId']: r for r in self.coverage['receipts']}
        for row in rows:
            self.assertEqual(row['lastCheckedAt'], receipts[row['taskId']]['completedAt'])
        for field in ('processing', 'historicalReview', 'gapTaskIds', 'scheduledAt', 'lastCollectionAt', 'validUntil'):
            self.assertEqual(rebuilt['coverage'][field], self.day_snapshot['coverage'][field])
        for field in ('events', 'evidence', 'reviewQueue', 'factProvenance'):
            self.assertEqual(rebuilt[field], self.day_snapshot[field])
        self.assertFalse(rebuilt['coverage']['processing']['complete'])
        self.assertEqual(rebuilt['coverage']['processing']['pendingDocuments'], 1)
        for oid, value in original_observations.items():
            self.assertEqual(self.f.store.read('observations/' + oid + '.json'), value)

    def test_same_day_rows_and_verifier_result_are_unchanged(self):
        rows = inventory(self.f.contract, self.f.time, self.coverage)
        self.assertEqual(self.day_snapshot['coverage']['sources'], rows)
        result = self.verify(self.day_snapshot)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_former_gate_day_join_is_rejected_by_unchanged_verifier(self):
        bad = copy.deepcopy(self.day_snapshot)
        bad['coverage']['sources'] = inventory(self.f.contract, '2026-10-25T00:23:00Z', self.coverage)
        result = self.verify(bad)
        self.assertEqual(result.returncode, 2)
        self.assertIn('completion differs from its source receipts', result.stderr)

    def test_inconsistent_gap_identity_checked_count_and_review_rows_still_reject(self):
        def gap_id(data):
            next(row for row in data['coverage']['sources'] if row['outcome'] != 'checked')['taskId'] = 'forged-gap'
        def checked_count(data):
            row = next(row for row in data['coverage']['sources'] if row['outcome'] == 'checked')
            row['outcome'] = row['intakeOutcome'] = 'not_checked'
        def review_summary(data):
            data['coverage']['sources'][0]['processing']['pendingDocuments'] += 1
        for mutate in (gap_id, checked_count, review_summary):
            with self.subTest(mutate=mutate.__name__):
                bad = copy.deepcopy(self.day_snapshot)
                mutate(bad)
                self.assertEqual(self.verify(bad).returncode, 2)

    def test_original_task_day_does_not_bypass_current_freshness_expiry(self):
        with self.assertRaisesRegex(ValueError, 'stale|future|expired'):
            self.snapshot('2026-10-26T06:00:01Z')


if __name__ == '__main__':
    unittest.main()
