"""Replay the twelve actual archived Q4 attempts with authenticated original contexts."""
import pathlib, sys, json
helper = pathlib.Path(__file__).resolve().parents[2] / 'accuracy/receipts/three-source-current-2026-11-02/current_state_replay.py'
exec(compile(helper.read_text().split('base = ReadOnly()')[0], str(helper), 'exec'))
from retained_audit import original_discovery
store = ReadOnly()
results, excluded = [], []
with patch.object(pathlib.Path, 'read_bytes', tracked_read), patch.object(socket.socket, 'connect', deny), patch.object(socket, 'create_connection', deny), patch.object(LocalStore, '__init__', deny):
    index = AuditIndex(store)
    store._retained_audit_index = index
    for receipt, origin in index.receipts.values():
        if receipt['sourceId'] not in ('jfrog:official:1', 'rapid7:official:1') or not receipt.get('discoveryRecorded'):
            continue
        try:
            contract = original_contract(store, origin)
        except FileNotFoundError:
            excluded.append(origin)
            continue
        source = next(s for s in contract['sources'] if s['id'] == receipt['sourceId'])
        if source.get('kind') != 'q4_press_list':
            continue
        found = original_discovery({'origin': origin}, contract, source, store, require_complete=False)
        if not found['complete']:
            assert found['reason'] == receipt['errorCode']
        results.append({'sourceId':source['id'], 'receiptSha256':digest(receipt), 'completedAt':receipt['completedAt'], 'complete':found['complete'], 'items':len(found['items']), 'cause':found.get('reason')})
assert len(results) == 12, len(results)
assert sum(r['complete'] for r in results) == 8
after = seal()
assert before_seal == after
O.mkdir(parents=True, exist_ok=True)
(O/'historical-q4.json').write_text(json.dumps({'attemptsVerified':len(results),'results':results,'excludedMissingContracts':excluded,'networkDenied':True,'persistentStoreConstructionDenied':True,'archiveBeforeSha256':digest(before_seal),'archiveAfterSha256':digest(after),'readEntries':len(readset)},indent=2)+'\n')
print('Verified twelve actual Q4 attempts; eight positives and four preserved failures.')
