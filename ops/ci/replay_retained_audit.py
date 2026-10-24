"""Offline actual-archive mechanics replay; all new state is memory-only."""
import copy
from contextlib import nullcontext
from datetime import timedelta
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'web/scripts/pipeline'))
from contracts import canonical, digest, instant, utcnow, require
from engine import Pipeline
from retained_audit import activate_compatibility, index_for, legacy_registry, replay_binding
from storage import LocalStore
from validation import reconcile, verified_partial_document_facts


class MemoryStore(LocalStore):
    def __init__(self, root):
        self.root = root
        self.memory = {}
        self.mutations = 0

    def read(self, key):
        if key in self.memory:
            return json.loads(self.memory[key])
        return super().read(key)

    def get(self, ref):
        raw = self.memory.get(ref['key'])
        if raw is None:
            return super().get(ref)
        require(digest(raw) == ref['sha256'] and len(raw) == ref['bytes'], 'Memory evidence integrity differs')
        return raw

    def write_once(self, key, body):
        raw = body if isinstance(body, bytes) else canonical(body)
        prior = self.memory.get(key)
        if prior is None and self._path(key).exists():
            prior = self._path(key).read_bytes()
        require(prior is None or prior == raw, 'Memory immutable object collision')
        self.memory[key] = raw
        self.mutations += 1

    def compare_and_swap(self, name, expected, value):
        require(self.read('heads/' + name + '.json') == expected, 'Memory CAS differs')
        self.memory['heads/' + name + '.json'] = canonical(value)
        self.mutations += 1

    def lock(self, name, blocking=False):
        return nullcontext()


def fingerprint(root):
    content, times, directories = [], [], []
    for path in sorted(root.rglob('*')):
        key = path.relative_to(root).as_posix()
        if path.is_file():
            content.append([key, digest(path.read_bytes())])
            times.append([key, path.stat().st_mtime_ns])
        elif path.is_dir():
            directories.append([key, path.stat().st_mtime_ns])
    return {'files': len(content), 'contentSha256': digest(content), 'fileMtimeSha256': digest(times),
            'directories': len(directories), 'directoryMtimeSha256': digest(directories)}


def main():
    archive = Path(sys.argv[1]).resolve()
    manifest_pin = sys.argv[2]
    before = fingerprint(archive)
    raw = (archive / 'archive-manifest.json').read_bytes()
    require(digest(raw) == manifest_pin, 'Archive manifest pin differs')
    manifest = json.loads(raw)
    for entry in manifest['files']:
        body = (archive / entry['key']).read_bytes()
        require(len(body) == entry['bytes'] and digest(body) == entry['sha256'], 'Archive file differs')
    store = MemoryStore(archive / 'state')
    coverage_ref = store.read('heads/latest-run.json')['receipt']
    old = json.loads(store.get(coverage_ref))
    plan = store.read('runs/' + old['runId'] + '/plan.json')
    contract = store.read('contracts/' + old['contractSha256'] + '.json')
    clock = (instant(old['checkedAt']) + timedelta(seconds=1)).isoformat().replace('+00:00', 'Z')
    # Load the fixed source-controlled migration input before installing disk guards.
    registry = legacy_registry()
    index = index_for(store)
    denied = []

    def guard(event, args):
        mutation = event in ('os.remove', 'os.rename', 'os.mkdir', 'os.rmdir', 'os.link', 'os.symlink',
                             'os.chmod', 'os.chown', 'os.utime', 'os.truncate')
        if event == 'open':
            mode, flags = args[1:3]
            mutation = (isinstance(mode, str) and any(c in mode for c in 'wax+')) or bool(
                isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
        if mutation or event.startswith(('socket.', 'subprocess.')) or event in ('os.system', 'os.posix_spawn'):
            denied.append(event)
            raise RuntimeError('Offline replay denied ' + event)

    sys.addaudithook(guard)

    class ArchivedFetcher:
        reads = 0

        def fetch(self, source, url, previous=None):
            self.reads += 1
            observed = index.latest_observation(source['id'], url)
            require(observed is not None, 'Archived transport missing')
            return copy.deepcopy(observed)

    fetcher = ArchivedFetcher()
    pipeline = Pipeline(contract, store, fetcher, clock=lambda: clock)
    pipeline.audit_index = index
    pipeline.audit_compatibility = activate_compatibility(store, plan, contract, index)
    pipeline.force_refresh = True
    pipeline.replay = False
    pipeline.model_unavailable = 'OFFLINE_REPLAY_NO_NEW_MODEL_OR_SOURCE_WORK'
    pipeline.prior_receipts = {}
    pipeline.budget_name = 'budget-' + plan['scheduledAt'][:10]
    old_tasks = [r for r in old['receipts'] if r.get('errorCode') == 'HISTORICAL_OR_UNCHANGED_AUDIT_PENDING']
    replacements, tasks = {}, []
    for original in old_tasks:
        task = next(t for t in plan['tasks'] if t['taskId'] == original['taskId'])
        audit_key = 'heads/audit-' + digest(original['sourceId']) + '.json'
        audit_before = copy.deepcopy(store.read(audit_key))
        receipt = pipeline._task(plan, task)
        replacements[receipt['taskId']] = receipt
        cursor_same = store.read(audit_key)['documents'] == audit_before['documents']
        require(cursor_same, 'Retained reuse changed cursor times')
        tasks.append({'sourceId': receipt['sourceId'], 'attemptId': receipt['attemptId'],
                      'outcome': receipt['outcome'], 'errorCode': receipt['errorCode'],
                      'fullInventory': receipt.get('retainedInventoryManifest'),
                      'fullInventoryURLs': len(json.loads(store.get(receipt['retainedInventoryManifest']))['items'])
                          if receipt.get('retainedInventoryManifest') else None,
                      'retainedBindings': receipt.get('retainedAuditBindings', []),
                      'retainedBindingCount': len(receipt.get('retainedAuditBindings', [])),
                      'unbound': receipt.get('retainedAuditUnbound', []),
                      'pendingDocuments': receipt.get('pendingDocuments', 0),
                      'pendingManifest': receipt.get('pendingManifest'),
                      'sourceAuditCursorTimesPreserved': cursor_same})
    receipts = [replacements.get(r['taskId'], r) for r in old['receipts']]
    checked = reconcile(plan, receipts, contract, clock, store)
    partial = verified_partial_document_facts(plan, checked, contract, clock, store)
    now = utcnow()
    eligible = []
    for task in tasks:
        for binding in task['retainedBindings']:
            try:
                replay_binding(binding, contract, task['sourceId'], now, store, index)
                result = {'eligibleAtEvaluation': True}
            except ValueError as exc:
                result = {'eligibleAtEvaluation': False, 'reason': str(exc)}
            eligible.append({'sourceId': task['sourceId'], 'url': binding['url'], **result})
    after = fingerprint(archive)
    require(before == after and not denied, 'Archive changed or denied call attempted')
    pins = ['web/scripts/pipeline/' + name for name in ('retained_audit.py', 'retained_audit_legacy.json', 'engine.py', 'validation.py')]
    pins += ['ops/ci/' + name for name in ('test_retained_audit_rebinding.py', 'test_compressed_article_input.py', 'replay_retained_audit.py')]
    print(json.dumps({'schemaVersion': 1, 'kind': 'actual_retained_audit_engine_and_reconciliation_offline_replay',
        'mechanicsOnlyNonAdmitting': True, 'evaluatedAt': now, 'archivedClockUsed': clock,
        'archive': {'root': str(archive), 'manifestSha256': manifest_pin, 'manifestFiles': len(manifest['files']),
                    'before': before, 'after': after, 'contentAndMtimesUnchanged': before == after},
        'legacyMigration': {'receipts': len(registry), 'registrySha256': digest((ROOT / 'web/scripts/pipeline/retained_audit_legacy.json').read_bytes())},
        'guards': {'networkModelsSubprocessAndDiskMutationsDenied': True, 'deniedAttempts': denied,
                   'actualSourceRequests': 0, 'actualModelCalls': 0, 'actualArchiveWrites': 0,
                   'archivedTransportReads': fetcher.reads, 'memoryOnlyMutations': store.mutations, 'indexScans': index.scans},
        'codePins': [{'path': p, 'sha256': digest((ROOT / p).read_bytes())} for p in pins],
        'coverage': {'originalReceipt': coverage_ref, 'contractSha256': old['contractSha256'],
                     'successfulTasks': checked['successfulTasks'], 'requiredTasks': checked['requiredTasks'],
                     'complete': checked['complete'], 'unchanged': all(checked[k] == old[k] for k in ('successfulTasks','requiredTasks','complete'))},
        'summary': {'actualSourceTasksReplayed': len(tasks), 'actualFullInventoryURLs': sum(t['fullInventoryURLs'] or 0 for t in tasks),
                    'actualRetainedBindings': sum(t['retainedBindingCount'] for t in tasks),
                    'actualUnboundDocuments': sum(len(t['unbound']) for t in tasks),
                    'actualGenuinePendingURLs': sum(t['pendingDocuments'] for t in tasks),
                    'historicalTasksStillIncomplete': sum(t['outcome'] not in ('updated','checked_no_change') for t in tasks),
                    'partialFactReferencesIndependentlyReplayed': len(partial),
                    'retainedBindingsEligibleAtEvaluationTime': sum(t['eligibleAtEvaluation'] for t in eligible),
                    'sourceAuditCursorsUnchanged': all(t['sourceAuditCursorTimesPreserved'] for t in tasks)},
        'tasks': tasks, 'evaluationTimeBindingEligibility': eligible,
        'limitations': ['Archive-only transport and memory-only new receipts are mechanical evidence, not semantic admission or a live collector run.',
                        'The clock is pinned one second after archived coverage; actual-time eligibility is reported separately.',
                        'Existing work bounds and freshness remain unchanged; historical incomplete tasks cannot earn coverage.']}, indent=2))


if __name__ == '__main__':
    main()
