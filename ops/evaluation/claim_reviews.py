"""Offline inventory and source-byte bindings for manual published-claim reviews.

Passing these checks never certifies the reviewers' semantic judgments.
"""
import argparse
from collections import Counter
import html
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'web/scripts/pipeline'))
from contracts import digest, instant, require, valid_hash
from discovery import Page
from storage import LocalStore

PARTITIONS = {'events_a_m', 'events_n_z', 'supplier_fields'}
VERDICTS = {'supported', 'contradicted', 'insufficient', 'primary_source_missing'}
EVENTS = 'web/src/data/tracker/events.ts'
SUPPLIERS = 'web/src/data/tracker/suppliers.ts'
EVIDENCE = 'web/src/data/evidence.ts'
ORIGINALS = 'web/src/data/tracker/originals.json'
BASELINE = 'contracts/factual-baseline.json'
INVENTORY_NAMES = {'events', 'suppliers', 'evidence'}
MIGRATION_SCOPE = 'frozen_historical_benchmark_only'
FIXTURE = 'ops/evaluation/fixtures/varonis-primary-2026-10-23/press-release.html'
PROVENANCE = 'ops/evaluation/fixtures/varonis-primary-2026-10-23/provenance.json'
RECEIPT = 'docs/active/daily-pipeline/receipts/varonis-missing-event-2026-10-22.md'
FIXTURE_ID = 'TR-varonis-proofpoint-agreement'
FIXTURE_SHA = '6c712edbfb4aa71e87567f5dc9de15dc6efebb72de73154daff595bbb9b220ca'
FIXTURE_URL = 'https://www.proofpoint.com/us/newsroom/press-releases/proofpoint-acquire-varonis-creating-global-leader-data-and-ai-security'


def inside(root, name):
    root = Path(root).resolve()
    path = (root / name).resolve()
    require(path.is_relative_to(root), 'Path escapes root: ' + str(name))
    return path


def pinned(root, pin, parse=True):
    require(set(pin) == {'path', 'sha256'} and valid_hash(pin['sha256']), 'Invalid hash pin')
    raw = inside(root, pin['path']).read_bytes()
    require(digest(raw) == pin['sha256'], 'Input hash mismatch: ' + pin['path'])
    return strict_json(raw) if parse else raw


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'Duplicate JSON property: ' + key)
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda _: require(False, 'Non-finite JSON input'))


def json_array(root, path, name):
    source = inside(root, path).read_text()
    match = re.search(r'export\s+const\s+' + re.escape(name) + r'\s*:[^=]+?=\s*', source)
    require(match is not None, 'Known JSON array declaration missing: ' + name)
    value, _ = json.JSONDecoder().raw_decode(source, match.end())
    require(isinstance(value, list), 'Dataset is not an array: ' + name)
    return value


def expected_records(root):
    events = json_array(root, EVENTS, 'handCollectedEvents')
    suppliers = json_array(root, SUPPLIERS, 'manualTrackerSuppliers')
    return records_from_arrays(events, suppliers)


def records_from_arrays(events, suppliers):
    rows = []
    for event in events:
        initial = event['supplierId'][0].lower()
        require('a' <= initial <= 'z', 'Supplier initial outside partition')
        rows.append({'id': 'event:' + event['id'], 'supplierId': event['supplierId'],
                     'partition': 'events_a_m' if initial <= 'm' else 'events_n_z', 'published': event})
    for supplier in suppliers:
        if supplier.get('edgarId'):
            continue
        for field in ('lastRound', 'headlineMetric', 'ownership'):
            if field in supplier:
                rows.append({'id': 'supplier:' + supplier['id'] + ':' + field,
                             'supplierId': supplier['id'], 'field': field,
                             'partition': 'supplier_fields', 'published': supplier[field]})
    require(len(rows) == len({r['id'] for r in rows}), 'Duplicate source record ID')
    return rows


def migrated_records(root, manifest, inventory, migration_pin):
    """An explicit pinned alternative to historical TypeScript byte verification."""
    migration = pinned(root, migration_pin)
    require(isinstance(migration, dict) and set(migration) == {
        'schemaVersion', 'kind', 'scope', 'historicalManifest', 'originals', 'baseline',
        'inventoryCounts', 'benchmarkCounts'}, 'Source migration schema differs')
    require(type(migration['schemaVersion']) is int and migration['schemaVersion'] == 1
            and migration['kind'] == 'pinned_historical_claim_source_migration'
            and migration['scope'] == MIGRATION_SCOPE, 'Unsupported source migration')
    require(pinned(root, migration['historicalManifest']) == manifest, 'Migration historical manifest differs')
    require(migration['originals'].get('path') == ORIGINALS and migration['baseline'].get('path') == BASELINE,
            'Unexpected migration source path')
    originals = pinned(root, migration['originals'])
    baseline = pinned(root, migration['baseline'])
    require(isinstance(originals, dict) and set(originals) == INVENTORY_NAMES, 'Migration original inventory schema differs')
    require(isinstance(baseline, dict) and set(baseline) == {'schemaVersion', 'inventories'}
            and type(baseline['schemaVersion']) is int and baseline['schemaVersion'] == 1
            and isinstance(baseline['inventories'], dict) and set(baseline['inventories']) == INVENTORY_NAMES,
            'Migration baseline schema differs')
    counts = migration['inventoryCounts']
    require(isinstance(counts, dict) and set(counts) == INVENTORY_NAMES
            and all(type(value) is int and value > 0 for value in counts.values()), 'Migration inventory counts invalid')
    benchmark_counts = migration['benchmarkCounts']
    require(isinstance(benchmark_counts, dict) and set(benchmark_counts) == {'records', 'evidence'}
            and all(type(value) is int and value > 0 for value in benchmark_counts.values()), 'Migration benchmark counts invalid')
    for name in sorted(INVENTORY_NAMES):
        rows, hashes = originals[name], baseline['inventories'][name]
        require(isinstance(rows, list) and len(rows) == counts[name]
                and all(isinstance(row, dict) and isinstance(row.get('id'), str) and row['id'] for row in rows),
                'Migration original inventory count/schema differs: ' + name)
        require(len({row['id'] for row in rows}) == len(rows), 'Duplicate migration original ID: ' + name)
        require(isinstance(hashes, dict) and all(valid_hash(value) for value in hashes.values()),
                'Invalid migration baseline hashes: ' + name)
        require({row['id']: digest(row) for row in rows} == hashes, 'Migration original before hashes differ: ' + name)
    expected = records_from_arrays(originals['events'], originals['suppliers'])
    require(len(expected) == benchmark_counts['records'] == len(inventory['records']), 'Migration benchmark count differs')
    require(inventory['records'] == expected, 'Frozen inventory differs from migrated original records')
    original_evidence = {row['id']: row for row in originals['evidence']}
    registry = {row['id']: row for row in inventory['evidence']}
    require(len(registry) == len(inventory['evidence']) == benchmark_counts['evidence'], 'Migration benchmark evidence count differs')
    for eid, row in registry.items():
        require(eid in original_evidence and row == original_evidence[eid], 'Frozen evidence object differs from migrated original: ' + eid)
    metadata = {'mode': 'explicit_pinned_originals_migration', 'scope': MIGRATION_SCOPE,
                'migrationManifestPin': migration_pin,
                'historicalManifestPin': migration['historicalManifest'],
                'originalsPin': migration['originals'], 'baselinePin': migration['baseline'],
                'inventoryCountsVerified': counts, 'benchmarkCountsVerified': benchmark_counts,
                'semanticAdmission': False,
                'historicalSourceFilesRetainedAsMetadata': True}
    return expected, metadata


def normalized(value):
    return re.sub(r'\s+', ' ', html.unescape(value)).strip()


def source_texts(body, url):
    raw = body.decode('utf8', errors='replace')
    texts = [raw, re.sub(r'<[^>]+>', ' ', raw)]
    # Auditors used both the article-aware parser and full HTML text. Both
    # must still resolve to the exact archived bytes, never registry excerpts.
    try:
        page = Page(raw, source_url=url)
        texts.append(page.readable)
    except (ValueError, AttributeError, TypeError):
        pass
    return [normalized(text) for text in texts]


def quotes(proof):
    excerpts = proof.get('support', {}).get('excerpts', [])
    require(isinstance(excerpts, list), 'Excerpt inventory must be a list')
    result = []
    for excerpt in excerpts:
        text = excerpt if isinstance(excerpt, str) else excerpt.get('quote')
        require(isinstance(text, str) and normalized(text), 'Empty or malformed proof excerpt')
        result.append(text)
    return result


def retained_fixture(root, manifest, proof):
    pins = manifest.get('retainedPrimary')
    require(pins and set(pins) == {'provenance', 'receipt'}, 'Unbound local fixture exception')
    require(pins['provenance']['path'] == PROVENANCE and pins['receipt']['path'] == RECEIPT,
            'Unknown retained provenance/receipt')
    provenance = pinned(root, pins['provenance'])
    receipt = pinned(root, pins['receipt'], parse=False).decode('utf8')
    require(provenance.get('kind') == 'retained_manual_primary_evidence'
            and provenance.get('provenanceReceipt') == RECEIPT and FIXTURE_SHA in receipt,
            'Retained primary provenance differs')
    rows = [f for f in provenance['fixtures'] if f.get('file') == 'press-release.html']
    require(len(rows) == 1, 'Retained fixture missing or duplicate')
    entry = rows[0]
    require(proof.get('proofKind') == 'retained_primary_fixture'
            and proof.get('evidenceId') == FIXTURE_ID and proof.get('bodyPath') == FIXTURE
            and proof.get('provenanceReceipt') == RECEIPT, 'Unknown local proof exception')
    require(entry['sha256'] == proof['bodySha256'] == FIXTURE_SHA
            and entry['sourceUrl'] == proof['url'] == FIXTURE_URL
            and entry['originalRetrievalRecordedAt'] == proof['fetchedAt'], 'Retained fixture identity/time differs')
    body = inside(root, FIXTURE).read_bytes()
    require(digest(body) == FIXTURE_SHA and len(body) == entry['bytes'], 'Retained fixture bytes differ')
    return body


def verify_proof(root, state, manifest, proof, record, registry):
    eid = proof['evidenceId']
    require(proof.get('sourceType') in ('primary', 'secondary'), 'Unknown source type')
    if eid is not None:
        require(eid in registry, 'Unknown proof evidence ID: ' + str(eid))
        require(proof['url'] == registry[eid]['canonicalUrl'], 'Proof canonical URL differs: ' + eid)
    cited = eid in record['published']['evidenceIds']
    if not cited:
        label = proof.get('relationship', '')
        require(isinstance(label, str) and ('additional' in label.lower() or 'supplemental' in label.lower()),
                'Unlabeled supplemental proof: ' + str(eid))
        require(bool(proof.get('observationId')), 'Supplemental proof lacks archived observation')
    for key in ('fetchedAt', 'sourceVerifiedAt'):
        if proof.get(key) is not None:
            require(instant(proof[key]) <= instant(manifest['evaluatedAt']), 'Proof timestamp after audit: ' + key)
    excerpt_values = quotes(proof)
    if proof.get('observationId'):
        oid = proof['observationId']
        require(valid_hash(oid), 'Invalid observation ID')
        observation = state.read('observations/' + oid + '.json')
        require(observation and observation.get('observationId') == oid, 'Observation identity differs')
        require(observation.get('status') in ('fetched', 'not_modified', 'retained_immutable'), 'Proof observation unsuccessful')
        require(proof['url'] in (observation.get('requestedUrl'), observation.get('finalUrl')),
                'Observation URL differs: ' + str(eid))
        require(proof['fetchedAt'] == observation['fetchedAt'], 'Observation fetch time differs: ' + str(eid))
        instant(proof['fetchedAt'])
        if observation.get('verifiedAt') is not None:
            require(instant(observation['verifiedAt']) <= instant(manifest['evaluatedAt']), 'Observation verification after audit')
        if proof.get('sourceVerifiedAt') is not None:
            require(proof['sourceVerifiedAt'] == observation.get('verifiedAt'), 'Observation verification time differs')
        require(proof['bodySha256'] == observation['body']['sha256'], 'Observation body hash differs: ' + str(eid))
        if proof.get('bodyBytes') is not None:
            require(proof['bodyBytes'] == observation['body']['bytes'], 'Declared body length differs')
        # Deliberately ignore reviewer-supplied bodyPath/observationPath.
        body = state.get(observation['body'])
    elif proof.get('bodySha256') is not None:
        body = retained_fixture(root, manifest, proof)
    else:
        require(not excerpt_values, 'Quoted proof has no source body')
        return {'bound': False, 'primary': False, 'quoteCount': 0}
    candidates = source_texts(body, proof['url'])
    for index, quote in enumerate(excerpt_values):
        require(any(normalized(quote) in text for text in candidates), 'Proof excerpt not in source: ' + record['id'] + '/' + str(eid) + '/excerpt[' + str(index) + ']')
    return {'bound': True, 'primary': proof['sourceType'] == 'primary', 'quoteCount': len(excerpt_values)}


def evaluate(root, state_root, manifest, source_migration_pin=None):
    root = Path(root).resolve()
    require(manifest.get('schemaVersion') == 1, 'Unsupported review manifest')
    instant(manifest['evaluatedAt'])
    require(set(manifest['inputs']) == {'inventory', 'reviews'}, 'Manifest input inventory differs')
    require(set(manifest['inputs']['reviews']) == PARTITIONS, 'Missing or unexpected review partition')
    inventory = pinned(root, manifest['inputs']['inventory'])
    if 'createdAt' in inventory:
        require(instant(inventory['createdAt']) <= instant(manifest['evaluatedAt']), 'Inventory created after audit')
    migration_metadata = None
    if source_migration_pin is None:
        for path in (EVENTS, SUPPLIERS, EVIDENCE):
            require(digest(inside(root, path).read_bytes()) == inventory['sourceFiles'][path], 'Dataset hash differs: ' + path)
        expected = expected_records(root)
        require(inventory['records'] == expected, 'Frozen inventory differs from independently decoded source arrays')
    else:
        expected, migration_metadata = migrated_records(root, manifest, inventory, source_migration_pin)
    registry = {e['id']: e for e in inventory['evidence']}
    require(len(registry) == len(inventory['evidence']), 'Duplicate evidence registry ID')
    expected_eids = {eid for row in expected for eid in row['published']['evidenceIds']}
    require(set(registry) == expected_eids, 'Frozen evidence ID inventory differs')
    state = LocalStore.__new__(LocalStore)
    state.root = Path(state_root).resolve()
    require(state.root.is_dir(), 'Read-only archive state missing')
    output, partitions = [], {}
    for partition in sorted(PARTITIONS):
        review = pinned(root, manifest['inputs']['reviews'][partition])
        require(review.get('kind') == 'archived_published_claim_review' and review.get('schemaVersion') == 1, 'Review kind/schema differs')
        require(instant(review.get('evaluatedAt')) <= instant(manifest['evaluatedAt']), 'Review evaluated after audit')
        dataset = SUPPLIERS if partition == 'supplier_fields' else EVENTS
        require(review['datasetPath'] == dataset and review['datasetFileSha256'] == inventory['sourceFiles'][dataset], 'Review dataset binding differs')
        evidence_path = review.get('evidenceRegistryPath', review.get('evidenceDatasetPath'))
        evidence_hash = review.get('evidenceRegistryFileSha256', review.get('evidenceDatasetFileSha256'))
        require(evidence_path == EVIDENCE and evidence_hash == inventory['sourceFiles'][EVIDENCE], 'Review evidence registry binding differs')
        rows = {r['id']: r for r in expected if r['partition'] == partition}
        records = review['records']
        require(len(records) == len({r['id'] for r in records}) == len(rows), 'Review omission or duplicate: ' + partition)
        require(set(rows) == {r['id'] for r in records}, 'Review IDs differ: ' + partition)
        ids = review['expectedRecordIds']
        require(len(ids) == len(set(ids)) and set(ids) == set(rows), 'Declared review IDs differ')
        require(review['reviewedCount'] == len(rows), 'Reviewed count differs')
        require(review['inventoryCount'] in (len(rows), sum(r['partition'].startswith('events_') for r in expected)) if partition.startswith('events_') else review['inventoryCount'] == len(rows), 'Review inventory count differs')
        if 'subsetInventoryCount' in review:
            require(review['subsetInventoryCount'] == len(rows), 'Subset count differs')
        counts = Counter()
        for record in records:
            original = rows[record['id']]
            require(record['published'] == original['published'] and record['supplierId'] == original['supplierId'], 'Published record changed: ' + record['id'])
            require(record['verdict'] in VERDICTS, 'Unknown verdict')
            proofs = record['sourceEvidence']
            require(set(original['published']['evidenceIds']) <= {p['evidenceId'] for p in proofs}, 'Cited evidence missing from review')
            bindings = [verify_proof(root, state, manifest, p, record, registry) for p in proofs]
            if record['verdict'] == 'supported':
                require(any(b['bound'] and b['primary'] and b['quoteCount'] for b in bindings), 'Supported verdict lacks quoted primary body')
            counts[record['verdict']] += 1
            output.append({'id': record['id'], 'partition': partition, 'supplierId': record['supplierId'],
                           'verdict': record['verdict'], 'bodyProofsVerified': sum(b['bound'] for b in bindings),
                           'quoteCountVerified': sum(b['quoteCount'] for b in bindings),
                           'checks': record.get('checks'), 'limitations': record.get('limitations', []),
                           'proposedCorrection': record.get('proposedCorrection')})
        partitions[partition] = {'inventoryCount': len(rows), 'reviewedCount': len(records), 'verdictCounts': dict(sorted(counts.items()))}
    verdict_counts = Counter(r['verdict'] for r in output)
    report = {'schemaVersion': 1, 'kind': 'published_claim_review_binding_report', 'evaluatedAt': manifest['evaluatedAt'],
            'appRevision': inventory.get('applicationRevision'), 'bindingChecksPassed': True,
            'inputPins': manifest['inputs'], 'sourceFiles': inventory['sourceFiles'],
            'retainedPrimaryPins': manifest.get('retainedPrimary'),
            'verifierFileSha256': digest(Path(__file__).read_bytes()),
            'verdictCounts': {key: verdict_counts[key] for key in sorted(VERDICTS)},
            'manifestSha256': digest(manifest), 'bindingsVerified': True, 'semanticVerdictsIndependentlyVerified': False,
            'semanticAdmission': False, 'sourceVerificationMode': 'explicit_pinned_originals_migration' if migration_metadata else 'historical_typescript_bytes',
            'inventoryCount': len(expected), 'reviewedCount': len(output), 'partitions': partitions,
            'nonSupportedRecords': [r for r in output if r['verdict'] != 'supported'],
            'records': output, 'limitations': ['Checks establish frozen inventory and archived byte/quote bindings only; they do not certify the manual interpretations.',
            'Historical support does not establish current endpoint freshness, claim admission, publishing readiness or completeness of eligible market events.',
            'This bounded review cannot estimate all-site precision, recall or reader value. No semantic verdict is rewritten.']}
    if migration_metadata:
        report['sourceMigration'] = migration_metadata
        report['limitations'].append('Explicit migration binds the frozen historical benchmark to unchanged original JSON values; current effective corrected facts are not audited.')
    return report


def markdown(report):
    lines = ['# Published claim review bindings', '', 'Frozen records and archived proof bindings verified. Manual semantic verdicts remain reviewer judgments.', '',
             'Source verification mode: ' + report.get('sourceVerificationMode', 'historical_typescript_bytes') + '.', '',
             '| Partition | Records | Verdict counts |', '|---|---:|---|']
    for name, row in report['partitions'].items():
        lines.append('| ' + name + ' | ' + str(row['reviewedCount']) + ' | ' + ', '.join(k + ': ' + str(v) for k, v in row['verdictCounts'].items()) + ' |')
    lines += ['', '## Records requiring review', '']
    for row in report['nonSupportedRecords']:
        lines += ['- ' + row['id'] + ': ' + row['verdict'] + '. ' + json.dumps(row['proposedCorrection'], ensure_ascii=False)]
    lines += ['', '## Limits', '', *['- ' + s for s in report['limitations']], '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    parser.add_argument('--state', required=True)
    parser.add_argument('--manifest', required=True)
    parser.add_argument('--outputprefix', required=True)
    parser.add_argument('--source-migration-manifest')
    parser.add_argument('--source-migration-sha256')
    args = parser.parse_args()
    prefix = Path(args.outputprefix)
    paths = [Path(str(prefix) + suffix) for suffix in ('.json', '.md')]
    require(not any(p.exists() for p in paths), 'Refusing to overwrite review output')
    require(bool(args.source_migration_manifest) == bool(args.source_migration_sha256),
            'Both source migration manifest and raw SHA-256 pin are required together')
    manifest = strict_json(Path(args.manifest).read_bytes())
    migration_pin = {'path': args.source_migration_manifest, 'sha256': args.source_migration_sha256} if args.source_migration_manifest else None
    report = evaluate(args.root, args.state, manifest, source_migration_pin=migration_pin)
    paths[0].parent.mkdir(parents=True, exist_ok=True)
    with paths[0].open('x') as stream:
        stream.write(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    with paths[1].open('x') as stream:
        stream.write(markdown(report))
    print(json.dumps({'bindingsVerified': True, 'inventoryCount': report['inventoryCount'],
                      'sourceVerificationMode': report['sourceVerificationMode'], 'semanticAdmission': False,
                      'outputs': [str(p) for p in paths]}))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError) as error:
        print('Review bindings failed: ' + str(error), file=sys.stderr)
        raise SystemExit(2)
