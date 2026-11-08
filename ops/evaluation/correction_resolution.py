#!/usr/bin/env python3
"""Measure only authenticated resolution of the five frozen contradictions.

Offline use is deliberately unmeasured. Authenticated mode reads the verified
evidence archive, GitHub workflow artifacts and current Vercel bytes; it never
dispatches, stages, promotes, writes archive state, calls a model or fetches
market sources.
"""
import argparse
import base64
import hashlib
import io
import os
import shutil
import json
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

PIPELINE = Path(__file__).resolve().parents[2] / 'web/scripts/pipeline'
sys.path.insert(0, str(PIPELINE))

import artifacts as artifacts_module  # noqa: E402
import archive as archive_module  # noqa: E402
import contracts as contracts_module  # noqa: E402
import corrections as corrections_module  # noqa: E402
import discovery as discovery_module  # noqa: E402
import provenance as provenance_module  # noqa: E402
import publication as publication_module  # noqa: E402
import storage as storage_module  # noqa: E402
import validation as validation_module  # noqa: E402
import vercel as vercel_module  # noqa: E402
import agents as agents_module  # noqa: E402
import documents as documents_module  # noqa: E402
import regulatory as regulatory_module  # noqa: E402
from artifacts import inventory, stage_files, unpack  # noqa: E402
from contracts import canonical, digest, instant, require, valid_hash  # noqa: E402
from corrections import load_policy, project_bundle, replay_admission  # noqa: E402
from archive import EVIDENCE_REMOTE, GitArchive  # noqa: E402
from provenance import GitHubAuthority  # noqa: E402
from publication import verify_acknowledgement  # noqa: E402
from storage import LocalStore  # noqa: E402
from vercel import VercelAdapter  # noqa: E402

DESIGN = 'docs/active/daily-pipeline/accuracy/correction-resolution-evaluation-design-2026-10-23.json'
DESIGN_SHA256 = '257a26c9126e9a3c9ba78ad1723c2517f5301c56e89772527085d98782565720'
AUDIT = 'docs/active/daily-pipeline/accuracy/source-bindings-2026-10-23.json'
INVENTORY = 'docs/active/daily-pipeline/accuracy/published-inventory-2026-10-23.json'
SOURCE_MIGRATION = 'docs/active/daily-pipeline/accuracy/source-migration-inputs-2026-10-23.json'
MARKET = 'contracts/market.json'
REQUESTS = 'contracts/factual-corrections.json'
BASELINE = 'contracts/factual-baseline.json'
ORIGINALS = 'web/src/data/tracker/originals.json'
PROJECT = 'jessepike/sec-market'
COLLECTOR_WORKFLOW = '.github/workflows/subscription-collector.yml'
COLLECTOR_ARTIFACT = 'subscription-collection-receipt'
FIVE = 'accuracy.known_contradictions_resolved'


class Unavailable(RuntimeError):
    """An authenticated evidence source could not be read."""


class AuthenticatedArchive:
    """Read-only local archive bytes tied to the current private GitHub ref."""
    def __init__(self, root, authority):
        self.root = Path(root).resolve()
        self.authority = authority
        self.remote_ref = 'refs/archive/market-evidence'
        self.commit = self._current_commit()
        local_raw = (self.root / 'archive-manifest.json').read_bytes()
        manifest_blob_sha, manifest_size = self._manifest_identity(self.commit)
        local_blob_sha = hashlib.sha1(b'blob ' + str(len(local_raw)).encode() + b'\0' + local_raw).hexdigest()
        if len(local_raw) != manifest_size or local_blob_sha != manifest_blob_sha:
            raise Unavailable('extracted archive differs from authenticated current ref')
        self.manifest = strict_json(local_raw, 'authenticated archive manifest')
        require(local_raw == canonical(self.manifest), 'Authenticated archive manifest is not canonical')
        self.manifest_sha256 = digest(self.manifest)
        GitArchive.verify(self.root, expected_manifest=self.manifest_sha256)

    def _current_commit(self):
        ref = _api_json(self.authority, 'git/ref/archive/market-evidence')
        commit = ref.get('object', {}).get('sha')
        require(ref.get('ref') == self.remote_ref and isinstance(commit, str)
                and re.fullmatch(r'[0-9a-f]{40}', commit), 'Private archive ref is invalid')
        return commit

    def _manifest_bytes(self, commit):
        require(isinstance(commit, str) and re.fullmatch(r'[0-9a-f]{40}', commit),
                'Archive commit identity is invalid')
        commit_obj = _api_json(self.authority, 'git/commits/' + commit)
        tree_sha = commit_obj.get('tree', {}).get('sha')
        require(isinstance(tree_sha, str) and re.fullmatch(r'[0-9a-f]{40}', tree_sha),
                'Archive commit tree identity is invalid')
        # The signed archive commit stores its manifest at the root. A
        # recursive tree request expands tens of thousands of archived files
        # and can exceed the authenticated CLI's bounded-response limit.
        tree = _api_json(self.authority, 'git/trees/' + tree_sha)
        require(tree.get('truncated') is False, 'Archive commit tree response is truncated')
        matches = [row for row in tree.get('tree', [])
                   if row.get('path') == 'archive-manifest.json' and row.get('type') == 'blob']
        require(len(matches) == 1, 'Archive manifest blob is missing or ambiguous')
        blob = _api_json(self.authority, 'git/blobs/' + matches[0]['sha'])
        require(blob.get('encoding') == 'base64' and isinstance(blob.get('content'), str),
                'Archive manifest blob is not available as base64')
        try:
            raw = base64.b64decode(''.join(blob['content'].split()), validate=True)
        except (ValueError, TypeError):
            raise ValueError('Malformed authenticated archive manifest blob') from None
        require(blob.get('size') == len(raw), 'Archive manifest blob size differs')
        return raw

    def _manifest_identity(self, commit):
        require(isinstance(commit, str) and re.fullmatch(r'[0-9a-f]{40}', commit),
                'Archive commit identity is invalid')
        commit_obj = _api_json(self.authority, 'git/commits/' + commit)
        tree_sha = commit_obj.get('tree', {}).get('sha')
        require(isinstance(tree_sha, str) and re.fullmatch(r'[0-9a-f]{40}', tree_sha),
                'Archive commit tree identity is invalid')
        tree = _api_json(self.authority, 'git/trees/' + tree_sha)
        require(tree.get('truncated') is False, 'Archive commit tree response is truncated')
        matches = [row for row in tree.get('tree', [])
                   if row.get('path') == 'archive-manifest.json' and row.get('type') == 'blob']
        require(len(matches) == 1 and isinstance(matches[0].get('size'), int),
                'Archive manifest blob is missing or ambiguous')
        return matches[0]['sha'], matches[0]['size']

    def manifest_at(self, commit):
        return strict_json(self._manifest_bytes(commit), 'historical archive manifest')

    def is_ancestor(self, ancestor, descendant):
        require(re.fullmatch(r'[0-9a-f]{40}', ancestor or '') is not None
                and re.fullmatch(r'[0-9a-f]{40}', descendant or '') is not None,
                'Archive ancestry commit is invalid')
        comparison = _api_json(self.authority, 'compare/' + ancestor + '...' + descendant)
        return comparison.get('status') in ('ahead', 'identical')

    def verify_unchanged(self):
        require(self._current_commit() == self.commit, 'Private archive ref changed during gather')
        local_raw = (self.root / 'archive-manifest.json').read_bytes()
        manifest_blob_sha, manifest_size = self._manifest_identity(self.commit)
        require(len(local_raw) == manifest_size
                and hashlib.sha1(b'blob ' + str(len(local_raw)).encode() + b'\0' + local_raw).hexdigest()
                == manifest_blob_sha, 'Authenticated archive manifest changed during gather')
        GitArchive.verify(self.root, expected_manifest=self.manifest_sha256)


def _orb_macos_gh_runner(argv, **kwargs):
    """Forward existing gh CLI calls to the host without copying credentials."""
    require(isinstance(argv, (list, tuple)) and argv and argv[0] == 'gh',
            'Only existing gh CLI read calls may cross the OrbStack host bridge')
    return subprocess.run(['mac', *argv], **kwargs)


def strict_json(raw, label='JSON'):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, f'{label}: duplicate property {key}')
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda _: require(False, f'{label}: non-finite number'))


def pin(root, relative, expected_sha):
    path = (Path(root) / relative).resolve()
    root = Path(root).resolve()
    require(path.is_relative_to(root), 'Pinned input escapes repository root')
    raw = path.read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    require(actual == expected_sha, f'Frozen input hash differs: {relative}')
    return strict_json(raw, relative), {'path': relative, 'sha256': actual}


def baseline(root):
    root = Path(root).resolve()
    design, design_pin = pin(root, DESIGN, DESIGN_SHA256)
    mapping = design['resolutionMapping']
    require(digest(mapping) == design['resolutionMappingSha256'], 'Frozen correction-resolution mapping hash differs')
    audit, audit_pin = pin(root, AUDIT, design['inputs']['claimAudit']['sha256'])
    inventory_obj, inventory_pin = pin(root, INVENTORY, design['inputs']['publishedInventory']['sha256'])
    migration, migration_pin = pin(root, SOURCE_MIGRATION, design['inputs']['sourceMigration']['sha256'])
    history_manifest, history_manifest_pin = pin(
        root, migration['historicalManifest']['path'], migration['historicalManifest']['sha256'])
    _, originals_pin = pin(root, ORIGINALS, design['inputs']['originals']['sha256'])
    _, baseline_pin = pin(root, BASELINE, design['inputs']['baseline']['sha256'])
    require(audit.get('kind') == 'published_claim_review_binding_report'
            and audit.get('bindingChecksPassed') is True, 'Frozen historical claim audit is invalid')
    contradicted = {row['id'] for row in audit['records'] if row.get('verdict') == 'contradicted'}
    require(contradicted == {row['auditRecordId'] for row in mapping} and len(mapping) == 5,
            'Frozen contradiction inventory differs from the five-row mapping')
    detailed_mapping = {row['auditRecordId']: row for row in design.get('exactMapping', [])}
    require(set(detailed_mapping) == {row['auditRecordId'] for row in mapping},
            'Detailed frozen mapping differs from the five-row mapping')
    for row in mapping:
        details = detailed_mapping[row['auditRecordId']]
        audit_record = _json_pointer(audit, details['baselineAuditPointer'])
        inventory_record = _json_pointer(inventory_obj, details['baselineInventoryPointer'])
        require(audit_record.get('id') == row['auditRecordId']
                and audit_record.get('verdict') == 'contradicted'
                and inventory_record.get('published') is not None
                and digest(inventory_record['published']) == row['originalSha256'],
                'Frozen audit/inventory pointer does not bind mapped published original')
    require(audit['appRevision'] == design['baseline']['applicationRevision'], 'Historical audit revision differs')
    require(inventory_obj.get('applicationRevision') == audit['appRevision'], 'Historical inventory revision differs')
    require(migration.get('kind') == 'pinned_historical_claim_source_migration'
            and migration.get('scope') == 'frozen_historical_benchmark_only'
            and digest(history_manifest) == audit.get('manifestSha256')
            and history_manifest.get('inputs') == audit.get('inputPins'),
            'Source migration does not bind the frozen historical audit manifest')
    require(migration['originals'] == {'path': ORIGINALS, 'sha256': design['inputs']['originals']['sha256']}
            and migration['baseline'] == {'path': BASELINE, 'sha256': design['inputs']['baseline']['sha256']},
            'Source migration originals/baseline pins differ')
    return design, mapping, {
        'design': design_pin, 'claimAudit': audit_pin, 'publishedInventory': inventory_pin,
        'sourceMigration': migration_pin, 'historicalManifest': history_manifest_pin,
        'originals': originals_pin, 'baseline': baseline_pin,
    }


def _json_pointer(document, pointer):
    require(isinstance(pointer, str) and pointer.startswith('/'), 'Invalid frozen source pointer')
    value = document
    for component in pointer[1:].split('/'):
        component = component.replace('~1', '/').replace('~0', '~')
        value = value[int(component)] if isinstance(value, list) else value[component]
    return value


def _observation(root, evaluated_at, states, evidence, unavailable):
    design, mapping, pins = baseline(root)
    now = evaluated_at
    instant(now)
    require(set(states) == {row['auditRecordId'] for row in mapping}, 'Derived state inventory differs')
    rows = []
    for item in mapping:
        state, reason = states[item['auditRecordId']]
        require(state in ('resolved', 'unresolved', 'unmeasured'), 'Invalid derived record state')
        rows.append({
            'auditRecordId': item['auditRecordId'], 'groupId': item['groupId'],
            'targetId': item['targetId'], 'state': state, 'reasonCode': reason,
            'candidateSha256': None, 'evidenceSetSha256': None,
            'groupReviewPolicySha256': None, 'admissionRef': None,
            'reviewRef': None, 'gateRunId': None, 'gateArtifactId': None,
            'artifactSha256': None, 'releaseId': None, 'publicObservationRefs': [],
        })
    resolved = sum(row['state'] == 'resolved' for row in rows)
    unresolved = sum(row['state'] == 'unresolved' for row in rows)
    unmeasured = 5 - resolved - unresolved
    status = 'pass' if resolved == 5 else 'fail' if unresolved else 'unmeasured'
    measure = {
        'id': FIVE, 'axis': 'accuracy', 'status': status,
        'numerator': resolved if resolved + unresolved else None, 'denominator': 5,
        'observedAt': now if resolved + unresolved else None,
        'evidence': evidence or {},
        'limitations': ('Current remediation of these five fixed targets only. This is not current claim precision, recall, or general site accuracy.'
                        if resolved + unresolved else
                        'No authenticated current target state was established. All five records remain unmeasured; historical verdicts are unchanged.'),
        'baselineAppRevision': design['baseline']['applicationRevision'],
        'observedProductionAppRevision': (evidence or {}).get('productionAppRevision'),
        'releaseId': (evidence or {}).get('releaseId'),
        'verifiedResolvedCount': resolved, 'verifiedUnresolvedCount': unresolved,
        'unmeasuredCount': unmeasured, 'records': rows,
    }
    if unavailable:
        measure['unavailablePhase'] = unavailable
        measure['limitations'] += ' Read-only authenticated gather was unavailable at ' + unavailable + '.'
    return {
        'schemaVersion': 1, 'kind': 'current_known_contradiction_remediation_observation',
        'observedAt': measure['observedAt'], 'evaluatedAt': now,
        'baselineClaimAudit': pins['claimAudit'], 'baselineInventory': pins['publishedInventory'],
        'mappingSha256': design['resolutionMappingSha256'], 'evidencePins': pins,
        'measure': measure,
        'historicalBenchmark': {
            'appRevision': design['baseline']['applicationRevision'], 'claimAudit': pins['claimAudit'],
            'contradictedRecordIds': [row['auditRecordId'] for row in mapping],
            'immutable': True, 'currentPrecision': False,
        },
        'marketSourceRequests': 0, 'modelCalls': 0, 'archiveWrites': 0, 'deploymentActions': 0,
        'limitations': ['This measure applies only to the five fixed historical contradiction targets.',
                        'Historical 177-record verdicts stay fixed and are not current precision.',
                        'No overall accuracy score is calculated.'],
    }


def observation(root, evaluated_at=None, unavailable=None):
    """Offline mode has no parameters that can supply a measured target state."""
    now = evaluated_at or datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    _, mapping, _ = baseline(root)
    states = {row['auditRecordId']: ('unmeasured', 'No authenticated production gather was performed.')
              for row in mapping}
    return _observation(root, now, states, {}, unavailable)


def measure_states(states):
    """Pure R/U/M computation used only after target states are derived."""
    require(isinstance(states, list) and len(states) == 5, 'Exactly five target states required')
    require(all(value in ('resolved', 'unresolved', 'unmeasured') for value in states), 'Unknown target state')
    require(states.count('resolved') + states.count('unresolved') <= 5, 'Target state counts exceed benchmark')
    r, u = states.count('resolved'), states.count('unresolved')
    return {'status': 'pass' if r == 5 else 'fail' if u else 'unmeasured',
            'numerator': r if r + u else None, 'denominator': 5,
            'verifiedResolvedCount': r, 'verifiedUnresolvedCount': u,
            'unmeasuredCount': 5 - r - u}


def _api_json(authority, path):
    try:
        return authority._api(path)
    except (OSError, subprocess.SubprocessError, ValueError) as exc:
        if str(exc) in ('GITHUB_PROVENANCE_UNAVAILABLE',) or isinstance(exc, (OSError, subprocess.SubprocessError)):
            raise Unavailable('GitHub API read: ' + path) from None
        raise


def _verify_release_inputs(root, manifest, authority, design, release_root):
    """Use the exact published commit's policy inputs and verifier code."""
    revision = manifest.get('appRevision')
    require(isinstance(revision, str) and re.fullmatch(r'[0-9a-f]{40}', revision),
            'Published application revision is invalid')
    release_root = Path(release_root)
    source_files = (
        'contracts/market.json', 'contracts/factual-corrections.json',
        'contracts/factual-baseline.json', 'web/src/data/tracker/originals.json',
        'web/src/data/tracker/factualCorrectionPolicy.json',
    )
    release_pins = {}
    for relative in source_files:
        blob = _api_json(authority, 'contents/' + relative + '?ref=' + revision)
        require(blob.get('type') == 'file' and blob.get('encoding') == 'base64'
                and isinstance(blob.get('content'), str), 'Published policy input is unavailable: ' + relative)
        try:
            body = base64.b64decode(''.join(blob['content'].split()), validate=True)
        except (ValueError, TypeError):
            raise ValueError('Malformed authenticated source blob: ' + relative) from None
        require(blob.get('size') == len(body), 'Published input size differs: ' + relative)
        destination = release_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(body)
        release_pins[relative] = {'path': relative, 'sha256': digest(body), 'bytes': len(body)}
    # The release baseline and originals must retain the immutable historical
    # benchmark inputs. The active request set may legitimately have evolved.
    require(release_pins['contracts/factual-baseline.json']['sha256'] == design['inputs']['baseline']['sha256']
            and release_pins['web/src/data/tracker/originals.json']['sha256'] == design['inputs']['originals']['sha256'],
            'Published immutable original baseline differs from the frozen benchmark')
    market = strict_json((release_root / 'contracts/market.json').read_bytes(), 'published market contract')
    requests = strict_json((release_root / 'contracts/factual-corrections.json').read_bytes(), 'published correction requests')
    require(isinstance(requests.get('groups'), list) and len(requests['groups']) == 6,
            'Published correction request inventory is not six groups')
    release_pins['activeCorrectionGroupsSha256'] = digest(requests['groups'])
    release_pins['marketPolicySha256'] = digest(market)
    # These imported read-only replay helpers must be the exact code that the
    # release shipped. GitHub's blob SHA is SHA-1 over the canonical Git blob
    # header and bytes; it is an identity check, not an authority claim.
    verifier_paths = (
        'web/package.json', 'web/scripts/app-release.mjs',
        'web/scripts/verify-current-facts.ts', 'web/scripts/verify-factual-corrections.mjs',
        'web/src/data/tracker/factualCorrections.ts', 'web/src/data/tracker/events.ts',
        'web/src/data/tracker/suppliers.ts', 'web/src/data/tracker/correctionData.ts', 'web/src/data/evidence.ts',
        'web/scripts/pipeline/artifacts.py', 'web/scripts/pipeline/archive.py',
        'web/scripts/pipeline/contracts.py', 'web/scripts/pipeline/corrections.py',
        'web/scripts/pipeline/discovery.py', 'web/scripts/pipeline/provenance.py',
        'web/scripts/pipeline/publication.py', 'web/scripts/pipeline/storage.py',
        'web/scripts/pipeline/validation.py', 'web/scripts/pipeline/vercel.py',
        'web/scripts/pipeline/agents.py', 'web/scripts/pipeline/documents.py',
        'web/scripts/pipeline/regulatory.py',
    )
    imported_paths = {
        'web/scripts/pipeline/artifacts.py': artifacts_module,
        'web/scripts/pipeline/archive.py': archive_module,
        'web/scripts/pipeline/contracts.py': contracts_module,
        'web/scripts/pipeline/corrections.py': corrections_module,
        'web/scripts/pipeline/discovery.py': discovery_module,
        'web/scripts/pipeline/provenance.py': provenance_module,
        'web/scripts/pipeline/publication.py': publication_module,
        'web/scripts/pipeline/storage.py': storage_module,
        'web/scripts/pipeline/validation.py': validation_module,
        'web/scripts/pipeline/vercel.py': vercel_module,
        'web/scripts/pipeline/agents.py': agents_module,
        'web/scripts/pipeline/documents.py': documents_module,
        'web/scripts/pipeline/regulatory.py': regulatory_module,
    }
    for relative in verifier_paths:
        blob = _api_json(authority, 'contents/' + relative + '?ref=' + revision)
        require(blob.get('type') == 'file' and isinstance(blob.get('sha'), str),
                'Published verifier source is unavailable: ' + relative)
        if relative in imported_paths:
            actual_local = Path(imported_paths[relative].__file__).resolve()
            require(actual_local.is_relative_to(PIPELINE.resolve())
                    and actual_local.relative_to(PIPELINE.resolve()).as_posix()
                    == relative.removeprefix('web/scripts/pipeline/'),
                    'Imported replay helper is outside the authenticated pipeline runtime: ' + relative)
            raw = actual_local.read_bytes()
            local_blob_sha = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
            if blob.get('sha') != local_blob_sha:
                raise Unavailable('executed replay helper differs from published code: ' + relative)
        else:
            require(re.fullmatch(r'[0-9a-f]{40}', blob.get('sha', '')) is not None
                    and isinstance(blob.get('size'), int),
                    'Published source identity is invalid: ' + relative)
    return market, release_pins


def _run_artifact(authority, run_id, artifact_name):
    listing = _api_json(authority, f'actions/runs/{run_id}/artifacts')
    matches = [item for item in listing.get('artifacts', [])
               if item.get('name') == artifact_name and item.get('expired') is False
               and item.get('workflow_run', {}).get('id') == run_id]
    require(len(matches) == 1, f'Expected one unexpired {artifact_name} artifact')
    meta = matches[0]
    try:
        payload = authority._api(f"actions/artifacts/{meta['id']}/zip", binary=True)
    except (OSError, subprocess.SubprocessError, ValueError):
        raise Unavailable('GitHub artifact download') from None
    require(meta.get('digest') == 'sha256:' + hashlib.sha256(payload).hexdigest(), 'GitHub artifact transport digest differs')
    try:
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            require(len(archive.infolist()) == 1, 'Unexpected collection artifact inventory')
            item = archive.infolist()[0]
            require(item.filename == 'smp-collection-receipt.json' and item.file_size <= 2_000_000,
                    'Unexpected collection receipt member')
            receipt = strict_json(archive.read(item), 'collection receipt')
    except (zipfile.BadZipFile, KeyError, OSError) as exc:
        raise ValueError('Malformed authenticated GitHub artifact') from exc
    return meta, payload, receipt


def _authenticate_collector_record(clock, authority):
    """Authenticate one archived collector execution and its exact receipt."""
    require(clock.get('executionCompleted') is True and clock.get('appRevision')
            and clock.get('runId') and clock.get('githubRunId'),
            'Collector run did not complete an identified run')
    github_run_id = int(clock['githubRunId'])
    run = _api_json(authority, f'actions/runs/{github_run_id}')
    require(run.get('id') == github_run_id and run.get('repository', {}).get('full_name') == PROJECT
            and run.get('path') == COLLECTOR_WORKFLOW
            and run.get('status') == 'completed' and run.get('conclusion') == 'success'
            and run.get('head_branch') == 'main' and run.get('head_sha') == clock['appRevision']
            and run.get('run_attempt') == clock['githubRunAttempt']
            and run.get('event') == clock['githubEventName'],
            'Collector workflow identity does not authenticate archived attempt')
    artifact_meta, artifact_bytes, receipt = _run_artifact(authority, github_run_id, COLLECTOR_ARTIFACT)
    fields = ('githubRunId', 'githubEventName', 'githubRef', 'appRevision', 'runId',
              'successfulTasks', 'requiredTasks', 'complete', 'executionCompleted', 'outcome')
    require(all(receipt.get(key) == clock.get(key) for key in fields),
            'Downloaded collector receipt differs from archived run/attempt record')
    require(receipt.get('githubEventName') in ('schedule', 'workflow_dispatch')
            and receipt.get('githubRef') == 'refs/heads/main', 'Collector receipt is not approved main execution')
    require(receipt.get('corrections') == clock.get('corrections'),
            'Downloaded collector correction outcome differs from archived attempt')
    return {'githubRunId': github_run_id, 'attempt': clock['githubRunAttempt'],
            'archiveReceiptSha256': digest(canonical(clock)),
            'artifactId': artifact_meta['id'],
            'collectorArtifactTransportSha256': hashlib.sha256(artifact_bytes).hexdigest()}


def _authenticate_collector(state, correction_head, outcome, authority, coverage):
    run_id = correction_head['runId']
    candidates = []
    runs_dir = state.root / 'ci/collection-runs'
    for path in sorted(runs_dir.glob('*.json')) if runs_dir.is_dir() else []:
        row = strict_json(path.read_bytes(), path.name)
        if row.get('runId') == run_id and row.get('corrections', {}).get('receipt') == correction_head.get('outcome'):
            candidates.append(row)
    require(len(candidates) == 1, 'Collector run/attempt archive record missing or ambiguous')
    clock = candidates[0]
    require(clock.get('runId') == outcome.get('runId') == coverage.get('runId'),
            'Collector run does not match latest coverage and correction outcome')
    evidence = _authenticate_collector_record(clock, authority)
    require({key: value for key, value in clock['corrections'].items() if key != 'receipt'}
            == {key: value for key, value in outcome.items() if key not in ('runId', 'checkedAt')},
            'Correction admission result differs from authenticated collector receipt')
    return evidence


def _original_attempt_for_admission(state, group, policy_sha, admission_ref):
    """Find the real accepted model-review attempt that created this admission.

    An admitted entry copied from the immutable index is not evidence of a new
    model call. Credit requires a matching accepted attempt in the collector
    execution that first admitted the exact same immutable admission reference.
    """
    admission = strict_json(state.get(admission_ref), 'correction admission')
    matches = []
    runs_dir = state.root / 'ci/collection-runs'
    for clock_path in sorted(runs_dir.glob('*.json')) if runs_dir.is_dir() else []:
        clock = strict_json(clock_path.read_bytes(), clock_path.name)
        correction = clock.get('corrections', {})
        if not any(row.get('groupId') == group['id'] and row.get('admission') == admission_ref
                   for row in correction.get('admitted', [])):
            continue
        for attempt_ref in correction.get('attempts', []):
            attempt_index_key = 'correction-attempts/' + attempt_ref.get('sha256', '') + '.json'
            indexed_ref = state.read(attempt_index_key)
            if indexed_ref != attempt_ref:
                continue
            attempt = strict_json(state.get(attempt_ref), 'correction attempt')
            if (attempt.get('groupId') != group['id'] or attempt.get('outcome') != 'accepted'
                    or attempt.get('error') is not None or attempt.get('review') != admission.get('review')
                    or attempt.get('candidateSha256') != digest(group)
                    or attempt.get('evidenceSetSha256') != digest(group['sources'])
                    or attempt.get('policySha256') != policy_sha):
                continue
            started, completed, admitted = (attempt.get('startedAt'), attempt.get('completedAt'),
                                             admission.get('admittedAt'))
            instant(started); instant(completed); instant(admitted)
            require(started <= admitted <= completed,
                    'Accepted attempt does not bracket the original admission time')
            reservation_key = ('correction-document-reservations/' + started[:10] + '/'
                               + digest({'group': group, 'policy': policy_sha}) + '.json')
            reservation = state.read(reservation_key)
            require(reservation and reservation.get('groupId') == group['id']
                    and reservation.get('candidateSha256') == digest(group)
                    and reservation.get('reservedAt') == started,
                    'Original accepted attempt lacks its document reservation')
            matches.append({'clock': clock, 'clockPath': clock_path, 'attempt': attempt,
                            'attemptRef': attempt_ref, 'attemptIndexKey': attempt_index_key,
                            'reservationKey': reservation_key, 'reservation': reservation,
                            'admission': admission})
    require(len(matches) == 1,
            'Admission lacks one unique original authenticated accepted review attempt')
    return matches[0]


def _authenticate_publisher(state, manifest, authority, archive, remote_commit):
    """Bind the archived publisher checkpoint to its actual Actions artifact."""
    matches = []
    for path in sorted((state.root / 'cloud/sessions').rglob('*.json')):
        row = strict_json(path.read_bytes(), path.name)
        result = row.get('result', {})
        publication = result.get('publication', {}) if isinstance(result, dict) else {}
        if (row.get('phase') == 'finish' and publication.get('releaseId') == manifest.get('releaseId')
                and str(result.get('githubRunId', '')).isdigit()):
            matches.append(row)
    require(len(matches) == 1, 'Publisher finish checkpoint for this release is missing or ambiguous')
    checkpoint = matches[0]
    require(checkpoint.get('appRevision') == manifest.get('appRevision')
            and checkpoint.get('contractSha256') == manifest.get('contractSha256'),
            'Publisher checkpoint code or contract differs from the release')
    published = checkpoint['result']
    session_match = re.fullmatch(r'github-publisher-(\d+)-(\d+)', checkpoint['sessionId'])
    require(session_match is not None, 'Publisher session identity is invalid')
    github_run_id = int(published['githubRunId'])
    run = _api_json(authority, f'actions/runs/{github_run_id}')
    require(run.get('id') == github_run_id and run.get('repository', {}).get('full_name') == PROJECT
            and run.get('path') == '.github/workflows/subscription-publisher.yml'
            and run.get('status') == 'completed' and run.get('conclusion') == 'success'
            and run.get('head_branch') == 'main' and run.get('head_sha') == manifest.get('appRevision')
            and int(session_match.group(1)) == github_run_id
            and int(session_match.group(2)) == run.get('run_attempt')
            and run.get('event') == published.get('githubEventName'),
            'Publisher workflow identity does not authenticate archived checkpoint')
    listing = _api_json(authority, f'actions/runs/{github_run_id}/artifacts')
    matches = [item for item in listing.get('artifacts', [])
               if item.get('name') == 'daily-publication-receipt' and item.get('expired') is False
               and item.get('workflow_run', {}).get('id') == github_run_id]
    require(len(matches) == 1, 'Expected one unexpired daily-publication-receipt artifact')
    meta = matches[0]
    try:
        payload = authority._api(f"actions/artifacts/{meta['id']}/zip", binary=True)
    except (OSError, subprocess.SubprocessError, ValueError):
        raise Unavailable('GitHub publisher artifact download') from None
    require(meta.get('digest') == 'sha256:' + hashlib.sha256(payload).hexdigest(),
            'Publisher artifact transport digest differs')
    try:
        with zipfile.ZipFile(io.BytesIO(payload)) as archive_zip:
            require(archive_zip.namelist() == ['smp-publish-receipt.json'],
                    'Unexpected publisher artifact inventory')
            receipt = strict_json(archive_zip.read('smp-publish-receipt.json'), 'publisher receipt')
    except (zipfile.BadZipFile, KeyError, OSError) as exc:
        raise ValueError('Malformed authenticated publisher artifact') from exc
    require(receipt.get('githubRunId') == published.get('githubRunId')
            and receipt.get('githubEventName') == published.get('githubEventName')
            and receipt.get('appRevision') == published.get('appRevision')
            and receipt.get('activated') is True and receipt.get('publication') == published.get('publication')
            and receipt.get('publication', {}).get('published') is True
            and receipt.get('publication', {}).get('releaseId') == manifest.get('releaseId'),
            'Publisher artifact differs from its retained finish checkpoint or release')
    archive_receipt = receipt.get('archive', {})
    archive_commit = archive_receipt.get('commit')
    require(archive_receipt.get('ref') == archive.remote_ref
            and isinstance(archive_commit, str) and re.fullmatch(r'[0-9a-f]{40}', archive_commit)
            and re.fullmatch(r'[0-9a-f]{64}', archive_receipt.get('manifestSha256', '')),
            'Publisher artifact lacks its exact final archive acknowledgement')
    require(archive.is_ancestor(archive_commit, remote_commit),
            'Publisher final archive acknowledgement is not retained in current archive history')
    historic_manifest = archive.manifest_at(archive_commit)
    require(digest(historic_manifest) == archive_receipt['manifestSha256'],
            'Publisher archive manifest acknowledgement differs')
    return {'githubRunId': github_run_id, 'artifactId': meta['id'],
            'checkpointSha256': digest(canonical(checkpoint)),
            'artifactTransportSha256': hashlib.sha256(payload).hexdigest(),
            'archiveCommit': archive_commit, 'archiveManifestSha256': archive_receipt['manifestSha256'],
            'releaseId': manifest['releaseId']}


def _verified_gate(state, saved, manifest, authority):
    provenance = manifest.get('testProvenance', {})
    run_id, artifact_id = provenance.get('githubRunId'), provenance.get('githubArtifactId')
    require(type(run_id) is int and run_id > 0 and type(artifact_id) is int and artifact_id > 0,
            'Release manifest lacks gate run/artifact identity')
    receipt = state.read(f'gate-receipts/{run_id}.json')
    require(receipt and receipt.get('githubArtifactId') == artifact_id,
            'Archived gate receipt missing or has another artifact ID')
    require(digest(receipt) == manifest.get('testReceiptSha256'), 'Release gate receipt hash differs')
    try:
        payload = authority._api(f'actions/artifacts/{artifact_id}/zip', binary=True)
    except (OSError, subprocess.SubprocessError, ValueError):
        raise Unavailable('GitHub gate artifact download') from None
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        names = archive.namelist()
        required_names = {'gate-receipt.json', 'release-input.json', 'build.zip', 'snapshot.json'}
        log_names = {'certify-sec.log', 'refresh-edgar.log', 'refresh-filing-events.log', 'test.log'}
        require(len(names) == len(set(names)) and required_names.issubset(names)
                and set(names).issubset(required_names | log_names),
                'Unexpected main gate artifact inventory')
        gate_receipt = strict_json(archive.read('gate-receipt.json'), 'gate receipt')
        inputs = strict_json(archive.read('release-input.json'), 'gate release input')
        build = archive.read('build.zip')
        snapshot_raw = archive.read('snapshot.json')
    require({**gate_receipt, 'githubArtifactId': artifact_id} == receipt,
            'Downloaded gate receipt differs from archived gate receipt')
    require(inputs.get('artifact') == manifest.get('artifact'), 'Published artifact differs from gate-tested artifact')
    require(inputs.get('snapshot') == manifest.get('snapshot'), 'Published snapshot differs from gate-tested snapshot')
    require(digest(snapshot_raw) == inputs['snapshot']['sha256'], 'Gate snapshot bytes differ from input reference')
    require(gate_receipt.get('githubRunId') == run_id and gate_receipt.get('result') == 'pass'
            and gate_receipt.get('executedTests', 0) > 0, 'Main gate receipt is not a passing run')
    checks = gate_receipt.get('checks', {})
    require(all(isinstance(checks.get(name), dict) and checks[name].get('result') == 'pass'
                for name in ('refresh:edgar', 'refresh:filing-events', 'certify:sec', 'test')),
            'Authenticated gate did not pass the build and current-fact verification test chain')
    require(gate_receipt.get('archiveCommit') and gate_receipt.get('archiveManifestSha256'),
            'Gate receipt lacks source archive binding')
    authority.verify_test_receipt(receipt, manifest['artifact'])
    fields = unpack(build)
    require(digest(inventory(fields)) == manifest['artifact']['sha256'], 'Gate artifact inventory differs')
    require(canonical(inventory(fields)) == state.get(manifest['artifact']['inventory']),
            'Gate artifact inventory object differs from verified archive')
    require(state.get(manifest['artifact']['archive']) == build, 'Gate build archive differs from published release object')
    require(gate_receipt.get('artifactSha256') == manifest['artifact']['sha256'],
            'Main gate does not bind published artifact')
    return gate_receipt, inputs, fields, {
        'githubRunId': run_id, 'githubArtifactId': artifact_id,
        'artifactSha256': manifest['artifact']['sha256'],
        'archiveCommit': gate_receipt['archiveCommit'],
        'archiveManifestSha256': gate_receipt['archiveManifestSha256'],
        'gateReceiptSha256': digest(receipt),
        'githubArtifactTransportSha256': hashlib.sha256(payload).hexdigest(),
    }


def _verify_groups(root, state, market, requests_context, outcome, public_bundle):
    groups = requests_context['requests']['groups']
    entries = outcome.get('admitted', [])
    require(not outcome.get('pending') and {row.get('groupId') for row in entries} == {g['id'] for g in groups}
            and len(entries) == len(groups), 'Not every current correction group was admitted')
    admitted = {row['groupId']: row for row in entries}
    public = {row.get('id'): row for row in public_bundle.get('groups', [])}
    require(len(public) == len(public_bundle.get('groups', [])) and set(public) == {g['id'] for g in groups},
            'Published correction group inventory differs from current policy')
    verified_refs = {}
    for group in groups:
        policy = requests_context['reviewPolicySha256ByGroup'][group['id']]
        entry = admitted[group['id']]
        admission = replay_admission(group, entry['admission'], state, market, policy, public_bundle['checkedAt'])
        require(public[group['id']]['targets'] == group['targets'],
                'Published atomic correction group differs from admitted group')
        expected_meta = {
            'candidateSha256': admission['candidateSha256'],
            'evidenceSetSha256': admission['evidenceSetSha256'],
            'policySha256': admission['policySha256'], 'admittedAt': admission['admittedAt'],
            'reviewSha256': admission['review']['sha256'], 'result': 'accepted',
        }
        if 'reviewScope' in admission:
            expected_meta['reviewScope'] = admission['reviewScope']
        require(public[group['id']]['admission'] == expected_meta,
                'Public correction admission metadata differs from replayed admission')
        verified_refs[group['id']] = {
            'candidateSha256': admission['candidateSha256'],
            'evidenceSetSha256': admission['evidenceSetSha256'],
            'groupReviewPolicySha256': policy,
            'admissionRef': entry['admission'],
            'reviewRef': admission['review'],
        }
    return verified_refs


def _verified_rollback(state, production_head):
    """Return an archived failed-release rollback that restored this head."""
    matches = []
    event_dir = state.root / 'rollback-events'
    for path in sorted(event_dir.glob('*.json')) if event_dir.is_dir() else []:
        event = strict_json(path.read_bytes(), path.name)
        if event.get('restoredReleaseId') != production_head.get('releaseId'):
            continue
        failed_id = event.get('failedReleaseId')
        if not isinstance(failed_id, str) or not re.fullmatch(r'[0-9a-f]{64}', failed_id):
            continue
        failed_manifest = state.read('release-attempts/' + failed_id + '.json')
        staged = state.read('deployment-attempts/' + failed_id + '.json')
        if (not failed_manifest or failed_manifest.get('releaseId') != failed_id
                or digest({k: v for k, v in failed_manifest.items() if k != 'releaseId'}) != failed_id
                or failed_manifest.get('parentReleaseId') != production_head.get('releaseId')
                or not staged or not re.fullmatch(r'https://[a-z0-9-]+\.vercel\.app',
                                                    staged.get('deploymentId', ''))):
            continue
        matches.append({'event': event, 'eventPath': path, 'failedManifest': failed_manifest,
                        'failedReleaseId': failed_id, 'staged': staged})
    if not matches:
        return None
    matches.sort(key=lambda row: row['failedManifest'].get('createdAt', ''))
    return matches[-1]


def _collector_clock_for_run(state, run_id):
    matches = []
    runs_dir = state.root / 'ci/collection-runs'
    for path in sorted(runs_dir.glob('*.json')) if runs_dir.is_dir() else []:
        row = strict_json(path.read_bytes(), path.name)
        if row.get('runId') == run_id:
            matches.append((path, row))
    require(len(matches) == 1, 'Release collector record missing or ambiguous')
    return matches[0]


def _require_current_correction_policy(outcome, correction_head, context):
    """Do not treat an older-policy correction result as current evidence."""
    require(outcome.get('runId') == correction_head.get('runId'),
            'Correction collection head/run differs')
    if outcome.get('policySha256') != context['policySha256']:
        # A market contract revision can change the global correction policy
        # even when each group's review policy is unchanged. This is a missing
        # current-policy observation, not evidence for or against resolution.
        raise Unavailable('Current correction collection does not match the published market policy')


def _frozen_original_values(root, design):
    inventory_obj, _ = pin(Path(root), INVENTORY,
                           design['inputs']['publishedInventory']['sha256'])
    details = {row['auditRecordId']: row for row in design.get('exactMapping', [])}
    result = {}
    for item in design['resolutionMapping']:
        detail = details[item['auditRecordId']]
        record = _json_pointer(inventory_obj, detail['baselineInventoryPointer'])
        result[item['auditRecordId']] = record['published']
    return result


def _effective_mapped_states(mapping, requests_context, public_bundle, rollback,
                             frozen_originals, resolved_admissions_proven=True):
    """Derive only exact resolved targets or a rollback-restored original.

    This is called only after the current release gate artifact and all public
    bytes have been authenticated. An absent or disabled correction export is
    unresolved only when the separately verified rollback proof is present;
    otherwise it remains unmeasured.
    """
    requested = {target['targetId']: target for group in requests_context['requests']['groups']
                 for target in group['targets']}
    live = {target.get('targetId'): target for group in public_bundle.get('groups', [])
            for target in group.get('targets', [])}
    states = {}
    for item in mapping:
        target = requested.get(item['targetId'])
        original_record = frozen_originals.get(item['auditRecordId'])
        require(original_record is not None and digest(original_record) == item['originalSha256'],
                'Frozen original target differs from the pinned historical inventory')
        if target is not None:
            require(target.get('originalSha256') == item['originalSha256']
                    and target.get('operation') == item['operation']
                    and digest(target.get('proposedValue')) == item['requiredProposedSha256']
                    and digest(target.get('original')) == item['originalSha256'],
                    'Mapped correction request differs from frozen before/after hashes')
        actual = live.get(item['targetId'])
        if actual is not None:
            require(target is not None,
                    'Live correction target is absent from the authenticated release request')
            require(actual == target, 'Live correction target is neither exact required correction nor original')
            states[item['auditRecordId']] = (('resolved', 'ADMITTED_TESTED_AND_LIVE')
                                               if resolved_admissions_proven else
                                               ('unmeasured', 'LIVE_CORRECTION_LACKS_JOINED_ADMISSION_PROOF'))
        elif public_bundle.get('enabled') is False and not public_bundle.get('groups'):
            states[item['auditRecordId']] = (('unresolved', 'VERIFIED_ROLLBACK_RESTORED_ORIGINAL')
                                               if rollback else
                                               ('unmeasured', 'ORIGINAL_EFFECTIVE_STATE_WITHOUT_ROLLBACK_PROOF'))
        else:
            # Enabled bundles must be complete and are validated by the
            # published runtime helper; a missing target is an invalid join.
            require(public_bundle.get('enabled') is False,
                    'Enabled correction bundle omits a required mapped target')
            states[item['auditRecordId']] = ('unmeasured', 'CORRECTION_EXPORT_NOT_PROVEN')
    return states


def _require_archive_item(manifest, key, body):
    row = next((item for item in manifest.get('files', []) if item.get('key') == key), None)
    require(row is not None and row.get('sha256') == digest(body) and row.get('bytes') == len(body),
            'Required proof was not present at the gate archive checkpoint: ' + key)


def _bind_group_to_gate_archive(root, state, group, policy_sha, entry, gate_manifest):
    admission = strict_json(state.get(entry['admission']), 'correction admission')
    _require_archive_item(gate_manifest, 'state/' + entry['admission']['key'], state.get(entry['admission']))
    review_ref = admission['review']
    _require_archive_item(gate_manifest, 'state/' + review_ref['key'], state.get(review_ref))
    index_key = 'correction-admissions/' + policy_sha + '/' + digest(group) + '-' + digest(group['sources']) + '.json'
    index = state.read(index_key)
    require(index == {'groupId': group['id'], 'admission': entry['admission']},
            'Accepted immutable correction index differs')
    index_path = (state.root / index_key).resolve()
    _require_archive_item(gate_manifest, 'state/' + index_key, index_path.read_bytes())
    for source in group['sources']:
        observation_path = 'observations/' + source['observationId'] + '.json'
        observed = state.read(observation_path)
        require(observed is not None, 'Correction source observation missing from archive')
        raw = (state.root / observation_path).read_bytes()
        _require_archive_item(gate_manifest, 'state/' + observation_path, raw)
        body = state.get(source['body'])
        _require_archive_item(gate_manifest, 'state/' + source['body']['key'], body)


def _bind_original_attempt_to_gate_archive(state, group, original, gate_manifest):
    """Require the original admission execution proof at the tested checkpoint."""
    clock = original['clock']
    _require_archive_item(gate_manifest,
                          'state/ci/collection-runs/' + original['clockPath'].name,
                          original['clockPath'].read_bytes())
    _require_archive_item(gate_manifest, 'state/' + original['attemptIndexKey'],
                          canonical(original['attemptRef']))
    _require_archive_item(gate_manifest, 'state/' + original['attemptRef']['key'],
                          state.get(original['attemptRef']))
    _require_archive_item(gate_manifest, 'state/' + original['reservationKey'],
                          canonical(original['reservation']))
    admission_ref = next(row['admission'] for row in clock['corrections']['admitted']
                         if row.get('groupId') == group['id'])
    _require_archive_item(gate_manifest, 'state/' + admission_ref['key'], state.get(admission_ref))
    _require_archive_item(gate_manifest, 'state/' + original['admission']['review']['key'],
                          state.get(original['admission']['review']))


def gather(root, archive_mirror=None, restored_archive=None, now=None,
           vercel_executable='vercel', vercel_global_config=None):
    root = Path(root).resolve()
    design, mapping, pins = baseline(root)
    checked_at = now or datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    instant(checked_at)
    # Fetch and verify the currently acknowledged private archive into a fresh
    # temporary mirror. restore() performs reads only; no archive push/checkpoint.
    require((archive_mirror is None) != (restored_archive is None),
            'Choose exactly one private archive source')
    try:
        authority = GitHubAuthority(runner=_orb_macos_gh_runner)
        with tempfile.TemporaryDirectory(prefix='smp-correction-resolution-state-') as directory:
            release_root = Path(directory) / 'published-source'
            if restored_archive:
                archive = AuthenticatedArchive(restored_archive, authority)
                state_path = archive.root / 'state'
                restored = {'commit': archive.commit, 'manifestSha256': archive.manifest_sha256}
            else:
                legacy = GitArchive(archive_mirror, EVIDENCE_REMOTE)
                state_path = Path(directory) / 'state'
                try:
                    restored = legacy.restore(state_path)
                except OSError:
                    raise Unavailable('verified private archive read') from None
                except ValueError as exc:
                    if str(exc) == 'GIT_ARCHIVE_OPERATION_FAILED':
                        raise Unavailable('verified private archive read') from None
                    raise
                archive = AuthenticatedArchive(legacy.root, authority)
                require(restored['commit'] == archive.commit
                        and restored['manifestSha256'] == archive.manifest_sha256,
                        'Git restored archive differs from authenticated current archive ref')
            state = LocalStore(state_path)
            remote_commit = restored['commit']
            if os.environ.get('SMP_CORRECTION_RESOLUTION_CHILD') != '1':
                return _run_isolated_release_pipeline(root, archive, state_path, authority, directory,
                                                      vercel_executable, vercel_global_config)
            result = _gather_from_state(root, state, archive, remote_commit, restored, design,
                                        mapping, pins, checked_at, release_root, authority,
                                        vercel_executable, vercel_global_config)
            archive.verify_unchanged()
            # Keep the report's observation time at the actual completion of
            # public reads, not at command start.
            result['evaluatedAt'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            if result['measure']['status'] != 'unmeasured':
                result['measure']['observedAt'] = result['evaluatedAt']
                result['observedAt'] = result['evaluatedAt']
            return result
    except Unavailable:
        raise


def _run_isolated_release_pipeline(root, archive, state_path, authority, directory,
                                   vercel_executable, vercel_global_config):
    """Run replay helpers downloaded and hash-checked at the live app revision."""
    head = strict_json((Path(state_path) / 'heads/production.json').read_bytes(), 'production head')
    saved = strict_json((Path(state_path) / ('releases/' + head['releaseId'] + '.json')).read_bytes(),
                        'production release')
    revision = saved.get('manifest', {}).get('appRevision')
    require(isinstance(revision, str) and re.fullmatch(r'[0-9a-f]{40}', revision),
            'Published application revision is invalid')
    runtime = Path(directory) / 'authenticated-release-runtime'
    pipeline = runtime / 'web/scripts/pipeline'
    pipeline.mkdir(parents=True)
    modules = (
        'agents.py', 'archive.py', 'artifacts.py', 'contracts.py', 'corrections.py',
        'discovery.py', 'documents.py', 'provenance.py', 'publication.py',
        'regulatory.py', 'storage.py', 'validation.py', 'vercel.py',
    )
    for name in modules:
        relative = 'web/scripts/pipeline/' + name
        blob = _api_json(authority, 'contents/' + relative + '?ref=' + revision)
        require(blob.get('type') == 'file' and blob.get('encoding') == 'base64'
                and isinstance(blob.get('content'), str) and 0 <= blob.get('size', -1) <= 2_000_000,
                'Published helper source is unavailable or exceeds its read bound: ' + relative)
        try:
            raw = base64.b64decode(''.join(blob['content'].split()), validate=True)
        except (ValueError, TypeError):
            raise ValueError('Malformed published helper source: ' + relative) from None
        git_sha = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        require(len(raw) == blob['size'] and git_sha == blob.get('sha'),
                'Published helper source content address differs: ' + relative)
        (pipeline / name).write_bytes(raw)
    child = runtime / 'ops/evaluation/correction_resolution.py'
    child.parent.mkdir(parents=True)
    shutil.copyfile(Path(__file__).resolve(), child)
    output = Path(directory) / 'isolated-observation'
    env = os.environ.copy()
    env['SMP_CORRECTION_RESOLUTION_CHILD'] = '1'
    command = [sys.executable, str(child), '--root', str(root), '--authenticate-production',
               '--restored-archive', str(archive.root), '--outputprefix', str(output)]
    command.extend(['--vercel-executable', vercel_executable])
    if vercel_global_config:
        command.extend(['--vercel-global-config', vercel_global_config])
    result = subprocess.run(command, capture_output=True, text=True, timeout=300, env=env)
    if result.returncode != 0 or not output.with_suffix('.json').is_file():
        detail = (result.stderr or result.stdout or 'isolated evaluator failed').strip()[:180]
        raise Unavailable('authenticated release helper replay: ' + detail)
    return strict_json(output.with_suffix('.json').read_bytes(), 'isolated remediation observation')


def _gather_from_state(root, state, archive, remote_commit, restored, design, mapping,
                       static_pins, checked_at, release_root, authority,
                       vercel_executable='vercel', vercel_global_config=None):
    current = state.read('heads/production.json')
    require(current and not current.get('legacyBaseline'), 'Current archive has no acknowledged production release')
    saved = state.read('releases/' + current['releaseId'] + '.json')
    require(saved and saved.get('manifest', {}).get('releaseId') == current['releaseId'],
            'Current production release manifest missing')
    manifest, archived_ack = saved['manifest'], saved['acknowledgement']
    require(manifest.get('releaseId') == current['releaseId']
            and digest({k: v for k, v in manifest.items() if k != 'releaseId'}) == current['releaseId'],
            'Current archived release identity/hash differs')
    require(manifest.get('artifact'), 'Current release does not bind a tested artifact')
    rollback = _verified_rollback(state, current)
    latest = state.read('heads/latest-run.json')
    normal_current_run = bool(latest and latest.get('runId') == manifest.get('runId'))
    require(normal_current_run or rollback is not None,
            'Current production run differs without an authenticated archived rollback')
    market, release_pins = _verify_release_inputs(root, manifest, authority, design, release_root)
    context = load_policy(release_root, market)
    frozen_originals = _frozen_original_values(root, design)
    correction_head = state.read('heads/correction-collection.json')
    if normal_current_run:
        require(correction_head and correction_head.get('runId') == manifest.get('runId'),
                'Current correction admissions do not belong to published collection run')
        outcome = strict_json(state.get(correction_head['outcome']), 'correction collection')
        _require_current_correction_policy(outcome, correction_head, context)
        coverage = strict_json(state.get(latest['receipt']), 'collection coverage')
        require(coverage.get('runId') == manifest['runId'], 'Published release coverage run differs')
        collector = _authenticate_collector(state, correction_head, outcome, authority, coverage)
    else:
        # A rollback has no current collector admission event. The restored
        # release's own authenticated gate, publisher receipt and live bytes
        # prove the baseline; absent effective export proof remains unmeasured.
        outcome = None
        correction_head = None
        collector = None
    gate_receipt, gate_inputs, gate_files, gate_evidence = _verified_gate(state, saved, manifest, authority)
    publisher_evidence = _authenticate_publisher(state, manifest, authority, archive, remote_commit)
    require(gate_receipt.get('archiveManifestSha256') and gate_receipt.get('archiveCommit'),
            'Gate archive checkpoint missing')
    # Verify the gate's exact archive manifest at its retained commit; the
    # current archive can be newer after publication checkpoints.
    require(archive.is_ancestor(gate_receipt['archiveCommit'], remote_commit),
            'Gate archive checkpoint is not an ancestor of current verified archive')
    gate_manifest = archive.manifest_at(gate_receipt['archiveCommit'])
    require(digest(gate_manifest) == gate_receipt['archiveManifestSha256'],
            'Gate archive manifest pin differs')
    factual_proof = gate_receipt.get('factualCorrections')
    require(factual_proof == manifest.get('factualCorrections')
            == gate_inputs['snapshot'].get('factualCorrections'), 'Gate/release correction seals differ')
    public_raw = gate_files.get('static/factual-corrections.json')
    group_refs = {}
    if factual_proof:
        require(public_raw is not None and digest(public_raw) == factual_proof['fileSha256'],
                'Gate artifact correction bytes differ from correction seal')
    public_bundle = strict_json(public_raw, 'gate correction bundle') if public_raw is not None else None
    if public_bundle is not None:
        if public_bundle.get('enabled'):
            require(public_bundle.get('policySha256') == context['policySha256'],
                    'Gate correction bundle uses another policy')
            if outcome is None:
                require(rollback is not None,
                        'Enabled correction bundle has no authenticated collector outcome')
            else:
                group_refs = _verify_groups(release_root, state, market, context, outcome, public_bundle)
        else:
            require(public_bundle == {'schemaVersion': 1, 'enabled': False,
                                      'policySha256': None, 'checkedAt': None, 'groups': []},
                    'Disabled correction bundle is malformed')
    elif rollback:
        # The old runtime did not publish the correction export. It cannot
        # establish an effective original value, so all five stay unmeasured.
        pass
    if normal_current_run:
        collection_id = str(collector['githubRunId']) + '-' + str(collector['attempt'])
        collector_path = state.root / 'ci/collection-runs' / (collection_id + '.json')
        collector_record = strict_json(collector_path.read_bytes(), 'collector archive record')
        _require_archive_item(gate_manifest, 'state/ci/collection-runs/' + collection_id + '.json',
                              collector_path.read_bytes())
        _require_archive_item(gate_manifest, 'state/heads/correction-collection.json',
                              canonical(correction_head))
    if public_bundle is not None and public_bundle.get('enabled') and outcome is not None:
        for group in context['requests']['groups']:
            entry = next(row for row in outcome['admitted'] if row['groupId'] == group['id'])
            original = _original_attempt_for_admission(
                state, group, context['reviewPolicySha256ByGroup'][group['id']], entry['admission'])
            original_collector = _authenticate_collector_record(original['clock'], authority)
            original_receipt_ref = original['clock'].get('corrections', {}).get('receipt')
            original_outcome = strict_json(state.get(original_receipt_ref), 'original correction collection')
            require(original_outcome.get('runId') == original['clock'].get('runId')
                    and any(row.get('groupId') == group['id'] and row.get('admission') == entry['admission']
                            for row in original_outcome.get('admitted', [])),
                    'Original accepted attempt is absent from its authenticated correction receipt')
            group_refs[group['id']]['originalReviewExecution'] = {
                'collector': original_collector,
                'collectorRunRecordSha256': digest(canonical(original['clock'])),
                'attemptRef': original['attemptRef'],
                'attemptSha256': digest(canonical(original['attempt'])),
                'reservationKey': original['reservationKey'],
                'reservationSha256': digest(canonical(original['reservation'])),
            }
            _bind_group_to_gate_archive(release_root, state, group,
                                        context['reviewPolicySha256ByGroup'][group['id']], entry, gate_manifest)
            _bind_original_attempt_to_gate_archive(state, group, original, gate_manifest)
    # Reproject the accepted full six-group correction bundle from the
    # original admission references and the acknowledged parent bundle.
    parent_id = manifest.get('parentReleaseId')
    parent = state.read('releases/' + parent_id + '.json') if parent_id else None
    previous_bundle = None
    if parent:
        previous_files = unpack(state.get(parent['manifest']['artifact']['archive']))
        if 'static/factual-corrections.json' in previous_files:
            previous_bundle = strict_json(previous_files['static/factual-corrections.json'], 'parent correction bundle')
    else:
        previous_bundle = {'schemaVersion': 1, 'enabled': False, 'policySha256': None, 'checkedAt': None, 'groups': []}
    if public_bundle is not None and public_bundle.get('enabled') and outcome is not None:
        projected = project_bundle(release_root, state, market, outcome, previous_bundle=previous_bundle,
                                   publication_at=public_bundle['checkedAt'])
        require(projected == public_bundle, 'Public correction bundle differs from replayed full-group projection')
    # The full current factual bundle and its six groups are tested as part of
    # the gate's build/test chain. Keep the fixed benchmark rows separate from
    # the Xage publication-role-only group.
    correction_groups = context['requests']['groups']
    require(len(correction_groups) == 6, 'Expected five factual groups and one scoped publication-role group')
    # Confirm current production, then bind every static byte to the tested
    # artifact. `pending_files` is intentionally populated before the probe.
    try:
        adapter = VercelAdapter(state, 'prj_g8sZPXo81XT2Xopa1oLrsbYjTehV',
                                'team_gRV7FrVjjr1PPI1IvgoCEJrH', 'pikeholdings',
                                executable=vercel_executable, global_config=vercel_global_config)
        require(adapter.production_paths_controlled(), 'Vercel production paths are not verified')
        deployment_host = current['deploymentId']
        deployment_meta = strict_json(adapter._cli(['api', '/v13/deployments/' + deployment_host.removeprefix('https://'), '--raw']),
                                      'Vercel deployment metadata')
        require(deployment_meta.get('projectId') == adapter.project_id
                and deployment_meta.get('readyState') == 'READY'
                and deployment_meta.get('url') == deployment_host.removeprefix('https://'),
                'Current immutable Vercel deployment is not ready')
        adapter.pending_files = stage_files(state, manifest['artifact'], archived_ack)
        live_site = adapter.probe_production()
        verify_acknowledgement(manifest, live_site)
        require(live_site == archived_ack, 'Current public acknowledgement differs from archived acknowledgement')
        adapter.verify_static_files(deployment_host)
        live_site_after = adapter.probe_production()
        require(live_site_after == live_site,
                'Current production receipts changed during the static-byte observation')
        public_bytes = adapter.pending_files.get('static/factual-corrections.json')
        if public_bundle is not None:
            require(public_bytes == public_raw, 'Gate correction bytes differ from staged release bytes')
            live_bundle = adapter._get(adapter.site, '/factual-corrections.json')
            require(live_bundle == public_bundle, 'Current public correction bundle differs from gate-tested bundle')
        else:
            require(public_bytes is None, 'Unparsed correction export is present in tested artifact')
        # Static verification checks exact bytes. The public JSON parse above
        # verifies the effective bundle is the one exercised by the gate's
        # build-time verify-current-facts assertion and test suite.
    except (OSError, urllib.error.URLError, subprocess.SubprocessError, RuntimeError) as exc:
        if str(exc).startswith(('VERCEL_', 'GITHUB_')) or isinstance(exc, (OSError, urllib.error.URLError, subprocess.SubprocessError)):
            partial = {
                'archiveCommit': remote_commit, 'archiveManifestSha256': restored['manifestSha256'],
                'collector': collector, 'gate': gate_evidence, 'publisher': publisher_evidence,
                'publishedSourcePins': release_pins, 'productionAppRevision': manifest['appRevision'],
                'releaseId': current['releaseId'], 'currentProductionObservation': None,
                'productionReadUnavailable': 'Vercel current production read',
            }
            partial_rows = []
            states = {}
            for item in mapping:
                ref = group_refs.get(item['groupId'], {})
                partial_rows.append({**item, 'state': 'unmeasured',
                    'reasonCode': 'PRODUCTION_VERIFICATION_UNAVAILABLE',
                    **ref, 'gateRunId': gate_evidence['githubRunId'],
                    'gateArtifactId': gate_evidence['githubArtifactId'],
                    'artifactSha256': gate_evidence['artifactSha256'],
                    'releaseId': current['releaseId'], 'publicObservationRefs': []})
                states[item['auditRecordId']] = ('unmeasured', 'Production verification unavailable.')
            result = _observation(root, checked_at, states, partial, None)
            result['measure']['records'] = partial_rows
            result['measure']['evidence'] = partial
            return result
        raise
    if public_bundle is None:
        target_states = {item['auditRecordId']: ('unmeasured', 'CURRENT_RELEASE_HAS_NO_CORRECTION_EXPORT')
                         for item in mapping}
    else:
        target_states = _effective_mapped_states(mapping, context, public_bundle, rollback is not None,
                                                 frozen_originals,
                                                 resolved_admissions_proven=not rollback)
    rows = []
    for item in mapping:
        state_name, reason_code = target_states[item['auditRecordId']]
        rows.append({**item, 'state': state_name, 'reasonCode': reason_code,
                     **group_refs.get(item['groupId'], {}), 'gateRunId': gate_evidence['githubRunId'],
                     'gateArtifactId': gate_evidence['githubArtifactId'],
                     'artifactSha256': gate_evidence['artifactSha256'],
                     'releaseId': current['releaseId'], 'publicObservationRefs': []})
    public_observation = {
        'at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'hosts': [adapter.site, deployment_host],
        'verifiedStaticFileCountPerHost': len([k for k in adapter.pending_files if k.startswith('static/')]),
        'factualCorrectionsSha256': digest(public_bytes) if public_bytes is not None else None,
        'staticFiles': [{'path': name, 'sha256': digest(body), 'bytes': len(body)}
                        for name, body in sorted(adapter.pending_files.items())
                        if name.startswith('static/')],
        'productionReceiptStableAcrossProbe': True,
        'releaseId': current['releaseId'],
    }
    public_ref = {'archiveCommit': remote_commit, 'archiveManifestSha256': restored['manifestSha256'],
                  'collector': collector, 'gate': gate_evidence, 'publisher': publisher_evidence,
                  'publishedSourcePins': release_pins,
                  'public': public_observation,
                  'productionAppRevision': manifest['appRevision'], 'releaseId': current['releaseId']}
    if rollback:
        public_ref['verifiedRollback'] = {
            'eventPath': 'rollback-events/' + rollback['eventPath'].name,
            'eventSha256': digest(rollback['eventPath'].read_bytes()),
            'failedReleaseId': rollback['failedReleaseId'],
            'restoredReleaseId': current['releaseId'],
            'failedAttemptManifestSha256': digest(canonical(rollback['failedManifest'])),
            'failedDeploymentId': rollback['staged']['deploymentId'],
        }
    for row in rows:
        row['publicObservationRefs'] = [public_observation]
    result = _observation(root, public_observation['at'],
                          {row['auditRecordId']: (row['state'], row['reasonCode']) for row in rows},
                          public_ref, None)
    result['measure']['records'] = rows
    result['measure']['evidence'] = public_ref
    return result


def markdown(report):
    measure = report['measure']
    lines = [
        '# Current known-contradiction remediation observation', '',
        f"Evaluated at {report['evaluatedAt']}. Status: **{measure['status']}**.", '',
        f"Resolved {measure['verifiedResolvedCount']}/5; positively unresolved {measure['verifiedUnresolvedCount']}; unmeasured {measure['unmeasuredCount']}.", '',
        'This measures only the five mapped records from the frozen audit. It does not estimate current precision, recall or general site accuracy. The historical 177-record audit remains unchanged.', '',
        '| Historical record | Correction group | State | Reason |', '|---|---|---|---|',
    ]
    for row in measure['records']:
        lines.append(f"| `{row['auditRecordId']}` | `{row['groupId']}` | {row['state']} | {row['reasonCode']} |")
    lines += ['', 'No overall score is calculated.', '']
    if measure.get('unavailablePhase'):
        lines.insert(4, f"Authenticated read unavailable at: {measure['unavailablePhase']}.")
        lines.insert(5, '')
    return '\n'.join(lines)


def write_pair(prefix, result):
    prefix = Path(prefix)
    json_path, md_path = prefix.with_suffix('.json'), prefix.with_suffix('.md')
    require(not json_path.exists() and not md_path.exists(), 'Refusing to overwrite evaluation output')
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    md_path.write_text(markdown(result))
    return json_path, md_path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, help='Repository root containing the frozen mapping and policy')
    parser.add_argument('--authenticate-production', action='store_true', help='Use existing read-only GitHub, archive and Vercel authority')
    parser.add_argument('--archive-mirror', help='Fresh local mirror to read through the existing Git archive adapter')
    parser.add_argument('--restored-archive', help='Immutable local extraction of the private archive; its current GitHub ref and every byte are verified')
    parser.add_argument('--vercel-executable', default='vercel', help='Existing official Vercel CLI executable path')
    parser.add_argument('--vercel-global-config', help='Existing Vercel CLI config directory; read in place')
    parser.add_argument('--outputprefix', required=True, help='New output path prefix; existing files are refused')
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    try:
        if args.authenticate_production:
            require((args.archive_mirror is None) != (args.restored_archive is None),
                    'Authenticated gather requires exactly one archive source')
            result = gather(root, args.archive_mirror, args.restored_archive,
                            vercel_executable=args.vercel_executable,
                            vercel_global_config=args.vercel_global_config)
        else:
            result = observation(root)
    except Unavailable as exc:
        result = observation(root, unavailable=str(exc))
    except (ValueError, OSError, KeyError, TypeError, zipfile.BadZipFile) as exc:
        print(json.dumps({'error': type(exc).__name__, 'reason': str(exc)[:200]}), file=sys.stderr)
        return 2
    try:
        paths = write_pair(args.outputprefix, result)
    except (ValueError, OSError) as exc:
        print(json.dumps({'error': type(exc).__name__, 'reason': str(exc)[:200]}), file=sys.stderr)
        return 2
    print(json.dumps({'status': result['measure']['status'], 'resolved': result['measure']['verifiedResolvedCount'],
                      'unresolved': result['measure']['verifiedUnresolvedCount'], 'unmeasured': result['measure']['unmeasuredCount'],
                      'json': str(paths[0]), 'markdown': str(paths[1])}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
