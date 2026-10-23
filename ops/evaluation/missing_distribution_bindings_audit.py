#!/usr/bin/env python3
"""Offline publisher leads only. Never fetches, admits, activates or edits archive state.

Run in OrbStack. Both output files must be new. Article and link findings cannot
establish a recurring source's supplier scope, pagination or retained completeness.
"""
import argparse
from collections import Counter
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import urljoin, urlsplit

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / 'web/scripts/pipeline'))
from contracts import digest, plan_run, require, utcnow
from corrections import validate_baseline
from discovery import decoded_discovery_body

FAMILIES = {'independent_reporting', 'release_distribution'}
WIRES = {'www.prnewswire.com', 'www.globenewswire.com', 'www.businesswire.com'}
EDITORIAL = {'siliconangle.com', 'www.securityweek.com', 'techcrunch.com', 'www.crn.com', 'www.bloomberg.com'}
THIRD_PARTY = EDITORIAL | WIRES | {'www.helpnetsecurity.com', 'tracxn.com', 'finance.yahoo.com', 'app.researchpool.com', 'en.wikipedia.org', 'www.returnonsecurity.com'}
WIRE_MARKER = re.compile(r'\(\s*(?:GLOBE\s+NEWSWIRE|BUSINESS\s+WIRE)\s*\)|/\s*PRNewswire\s*/', re.I)


class Markup(HTMLParser):
    """Diagnostic decoding only; this is not a replacement publication parser."""
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.text, self.links, self.skip, self.anchor = [], [], 0, None
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag in ('script', 'style', 'noscript', 'template'):
            self.skip += 1
        if self.skip:
            return
        if tag in ('a', 'link') and values.get('href'):
            link = {'literalHref': values['href'], 'tag': tag, 'rel': values.get('rel') or '',
                    'type': values.get('type') or '', 'rawTag': self.get_starttag_text(), 'text': ''}
            self.links.append(link)
            if tag == 'a':
                self.anchor = link

    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'noscript', 'template') and self.skip:
            self.skip -= 1
        if tag == 'a':
            self.anchor = None

    def handle_data(self, data):
        if not self.skip:
            self.text.append(data)
            if self.anchor is not None:
                self.anchor['text'] += data


def normalized(value):
    return re.sub(r'\s+', ' ', value).strip()


def contains(text, names):
    for name in names:
        if name and re.search(r'(?<!\w)' + re.escape(name) + r'(?!\w)', text, re.I):
            return name
    return None


def audit(repo, archive, prefix):
    repo, archive, prefix = Path(repo).resolve(), Path(archive).resolve(), Path(prefix).resolve()
    outputs = [Path(str(prefix) + extension) for extension in ('.json', '.md')]
    require(not any(path.exists() for path in outputs), 'Refusing to overwrite audit output')
    prior_name = 'docs/active/daily-pipeline/accuracy/correction-source-replay-2026-10-23.json'
    prior_raw = (repo / prior_name).read_bytes()
    prior = json.loads(prior_raw)
    manifest_raw = (archive / 'archive-manifest.json').read_bytes()
    require(digest(manifest_raw) == prior['archiveManifestSha256'], 'Frozen manifest pin differs')
    manifest = json.loads(manifest_raw)
    pins = {entry['key']: entry for entry in manifest['files']}
    require(len(pins) == len(manifest['files']), 'Duplicate frozen manifest path')
    verified = set()

    def raw(key):
        path = (archive / key).resolve()
        require(path.is_relative_to(archive), 'Archive path escapes root')
        body = path.read_bytes()
        pin = pins[key]
        require(digest(body) == pin['sha256'] and len(body) == pin['bytes'], 'Archived entry differs: ' + key)
        verified.add(key)
        return body

    def observation_ref(observation):
        key = 'state/observations/' + observation['observationId'] + '.json'
        require(json.loads(raw(key)) == observation, 'Observation metadata differs')
        return {key: observation.get(key) for key in ('observationId', 'sourceId', 'requestedUrl', 'finalUrl', 'status', 'fetchedAt', 'verifiedAt', 'httpStatus', 'errorCode', 'body')}

    checked_at = utcnow()
    market = json.loads((repo / 'contracts/market.json').read_bytes())
    originals = json.loads((repo / 'web/src/data/tracker/originals.json').read_bytes())
    requests = json.loads((repo / 'contracts/factual-corrections.json').read_bytes())
    baseline_raw = (repo / 'contracts/factual-baseline.json').read_bytes()
    require(digest(baseline_raw) == requests['baseline']['sha256'], 'Original baseline pin differs')
    validate_baseline(originals, json.loads(baseline_raw))
    plan = plan_run(market, checked_at)
    missing = [task for task in plan['tasks'] if task['kind'] == 'missing_discovery' and task.get('family') in FAMILIES]
    require(Counter(task['family'] for task in missing) == {'independent_reporting': 74, 'release_distribution': 67}, 'Missing141 denominator changed')
    require(len(plan['tasks']) == 557 and len(market['suppliers']) == 74, 'Whole inventory changed')
    sources = {source['id']: source for source in market['sources']}
    suppliers = {supplier['id']: supplier for supplier in market['suppliers']}
    raw_suppliers = {supplier['id']: supplier for supplier in originals['suppliers']}
    evidence = {record['id']: record for record in originals['evidence']}
    observations = [json.loads(raw(str(path.relative_to(archive)))) for path in sorted((archive / 'state/observations').glob('*.json'))]
    by_url, by_source = {}, {}
    for observation in observations:
        by_url.setdefault(observation.get('requestedUrl'), []).append(observation)
        by_source.setdefault(observation.get('sourceId'), []).append(observation)
    stories, leads, failures = [], [], []
    names = {sid: list(dict.fromkeys([supplier['name'], raw_suppliers[sid]['name'], *supplier['aliases']])) for sid, supplier in suppliers.items()}

    def snippet(text, match, label, before=70, after=180):
        start, end = max(0, match.start() - before), min(len(text), match.end() + after)
        return {'label': label, 'decodedStart': start, 'decodedEnd': end, 'text': text[start:end]}

    scanned = 0
    for source in market['sources']:
        if source['kind'] != 'citation' or urlsplit(source['url']).hostname in ('www.sec.gov', 'data.sec.gov'):
            continue
        matches = [o for o in by_source.get(source['id'], []) if o.get('requestedUrl') == source['url']]
        retained = [o for o in matches if o.get('status') in ('fetched', 'not_modified') and o.get('body')]
        if not retained:
            continue
        scanned += 1
        observation = max(retained, key=lambda o: o['fetchedAt'])
        latest = max(matches, key=lambda o: o['fetchedAt'])
        body = raw('state/' + observation['body']['key'])
        if body.startswith(b'%PDF-'):
            failures.append({'sourceId': source['id'], 'observation': observation_ref(observation), 'reason': 'Binary PDF not decoded for publisher HTML leads'})
            continue
        try:
            decoded_body = decoded_discovery_body(body)
            text_source = decoded_body.decode('utf8', errors='strict')
        except (ValueError, UnicodeError) as exc:
            failures.append({'sourceId': source['id'], 'observation': observation_ref(observation),
                             'reason': 'Archived body diagnostic decoding failed: ' + str(exc)[:150]})
            continue
        markup = Markup(text_source)
        text = normalized(' '.join(markup.text))
        sid = source['supplierId']
        matched_name = contains(text, names[sid])
        host = urlsplit(source['url']).hostname
        wire = WIRE_MARKER.search(text)
        paid = re.search(r'This is a paid press release\.', text, re.I)
        role = 'issuer_owned_material'
        markers = []
        if host == 'siliconangle.com' and re.search(r'by (?:Duncan Riley|Maria Deutscher)', text):
            role = 'named_editorial_story'
            markers.append(snippet(text, re.search(r'by (?:Duncan Riley|Maria Deutscher)', text), 'named article byline'))
        elif host == 'www.helpnetsecurity.com':
            role = 'industry_news_origin_not_independently_established'
            marker = re.search('Industry News', text)
            if marker:
                markers.append(snippet(text, marker, 'Industry News label; not proof of independent reporting'))
        elif host == 'tracxn.com':
            role = 'company_data_profile_not_editorial_reporting'
            marker = re.search(r"BigID.?s Funding Rounds", text)
            if marker:
                markers.append(snippet(text, marker, 'company funding database'))
        elif paid and wire:
            role = 'paid_issuer_release_syndicated_by_third_party'
            markers.append(snippet(text, paid, 'explicit paid release disclosure'))
        elif host in WIRES and (wire or re.search(r'News provided by|Source:', text, re.I)):
            role = 'release_distributor_story'
        elif wire:
            role = 'issuer_hosted_wire_release_copy'
        elif host in THIRD_PARTY:
            role = 'third_party_material_origin_unresolved'
        if wire:
            markers.append(snippet(text, wire, 'literal distribution dateline'))
        if matched_name:
            markers.append(snippet(text, re.search(re.escape(matched_name), text, re.I), 'literal declared supplier name'))
        current_evidence = next((record for record in evidence.values() if record['canonicalUrl'] == source['url']), None)
        proof_id = 'PUB-' + digest({'sourceId': source['id'], 'observationId': observation['observationId']})[:20]
        proof = {'proofId': proof_id, 'supplierId': sid, 'classification': role, 'supplierNameLiteral': matched_name,
                 'supplierSpecificBodySupport': bool(matched_name), 'evidenceIds': [record['id'] for record in evidence.values() if record['canonicalUrl'] == source['url']],
                 'declaredSourceClass': current_evidence.get('sourceClass') if current_evidence else None,
                 'originalEvidenceSha256': digest(current_evidence) if current_evidence else None,
                 'observation': observation_ref(observation), 'latestObservation': observation_ref(latest),
                 'decodedViewSha256': digest(decoded_body),
                 'fullDecodedChars': len(text), 'support': markers, 'recurringSourceQualified': False, 'sourceActivation': False}
        relevant_story = role != 'issuer_owned_material'
        if relevant_story:
            stories.append(proof)
        for link in markup.links:
            literal, resolved = link['literalHref'], urljoin(observation.get('finalUrl') or source['url'], link['literalHref'])
            parsed = urlsplit(resolved)
            if parsed.scheme not in ('https', 'http'):
                continue
            path, target_host = parsed.path.lower(), parsed.hostname
            own_story = resolved in (source['url'], observation.get('finalUrl'))
            named_link = bool(contains(normalized(link['text']), names[sid]))
            lead_type = None
            if link['tag'] == 'link' and 'alternate' in link['rel'].split() and any(kind in link['type'] for kind in ('rss', 'atom')):
                lead_type = 'comments_feed_excluded' if '/comments/' in path else 'literal_feed_link'
            elif re.search(r'/(rss|feed)(/|$)', path):
                lead_type = 'literal_rss_directory_or_feed'
            elif target_host in WIRES and ('/news/' in path or '/search/organization/' in path) and named_link:
                lead_type = 'literal_distributor_organization_index'
            elif host == 'siliconangle.com' and target_host == host and (path.rstrip('/') == '/category/security' or '/author/' in path and contains(link['text'], ['Duncan Riley', 'Maria Deutscher'])):
                lead_type = 'literal_editorial_category_or_author_index'
            elif host == 'www.helpnetsecurity.com' and target_host == host and path.rstrip('/') in ('/author/industrynews', '/tag/accenture'):
                lead_type = 'literal_industry_news_or_acquirer_index'
            elif target_host in WIRES and re.search(r'/(news-releases?/.*\.html$|news/home/\d+/)', path) and not own_story and (named_link or host not in WIRES and wire):
                lead_type = 'literal_distributor_story_link_only'
            if lead_type is None:
                continue
            # A company-owned RSS feed remains official-announcements evidence.
            # It cannot fill either of these two different publisher families.
            publisher_family = 'release_distribution' if target_host in WIRES else 'independent_reporting' if target_host in EDITORIAL else None
            if target_host == 'www.helpnetsecurity.com':
                publisher_family = 'independent_reporting_requires_origin_review'
            if publisher_family is None:
                lead_type = 'owned_or_unclassified_feed_wrong_family'
                if not relevant_story:
                    continue
            lead = {'supplierId': sid, 'sourceProofId': proof_id, 'sourceBody': observation['body'],
                    'sourceObservation': observation_ref(observation), 'literalHref': literal, 'resolvedUrl': resolved,
                    'literalMarkup': link['rawTag'], 'anchorText': normalized(link['text']), 'leadType': lead_type,
                    'proposedFamily': publisher_family, 'destinationResponseArchived': any(o.get('status') in ('fetched', 'not_modified') and o.get('body') for o in by_url.get(resolved, [])),
                    'supplierScopedCompletenessEstablished': False, 'recurringSourceQualified': False, 'newSourceCheck': False}
            require(link['rawTag'] in text_source, 'Lead markup not literal in archived HTML')
            if not relevant_story:
                lead['sourceBodyClassification'] = role
            leads.append(lead)

    # Immutable reference text is a lead only when no story bytes exist. It is
    # never a substitute for actual observation/body evidence or product scope.
    references = []
    for record in evidence.values():
        host = urlsplit(record['canonicalUrl']).hostname
        if record['sourceClass'] != 'INDEPENDENT' and host not in WIRES:
            continue
        attached = {source['supplierId'] for source in market['sources'] if source['kind'] == 'citation' and source['url'] == record['canonicalUrl']}
        if not attached:
            label = record['organization'] + ' ' + record['title']
            attached = {sid for sid in suppliers if contains(label, names[sid])}
        if not attached:
            continue
        observed = by_url.get(record['canonicalUrl'], [])
        retained = [o for o in observed if o.get('status') in ('fetched', 'not_modified') and o.get('body')]
        latest = max(observed, key=lambda o: o['fetchedAt']) if observed else None
        references.append({'evidenceId': record['id'], 'originalEvidenceSha256': digest(record), 'supplierIds': sorted(attached),
                           'association': 'Existing citation binding or exact immutable reference label; actual supplier body support is separately recorded.',
                           'url': record['canonicalUrl'], 'organization': record['organization'], 'declaredSourceClass': record['sourceClass'],
                           'retainedStoryAvailable': bool(retained), 'latestObservation': observation_ref(latest) if latest else None,
                           'recurringSourceQualified': False})

    # Dedupe identical literal anchors without inventing or simplifying URLs.
    leads = list({(lead['supplierId'], lead['resolvedUrl'], lead['sourceBody']['sha256'], lead['leadType']): lead for lead in reversed(leads)}.values())
    task_rows = []
    for task in sorted(missing, key=lambda task: (task['family'], task['supplierId'])):
        sid, family = task['supplierId'], task['family']
        material = [story for story in stories if story['supplierId'] == sid and story['supplierSpecificBodySupport']]
        if family == 'independent_reporting':
            matching = [story for story in material if story['classification'] == 'named_editorial_story']
            state = 'retained_named_editorial_story_only' if matching else 'retained_other_material_not_editorial_proof' if material else 'no_retained_editorial_story_binding'
        else:
            matching = [story for story in material if story['classification'] in ('release_distributor_story', 'paid_issuer_release_syndicated_by_third_party', 'issuer_hosted_wire_release_copy')]
            state = 'retained_release_or_wire_copy_only' if matching else 'no_retained_distributor_story_binding'
        reference_ids = [ref['evidenceId'] for ref in references if sid in ref['supplierIds']]
        relevant_leads = [index for index, lead in enumerate(leads) if lead['supplierId'] == sid and lead['proposedFamily'] == family]
        task_rows.append({'taskId': task['taskId'], 'supplierId': sid, 'supplierName': suppliers[sid]['name'], 'family': family,
                          'currentState': state, 'retainedMatchingStoryProofIds': [story['proofId'] for story in matching],
                          'otherRetainedMaterialProofIds': [story['proofId'] for story in material if story not in matching],
                          'staticEvidenceReferenceIds': reference_ids, 'literalLeadIndices': relevant_leads,
                          'recurringBindingQualified': False, 'newCoverageCredit': 0,
                          'nextAction': 'Qualify an exact supplier-scoped recurring publisher endpoint, origin and retained traversal in a future authorized fetch window; keep this task incomplete until then.'})
    require(len(task_rows) == 141 and len({row['taskId'] for row in task_rows}) == 141, 'Missing-task inventory differs')
    xage = next(story for story in stories if story['supplierId'] == 'xage' and story['classification'] == 'paid_issuer_release_syndicated_by_third_party')
    require(xage['declaredSourceClass'] == 'INDEPENDENT' and 'TR-xage-1' in xage['evidenceIds'], 'Expected Xage classification evidence differs')
    classification_defect = {'id': 'XAGE-SOURCE-CLASS-20261023', 'evidenceId': 'TR-xage-1', 'currentSourceClass': 'INDEPENDENT',
        'currentOrganization': evidence['TR-xage-1']['organization'], 'originalEvidenceSha256': digest(evidence['TR-xage-1']),
        'proofId': xage['proofId'], 'observation': xage['observation'], 'literalSupport': xage['support'],
        'finding': 'The retained body explicitly identifies a paid Xage issuer release syndicated by GlobeNewswire on Yahoo Finance. This is not independent editorial reporting.',
        'requiresDatedMetadataCorrection': True, 'separateFromFixed177SemanticAuditAndFiveDraftGroups': True,
        'proposedSourceClass': {'value': 'OFFICIAL', 'status': 'proposal pending proper attribution and policy review',
                               'basis': 'The enum already includes OFFICIAL and IR. Existing attributed issuer releases use both; no dedicated syndicated-release class exists. OFFICIAL is the proposed issuer-release label, not an automatic admitted change.',
                               'existingOfficialIssuerExamples': [{'evidenceId': eid, 'sourceClass': evidence[eid]['sourceClass'], 'url': evidence[eid]['canonicalUrl']} for eid in ('TR-nozomi-1', 'TR-nozomi-2', 'TR-delinea-5')]},
        'currentCorrectionPolicyLimit': 'The existing factual correction validator protects evidence sourceClass and organization. A separately reviewed dated metadata route or explicit policy extension is needed before publication. Do not edit originals or the five draft requests.',
        'validatorLocations': [
            {'path': 'web/scripts/pipeline/corrections.py', 'lines': [33, 143], 'rule': 'EVIDENCE_MUTABLE excludes sourceClass and organization; every other original evidence field must be identical.'},
            {'path': 'web/src/data/tracker/factualCorrections.ts', 'lines': [61, 302, 303], 'rule': 'evidenceChanges excludes sourceClass and organization; unchanged evidence properties must compare equal.'},
            {'path': 'web/scripts/pipeline/corrections.py', 'lines': [183], 'rule': 'load_policy accepts source evidence only when its immutable class is IR,FILING or OFFICIAL. TR-xage-1 remains INDEPENDENT today; a proposed correction cannot bypass this guard.'}],
        'minimalDatedCorrectionRecommendation': {
            'targetId': 'evidence:TR-xage-1', 'originalSha256': digest(evidence['TR-xage-1']),
            'allowedFieldChanges': {'sourceClass': {'before': 'INDEPENDENT', 'after': 'OFFICIAL'},
                'limitations': {'before': evidence['TR-xage-1']['limitations'],
                    'after': 'This is a paid Xage Security press release distributed by GlobeNewswire and republished by Yahoo Finance. Growth figures are company-reported; this source is not independent editorial reporting. The release does not disclose an absolute revenue figure.'}},
            'preserve': 'All other evidence fields, including organization, identity, canonical URL, excerpt and original retrieval metadata, remain exactly unchanged. The limitations clarify carrier versus issuer without rewriting original attribution.',
            'implementationBoundary': 'Propose a single-record, exact-before-hash exception for only this sourceClass transition, with ordinary whole-group source-byte binding and real independent review. Do not add sourceClass or organization to a general mutable-fields list. Preserve the primary-source guard generally; any exceptional paid-release proof admission must be equally confined to this exact record and retained body.',
            'reviewStatus': 'proposal only; not implemented or admitted', 'semanticAuditDenominator': 177,
            'existingFiveDraftGroupsChanged': False},
        'changed': False, 'admitted': False}
    inputs = ['contracts/market.json', 'contracts/factual-baseline.json', 'contracts/factual-corrections.json', 'web/src/data/tracker/originals.json', 'web/src/data/types.ts', 'web/src/data/tracker/factualCorrections.ts', 'web/scripts/pipeline/corrections.py', 'web/scripts/pipeline/discovery.py', 'web/scripts/pipeline/selection.py', 'web/scripts/pipeline/validation.py']
    result = {'kind': 'offline_missing_distribution_and_reporting_binding_audit', 'checkedAt': checked_at,
              'archiveCommit': prior['archiveCommit'], 'archiveManifestSha256': prior['archiveManifestSha256'],
              'archivePinSource': prior_name, 'archivePinSourceSha256': digest(prior_raw), 'verifiedArchiveEntries': len(verified),
              'inputs': {name: {'sha256': digest((repo / name).read_bytes()), 'bytes': (repo / name).stat().st_size} for name in inputs},
              'auditScriptSha256': digest(Path(__file__).read_bytes()),
              'scope': {'suppliers': 74, 'wholeRequiredInventory': 557, 'missingTaskCounts': dict(Counter(row['family'] for row in task_rows)),
                        'missingTaskCount': 141, 'retainedNonSecCitationBodiesExamined': scanned,
                        'newQualifiedBindings': 0, 'newCurrentSourceChecks': 0, 'coverageCredit': 0},
              'existingDistributionCandidatesOutsideMissing67': [source for source in market['sources'] if source['family'] == 'release_distribution'],
              'taskStateCounts': {family: dict(Counter(row['currentState'] for row in task_rows if row['family'] == family)) for family in sorted(FAMILIES)},
              'missingTasks': task_rows, 'retainedPublisherMaterial': stories, 'literalEndpointAndStoryLeads': leads,
              'immutablePublisherReferences': references, 'diagnosticDecodeLimits': failures,
              'additionalClassificationDefect': classification_defect,
              'qualificationActions': [
                  {'owner': 'Security Market Pulse source researcher', 'action': 'Start with retained named SiliconANGLE stories for Chainguard and Claroty. Qualify an exact recurring scope; the literal security category and author archives are broad leads, not supplier-complete feeds.'},
                  {'owner': 'Security Market Pulse source researcher', 'action': 'For Cyera, JFrog, Rapid7, Rubrik, Trend Micro and Xage, retain literal distributor datelines and any original-story links. Obtain real distributor organization/index/feed responses in the next authorized fetch window. Company-owned feeds stay official_announcements.'},
                  {'owner': 'Security Market Pulse source researcher', 'action': 'Inspect origin and publisher labels for Help Net Security Industry News, Tracxn profiles and syndicated material. Do not substitute them for independently authored editorial reporting.'},
                  {'owner': 'Security Market Pulse correction operator', 'action': 'Prepare a separate dated metadata correction proposal for TR-xage-1 with preserved Yahoo/GlobeNewswire/Xage attribution and a reviewed path for protected sourceClass changes. Keep the fixed177 semantic audit, five existing draft groups and all original records unchanged.'},
                  {'owner': 'Security Market Pulse source researcher', 'action': 'For blocked Bloomberg/ResearchPool and references with no retained body, keep the gap explicit and seek a public accessible alternative within the existing family. Do not bypass access controls or broaden subscriptions.'},
                  {'owner': 'Security Market Pulse implementation operator', 'action': 'A later qualified recurring binding must prove supplier selection, publication scope, pagination or terminal response and retained-window completeness, then replace exactly one missing-family task. Shared publisher homepages and story bytes cannot establish silence.'}],
              'ownerOnlyChoice': {'neededNow': False, 'reason': 'Public source qualification and a dated correction proposal remain agent-owned. No paid access, family waiver, new subscription or silent reclassification is proposed.'},
              'limits': ['Only exact retained observation/body bytes and literal HTML attributes support the findings. Reference labels without a body remain unverified leads.',
                         'Publisher material is classified by article byline, explicit paid/wire dateline or profile labels, not by a declared sourceClass alone.',
                         'A historical article, company profile, generic feed link or publisher homepage is not a complete qualified recurring source and proves no quiet outcome.',
                         'No parent or acquirer article is silently attributed to a product segment. Supplier body mentions use only declared names and aliases.',
                         'Seven existing release-distribution candidate bindings are outside the missing67 inventory and are not credited by this audit.'],
              'semanticAdmission': False, 'sourceActivation': False, 'contractChanged': False, 'originalsChanged': False,
              'modelCalls': 0, 'sourceRequests': 0, 'archiveWrites': 0, 'quotaChanges': False, 'productionChanged': False}
    result['auditSha256'] = digest(result)
    outputs[0].parent.mkdir(parents=True, exist_ok=True)
    with outputs[0].open('x') as out:
        out.write(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    states = result['taskStateCounts']
    markdown = f'''# Missing distribution and reporting bindings: offline audit

All 141 obligations remain open: 74 for independent reporting and 67 for release distribution. No recurring source was qualified and no current check or quiet outcome was credited. The full inventory remains 74 suppliers and 557 obligations.

Retained named SiliconANGLE stories provide editorial leads for Chainguard and Claroty. Their literal security-category and author links still need supplier scope and traversal checks. Help Net Security's Dragos item is labelled Industry News; its origin is not established as independent reporting. BigID's Tracxn material is a company data profile. Neither substitutes for a qualified editorial source.

The missing distribution tasks have retained issuer-release or wire-copy evidence for Cyera, JFrog, Rapid7, Rubrik, Trend Micro and Xage. Exact distributor datelines and literal story links are in the JSON. Company-owned RSS feeds retain their existing family; a generic wire homepage or an old story does not establish recurring completeness. The seven already registered PR Newswire/GlobeNewswire candidates are outside these missing 67 tasks.

## Additional metadata defect

`TR-xage-1` is currently labelled `INDEPENDENT`, with organization Yahoo Finance. Its archived body explicitly says “This is a paid press release” and identifies GlobeNewswire in the dateline. It is an issuer release carried by a third party, not independent editorial reporting. Observation `{xage['observation']['observationId']}` retains the original `{xage['observation']['fetchedAt']}` retrieval time and body SHA-256 `{xage['observation']['body']['sha256']}`.

Prepare a separate dated metadata correction proposal. `OFFICIAL` is a proposed existing label for attributed issuer releases; `IR` also appears on existing wire releases, so attribution needs review. The current correction policy protects `sourceClass` and organization. It needs a reviewed metadata route before this can change. This defect is separate from the fixed 177-record semantic audit and five existing draft correction groups. None was changed here.

The minimal proposal changes only `TR-xage-1.sourceClass` from `INDEPENDENT` to `OFFICIAL`, together with this limitations wording: “This is a paid Xage Security press release distributed by GlobeNewswire and republished by Yahoo Finance. Growth figures are company-reported; this source is not independent editorial reporting. The release does not disclose an absolute revenue figure.” Preserve organization, URL, identity, excerpt and original retrieval metadata. Bind any exception to the exact original record and retained source bytes, with a real independent review; do not weaken the general protected-fields rule.

Current guards are `web/scripts/pipeline/corrections.py:33` and `:143`, and `web/src/data/tracker/factualCorrections.ts:61` and `:302–303`. The backend primary-evidence class guard at `corrections.py:183` also rejects the current `INDEPENDENT` record. A proposal must address that exact case without opening other evidence classes generally.

## Bounded next work

The source researcher should qualify the retained SiliconANGLE leads, resolve actual distributor organization/index responses from the six issuer-release leads, and keep all blocked or missing-body references explicit. The operator should require supplier selection, retained history and pagination or a proved terminal response before replacing a missing-family task. Public alternatives can be investigated without expanding subscriptions.

No owner-only choice is needed now. No source, contract, original record, archive state, allowance or production data changed. The detailed JSON contains all 141 exact task IDs, source references, literal endpoint attributes, original observations and archive-manifest bindings.

Detailed evidence: [{outputs[0].name}]({outputs[0].name}).
'''
    with outputs[1].open('x') as out:
        out.write(markdown)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=REPO)
    parser.add_argument('--archive', type=Path, default=Path('/tmp/smp-coverage-baseline-20261023'))
    parser.add_argument('--output-prefix', type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.repo, args.archive, args.output_prefix)
    print(json.dumps({'auditSha256': result['auditSha256'], 'scope': result['scope'], 'taskStateCounts': result['taskStateCounts'],
                      'retainedPublisherMaterialCount': len(result['retainedPublisherMaterial']), 'literalLeadCount': len(result['literalEndpointAndStoryLeads'])}, indent=2))
