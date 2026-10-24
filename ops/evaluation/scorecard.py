"""Offline, evidence-bound operational scorecard. No network, model or state writes."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
from collections import Counter, defaultdict

PIPELINE = Path(__file__).resolve().parents[2] / 'web/scripts/pipeline'
sys.path.insert(0, str(PIPELINE))
from contracts import digest, instant, plan_run, require, valid_hash  # noqa: E402


SEPARATE_MODE = 'daily_intake_with_separate_history'
SEPARATE_MEASURE = 'daily_source_intake_v2'


def separate_progress(value, kind):
    fields = ('inventoryDocuments', 'reviewedDocuments', 'pendingDocuments', 'heldDocuments')
    if kind == 'processing':
        fields += ('changedDocuments', 'unknownDateDocuments')
    require(isinstance(value, dict) and value.get('evaluated') is not False,
            'Uncollected preview progress is not a collector receipt')
    require(all(type(value.get(field)) is int and value[field] >= 0 for field in fields),
            'Invalid separate progress counter')
    require(value['inventoryDocuments'] == value['reviewedDocuments'] + value['pendingDocuments']
            and value['heldDocuments'] <= value['reviewedDocuments'], 'Separate review partition differs')
    if kind == 'processing':
        require(value['changedDocuments'] + value['unknownDateDocuments'] <= value['inventoryDocuments'],
                'Separate document classifications overlap or exceed inventory')
    complete = value['pendingDocuments'] == 0 and (kind != 'processing' or value['heldDocuments'] == 0)
    require(type(value.get('complete')) is bool and value['complete'] == complete,
            'False separate progress completeness')
    return {field: value[field] for field in fields}


def separate_views(coverage, plan, receipts):
    require(coverage.get('schemaVersion') == 2 and coverage.get('measure') == SEPARATE_MEASURE,
            'Separate intake coverage schema or measure differs')
    require(coverage.get('intake', {}).get('evaluated') is True,
            'Separate intake is not a collected observation')
    rows = coverage.get('tasks')
    require(isinstance(rows, list) and all(isinstance(row, dict) for row in rows), 'Separate task views missing')
    require(len(rows) == len({row['taskId'] for row in rows}) == len(plan['tasks']), 'Separate task inventory differs')
    views = {row['taskId']: row for row in rows}
    require(set(views) == {task['taskId'] for task in plan['tasks']}, 'Separate task inventory differs')
    for task in plan['tasks']:
        row, receipt = views[task['taskId']], receipts[task['taskId']]
        require('sourceId' in row and 'supplierId' in row,
                'Separate task subject fields missing')
        require(row.get('sourceId') == task['sourceId'] and row.get('supplierId') == task['supplierId'],
                'Separate task view subject differs')
        require(row.get('intakeOutcome') in ('checked', 'not_checked', 'blocked', 'failed')
                and row.get('outcome') == row['intakeOutcome'], 'Separate intake outcome differs')
        require(row.get('processingOutcome') == receipt['outcome'], 'Separate processing outcome differs')
        require(row.get('intakeErrorCode') is None if row['intakeOutcome'] == 'checked'
                else isinstance(row.get('intakeErrorCode'), str) and bool(row['intakeErrorCode']),
                'Separate intake error differs')
        for kind in ('processing', 'historicalReview'):
            separate_progress(row.get(kind), kind)
    summaries = {}
    for kind in ('processing', 'historicalReview'):
        summary = separate_progress(coverage.get(kind), kind)
        for field, count in summary.items():
            require(count == sum(row[kind][field] for row in rows), 'Separate aggregate differs from task views')
        require(coverage[kind]['complete'] == all(row[kind]['complete'] for row in rows),
                'Separate aggregate completeness differs')
        summaries[kind] = summary
    expected_intake = {key: coverage[key] for key in
                       ('successfulTasks', 'requiredTasks', 'gapTaskIds', 'complete')}
    expected_intake.update(measure=SEPARATE_MEASURE, evaluated=True, status='collected')
    require(coverage.get('intake') == expected_intake,
            'Separate intake aliases differ')
    return views, summaries


def load_pinned(entry, base):
    require(set(entry) == {'path', 'sha256'}, 'Pin requires path and raw sha256')
    require(valid_hash(entry['sha256']), 'Invalid input hash')
    path = Path(entry['path'])
    path = path if path.is_absolute() else base / path
    raw = path.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == entry['sha256'], 'Input hash mismatch: ' + str(path))
    return json.loads(raw)


def evaluate(manifest, base=Path('.')):
    require(manifest.get('schemaVersion') == 1, 'Unknown manifest schema')
    require(set(manifest) == {'schemaVersion', 'evaluatedAt', 'appRevision', 'inputs'}, 'Manifest schema mismatch')
    now = instant(manifest['evaluatedAt'])
    require(__import__('re').fullmatch('[a-f0-9]{40}', manifest['appRevision']) is not None, 'Invalid app revision')
    pins = manifest['inputs']
    require({'contract', 'coverage'} <= set(pins) <= {'contract', 'coverage', 'gate', 'collection', 'publication', 'rollback', 'continuity', 'claimAudit'}, 'Unknown/missing input')
    data = {name: load_pinned(entry, base) for name, entry in pins.items()}
    contract, coverage = data['contract'], data['coverage']
    checked = instant(coverage['checkedAt'])
    require(checked <= now, 'Coverage is future dated')
    plan = plan_run(contract, coverage['checkedAt'])
    require(coverage['contractSha256'] == digest(contract), 'Coverage policy mismatch')
    require(coverage['runId'] == plan['runId'] and coverage['inventorySha256'] == plan['inventorySha256'], 'Coverage inventory identity mismatch')
    tasks = {t['taskId']: t for t in plan['tasks'] if t['required']}
    receipts = coverage['receipts']
    require(len(receipts) == len({r['taskId'] for r in receipts}), 'Duplicate receipt')
    require({r['taskId'] for r in receipts} == {t['taskId'] for t in plan['tasks']}, 'Receipt inventory mismatch')
    require(coverage['requiredTasks'] == len(tasks) and coverage['supplierCount'] == len(contract['suppliers']), 'Coverage denominator mismatch')
    separated = contract.get('collection', {}).get('mode') == SEPARATE_MODE
    views, progress = (separate_views(coverage, plan, {r['taskId']: r for r in receipts}) if separated else ({}, {}))
    if not separated:
        require(coverage.get('schemaVersion', 1) != 2 and coverage.get('measure') != SEPARATE_MEASURE,
                'Separate intake receipt used with legacy policy')
    good = set()
    for receipt in receipts:
        task = next(t for t in plan['tasks'] if t['taskId'] == receipt['taskId'])
        require(receipt['runId'] == plan['runId'] and receipt['sourceId'] == task['sourceId'] and receipt['supplierId'] == task['supplierId'], 'Receipt identity mismatch')
        require(instant(receipt['completedAt']) <= checked, 'Future task completion')
        success = views[receipt['taskId']]['intakeOutcome'] == 'checked' if separated else receipt['outcome'] in ('updated', 'checked_no_change')
        if separated:
            # The separate intake label must be supported by the raw discovery receipt.
            # Processing can be incomplete, but it cannot manufacture or conceal intake.
            discovered = receipt.get('discoveryComplete')
            observation_ids = receipt.get('observationIds')
            require(type(discovered) is bool and isinstance(observation_ids, list)
                    and all(isinstance(value, str) and value for value in observation_ids),
                    'Invalid raw discovery receipt')
            if success:
                require(discovered and bool(observation_ids),
                        'Checked intake lacks complete raw discovery')
        if success:
            require(receipt.get('discoveryComplete') is True and bool(receipt.get('observationIds')), 'Unsupported success receipt')
            if separated:
                source = next((source for source in contract['sources'] if source['id'] == task['sourceId']), None)
                require(source and source['registration'] == 'verified', 'Unverified source claims intake success')
            if receipt['taskId'] in tasks:
                good.add(receipt['taskId'])
    require(type(coverage['successfulTasks']) is int and coverage['successfulTasks'] == len(good), 'Success counter differs from receipts')
    require(set(coverage['gapTaskIds']) == set(tasks) - good and len(coverage['gapTaskIds']) == len(set(coverage['gapTaskIds'])), 'Gap inventory mismatch')
    require(type(coverage['complete']) is bool and coverage['complete'] == (len(good) == len(tasks)), 'False complete claim')
    revision = manifest['appRevision']
    measures = []

    def add(identifier, axis, status, numerator=None, denominator=None, evidence=(), limitation='', observed_at=None, **extra):
        require(status in ('pass', 'fail', 'unmeasured'), 'Invalid status')
        measures.append(dict(id=identifier, axis=axis, status=status, numerator=numerator, denominator=denominator,
                             observedAt=observed_at, evidence=list(evidence), limitations=limitation, **extra))

    add('coverage.required_tasks', 'coverage', 'pass' if coverage['complete'] else 'fail', len(good), len(tasks), ['coverage', 'contract'],
        ('Fresh source intake only; processing and historical review are separate. No complete-event or all-site accuracy claim.'
         if separated else 'Receipt-level source checks; does not establish every historical claim is accurate.'), coverage['checkedAt'],
        **({'label': 'Daily source intake'} if separated else {}))
    if separated:
        for kind, label in (('processing', 'Observed document processing'), ('historicalReview', 'Retained historical review')):
            value = progress[kind]
            observed = value['inventoryDocuments'] > 0
            add('coverage.' + kind, 'coverage', ('pass' if coverage[kind]['complete'] else 'fail') if observed else 'unmeasured',
                value['reviewedDocuments'] if observed else None, value['inventoryDocuments'] if observed else None,
                ['coverage', 'contract'], 'Source/URL inventory; reviewed documents can contain held claims. Pinned counters are not source-body authentication or an accuracy estimate.',
                coverage['checkedAt'], label=label, **value)
    sources = {s['id']: s for s in contract['sources']}
    sec = {tid for tid, task in tasks.items() if sources.get(task['sourceId'], {}).get('kind') in ('sec_facts', 'sec_submissions', 'sec_documents')}
    add('coverage.sec_tasks', 'coverage', 'pass' if sec and sec <= good else 'fail', len(sec & good), len(sec), ['coverage', 'contract'],
        'SEC source checks are distinct from the independent SEC claim gate.', coverage['checkedAt'])
    age = (now - checked).total_seconds() / 3600
    add('freshness.collection_receipt', 'freshness', 'pass' if age <= contract['schedule']['overdueHours'] else 'fail', evidence=['coverage', 'contract'],
        limitation='Collection check age only. This evaluator does not replay archived observation bodies.', observed_at=coverage['checkedAt'],
        ageHours=age, maximumAgeHours=contract['schedule']['overdueHours'])
    add('freshness.all_required_checks', 'freshness', 'pass' if coverage['complete'] and age <= contract['schedule']['overdueHours'] else 'fail', len(good), len(tasks), ['coverage', 'contract'],
        ('Fresh intake across the declared roster only; pending processing and history remain separately visible.'
         if separated else 'Incomplete required source checks prevent a full-roster freshness pass.'), coverage['checkedAt'],
        **({'label': 'Fresh intake across the declared roster'} if separated else {}))
    gate = data.get('gate')
    if gate:
        require(gate['runId'] == coverage['runId'] and gate['appRevision'] == revision and gate['contractSha256'] == digest(contract), 'Gate identity mismatch')
        require(gate['collectionReceiptSha256'] == pins['coverage']['sha256'], 'Gate covers different raw coverage bytes')
        require(type(gate['githubRunId']) is int and gate['githubRunId'] > 0 and valid_hash(gate['artifactSha256']), 'Gate lacks artifact/run identity')
        checks = gate['checks']
        require({'certify:sec', 'refresh:edgar', 'refresh:filing-events', 'test'} <= set(checks), 'Gate checks missing')
        require(all(valid_hash(c['logSha256']) for c in checks.values()), 'Missing check log hash')
        passing = sum(c['result'] == 'pass' for c in checks.values())
        passed = gate['result'] == 'pass' and passing == len(checks)
        require(type(gate['executedTests']) is int and gate['executedTests'] > 0, 'Missing test denominator')
        add('accuracy.known_release_checks', 'accuracy', 'pass' if passed else 'fail', passing, len(checks), ['gate'],
            'Pinned gate receipt reports known checks, including SEC recomputation. Tests do not estimate all-site precision/recall.', executedTests=gate['executedTests'])
    else:
        add('accuracy.known_release_checks', 'accuracy', 'unmeasured', limitation='No pinned gate receipt supplied.')
    claim_audit = data.get('claimAudit')
    if claim_audit:
        require(claim_audit.get('schemaVersion') == 1 and claim_audit.get('kind') == 'published_claim_review_binding_report', 'Unknown claim-audit schema')
        require(claim_audit.get('appRevision') == revision, 'Claim audit covers another application')
        require(claim_audit.get('bindingChecksPassed') is True, 'Claim audit lacks verified source/dataset bindings')
        require(instant(claim_audit['evaluatedAt']) <= now, 'Future claim audit')
        audit_pins = claim_audit['inputPins']
        require(set(audit_pins) >= {'inventory', 'reviews'} and set(audit_pins['reviews']) == {'events_a_m', 'events_n_z', 'supplier_fields'}, 'Claim-audit evidence pins missing')
        for pin in [audit_pins['inventory'], *audit_pins['reviews'].values()]:
            require(set(pin) == {'path', 'sha256'} and isinstance(pin['path'], str) and valid_hash(pin['sha256']), 'Invalid claim-audit evidence pin')
        rows = claim_audit['records']
        allowed = {'supported', 'contradicted', 'insufficient', 'primary_source_missing'}
        require(isinstance(rows, list) and rows and len(rows) == len({row['id'] for row in rows}), 'Missing/duplicate reviewed record')
        require(all(row['verdict'] in allowed for row in rows), 'Unknown reviewed verdict')
        require(all(row['partition'] in audit_pins['reviews'] for row in rows), 'Unknown review partition')
        require(type(claim_audit['inventoryCount']) is int and type(claim_audit['reviewedCount']) is int
                and claim_audit['inventoryCount'] == claim_audit['reviewedCount'] == len(rows), 'Reviewed inventory mismatch')
        counts = Counter(row['verdict'] for row in rows)
        require(set(claim_audit['verdictCounts']) == allowed and all(type(value) is int for value in claim_audit['verdictCounts'].values())
                and claim_audit['verdictCounts'] == {key: counts[key] for key in allowed}, 'Reviewed verdict counters differ')
        add('accuracy.reviewed_records', 'accuracy', 'pass', len(rows), len(rows), ['claimAudit'],
            'Fixed audit inventory completed; this is review coverage, not the number of accurate records.', claim_audit['evaluatedAt'], verdictCounts=claim_audit['verdictCounts'])
        add('accuracy.known_contradictions', 'accuracy', 'fail' if counts['contradicted'] else 'pass', counts['contradicted'], 0, ['claimAudit'],
            'Known contradicting records in this fixed audit; zero required. Other records may still lack sufficient support. No whole-site precision/recall estimate.',
            claim_audit['evaluatedAt'], maximumCount=0, recordIds=[row['id'] for row in rows if row['verdict'] == 'contradicted'])
    else:
        add('accuracy.reviewed_records', 'accuracy', 'unmeasured', limitation='No pinned published-claim audit supplied.')
        add('accuracy.known_contradictions', 'accuracy', 'unmeasured', limitation='No pinned published-claim audit supplied; passing release tests do not establish absence of factual errors.')
    for kind in ('claim_precision', 'eligible_event_recall'):
        add('accuracy.' + kind, 'accuracy', 'unmeasured', limitation='No fixed reviewed benchmark and scoring denominators supplied.')
    collection = data.get('collection')
    if collection:
        require(collection['runId'] == coverage['runId'] and collection['appRevision'] == revision, 'Collector identity mismatch')
        require(collection['requiredTasks'] == len(tasks) and collection['successfulTasks'] == len(good), 'Collector coverage differs')
        require(collection.get('complete') == coverage['complete'], 'Collector completeness differs')
        if collection.get('githubEventName') == 'schedule':
            passed = collection.get('executionCompleted') is True and collection.get('githubRef') == 'refs/heads/main'
            add('durability.scheduled_execution', 'durability', 'pass' if passed else 'fail', int(passed), 1, ['collection'], observed_at=coverage['checkedAt'], limitation='One pinned scheduled cycle; not a sustained-operation rate.')
        else:
            add('durability.scheduled_execution', 'durability', 'unmeasured', evidence=['collection'],
                observed_at=coverage['checkedAt'], limitation='A non-scheduled run supplies no timer observation or scheduled-attempt denominator.')
    else:
        add('durability.scheduled_execution', 'durability', 'unmeasured', limitation='No scheduled collector receipt supplied.')
    publication = data.get('publication')
    if publication:
        require(gate is not None, 'Publication requires pinned gate')
        require(publication['appRevision'] == revision and publication['publication']['githubRunId'] == gate['githubRunId'], 'Publication/gate mismatch')
        passed = publication['publication'].get('published') is True
        add('durability.publication', 'durability', 'pass' if passed else 'fail', int(passed), 1, ['publication', 'gate'], limitation='Pinned historical acceptance; not a new live probe.')
    else:
        add('durability.publication', 'durability', 'unmeasured', limitation='No publication receipt supplied.')
    rollback = data.get('rollback')
    if rollback:
        require(publication is not None, 'Rollback requires publication')
        drill = rollback['drill']
        require(drill['current']['releaseId'] == publication['publication']['releaseId'] and drill['current']['deploymentId'] == publication['publication']['deploymentId'], 'Rollback release mismatch')
        require(instant(drill['completedAt']) <= now, 'Future rollback completion')
        passed = rollback.get('passed') is True and drill.get('phase') == 'passed' and drill.get('currentBytesVerified') is True and drill.get('productionHeadRemains') == drill['current']['releaseId']
        add('durability.rollback_restoration', 'durability', 'pass' if passed else 'fail', int(passed), 1, ['rollback', 'publication'],
            'Legacy baseline full byte inventory may be unavailable; retain that limitation.', drill['completedAt'], baselineByteInventoryAvailable=drill.get('baselineByteInventoryAvailable'))
    else:
        add('durability.rollback_restoration', 'durability', 'unmeasured', limitation='No rollback/restoration receipt supplied.')
    continuity = data.get('continuity')
    if continuity:
        require(continuity['runId'] == coverage['runId'] and continuity['appRevision'] == revision, 'Continuity identity mismatch')
        if 'contractSha256' in continuity:
            require(continuity['contractSha256'] == digest(contract), 'Continuity policy mismatch')
        require(instant(continuity['checkedAt']) <= now, 'Future continuity check')
        require(valid_hash(continuity['sourceSnapshotSha256']) and valid_hash(continuity['publishedSnapshotSha256']), 'Continuity snapshot hashes missing')
        if gate:
            require(continuity['publishedSnapshotSha256'] == gate['snapshotSha256'], 'Continuity covers another published snapshot')
        rows = continuity['measures']
        require(bool(rows) and len(rows) == len({row['id'] for row in rows}), 'Missing/duplicate continuity measures')
        for row in rows:
            require(type(row['expected']) is int and type(row['retained']) is int and 0 <= row['retained'] <= row['expected'], 'Invalid continuity counts')
            require(type(row['passed']) is bool and row['passed'] == (row['retained'] == row['expected']), 'False continuity pass')
        passed = all(row['passed'] for row in rows)
        add('durability.data_continuity', 'durability', 'pass' if passed else 'fail', sum(row['passed'] for row in rows), len(rows), ['continuity'],
            'Held claims and historical facts require explicit preservation checks; operational rollback cannot substitute for these.', continuity['checkedAt'], checks=rows, auditLimitations=continuity.get('limitations', []))
    else:
        add('durability.data_continuity', 'durability', 'unmeasured', limitation='No pinned held-claim/historical-data continuity audit supplied. Rollback/tests do not establish preservation.')
    add('durability.sustained_operation', 'durability', 'unmeasured', limitation='No complete observation-window history supplied; one cycle cannot establish durability over time.')
    add('value.observed_use', 'value', 'unmeasured', limitation='Owner reports no observed real use yet. Technical reliability, accuracy and freshness are the current priority.')
    suppliers = {s['id']: s for s in contract['suppliers']}
    receipt_by_task = {r['taskId']: r for r in receipts}
    groups = {axis: defaultdict(list) for axis in ('family', 'supplier', 'domain', 'reason')}
    for tid, task in tasks.items():
        source = sources.get(task['sourceId'], {})
        receipt = receipt_by_task[tid]
        family = source.get('family', task.get('family', 'unknown'))
        reason = 'successful' if tid in good else (views[tid].get('intakeErrorCode') or views[tid]['intakeOutcome'] if separated else receipt.get('errorCode') or receipt['outcome'])
        groups['family'][family].append(tid)
        groups['supplier'][task['supplierId']].append(tid)
        for domain in suppliers[task['supplierId']].get('domainIds', ['unclassified']):
            groups['domain'][domain].append(tid)
        groups['reason'][reason].append(tid)
    breakdowns = {}
    for axis, buckets in groups.items():
        rows = []
        for label, ids in sorted(buckets.items()):
            display = suppliers[label]['name'] if axis == 'supplier' else label.replace('_', ' ').replace('-', ' ')
            rows.append(dict(id=label, label=display, requiredTasks=len(ids), successfulTasks=len(set(ids) & good),
                             missingBindings=sum(tasks[tid]['sourceId'] is None for tid in ids),
                             candidateBindings=sum(sources.get(tasks[tid]['sourceId'], {}).get('registration') == 'candidate' for tid in ids),
                             verifiedBindings=sum(sources.get(tasks[tid]['sourceId'], {}).get('registration') == 'verified' for tid in ids),
                             outcomes=dict(Counter(views[tid]['intakeOutcome'] if separated else receipt_by_task[tid]['outcome'] for tid in ids)), taskIds=ids))
        breakdowns[axis] = rows
    registration = Counter(s['registration'] for s in sources.values() if s['required'])
    overview = dict(requiredTasks=len(tasks), successfulTasks=len(good), gapTasks=len(tasks)-len(good),
                    verifiedRegisteredBindings=registration['verified'], candidateBindings=registration['candidate'],
                    missingBindings=sum(t['sourceId'] is None for t in tasks.values()),
                    limitation='Verified registration is not a successful source check. 557 total obligations remain the primary denominator. Domain totals can overlap for suppliers in multiple domains.')
    return dict(schemaVersion=1, evaluatedAt=manifest['evaluatedAt'], appRevision=revision, runId=coverage['runId'],
                **({'coverageMeasure': SEPARATE_MEASURE} if separated else {}),
                contractSha256=digest(contract), inputs=pins, measures=measures,
                manifestSha256=digest(manifest),
                coverageOverview=overview, coverageBreakdowns=breakdowns,
                trustBoundary='Offline consistency evaluation of explicitly pinned supplied receipts. Does not authenticate GitHub or replay archived source bodies. No overall score.')


def markdown(report):
    labels = {
        'coverage.required_tasks': 'All declared source checks',
        'coverage.sec_tasks': 'SEC source checks',
        'freshness.collection_receipt': 'Age of the collection check',
        'freshness.all_required_checks': 'Freshness across the declared roster',
        'accuracy.known_release_checks': 'Known release checks',
        'accuracy.reviewed_records': 'Records included in the fixed source audit',
        'accuracy.known_contradictions': 'Known contradicting records in the fixed audit',
        'accuracy.claim_precision': 'Claim accuracy on a reviewed benchmark',
        'accuracy.eligible_event_recall': 'Eligible events found on a reviewed benchmark',
        'durability.scheduled_execution': 'Actual scheduled collection',
        'durability.publication': 'Exact release publication',
        'durability.rollback_restoration': 'Rollback and restoration',
        'durability.data_continuity': 'Preserved facts and pending work',
        'durability.sustained_operation': 'Sustained operation',
        'value.observed_use': 'Observed reader value',
        'review_queue.pending': 'Unresolved reviews retained',
        'historical_candidates.retained_or_quarantined': 'Historical candidates retained or quarantined',
    }
    lines = ['# Operational evaluation', '', f"Evaluated: {report['evaluatedAt']}", f"Revision: `{report['appRevision']}`", f"Run: `{report['runId']}`", '', report['trustBoundary'], '',
             '| Measure | Status | Observed / required | Observed at | Evidence | Limitations |', '|---|---|---|---|---|---|']
    for m in report['measures']:
        count = 'unmeasured' if m['numerator'] is None else f"{m['numerator']} / {m['denominator']}"
        if 'ageHours' in m:
            count = f"{m['ageHours']:.2f}h / maximum {m['maximumAgeHours']}h"
        if 'maximumCount' in m:
            count = f"{m['numerator']} / maximum {m['maximumCount']}"
        lines.append(f"| {m.get('label', labels.get(m['id'], m['id']))} | {m['status']} | {count} | {m['observedAt'] or 'Not supplied'} | {', '.join(m['evidence'])} | {m['limitations']} |")
        for check in m.get('checks', []):
            lines.append(f"| {labels.get(check['id'], check['id'])} | {'pass' if check['passed'] else 'fail'} | {check['retained']} / {check['expected']} retained | {m['observedAt']} | {', '.join(m['evidence'])} | Durable retention or quarantine; not publication eligibility. |")
    lines += ['', '## Pinned inputs', '']
    for name, pin in report['inputs'].items():
        lines.append(f"- {name}: `{pin['path']}` SHA-256 `{pin['sha256']}`")
    overview = report['coverageOverview']
    lines += ['', '## Coverage inventory', '',
              f"{overview['successfulTasks']}/{overview['requiredTasks']} successful required checks; {overview['gapTasks']} gaps. "
              f"{overview['verifiedRegisteredBindings']} verified registered bindings, {overview['candidateBindings']} candidate bindings, {overview['missingBindings']} missing bindings.",
              '', overview['limitation']]
    for axis, rows in report['coverageBreakdowns'].items():
        lines += ['', '### By ' + axis, '', '| Group | Successful / required | Verified bindings | Candidates | Missing bindings | Outcomes |', '|---|---|---|---|---|---|']
        for row in rows:
            outcomes = ', '.join(f'{key}: {value}' for key, value in sorted(row['outcomes'].items()))
            lines.append(f"| {row.get('label', row['id'])} | {row['successfulTasks']} / {row['requiredTasks']} | {row['verifiedBindings']} | {row['candidateBindings']} | {row['missingBindings']} | {outcomes} |")
    lines += ['', '## Next actions by evidence gap', '',
              '- Missing bindings: qualify an explicit source and adapter against archived primary evidence; preserve the obligation until registered.',
              '- Candidate bindings: verify entity scope, date boundaries, pagination and positive/quiet/blocked cases before awarding coverage.',
              '- Fetch or model caps: retain the charged limits and queue; retry only in an authorized later allowance and reuse valid prior checks.',
              '- Blocked or failed pages: inspect the retained failure and repair the adapter or document a supported alternate primary source.',
              '- Held claims: preserve the review queue and resolve source/date/status support before publication; do not infer an owner decision from a machine hold.']
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True, help='New output prefix; writes .json and .md without overwriting')
    args = parser.parse_args()
    try:
        report = evaluate(json.loads(args.manifest.read_text()), args.manifest.parent)
        targets = [args.output.with_suffix('.json'), args.output.with_suffix('.md')]
        require(not any(p.exists() for p in targets), 'Output exists; choose a new prefix')
        contents = [json.dumps(report, indent=2, allow_nan=False) + '\n', markdown(report)]
        for path, content in zip(targets, contents):
            with path.open('x') as output:
                output.write(content)
    except (ValueError, KeyError, TypeError, OSError) as exc:
        parser.exit(2, f'Evaluation refused: {exc}\n')
    print(args.output.with_suffix('.json'))
    print(args.output.with_suffix('.md'))


if __name__ == '__main__':
    main()
