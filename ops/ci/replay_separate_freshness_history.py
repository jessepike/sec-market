"""Replay D-112 against sealed archive bytes with no live or publication credit."""
import copy
from datetime import timedelta
import json
import os
from pathlib import Path
import sys

from replay_retained_audit import MemoryStore, fingerprint, ROOT
from contracts import digest, instant, plan_run, require, utcnow
from engine import Pipeline
from retained_audit import activate_compatibility, index_for, bounded, legacy_registry
from separation import audit_version
from validation import reconcile, verified_partial_document_facts


def main():
    archive, manifest_pin = Path(sys.argv[1]).resolve(), sys.argv[2]
    before = fingerprint(archive)
    raw = (archive / 'archive-manifest.json').read_bytes()
    require(digest(raw) == manifest_pin, 'Archive manifest pin differs')
    manifest = json.loads(raw)
    for entry in manifest['files']:
        body = (archive / entry['key']).read_bytes()
        require(digest(body) == entry['sha256'] and len(body) == entry['bytes'], 'Archive evidence differs')
    store = MemoryStore(archive / 'state')
    old_ref = store.read('heads/latest-run.json')['receipt']
    old = json.loads(store.get(old_ref))
    old_contract = store.read('contracts/' + old['contractSha256'] + '.json')
    old_plan = store.read('runs/' + old['runId'] + '/plan.json')
    current = json.loads((ROOT / 'contracts/market.json').read_bytes())
    plan = plan_run(current, old_plan['scheduledAt'])
    clock = (instant(old['checkedAt']) + timedelta(seconds=1)).isoformat().replace('+00:00', 'Z')
    legacy_registry()
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
            raise RuntimeError('Offline D112 replay denied ' + event)
    sys.addaudithook(guard)
    old_replayed = reconcile(old_plan, old['receipts'], old_contract, old['checkedAt'], store)
    store.write_once('runs/' + plan['runId'] + '/plan.json', plan)
    store.write_once('contracts/' + digest(current) + '.json', current)

    class ArchivedFetcher:
        reads = 0
        def fetch(self, source, url, previous=None):
            self.reads += 1
            observed = index.latest_observation(source['id'], url)
            require(observed is not None, 'Archived source transport missing')
            return copy.deepcopy(observed)

    fetcher = ArchivedFetcher()
    pipeline = Pipeline(current, store, fetcher, clock=lambda: clock)
    pipeline.audit_index = index
    pipeline.audit_compatibility = activate_compatibility(store, plan, current, index)
    pipeline.force_refresh, pipeline.replay = True, False
    pipeline.model_unavailable = 'OFFLINE_REPLAY_NO_NEW_SOURCE_OR_MODEL_WORK'
    pipeline.prior_receipts = {}
    pipeline.budget_name = 'budget-' + plan['scheduledAt'][:10]
    target_ids = {r['sourceId'] for r in old['receipts'] if r.get('errorCode') == 'HISTORICAL_OR_UNCHANGED_AUDIT_PENDING'}
    receipts, target_tasks = [], []
    for task in plan['tasks']:
        if task['sourceId'] in target_ids:
            receipt = pipeline._task(plan, task)
            target_tasks.append(receipt)
        else:
            receipt = {'runId': plan['runId'], 'taskId': task['taskId'], 'attemptId': digest({'offlineUnexecuted': task['taskId']}),
                       'sourceId': task['sourceId'], 'supplierId': task['supplierId'], 'startedAt': clock, 'completedAt': None,
                       'outcome': 'not_checked', 'discoveryComplete': False, 'observationIds': [], 'newFactIds': [],
                       'validatedFacts': [], 'errorCode': 'OFFLINE_REPLAY_NOT_EXECUTED'}
            source = pipeline.sources.get(task['sourceId'])
            if bounded(source, current):
                receipt.update(retainedAuditVersion=audit_version(current), retainedAuditCompatibility=pipeline.audit_compatibility)
            receipt = pipeline._finish(receipt)
        receipts.append(receipt)
    checked = reconcile(plan, receipts, current, clock, store)
    partial = verified_partial_document_facts(plan, checked, current, clock, store)
    original_facts = {ref['sha256']: ref for receipt in target_tasks for binding in receipt['retainedAuditBindings']
                      for ref in json.loads(store.get(binding['validation']))['factRefs']}
    require(set(original_facts) == {ref['sha256'] for ref in partial}, 'Ordinary retained accepted facts changed during policy migration')
    views = {v['taskId']: v for v in checked['tasks']}
    targets = [{'sourceId': r['sourceId'], 'processingManifest': r['processingManifest'],
                'fullInventoryManifest': r['retainedInventoryManifest'], 'bindings': r['retainedAuditBindings'],
                **{k: views[r['taskId']][k] for k in ('intakeOutcome', 'processingOutcome', 'processing', 'historicalReview')}} for r in target_tasks]
    for task in targets:
        old_audit = json.loads((store.root / ('heads/audit-' + digest(task['sourceId']) + '.json')).read_bytes())
        new_audit = store.read('heads/audit-' + digest(task['sourceId']) + '.json')
        require(old_audit['documents'] == new_audit['documents'], 'Original audit cursor times changed')
    after = fingerprint(archive)
    require(before == after and not denied, 'Archive seal or offline guard changed')
    paths = ['contracts/market.json'] + ['web/scripts/pipeline/' + p + '.py' for p in
             ('contracts', 'engine', 'retained_audit', 'separation', 'selection', 'validation', 'snapshot', 'reporting')]
    paths += ['ops/ci/test_separate_freshness_history.py', 'ops/ci/replay_separate_freshness_history.py']
    print(json.dumps({'schemaVersion': 1, 'kind': 'separate_daily_intake_processing_historical_review_offline_replay',
        'mechanicsOnlyNonAdmitting': True, 'evaluatedAt': utcnow(), 'archivedClockUsed': clock,
        'archive': {'root': str(archive), 'manifestSha256': manifest_pin, 'manifestFiles': len(manifest['files']),
                    'before': before, 'after': after, 'contentAndMtimesUnchanged': before == after},
        'guards': {'networkModelsSubprocessAndDiskMutationsDenied': True, 'deniedAttempts': denied,
                   'actualSourceRequests': 0, 'actualModelCalls': 0, 'actualArchiveWrites': 0,
                   'actualPublicationCalls': 0, 'archivedTransportReads': fetcher.reads,
                   'memoryOnlyMutations': store.mutations, 'indexScans': index.scans},
        'codePins': [{'path': p, 'sha256': digest((ROOT / p).read_bytes())} for p in paths],
        'legacyCombinedCoverage': {'receipt': old_ref, 'contractSha256': digest(old_contract),
                                   **{k: old_replayed[k] for k in ('schemaVersion','successfulTasks','requiredTasks','complete')}},
        'prospectivePolicy': {'contractSha256': digest(current), 'runId': plan['runId'], 'inventorySha256': plan['inventorySha256']},
        'archivedObservationMeasures': {k: checked[k] for k in ('schemaVersion','measure','intake','processing','historicalReview')},
        'targetHistoricalTasks': {'sourceTasks': len(targets), 'inventoryDocuments': sum(t['historicalReview']['inventoryDocuments'] for t in targets),
                                  'reviewedDocuments': sum(t['historicalReview']['reviewedDocuments'] for t in targets),
                                  'pendingDocuments': sum(t['historicalReview']['pendingDocuments'] for t in targets),
                                  'bindings': sum(len(t['bindings']) for t in targets),
                                  'intakePassedAtArchivedClock': sum(t['intakeOutcome'] == 'checked' for t in targets),
                                  'processingStillIncomplete': sum(not t['processing']['complete'] for t in targets)},
        'partialFactReferencesIndependentlyReplayed': len(partial),
        'ordinaryFactRetention': {'exactOriginalReferencesPreserved': True,
                                  'originalFactReferences': list(original_facts.values()), 'currentFactReferences': partial,
                                  'originalFacts': [json.loads(store.get(ref)) for ref in original_facts.values()]},
        'tasks': targets, 'targetReceipts': target_tasks,
        'limitations': ['Only the 17 historical source discoveries were executed using archived transport bytes and original timestamps.',
                        'Every other task stays explicitly uncollected under the new policy; this is not a live 557-task collector run.',
                        'The original 244/557 combined report retains its original policy and meaning.',
                        'No operational credit, publication, new semantic admission or freshness renewal comes from this replay.']}, indent=2))


if __name__ == '__main__':
    main()
