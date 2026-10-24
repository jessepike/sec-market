"""Read-only actual-archive replay of unchanged corrections under D-112."""
import json
import os
from pathlib import Path
import sys

from replay_retained_audit import ROOT, MemoryStore, fingerprint
from artifacts import stage_files
from contracts import digest, require
from corrections import load_policy, process_corrections, project_bundle


def main():
    archive, manifest_sha = Path(sys.argv[1]).resolve(), sys.argv[2]
    before = fingerprint(archive)
    raw = (archive / 'archive-manifest.json').read_bytes()
    require(digest(raw) == manifest_sha, 'Archive manifest differs')
    manifest = json.loads(raw)
    for entry in manifest['files']:
        body = (archive / entry['key']).read_bytes()
        require(digest(body) == entry['sha256'] and len(body) == entry['bytes'], 'Archive bytes differ')
    store = MemoryStore(archive / 'state')
    production = store.read('heads/production.json')
    release = store.read('releases/' + production['releaseId'] + '.json')
    files = stage_files(store, release['manifest']['artifact'], release['acknowledgement'])
    previous = json.loads(files['static/factual-corrections.json'])
    market = json.loads((ROOT / 'contracts/market.json').read_bytes())
    context = load_policy(ROOT, market)
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
            raise RuntimeError('Offline correction migration denied ' + event)

    sys.addaudithook(guard)

    class NoModel:
        def __getattr__(self, name):
            raise AssertionError('No model work is permitted')

    def no_reservation(*args, **kwargs):
        raise AssertionError('No reservation is permitted')

    simulated = '2026-10-25T06:23:00Z'
    outcome = process_corrections(ROOT, store, market, NoModel(), no_reservation, simulated)
    require(not outcome['pending'] and not outcome['attempts'] and len(outcome['admitted']) == 6,
            'Original accepted corrections did not replay without new work')
    projected = project_bundle(ROOT, store, market, outcome, previous_bundle=previous, publication_at=simulated)
    require(projected['groups'] == previous['groups'], 'Original correction rows or dates changed')
    require(projected['policySha256'] == context['policySha256'] != previous['policySha256'],
            'Prospective global policy migration differs')
    require(store.mutations == 0 and not denied, 'Read-only replay performed external work')
    after = fingerprint(archive)
    require(before == after, 'Archive content or timestamps changed')
    print(json.dumps({'kind': 'offline_correction_policy_migration', 'mechanicsOnlyNonAdmitting': True,
                      'archiveManifestSha256': manifest_sha, 'archiveFiles': len(manifest['files']),
                      'releaseId': production['releaseId'], 'originalPolicySha256': previous['policySha256'],
                      'prospectivePolicySha256': projected['policySha256'], 'simulatedPublicationAt': simulated,
                      'unchangedGroups': len(projected['groups']),
                      'unchangedTargetCount': sum(len(group['targets']) for group in projected['groups']),
                      'originalGroupDates': {group['id']: group['date'] for group in projected['groups']},
                      'originalRowsAndAdmissionsUnchanged': True, 'archiveSealBefore': before,
                      'archiveSealAfter': after, 'modelCalls': 0, 'sourceRequests': 0, 'reservations': 0,
                      'stateWrites': store.mutations, 'publicationAttempts': 0,
                      'limitations': ['A simulated later publication time exercises retention; this is not a new release or live observation.']}, indent=2))


if __name__ == '__main__':
    main()
