"""Additive roster transition (D-138, SEC-083).

The authority chain (H to J, see q4_qualification_origin) pins exact contract
bytes. A roster change adds suppliers and sources without touching anything J
already contains, so this module proves the current contract is exactly J plus
the reviewed additions in contracts/roster-transition.json, and hands the
qualification and seeding authorities J itself. Every addition is reversible by
inversion: removing the listed rows must give back J byte for byte.
"""
import copy
import json
from pathlib import Path

from contracts import digest, require

BASE_SHA256 = '47b9f22636f0e6ea79cf830ae90aab844d8f554d44110a5bb08f29f00266593a'
KIND = 'additive_roster_transition'
TRANSITION = Path(__file__).resolve().parents[3] / 'contracts/roster-transition.json'


def load_transition(path=TRANSITION):
    path = Path(path)
    if not path.exists():
        return None
    value = json.loads(path.read_bytes())
    require(type(value) is dict and set(value) == {'schemaVersion', 'kind', 'baseContractSha256',
                                                  'activatedContractSha256', 'addedSuppliers', 'addedSources',
                                                  'appendedSourceIds'} and
            value['schemaVersion'] == 1 and value['kind'] == KIND and value['baseContractSha256'] == BASE_SHA256,
            'ROSTER_TRANSITION_SHAPE_DIFFERS')
    require(all(type(value[k]) is list and all(type(x) is str for x in value[k]) and len(set(value[k])) == len(value[k])
                for k in ('addedSuppliers', 'addedSources')), 'ROSTER_TRANSITION_LISTS_INVALID')
    require(type(value['appendedSourceIds']) is dict and all(
        type(ids) is list and ids and all(type(i) is str for i in ids) for ids in value['appendedSourceIds'].values()),
        'ROSTER_TRANSITION_APPENDS_INVALID')
    return value


def invert(contract, transition):
    """Remove exactly the declared additions and return the base contract."""
    added_suppliers, added_sources = set(transition['addedSuppliers']), set(transition['addedSources'])
    appended = transition['appendedSourceIds']
    base = copy.deepcopy(contract)
    present_suppliers = {s['id'] for s in contract['suppliers']}
    present_sources = {s['id'] for s in contract['sources']}
    require(added_suppliers <= present_suppliers and added_sources <= present_sources,
            'ROSTER_TRANSITION_ADDITION_MISSING')
    require(not set(appended) & added_suppliers and set(appended) <= present_suppliers,
            'ROSTER_TRANSITION_APPEND_TARGET_INVALID')
    for supplier_id, ids in appended.items():
        require(set(ids) <= added_sources, 'ROSTER_TRANSITION_APPEND_NOT_ADDED')
    base['suppliers'] = [s for s in base['suppliers'] if s['id'] not in added_suppliers]
    base['sources'] = [s for s in base['sources'] if s['id'] not in added_sources]
    for supplier in base['suppliers']:
        ids = appended.get(supplier['id'])
        if ids:
            require(supplier['sourceIds'][-len(ids):] == ids, 'ROSTER_TRANSITION_APPEND_ORDER_DIFFERS')
            supplier['sourceIds'] = supplier['sourceIds'][:-len(ids)]
    for source in contract['sources']:
        if source['id'] in added_sources:
            owner = source['supplierId']
            require(owner in added_suppliers or source['id'] in appended.get(owner, []),
                    'ROSTER_TRANSITION_SOURCE_OWNER_UNDECLARED')
    return base


def is_roster_successor(contract, transition=None):
    transition = transition if transition is not None else load_transition()
    return bool(transition) and digest(contract) == transition['activatedContractSha256']


def base_contract(contract, transition=None):
    """J for J or for its declared additive successor; anything else is refused."""
    if digest(contract) == BASE_SHA256:
        return contract
    transition = transition if transition is not None else load_transition()
    require(transition is not None and digest(contract) == transition['activatedContractSha256'],
            'ROSTER_TRANSITION_NOT_AUTHORIZED')
    base = invert(contract, transition)
    require(digest(base) == BASE_SHA256, 'ROSTER_TRANSITION_INVERSE_DIFFERS')
    return base


def authority_contract(contract):
    """The contract qualification authorities judge: J when this is J's roster successor, else unchanged."""
    transition = load_transition()
    if transition and digest(contract) == transition['activatedContractSha256']:
        return base_contract(contract, transition)
    return contract
