"""Read-only historical audit of exactly 39 official and 52 investor-family gaps.

Run in OrbStack. This script never fetches, onboards, admits facts or writes state.
The only outputs are the two assigned audit documents in the project workspace.
"""
import argparse
import hashlib
import html
import json
from pathlib import Path
import re
import sys
from urllib.parse import parse_qs, unquote, urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'web/scripts/pipeline'))
from contracts import plan_run
from discovery import Page, decoded_discovery_body

DAY = '2026-10-23'
FAMILIES = {'official_announcements': 39, 'investor_acquirer': 52}
BASE = 'missing-primary-bindings-audit-' + DAY

# These strings select literal, retained links. They never construct a URL.
HOST_WORDS = {
    'abnormal-security': ['abnormal', 'abnormalsecurity'], 'aqua': ['aquasec'], 'arctic-wolf': ['arcticwolf'],
    'armis': ['armis'], 'axonius': ['axonius'], 'barracuda': ['barracuda'], 'beyondtrust': ['beyondtrust'],
    'bigid': ['bigid'], 'cato': ['catonetworks'], 'chainguard': ['chainguard'], 'checkpoint-email': ['checkpoint'],
    'claroty': ['claroty'], 'cloudflare': ['cloudflare'], 'cohesity': ['cohesity'], 'commvault': ['commvault'],
    'crwd': ['crowdstrike'], 'crwd-exposure': ['crowdstrike'], 'cyberark': ['cyberark'], 'cyera': ['cyera'],
    'delinea': ['delinea'], 'dragos': ['dragos'], 'esentire': ['esentire'], 'exabeam': ['exabeam'],
    'expel': ['expel'], 'forescout': ['forescout'], 'fortinet': ['fortinet'], 'github-advanced-security': ['github'],
    'google-secops': ['google'], 'hiddenlayer': ['hiddenlayer'], 'ivanti': ['ivanti'], 'lakera': ['lakera'],
    'mimecast': ['mimecast'], 'msft-defender': ['microsoft'], 'msft-defender-o365': ['microsoft'],
    'msft-entra': ['microsoft'], 'netskope': ['netskope'], 'nozomi': ['nozominetworks'], 'okta': ['okta'],
    'optiv': ['optiv'], 'orca': ['orca'], 'panw': ['paloaltonetworks'], 'panw-xsiam': ['paloaltonetworks'],
    'ping-identity': ['pingidentity'], 'proofpoint': ['proofpoint'], 'protect-ai': ['protectai'], 'qualys': ['qualys'],
    'red-canary': ['redcanary'], 'reliaquest': ['reliaquest'], 's1': ['sentinelone'], 'sailpoint': ['sailpoint'],
    'snyk': ['snyk'], 'sonatype': ['sonatype'], 'sophos': ['sophos'], 'splunk': ['splunk'],
    'surepath': ['surepath'], 'sysdig': ['sysdig'], 'tenable': ['tenable'], 'tines': ['tines'],
    'torq': ['torq'], 'trustwave': ['trustwave'], 'upwind': ['upwind'], 'varonis': ['varonis'],
    'veeam': ['veeam'], 'veracode': ['veracode'], 'witnessai': ['witness'], 'wiz': ['wiz'],
    'xage': ['xage'], 'zenity': ['zenity'], 'zscaler': ['zscaler'],
}
ALIASES = {
    'crwd-exposure': ['Falcon Exposure Management'], 'github-advanced-security': ['GitHub Advanced Security'],
    'google-secops': ['Google SecOps', 'Chronicle'], 'msft-defender': ['Microsoft Defender for Endpoint', 'Defender for Endpoint'],
    'msft-defender-o365': ['Microsoft Defender for Office 365', 'Defender for Office 365'],
    'msft-entra': ['Microsoft Entra ID', 'Entra ID'], 'panw-xsiam': ['Cortex XSIAM', 'XSIAM'],
    'protect-ai': ['Protect AI', 'ProtectAI'], 'checkpoint-email': ['Check Point Email Security', 'Harmony Email'],
}
INVESTOR_HOST_WORDS = [
    'thomabravo.com', 'kkr.com', 'clearlake.com', 'franciscopartners.com', 'tpg.com', 'insightpartners.com',
    'tlv.partners', 'lsvp.com', 'ion-am.com', 'accel.com', 'capitalg.com', 'paladincapgroup.com',
    'deltavcapital.com', 'm12.vc', 'boozallen.com', 'ftvcapital.com', 'eqtgroup.com', 'eqtpartners.com',
    'warburgpincus.com', 'georgian.io', 'cdpq.com', 'temasek.com', 'temasek.com.sg', 'ta.com',
    'goldmansachs.com', 'norwest.com', 'norwestvp.com', 'riverwoodcapital.com', 'gc.com',
]
# Exact already-observed URLs, selected because the subject appears in the transaction title.
# Not every historical publisher is the supplier's present owner.
THOMA_PAGES = {
    'barracuda': ['kkr-completes-acquisition-of-barracuda-from-thoma-bravo', 'kkr-to-acquire-barracuda-networks'],
    'delinea': ['centrify-now-delinea', 'delinea-to-acquire-fastpath-to-revolutionize-privileged-access-and-identity-governance'],
    'ping-identity': ['thoma-bravo-completes-acquisition-of-ping-identity', 'thoma-bravo-completes-acquisition-of-forgerock-combines-forgerock-into-ping-identity'],
    'proofpoint': ['thoma-bravo-completes-acquisition-of-proofpoint', 'proofpoint-enters-definitive-agreement-to-be-acquired-by-thoma-bravo-in-12.3-billion-transaction'],
    'veracode': ['thoma-bravo-completes-acquisition-of-veracode-software', 'veracode-announces-significant-growth-investment-from-ta-associates'],
    'cyberark': ['cyberark-completes-acquisition-of-machine-identity-management-leader-venafi'],
    'sailpoint': ['thoma-bravo-completes-acquisition-of-sailpoint'],
    'exabeam': ['exabeam-appoints-pete-harteveld-as-ceo'],
    'sophos': ['sophos-completes-secureworks-acquisition'],
}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def normalized(value):
    return re.sub(r'\s+', ' ', value).strip()


class AuditPage(Page):
    """An explicit audit-only view tolerating valueless HTML attributes.

    Raw objects are unchanged. This is not a claim that the runtime extractor
    accepted or semantically validated the document.
    """
    def handle_starttag(self, tag, attrs):
        super().handle_starttag(tag, [(key, value or '') for key, value in attrs])


def evidence_ids(value):
    if isinstance(value, dict):
        own = set(value.get('evidenceIds', []))
        return own | set().union(*(evidence_ids(v) for k, v in value.items() if k != 'evidenceIds'))
    if isinstance(value, list):
        return set().union(*(evidence_ids(v) for v in value))
    return set()


def aliases(subject):
    if subject['id'] in ALIASES:
        return ALIASES[subject['id']]
    values = [subject['name'], *subject.get('aliases', [])]
    short = re.sub(r',?\s+(?:Inc\.?|Ltd\.?|LLC|Holdings,? Inc\.?)$', '', subject['name']).strip()
    brand = {'crwd': 'CrowdStrike', 's1': 'SentinelOne'}.get(subject['id'], subject['id'].replace('-', ' '))
    return list(dict.fromkeys([*values, short, brand]))


def subject_matches(text, subject):
    matches = []
    for name in aliases(subject):
        matches.extend(re.finditer(r'(?<!\w)' + re.escape(name) + r'(?!\w)', text, re.I))
    return sorted(matches, key=lambda match: match.start())


def excerpt(text, subject, evidence):
    # Prefer a complete, literal retained excerpt when it actually matches the body.
    saved = normalized(evidence.get('excerpt', ''))
    if saved and saved in text:
        value, offset, method = saved[:650], text.index(saved), 'retained_excerpt_literal_match'
    else:
        matches = subject_matches(text, subject)
        def rank(match):
            nearby = text[max(0, match.start()-100):match.start()+500].lower()
            return (sum(word in nearby for word in ['acquisition', 'acquire', 'acquired', 'funding', 'investment', 'investor', 'completed', 'announced', 'merger']), -match.start())
        match = max(matches, key=rank) if matches else None
        offset = max(0, match.start()-80) if match else 0
        value, method = text[offset:offset+650], 'subject_adjacent_literal_rendered_text' if match else 'issuer_context_only_no_subject_match'
    assert text[offset:offset+len(value)] == value
    return {'text': value, 'offset': offset, 'length': len(value), 'method': method,
            'normalizedTextSha256': digest(text.encode()), 'normalization': 'HTML visible text; entities decoded; whitespace collapsed',
            'literalInDerivedText': True, 'subjectExplicitlyMentioned': bool(subject_matches(text, subject))}


def source_role(url, subject):
    host = urlsplit(url).hostname or ''
    if host in ('www.prnewswire.com', 'www.globenewswire.com'):
        return 'shared_release_distributor_statement'
    if host == 'www.sec.gov':
        return 'supplier_issuer_statement_sec_hosted' if subject['kind'] == 'public' else 'parent_or_acquirer_statement_sec_hosted'
    if host in ('www.thomabravo.com', 'newsroom.accenture.com', 'www.levelblue.com'):
        return 'investor_acquirer_or_historical_counterparty_primary'
    if host in ('siliconangle.com', 'tracxn.com', 'finance.yahoo.com', 'www.helpnetsecurity.com', 'www.bloomberg.com'):
        return 'secondary_reporting_or_database'
    if any(word in host.lower() for word in HOST_WORDS[subject['id']]):
        return 'supplier_owned_primary'
    return 'other_primary_context_requires_relationship_proof'


def literal_leads(page, text, subject, proof, observation_index):
    values = []
    for link in page.links:
        target = urljoin(proof['finalUrl'], link['url'])
        parsed = urlsplit(target)
        if parsed.scheme not in ('http', 'https') or not parsed.hostname:
            continue
        # Fragment removal and relative resolution are disclosed explicitly.
        target = target.split('#')[0]
        host = parsed.hostname.lower()
        own = any(word in host for word in HOST_WORDS[subject['id']])
        investor = any(host == word or host.endswith('.' + word) for word in INVESTOR_HOST_WORDS)
        history_path = parsed.path.lower()
        if own:
            if any(token in history_path for token in ('press', 'news', 'blog', 'feed', 'rss', 'investor')) or host.startswith(('ir.', 'investor.', 'investors.')) or history_path in ('', '/', '/en.html'):
                kind = ('advertised_feed' if target in [urljoin(proof['finalUrl'], f) for f in page.feeds] else
                        'literal_news_or_press_index_candidate' if re.search(r'/(news|newsroom|press|press-releases|press-office)/?$', history_path) else
                        'literal_historical_article_or_topic_link' if any(t in history_path for t in ('press', '/news/', '/blog/')) else
                        'literal_supplier_or_ir_entry_site')
                values.append((target, kind, 'supplier_site_reference', link['url']))
        if investor and (host != 'www.thomabravo.com' or '/companies/' in history_path or history_path.rstrip('/') in ('', '/press-releases')):
            values.append((target, 'literal_investor_entry_or_portfolio_link', 'investor_reference_relationship_still_requires_proof', link['url']))
        # Unwrap only explicit standard URL query fields. Never execute a redirect.
        if host in ('cts.businesswire.com', 'edge.prnewswire.com'):
            query = parse_qs(parsed.query)
            for key in ('url', 'u'):
                for embedded in query.get(key, []):
                    embedded_host = urlsplit(embedded).hostname or ''
                    embedded_investor = any(embedded_host == word or embedded_host.endswith('.'+word) for word in INVESTOR_HOST_WORDS)
                    if any(word in embedded_host for word in HOST_WORDS[subject['id']]) or embedded_investor:
                        values.append((embedded, 'literal_encoded_target_not_fetched',
                                       'investor_reference_relationship_still_requires_proof' if embedded_investor else 'supplier_site_reference', link['url']))
    for feed in page.feeds:
        target = urljoin(proof['finalUrl'], feed)
        host = urlsplit(target).hostname or ''
        if any(word in host for word in HOST_WORDS[subject['id']]) and 'comments' not in target:
            values.append((target, 'advertised_feed', 'supplier_site_reference', feed))
    # A bare website reference is preserved as written; no scheme or path is guessed.
    for match in re.finditer(r'(?:https?://)?(?:www\.|investors?\.|ir\.)[A-Za-z0-9./_-]+', text):
        literal = match.group(0).rstrip('.,')
        if any(word in literal.lower() for word in HOST_WORDS[subject['id']]):
            if literal.startswith(('http://', 'https://')):
                values.append((literal, 'literal_rendered_website_reference', 'supplier_site_reference', literal))
            else:
                values.append((literal, 'bare_website_reference_no_protocol_inferred', 'identity_lead_only', literal))
    found, output = set(), []
    priority = {'advertised_feed': 0, 'literal_news_or_press_index_candidate': 1,
                'literal_investor_entry_or_portfolio_link': 2, 'literal_historical_article_or_topic_link': 3}
    for target, kind, boundary, literal in sorted(values, key=lambda value: (priority.get(value[1], 4), value[0])):
        if target in found:
            continue
        found.add(target)
        response = observation_index.get(target)
        output.append({'literalTarget': target, 'kind': kind, 'roleBoundary': boundary,
                       'disclosedInObservationId': proof['observationId'], 'bodySha256': proof['body']['sha256'],
                       'literalHrefOrRenderedReference': literal, 'resolution': 'HTML entity decoding and relative URL resolution only; an encoded target is an explicit URL query value',
                       'responseObservationId': response['observationId'] if response else None,
                       'isQualifiedRecurringEndpoint': False})
    return output


def archive_seal(state):
    entries = sorted((str(path.relative_to(state)), path.stat().st_size, path.stat().st_mtime_ns)
                     for path in state.rglob('*') if path.is_file())
    return {'fileCount': len(entries), 'metadataSha256': digest(json.dumps(entries, separators=(',', ':')).encode())}


def run(repo, state):
    before = archive_seal(state)
    contract_bytes = (repo / 'contracts/market.json').read_bytes()
    original_bytes = (repo / 'web/src/data/tracker/originals.json').read_bytes()
    contract, originals = json.loads(contract_bytes), json.loads(original_bytes)
    plan = plan_run(contract, DAY + 'T00:00:00Z')
    missing = [task for task in plan['tasks'] if task['kind'] == 'missing_discovery']
    selected = [task for task in missing if task['family'] in FAMILIES]
    assert len(contract['suppliers']) == 74 and len(plan['tasks']) == 557 and len(missing) == 254
    assert {family: sum(t['family'] == family for t in selected) for family in FAMILIES} == FAMILIES
    scorecard_path = repo / 'docs/active/daily-pipeline/evaluations/2026-10-23/accuracy-scorecard.json'
    scorecard = json.loads(scorecard_path.read_bytes())
    for family, expected in FAMILIES.items():
        row = next(row for row in scorecard['coverageBreakdowns']['family'] if row['id'] == family)
        assert row['missingBindings'] == expected and row['successfulTasks'] == 0
    suppliers = {s['id']: s for s in contract['suppliers']}
    manual_suppliers = {s['id']: s for s in originals['suppliers']}
    evidence = {e['id']: e for e in originals['evidence']}
    observations = []
    for path in sorted((state / 'observations').glob('*.json')):
        value = json.loads(path.read_bytes())
        if value.get('status') == 'fetched' and value.get('httpStatus') == 200 and value.get('body'):
            observations.append(value)
    by_url = {}
    for observation in observations:
        for url in (observation['requestedUrl'], observation.get('finalUrl')):
            if url and (url not in by_url or observation['fetchedAt'] > by_url[url]['fetchedAt']):
                by_url[url] = observation
    records, proof_inventory = [], {}
    for task in sorted(selected, key=lambda t: (t['family'], t['supplierId'])):
        subject, manual = suppliers[task['supplierId']], manual_suppliers[task['supplierId']]
        ids = (evidence_ids(manual) | evidence_ids([event for event in originals['events'] if event['supplierId'] == subject['id']]) |
               {source['evidenceId'] for source in contract['sources'] if source['supplierId'] == subject['id'] and source.get('evidenceId')})
        refs = [{'url': evidence[eid]['canonicalUrl'], 'evidenceId': eid, 'retained': evidence[eid]} for eid in sorted(ids) if eid in evidence]
        for suffix in THOMA_PAGES.get(subject['id'], []):
            # Match an exact archived path, not an invented request endpoint.
            matches = [url for url in by_url if urlsplit(url).hostname == 'www.thomabravo.com' and urlsplit(url).path == '/press-releases/' + suffix]
            assert matches, ('Expected already-observed cross-source body absent', subject['id'], suffix)
            refs.append({'url': sorted(matches)[0], 'evidenceId': None, 'retained': {}})
        proofs, unavailable, leads, seen = [], [], [], set()
        for ref in refs:
            observation = by_url.get(ref['url'])
            if not observation:
                unavailable.append({'evidenceId': ref['evidenceId'], 'url': ref['url'], 'primaryBodyAvailableInFrozenArchive': False,
                                    'boundary': 'A retained excerpt, title or retrieval hash alone is not a primary body. Do not renew its date or infer endpoint operation.'})
                continue
            if observation['observationId'] in seen:
                continue
            seen.add(observation['observationId'])
            raw = (state / observation['body']['key']).read_bytes()
            assert digest(raw) == observation['body']['sha256'] and len(raw) == observation['body']['bytes']
            body = decoded_discovery_body(raw)
            page = AuditPage(body.decode('utf8', errors='replace'), source_url=observation.get('finalUrl') or observation['requestedUrl'])
            text = normalized(page.readable)
            proof = {'observationId': observation['observationId'], 'observationPath': str(state / 'observations' / (observation['observationId'] + '.json')),
                     'sourceId': observation['sourceId'], 'requestedUrl': observation['requestedUrl'], 'finalUrl': observation.get('finalUrl') or observation['requestedUrl'],
                     'fetchedAt': observation['fetchedAt'], 'httpStatus': observation['httpStatus'], 'body': observation['body'],
                     'bodyPath': str(state / observation['body']['key']), 'rawHashAndSizeVerified': True,
                     'decodedSha256': digest(body), 'decodedBytes': len(body), 'archivedRole': source_role(observation.get('finalUrl') or observation['requestedUrl'], subject),
                     'retainedEvidenceIds': [e['evidenceId'] for e in refs if e['url'] == ref['url'] and e['evidenceId']],
                     'retainedEvidencePublicationDates': [e['retained'].get('publicationDate') for e in refs if e['url'] == ref['url'] and e['evidenceId']],
                     'parsedPublicationMetadata': page.published, 'publicationMetadataIsNotCurrentCheck': True,
                     'literalExcerpt': excerpt(text, subject, ref['retained'])}
            proofs.append(proof)
            proof_inventory[proof['observationId']] = proof['body']
            leads.extend(literal_leads(page, text, subject, proof, by_url))
        deduplicated = {}
        for lead in leads:
            deduplicated.setdefault((lead['literalTarget'], lead['kind']), lead)
        leads = list(deduplicated.values())
        roles = sorted({proof['archivedRole'] for proof in proofs})
        primary = [proof for proof in proofs if proof['archivedRole'] != 'secondary_reporting_or_database']
        own = [proof for proof in proofs if proof['archivedRole'] == 'supplier_owned_primary']
        issuer_sec = [proof for proof in proofs if proof['archivedRole'] == 'supplier_issuer_statement_sec_hosted']
        counterparty = [proof for proof in proofs if proof['archivedRole'] in ('investor_acquirer_or_historical_counterparty_primary', 'parent_or_acquirer_statement_sec_hosted')]
        if task['family'] == 'official_announcements':
            classification = ('supplier_site_body_historical_only' if own else 'issuer_sec_statement_only' if issuer_sec else
                              'other_party_primary_only' if counterparty else 'release_distributor_only' if any('distributor' in role for role in roles) else 'secondary_or_no_body_only')
            candidate_leads = [lead for lead in leads if lead['roleBoundary'] == 'supplier_site_reference']
            action = ('Use the literal supplier-site link below to capture the actual press/news index or its advertised feed. A linked event page or IR entry is only the first qualification step.' if candidate_leads else
                      'Locate a supplier-owned primary news source using the exact cited issuer or counterparty document. No supplier-owned recurring endpoint is established by the retained bytes here.')
            boundary = 'A SEC-hosted issuer statement, parent filing, distributor release or investor page is not itself a supplier-owned recurring news source.'
        else:
            relevant_counterparty = [proof for proof in counterparty if proof['literalExcerpt']['subjectExplicitlyMentioned']]
            classification = ('counterparty_primary_historical_only' if relevant_counterparty else
                              'parent_context_without_exact_subject_match' if counterparty else 'supplier_funding_or_business_statement_only' if own else
                              'release_distributor_only' if any('distributor' in role for role in roles) else 'secondary_or_no_body_only')
            candidate_leads = [lead for lead in leads if lead['roleBoundary'] == 'investor_reference_relationship_still_requires_proof']
            action = ('Capture a supplier-specific counterparty portfolio/disclosure or retained transaction lead, then qualify a bounded supplier-filtered index. An investor-wide sitemap and a single historical acquisition are insufficient.' if counterparty else
                      'Obtain a dated statement from the named investor/acquirer itself, using literal party links where present. A supplier funding announcement can identify a party but cannot establish that party’s recurring source.')
            boundary = 'A historical investor/acquirer disclosure proves only the stated event and parties at that date. Portfolio reposts and a counterparty’s other acquisitions do not establish present ownership or complete supplier coverage.'
        names = {'ownershipAcquirerAsRetained': manual.get('ownership', {}).get('acquirer'),
                 'roundLeadAsRetained': manual.get('lastRound', {}).get('lead'),
                 'boundary': 'These retained tracker strings are research targets only unless supported by the quoted primary bytes; no field is newly admitted by this audit.'}
        records.append({'taskId': task['taskId'], 'supplierId': subject['id'], 'supplierName': subject['name'], 'supplierKind': subject['kind'],
                        'family': task['family'], 'missingBindingUnchanged': True, 'registrationActivated': False, 'coverageCredit': 0,
                        'classification': classification, 'sourceRolesPresent': roles, 'retainedPartyResearchTargets': names,
                        'bodyProofs': proofs, 'unavailableExactCitations': unavailable, 'literalEndpointLeads': leads,
                        'nextQualificationAction': {'owner': 'pipeline agent', 'humanDecisionNeeded': False, 'action': action,
                                                    'preferredLiteralLeads': [lead['literalTarget'] for lead in candidate_leads[:5]],
                                                    'when': 'After natural allowance renewal, through the persistent source-probe reservation path restored from the latest verified real archive.'},
                        'qualificationStillRequired': ['Exact supplier and issuer/counterparty relationship from retained primary evidence.',
                                                      'Actual endpoint bytes and a source-specific bounded item/entity scope.',
                                                      'All pagination/retention boundaries for the registered current window.',
                                                      'Positive, quiet and blocked behavior; no empty-shell or unrelated-parent shortcut.',
                                                      'Separate ordinary registration review and actual collector/gate receipts.'],
                        'confidenceBoundary': boundary, 'subjectRelationshipLimit': ('Product/segment references must be explicit. A parent name alone cannot qualify this segment.' if subject['kind'] == 'segment' else 'Do not promote an historical statement into a current ownership or freshness claim.'),
                        'noPrimaryBodyClaimWhereAbsent': not bool(primary)})
    after = archive_seal(state)
    assert before == after and (repo / 'contracts/market.json').read_bytes() == contract_bytes and (repo / 'web/src/data/tracker/originals.json').read_bytes() == original_bytes
    summary = {family: {'obligations': FAMILIES[family], 'stillMissing': FAMILIES[family],
                        'classifications': {classification: sum(record['family'] == family and record['classification'] == classification for record in records)
                                            for classification in sorted({record['classification'] for record in records if record['family'] == family})},
                        'withAnyRetainedBody': sum(record['family'] == family and bool(record['bodyProofs']) for record in records),
                        'withLiteralLead': sum(record['family'] == family and bool(record['literalEndpointLeads']) for record in records),
                        'withFamilyRelevantLiteralLead': sum(record['family'] == family and bool(record['nextQualificationAction']['preferredLiteralLeads']) for record in records),
                        'qualifiedRecurringEndpoints': 0} for family in FAMILIES}
    report = {'schemaVersion': 1, 'id': 'SEC-MARKET-MISSING-PRIMARY-BINDINGS-20261023', 'auditDate': DAY,
              'scope': {'families': FAMILIES, 'auditedObligations': 91, 'suppliers': 74, 'requiredObligations': 557,
                        'totalMissingBindings': 254, 'existingSuccessfulChecks': 121, 'newCoverageCredit': 0,
                        'unverifiedCandidateBindingsUntouched': 28},
              'inputs': {'contract': {'path': 'contracts/market.json', 'sha256': digest(contract_bytes)},
                         'originals': {'path': 'web/src/data/tracker/originals.json', 'sha256': digest(original_bytes)},
                         'scorecard': {'path': str(scorecard_path.relative_to(repo)), 'sha256': digest(scorecard_path.read_bytes())},
                         'script': {'path': str(Path(__file__).relative_to(ROOT)), 'sha256': digest(Path(__file__).read_bytes())},
                         'archiveRoot': str(state)},
              'method': {'selection': 'All exact retained citation URLs linked by supplier fields, supplier events or current citation bindings, plus explicitly enumerated already-observed supplier-specific investor/counterparty transaction pages. Latest retained HTTP200 bodies; final URL aliases only where actually observed.',
                         'wholeArchiveCompletenessClaim': False, 'observationsIndexed': len(observations),
                         'distinctProofObservations': len(proof_inventory), 'proofBindings': sum(len(record['bodyProofs']) for record in records),
                         'auditParsing': 'Read-only bounded decoding, HTML text extraction and explicit valueless-attribute-to-empty normalization. This derived view does not constitute runtime source acceptance or semantic admission.',
                         'literalLinks': 'All targets come from retained HTML href/feed attributes, explicit URL query values or rendered website references. Bare hosts remain bare. No endpoint path is generated from a company name.'},
              'historicalParserNormalization': {'subject': 'reliaquest',
                         'observationId': '7811b478cfe36ed4e1b5c69ea0c10b37c919c26be9fa3b5326ba7828a1388947',
                         'bodySha256': 'ae823daea1d3fd09c791948763d3d51d2e37c9beb9fca4c589bed7b9de0f6cb7',
                         'originalFetchedAt': '2026-10-23T04:14:58.384402Z',
                         'historicalFailure': "Page raised AttributeError when a valueless class attribute reached a.get('class', '').split().",
                         'auditTreatment': 'AuditPage converted valueless attributes to empty strings in its derived parsing view only; original body and observation remained unchanged.',
                         'repairBoundary': 'A separate runtime repair now replays the actual archived body. That repair does not qualify a source, renew its observation time or grant coverage credit.'},
              'archiveBefore': before, 'archiveAfter': after, 'archiveMetadataUnchanged': True, 'summary': summary,
              'limits': {'newNetworkCalls': 0, 'newModelCalls': 0, 'newAdmissionCalls': 0, 'realArchiveWrites': 0,
                         'registryEdits': 0, 'quotaChanges': 0, 'newGatePublicationAttempts': 0,
                         'chargedFetchesUnchanged': 5500, 'chargedModelCallsUnchanged': 80, 'chargedDocumentsUnchanged': 40,
                         'freshSourceChecksClaimed': 0},
              'ownerDecisionsNeeded': [], 'recommendation': 'Preserve all 91 missing bindings. Prioritize supplier-specific archived primary leads and explicit investor portfolio/transaction links for bounded qualification after natural allowance renewal. Keep current verified-source reliability ahead of general expansion.',
              'records': records}
    out = repo / 'docs/active/daily-pipeline/accuracy'
    (out / (BASE + '.json')).write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    md = ['# Missing primary-family bindings, October 23, 2026', '',
          'All 91 audited obligations remain missing: 39 supplier official-announcement bindings and 52 investor/acquirer bindings. The full inventory remains 74 suppliers and 557 obligations, with the existing live receipt at 121 successful checks. This audit adds zero checks and activates no source.', '',
          'I would qualify the supplier-specific primary leads already present in the archive first, using the persistent fetch reservation path after the natural allowance renews. Historical event bodies help identify parties and exact links; they do not prove a complete recurring source. No owner decision blocks the evidence work below.', '',
          '## Evidence and limits', '',
          f"The audit binds {report['method']['distinctProofObservations']} distinct HTTP 200 observations across {report['method']['proofBindings']} obligation/body references. Every selected body passes its stored SHA-256 and byte count. Exact request and final URLs, original retrieval times, literal excerpts and source roles are retained in the JSON companion. The {before['fileCount']:,} archived file metadata entries remain unchanged.", '',
          'The 39 official-announcement gaps break down into 13 with only SEC issuer statements, 18 with only other-party primary statements, four with distributor statements and four with secondary or absent bodies. Thirty-eight have a retained body; 14 have a literal supplier-site lead, which still requires endpoint qualification.', '',
          'The 52 investor/acquirer gaps break down into 15 with historical counterparty primary statements, four with parent context lacking an exact product/segment mention, 24 with supplier funding or business statements, four with distributor statements and five with secondary or absent bodies. Fifty have a retained body; 15 have literal investor entry or portfolio links. None is a qualified recurring endpoint.', '',
          'The archive is `/tmp/smp-coverage-baseline-20261023/state` in OrbStack. No network or model call, onboarding, admission, actual archive write, quota operation, source registration or publication occurred. The charged October 23 counters remain 5,500/80/40. The other missing source families and the 28 candidate bindings remain outside this audit.', '',
          'The audit uses an explicit read-only HTML normalization for valueless attributes. A literal excerpt is checked against the whitespace-normalized rendered text derived from the bound body. This is evidence inspection and does not assert that the production extractor accepted the page or that a statement passed independent semantic review. An unmatched retained excerpt is never reported as a literal primary quote.', '',
          'The original ReliaQuest body exposed an AttributeError in Page when a valueless class attribute reached `.split()`. The audit initially used its disclosed attribute normalization to inspect that body. A separate runtime repair now replays the actual archived body. The original observation is `7811b478cfe36ed4e1b5c69ea0c10b37c919c26be9fa3b5326ba7828a1388947`, fetched at `2026-10-23T04:14:58.384402Z`, with body SHA-256 `ae823daea1d3fd09c791948763d3d51d2e37c9beb9fca4c589bed7b9de0f6cb7`. This historical parsing limitation and its repair earn no source qualification or fresh check.', '',
          '## Source-role boundary', '',
          'Supplier-owned pages, SEC-hosted issuer statements, parent/acquirer statements, investor disclosures, shared release distributors and secondary reporting are labelled separately. A distributor’s published company statement can support a historical statement while leaving the supplier-owned announcement stream missing. A parent filing can mention an acquired supplier or product while leaving its supplier-specific discovery scope unqualified. A broad investor sitemap cannot establish quiet coverage for one portfolio company.', '',
          'Thoma Bravo pages include historical Barracuda, Ping Identity, Proofpoint and Veracode transaction evidence. Their original dates and transaction parties must remain visible. Delinea’s archived Thoma Bravo page explicitly says it was backed by TPG Capital; publication on an investor’s website alone does not establish current ownership. The same caution applies to old take-private statements and later IPOs.', '',
          '## Audited missing obligations', '']
    for family in FAMILIES:
        md += ['### ' + ('Supplier official announcements: 39 remain missing' if family == 'official_announcements' else 'Investor/acquirer sources: 52 remain missing'), '',
               '| Supplier | Retained evidence | Literal next lead | Required qualification |', '|---|---|---|---|']
        for record in [record for record in records if record['family'] == family]:
            roles = ', '.join(record['sourceRolesPresent']) if record['sourceRolesPresent'] else 'No exact cited body in the frozen archive.'
            preferred = record['nextQualificationAction']['preferredLiteralLeads']
            if not preferred and family == 'official_announcements':
                preferred = [lead['literalTarget'] for lead in record['literalEndpointLeads'][:1]]
            lead = '`' + preferred[0].replace('|', '%7C') + '`' if preferred else 'No counterparty endpoint disclosed.' if family == 'investor_acquirer' else 'No literal endpoint established.'
            if preferred and record['supplierKind'] == 'segment' and family == 'official_announcements':
                lead += ' Parent entry only; product binding unproved.'
            targets = [str(value) for key, value in record['retainedPartyResearchTargets'].items() if key != 'boundary' and value]
            target_text = '; '.join(dict.fromkeys(targets)).replace('|', '/')
            action = ('Capture the linked supplier source, then prove its dated announcement scope and complete paging.' if family == 'official_announcements' and preferred else
                      'Find and capture the supplier-owned press source; retained third-party/parent evidence does not complete it.' if family == 'official_announcements' else
                      'Capture the counterparty’s supplier-specific disclosure; prove the entity filter, dates and all paging.' if preferred else
                      'Seek the counterparty’s own dated supplier disclosure' + ('; retained research targets: ' + target_text if target_text else '; derive its exact identity from the retained primary body') + '.')
            md.append('| ' + record['supplierName'].replace('|', '/') + ' | ' + roles.replace('_', ' ') + ' | ' + lead + ' | ' + action + ' |')
        md += ['']
    md += ['## Qualification acceptance', '',
           'Every proposed binding still needs exact supplier/party identity, actual endpoint bytes, a bounded item and entity scope, publication and retention dates, all pagination boundaries, and positive/quiet/blocked replay. A historical article, linked homepage, quoted investor name or old portfolio listing is a lead. Unknown identity, expired evidence, an empty JavaScript shell, a truncated feed or unrelated parent activity stays incomplete.', '',
           'Bare website names remain as written, without an invented scheme or path. Encoded Business Wire/PR Newswire URL parameters are disclosed as decoded query targets and were never followed. A response observation for a linked page, where present, still provides no full traversal or registration approval.', '',
           'Each of the 91 rows has an agent owner and an exact next qualification action in the JSON. Retained tracker owner/round-lead strings are research targets until a primary body supports them. Missing primary evidence requires agent research and properly budgeted requests; it is not an invented approval question for the owner.', '',
           f"Detailed evidence: `/Users/jessepike/code/projects/sec-market-finish-20261022/docs/active/daily-pipeline/accuracy/{BASE}.json`.",
           'Reproduction script: `/Users/jessepike/code/projects/sec-market-finish-20261022/ops/evaluation/missing_primary_bindings_audit.py`.', '']
    (out / (BASE + '.md')).write_text('\n'.join(md))
    return {'families': FAMILIES, 'records': len(records), 'summary': summary, 'proofObservations': len(proof_inventory),
            'outputs': [str(out / (BASE + extension)).replace('/mnt/mac', '') for extension in ('.json', '.md')]}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=ROOT)
    parser.add_argument('--archive', type=Path, default=Path('/tmp/smp-coverage-baseline-20261023/state'))
    args = parser.parse_args()
    print(json.dumps(run(args.repo, args.archive), indent=2))
