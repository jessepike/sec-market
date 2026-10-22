"""Official app-server managed-auth refresh; no OAuth endpoint implementation."""
import json
import os
import selectors
import signal
import subprocess
import time

from bootstrap import safe_process_env


def refresh_account(keeper, popen=subprocess.Popen, timeout_seconds=75):
    process = popen(['codex', 'app-server', '--listen', 'stdio://'], stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                    env=safe_process_env(home=keeper.home), start_new_session=True)
    selector = selectors.DefaultSelector()
    selector.register(process.stdout, selectors.EVENT_READ)
    buffer = b''
    initialized = False
    def send(value):
        process.stdin.write((json.dumps(value) + '\n').encode())
        process.stdin.flush()
    try:
        send({'id': 1, 'method': 'initialize', 'params': {'clientInfo': {'name': 'smp_auth_acceptance', 'version': '1.0'},
                                                       'capabilities': {'experimentalApi': False}}})
        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            for key, _ in selector.select(timeout=min(0.2, timeout_seconds)):
                chunk = os.read(key.fileobj.fileno(), 65536)
                if not chunk:
                    raise RuntimeError('OFFICIAL_REFRESH_CLIENT_ENDED_EARLY')
                buffer += chunk
                if len(buffer) > 1_000_000:
                    raise RuntimeError('OFFICIAL_REFRESH_RESPONSE_EXCEEDS_BOUND')
                while b'\n' in buffer:
                    line, buffer = buffer.split(b'\n', 1)
                    try:
                        message = json.loads(line)
                    except ValueError:
                        continue
                    if message.get('id') == 1 and not initialized:
                        if 'error' in message:
                            raise RuntimeError('OFFICIAL_REFRESH_INITIALIZATION_FAILED')
                        initialized = True
                        send({'method': 'initialized', 'params': {}})
                        send({'id': 2, 'method': 'account/read', 'params': {'refreshToken': True}})
                    elif message.get('id') == 2:
                        if 'error' in message or (message.get('result', {}).get('account') or {}).get('type') != 'chatgpt':
                            raise RuntimeError('OFFICIAL_MANAGED_ACCOUNT_REFRESH_FAILED')
                        return {'officialClientRefreshRequested': True, 'managedAccountConfirmed': True}
        raise RuntimeError('OFFICIAL_REFRESH_CLIENT_TIMED_OUT')
    finally:
        selector.close()
        if process.poll() is None:
            os.killpg(process.pid, signal.SIGTERM)
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait(timeout=5)
        process.stdin.close()
        process.stdout.close()
        # Preserve any actual rotation, even when the RPC response failed.
        keeper.checkpoint()
