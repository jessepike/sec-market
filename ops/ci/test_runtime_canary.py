"""Offline hosting/archive checks; real archive verification, no source transport."""
import ast
import contextlib
import copy
import fnmatch
import json
import os
import re
from pathlib import Path
import shutil
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import runtime_canary
from archive import GitArchive
from contracts import canonical, digest, plan_run
from fetcher import Fetcher
from storage import LocalStore
from coverage_summary import MEASURE


NOW = '2026-10-23T12:00:00Z'

# Fictional fixtures copied unchanged from the collection/coverage tests.
# Keep this canary suite independent of unrelated collection/parser imports.
def fixture_contract():
    source = {'id': 'generic', 'supplierId': 'fixture', 'family': 'official_announcements',
              'kind': 'rss', 'url': 'https://example.invalid/feed.xml', 'allowedHosts': ['example.invalid'],
              'registration': 'verified', 'required': True, 'maxPages': 2, 'scopePrefixes': ['/release/']}
    sources = [source, {**source, 'id': 'citation', 'kind': 'citation', 'family': 'citation_integrity',
                        'url': 'https://example.invalid/release/one'},
               {**source, 'id': 'sec', 'kind': 'sec_facts', 'family': 'regulatory_filings',
                'url': 'https://example.invalid/facts.json'}]
    return {'schemaVersion': 1, 'version': 'synthetic-collection-mechanics',
            'schedule': {'intervalHours': 24, 'overdueHours': 30, 'reconcileEveryRun': True,
                         'maxWorkers': 3, 'maxFetchesPerRun': 10},
            'model': {'provider': 'codex_subscription', 'allowApiBilling': False, 'maxDocumentsPerRun': 2,
                      'maxCallsPerRun': 3, 'maxDocumentChars': 30000, 'timeoutSeconds': 2},
            'publication': {'enabled': False, 'allowDegradedCoverage': True},
            'suppliers': [{'id': 'fixture', 'name': 'Fixture Vendor', 'kind': 'private', 'aliases': [],
                           'sourceIds': [s['id'] for s in sources], 'requiredCategories': ['funding_valuation'],
                           'requiredFamilies': [s['family'] for s in sources]}], 'sources': sources}


def separated_coverage():
    return {'schemaVersion': 2, 'measure': MEASURE, 'successfulTasks': 1, 'requiredTasks': 1,
            'complete': True, 'gapTaskIds': [],
            'intake': {'measure': MEASURE, 'evaluated': True, 'status': 'collected',
                       'successfulTasks': 1, 'requiredTasks': 1, 'complete': True, 'gapTaskIds': []},
            'processing': {'complete': False, 'inventoryDocuments': 3, 'reviewedDocuments': 1,
                           'pendingDocuments': 2, 'heldDocuments': 1, 'changedDocuments': 2, 'unknownDateDocuments': 1},
            'historicalReview': {'complete': False, 'inventoryDocuments': 20, 'reviewedDocuments': 2,
                                 'pendingDocuments': 18, 'heldDocuments': 1}}


class RuntimeCanaryTests(unittest.TestCase):
    def test_v2_archive_reports_intake_and_pending_reviews_without_live_credit(self):
        coverage = {**self.coverage, **separated_coverage()}
        # Keep the real fixture's required source inventory and blocked intake.
        coverage.update(successfulTasks=0, requiredTasks=self.coverage['requiredTasks'], complete=False,
                        gapTaskIds=[r['taskId'] for r in coverage['receipts']])
        coverage['intake'].update(successfulTasks=0, requiredTasks=coverage['requiredTasks'], complete=False,
                                  gapTaskIds=coverage['gapTaskIds'])
        self.replace_coverage(coverage)
        self.prepare()
        result = self.execute()
        self.assertEqual(result['archivedCoverage']['coverageMeasure'], 'daily_source_intake_v2')
        self.assertFalse(result['archivedCoverage']['processing']['complete'])
        self.assertEqual(result['archivedCoverage']['historicalReview']['pendingDocuments'], 18)
        self.assertFalse(result['coverageCredit'])
        self.assert_no_market_work()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / 'runtime'
        self.repo = self.base / 'repo'
        (self.repo / 'contracts').mkdir(parents=True)
        self.contract = fixture_contract()
        (self.repo / 'contracts/market.json').write_bytes(canonical(self.contract))
        self.original = LocalStore(self.base / 'original')
        self.plan = plan_run(self.contract, NOW)
        run_id = self.plan['runId']
        self.original.write_once(f'runs/{run_id}/plan.json', self.plan)
        receipts = []
        for task in self.plan['tasks']:
            row = {'runId': run_id, 'taskId': task['taskId'], 'sourceId': task['sourceId'],
                   'attemptId': digest(task), 'outcome': 'blocked', 'discoveryComplete': False,
                   'startedAt': NOW, 'completedAt': NOW, 'observationIds': []}
            receipts.append(row)
            self.original.write_once(f"runs/{run_id}/attempts/{row['attemptId']}.json", row)
        self.coverage = {'schemaVersion': 1, 'runId': run_id, 'contractSha256': digest(self.contract),
                         'inventorySha256': self.plan['inventorySha256'], 'checkedAt': NOW,
                         'supplierCount': 1, 'requiredTasks': len(receipts), 'successfulTasks': 0,
                         'complete': False, 'receipts': receipts}
        self.original.compare_and_swap('latest-run', None,
            {'runId': run_id, 'receipt': self.original.put(self.coverage)})
        self.original.compare_and_swap('budget-2026-10-23', None,
            {'fetches': 5500, 'calls': 80, 'documents': 40, 'retained': {'unchanged': True}})
        for name in ('cloud-collector', 'worker-heartbeat', 'dailySnapshot', 'cloud-snapshot', 'source-fictional'):
            self.original.compare_and_swap(name, None, {'sentinel': name})
        self.event = self.base / 'event.json'
        self.event.write_text(json.dumps({'repository': {'full_name': 'jessepike/sec-market', 'private': True}}))
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(patch.dict(os.environ, {'GITHUB_ACTIONS': 'true', 'GITHUB_REPOSITORY': 'jessepike/sec-market',
            'GITHUB_EVENT_PATH': str(self.event), 'GITHUB_RUN_ID': '123'}, clear=True))
        self.stack.enter_context(patch.object(runtime_canary, 'REPO', self.repo))
        self.stack.enter_context(patch.object(runtime_canary, 'utcnow', return_value='2026-10-24T12:00:00Z'))
        self.stack.enter_context(patch.object(runtime_canary.shutil, 'disk_usage', return_value=SimpleNamespace(free=10**12)))
        self.git = self.stack.enter_context(patch.object(runtime_canary.subprocess, 'check_output', return_value='a'*40))
        self.open = self.stack.enter_context(patch.object(GitArchive, '_open', return_value='b'*40))
        self.push = self.stack.enter_context(patch.object(GitArchive, 'push', side_effect=AssertionError('No remote writes')))
        self.fetch = self.stack.enter_context(patch.object(Fetcher, 'fetch', side_effect=AssertionError('No market transport')))

    def prepare(self):
        mirror = self.root / 'mirror'
        shutil.copytree(self.original.root, mirror / 'state')
        self.expected = {str(path.relative_to(mirror / 'state')): path.read_bytes()
                         for path in (mirror / 'state').rglob('*') if path.is_file()}
        manifest = {'schemaVersion': 1, 'files': [
            {'key': 'state/' + name, 'sha256': digest(body), 'bytes': len(body)}
            for name, body in sorted(self.expected.items()) if 'locks' not in Path(name).parts]}
        (mirror / 'archive-manifest.json').write_bytes(canonical(manifest))
        return manifest

    def execute(self):
        # Restoring copies bytes through GitArchive.restore; no pipeline state
        # mutation is allowed before or after reading the restored evidence.
        with patch.object(LocalStore, 'put', side_effect=AssertionError('No object writes')), \
                patch.object(LocalStore, 'write_once', side_effect=AssertionError('No immutable writes')), \
                patch.object(LocalStore, 'compare_and_swap', side_effect=AssertionError('No head writes')):
            return runtime_canary.run(self.root)

    def replace_coverage(self, coverage):
        before = self.original.read('heads/latest-run.json')
        self.original.compare_and_swap('latest-run', before,
            {'runId': coverage['runId'], 'receipt': self.original.put(coverage)})

    def assert_no_market_work(self):
        self.fetch.assert_not_called()
        self.push.assert_not_called()

    def test_exhausted_daily_ledger_has_zero_requests_and_identical_restored_state(self):
        manifest = self.prepare()
        result = self.execute()
        restored = self.root / 'state'
        actual = {str(path.relative_to(restored)): path.read_bytes() for path in restored.rglob('*') if path.is_file()}
        self.assertEqual(actual, self.expected)
        self.assertEqual(result['archive'], {'commit': 'b'*40, 'manifestSha256': digest(manifest), 'files': len(manifest['files'])})
        self.assertTrue(result['runtimeCanaryPassed'])
        self.assertEqual(result['runtimeCanaryScope'], 'private_hosting_archive_integrity')
        self.assertFalse(result['archivedCoverage']['complete'])
        self.assertEqual(result['archivedCoverage']['checkedAt'], NOW)
        self.assertTrue(result['archivedCoverage']['historical'])
        self.assertEqual(result['archivedCoverage']['receiptSha256'], self.original.read('heads/latest-run.json')['receipt']['sha256'])
        self.assert_no_market_work()

    def test_pass_cannot_be_mistaken_for_live_source_connectivity_or_coverage(self):
        self.prepare()
        result = self.execute()
        self.assertEqual(result['sourceProbe'], {'performed': False, 'reason': 'LEASED_COLLECTOR_WORKFLOW_REQUIRED'})
        self.assertEqual(result['marketSourceRequests'], 0)
        self.assertEqual(result['sourceChecksCredited'], 0)
        self.assertEqual(result['qualifiedSources'], 0)
        self.assertFalse(result['coverageCredit'])
        self.assertFalse(result['semanticAdmission'])
        self.assertEqual(result['modelCalls'], 0)
        self.assertFalse(result['subscriptionCredentialsTransferred'])
        self.assertNotIn('httpStatus', result['sourceProbe'])
        self.assertNotIn('checkedAt', result['sourceProbe'])
        self.assertNotIn('validSecResponse', result['sourceProbe'])
        self.assert_no_market_work()

    def test_current_contract_mismatch_fails_after_verified_restore(self):
        self.prepare()
        policy = {**self.contract, 'version': 'changed-current-contract'}
        (self.repo / 'contracts/market.json').write_bytes(canonical(policy))
        with self.assertRaisesRegex(ValueError, 'another source contract'):
            self.execute()
        self.assert_no_market_work()

    def test_missing_coverage_fails_honestly(self):
        (self.original.root / 'heads/latest-run.json').unlink()
        self.prepare()
        with self.assertRaisesRegex(ValueError, 'no collection receipt'):
            self.execute()
        self.assert_no_market_work()

    def test_failed_restore_does_not_run_source_or_state_work(self):
        with patch.object(GitArchive, 'restore', side_effect=RuntimeError('fictional restore failed')):
            with self.assertRaisesRegex(RuntimeError, 'restore failed'):
                self.execute()
        self.assertFalse((self.root / 'state').exists())
        self.assert_no_market_work()

    def test_real_archive_manifest_verification_rejects_corrupted_body(self):
        self.prepare()
        (self.root / 'mirror/state/heads/budget-2026-10-23.json').write_bytes(b'changed after manifest')
        with self.assertRaisesRegex(ValueError, 'integrity mismatch'):
            self.execute()
        self.assertFalse((self.root / 'state').exists())
        self.assert_no_market_work()

    def test_content_addressed_coverage_reference_is_checked(self):
        head = self.original.read('heads/latest-run.json')
        head['receipt']['sha256'] = 'f'*64
        path = self.original.root / 'heads/latest-run.json'
        path.write_bytes(canonical(head))
        self.prepare()
        with self.assertRaisesRegex(ValueError, 'integrity verification'):
            self.execute()
        self.assert_no_market_work()

    def test_changed_deterministic_plan_fails(self):
        plan = copy.deepcopy(self.plan)
        plan['tasks'][0]['required'] = False
        (self.original.root / f"runs/{plan['runId']}/plan.json").write_bytes(canonical(plan))
        self.prepare()
        with self.assertRaisesRegex(ValueError, 'PLAN_DIFFERS'):
            self.execute()
        self.assert_no_market_work()

    def test_changed_attempt_inventory_fails(self):
        coverage = copy.deepcopy(self.coverage)
        coverage['receipts'] = coverage['receipts'][:-1]
        self.replace_coverage(coverage)
        self.prepare()
        with self.assertRaisesRegex(ValueError, 'ATTEMPT_INVENTORY_DIFFERS'):
            self.execute()
        self.assert_no_market_work()

    def test_changed_archived_attempt_fails(self):
        row = self.coverage['receipts'][0]
        (self.original.root / f"runs/{row['runId']}/attempts/{row['attemptId']}.json").write_bytes(canonical({**row, 'outcome': 'updated'}))
        self.prepare()
        with self.assertRaisesRegex(ValueError, 'ATTEMPT_DIFFERS'):
            self.execute()
        self.assert_no_market_work()

    def test_wrong_coverage_denominator_fails(self):
        self.replace_coverage({**self.coverage, 'requiredTasks': 557})
        self.prepare()
        with self.assertRaisesRegex(ValueError, 'COVERAGE_INVENTORY_DIFFERS'):
            self.execute()
        self.assert_no_market_work()

    def test_wrong_private_hosting_context_starts_no_archive_restore(self):
        for event in ({'repository': {'full_name': 'jessepike/sec-market', 'private': False}},
                      {'repository': {'full_name': 'other/repo', 'private': True}}, {}):
            with self.subTest(event=event):
                self.event.write_text(json.dumps(event))
                with self.assertRaises(ValueError):
                    self.execute()
        self.open.assert_not_called()
        self.git.assert_not_called()
        self.assert_no_market_work()

    def test_non_github_or_wrong_repository_starts_no_archive_restore(self):
        for update in ({'GITHUB_ACTIONS': 'false'}, {'GITHUB_REPOSITORY': 'other/repo'}):
            with self.subTest(update=update), patch.dict(os.environ, update), self.assertRaises(ValueError):
                self.execute()
        self.open.assert_not_called()
        self.assert_no_market_work()

    def test_failure_receipt_never_claims_source_work_or_copies_remote_error_text(self):
        result = runtime_canary.failure(RuntimeError('remote response could be sensitive'))
        self.assertFalse(result['runtimeCanaryPassed'])
        self.assertEqual(result['reason'], 'RuntimeError')
        self.assertEqual(result['marketSourceRequests'], 0)
        self.assertFalse(result['sourceProbe']['performed'])
        self.assertFalse(result['coverageCredit'])
        self.assertFalse(result['semanticAdmission'])
        self.assertFalse(result['publicationAttempted'])
        self.assertNotIn('sensitive', json.dumps(result))

    def test_workflow_wording_and_permissions_describe_archive_only_scope(self):
        path = Path(__file__).resolve().parents[2] / '.github/workflows/subscription-runtime-canary.yml'
        workflow = path.read_text()
        self.assertIn('without source requests', workflow)
        self.assertIn('contents: read', workflow)
        self.assertNotIn('contents: write', workflow)
        self.assertNotIn('secrets.', workflow)
        self.assertNotIn('probe a source', workflow)

    def test_workflow_trigger_covers_actual_local_import_closure_and_contract(self):
        root = Path(__file__).resolve().parents[2]
        workflow_path = '.github/workflows/subscription-runtime-canary.yml'
        workflow = (root / workflow_path).read_text()
        push = workflow.split('  workflow_dispatch:', 1)[0]
        patterns = re.findall(r"^      - '([^']+)'$", push, re.MULTILINE)
        self.assertTrue(patterns)
        pending = [root / 'ops/ci' / name for name in
                   ('runtime_canary.py', 'auth_store.py', 'test_runtime_canary.py', 'test_auth_store.py')]
        closure = set()
        while pending:
            path = pending.pop()
            if path in closure:
                continue
            closure.add(path)
            for node in ast.walk(ast.parse(path.read_text())):
                names = ([node.module] if isinstance(node, ast.ImportFrom) else
                         [alias.name for alias in node.names] if isinstance(node, ast.Import) else [])
                for name in names:
                    for directory in ('ops/ci', 'web/scripts/pipeline'):
                        dependency = root / directory / (name.split('.')[0] + '.py')
                        if dependency.exists():
                            pending.append(dependency)
        required = {path.relative_to(root).as_posix() for path in closure}
        required.update(('contracts/market.json', workflow_path))
        self.assertEqual(set(patterns), required)
        for unrelated in ('ops/ci/collect.py', 'ops/ci/test_correction_collection.py',
                          'web/scripts/pipeline/engine.py', 'web/src/pages/index.astro'):
            self.assertFalse(any(fnmatch.fnmatchcase(unrelated, pattern) for pattern in patterns), unrelated)

    def test_workflow_runs_only_the_two_focused_fictional_suites_before_native_restore(self):
        root = Path(__file__).resolve().parents[2]
        workflow = (root / '.github/workflows/subscription-runtime-canary.yml').read_text()
        commands = re.findall(r'^          (python3 -m unittest .+)$', workflow, re.MULTILINE)
        self.assertEqual(commands, [
            "python3 -m unittest discover -s ops/ci -p 'test_auth_store.py' -v",
            "python3 -m unittest discover -s ops/ci -p 'test_runtime_canary.py' -v"])
        self.assertLess(workflow.index(commands[-1]), workflow.index('python3 ops/ci/runtime_canary.py'))


if __name__ == '__main__':
    unittest.main()
