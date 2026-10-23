"""Offline audit of the exact five HTTP 403 citation tasks. Run in OrbStack."""
import argparse
from collections import Counter
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'web/scripts/pipeline'))
from contracts import plan_run
from discovery import Page, decoded_discovery_body

EXPECTED = {'bigid:citation:TR-bigid-1', 'delinea:citation:TR-delinea-3',
            'delinea:citation:TR-delinea-5', 'sophos:citation:TR-sophos-3',
            'tines:citation:TR-tines-1'}
BASE = 'blocked-citation-audit-2026-10-23'
ARCHIVE_COMMIT = 'b78cfa15980d7be9da54b31e28b16a0840c1d112'
ARCHIVE_MANIFEST = '760b5c38fcb7fba2a3a223233539cce4eb5aa47d559571efa95b287047ac1ff8'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def instant(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00'))


def seal(state):
    rows = sorted((str(p.relative_to(state)), p.stat().st_size, p.stat().st_mtime_ns)
                  for p in state.rglob('*') if p.is_file())
    return {'fileCount': len(rows), 'metadataSha256': sha(json.dumps(rows, separators=(',', ':')).encode())}


def run(repo, state):
    before = seal(state)
    assert before['fileCount'] == 25777
    paths = {'contract': repo/'contracts/market.json', 'originals': repo/'web/src/data/tracker/originals.json',
             'coverage': repo/'docs/active/daily-pipeline/evaluations/2026-10-23/inputs/coverage.json',
             'archiveProvenance': repo/'docs/active/daily-pipeline/receipts/coverage-recovery-remote-2026-10-23.json',
             'priorReadOnlySeal': repo/'docs/active/daily-pipeline/accuracy/missing-primary-bindings-audit-2026-10-23.json'}
    inputs = {key: path.read_bytes() for key, path in paths.items()}
    contract, originals, coverage = (json.loads(inputs[key]) for key in ('contract', 'originals', 'coverage'))
    provenance = json.loads(inputs['archiveProvenance'])['canaryReceipt']['archive']
    assert provenance == {'commit': ARCHIVE_COMMIT, 'manifestSha256': ARCHIVE_MANIFEST, 'files': 25777}
    assert json.loads(inputs['priorReadOnlySeal'])['archiveAfter'] == before
    assert coverage['supplierCount'] == 74 and coverage['requiredTasks'] == 557 and coverage['successfulTasks'] == 121
    tasks = [t for t in coverage['receipts'] if t.get('errorCode') == 'HTTP_403']
    assert len(tasks) == 5 and {t['sourceId'] for t in tasks} == EXPECTED
    sources = {s['id']: s for s in contract['sources']}
    evidence = {e['id']: e for e in originals['evidence']}
    plan = plan_run(contract, coverage['checkedAt'])
    assert plan['contractSha256'] == coverage['contractSha256']
    planned = {t['taskId']: t for t in plan['tasks']}
    observations = {}
    observation_bytes = {}
    for path in sorted((state/'observations').glob('*.json')):
        raw = path.read_bytes(); observation = json.loads(raw)
        assert path.stem == observation['observationId']
        observations[path.stem] = observation
        observation_bytes[path.stem] = raw
    as_of = coverage['checkedAt']; overdue = contract['schedule']['overdueHours']
    inspected = {}; scan_candidates = {key: [] for key in EXPECTED}

    def body_view(observation):
        ref = observation['body']; key = ref['key']
        raw = (state/key).read_bytes()
        assert sha(raw) == ref['sha256'] and len(raw) == ref['bytes']
        return decoded_discovery_body(raw)

    def inspect(observation):
        oid = observation['observationId']
        if oid not in inspected:
            decoded = body_view(observation)
            page = Page(decoded.decode('utf8', errors='replace'), source_url=observation.get('finalUrl') or observation['requestedUrl'])
            text = re.sub(r'\s+', ' ', page.readable).strip()
            inspected[oid] = (page, text)
        return inspected[oid]

    def pin(observation, terms=()):
        oid = observation['observationId']
        result = {'observationId': oid, 'observationPath': str(state/'observations'/f'{oid}.json'),
                  'observationSha256': sha(observation_bytes[oid]), 'sourceId': observation['sourceId'],
                  'requestedUrl': observation['requestedUrl'], 'finalUrl': observation.get('finalUrl'),
                  'status': observation['status'], 'httpStatus': observation.get('httpStatus'),
                  'errorCode': observation.get('errorCode'), 'fetchedAt': observation['fetchedAt'],
                  'verifiedAt': observation.get('verifiedAt'), 'body': observation.get('body'),
                  'bodyRetained': bool(observation.get('body')),
                  'ageHoursAtFixedCoverage': round((instant(as_of)-instant(observation['fetchedAt'])).total_seconds()/3600, 6),
                  'withinThirtyHourSourceLimit': 0 <= (instant(as_of)-instant(observation.get('verifiedAt', observation['fetchedAt']))).total_seconds()/3600 <= overdue,
                  'earnsCurrentCoverage': False}
        if observation.get('body'):
            decoded = body_view(observation)
            result.update({'bodyPath': str(state/observation['body']['key']), 'rawBodyHashAndSizeVerified': True,
                           'decodedSha256': sha(decoded), 'decodedBytes': len(decoded)})
        if observation.get('body') and observation.get('httpStatus') == 200:
            page, text = inspect(observation)
            excerpts = []
            for term in terms:
                match = re.search(term, text, re.I)
                if match:
                    start = max(0, match.start()-60); value = text[start:start+650]
                    assert text[start:start+len(value)] == value
                    excerpts.append({'term': term, 'text': value, 'offset': start, 'normalizedTextSha256': sha(text.encode())})
            result.update({'observedCanonicals': page.canonicals, 'publicationMetadata': page.published,
                           'literalExcerpts': excerpts, 'textNormalization': 'HTML text with entity decoding and collapsed whitespace; no source bytes changed.'})
        return result

    # Scan every unique successful body for literal subject/event terms. Broad
    # substring matches such as routines are excluded by explicit word boundaries.
    successful = [o for o in observations.values() if o.get('httpStatus') == 200 and o.get('body')]
    by_body = {}
    for o in successful:
        old = by_body.get(o['body']['key'])
        if old is None or o['fetchedAt'] > old['fetchedAt']: by_body[o['body']['key']] = o
    scan_patterns = {
        'bigid:citation:TR-bigid-1': (r'\bBigID\b', r'\bRiverwood\b'),
        'delinea:citation:TR-delinea-3': (r'\bDelinea\b', r'\bTimothy Regan\b'),
        'delinea:citation:TR-delinea-5': (r'\bDelinea\b', r'\bStrongDM\b'),
        'sophos:citation:TR-sophos-3': (r'\bSophos\b', r'\bMoody[’\']?s?\b|ResearchPool'),
        'tines:citation:TR-tines-1': (r'\bTines\b', r'\bSoftBank\b|Goldman|\$125 million|\$1\.13 billion'),
    }
    for observation in by_body.values():
        decoded = body_view(observation).decode('utf8', errors='replace')
        lower = decoded.lower()
        possible = [key for key, patterns in scan_patterns.items() if key.split(':')[0] in lower and all(re.search(pattern, decoded, re.I) for pattern in patterns)]
        if not possible: continue
        page, text = inspect(observation)
        for key in possible:
            if all(re.search(pattern, text, re.I) for pattern in scan_patterns[key]):
                # Require a named subject in the actual URL/title context to
                # discard incidental mentions in unrelated filings and sitemaps.
                subject = key.split(':')[0]
                if subject in observation['requestedUrl'].lower(): scan_candidates[key].append(observation)

    records = []
    for task in sorted(tasks, key=lambda t: t['sourceId']):
        source = sources[task['sourceId']]; original = evidence[source['evidenceId']]
        assert task['supplierId'] == source['supplierId'] == planned[task['taskId']]['supplierId']
        assert planned[task['taskId']]['sourceId'] == source['id'] and source['url'] == original['canonicalUrl']
        assert source['kind'] == 'citation' and source['registration'] == 'verified'
        assert task['outcome'] == 'blocked' and task['discoveryComplete'] is False
        assert task['validatedFacts'] == [] and task['newFactIds'] == [] and len(task['observationIds']) == 1
        current = observations[task['observationIds'][0]]
        assert current['sourceId'] == source['id'] and current['requestedUrl'] == source['url']
        assert current['status'] == 'blocked' and current['httpStatus'] == 403 and current.get('errorCode') == 'HTTP_403'
        assert instant(task['startedAt']) <= instant(current['fetchedAt']) <= instant(task['completedAt']) <= instant(as_of)
        manifest_raw = (state/task['itemManifest']['key']).read_bytes()
        assert sha(manifest_raw) == task['itemManifest']['sha256'] and len(manifest_raw) == task['itemManifest']['bytes']
        history = sorted([o for o in observations.values() if o['requestedUrl'] == source['url'] or o.get('finalUrl') == source['url']], key=lambda o: (o['fetchedAt'], o['observationId']))
        prior_full = [o for o in history if o.get('httpStatus') == 200 and o.get('body') and instant(o['fetchedAt']) < instant(current['fetchedAt'])]
        terms = scan_patterns[source['id']]
        candidates = {o['observationId']: o for o in scan_candidates[source['id']]}
        # Include every successful same-URL version rather than only the latest.
        candidates.update({o['observationId']: o for o in prior_full})
        leads = []; seen_leads = set()
        for o in sorted(candidates.values(), key=lambda o: o['fetchedAt']):
            page, text = inspect(o)
            for literal in [*page.canonicals, *(link['url'] for link in page.links), *page.feeds]:
                target = urljoin(o.get('finalUrl') or o['requestedUrl'], literal).split('#')[0]
                parsed = urlsplit(target); host = parsed.hostname or ''
                if parsed.scheme not in ('http', 'https'): continue
                event_words = ('regan',) if source['evidenceId'] == 'TR-delinea-3' else ('strongdm',) if source['evidenceId'] == 'TR-delinea-5' else (source['supplierId'],)
                own = host in (source['supplierId']+'.com', 'www.'+source['supplierId']+'.com')
                relevant = (own and (parsed.path in ('', '/', '/news', '/press', '/news/rss.xml') or parsed.path.startswith('/news/') and any(word in parsed.path.lower() for word in event_words)) or host.endswith('riverwoodcapital.com') or
                            host in ('www.globenewswire.com', 'www.prnewswire.com') and (any(word in parsed.path.lower() for word in event_words) or parsed.path.rstrip('/') in ('/en/search/organization/Delinea', '/en/search/tag/delinea')) or
                            host.endswith('moodys.com') or host.endswith('goldmansachs.com') or host.endswith('softbank.com'))
                if not relevant or target in seen_leads: continue
                seen_leads.add(target)
                observed = sorted([q for q in observations.values() if q['requestedUrl'] == target or q.get('finalUrl') == target], key=lambda q: q['fetchedAt'])
                leads.append({'literalHrefOrCanonical': literal, 'resolvedUrl': target, 'disclosedInObservationId': o['observationId'],
                              'disclosedInBodySha256': o['body']['sha256'], 'isObservedCanonical': literal in page.canonicals,
                              'role': 'supplier_site_historical_lead' if source['supplierId'] in host else 'distributor_historical_lead' if 'newswire' in host else 'named_counterparty_or_agency_lead',
                              'observedResponseIds': [q['observationId'] for q in observed],
                              'successfulBodyObservationIds': [q['observationId'] for q in observed if q.get('httpStatus') == 200 and q.get('body')],
                              'isVerifiedReplacement': False})
        interpretation = {
            'bigid': 'The earlier Tracxn aggregator table lists February 8, 2024, $61.4M Series D, $1B and Riverwood Capital. The retained tracker says March 2024 and $60M. This audit preserves that discrepancy and admits no replacement funding fact. The literal BigID homepage is only a primary research entry.',
            'delinea': ('Earlier GlobeNewswire bodies retain the September CFO appointment statement and source identity. The literal Delinea homepage and distributor organization search are research entries; neither is an exact supplier-owned replacement for this CFO release.' if source['evidenceId'] == 'TR-delinea-3' else 'Earlier GlobeNewswire bodies are historical distributed Delinea statements. The retained supplier-owned January signing statement is a distinct event from March completion. Its literal completed-acquisition link is a useful primary lead only until its actual body and dates are checked.'),
            'sophos': 'The configured ResearchPool URL identifies a generic Moody’s provider listing rather than an exact Sophos rating-action document. No successful same-URL body exists, and no original agency report for this claim was found by this scan. A successful future listing response alone would not substantiate the rating claim.',
            'tines': 'No successful Bloomberg body or same-event primary funding statement was found by the disclosed retained-body scan. Original tracker prose mentioning a company newsroom and Irish Times corroboration supplies no literal URL or retained body for those alternatives.'}[source['supplierId']]
        action = {'bigid': 'After natural allowance renewal, use ordinary budgeted access to the unchanged citation if permitted. Separately locate BigID’s or Riverwood’s original round statement from the literal BigID entry, resolve amount/date differences, and retain a reviewed correction proposal if warranted.',
                  'delinea': 'After natural allowance renewal, retry the unchanged citation only through normal permitted transport. Qualify a supplier-owned event alternative from retained literal links with actual body, publication date and exact event identity before proposing any reviewed citation change.',
                  'sophos': 'Locate the exact Moody’s Sophos rating action and an openly accessible primary agency or issuer disclosure through ordinary permitted research. Retain the current citation as blocked; hold unsupported rating/date details for factual review. No proxy, login bypass or provider-listing substitution.',
                  'tines': 'Locate an openly accessible Tines, Goldman Sachs or SoftBank statement for the exact February 2025 round, then verify amount, valuation and lead investors. If ordinary Bloomberg access remains blocked, retain that status and propose a separately reviewed exact evidence replacement; do not bypass its controls.'}[source['supplierId']]
        records.append({'taskId': task['taskId'], 'sourceId': source['id'], 'supplierId': source['supplierId'],
                        'source': source, 'originalEvidence': original, 'originalEvidenceSha256': sha(json.dumps(original, sort_keys=True, separators=(',', ':')).encode()),
                        'fixedReceipt': task, 'itemManifest': json.loads(manifest_raw), 'currentBlockedObservation': pin(current),
                        'sameUrlHistory': [pin(o, terms) for o in history],
                        'sameUrlStatusCounts': dict(Counter(str(o.get('httpStatus')) for o in history)),
                        'observedSameUrlRedirects': [{'requestedUrl': o['requestedUrl'], 'finalUrl': o['finalUrl'], 'observationId': o['observationId']} for o in history if o.get('finalUrl') and o['requestedUrl'] != o['finalUrl']],
                        'manualRetrievalObjectPresent': bool(original.get('retrieval') and (state/'objects'/original['retrieval']['sha256']).is_file()),
                        'earlierSameUrlSuccessfulBodies': len(prior_full),
                        'historicalEventCandidateBodies': [pin(o, terms) for o in sorted(candidates.values(), key=lambda o: (o['requestedUrl'], o['fetchedAt']))],
                        'literalAlternateLeads': leads, 'evidenceInterpretation': interpretation,
                        'nextAction': {'owner': 'pipeline agent', 'action': action, 'humanInputRequired': False},
                        'sourceRelocationLimit': {'ordinaryCorrectionCanChangeCanonicalUrl': False, 'ordinaryCorrectionCanChangeSourceClassOrOrganization': False,
                                                  'sourceBindingRemainsBoundToImmutableOriginalUrl': True,
                                                  'futureReviewedRelocationOrNewPrimaryEvidencePathRequiredIfDifferentUrlUsed': True,
                                                  'currentlyImplementedOrAuthorizedByThisAudit': False},
                        'currentCoverageCredit': 0, 'currentOutcomeUnchanged': 'blocked',
                        'boundary': 'Citation collection checks transport. Historical body presence, a canonical URL or a distributor link does not validate financial content, refresh a check, qualify recurring discovery or authorize a URL change.'})
    after = seal(state)
    assert before == after
    assert all(path.read_bytes() == inputs[key] for key, path in paths.items())
    report = {'schemaVersion': 1, 'id': 'SEC-MARKET-BLOCKED-CITATION-AUDIT-20261023', 'auditDate': '2026-10-23',
              'fixedAsOf': as_of, 'scope': {'exactSourceIds': sorted(EXPECTED), 'blockedTasksAudited': 5,
                                          'blockedTasksRemain': 5, 'suppliersUnchanged': 74, 'requiredTasksUnchanged': 557,
                                          'successfulTasksUnchanged': 121, 'newCoverageCredit': 0},
              'inputs': {key: {'path': str(path), 'sha256': sha(inputs[key])} for key, path in paths.items()},
              'script': {'path': str(Path(__file__)), 'sha256': sha(Path(__file__).read_bytes())},
              'archive': {'root': str(state), 'provenance': provenance, 'before': before, 'after': after,
                          'allFileSizesAndMtimesUnchanged': True, 'matchesPriorReadOnlySeal': True},
              'method': {'allObservationRecordsIndexed': len(observations), 'uniqueFullSuccessBodiesScannedAndHashVerified': len(by_body),
                         'scope': 'Every successful archived body was bounded-decoded and raw hash/size checked. Explicit subject and event word patterns selected rendered-text candidates; subject must occur in requested URL to exclude unrelated page mentions. All same-URL successes are retained independently of that filter.',
                         'patterns': scan_patterns, 'limitations': 'This literal scan cannot prove that differently worded or uncited primary evidence does not exist. No live availability, redirect or access-policy result is inferred.',
                         'sourceAge': 'Age is measured against the original fixed coverage.checkedAt using the unchanged 30-hour source limit. Original fetchedAt/verifiedAt values remain unchanged. Publication date and original manual retrievedAt are distinct from a collector check.',
                         'blockedBodyAbsence': 'All five current blocked observations omit body and finalUrl. The report preserves null for absent fields and does not invent a response body, redirect destination or block reason.'},
              'summary': {'withEarlierSameUrlSuccessfulBody': sum(r['earlierSameUrlSuccessfulBodies'] > 0 for r in records),
                          'withoutEarlierSameUrlSuccessfulBody': sum(r['earlierSameUrlSuccessfulBodies'] == 0 for r in records),
                          'verifiedReplacementUrls': 0, 'ownerDecisionsNeeded': []},
              'existingReviewUnchanged': {'records': 177, 'supported': 90, 'insufficient': 71, 'missingStrictPrimary': 11, 'contradicted': 5,
                                          'bigidTableDiscrepancy': 'Insufficient primary support requiring research; no new contradiction verdict or count is assigned.'},
              'limits': {'sourceRequests': 0, 'networkRequests': 0, 'modelCalls': 0, 'admissionCalls': 0, 'realStateWrites': 0,
                         'quotaChanges': 0, 'urlOrRegistrationEdits': 0, 'chargedFetchesUnchanged': 5500,
                         'chargedModelCallsUnchanged': 80, 'chargedDocumentsUnchanged': 40, 'freshChecksClaimed': 0},
              'records': records}
    out = repo/'docs/active/daily-pipeline/accuracy'
    (out/(BASE+'.json')).write_text(json.dumps(report, indent=2, ensure_ascii=False)+'\n')
    md = ['# Five blocked citation checks, October 23, 2026', '',
          'All five fixed HTTP 403 tasks remain blocked. Three have earlier successful same-URL bodies, all beyond the unchanged 30-hour source limit at the original coverage time. Sophos and Tines have no successful same-URL body. The existing result remains 121/557 for 74 suppliers.', '',
          'I would preserve the five failures and qualify the retained supplier-owned alternatives through ordinary budgeted access after natural renewal. No owner choice blocks this work. No access control was bypassed and no URL or registration was changed.', '',
          f"The fixed collection time is `{as_of}`. The read-only archive is `{state}`, commit `{ARCHIVE_COMMIT}`, manifest `{ARCHIVE_MANIFEST}`. All {before['fileCount']:,} file size/mtime entries match the prior retained seal and remained unchanged. The script checked {len(by_body):,} distinct successful raw bodies against their stored hashes and sizes while searching literal subject/event terms. The JSON records exact observations, original times, bytes, hashes, canonicals, literal links and excerpts.", '',
          'The current 403 records retain no body and no final URL. Those absences are explicit. A block reason, redirect, canonical alternative or primary statement cannot be inferred from HTTP 403 alone. Historical success does not refresh a source check or prove the retained business claim.', '']
    for row in records:
        current = row['currentBlockedObservation']; original = row['originalEvidence']
        md += ['## '+row['sourceId'], '',
               f"Task `{row['taskId']}` requests `{row['source']['url']}`. Its original blocked observation is `{current['observationId']}`, fetched `{current['fetchedAt']}`; status is HTTP 403 with no retained response body or final URL.", '',
               f"The original evidence is `{original['id']}`, published `{original['publicationDate']}`, manually retrieved `{original['retrievedAt']}`. Its retained excerpt is a tracker input; a quote becomes body-supported only where the JSON binds literal text to a verified archived object.", '',
               row['evidenceInterpretation'], '', '| Earlier same-URL HTTP 200 observation | Original fetched time | Raw body SHA-256 | Age at fixed coverage |', '|---|---|---|---|']
        successes = [o for o in row['sameUrlHistory'] if o['httpStatus'] == 200 and o['bodyRetained']]
        for o in successes: md.append(f"| `{o['observationId']}` | `{o['fetchedAt']}` | `{o['body']['sha256']}` | {o['ageHoursAtFixedCoverage']:.2f} hours |")
        if not successes: md.append('| No retained successful body. | None. | None. | No age can establish freshness. |')
        md += ['', 'Literal alternatives retained in the inspected event bodies:', '']
        for lead in row['literalAlternateLeads']:
            if lead['resolvedUrl'] == row['source']['url']: continue
            md.append(f"- `{lead['resolvedUrl']}` is disclosed by observation `{lead['disclosedInObservationId']}`. Retained successful body count: {len(lead['successfulBodyObservationIds'])}. It remains an unqualified lead.")
        if not any(l['resolvedUrl'] != row['source']['url'] for l in row['literalAlternateLeads']): md.append('No distinct literal primary or wire replacement URL was established.')
        md += ['', 'The pipeline agent owns the next step: '+row['nextAction']['action'], '',
               'A different URL cannot close this exact citation task. The ordinary dated correction operation preserves canonical URL, source class and organization, and binding validation still consults immutable original URLs. Using a different primary page requires a future properly reviewed source-relocation or new-primary-evidence path. This audit neither designs nor implements that path.', '']
    md += ['## Scope and preservation', '',
           'Source, network, model and admission requests were zero. State/archive writes, quota changes, URL changes, registrations and new coverage credit were zero. Charged counters remain 5,500/80/40. No test, re-fetch, semantic admission or current block recovery is claimed.', '',
           'The search uses exact retained URL associations and explicit literal event patterns. It cannot rule out differently worded primary evidence elsewhere. A historical signing announcement cannot replace completion evidence, and a generic ratings-provider page cannot identify a specific rating action. An openly available alternative still needs an actual fetched body, publisher/subject/date checks and the ordinary reviewed evidence-change path.', '',
           'The existing 177-record review and all verdicts remain unchanged: 90 supported, 71 insufficient, 11 missing strict primary proof and five contradicted. BigID’s old aggregator-table difference is insufficient primary support pending research; it does not add a contradiction verdict. Source-relocation limits follow `/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/factual-corrections-spec.md` and `/Users/jessepike/code/projects/sec-market-finish-20261022/web/scripts/pipeline/corrections.py`.', '',
           f"Detailed evidence: `/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/{BASE}.json`.",
           'Reproduce in OrbStack: `orb run -m dev python3 /mnt/mac/Users/jessepike/code/projects/sec-market-finish-20261022/ops/evaluation/blocked_citation_audit.py`.', '']
    (out/(BASE+'.md')).write_text('\n'.join(md))
    return {'blockedTasks': len(records), **report['summary'], 'successfulBodiesScanned': len(by_body),
            'archiveUnchanged': before == after, 'outputs': [str(out/(BASE+ext)) for ext in ('.json', '.md')]}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=ROOT)
    parser.add_argument('--archive', type=Path, default=Path('/tmp/smp-coverage-baseline-20261023/state'))
    args = parser.parse_args()
    print(json.dumps(run(args.repo, args.archive), indent=2))
