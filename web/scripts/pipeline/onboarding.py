"""Probe actual publisher discovery endpoints and archive registration receipts."""
import json
import re
import copy
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta, timezone
from pathlib import Path
import threading
import time
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlsplit
from urllib.robotparser import RobotFileParser

from contracts import digest, instant, require, utcnow, valid_hash, validate_contract
from discovery import (DELINEA_HTML_MODE, DELINEA_HTML_MODE_V2, DELINEA_HTML_MODE_V3, DELINEA_HTML_MODE_V4, DELINEA_INDEX,
                       PING_HTML_MODE, PING_HTML_MODE_V2, PING_HTML_MODE_V3, PING_INDEX,
                       SONATYPE_HTML_MODE, SONATYPE_HTML_MODE_V2, SONATYPE_HTML_MODE_V3, SONATYPE_HTML_MODE_V4, SONATYPE_INDEX, IndexMarkup, Page,
                       decoded_discovery_body, parse_source_html_index, ping_article_date,
                       _v3_literal_article_href, xml_links)


BOUNDED_CANDIDATE_OPERATION = 'bounded_candidate_traversal'
DISABLED_QUALIFICATION_OPERATION = 'disabled_qualification_probe'
BOUNDED_CANDIDATE_LIMIT = 60
BOUNDED_CANDIDATE_SAMPLE_LIMIT = 1
BOUNDED_CANDIDATE_MAX_REQUESTS = 183
BOUNDED_CANDIDATE_BINDINGS = (
    ('ping-identity:official:1', PING_INDEX, PING_HTML_MODE),
    ('delinea:official:1', DELINEA_INDEX, DELINEA_HTML_MODE),
    ('sonatype:official:1', SONATYPE_INDEX, SONATYPE_HTML_MODE),
)
BOUNDED_CANDIDATE_BINDINGS_V2 = (
    ('ping-identity:official:1', PING_INDEX, PING_HTML_MODE_V2),
    ('delinea:official:1', DELINEA_INDEX, DELINEA_HTML_MODE_V2),
    ('sonatype:official:1', SONATYPE_INDEX, SONATYPE_HTML_MODE_V2),
)
BOUNDED_CANDIDATE_BINDINGS_V3 = (
    ('ping-identity:official:1', PING_INDEX, PING_HTML_MODE_V3),
    ('delinea:official:1', DELINEA_INDEX, DELINEA_HTML_MODE_V3),
    ('sonatype:official:1', SONATYPE_INDEX, SONATYPE_HTML_MODE_V3),
)
BOUNDED_CANDIDATE_BINDINGS_V4 = (
    ('ping-identity:official:1', PING_INDEX, PING_HTML_MODE_V3),
    ('delinea:official:1', DELINEA_INDEX, DELINEA_HTML_MODE_V4),
    ('sonatype:official:1', SONATYPE_INDEX, SONATYPE_HTML_MODE_V4),
)


class ProbeReservationDenied(RuntimeError):
    def __init__(self, reason):
        super().__init__(reason)
        self.reason = reason


class PersistentProbeBudget:
    """A current-day, store/contract-bound reservation context; never a refund."""
    def __init__(self, store, contract, *, clock=utcnow, monotonic=time.monotonic, maximum_seconds=1200):
        limit = contract['schedule'].get('maxFetchesPerRun', 5000)
        runtime = contract['schedule'].get('maxRuntimeSeconds', 7200)
        require(type(limit) is int and 1 <= limit <= 5500, 'SOURCE_PROBE_FETCH_LIMIT_INVALID')
        require(type(runtime) is int and runtime > 0 and type(maximum_seconds) is int
                and 0 < maximum_seconds <= 1200, 'SOURCE_PROBE_RUNTIME_LIMIT_INVALID')
        self.store, self.contract_sha256, self.clock, self.monotonic = store, digest(contract), clock, monotonic
        self.started_at = clock()
        self.started = instant(self.started_at).astimezone(timezone.utc)
        self.day = self.started.date().isoformat()
        self.budget_name = 'budget-' + self.day
        self.limit, self.maximum_seconds = limit, min(runtime, maximum_seconds)
        self.deadline = monotonic() + self.maximum_seconds
        self.mutex = threading.RLock()
        self.reservations, self.denials = 0, Counter()
        with store.lock('daily-budget-reservation', blocking=True):
            self.initial_budget = copy.deepcopy(store.read('heads/' + self.budget_name + '.json'))

    def assert_bound(self, store, contract):
        require(self.store is store and self.contract_sha256 == digest(contract), 'SOURCE_PROBE_RESERVATION_CONTEXT_UNBOUND')

    def _guard(self):
        try:
            moment = instant(self.clock()).astimezone(timezone.utc)
        except (ValueError, TypeError, AttributeError):
            raise ProbeReservationDenied('SOURCE_PROBE_CLOCK_INVALID') from None
        if moment.date().isoformat() != self.day:
            raise ProbeReservationDenied('SOURCE_PROBE_UTC_DAY_CHANGED')
        if moment < self.started:
            raise ProbeReservationDenied('SOURCE_PROBE_CLOCK_REGRESSED')
        if self.monotonic() >= self.deadline:
            raise ProbeReservationDenied('SOURCE_PROBE_DEADLINE_EXCEEDED')

    def reserve_fetch(self):
        with self.mutex:
            try:
                self._guard()
                # The same lock and head are shared with daily collection.
                with self.store.lock('daily-budget-reservation', blocking=True):
                    self._guard()
                    previous = self.store.read('heads/' + self.budget_name + '.json')
                    if previous is not None and not isinstance(previous, dict):
                        raise ProbeReservationDenied('SOURCE_PROBE_FETCH_LEDGER_INVALID')
                    counts = dict(previous) if previous is not None else {'calls': 0, 'documents': 0, 'fetches': 0}
                    count = counts.get('fetches', 0)
                    if type(count) is not int or count < 0:
                        raise ProbeReservationDenied('SOURCE_PROBE_FETCH_LEDGER_INVALID')
                    if count >= self.limit:
                        raise ProbeReservationDenied('FETCHES_BUDGET_EXHAUSTED')
                    counts['fetches'] = count + 1
                    self.store.compare_and_swap(self.budget_name, previous, counts)
                    self.reservations += 1
                    return {'budgetDay': self.day, 'fetchLimit': self.limit, 'chargedFetchCount': counts['fetches']}
            except ProbeReservationDenied as error:
                self.denials[error.reason] += 1
                raise
            except (ValueError, OSError, RuntimeError):
                reason = 'SOURCE_PROBE_RESERVATION_PERSISTENCE_FAILED'
                self.denials[reason] += 1
                raise ProbeReservationDenied(reason) from None

    def before_fetch(self):
        # A reservation remains charged if the deadline/day changes between
        # its durable write and the immediate transport invocation.
        with self.mutex:
            try:
                self._guard()
            except ProbeReservationDenied as error:
                self.denials[error.reason] += 1
                raise

    def summary(self):
        with self.mutex, self.store.lock('daily-budget-reservation', blocking=True):
            return {'budgetDay': self.day, 'contractSha256': self.contract_sha256,
                    'fetchLimit': self.limit, 'maximumRuntimeSeconds': self.maximum_seconds,
                    'startedAt': self.started_at, 'initialBudget': copy.deepcopy(self.initial_budget),
                    'probeFetchReservations': self.reservations, 'reservationDenials': dict(self.denials),
                    'currentBudget': self.store.read('heads/' + self.budget_name + '.json')}


def _qualification_url(url, source):
    require(isinstance(url, str), 'QUALIFICATION_URL_INVALID')
    value = urlsplit(url)
    require(value.scheme == 'https' and value.hostname in source['allowedHosts']
            and not value.username and not value.password and value.port in (None, 443)
            and not value.fragment and not any(c.isspace() for c in url), 'QUALIFICATION_URL_HOST_INVALID')
    return url


def _qualification_reference(store, reference, pattern):
    require(isinstance(reference, dict) and set(reference) == {'key', 'sha256', 'bytes'}
            and isinstance(reference['key'], str) and re.fullmatch(pattern, reference['key'])
            and valid_hash(reference['sha256']) and type(reference['bytes']) is int
            and 0 < reference['bytes'] <= 32_000_000, 'QUALIFICATION_PROOF_REFERENCE_INVALID')
    if reference['key'].startswith('objects/'):
        require(reference['key'] == 'objects/' + reference['sha256'], 'QUALIFICATION_OBJECT_ADDRESS_INVALID')
    return store.get(reference)


def _qualification_proof_policy(recorded, proof, source, contract, store):
    """Read original evidence under its policy; allow only the exact D-112 transition."""
    current_hash = digest(contract)
    descriptor = proof.get('historicalPolicyBridge')
    if recorded.get('contractSha256') == current_hash:
        require('historicalPolicyBridge' not in proof, 'QUALIFICATION_UNNECESSARY_HISTORICAL_POLICY_BRIDGE')
        return contract, source
    require(proof['type'] == 'qualification_observation', 'QUALIFICATION_HISTORICAL_EXPLICIT_PROOF_REQUIRED')
    require(isinstance(descriptor, dict) and set(descriptor) == {
            'schemaVersion', 'transition', 'originalContract', 'originalContractSha256',
            'currentContractSha256', 'semanticContextSha256'} and
            type(descriptor['schemaVersion']) is int and descriptor['schemaVersion'] == 1 and
            descriptor['transition'] == 'd112-intake-history-separation' and
            valid_hash(descriptor['originalContractSha256']) and
            descriptor['originalContractSha256'] == recorded.get('contractSha256') and
            descriptor['currentContractSha256'] == current_hash,
            'QUALIFICATION_HISTORICAL_POLICY_BRIDGE_REQUIRED_OR_INVALID')
    reference = descriptor['originalContract']
    require(isinstance(reference, dict) and reference.get('key') ==
            'contracts/' + descriptor['originalContractSha256'] + '.json' and
            reference.get('sha256') == descriptor['originalContractSha256'] and
            type(reference.get('bytes')) is int and 0 < reference['bytes'] <= 1_000_000,
            'QUALIFICATION_ORIGINAL_CONTRACT_REFERENCE_INVALID')
    raw = _qualification_reference(store, reference, r'contracts/[a-f0-9]{64}\.json')
    original = json.loads(raw)
    require(isinstance(original, dict) and digest(original) == descriptor['originalContractSha256'],
            'QUALIFICATION_ORIGINAL_CONTRACT_CANONICAL_HASH_DIFFERS')
    validate_contract(original)
    validate_contract(contract)
    require(original['version'] == 'market-daily-v1' and contract['version'] == 'market-daily-v2' and
            original.get('collection', {}).get('mode') == 'delta_with_retained_audit' and
            contract.get('collection', {}).get('mode') == 'daily_intake_with_separate_history',
            'QUALIFICATION_D112_TRANSITION_INVALID')
    old_policy, current_policy = copy.deepcopy(original), copy.deepcopy(contract)
    for policy in (old_policy, current_policy):
        policy.pop('version')
        policy['collection'].pop('mode')
    require(digest(old_policy) == digest(current_policy), 'QUALIFICATION_D112_SUBSTANTIVE_POLICY_CHANGE')
    from separation import bridge
    derived = bridge(original, contract, source['id'])
    require(all(descriptor[key] == derived[key] for key in
                ('originalContractSha256', 'currentContractSha256', 'semanticContextSha256')),
            'QUALIFICATION_HISTORICAL_SOURCE_CONTEXT_DIFFERS')
    original_source = next(s for s in original['sources'] if s['id'] == source['id'])
    require(original_source == source and original_source['registration'] == 'candidate',
            'QUALIFICATION_HISTORICAL_SOURCE_BINDING_DIFFERS')
    return original, original_source


def _qualification_explicit_observation(recorded, proof, source, contract, store):
    """Bind a retained explicit result to its old committed plan and charged request."""
    require(recorded.get('executionCompleted') is True and recorded.get('outcome') == 'completed_diagnostic'
            and recorded.get('apiFallback') is False
            and isinstance(recorded.get('appRevision'), str) and re.fullmatch(r'[a-f0-9]{40}', recorded['appRevision'])
            and recorded.get('publication') == {'published': False, 'reason': 'SOURCE_PROBE_DIAGNOSTIC_ONLY'},
            'QUALIFICATION_PRIOR_RUN_NOT_COMPLETED_DIAGNOSTIC')
    diagnostic = recorded.get('diagnostic')
    require(isinstance(diagnostic, dict), 'QUALIFICATION_PRIOR_DIAGNOSTIC_INVALID')
    qualification = diagnostic.get('qualification')
    require(isinstance(qualification, dict), 'QUALIFICATION_PRIOR_EXPLICIT_RESULTS_REQUIRED')
    for summary in (diagnostic, qualification):
        require(summary.get('semanticAdmission') is False and summary.get('coverageCredit') is False
                and summary.get('facts') == []
                and all(type(summary.get(k)) is int and summary[k] == 0
                        for k in ('sourceChecksCredited', 'qualifiedSources')),
                'QUALIFICATION_PRIOR_SUMMARY_CREDIT_INVALID')
    require(diagnostic.get('contractSha256') == digest(contract) and diagnostic.get('executionCompleted') is True
            and diagnostic.get('qualified') is False and diagnostic.get('budgetDenied') is False
            and qualification.get('modelCalls') == 0 and type(qualification.get('modelCalls')) is int,
            'QUALIFICATION_PRIOR_SUMMARY_POLICY_INVALID')
    prior = qualification.get('plan')
    require(isinstance(prior, dict), 'QUALIFICATION_PRIOR_PLAN_REQUIRED')
    if 'rawPlanReference' in prior:
        require('priorPlanReference' in proof and proof['priorPlanReference'] == prior['rawPlanReference'],
                'QUALIFICATION_PRIOR_PLAN_REFERENCE_DIFFERS')
        raw = _qualification_reference(store, proof['priorPlanReference'], r'objects/[a-f0-9]{64}')
        require(proof['priorPlanReference']['sha256'] == prior.get('rawSha256'),
                'QUALIFICATION_PRIOR_PLAN_REFERENCE_HASH_DIFFERS')
    else:
        require(isinstance(proof.get('priorPlanRaw'), str), 'QUALIFICATION_LEGACY_PRIOR_PLAN_RAW_REQUIRED')
        raw = proof['priorPlanRaw'].encode()
    require(0 < len(raw) <= 1_000_000, 'QUALIFICATION_PRIOR_PLAN_REQUIRED')
    old_plan = json.loads(raw)
    require(digest(raw) == proof['priorPlanRawSha256'] == prior.get('rawSha256')
            and digest(old_plan) == proof['priorPlanCanonicalSha256'] == prior.get('canonicalSha256')
            and old_plan == prior.get('plan') and old_plan.get('marketSha256') == digest(contract)
            and prior.get('marketSha256') == digest(contract) and prior.get('maxRequests') == 7
            and set(old_plan) == {'schemaVersion', 'marketSha256', 'maxRequests', 'targets'}
            and type(old_plan['schemaVersion']) is int and old_plan['schemaVersion'] == 1
            and type(old_plan['maxRequests']) is int and old_plan['maxRequests'] == 7,
            'QUALIFICATION_PRIOR_PLAN_HASH_OR_POLICY_DIFFERS')
    old_targets, validated, rows = old_plan.get('targets'), prior.get('targets'), qualification.get('targets')
    require(all(isinstance(x, list) and len(x) == 7 and all(isinstance(t, dict) for t in x)
                for x in (old_targets, validated, rows)), 'QUALIFICATION_PRIOR_TARGET_INVENTORY_INVALID')
    require(len({t.get('id') for t in old_targets}) == 7
            and len({r.get('targetId') for r in rows}) == 7,
            'QUALIFICATION_PRIOR_TARGET_AMBIGUOUS')
    for old, checked, row in zip(old_targets, validated, rows):
        require({k:v for k,v in checked.items() if k != 'literalRecognition'} == old
                and checked.get('literalRecognition') in ('html_link_feed_or_canonical', 'rss_or_atom_item_link',
                                                          'source_bound_rss_channel_link')
                and row.get('targetId') == old.get('id')
                and all(row.get(k) == old.get(k) for k in ('sourceId', 'url', 'expectedFormat', 'proof')),
                'QUALIFICATION_PRIOR_TARGET_MOVED_OR_CHANGED')
        require(row.get('qualified') is False and row.get('facts') == []
                and row.get('semanticAdmission') is False and row.get('coverageCredit') is False
                and all(type(row.get(k)) is int and row[k] == 0
                        for k in ('sourceChecksCredited', 'qualifiedSources', 'modelCalls')),
                'QUALIFICATION_PRIOR_ROW_CREDIT_INVALID')
    index = proof['priorTargetIndex']
    require(type(index) is int and 0 <= index < 7, 'QUALIFICATION_PRIOR_TARGET_INDEX_INVALID')
    row = rows[index]
    require(row.get('targetId') == proof['priorTargetId'] and digest(row) == proof['priorTargetSha256']
            and row.get('sourceId') == source['id'] and row.get('observation') == proof['observation']
            and row.get('budgetDenied') is False and not row.get('errorType')
            and row.get('reason') == 'RESPONSE_RETAINED_SCOPE_AND_HISTORY_REVIEW_REQUIRED'
            and row.get('qualified') is False and row.get('facts') == []
            and row.get('semanticAdmission') is False and row.get('coverageCredit') is False
            and all(type(row.get(k)) is int and row[k] == 0
                    for k in ('sourceChecksCredited', 'qualifiedSources', 'modelCalls')),
            'QUALIFICATION_PRIOR_EXPLICIT_ROW_DIFFERS_OR_FAILED')
    context = diagnostic.get('reservationContext')
    require(isinstance(context, dict) and context.get('contractSha256') == digest(contract)
            and isinstance(context.get('initialBudget'), dict) and isinstance(context.get('currentBudget'), dict)
            and type(context.get('fetchLimit')) is int
            and context['fetchLimit'] == contract['schedule'].get('maxFetchesPerRun', 5000),
            'QUALIFICATION_PRIOR_RESERVATION_CONTEXT_INVALID')
    initial, current = context['initialBudget'], context['currentBudget']
    require(all(type(b.get(k)) is int and b[k] >= 0 for b in (initial,current)
                for k in ('calls','documents','fetches'))
            and all(initial[k] == current[k] for k in ('calls','documents')),
            'QUALIFICATION_PRIOR_COUNTERS_INVALID')
    generic = diagnostic.get('sources')
    require(isinstance(generic, list) and all(isinstance(s,dict) and isinstance(s.get('fetchReservations'),list)
            for s in generic), 'QUALIFICATION_PRIOR_RESERVATION_INVENTORY_INVALID')
    source_rows = [s for s in generic if s.get('sourceId') == source['id']]
    require(len(source_rows) == 1 and source_rows[0].get('supplierId') == source['supplierId']
            and source_rows[0].get('registration') == 'candidate'
            and source_rows[0].get('qualified') is False and source_rows[0].get('facts') == []
            and source_rows[0].get('semanticAdmission') is False and source_rows[0].get('coverageCredit') is False,
            'QUALIFICATION_PRIOR_SOURCE_JOIN_DIFFERS')
    reservations = [r for s in generic for r in s['fetchReservations']]
    reservations += [r['reservation'] for r in rows if r.get('reservation') is not None]
    require(type(context.get('probeFetchReservations')) is int
            and len(reservations) == context['probeFetchReservations'] == current['fetches'] - initial['fetches']
            and type(qualification.get('chargedExplicitRequests')) is int
            and qualification['chargedExplicitRequests'] == sum(r.get('reservation') is not None for r in rows)
            and type(qualification.get('maximumExplicitRequests')) is int and qualification['maximumExplicitRequests'] == 7,
            'QUALIFICATION_PRIOR_RESERVATION_COUNTS_DIFFER')
    charges=[]
    for reservation in reservations:
        require(isinstance(reservation, dict) and reservation.get('budgetDay') == context.get('budgetDay')
                and type(reservation.get('fetchLimit')) is int and reservation['fetchLimit'] == context['fetchLimit']
                and type(reservation.get('chargedFetchCount')) is int
                and initial['fetches'] < reservation['chargedFetchCount'] <= current['fetches'] <= context['fetchLimit'],
                'QUALIFICATION_PRIOR_CHARGE_INVALID')
        charges.append(reservation['chargedFetchCount'])
    require(sorted(charges) == list(range(initial['fetches']+1,current['fetches']+1))
            and row.get('reservation') is not None, 'QUALIFICATION_PRIOR_UNRESERVED_OR_DUPLICATE_CHARGE')
    observed = json.loads(_qualification_reference(store, proof['observation'], r'objects/[a-f0-9]{64}'))
    maximum = context.get('maximumRuntimeSeconds')
    contract_runtime = contract['schedule'].get('maxRuntimeSeconds', 7200)
    require(type(maximum) is int and type(contract_runtime) is int and 0 < maximum <= min(contract_runtime,1200),
            'QUALIFICATION_PRIOR_RUNTIME_BOUND_INVALID')
    started = instant(context['startedAt']).astimezone(timezone.utc)
    fetched = instant(proof['fetchedAt']).astimezone(timezone.utc)
    checked = instant(diagnostic['checkedAt']).astimezone(timezone.utc)
    require(observed.get('requestedUrl') == row['url'] == observed.get('finalUrl')
            and all(moment.date().isoformat() == context['budgetDay'] for moment in (started,fetched,checked))
            and started <= fetched <= checked and (checked-started).total_seconds() <= maximum,
            'QUALIFICATION_PRIOR_REQUEST_OR_RESERVATION_TIME_DIFFERS')
    return observed


def validate_qualification_probe_plan(contract, store, path):
    """Validate one explicit qualification operation without changing schema 1."""
    raw = Path(path).read_bytes()
    require(0 < len(raw) <= 1_000_000, 'QUALIFICATION_PLAN_SIZE_INVALID')
    plan = json.loads(raw)
    if isinstance(plan, dict) and type(plan.get('schemaVersion')) is int and plan.get('schemaVersion') == 2:
        operation = plan.get('operation')
        if operation == BOUNDED_CANDIDATE_OPERATION:
            return _validate_bounded_candidate_plan(contract, store, path, raw, plan)
        if operation == DISABLED_QUALIFICATION_OPERATION:
            return _validate_disabled_qualification_plan(contract, path, raw, plan)
        require(False, 'QUALIFICATION_PLAN_OPERATION_UNKNOWN')
    return _validate_legacy_qualification_probe_plan(contract, store, path, raw=raw, plan=plan)


def _validate_disabled_qualification_plan(contract, path, raw, plan):
    """Validate the closed no-source operation for the exact current policy."""
    require(isinstance(plan, dict) and set(plan) == {
                'schemaVersion', 'operation', 'marketSha256', 'maxRequests', 'sources'}
            and type(plan.get('schemaVersion')) is int and plan['schemaVersion'] == 2
            and plan.get('operation') == DISABLED_QUALIFICATION_OPERATION
            and plan.get('marketSha256') == digest(contract)
            and type(plan.get('maxRequests')) is int and plan['maxRequests'] == 0
            and type(plan.get('sources')) is list and plan['sources'] == [],
            'DISABLED_QUALIFICATION_PLAN_SHAPE_OR_POLICY_INVALID')
    return {'rawSha256': digest(raw), 'canonicalSha256': digest(plan), 'path': str(path),
            'marketSha256': digest(contract), 'maxRequests': 0,
            'operation': DISABLED_QUALIFICATION_OPERATION, 'plan': plan}


def _candidate_adapter(source, index_url, mode):
    adapter = copy.deepcopy(source)
    adapter.update(kind='html_index', url=index_url, htmlCompleteness=mode)
    return adapter


def _validate_bounded_candidate_plan(contract, store, path, raw, plan):
    revision = plan.get('parserRevision', 1) if isinstance(plan, dict) else None
    require(type(revision) is int and revision in (1, 2, 3, 4)
            and (revision in (2, 3, 4) or 'parserRevision' not in plan),
            'BOUNDED_CANDIDATE_PARSER_REVISION_INVALID')
    fields = {
            'schemaVersion', 'operation', 'marketSha256', 'maxRequests',
            'maxIndexPagesPerSource', 'primarySamplesPerSource', 'sources'}
    if revision in (2, 3, 4):
        fields.add('parserRevision')
    bindings = {1: BOUNDED_CANDIDATE_BINDINGS, 2: BOUNDED_CANDIDATE_BINDINGS_V2,
                3: BOUNDED_CANDIDATE_BINDINGS_V3, 4: BOUNDED_CANDIDATE_BINDINGS_V4}[revision]
    require(isinstance(plan, dict) and set(plan) == fields
            and type(plan.get('schemaVersion')) is int and plan['schemaVersion'] == 2
            and plan.get('operation') == BOUNDED_CANDIDATE_OPERATION
            and plan.get('marketSha256') == digest(contract)
            and type(plan.get('maxRequests')) is int and plan['maxRequests'] == BOUNDED_CANDIDATE_MAX_REQUESTS
            and type(plan.get('maxIndexPagesPerSource')) is int
            and plan['maxIndexPagesPerSource'] == BOUNDED_CANDIDATE_LIMIT
            and type(plan.get('primarySamplesPerSource')) is int
            and plan['primarySamplesPerSource'] == BOUNDED_CANDIDATE_SAMPLE_LIMIT
            and isinstance(plan.get('sources'), list) and len(plan['sources']) == len(BOUNDED_CANDIDATE_BINDINGS),
            'BOUNDED_CANDIDATE_PLAN_SHAPE_OR_POLICY_INVALID')
    sources = {source['id']: source for source in contract['sources']}
    validated = []
    # Validate all source declarations and all independently retained start proofs
    # before the caller can make its first request.
    for row, (source_id, index_url, mode) in zip(plan['sources'], bindings):
        require(isinstance(row, dict) and set(row) == {
                'sourceId', 'originalSourceSha256', 'proposedAdapterSha256', 'startProof'}
                and row.get('sourceId') == source_id, 'BOUNDED_CANDIDATE_SOURCE_INVENTORY_INVALID')
        source = sources.get(source_id)
        require(isinstance(source, dict) and source.get('registration') == 'candidate'
                and source.get('kind') == 'official_discovery'
                and source.get('family') == 'official_announcements'
                and type(source.get('maxPages')) is int and source['maxPages'] == BOUNDED_CANDIDATE_LIMIT
                and row.get('originalSourceSha256') == digest(source),
                'BOUNDED_CANDIDATE_ORIGINAL_SOURCE_BINDING_INVALID')
        adapter = _candidate_adapter(source, index_url, mode)
        require(row.get('proposedAdapterSha256') == digest(adapter)
                and adapter.get('allowedHosts') == [urlsplit(index_url).hostname],
                'BOUNDED_CANDIDATE_PROPOSED_ADAPTER_BINDING_INVALID')
        proof = row.get('startProof')
        require(isinstance(proof, dict) and proof.get('type') == 'qualification_observation'
                and set(proof) == {'type', 'record', 'body', 'fetchedAt', 'observation',
                    'priorTargetId', 'priorTargetIndex', 'priorTargetSha256',
                    'priorPlanRawSha256', 'priorPlanCanonicalSha256', 'priorPlanReference'},
                'BOUNDED_CANDIDATE_START_PROOF_SHAPE_INVALID')
        recorded = json.loads(_qualification_reference(
            store, proof['record'], r'ci/source-probe-runs/[0-9]+-[0-9]+\.json'))
        proof_contract, proof_source = _qualification_proof_policy(recorded, proof, source, contract, store)
        require(isinstance(recorded, dict) and recorded.get('checkpointProfile') == 'source_probe'
                and recorded.get('contractSha256') == digest(proof_contract)
                and all(type(recorded.get(key)) is int and recorded[key] == 0
                        for key in ('modelCalls', 'sourceChecksCredited', 'qualifiedSources'))
                and recorded.get('semanticAdmission') is False and recorded.get('coverageCredit') is False
                and recorded.get('githubEventName') == 'workflow_dispatch'
                and recorded.get('githubRef') == 'refs/heads/main'
                and str(recorded.get('githubRunId')) + '-' + str(recorded.get('githubRunAttempt'))
                    == Path(proof['record']['key']).stem,
                'BOUNDED_CANDIDATE_START_PROVENANCE_INVALID')
        observed = _qualification_explicit_observation(recorded, proof, proof_source, proof_contract, store)
        require(observed.get('status') == 'fetched' and observed.get('httpStatus') == 200
                and observed.get('body') == proof.get('body') and observed.get('fetchedAt') == proof.get('fetchedAt')
                and observed.get('requestedUrl') == observed.get('finalUrl'),
                'BOUNDED_CANDIDATE_START_OBSERVATION_INVALID')
        start_body = decoded_discovery_body(_qualification_reference(store, proof['body'], r'objects/[a-f0-9]{64}'))
        start_page = Page(start_body.decode('utf8', errors='strict'), source_url=observed['finalUrl'])
        require(index_url in {urljoin(observed['finalUrl'], target) for target in start_page.canonicals}
                and urlsplit(index_url).hostname in source['allowedHosts'],
                'BOUNDED_CANDIDATE_START_INDEX_NOT_DISCLOSED')
        validated.append({'sourceId': source_id, 'originalSourceSha256': digest(source),
                          'proposedAdapterSha256': digest(adapter), 'indexUrl': index_url,
                          'mode': mode, 'source': copy.deepcopy(source), 'adapter': adapter,
                          'startProof': copy.deepcopy(proof)})
    require(len({row['sourceId'] for row in validated}) == len(BOUNDED_CANDIDATE_BINDINGS),
            'BOUNDED_CANDIDATE_SOURCE_JOIN_NOT_ONE_TO_ONE')
    return {'rawSha256': digest(raw), 'canonicalSha256': digest(plan), 'path': str(path),
            'marketSha256': digest(contract), 'maxRequests': BOUNDED_CANDIDATE_MAX_REQUESTS,
            'operation': BOUNDED_CANDIDATE_OPERATION, 'parserRevision': revision,
            'plan': plan, 'sources': validated}


def _validate_legacy_qualification_probe_plan(contract, store, path, *, raw=None, plan=None):
    """Read and prove the entire committed allowlist without writing or fetching."""
    raw = Path(path).read_bytes() if raw is None else raw
    require(0 < len(raw) <= 1_000_000, 'QUALIFICATION_PLAN_SIZE_INVALID')
    plan = json.loads(raw) if plan is None else plan
    require(isinstance(plan, dict) and set(plan) == {'schemaVersion', 'marketSha256', 'maxRequests', 'targets'}
            and type(plan['schemaVersion']) is int and plan['schemaVersion'] == 1
            and plan['marketSha256'] == digest(contract)
            and type(plan['maxRequests']) is int and plan['maxRequests'] == 7
            and isinstance(plan['targets'], list) and len(plan['targets']) == 7,
            'QUALIFICATION_PLAN_SHAPE_OR_POLICY_INVALID')
    sources = {s['id']: s for s in contract['sources']}
    identifiers, urls, validated, historical_bridges = set(), set(), [], []
    for target in plan['targets']:
        require(isinstance(target, dict) and set(target) == {'id', 'sourceId', 'url', 'expectedFormat', 'proof'}
                and isinstance(target['id'], str) and re.fullmatch(r'[a-z][a-z0-9-]{0,79}', target['id'])
                and target['id'] not in identifiers and isinstance(target['sourceId'], str)
                and target['sourceId'] in sources and target['expectedFormat'] in ('html', 'rss'),
                'QUALIFICATION_TARGET_INVALID')
        source = sources[target['sourceId']]
        require(source['registration'] == 'candidate', 'QUALIFICATION_SOURCE_MUST_REMAIN_CANDIDATE')
        url = _qualification_url(target['url'], source)
        require(url not in urls, 'QUALIFICATION_TARGET_DUPLICATE_URL')
        identifiers.add(target['id']); urls.add(url)
        proof = target['proof']
        require(isinstance(proof, dict) and proof.get('type') in ('source_observation', 'diagnostic_observation', 'qualification_observation'),
                'QUALIFICATION_PROOF_TYPE_INVALID')
        fields = {'type', 'record', 'body', 'fetchedAt'}
        if proof['type'] != 'source_observation':
            fields.add('observation')
            if 'historicalPolicyBridge' in proof:
                fields.add('historicalPolicyBridge')
        if proof['type'] == 'qualification_observation':
            fields.update(('priorTargetId','priorTargetIndex','priorTargetSha256',
                           'priorPlanRawSha256','priorPlanCanonicalSha256'))
            require(('priorPlanRaw' in proof) != ('priorPlanReference' in proof),
                    'QUALIFICATION_PRIOR_PLAN_EXACTLY_ONE_REPRESENTATION_REQUIRED')
            fields.add('priorPlanRaw' if 'priorPlanRaw' in proof else 'priorPlanReference')
        require(set(proof) == fields, 'QUALIFICATION_PROOF_SHAPE_INVALID')
        if proof['type'] == 'source_observation':
            observation = json.loads(_qualification_reference(store, proof['record'], r'observations/[a-f0-9]{64}\.json'))
            require(isinstance(observation, dict) and observation.get('observationId') == Path(proof['record']['key']).stem,
                    'QUALIFICATION_OBSERVATION_ID_DIFFERS')
            original = sources.get(observation.get('sourceId'))
            require(original and original['supplierId'] == source['supplierId']
                    and original['registration'] == 'verified'
                    and observation.get('requestedUrl') == original['url'], 'QUALIFICATION_SOURCE_BINDING_DIFFERS')
        else:
            recorded = json.loads(_qualification_reference(store, proof['record'], r'ci/source-probe-runs/[0-9]+-[0-9]+\.json'))
            require(isinstance(recorded, dict), 'QUALIFICATION_DIAGNOSTIC_PROVENANCE_INVALID')
            proof_contract, proof_source = _qualification_proof_policy(recorded, proof, source, contract, store)
            require(recorded.get('checkpointProfile') == 'source_probe'
                    and recorded.get('contractSha256') == digest(proof_contract)
                    and all(type(recorded.get(k)) is int and recorded[k] == 0
                            for k in ('modelCalls', 'sourceChecksCredited', 'qualifiedSources'))
                    and recorded.get('semanticAdmission') is False and recorded.get('coverageCredit') is False
                    and recorded.get('githubEventName') == 'workflow_dispatch' and recorded.get('githubRef') == 'refs/heads/main'
                    and str(recorded.get('githubRunId')) + '-' + str(recorded.get('githubRunAttempt')) == Path(proof['record']['key']).stem,
                    'QUALIFICATION_DIAGNOSTIC_PROVENANCE_INVALID')
            diagnostic = recorded.get('diagnostic', {})
            if proof['type'] == 'qualification_observation':
                observation = _qualification_explicit_observation(recorded, proof, proof_source, proof_contract, store)
            else:
                observation = _qualification_generic_observation(diagnostic, proof, proof_source, store)
            if 'historicalPolicyBridge' in proof:
                historical_bridges.append({'targetId': target['id'], 'record': copy.deepcopy(proof['record']),
                                          'historicalPolicyBridge': copy.deepcopy(proof['historicalPolicyBridge'])})
        require(isinstance(observation, dict) and observation.get('status') == 'fetched'
                and observation.get('httpStatus') == 200 and observation.get('body') == proof['body']
                and observation.get('fetchedAt') == proof['fetchedAt'], 'QUALIFICATION_OBSERVATION_BODY_OR_TIME_DIFFERS')
        require(isinstance(proof['fetchedAt'], str), 'QUALIFICATION_PROOF_TIMESTAMP_INVALID')
        instant(proof['fetchedAt'])
        _qualification_url(observation.get('requestedUrl'), source)
        base = _qualification_url(observation.get('finalUrl') or observation['requestedUrl'], source)
        body = decoded_discovery_body(_qualification_reference(store, proof['body'], r'objects/[a-f0-9]{64}'))
        content = body.lstrip()
        if content.startswith(b'<?xml') or re.match(br'<(rss|feed)\b', content):
            parsed = xml_links(body, base)
            require(parsed['kind'] in ('rss', 'feed'), 'QUALIFICATION_DISCLOSURE_XML_INVALID')
            literal_urls = set(parsed['links'])
            recognition = 'rss_or_atom_item_link'
            channels = {'delinea:official:1': ('https://delinea.com/news/rss.xml', 'https://delinea.com/news'),
                        'sonatype:official:1': ('https://www.sonatype.com/press-releases/rss.xml', 'https://www.sonatype.com/press-releases')}
            allowed = channels.get(source['id'])
            if proof['type'] == 'qualification_observation' and allowed and base == allowed[0] and url == allowed[1]:
                root = ET.fromstring(body)
                links = root.findall('./channel/link') if root.tag == 'rss' else []
                require(len(links) == 1 and links[0].text and links[0].text.strip() == url,
                        'QUALIFICATION_SOURCE_CHANNEL_DISCLOSURE_DIFFERS')
                literal_urls.add(url)
                recognition = 'source_bound_rss_channel_link'
        else:
            page = Page(body.decode('utf8', errors='strict'), source_url=base)
            literal_urls = {urljoin(base, u) for u in [*page.canonicals, *page.feeds, *(link['url'] for link in page.links)]}
            recognition = 'html_link_feed_or_canonical'
        require(url in literal_urls, 'QUALIFICATION_TARGET_NOT_LITERAL_IN_PROOF')
        validated.append({**copy.deepcopy(target), 'literalRecognition': recognition})
    result = {'rawSha256': digest(raw), 'canonicalSha256': digest(plan), 'path': str(path),
              'marketSha256': digest(contract), 'maxRequests': 7, 'plan': plan, 'targets': validated}
    if historical_bridges:
        result['historicalPolicyBridges'] = historical_bridges
    return result


def _qualification_generic_observation(diagnostic, proof, source, store):
    require(isinstance(diagnostic, dict) and isinstance(diagnostic.get('sources'), list),
            'QUALIFICATION_DIAGNOSTIC_SHAPE_INVALID')
    require(all(isinstance(r, dict) for r in diagnostic['sources']), 'QUALIFICATION_DIAGNOSTIC_SOURCE_SHAPE_INVALID')
    matches = [r for r in diagnostic['sources'] if r.get('sourceId') == source['id']]
    require(len(matches) == 1 and matches[0].get('supplierId') == source['supplierId']
            and matches[0].get('qualified') is False and matches[0].get('facts') == []
            and matches[0].get('registration') == 'candidate'
            and matches[0].get('semanticAdmission') is False and matches[0].get('coverageCredit') is False
            and isinstance(matches[0].get('observations'), list)
            and proof['observation'] in matches[0].get('observations', []),
            'QUALIFICATION_DIAGNOSTIC_SOURCE_BINDING_DIFFERS')
    reservations = matches[0].get('fetchReservations')
    require(isinstance(reservations, list) and all(isinstance(r, dict) for r in reservations),
            'QUALIFICATION_DIAGNOSTIC_RESERVATIONS_INVALID')
    observation = json.loads(_qualification_reference(store, proof['observation'], r'objects/[a-f0-9]{64}'))
    require(isinstance(observation, dict)
            and observation.get('requestedUrl') in [r.get('url') for r in reservations],
            'QUALIFICATION_DIAGNOSTIC_REQUEST_DIFFERS')
    return observation


def _probe_qualification_targets(contract, store, fetcher, budget, plan):
    sources = {s['id']: s for s in contract['sources']}
    results = []
    for target in plan['targets']:
        row = {'targetId': target['id'], 'sourceId': target['sourceId'], 'url': target['url'],
               'expectedFormat': target['expectedFormat'], 'proof': target['proof'],
               'qualified': False, 'semanticAdmission': False, 'coverageCredit': False,
               'sourceChecksCredited': 0, 'qualifiedSources': 0, 'modelCalls': 0, 'facts': [],
               'reservation': None, 'observation': None, 'budgetDenied': False}
        try:
            row['reservation'] = budget.reserve_fetch()
            budget.before_fetch()
            observed = fetcher.fetch(sources[target['sourceId']], target['url'])
            row['observation'] = store.put(observed)
            require(observed.get('requestedUrl') == target['url'], 'QUALIFICATION_RESPONSE_URL_DIFFERS')
            if observed.get('status') != 'fetched' or observed.get('httpStatus') != 200:
                row['reason'] = observed.get('errorCode') or 'HTTP_' + str(observed.get('httpStatus', 'UNAVAILABLE'))
            elif observed.get('finalUrl', target['url']) != target['url']:
                row['reason'] = 'QUALIFICATION_REDIRECTED'
            else:
                body = decoded_discovery_body(store.get(observed['body']))
                if target['expectedFormat'] == 'rss':
                    parsed = xml_links(body, target['url'])
                    require(parsed['kind'] in ('rss', 'feed'), 'QUALIFICATION_EXPECTED_RSS_OR_ATOM')
                    row.update(format=parsed['kind'], itemCount=len(parsed['links']), continuationCount=len(parsed['indexes']))
                    row['reason'] = ('RESPONSE_RETAINED_SCOPE_AND_HISTORY_REVIEW_REQUIRED' if parsed['links'] else
                                     'EMPTY_FEED_RETAINED_REQUIRES_QUALIFICATION')
                else:
                    require(re.search(br'<(?:html|head|body)\b', body[:8192], re.I), 'QUALIFICATION_EXPECTED_HTML')
                    page = Page(body.decode('utf8', errors='strict'), source_url=target['url'])
                    require(bool(page.readable.strip()), 'QUALIFICATION_EMPTY_HTML')
                    row.update(format='html', canonicals=page.canonicals, advertisedFeeds=page.feeds)
                    row['reason'] = 'RESPONSE_RETAINED_SCOPE_AND_HISTORY_REVIEW_REQUIRED'
        except ProbeReservationDenied as error:
            row.update(reason=error.reason, budgetDenied=True)
        except (ValueError, OSError, RuntimeError, ET.ParseError, KeyError, TypeError) as error:
            row.update(reason=str(error)[:160] if isinstance(error, ValueError) else type(error).__name__,
                       errorType=type(error).__name__)
        store.write_once(f"source-probes/qualification/{plan['canonicalSha256']}/{digest(row)}.json", row)
        results.append(row)
    return {'plan': plan, 'targets': results, 'maximumExplicitRequests': 7,
            'chargedExplicitRequests': sum(row['reservation'] is not None for row in results),
            'qualifiedSources': 0, 'sourceChecksCredited': 0, 'semanticAdmission': False,
            'coverageCredit': False, 'modelCalls': 0, 'facts': []}


def _candidate_primary_shape(body, url, parser_revision=1):
    """Check primary transport shape only; produce no fact or admission."""
    decoded = decoded_discovery_body(body)
    text = decoded.decode('utf8', errors='strict')
    nodes = list(IndexMarkup(text).root.walk())
    canonicals = [node.attrs.get('href') for node in nodes
                  if node.tag == 'link' and 'canonical' in node.attrs.get('rel', '').split()]
    headings = [' '.join(node.text.split()) for node in nodes if node.tag == 'h1']
    require(canonicals == [url], 'BOUNDED_CANDIDATE_PRIMARY_CANONICAL_DIFFERS')
    require(type(parser_revision) is int and parser_revision in (1, 2, 3, 4),
            'BOUNDED_CANDIDATE_PARSER_REVISION_INVALID')
    # Revision 4 changes index routes only; its primary shape is exactly V3.
    if parser_revision == 4:
        parser_revision = 3
    if parser_revision == 3:
        _v3_literal_article_href(url)
    if parser_revision in (2, 3) and urlsplit(url).netloc == 'press.pingidentity.com' \
            and any(node.tag == 'div' and 'wd_newsfeed_releases-detail' in node.classes for node in nodes):
        require(not headings, 'BOUNDED_CANDIDATE_PRIMARY_PING_DETAIL_AMBIGUOUS')
    if parser_revision in (2, 3) and not headings:
        parsed_url = urlsplit(url)
        path_allowed = bool(re.fullmatch(r'/\d{4}-\d{2}-\d{2}-[A-Za-z0-9_,-]+', parsed_url.path))
        if parser_revision == 3:
            path_allowed = ping_article_date(parsed_url.path, PING_HTML_MODE_V3) is not None
        require(parsed_url.scheme == 'https' and parsed_url.netloc == 'press.pingidentity.com'
                and not parsed_url.query and not parsed_url.fragment
                and path_allowed,
                'BOUNDED_CANDIDATE_PRIMARY_HEADING_AMBIGUOUS')
        mains = [node for node in nodes if node.tag == 'main']
        details = [node for node in nodes if node.tag == 'div'
                   and 'wd_newsfeed_releases-detail' in node.classes]
        titles = [node for node in nodes if node.tag == 'div' and 'wd_title' in node.classes]
        bodies = [node for node in nodes if node.tag == 'div'
                  and {'wd_body', 'wd_news_body'} <= node.classes]
        require(len(mains) == len(details) == len(titles) == len(bodies) == 1
                and all(node.closed for node in mains + details + titles + bodies)
                and details[0].inside(mains[0]) and titles[0].parent is details[0]
                and bodies[0].inside(details[0])
                and len(' '.join(bodies[0].text.split())) >= 100,
                'BOUNDED_CANDIDATE_PRIMARY_PING_DETAIL_AMBIGUOUS')
        opening = ' '.join(bodies[0].text.split())[:2000].lower()
        require(not any(marker in opening for marker in (
            'your request originates from an undeclared automated tool',
            'request rate threshold exceeded', 'access denied', 'verify you are human')),
            'SOURCE_BLOCK_PAGE')
        title = ' '.join(titles[0].text.split())
        document_titles = [' '.join(node.text.split()) for node in nodes if node.tag == 'title']
        og_titles = [node.attrs.get('content') for node in nodes
                     if node.tag == 'meta' and node.attrs.get('property') == 'og:title']
        og_urls = [node.attrs.get('content') for node in nodes
                   if node.tag == 'meta' and node.attrs.get('property') == 'og:url']
        require(title and document_titles == [title] and og_titles == [title] and og_urls == [url],
                'BOUNDED_CANDIDATE_PRIMARY_PING_METADATA_DIFFERS')
        headings = [title]
    require(len(headings) == 1 and headings[0], 'BOUNDED_CANDIDATE_PRIMARY_HEADING_AMBIGUOUS')
    from documents import readable_document
    readable = readable_document(body, 'text/html')
    date_values = []
    for node in nodes:
        if node.tag == 'time' and node.attrs.get('datetime'):
            date_values.append({'kind': 'time_datetime', 'value': node.attrs['datetime']})
        elif node.tag == 'meta' and node.attrs.get('property') in ('article:published_time', 'datePublished'):
            value = node.attrs.get('content', '')
            if value:
                date_values.append({'kind': 'published_meta', 'value': value})
    return {'canonical': canonicals[0], 'heading': headings[0], 'readableCharacters': len(readable.strip()),
            'dateMetadata': date_values, 'dateMetadataState': 'one_or_more_present' if date_values else 'unknown'}


def _store_bounded_candidate_observation(store, binding, url, observed):
    """Wrap an immutable raw fetch result with the candidate identity that requested it."""
    raw_reference = store.put(observed)
    return store.put({'schemaVersion': 1, 'sourceId': binding['sourceId'],
                      'adapterSha256': binding['proposedAdapterSha256'],
                      'requestedUrl': url, 'rawObservation': raw_reference})


def _read_bounded_candidate_observation(store, reference, binding, url):
    wrapper = json.loads(_qualification_reference(store, reference, r'objects/[a-f0-9]{64}'))
    require(isinstance(wrapper, dict) and set(wrapper) == {
            'schemaVersion', 'sourceId', 'adapterSha256', 'requestedUrl', 'rawObservation'}
            and type(wrapper.get('schemaVersion')) is int and wrapper['schemaVersion'] == 1
            and wrapper.get('sourceId') == binding['sourceId']
            and wrapper.get('adapterSha256') == binding['proposedAdapterSha256']
            and wrapper.get('requestedUrl') == url,
            'BOUNDED_CANDIDATE_OBSERVATION_SOURCE_BINDING_INVALID')
    observed = json.loads(_qualification_reference(store, wrapper['rawObservation'], r'objects/[a-f0-9]{64}'))
    require(isinstance(observed, dict), 'BOUNDED_CANDIDATE_RAW_OBSERVATION_INVALID')
    return observed


def _replay_bounded_candidate_result(contract, store, plan, report, raw_plan_bytes):
    """Replay a bounded diagnostic against the exact immutable plan bytes supplied."""
    require(isinstance(report, dict) and type(report.get('schemaVersion')) is int and report.get('schemaVersion') == 1
            and report.get('operation') == BOUNDED_CANDIDATE_OPERATION
            and report.get('contractSha256') == digest(contract)
            and report.get('planRawSha256') == plan['rawSha256']
            and report.get('planCanonicalSha256') == plan['canonicalSha256']
            and report.get('qualified') is False and report.get('semanticAdmission') is False
            and report.get('coverageCredit') is False and report.get('facts') == []
            and all(type(report.get(key)) is int and report[key] == 0
                    for key in ('sourceChecksCredited', 'qualifiedSources', 'modelCalls'))
            and report.get('newFactIds') == [],
            'BOUNDED_CANDIDATE_REPORT_CREDIT_OR_POLICY_INVALID')
    plan_reference = report.get('planReference')
    require(isinstance(plan_reference, dict)
            and _qualification_reference(store, plan_reference, r'objects/[a-f0-9]{64}')
            == raw_plan_bytes
            and digest(raw_plan_bytes) == plan['rawSha256'],
            'BOUNDED_CANDIDATE_PLAN_REFERENCE_DIFFERS')
    context = report.get('reservationContext')
    require(isinstance(context, dict) and context.get('contractSha256') == digest(contract)
            and isinstance(context.get('initialBudget'), (dict, type(None)))
            and isinstance(context.get('currentBudget'), dict)
            and type(context.get('fetchLimit')) is int
            and context['fetchLimit'] == contract['schedule'].get('maxFetchesPerRun', 5000)
            and type(context.get('probeFetchReservations')) is int
            and context['probeFetchReservations'] >= 0
            and context.get('budgetDay') == instant(context.get('startedAt')).astimezone(timezone.utc).date().isoformat()
            and type(context.get('maximumRuntimeSeconds')) is int
            and 0 < context['maximumRuntimeSeconds'] <= 1200,
            'BOUNDED_CANDIDATE_RESERVATION_CONTEXT_INVALID')
    started = instant(context['startedAt']).astimezone(timezone.utc)
    checked = instant(report['checkedAt']).astimezone(timezone.utc)
    denial_reasons = {denial.get('reason') for source_result in report.get('sources', [])
                      for denial in source_result.get('reservationDenials', [])}
    outer_completion_denial = report.get('completionDenial')
    if outer_completion_denial is not None:
        require(outer_completion_denial in ('SOURCE_PROBE_DEADLINE_EXCEEDED',
                                            'SOURCE_PROBE_UTC_DAY_CHANGED'),
                'BOUNDED_CANDIDATE_COMPLETION_GUARD_INVALID')
        denial_reasons.add(outer_completion_denial)
    require(started <= checked
            and (checked.date().isoformat() == context['budgetDay']
                 or 'SOURCE_PROBE_UTC_DAY_CHANGED' in denial_reasons)
            and ((checked-started).total_seconds() <= context['maximumRuntimeSeconds']
                 or 'SOURCE_PROBE_DEADLINE_EXCEEDED' in denial_reasons),
            'BOUNDED_CANDIDATE_RUN_TIME_INVALID')
    initial_budget = context['initialBudget'] or {'calls': 0, 'documents': 0, 'fetches': 0}
    current_budget = context['currentBudget']
    require(all(type(row.get(key)) is int and row[key] >= 0
                for row in (initial_budget, current_budget) for key in ('calls', 'documents', 'fetches'))
            and initial_budget['calls'] == current_budget['calls']
            and initial_budget['documents'] == current_budget['documents'],
            'BOUNDED_CANDIDATE_NONFETCH_LEDGER_CHANGED')
    initial_count = initial_budget.get('fetches', 0)
    current_count = current_budget.get('fetches')
    require(type(initial_count) is int and initial_count >= 0 and type(current_count) is int
            and initial_count <= current_count <= context['fetchLimit'],
            'BOUNDED_CANDIDATE_LEDGER_COUNTERS_INVALID')
    sources = report.get('sources')
    require(isinstance(sources, list) and len(sources) == len(plan['sources']),
            'BOUNDED_CANDIDATE_SOURCE_REPORT_INVALID')
    charges, request_count = [], 0
    for source_result, binding in zip(sources, plan['sources']):
        require(source_result.get('sourceId') == binding['sourceId']
                and source_result.get('originalSourceSha256') == binding['originalSourceSha256']
                and source_result.get('proposedAdapterSha256') == binding['proposedAdapterSha256']
                and source_result.get('registration') == 'candidate'
                and source_result.get('qualified') is False and source_result.get('facts') == []
                and source_result.get('semanticAdmission') is False and source_result.get('coverageCredit') is False
                and all(type(source_result.get(key)) is int and source_result[key] == 0
                        for key in ('sourceChecksCredited', 'qualifiedSources', 'modelCalls'))
                and source_result.get('newFactIds') == [],
                'BOUNDED_CANDIDATE_SOURCE_REPORT_JOIN_INVALID')
        observations = source_result.get('observations')
        require(isinstance(observations, list) and len(observations) <= BOUNDED_CANDIDATE_LIMIT,
                'BOUNDED_CANDIDATE_PAGE_INVENTORY_INVALID')
        highest, visited, items, dates = 1, set(), set(), {}
        terminal, expected_url = False, binding['indexUrl']
        consumed_pages = 0
        for page_number, page_row in enumerate(observations, 1):
            consumed_pages += 1
            require(isinstance(page_row, dict) and set(page_row) == {'url', 'observation', 'parser'},
                    'BOUNDED_CANDIDATE_PAGE_ROW_INVALID')
            url = page_row['url']
            require(url == expected_url and url not in visited and page_number <= BOUNDED_CANDIDATE_LIMIT,
                    'BOUNDED_CANDIDATE_PAGE_SEQUENCE_INVALID')
            visited.add(url)
            observed = _read_bounded_candidate_observation(store, page_row['observation'], binding, url)
            if observed.get('status') != 'fetched' or observed.get('httpStatus') != 200:
                require(page_row['parser'] is None,
                        'BOUNDED_CANDIDATE_FAILED_PAGE_ROW_INVALID')
                if isinstance(observed.get('fetchedAt'), str):
                    failed_at = instant(observed['fetchedAt']).astimezone(timezone.utc)
                    require(started <= failed_at <= checked and failed_at.date().isoformat() == context['budgetDay'],
                            'BOUNDED_CANDIDATE_FAILED_PAGE_TIME_INVALID')
                expected_url = None
                break
            if page_row['parser'] == {'error': 'BOUNDED_CANDIDATE_INDEX_RESPONSE_URL_DIFFERS'}:
                require(observed.get('requestedUrl') != url or observed.get('finalUrl') != url,
                        'BOUNDED_CANDIDATE_RECORDED_URL_FAILURE_NOT_PRESENT')
                expected_url = None
                break
            require(isinstance(observed, dict) and observed.get('requestedUrl') == url
                    and observed.get('finalUrl') == url and observed.get('status') == 'fetched'
                    and observed.get('httpStatus') == 200 and isinstance(observed.get('body'), dict),
                    'BOUNDED_CANDIDATE_PAGE_OBSERVATION_INVALID')
            fetched = instant(observed.get('fetchedAt')).astimezone(timezone.utc)
            if page_row['parser'] == {'error': 'BOUNDED_CANDIDATE_INDEX_RESPONSE_TIME_INVALID'}:
                require(fetched.date().isoformat() != context['budgetDay'] or fetched < started or fetched > checked,
                        'BOUNDED_CANDIDATE_RECORDED_TIME_FAILURE_NOT_PRESENT')
                expected_url = None
                break
            require(started <= fetched <= checked and fetched.date().isoformat() == context['budgetDay'],
                    'BOUNDED_CANDIDATE_PAGE_TIME_INVALID')
            body = _qualification_reference(store, observed['body'], r'objects/[a-f0-9]{64}')
            try:
                parsed = parse_source_html_index(binding['adapter'], url, body, highest, observed['fetchedAt'])
            except (ValueError, TypeError, KeyError) as error:
                require(page_row['parser'] == {'error': str(error)[:160]},
                        'BOUNDED_CANDIDATE_PAGE_PARSER_FAILURE_DIFFERS')
                expected_url = None
                break
            snapshot = {'currentPage': parsed['currentPage'], 'highestPage': parsed['highestPage'],
                        'items': sorted(parsed['items']), 'dates': parsed['dates'], 'next': parsed['next'],
                        'terminalProved': parsed['terminalProved']}
            require(page_row['parser'] == snapshot and parsed['currentPage'] == page_number,
                    'BOUNDED_CANDIDATE_PAGE_PARSER_REPLAY_DIFFERS')
            overlap = items & parsed['items']
            date_conflict = any(item in dates and dates[item] != value
                                for item, value in parsed['dates'].items())
            if overlap or date_conflict:
                require(source_result.get('reason') == ('BOUNDED_CANDIDATE_CROSS_PAGE_DUPLICATE'
                        if overlap else 'BOUNDED_CANDIDATE_CROSS_PAGE_DATE_CONFLICT'),
                        'BOUNDED_CANDIDATE_CROSS_PAGE_CONFLICT_REASON_DIFFERS')
                items.update(parsed['items'])
                for item, value in parsed['dates'].items():
                    dates.setdefault(item, value)
                expected_url = None
                break
            items.update(parsed['items']); dates.update(parsed['dates']); highest = parsed['highestPage']
            terminal = bool(parsed['terminalProved'])
            expected_url = parsed['next']
            if expected_url is None:
                break
        require(consumed_pages == len(observations), 'BOUNDED_CANDIDATE_UNCONSUMED_PAGE_ROWS')
        require(source_result.get('inventory') == {'items': sorted(items), 'dates': dates}
                and source_result.get('indexComplete') is (terminal and bool(observations)
                    and len(observations) <= BOUNDED_CANDIDATE_LIMIT)
                and source_result.get('terminalProved') is terminal,
                'BOUNDED_CANDIDATE_INVENTORY_OR_COMPLETION_DIFFERS')
        sample = source_result.get('primarySample')
        if sample is not None:
            require(isinstance(sample, dict) and sample.get('url') == (sorted(items)[0] if items else None)
                    and isinstance(sample.get('observation'), dict), 'BOUNDED_CANDIDATE_SAMPLE_SELECTION_INVALID')
            observed = _read_bounded_candidate_observation(store, sample['observation'], binding, sample['url'])
            if observed.get('status') == 'fetched' and observed.get('httpStatus') == 200:
                if observed.get('finalUrl') != sample['url']:
                    expected_reason = (observed.get('errorCode') or
                                       'BOUNDED_CANDIDATE_PRIMARY_RESPONSE_INVALID')
                    require(sample.get('shape') is None and source_result.get('reason') == expected_reason,
                            'BOUNDED_CANDIDATE_SAMPLE_RESPONSE_URL_INVALID')
                elif observed.get('requestedUrl') != sample['url']:
                    expected_reason = (observed.get('errorCode') or
                                       'BOUNDED_CANDIDATE_PRIMARY_RESPONSE_INVALID')
                    require(sample.get('shape') is None and source_result.get('reason') == expected_reason,
                            'BOUNDED_CANDIDATE_SAMPLE_RESPONSE_URL_INVALID')
                else:
                    require(isinstance(observed.get('body'), dict), 'BOUNDED_CANDIDATE_SAMPLE_RESPONSE_URL_INVALID')
                    fetched = instant(observed.get('fetchedAt')).astimezone(timezone.utc)
                    if fetched.date().isoformat() != context['budgetDay'] or fetched < started or fetched > checked:
                        require(sample.get('shape') is None and source_result.get('reason') ==
                                'BOUNDED_CANDIDATE_PRIMARY_RESPONSE_TIME_INVALID',
                                'BOUNDED_CANDIDATE_SAMPLE_TIME_INVALID')
                    else:
                        body = _qualification_reference(store, observed['body'], r'objects/[a-f0-9]{64}')
                        try:
                            shape = _candidate_primary_shape(body, sample['url'], plan.get('parserRevision', 1))
                        except (ValueError, TypeError, KeyError) as error:
                            shape = {'error': str(error)[:160]}
                        require(sample.get('shape') == shape, 'BOUNDED_CANDIDATE_SAMPLE_SHAPE_REPLAY_DIFFERS')
            else:
                require(sample.get('shape') is None, 'BOUNDED_CANDIDATE_FAILED_SAMPLE_HAS_SHAPE')
        elif items:
            require(source_result.get('sampleReason'), 'BOUNDED_CANDIDATE_SAMPLE_MISSING_REASON')
        request_rows = source_result.get('requestReservations')
        require(isinstance(request_rows, list), 'BOUNDED_CANDIDATE_REQUEST_RESERVATIONS_INVALID')
        local_observations = [row['observation'] for row in observations]
        if sample is not None:
            local_observations.append(sample['observation'])
        observed_refs = list(local_observations)
        request_refs = []
        for request_row in request_rows:
            require(isinstance(request_row, dict) and isinstance(request_row.get('reservation'), dict)
                    and (request_row.get('observation') is None or isinstance(request_row.get('observation'), dict)),
                    'BOUNDED_CANDIDATE_REQUEST_RESERVATION_JOIN_INVALID')
            if request_row.get('observation') is not None:
                require(set(request_row) == {'url', 'reservation', 'observation'},
                        'BOUNDED_CANDIDATE_REQUEST_RESERVATION_JOIN_INVALID')
            else:
                require((set(request_row) == {'url', 'reservation', 'observation', 'denial'}
                         and isinstance(request_row.get('denial'), str)
                         and any(denial.get('url') == request_row.get('url')
                                 and denial.get('reason') == request_row['denial']
                                 and denial.get('reservationCharged') is True
                                 and denial.get('reservation') == request_row['reservation']
                                 for denial in source_result.get('reservationDenials', []))
                         or set(request_row) == {'url', 'reservation', 'observation', 'transportOrParseError'}
                         and isinstance(request_row.get('transportOrParseError'), str)
                         and source_result.get('reason') == request_row['transportOrParseError']),
                        'BOUNDED_CANDIDATE_REQUEST_RESERVATION_JOIN_INVALID')
            reservation = request_row['reservation']
            require(reservation.get('budgetDay') == context['budgetDay']
                    and reservation.get('fetchLimit') == context['fetchLimit']
                    and type(reservation.get('chargedFetchCount')) is int
                    and initial_count < reservation['chargedFetchCount'] <= current_count,
                    'BOUNDED_CANDIDATE_REQUEST_CHARGE_INVALID')
            charges.append(reservation['chargedFetchCount'])
            request_count += 1
            observation_ref = request_row.get('observation')
            if observation_ref is None:
                require(request_row.get('denial') or request_row.get('transportOrParseError'),
                        'BOUNDED_CANDIDATE_CHARGED_REQUEST_WITHOUT_OUTCOME')
                continue
            require(observation_ref in observed_refs and request_row.get('url') in
                    [row['url'] for row in observations] + ([sample['url']] if sample is not None else []),
                    'BOUNDED_CANDIDATE_REQUEST_OBSERVATION_JOIN_INVALID')
            observed = _read_bounded_candidate_observation(store, observation_ref, binding, request_row['url'])
            request_refs.append(observation_ref)
        require([ref['sha256'] for ref in request_refs] == [ref['sha256'] for ref in observed_refs],
                'BOUNDED_CANDIDATE_REQUEST_OBSERVATION_INVENTORY_DIFFERS')
    denial_counts = Counter()
    for source_result in sources:
        completion_guards = []
        for denial in source_result.get('reservationDenials', []):
            require(isinstance(denial, dict) and isinstance(denial.get('reason'), str),
                    'BOUNDED_CANDIDATE_DENIAL_ROW_INVALID')
            denial_counts[denial['reason']] += 1
            reservation = denial.get('reservation')
            if denial.get('reservationCharged'):
                require(isinstance(reservation, dict)
                        and any(row.get('reservation') == reservation and row.get('denial') == denial['reason']
                                for row in source_result.get('requestReservations', [])),
                        'BOUNDED_CANDIDATE_CHARGED_DENIAL_JOIN_INVALID')
            else:
                require(reservation is None, 'BOUNDED_CANDIDATE_UNCHARGED_DENIAL_HAS_RESERVATION')
            if denial.get('phase') == 'post_response_completion_guard':
                require(denial.get('reservationCharged') is False
                        and denial.get('reason') in ('SOURCE_PROBE_DEADLINE_EXCEEDED', 'SOURCE_PROBE_UTC_DAY_CHANGED'),
                        'BOUNDED_CANDIDATE_COMPLETION_GUARD_INVALID')
                completion_guards.append(denial['reason'])
        guard_reason = source_result.get('completionGuardReason')
        require((guard_reason is None and not completion_guards)
                or (len(completion_guards) == 1 and guard_reason == completion_guards[0]),
                'BOUNDED_CANDIDATE_COMPLETION_GUARD_INVALID')
    expected_context_denials = Counter(denial_counts)
    if outer_completion_denial is not None:
        expected_context_denials[outer_completion_denial] += 1
    require(request_count <= BOUNDED_CANDIDATE_MAX_REQUESTS and len(charges) == len(set(charges))
            and len(charges) == context.get('probeFetchReservations')
            and sorted(charges) == list(range(initial_count + 1, current_count + 1))
            and current_count - initial_count == len(charges)
            and dict(expected_context_denials) == context.get('reservationDenials', {})
            and report.get('budgetDenied') is bool(expected_context_denials)
            and report.get('executionCompleted') is (not bool(expected_context_denials)),
            'BOUNDED_CANDIDATE_TOTAL_REQUEST_BOUND_INVALID')
    return True


def _verify_bounded_candidate_result(contract, store, plan, report):
    """Replay a live diagnostic and require the current plan file to remain exact."""
    require(isinstance(plan, dict) and isinstance(plan.get('path'), str),
            'BOUNDED_CANDIDATE_CURRENT_PLAN_PATH_REQUIRED')
    raw = Path(plan['path']).read_bytes()
    require(digest(raw) == plan.get('rawSha256'), 'BOUNDED_CANDIDATE_CURRENT_PLAN_CHANGED')
    return _replay_bounded_candidate_result(contract, store, plan, report, raw)


def replay_bounded_candidate_diagnostic(original_contract, store, run_record_reference, raw_plan_reference):
    """Replay one archived schema-2 diagnostic without consulting the live plan path.

    The caller must authenticate the run record's external Actions provenance. This
    function checks the immutable record reference and its internal execution envelope.
    It returns diagnostic evidence only; it never changes a source declaration or grants
    semantic, intake, or coverage credit.
    """
    record_raw = _qualification_reference(
        store, run_record_reference, r'ci/source-probe-runs/[0-9]+-[0-9]+\.json')
    record = json.loads(record_raw)
    require(isinstance(record, dict)
            and type(record.get('schemaVersion')) is int and record['schemaVersion'] == 1
            and record.get('checkpointProfile') == 'source_probe'
            and type(record.get('githubRunId')) in (str, int)
            and str(record.get('githubRunId')).isdigit()
            and type(record.get('githubRunAttempt')) is int and record['githubRunAttempt'] > 0
            and run_record_reference['key'] ==
                f"ci/source-probe-runs/{record['githubRunId']}-{record['githubRunAttempt']}.json"
            and record.get('githubEventName') == 'workflow_dispatch'
            and record.get('githubRef') == 'refs/heads/main'
            and isinstance(record.get('appRevision'), str)
            and re.fullmatch(r'[a-f0-9]{40}', record['appRevision'])
            and record.get('contractSha256') == digest(original_contract)
            and type(record.get('apiFallback')) is bool and record['apiFallback'] is False
            and type(record.get('modelCalls')) is int and record['modelCalls'] == 0
            and type(record.get('sourceChecksCredited')) is int and record['sourceChecksCredited'] == 0
            and type(record.get('qualifiedSources')) is int and record['qualifiedSources'] == 0
            and type(record.get('semanticAdmission')) is bool and record['semanticAdmission'] is False
            and type(record.get('coverageCredit')) is bool and record['coverageCredit'] is False
            and record.get('publication') == {'published': False,
                'reason': 'SOURCE_PROBE_DIAGNOSTIC_ONLY'}
            and isinstance(record.get('diagnostic'), dict),
            'BOUNDED_CANDIDATE_HISTORICAL_RUN_ENVELOPE_INVALID')
    report = record['diagnostic']
    require(report.get('operation') == BOUNDED_CANDIDATE_OPERATION
            and report.get('contractSha256') == digest(original_contract)
            and report.get('planReference') == raw_plan_reference
            and isinstance(raw_plan_reference, dict)
            and set(raw_plan_reference) == {'key', 'sha256', 'bytes'},
            'BOUNDED_CANDIDATE_HISTORICAL_PLAN_JOIN_INVALID')
    raw = _qualification_reference(store, raw_plan_reference, r'objects/[a-f0-9]{64}')
    try:
        plan_data = json.loads(raw)
    except (ValueError, TypeError):
        require(False, 'BOUNDED_CANDIDATE_HISTORICAL_PLAN_JSON_INVALID')
    plan = _validate_bounded_candidate_plan(original_contract, store, None, raw, plan_data)
    require(type(record.get('executionCompleted')) is bool
            and ((record.get('outcome') == 'completed_diagnostic'
                  and record['executionCompleted'] and report.get('executionCompleted') is True)
                 or (record.get('outcome') == 'budget_denied'
                     and not record['executionCompleted'] and report.get('executionCompleted') is False)
                 or (record.get('outcome') == 'cancelled' and not record['executionCompleted'])),
            'BOUNDED_CANDIDATE_HISTORICAL_OUTCOME_INVALID')
    _replay_bounded_candidate_result(original_contract, store, plan, report, raw)
    return {'plan': plan, 'report': report}


def _probe_bounded_candidate_traversal(contract, store, fetcher, budget, plan):
    """Run the explicit three-source diagnostic; never invoke generic fanout."""
    require(plan.get('operation') == BOUNDED_CANDIDATE_OPERATION, 'BOUNDED_CANDIDATE_OPERATION_REQUIRED')
    raw = Path(plan['path']).read_bytes()
    require(digest(raw) == plan['rawSha256'], 'BOUNDED_CANDIDATE_CURRENT_PLAN_CHANGED')
    plan_reference = store.put(raw)
    started_at = budget.started_at
    results = []
    global_denial = None
    for binding in plan['sources']:
        result = {'sourceId': binding['sourceId'], 'supplierId': binding['source']['supplierId'],
                  'registration': 'candidate', 'originalSourceSha256': binding['originalSourceSha256'],
                  'proposedAdapterSha256': binding['proposedAdapterSha256'], 'observations': [],
                  'inventory': {'items': [], 'dates': {}}, 'indexComplete': False,
                  'terminalProved': False, 'primarySample': None, 'requestReservations': [],
                  'qualified': False, 'semanticAdmission': False, 'coverageCredit': False,
                  'sourceChecksCredited': 0, 'qualifiedSources': 0, 'modelCalls': 0, 'facts': [], 'newFactIds': []}
        items, dates, visited = set(), {}, set()
        highest, url = 1, binding['indexUrl']
        for page_number in range(1, BOUNDED_CANDIDATE_LIMIT + 1):
            if global_denial:
                result['reason'] = global_denial
                break
            if url is None:
                break
            if url in visited:
                result['reason'] = 'BOUNDED_CANDIDATE_PAGINATION_LOOP'
                break
            visited.add(url)
            reservation = None
            try:
                reservation = budget.reserve_fetch()
                budget.before_fetch()
            except ProbeReservationDenied as error:
                result['reservationDenials'] = [{'url': url, 'reason': error.reason,
                    'budgetDay': budget.day, 'reservationCharged': reservation is not None,
                    'reservation': reservation}]
                if reservation is not None:
                    result['requestReservations'].append({'url': url, 'reservation': reservation,
                                                          'observation': None, 'denial': error.reason})
                result['reason'] = error.reason
                global_denial = error.reason
                break
            try:
                observed = fetcher.fetch(binding['adapter'], url)
                observation_ref = _store_bounded_candidate_observation(store, binding, url, observed)
                result['requestReservations'].append({'url': url, 'reservation': reservation,
                                                      'observation': observation_ref})
                page_row = {'url': url, 'observation': observation_ref, 'parser': None}
                result['observations'].append(page_row)
                if observed.get('status') != 'fetched' or observed.get('httpStatus') != 200:
                    result['reason'] = observed.get('errorCode') or 'BOUNDED_CANDIDATE_INDEX_UNAVAILABLE'
                    break
                if observed.get('requestedUrl') != url or observed.get('finalUrl') != url:
                    page_row['parser'] = {'error': 'BOUNDED_CANDIDATE_INDEX_RESPONSE_URL_DIFFERS'}
                    result['reason'] = 'BOUNDED_CANDIDATE_INDEX_RESPONSE_URL_DIFFERS'
                    break
                fetched = instant(observed.get('fetchedAt')).astimezone(timezone.utc)
                checked_now = instant(budget.clock()).astimezone(timezone.utc)
                if fetched.date().isoformat() != budget.day or budget.started > fetched or fetched > checked_now:
                    page_row['parser'] = {'error': 'BOUNDED_CANDIDATE_INDEX_RESPONSE_TIME_INVALID'}
                    result['reason'] = 'BOUNDED_CANDIDATE_INDEX_RESPONSE_TIME_INVALID'
                    break
                body = _qualification_reference(store, observed['body'], r'objects/[a-f0-9]{64}')
                try:
                    parsed = parse_source_html_index(binding['adapter'], url, body, highest, observed['fetchedAt'])
                except (ValueError, TypeError, KeyError) as error:
                    page_row['parser'] = {'error': str(error)[:160]}
                    raise
                require(parsed.get('currentPage') == page_number, 'BOUNDED_CANDIDATE_PAGE_SEQUENCE_DIFFERS')
                snapshot = {'currentPage': parsed['currentPage'], 'highestPage': parsed['highestPage'],
                            'items': sorted(parsed['items']), 'dates': parsed['dates'], 'next': parsed['next'],
                            'terminalProved': parsed['terminalProved']}
                page_row['parser'] = snapshot
                overlap = items & parsed['items']
                date_conflict = any(item in dates and dates[item] != value
                                    for item, value in parsed['dates'].items())
                if overlap or date_conflict:
                    items.update(parsed['items'])
                    for item, value in parsed['dates'].items():
                        dates.setdefault(item, value)
                    result['reason'] = ('BOUNDED_CANDIDATE_CROSS_PAGE_DUPLICATE' if overlap
                                        else 'BOUNDED_CANDIDATE_CROSS_PAGE_DATE_CONFLICT')
                    break
                items.update(parsed['items']); dates.update(parsed['dates']); highest = parsed['highestPage']
                if parsed.get('terminalProved'):
                    result['terminalProved'] = True
                    result['indexComplete'] = True
                    result['reason'] = 'COMPLETE_DIAGNOSTIC_INVENTORY'
                    break
                if parsed.get('next') is None:
                    result['reason'] = 'BOUNDED_CANDIDATE_TERMINAL_UNPROVED'
                    break
                if page_number == BOUNDED_CANDIDATE_LIMIT:
                    result['reason'] = 'BOUNDED_CANDIDATE_PAGE_CAP_REACHED'
                    break
                url = parsed['next']
            except ProbeReservationDenied as error:
                # The reservation remains charged; no response observation exists.
                result['reservationDenials'] = [{'url': url, 'reason': error.reason,
                    'budgetDay': budget.day, 'reservationCharged': True, 'reservation': reservation}]
                if reservation is not None:
                    result['requestReservations'].append({'url': url, 'reservation': reservation,
                                                          'observation': None, 'denial': error.reason})
                result['reason'] = error.reason
                global_denial = error.reason
                break
            except (ValueError, OSError, RuntimeError, KeyError, TypeError) as error:
                result['reason'] = str(error)[:160] if isinstance(error, ValueError) else type(error).__name__
                if reservation is not None and not any(row['url'] == url for row in result['requestReservations']):
                    result['requestReservations'].append({'url': url, 'reservation': reservation,
                                                          'observation': None, 'transportOrParseError': result['reason']})
                break
        if result.get('indexComplete') and result['observations']:
            result['inventory'] = {'items': sorted(items), 'dates': dates}
        else:
            result['inventory'] = {'items': sorted(items), 'dates': dates}
        if items and not global_denial:
            sample_url = sorted(items)[0]
            reservation = None
            try:
                reservation = budget.reserve_fetch()
                budget.before_fetch()
                observed = fetcher.fetch(binding['adapter'], sample_url)
                observation_ref = _store_bounded_candidate_observation(store, binding, sample_url, observed)
                result['requestReservations'].append({'url': sample_url, 'reservation': reservation,
                                                      'observation': observation_ref})
                result['primarySample'] = {'url': sample_url, 'observation': observation_ref, 'shape': None}
                if observed.get('requestedUrl') != sample_url or observed.get('finalUrl') != sample_url \
                        or observed.get('status') != 'fetched' or observed.get('httpStatus') != 200:
                    result['reason'] = observed.get('errorCode') or 'BOUNDED_CANDIDATE_PRIMARY_RESPONSE_INVALID'
                else:
                    fetched = instant(observed.get('fetchedAt')).astimezone(timezone.utc)
                    checked_now = instant(budget.clock()).astimezone(timezone.utc)
                    require(fetched.date().isoformat() == budget.day and budget.started <= fetched
                            and fetched <= checked_now,
                            'BOUNDED_CANDIDATE_PRIMARY_RESPONSE_TIME_INVALID')
                    body = _qualification_reference(store, observed['body'], r'objects/[a-f0-9]{64}')
                    try:
                        result['primarySample']['shape'] = _candidate_primary_shape(
                            body, sample_url, plan.get('parserRevision', 1))
                    except (ValueError, TypeError, KeyError) as error:
                        result['primarySample']['shape'] = {'error': str(error)[:160]}
                        result['reason'] = str(error)[:160]
                    if not result['indexComplete']:
                        result['reason'] = result.get('reason', 'BOUNDED_CANDIDATE_INDEX_INCOMPLETE')
            except ProbeReservationDenied as error:
                result['reservationDenials'] = [{'url': sample_url, 'reason': error.reason,
                    'budgetDay': budget.day, 'reservationCharged': reservation is not None,
                    'reservation': reservation}]
                if reservation is not None:
                    result['requestReservations'].append({'url': sample_url, 'reservation': reservation,
                                                          'observation': None, 'denial': error.reason})
                result['reason'] = error.reason
                result['sampleReason'] = error.reason
                global_denial = error.reason
            except (ValueError, OSError, RuntimeError, KeyError, TypeError) as error:
                result['reason'] = str(error)[:160] if isinstance(error, ValueError) else type(error).__name__
                result['sampleReason'] = result['reason']
                if reservation is not None and not any(row['url'] == sample_url for row in result['requestReservations']):
                    result['requestReservations'].append({'url': sample_url, 'reservation': reservation,
                                                          'observation': None, 'transportOrParseError': result['reason']})
        elif items:
            result.setdefault('sampleReason', 'SKIPPED_AFTER_RESERVATION_DENIAL')
        elif not result.get('reason'):
            result['reason'] = 'BOUNDED_CANDIDATE_NO_INVENTORY'
        if global_denial is None:
            try:
                # Catch a deadline or UTC-day change after the final response,
                # even when no further reservation would otherwise be attempted.
                budget.before_fetch()
            except ProbeReservationDenied as error:
                global_denial = error.reason
                result['completionGuardReason'] = error.reason
                result.setdefault('reservationDenials', []).append({
                    'url': (result.get('requestReservations') or [{'url': binding['indexUrl']}])[-1]['url'],
                    'reason': error.reason, 'budgetDay': budget.day,
                    'reservationCharged': False, 'reservation': None,
                    'phase': 'post_response_completion_guard'})
        store.write_once(f"source-probes/bounded-candidate/{plan['canonicalSha256']}/"
                         f"{binding['sourceId'].replace(':', '_')}/{digest(result)}.json", result)
        results.append(result)
    report = {'schemaVersion': 1, 'operation': BOUNDED_CANDIDATE_OPERATION,
              'checkedAt': budget.clock(), 'startedAt': started_at,
              'contractSha256': digest(contract), 'planRawSha256': plan['rawSha256'],
              'planCanonicalSha256': plan['canonicalSha256'], 'planReference': plan_reference,
              'sources': results, 'reservationContext': budget.summary(),
              'executionCompleted': global_denial is None, 'budgetDenied': global_denial is not None,
              'qualified': False, 'sourceChecksCredited': 0, 'qualifiedSources': 0,
              'semanticAdmission': False, 'coverageCredit': False, 'modelCalls': 0,
              'facts': [], 'newFactIds': []}
    _verify_bounded_candidate_result(contract, store, plan, report)
    return report


def _sec_diagnostic_pages(source, root_document, checked_at):
    """Return literal SEC JSON pages required for a candidate's bounded window."""
    issuer = source.get('regulatoryIssuer')
    require(source.get('registration') == 'candidate' and source.get('kind') == 'sec_index'
            and source.get('family') == 'regulatory_filings'
            and isinstance(issuer, dict) and set(issuer) == {'cik', 'legalName', 'relationship'}
            and isinstance(issuer.get('cik'), str) and re.fullmatch(r'[0-9]{10}', issuer['cik'])
            and isinstance(issuer.get('legalName'), str) and issuer['legalName'].strip() == issuer['legalName']
            and issuer.get('relationship') in ('parent', 'direct'), 'SEC_DIAGNOSTIC_SOURCE_BINDING_INVALID')
    endpoint = 'https://data.sec.gov/submissions/CIK' + issuer['cik'] + '.json'
    require(source.get('url') == endpoint and source.get('allowedHosts') == ['data.sec.gov']
            and source.get('scopePrefixes') == ['/submissions/'], 'SEC_DIAGNOSTIC_ENDPOINT_BINDING_INVALID')
    require(type(source.get('maxPages')) is int and 1 <= source['maxPages'] <= 40
            and type(source.get('lookbackDays', 365)) is int and 1 <= source.get('lookbackDays', 365) <= 365,
            'SEC_DIAGNOSTIC_PAGE_OR_WINDOW_BOUND_INVALID')
    require(isinstance(root_document, dict) and str(root_document.get('cik', '')).zfill(10) == issuer['cik']
            and root_document.get('name') == issuer['legalName'], 'SEC_DIAGNOSTIC_ROOT_ISSUER_MISMATCH')
    filings = root_document.get('filings')
    require(isinstance(filings, dict) and isinstance(filings.get('files'), list),
            'SEC_DIAGNOSTIC_HISTORY_METADATA_MISSING')
    checked = instant(checked_at).astimezone(timezone.utc).date()
    cutoff = checked - timedelta(days=source.get('lookbackDays', 365))
    required = []
    seen = set()
    for archive in filings['files']:
        require(isinstance(archive, dict) and set(archive) == {'name', 'filingCount', 'filingFrom', 'filingTo'},
                'SEC_DIAGNOSTIC_ARCHIVE_METADATA_INVALID')
        name = archive.get('name')
        require(isinstance(name, str) and re.fullmatch(r'CIK' + issuer['cik'] + r'-submissions-[0-9]{3}\.json', name)
                and name not in seen, 'SEC_DIAGNOSTIC_ARCHIVE_NAME_INVALID')
        seen.add(name)
        first_text, last_text = archive.get('filingFrom'), archive.get('filingTo')
        require(isinstance(first_text, str) and isinstance(last_text, str)
                and re.fullmatch(r'\d{4}-\d{2}-\d{2}', first_text)
                and re.fullmatch(r'\d{4}-\d{2}-\d{2}', last_text), 'SEC_DIAGNOSTIC_ARCHIVE_DATES_INVALID')
        first, last = date.fromisoformat(first_text), date.fromisoformat(last_text)
        require(first <= last <= checked and type(archive.get('filingCount')) is int and archive['filingCount'] > 0,
                'SEC_DIAGNOSTIC_ARCHIVE_RANGE_INVALID')
        if last >= cutoff:
            required.append({'url': 'https://data.sec.gov/submissions/' + name, **archive})
    require(1 + len(required) <= source['maxPages'], 'SEC_DIAGNOSTIC_PAGE_CAP_EXCEEDED')
    return required


def _validate_sec_candidate_index(source, documents, checked_at):
    """Replay the strict index structure without invoking verified-only acceptance."""
    from regulatory import _cik, _date, _table, validate_index_source

    validate_index_source(source)
    checked = instant(checked_at).astimezone(timezone.utc)
    require(isinstance(documents, list) and documents and len(documents) <= source['maxPages']
            and all(isinstance(row, dict) and set(row) == {'url', 'document'}
                    and isinstance(row['url'], str) and isinstance(row['document'], dict) for row in documents),
            'SEC_DIAGNOSTIC_INDEX_DOCUMENTS_INVALID')
    require(documents[0]['url'] == source['url'], 'SEC_DIAGNOSTIC_ROOT_NOT_FIRST')
    urls = [row['url'] for row in documents]
    require(len(urls) == len(set(urls)), 'SEC_DIAGNOSTIC_DUPLICATE_INDEX_PAGE')
    issuer = source['regulatoryIssuer']
    initial = documents[0]['document']
    require(_cik(initial.get('cik')) == issuer['cik'] and initial.get('name') == issuer['legalName'],
            'SEC_DIAGNOSTIC_ROOT_ISSUER_MISMATCH')
    filings = initial.get('filings')
    require(isinstance(filings, dict) and isinstance(filings.get('files'), list),
            'SEC_DIAGNOSTIC_HISTORY_METADATA_MISSING')
    cutoff = checked.date() - timedelta(days=source.get('lookbackDays', 365))
    recent = _table(filings.get('recent'), checked, 'SEC diagnostic root')
    required = {}
    names = set()
    for archive in filings['files']:
        require(isinstance(archive, dict) and set(archive) == {'name', 'filingCount', 'filingFrom', 'filingTo'},
                'SEC_DIAGNOSTIC_ARCHIVE_METADATA_INVALID')
        name = archive['name']
        require(isinstance(name, str) and re.fullmatch(r'CIK' + issuer['cik'] + r'-submissions-[0-9]{3}\.json', name)
                and name not in names, 'SEC_DIAGNOSTIC_ARCHIVE_NAME_INVALID')
        names.add(name)
        first, last = _date(archive['filingFrom'], 'SEC diagnostic older first date'), _date(
            archive['filingTo'], 'SEC diagnostic older last date')
        require(first <= last <= checked.date() and type(archive['filingCount']) is int
                and archive['filingCount'] > 0, 'SEC_DIAGNOSTIC_ARCHIVE_RANGE_INVALID')
        if last >= cutoff:
            required['https://data.sec.gov/submissions/' + name] = archive
    require(set(urls[1:]) == set(required), 'SEC_DIAGNOSTIC_OLDER_PAGE_SET_DIFFERS')
    rows = list(recent)
    for item in documents[1:]:
        metadata = required[item['url']]
        page_rows = _table(item['document'], checked, 'SEC diagnostic older page')
        dates = [row['filingDate'] for row in page_rows]
        require(len(page_rows) == metadata['filingCount'] and dates
                and metadata['filingFrom'] <= min(dates) <= max(dates) <= metadata['filingTo'],
                'SEC_DIAGNOSTIC_OLDER_PAGE_COUNT_OR_RANGE_DIFFERS')
        rows.extend(page_rows)
    unique_rows = {}
    for row in rows:
        accession = row['accessionNumber']
        require(accession not in unique_rows or unique_rows[accession] == row,
                'SEC_DIAGNOSTIC_CONFLICTING_DUPLICATE_ACCESSION')
        unique_rows[accession] = row
    return {'windowStart': cutoff.isoformat(), 'windowEnd': checked.date().isoformat(),
            'indexDocumentCount': len(documents), 'filingRows': len(rows),
            'uniqueFilings': len(unique_rows)}


def _sec_diagnostic_result(source, checked_at):
    return {'sourceId': source['id'], 'supplierId': source['supplierId'], 'checkedAt': checked_at,
            'registration': 'candidate', 'observations': [], 'fetchReservations': [],
            'reservationDenials': [], 'qualified': False, 'semanticAdmission': False,
            'coverageCredit': False, 'facts': [], 'sourceChecksCredited': 0, 'qualifiedSources': 0}


def _validate_sec_diagnostic_pair(index_source, documents_source, suppliers=None):
    """Pure declaration preflight; it does not grant verified registration."""
    from regulatory import validate_filing_source, validate_index_source

    validate_index_source(index_source, suppliers)
    validate_filing_source(documents_source, suppliers)
    issuer = index_source['regulatoryIssuer']
    require(index_source.get('registration') == 'candidate'
            and index_source.get('url') == 'https://data.sec.gov/submissions/CIK' + issuer['cik'] + '.json'
            and index_source.get('allowedHosts') == ['data.sec.gov']
            and index_source.get('scopePrefixes') == ['/submissions/']
            and type(index_source.get('maxPages')) is int and 1 <= index_source['maxPages'] <= 40
            and type(index_source.get('lookbackDays', 365)) is int
            and 1 <= index_source.get('lookbackDays', 365) <= 365,
            'SEC_DIAGNOSTIC_INDEX_SOURCE_BOUND_INVALID')
    require(documents_source.get('registration') == 'candidate'
            and documents_source.get('kind') == 'sec_documents'
            and documents_source.get('family') == 'filing_documents'
            and documents_source.get('supplierId') == index_source['supplierId']
            and documents_source.get('regulatoryIssuer') == issuer
            and documents_source.get('cik') == issuer['cik']
            and documents_source.get('url') == index_source['url']
            and documents_source.get('allowedHosts') == ['data.sec.gov', 'www.sec.gov']
            and documents_source.get('scopePrefixes') == ['/Archives/edgar/data/']
            and type(documents_source.get('maxPages')) is int and 1 <= documents_source['maxPages'] <= 100
            and documents_source.get('lookbackDays', 365) == index_source.get('lookbackDays', 365),
            'SEC_DIAGNOSTIC_DOCUMENT_SOURCE_BINDING_INVALID')


def _sec_diagnostic_get(source, url, store, fetcher, budget, result):
    reservation = None
    try:
        reservation = budget.reserve_fetch()
        result['fetchReservations'].append({'url': url, **reservation})
        budget.before_fetch()
    except ProbeReservationDenied as error:
        result['reservationDenials'].append({'url': url, 'reason': error.reason,
            'budgetDay': budget.day,
            'reservationCharged': None if error.reason == 'SOURCE_PROBE_RESERVATION_PERSISTENCE_FAILED'
            else reservation is not None})
        raise
    observed = fetcher.fetch(source, url)
    try:
        fetched = instant(observed.get('fetchedAt')).astimezone(timezone.utc)
        current = instant(budget.clock()).astimezone(timezone.utc)
    except (ValueError, TypeError, AttributeError):
        raise ValueError('SEC_DIAGNOSTIC_FETCH_TIME_INVALID') from None
    require(budget.started <= fetched <= current and fetched.date().isoformat() == budget.day,
            'SEC_DIAGNOSTIC_FETCH_TIME_OUTSIDE_LEASED_WINDOW')
    result['observations'].append(store.put({**observed, 'sourceId': source['id']}))
    return observed, store.get(observed['body']) if observed.get('body') else b''


def _probe_sec_candidate_pair(index_source, documents_source, store, fetcher, budget, suppliers=None):
    """Collect fresh neutral SEC index bytes, then exact primary bodies under their own source ID."""
    from documents import readable_document
    from regulatory import filing_document_inventory

    index_result = _sec_diagnostic_result(index_source, budget.clock())
    documents_result = _sec_diagnostic_result(documents_source, budget.clock())
    index_result['secIndexDiagnostic'] = {'allRequiredPagesFetched': False, 'qualificationComplete': False,
        'requiredOlderPages': [], 'issuer': copy.deepcopy(index_source.get('regulatoryIssuer'))}
    documents_result['secDocumentsDiagnostic'] = {'indexSourceId': index_source['id'],
        'primaryDocuments': [], 'allSelectedBodiesFetched': False, 'semanticEvidence': False}
    final_window_check = False
    try:
        _validate_sec_diagnostic_pair(index_source, documents_source, suppliers)
        issuer = index_source['regulatoryIssuer']
        root_response, root_body = _sec_diagnostic_get(index_source, index_source['url'], store, fetcher, budget, index_result)
        require(root_response.get('status') == 'fetched' and root_response.get('httpStatus') == 200
            and root_response.get('requestedUrl') == index_source['url']
            and root_response.get('finalUrl', index_source['url']) == index_source['url'],
            'SEC_DIAGNOSTIC_ROOT_RESPONSE_INVALID')
        root_document = json.loads(decoded_discovery_body(root_body))
        checked_at = root_response['fetchedAt']
        required_pages = _sec_diagnostic_pages(index_source, root_document, checked_at)
        require(1 + len(required_pages) <= documents_source['maxPages'],
                'SEC_DIAGNOSTIC_DOCUMENT_INDEX_PAGE_CAP_EXCEEDED')
        index_documents = [{'url': index_source['url'], 'document': root_document}]
        for page in required_pages:
            observed, body = _sec_diagnostic_get(index_source, page['url'], store, fetcher, budget, index_result)
            entry = {'url': page['url'], 'filingFrom': page['filingFrom'], 'filingTo': page['filingTo'],
                     'filingCount': page['filingCount'], 'observation': index_result['observations'][-1],
                     'status': observed.get('status')}
            index_result['secIndexDiagnostic']['requiredOlderPages'].append(entry)
            require(observed.get('status') == 'fetched' and observed.get('httpStatus') == 200
                    and observed.get('requestedUrl') == page['url']
                    and observed.get('finalUrl', page['url']) == page['url'],
                    'SEC_DIAGNOSTIC_OLDER_PAGE_RESPONSE_INVALID')
            document = json.loads(decoded_discovery_body(body))
            index_documents.append({'url': page['url'], 'document': document})
        verified_index = _validate_sec_candidate_index(index_source, index_documents, checked_at)
        index_result['secIndexDiagnostic']['allRequiredPagesFetched'] = True
        cutoff = date.fromisoformat(verified_index['windowStart'])
        primary = filing_document_inventory(documents_source, index_documents,
            cutoff.isoformat(), verified_index['windowEnd'])
        documents_result['secDocumentsDiagnostic']['indexObservations'] = list(index_result['observations'])
        documents_result['secDocumentsDiagnostic']['selectedCount'] = len(primary)
        documents_result['secDocumentsDiagnostic']['selectedDocuments'] = copy.deepcopy(primary)
        documents_result['secDocumentsDiagnostic']['primaryBodyGuard'] = 100
        if len(primary) > 100:
            index_result['reason'] = 'SEC_JSON_RETAINED_CANDIDATE_DIAGNOSTIC_ONLY'
            documents_result['reason'] = 'SEC_DIAGNOSTIC_PRIMARY_BODY_GUARD_EXCEEDED'
        else:
            for item in primary:
                observed, body = _sec_diagnostic_get(documents_source, item['url'], store, fetcher, budget, documents_result)
                body_entry = {'url': item['url'], 'filingDate': item['filingDate'],
                              'observation': documents_result['observations'][-1], 'status': observed.get('status'),
                              'httpStatus': observed.get('httpStatus'), 'errorCode': observed.get('errorCode')}
                documents_result['secDocumentsDiagnostic']['primaryDocuments'].append(body_entry)
                require(observed.get('status') == 'fetched' and observed.get('httpStatus') == 200
                        and observed.get('requestedUrl') == item['url']
                        and observed.get('finalUrl', item['url']) == item['url'],
                        'SEC_DIAGNOSTIC_PRIMARY_BODY_RESPONSE_INVALID')
                text = readable_document(body, observed.get('contentType', ''))
                body_entry['readableText'] = store.put(text.encode())
            documents_result['secDocumentsDiagnostic']['allSelectedBodiesFetched'] = True
            documents_result['reason'] = 'SEC_PRIMARY_BODIES_RETAINED_CANDIDATE_DIAGNOSTIC_ONLY'
        final_window_check = True
        budget.before_fetch()
        completed_at = budget.clock()
        budget.before_fetch()
        index_result['checkedAt'] = completed_at
        documents_result['checkedAt'] = completed_at
        index_result['reason'] = index_result.get('reason', 'SEC_JSON_RETAINED_CANDIDATE_DIAGNOSTIC_ONLY')
    except ProbeReservationDenied as error:
        if final_window_check:
            denial = {'url': None, 'reason': error.reason, 'budgetDay': budget.day,
                      'reservationCharged': False, 'phase': 'final_window_check'}
            index_result['reservationDenials'].append(denial)
            documents_result['reservationDenials'].append(copy.deepcopy(denial))
            index_result['secIndexDiagnostic']['allRequiredPagesFetched'] = False
            index_result['secIndexDiagnostic']['qualificationComplete'] = False
            documents_result['secDocumentsDiagnostic']['allSelectedBodiesFetched'] = False
        index_result['reason'] = error.reason
        documents_result['reason'] = error.reason
        index_result['executionCompleted'] = False
        documents_result['executionCompleted'] = False
        index_result['budgetDenied'] = True
        documents_result['budgetDenied'] = True
    except (ValueError, OSError, RuntimeError, KeyError, TypeError) as error:
        reason = str(error)[:160] if isinstance(error, ValueError) else type(error).__name__
        if 'reason' not in index_result:
            index_result['reason'] = reason
        if 'reason' not in documents_result:
            documents_result['reason'] = reason
    for result in (index_result, documents_result):
        result['executionCompleted'] = not bool(result['reservationDenials'])
        result['budgetDenied'] = bool(result['reservationDenials'])
        store.write_once(f"source-probes/{result['sourceId'].replace(':', '_')}/{digest(result)}.json", result)
    return [index_result, documents_result]


def _probe_disabled_qualification(contract, store, budget, plan):
    """Retain an explicit zero-request diagnostic; never enter source probing."""
    require(plan.get('operation') == DISABLED_QUALIFICATION_OPERATION
            and plan.get('maxRequests') == 0 and plan.get('plan', {}).get('sources') == [],
            'DISABLED_QUALIFICATION_OPERATION_REQUIRED')
    return {'schemaVersion': 1, 'operation': DISABLED_QUALIFICATION_OPERATION,
            'checkedAt': budget.clock(), 'startedAt': budget.started_at,
            'contractSha256': digest(contract), 'planRawSha256': plan['rawSha256'],
            'planCanonicalSha256': plan['canonicalSha256'], 'planReference': plan['rawPlanReference'],
            'maxRequests': 0, 'sources': [], 'reservationContext': budget.summary(),
            'executionCompleted': True, 'budgetDenied': False,
            'disabled': True, 'reason': 'QUALIFICATION_PROBE_EXPLICITLY_DISABLED',
            'qualified': False, 'sourceChecksCredited': 0, 'qualifiedSources': 0,
            'semanticAdmission': False, 'coverageCredit': False, 'modelCalls': 0,
            'facts': [], 'newFactIds': []}


def probe_sources(contract, store, fetcher, *, reservation_context=None, qualification_plan_path=None):
    require(isinstance(reservation_context, PersistentProbeBudget), 'SOURCE_PROBE_BOUND_RESERVATION_CONTEXT_REQUIRED')
    reservation_context.assert_bound(store, contract)
    qualification = (validate_qualification_probe_plan(contract, store, qualification_plan_path)
                     if qualification_plan_path is not None else None)
    if qualification is not None:
        # The leased caller has acknowledged escrow before entering this path.
        # Persist only a plan that was fully validated before transport.
        raw = Path(qualification['path']).read_bytes()
        require(digest(raw) == qualification['rawSha256'], 'QUALIFICATION_CURRENT_PLAN_CHANGED_AFTER_VALIDATION')
        qualification['rawPlanReference'] = store.put(raw)
        if qualification.get('operation') == BOUNDED_CANDIDATE_OPERATION:
            return _probe_bounded_candidate_traversal(contract, store, fetcher, reservation_context, qualification)
        if qualification.get('operation') == DISABLED_QUALIFICATION_OPERATION:
            return _probe_disabled_qualification(contract, store, reservation_context, qualification)
    def probe(source):
        result = {"sourceId": source["id"], "supplierId": source["supplierId"],
                  "checkedAt": reservation_context.clock(), "registration": "candidate", "observations": [], "endpoints": [],
                  "qualified": False, "semanticAdmission": False, "coverageCredit": False, "facts": [],
                  "fetchReservations": [], "reservationDenials": []}
        def get(url):
            reservation = None
            try:
                reservation = reservation_context.reserve_fetch()
                result['fetchReservations'].append({'url': url, **reservation})
                reservation_context.before_fetch()
            except ProbeReservationDenied as error:
                result['reservationDenials'].append({'url': url, 'reason': error.reason,
                    'budgetDay': reservation_context.day,
                    'reservationCharged': None if error.reason == 'SOURCE_PROBE_RESERVATION_PERSISTENCE_FAILED' else reservation is not None})
                raise
            observed = fetcher.fetch(source, url)
            result["observations"].append(store.put(observed))
            return observed, store.get(observed["body"]) if observed.get("body") else b""
        try:
            observed, root = get(source["url"])
            if observed["status"] != "fetched":
                result["reason"] = observed.get("errorCode", "ROOT_UNAVAILABLE")
                return result
            root_text = decoded_discovery_body(root).decode('utf8', errors='strict' if root.startswith(b'\x1f\x8b') else 'replace')
            page = Page(root_text)
            robots_url = urljoin(source["url"], "/robots.txt")
            observed, robots = get(robots_url)
            parser = RobotFileParser(robots_url)
            if observed["status"] == "fetched":
                robots_text = decoded_discovery_body(robots).decode('utf8', errors='strict' if robots.startswith(b'\x1f\x8b') else 'replace')
                parser.parse(robots_text.splitlines())
                sitemaps = re.findall(r"(?im)^sitemap:\s*(https://\S+)", robots_text)
            else:
                sitemaps = []
            candidates = [(urljoin(source["url"], u), "rss") for u in page.feeds]
            candidates += [(u, "sitemap") for u in sitemaps]
            if not candidates:
                candidates = [(urljoin(source["url"], "/sitemap.xml"), "sitemap")]
            for url, kind in list(dict.fromkeys(candidates))[:8]:
                if urlsplit(url).hostname not in source["allowedHosts"]:
                    result["endpoints"].append({"url": url, "result": "ADDITIONAL_HOST_REQUIRES_REGISTRATION"})
                    continue
                if robots and not parser.can_fetch("SecurityMarketPulse", url):
                    result["endpoints"].append({"url": url, "result": "ROBOTS_DISALLOWED"})
                    continue
                observed, body = get(url)
                if observed["status"] != "fetched":
                    result["endpoints"].append({"url": url, "result": observed.get("errorCode", "UNAVAILABLE")})
                    continue
                try:
                    parsed = xml_links(body, url)
                except (ValueError, __import__('xml.etree.ElementTree', fromlist=['ParseError']).ParseError):
                    result["endpoints"].append({"url": url, "result": "NOT_DISCOVERY_XML"})
                    continue
                result["endpoints"].append({"url": url, "kind": kind, "format": parsed["kind"],
                                            "result": "DISCOVERY_ENDPOINT_RESPONDED", "body": observed["body"],
                                            "itemCount": len(parsed["links"]), "indexCount": len(parsed["indexes"]),
                                            "sampleItems": parsed["links"][:5], "sampleIndexes": parsed["indexes"][:5]})
            # An XML response alone cannot establish entity scope, history or completeness.
            result["reason"] = "ENDPOINTS_PROBED_SCOPE_AND_HISTORY_REVIEW_REQUIRED"
        except ProbeReservationDenied as exc:
            result['reason'] = exc.reason
        except (ValueError, OSError, RuntimeError) as exc:
            result["reason"] = type(exc).__name__
        finally:
            result['executionCompleted'] = not bool(result['reservationDenials'])
            result['budgetDenied'] = bool(result['reservationDenials'])
            store.write_once(f"source-probes/{source['id'].replace(':', '_')}/{digest(result)}.json", result)
        return result
    sources = [s for s in contract["sources"] if s["registration"] == "candidate"]
    sec_indexes = [s for s in sources if s.get('kind') == 'sec_index']
    sec_documents = [s for s in sources if s.get('kind') == 'sec_documents']
    sec_sources = sec_indexes + sec_documents
    results = []
    # Validate the full two-way source pairing inventory before any SEC request.
    # Candidate IDs may not be reused to fetch the same issuer under multiple declarations.
    pair_candidates = []
    pair_error = None
    try:
        from regulatory import validate_filing_source, validate_index_source
        for source in sec_indexes:
            validate_index_source(source, contract.get('suppliers') or None)
        for source in sec_documents:
            validate_filing_source(source, contract.get('suppliers') or None)
        if len(sec_indexes) != len(sec_documents):
            raise ValueError('SEC_DIAGNOSTIC_EXACT_ONE_TO_ONE_SOURCE_JOIN_REQUIRED')
        for index_source in sec_indexes:
            matches = [s for s in sec_documents
                       if s.get('supplierId') == index_source.get('supplierId')
                       and s.get('cik') == index_source.get('regulatoryIssuer', {}).get('cik')]
            require(len(matches) == 1, 'SEC_DIAGNOSTIC_EXACT_DOCUMENT_SOURCE_JOIN_REQUIRED')
            documents_source = matches[0]
            reverse = [s for s in sec_indexes
                       if s.get('supplierId') == documents_source.get('supplierId')
                       and s.get('regulatoryIssuer', {}).get('cik') == documents_source.get('cik')]
            require(len(reverse) == 1 and reverse[0]['id'] == index_source['id'],
                    'SEC_DIAGNOSTIC_EXACT_INDEX_SOURCE_JOIN_REQUIRED')
            _validate_sec_diagnostic_pair(index_source, documents_source,
                                           contract.get('suppliers') or None)
            pair_candidates.append((index_source, documents_source))
    except (ValueError, KeyError, TypeError) as error:
        pair_error = str(error)[:160] if isinstance(error, ValueError) else type(error).__name__
    if pair_error is None:
        for index_source, documents_source in pair_candidates:
            results.extend(_probe_sec_candidate_pair(index_source, documents_source, store, fetcher,
                reservation_context, contract.get('suppliers') or None))
    else:
        for source in sec_sources:
            row = _sec_diagnostic_result(source, reservation_context.clock())
            row.update(reason=pair_error, executionCompleted=True, budgetDenied=False)
            store.write_once(f"source-probes/{source['id'].replace(':', '_')}/{digest(row)}.json", row)
            results.append(row)
    ordinary_sources = [s for s in sources if s not in sec_sources]
    if pair_error is None:
        with ThreadPoolExecutor(max_workers=4) as pool:
            results.extend(pool.map(probe, ordinary_sources))
        explicit = _probe_qualification_targets(contract, store, fetcher, reservation_context, qualification) if qualification else None
    else:
        explicit = None
        for source in ordinary_sources:
            row = {'sourceId': source['id'], 'supplierId': source['supplierId'],
                   'checkedAt': reservation_context.clock(), 'registration': 'candidate',
                   'observations': [], 'endpoints': [], 'qualified': False, 'semanticAdmission': False,
                   'coverageCredit': False, 'facts': [], 'fetchReservations': [], 'reservationDenials': [],
                   'reason': 'SEC_DIAGNOSTIC_PREFLIGHT_BLOCKED_ALL_TRANSPORT',
                   'executionCompleted': True, 'budgetDenied': False}
            store.write_once(f"source-probes/{source['id'].replace(':', '_')}/{digest(row)}.json", row)
            results.append(row)
    denied = any(result['budgetDenied'] for result in results)
    denied = denied or bool(explicit and any(row['budgetDenied'] for row in explicit['targets']))
    report = {"schemaVersion": 1, "checkedAt": reservation_context.clock(), "contractSha256": digest(contract), "sources": results,
            "reservationContext": reservation_context.summary(), "qualified": False,
            "executionCompleted": not denied, "budgetDenied": denied,
            "sourceChecksCredited": 0, "qualifiedSources": 0,
            "semanticAdmission": False, "coverageCredit": False, "facts": []}
    if explicit is not None:
        report['qualification'] = explicit
    return report
