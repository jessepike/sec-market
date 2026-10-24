"""Exclusive, zero-credit neutral SEC diagnostics. No import-time work or activation."""
import copy
import json
import re
from datetime import timezone
from pathlib import Path

from contracts import canonical, digest, instant, require, validate_contract

OPERATION = 'bounded_neutral_sec_qualification'
MAX_REQUESTS = 280
MAX_INDEX_PAGES = 40
MAX_PRIMARY_BODIES = 100
PROPOSAL_SHA256 = '9928884e5b0b9ec99811f09033fe1477ecde2353c012a634dd83317a63769526'
PROPOSAL_BYTES = 60966
PROPOSAL_SEAL = '3d8590537e2693025577c887408625f4319a37e11acc108ae833a7baaaf2ec8e'
RELATIONSHIP_ARCHIVE_MANIFEST = 'cd9d84c67a70f11b72eeba25a012e3402a88b2d5a9c692f145c225b0a2c3418a'
BINDINGS = (('crwd-exposure', '0001535527', 'CrowdStrike Holdings, Inc.', 'crwd-falcon-10k'),
            ('panw-xsiam', '0001327567', 'Palo Alto Networks Inc', 'panw-xsiam-10k'))
PLAN_FIELDS = {'schemaVersion', 'operation', 'marketSha256', 'originalContract', 'maxRequests',
               'maxIndexPagesPerPair', 'maxPrimaryBodiesPerPair', 'lookbackDays', 'pairs'}
PAIR_FIELDS = {'supplierId', 'indexSourceId', 'indexSourceSha256', 'documentsSourceId',
               'documentsSourceSha256', 'regulatoryIssuer', 'relationshipProof'}
ZERO_FIELDS = ('modelCalls', 'documentsProcessed', 'gateUses', 'sourceChecksCredited', 'qualifiedSources')


def _blob(store, ref, pattern=r'objects/[a-f0-9]{64}'):
    require(type(ref) is dict and set(ref) == {'key', 'sha256', 'bytes'} and
            isinstance(ref['key'], str) and re.fullmatch(pattern, ref['key']) and
            isinstance(ref['sha256'], str) and re.fullmatch(r'[a-f0-9]{64}', ref['sha256']) and
            type(ref['bytes']) is int and 0 < ref['bytes'] <= 32_000_000,
            'NEUTRAL_SEC_REFERENCE_INVALID')
    if ref['key'].startswith('objects/'):
        require(ref['key'] == 'objects/' + ref['sha256'], 'NEUTRAL_SEC_OBJECT_ADDRESS_DIFFERS')
    raw = store.get(ref)
    require(len(raw) == ref['bytes'] and digest(raw) == ref['sha256'], 'NEUTRAL_SEC_REFERENCE_INTEGRITY_DIFFERS')
    return raw


def _json(store, ref, pattern=r'objects/[a-f0-9]{64}'):
    result = json.loads(_blob(store, ref, pattern))
    require(type(result) is dict, 'NEUTRAL_SEC_JSON_OBJECT_REQUIRED')
    return result


def _relationship(store, value, binding):
    from discovery import decoded_discovery_body
    from documents import readable_document
    require(type(value) is dict and set(value) == {'proposal', 'proofId'} and value['proofId'] == binding[3],
            'NEUTRAL_SEC_RELATIONSHIP_PROOF_INVALID')
    require(value['proposal'] == {'key': 'objects/' + PROPOSAL_SHA256, 'sha256': PROPOSAL_SHA256,
                                  'bytes': PROPOSAL_BYTES}, 'NEUTRAL_SEC_RELATIONSHIP_AUTHORITY_DIFFERS')
    proposal = _json(store, value['proposal'])
    require(proposal.get('proposalSha256') == PROPOSAL_SEAL and
            digest({k:v for k,v in proposal.items() if k != 'proposalSha256'}) == PROPOSAL_SEAL and
            proposal['archive']['manifestSha256'] == RELATIONSHIP_ARCHIVE_MANIFEST,
            'NEUTRAL_SEC_RELATIONSHIP_REVIEW_SEAL_DIFFERS')
    matches = [p for p in proposal['primaryParentRelationshipProofs'] if p['proofId'] == value['proofId']]
    require(len(matches) == 1, 'NEUTRAL_SEC_RELATIONSHIP_PROOF_AMBIGUOUS')
    proof = matches[0]
    ref = copy.deepcopy(proof['observationActualReference'])
    require(ref['key'].startswith('state/observations/'), 'NEUTRAL_SEC_RELATIONSHIP_OBSERVATION_KEY_DIFFERS')
    ref['key'] = ref['key'][6:]
    observed = _json(store, ref, r'observations/[a-f0-9]{64}\.json')
    require(all(observed.get(key) == proof[key] for key in
                ('sourceId', 'requestedUrl', 'finalUrl', 'observationId', 'fetchedAt', 'status', 'body')),
            'NEUTRAL_SEC_RELATIONSHIP_ORIGINAL_OBSERVATION_DIFFERS')
    body = _blob(store, proof['body'])
    decoded = decoded_discovery_body(body)
    text = readable_document(body, observed.get('contentType', ''))
    require(proof['submissionsIdentity']['cik'] == binding[1] and
            proof['submissionsIdentity']['legalName'] == binding[2] and
            proof['inlineXbrlIdentity']['EntityCentralIndexKey']['value'] == binding[1] and
            all(item['rawMarkup'].encode() in decoded for item in proof['inlineXbrlIdentity'].values()) and
            proof['relationshipPhrase'] in text and all(item['text'] in text for item in proof['excerpts']),
            'NEUTRAL_SEC_RELATIONSHIP_PRIMARY_SCOPE_DIFFERS')
    issuer_root = _json(store, proof['submissionsIdentity']['initialIndexBody'])
    require(str(issuer_root.get('cik')).zfill(10) == binding[1] and issuer_root.get('name') == binding[2],
            'NEUTRAL_SEC_RELATIONSHIP_ORIGINAL_ISSUER_DIFFERS')
    return proposal


def validate_plan(contract, store, raw_plan_bytes, path=None):
    """Preflight both pairs and original relationship bytes before any transport."""
    from onboarding import _validate_sec_diagnostic_pair
    require(type(raw_plan_bytes) is bytes and 0 < len(raw_plan_bytes) <= 1_000_000, 'NEUTRAL_SEC_PLAN_SIZE_INVALID')
    plan = json.loads(raw_plan_bytes)
    require(type(plan) is dict and set(plan) == PLAN_FIELDS and type(plan['schemaVersion']) is int and
            plan['schemaVersion'] == 2 and plan['operation'] == OPERATION and
            plan['marketSha256'] == digest(contract) and
            all(type(plan[k]) is int and plan[k] == value for k,value in
                (('maxRequests', MAX_REQUESTS), ('maxIndexPagesPerPair', MAX_INDEX_PAGES),
                 ('maxPrimaryBodiesPerPair', MAX_PRIMARY_BODIES), ('lookbackDays', 365))) and
            type(plan['pairs']) is list and len(plan['pairs']) == 2, 'NEUTRAL_SEC_PLAN_SHAPE_OR_POLICY_INVALID')
    validate_contract(contract)
    policy = _json(store, plan['originalContract'], r'contracts/[a-f0-9]{64}\.json')
    require(plan['originalContract']['key'] == 'contracts/' + digest(contract) + '.json' and
            digest(policy) == digest(contract), 'NEUTRAL_SEC_ORIGINAL_WHOLE_POLICY_DIFFERS')
    pairs = []
    for row, binding in zip(plan['pairs'], BINDINGS):
        sid, cik, name, _ = binding
        require(type(row) is dict and set(row) == PAIR_FIELDS and row['supplierId'] == sid and
                row['indexSourceId'] == sid + ':sec_index' and row['documentsSourceId'] == sid + ':sec_documents' and
                digest(row['regulatoryIssuer']) == digest({'cik': cik, 'legalName': name, 'relationship': 'parent'}),
                'NEUTRAL_SEC_PAIR_INVENTORY_INVALID')
        proposal = _relationship(store, row['relationshipProof'], binding)
        sources = []
        for field in ('indexSourceId', 'documentsSourceId'):
            candidates = [s for s in contract['sources'] if s['id'] == row[field]]
            reviewed = [s for s in proposal['proposedSources'] if s['id'] == row[field]]
            require(len(candidates) == len(reviewed) == 1 and digest(candidates[0]) == digest(reviewed[0]) and
                    row[field.replace('Id', 'Sha256')] == digest(candidates[0]),
                    'NEUTRAL_SEC_EXACT_CANDIDATE_DECLARATION_DIFFERS')
            sources.append(copy.deepcopy(candidates[0]))
        _validate_sec_diagnostic_pair(*sources, contract['suppliers'])
        pairs.append({'index': sources[0], 'documents': sources[1]})
    return {'operation': OPERATION, 'rawSha256': digest(raw_plan_bytes), 'canonicalSha256': digest(plan),
            'path': str(path) if path is not None else None, 'plan': plan, 'pairs': pairs}


class _OperationBudget:
    def __init__(self, budget):
        self.base, self.initial = budget, budget.reservations
    def __getattr__(self, key):
        return getattr(self.base, key)
    def reserve_fetch(self):
        from onboarding import ProbeReservationDenied
        if self.base.reservations - self.initial >= MAX_REQUESTS:
            self.base.denials['NEUTRAL_SEC_OPERATION_LIMIT'] += 1
            raise ProbeReservationDenied('NEUTRAL_SEC_OPERATION_LIMIT')
        return self.base.reserve_fetch()


def execute(contract, store, fetcher, budget, normalized_plan):
    """Only these two pairs are executed; caller owns exclusive operation dispatch."""
    from onboarding import PersistentProbeBudget, ProbeReservationDenied, _probe_sec_candidate_pair
    require(isinstance(budget, PersistentProbeBudget), 'NEUTRAL_SEC_BOUND_BUDGET_REQUIRED')
    budget.assert_bound(store, contract)
    require(normalized_plan.get('operation') == OPERATION and isinstance(normalized_plan.get('path'), str),
            'NEUTRAL_SEC_CURRENT_PLAN_PATH_REQUIRED')
    raw = Path(normalized_plan['path']).read_bytes()
    require(digest(raw) == normalized_plan['rawSha256'], 'NEUTRAL_SEC_CURRENT_PLAN_CHANGED')
    plan = validate_plan(contract, store, raw, normalized_plan['path'])
    require(budget.reservations == 0, 'NEUTRAL_SEC_EXCLUSIVE_BUDGET_CONTEXT_REQUIRED')
    raw_ref = store.put(raw)
    limited = _OperationBudget(budget)
    rows = []
    for pair in plan['pairs']:
        rows.extend(_probe_sec_candidate_pair(pair['index'], pair['documents'], store, fetcher, limited, contract['suppliers']))
    final_denial = None
    checked_at = None
    try:
        budget.before_fetch()
        checked_at = budget.clock()
        budget.before_fetch()
    except ProbeReservationDenied as error:
        final_denial = error.reason
    if checked_at is None:
        checked_at = budget.clock()
    report = {'schemaVersion': 1, 'operation': OPERATION, 'contractSha256': digest(contract),
              'planRawSha256': digest(raw), 'planCanonicalSha256': plan['canonicalSha256'], 'planReference': raw_ref,
              'startedAt': budget.started_at, 'checkedAt': checked_at, 'sources': rows,
              'reservationContext': budget.summary(), 'completionDenial': final_denial,
              'executionCompleted': final_denial is None and not any(r['budgetDenied'] for r in rows),
              'budgetDenied': final_denial is not None or any(r['budgetDenied'] for r in rows),
              'qualified': False, 'semanticAdmission': False, 'coverageCredit': False,
              'facts': [], 'newFactIds': [], 'heldClaims': [], 'documentValidations': [],
              **{key: 0 for key in ZERO_FIELDS}}
    report['pairReadiness'] = _assess_rows(store, plan, report)
    verify_report(contract, store, raw, report)
    return report


def _observations(store, row, source, start, end, day):
    require(type(row.get('observations')) is list and type(row.get('fetchReservations')) is list and
            len(row['observations']) <= len(row['fetchReservations']) <= len(row['observations']) + 1,
            'NEUTRAL_SEC_OBSERVATION_RESERVATION_INVENTORY_DIFFERS')
    values = []
    for ref, reservation in zip(row['observations'], row['fetchReservations']):
        observed = _json(store, ref)
        require(observed.get('sourceId') == source['id'] and observed.get('requestedUrl') == reservation.get('url'),
                'NEUTRAL_SEC_OBSERVATION_SOURCE_OR_URL_DIFFERS')
        at = instant(observed.get('fetchedAt')).astimezone(timezone.utc)
        require(start <= at <= end and at.date().isoformat() == day, 'NEUTRAL_SEC_OBSERVATION_TIME_DIFFERS')
        if observed.get('body') is not None:
            _blob(store, observed['body'])
        values.append(observed)
    return values


def _fetched(observed, url):
    return (observed.get('status') == 'fetched' and type(observed.get('httpStatus')) is int and
            observed['httpStatus'] == 200 and observed.get('requestedUrl') == url and
            observed.get('finalUrl') == url and isinstance(observed.get('body'), dict))


def _assess_pair(store, pair, rows, start, end, day, outer_denial):
    from onboarding import _sec_diagnostic_pages, _validate_sec_candidate_index
    from discovery import decoded_discovery_body
    from documents import readable_document
    from regulatory import filing_document_inventory
    index, documents = pair['index'], pair['documents']
    ir, dr = rows
    ios = _observations(store, ir, index, start, end, day)
    dos = _observations(store, dr, documents, start, end, day)
    ix, dx = ir['secIndexDiagnostic'], dr['secDocumentsDiagnostic']
    require(set(ix) == {'allRequiredPagesFetched', 'qualificationComplete', 'requiredOlderPages', 'issuer'} and
            ix['qualificationComplete'] is False and digest(ix['issuer']) == digest(index['regulatoryIssuer']) and
            type(ix['allRequiredPagesFetched']) is bool and type(ix['requiredOlderPages']) is list,
            'NEUTRAL_SEC_INDEX_RESULT_SCHEMA_DIFFERS')
    require(dx.get('indexSourceId') == index['id'] and dx.get('semanticEvidence') is False and
            type(dx.get('allSelectedBodiesFetched')) is bool and type(dx.get('primaryDocuments')) is list,
            'NEUTRAL_SEC_DOCUMENT_RESULT_SCHEMA_DIFFERS')
    pages, required, selected, index_complete, reason = [], [], None, False, 'INDEX_INCOMPLETE'
    try:
        require(ios and _fetched(ios[0], index['url']), 'INDEX_ROOT_RESPONSE_INCOMPLETE')
        root = json.loads(decoded_discovery_body(_blob(store, ios[0]['body'])))
        required = _sec_diagnostic_pages(index, root, ios[0]['fetchedAt'])
        pages = [{'url': index['url'], 'document': root}]
        require(len(ios) <= 1 + len(required), 'NEUTRAL_SEC_EXTRA_INDEX_OBSERVATION')
        for observed, item in zip(ios[1:], required):
            require(_fetched(observed, item['url']), 'INDEX_OLDER_RESPONSE_INCOMPLETE')
            pages.append({'url': item['url'], 'document': json.loads(decoded_discovery_body(_blob(store, observed['body'])))})
        require(len(ios) == 1 + len(required), 'INDEX_OLDER_PAGES_INCOMPLETE')
        checked = _validate_sec_candidate_index(index, pages, ios[0]['fetchedAt'])
        selected = filing_document_inventory(documents, pages, checked['windowStart'], checked['windowEnd'])
        index_complete = True
    except (ValueError, KeyError, TypeError) as error:
        reason = str(error)
    require(len(ios) <= 1 + len(required) and
            [o['requestedUrl'] for o in ios] == [index['url']] + [p['url'] for p in required[:max(0,len(ios)-1)]]
            if ios else True, 'NEUTRAL_SEC_INDEX_SEQUENCE_DIFFERS')
    expected_older = [{'url': item['url'], 'filingFrom': item['filingFrom'], 'filingTo': item['filingTo'],
                      'filingCount': item['filingCount'], 'observation': ir['observations'][i+1],
                      'status': ios[i+1].get('status')} for i,item in enumerate(required[:max(0,len(ios)-1)])]
    require(digest(ix['requiredOlderPages']) == digest(expected_older), 'NEUTRAL_SEC_OLDER_METADATA_DIFFERS')
    index_urls = [index['url']] + [p['url'] for p in required]
    require([r['url'] for r in ir['fetchReservations']] == index_urls[:len(ir['fetchReservations'])] and
            len(ir['fetchReservations']) <= len(index_urls), 'NEUTRAL_SEC_INDEX_RESERVATION_SEQUENCE_DIFFERS')
    final_denied = any(d.get('phase') == 'final_window_check' for row in rows for d in row['reservationDenials'])
    require(ix['allRequiredPagesFetched'] is (index_complete and not final_denied), 'NEUTRAL_SEC_INDEX_COMPLETION_DIFFERS')
    base_fields = {'indexSourceId', 'primaryDocuments', 'allSelectedBodiesFetched', 'semanticEvidence'}
    if not index_complete:
        require(set(dx) == base_fields and not dx['primaryDocuments'] and not dos and not dr['fetchReservations'] and
                dx['allSelectedBodiesFetched'] is False, 'NEUTRAL_SEC_INCOMPLETE_INDEX_CARRIES_DOCUMENT_AUTHORITY')
        return {'supplierId': index['supplierId'], 'indexComplete': False, 'documentsComplete': False,
                'evidenceComplete': False, 'selectedCount': None, 'observedPrimaryCount': 0,
                'pendingPrimaryUrls': [], 'reason': reason}
    require(set(dx) == base_fields | {'indexObservations', 'selectedCount', 'selectedDocuments', 'primaryBodyGuard'} and
            dx['indexObservations'] == ir['observations'] and type(dx['selectedCount']) is int and
            dx['selectedCount'] == len(selected) and digest(dx['selectedDocuments']) == digest(selected) and
            type(dx['primaryBodyGuard']) is int and dx['primaryBodyGuard'] == MAX_PRIMARY_BODIES,
            'NEUTRAL_SEC_PRIMARY_SELECTION_DIFFERS')
    require(len(dos) <= min(len(selected), MAX_PRIMARY_BODIES) and len(dx['primaryDocuments']) == len(dos),
            'NEUTRAL_SEC_PRIMARY_PARTITION_DIFFERS')
    require([r['url'] for r in dr['fetchReservations']] == [p['url'] for p in selected[:len(dr['fetchReservations'])]] and
            len(dr['fetchReservations']) <= len(selected), 'NEUTRAL_SEC_PRIMARY_RESERVATION_SEQUENCE_DIFFERS')
    if len(selected) > MAX_PRIMARY_BODIES:
        require(not dos and not dr['fetchReservations'], 'NEUTRAL_SEC_BODY_GUARD_TRUNCATED')
    good = set()
    for i,(observed,item,row) in enumerate(zip(dos, selected, dx['primaryDocuments'])):
        require(set(row) in ({'url','filingDate','observation','status','httpStatus','errorCode'},
                             {'url','filingDate','observation','status','httpStatus','errorCode','readableText'}) and
                row['url'] == item['url'] == observed['requestedUrl'] and row['filingDate'] == item['filingDate'] and
                row['observation'] == dr['observations'][i] and all(row[k] == observed.get(k) for k in
                    ('status','httpStatus','errorCode')), 'NEUTRAL_SEC_PRIMARY_OBSERVATION_DIFFERS')
        readable = None
        if _fetched(observed, item['url']):
            try:
                readable = readable_document(_blob(store, observed['body']), observed.get('contentType',''))
            except (ValueError, OSError, RuntimeError):
                pass
        require(('readableText' in row) == (readable is not None), 'NEUTRAL_SEC_READABLE_TEXT_PRESENCE_DIFFERS')
        if readable is not None:
            require(_blob(store, row['readableText']) == readable.encode(), 'NEUTRAL_SEC_READABLE_TEXT_DIFFERS')
            good.add(item['url'])
        else:
            require(i == len(dos)-1, 'NEUTRAL_SEC_CONTINUED_AFTER_FAILED_PRIMARY')
    raw_complete = len(selected) <= MAX_PRIMARY_BODIES and len(good) == len(selected)
    require(dx['allSelectedBodiesFetched'] is (raw_complete and not final_denied), 'NEUTRAL_SEC_DOCUMENT_COMPLETION_DIFFERS')
    complete = raw_complete and not outer_denial and not any(row['reservationDenials'] for row in rows)
    return {'supplierId': index['supplierId'], 'indexComplete': index_complete and not final_denied,
            'documentsComplete': complete, 'evidenceComplete': complete,
            'selectedCount': len(selected), 'observedPrimaryCount': len(dos),
            'pendingPrimaryUrls': [i['url'] for i in selected if i['url'] not in good],
            'reason': 'COMPLETE_DIAGNOSTIC_EVIDENCE_ONLY' if complete else 'PRIMARY_OR_LEASE_INCOMPLETE'}


def _assess_rows(store, plan, report):
    context = report['reservationContext']
    start = instant(context['startedAt']).astimezone(timezone.utc)
    end = instant(report['checkedAt']).astimezone(timezone.utc)
    require(end >= start and report['startedAt'] == context['startedAt'], 'NEUTRAL_SEC_REPORT_TIME_DIFFERS')
    rows = report['sources']
    require(type(rows) is list and len(rows) == 4, 'NEUTRAL_SEC_SOURCE_PARTITION_DIFFERS')
    results = []
    for i,pair in enumerate(plan['pairs']):
        pair_rows = rows[i*2:i*2+2]
        for row,source,diagnostic in zip(pair_rows, (pair['index'],pair['documents']), ('secIndexDiagnostic','secDocumentsDiagnostic')):
            require(type(row) is dict and set(row) == {'sourceId','supplierId','checkedAt','registration','observations',
                    'fetchReservations','reservationDenials','qualified','semanticAdmission','coverageCredit','facts',
                    'sourceChecksCredited','qualifiedSources','reason','executionCompleted','budgetDenied',diagnostic} and
                    row['sourceId'] == source['id'] and row['supplierId'] == source['supplierId'] and
                    row['registration'] == 'candidate' and all(row[k] is False for k in
                        ('qualified','semanticAdmission','coverageCredit')) and row['facts'] == [] and
                    all(type(row[k]) is int and row[k] == 0 for k in ('sourceChecksCredited','qualifiedSources')) and
                    type(row['reservationDenials']) is list and isinstance(row['reason'],str) and
                    row['executionCompleted'] is (not bool(row['reservationDenials'])) and
                    row['budgetDenied'] is bool(row['reservationDenials']), 'NEUTRAL_SEC_SOURCE_ENVELOPE_DIFFERS')
            require(start <= instant(row['checkedAt']) <= end, 'NEUTRAL_SEC_SOURCE_TIME_DIFFERS')
            for denial in row['reservationDenials']:
                require(type(denial) is dict and set(denial) in
                        ({'url','reason','budgetDay','reservationCharged'},
                         {'url','reason','budgetDay','reservationCharged','phase'}) and
                        isinstance(denial['reason'],str) and denial['reason'] and
                        denial['budgetDay'] == context['budgetDay'] and
                        (denial['reservationCharged'] is None or type(denial['reservationCharged']) is bool) and
                        ('phase' not in denial or (denial['phase'] == 'final_window_check' and
                            denial['url'] is None and denial['reservationCharged'] is False)),
                        'NEUTRAL_SEC_DENIAL_SCHEMA_DIFFERS')
                if denial['reservationCharged'] is True:
                    require(row['fetchReservations'] and denial['url'] == row['fetchReservations'][-1]['url'],
                            'NEUTRAL_SEC_CHARGED_DENIAL_DIFFERS')
        results.append(_assess_pair(store,pair,pair_rows,start,end,context['budgetDay'],report['completionDenial']))
    return results


def verify_report(original_contract, store, raw_plan_bytes, report):
    """Replay raw evidence without transport, state writes or qualification credit."""
    plan = validate_plan(original_contract, store, raw_plan_bytes)
    fields = {'schemaVersion','operation','contractSha256','planRawSha256','planCanonicalSha256','planReference',
              'startedAt','checkedAt','sources','reservationContext','completionDenial','executionCompleted',
              'budgetDenied','qualified','semanticAdmission','coverageCredit','facts','newFactIds','heldClaims',
              'documentValidations','pairReadiness',*ZERO_FIELDS}
    require(type(report) is dict and set(report) == fields and type(report['schemaVersion']) is int and
            report['schemaVersion'] == 1 and report['operation'] == OPERATION and
            report['contractSha256'] == digest(original_contract) and report['planRawSha256'] == digest(raw_plan_bytes) and
            report['planCanonicalSha256'] == plan['canonicalSha256'] and _blob(store, report['planReference']) == raw_plan_bytes and
            (report['completionDenial'] is None or isinstance(report['completionDenial'],str)) and
            all(report[k] is False for k in ('qualified','semanticAdmission','coverageCredit')) and
            all(type(report[k]) is int and report[k] == 0 for k in ZERO_FIELDS) and
            all(report[k] == [] for k in ('facts','newFactIds','heldClaims','documentValidations')),
            'NEUTRAL_SEC_REPORT_ENVELOPE_DIFFERS')
    c = report['reservationContext']
    require(type(c) is dict and set(c) == {'budgetDay','contractSha256','fetchLimit','maximumRuntimeSeconds','startedAt',
                'initialBudget','currentBudget','probeFetchReservations','reservationDenials'} and
            c['contractSha256'] == digest(original_contract) and type(c['fetchLimit']) is int and
            c['fetchLimit'] == original_contract['schedule'].get('maxFetchesPerRun',5000) <= 5500 and
            type(c['maximumRuntimeSeconds']) is int and 0 < c['maximumRuntimeSeconds'] <= min(1200,original_contract['schedule'].get('maxRuntimeSeconds',7200)) and
            type(c['probeFetchReservations']) is int and 0 <= c['probeFetchReservations'] <= MAX_REQUESTS and
            type(c['reservationDenials']) is dict and all(type(n) is int and n > 0 for n in c['reservationDenials'].values()) and
            instant(c['startedAt']).astimezone(timezone.utc).date().isoformat() == c['budgetDay'], 'NEUTRAL_SEC_BUDGET_CONTEXT_DIFFERS')
    initial = c['initialBudget'] if c['initialBudget'] is not None else {'calls':0,'documents':0,'fetches':0}
    current = c['currentBudget'] if c['currentBudget'] is not None else {'calls':0,'documents':0,'fetches':0}
    require(type(initial) is dict and type(current) is dict and all(type(b.get(k)) is int and b[k] >= 0
            for b in (initial,current) for k in ('calls','documents','fetches')) and
            digest({k:v for k,v in initial.items() if k!='fetches'}) == digest({k:v for k,v in current.items() if k!='fetches'}) and
            current['fetches'] - initial['fetches'] == c['probeFetchReservations'] and
            current['fetches'] <= c['fetchLimit'], 'NEUTRAL_SEC_COUNTERS_DIFFER')
    readiness = _assess_rows(store,plan,report)
    charges = []
    for i,row in enumerate(report['sources']):
        require(len(row['fetchReservations']) <= (MAX_INDEX_PAGES if i%2 == 0 else MAX_PRIMARY_BODIES), 'NEUTRAL_SEC_SOURCE_REQUEST_CAP_EXCEEDED')
        for r in row['fetchReservations']:
            require(type(r) is dict and set(r) == {'url','budgetDay','fetchLimit','chargedFetchCount'} and
                    r['budgetDay'] == c['budgetDay'] and type(r['fetchLimit']) is int and r['fetchLimit'] == c['fetchLimit'] and
                    type(r['chargedFetchCount']) is int, 'NEUTRAL_SEC_CHARGE_INVALID')
            charges.append(r['chargedFetchCount'])
    require(charges == list(range(initial['fetches']+1,current['fetches']+1)), 'NEUTRAL_SEC_CHARGE_INTERVAL_DIFFERS')
    denied = report['completionDenial'] is not None or any(r['reservationDenials'] for r in report['sources'])
    require(report['budgetDenied'] is denied and report['executionCompleted'] is (not denied) and
            digest(report['pairReadiness']) == digest(readiness), 'NEUTRAL_SEC_READINESS_OR_COMPLETION_DIFFERS')
    if report['completionDenial'] is not None:
        require(report['completionDenial'] in c['reservationDenials'], 'NEUTRAL_SEC_FINAL_DENIAL_NOT_RETAINED')
    denial_events = set()
    for i,row in enumerate(report['sources']):
        for d in row['reservationDenials']:
            denial_events.add((d['reason'], i//2 if d.get('phase') == 'final_window_check' else i,
                               d['url'], d.get('phase'), d['reservationCharged']))
    by_reason = {}
    for reason,*_ in denial_events:
        by_reason[reason] = by_reason.get(reason,0) + 1
    if report['completionDenial'] is not None:
        reason = report['completionDenial']; by_reason[reason] = by_reason.get(reason,0) + 1
    require(digest(by_reason) == digest(c['reservationDenials']), 'NEUTRAL_SEC_DENIAL_ACCOUNTING_DIFFERS')
    end,start = instant(report['checkedAt']).astimezone(timezone.utc),instant(c['startedAt']).astimezone(timezone.utc)
    if end.date().isoformat() != c['budgetDay'] or (end-start).total_seconds() >= c['maximumRuntimeSeconds']:
        require(denied and not any(r['evidenceComplete'] for r in readiness), 'NEUTRAL_SEC_EXPIRED_RUN_CANNOT_COMPLETE')
    return {'pairs': readiness, 'evidenceComplete': all(r['evidenceComplete'] for r in readiness),
            'qualified': False, 'coverageCredit': False}


def replay_diagnostic(original_contract, store, run_record_reference, raw_plan_reference):
    """Internal content replay only; external run authentication remains caller-owned."""
    record = _json(store, run_record_reference, r'ci/source-probe-runs/[0-9]+-[0-9]+\.json')
    require(type(record.get('schemaVersion')) is int and record['schemaVersion'] == 1 and
            record.get('checkpointProfile') == 'source_probe' and record.get('contractSha256') == digest(original_contract) and
            type(record.get('githubRunId')) in (str,int) and str(record['githubRunId']).isdigit() and
            type(record.get('githubRunAttempt')) is int and record['githubRunAttempt'] > 0 and
            run_record_reference['key'] == f"ci/source-probe-runs/{record['githubRunId']}-{record['githubRunAttempt']}.json" and
            record.get('githubEventName') == 'workflow_dispatch' and record.get('githubRef') == 'refs/heads/main' and
            isinstance(record.get('appRevision'),str) and re.fullmatch(r'[a-f0-9]{40}',record['appRevision']) and
            record.get('apiFallback') is False and all(type(record.get(k)) is int and record[k] == 0
                for k in ('modelCalls','sourceChecksCredited','qualifiedSources')) and
            record.get('semanticAdmission') is False and record.get('coverageCredit') is False and
            record.get('publication') == {'published':False,'reason':'SOURCE_PROBE_DIAGNOSTIC_ONLY'},
            'NEUTRAL_SEC_HISTORICAL_RUN_ENVELOPE_DIFFERS')
    report = record.get('diagnostic')
    require(type(report) is dict, 'NEUTRAL_SEC_HISTORICAL_REPORT_REQUIRED')
    require(report['planReference'] == raw_plan_reference and record['executionCompleted'] is report['executionCompleted'] and
            (record['outcome'] == ('completed_diagnostic' if report['executionCompleted'] else 'budget_denied') or
             (record['outcome'] == 'cancelled' and record['executionCompleted'] is False)),
            'NEUTRAL_SEC_HISTORICAL_OUTCOME_OR_PLAN_DIFFERS')
    raw = _blob(store,raw_plan_reference)
    readiness = verify_report(original_contract,store,raw,report)
    return {'plan':validate_plan(original_contract,store,raw), 'report':report, 'readiness':readiness}
