import json
import os
import subprocess
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from auth_store import AuthStoreError
from bootstrap import check_request, GuardedRunner, device_challenge, safe_process_env, ModelUnavailable


class BootstrapTests(unittest.TestCase):
    def test_sign_in_again_replaces_only_an_existing_login_with_owner_approval(self):
        have = {"total_count": 1, "secrets": [{"name": "SMP_CODEX_AUTH_JSON"}]}
        none = {"total_count": 0, "secrets": []}
        again = {"operation": "sign_in_again", "ownerApproved": True, "approval": "owner 2026-11-13"}
        first = {"operation": "initialize_codex", "ownerApproved": True}
        self.assertEqual(check_request(again, have), "sign_in_again")
        self.assertEqual(check_request(first, none), "initialize_codex")
        for request, secrets, reason in [
            (first, have, "ACCOUNT_ALREADY_INITIALIZED_USE_PROBE_INSTEAD"),
            (again, none, "NO_LOGIN_TO_REPLACE_USE_INITIALIZE"),
            (dict(again, approval=""), have, "OWNER_APPROVAL_REFERENCE_REQUIRED"),
            (dict(again, ownerApproved=False), have, "EXPLICIT_INITIALIZATION_REQUEST_REQUIRED"),
        ]:
            with self.assertRaisesRegex(RuntimeError, reason):
                check_request(request, secrets)

    def test_only_official_device_url_and_a_standalone_code_are_exposed(self):
        self.assertEqual(device_challenge('Open https://auth.openai.com/codex/device\n\x1b[32mABCD-EFGHI\x1b[0m\n'),
                         {'url':'https://auth.openai.com/codex/device','code':'ABCD-EFGHI'})
        for raw in ['https://evil.invalid/device\nABCD-EFGHI\n','https://auth.openai.com/codex/device\nnot a code', 'https://auth.openai.com/codex/device\nBearer token ABCD-EFGHI']:
            self.assertIsNone(device_challenge(raw))

    def test_login_child_does_not_inherit_repository_or_api_credentials(self):
        with patch.dict(os.environ, {'SMP_AUTH_STORE_TOKEN':'fictional-writer','GH_TOKEN':'fictional-gh','OPENAI_API_KEY':'fictional-api','VERCEL_TOKEN':'fictional-vercel','CODEX_HOME':'/wrong/home'}):
            env=safe_process_env(home='/dedicated')
        for key in ['SMP_AUTH_STORE_TOKEN','GH_TOKEN','OPENAI_API_KEY','VERCEL_TOKEN']:
            self.assertNotIn(key,env)
        self.assertEqual(env['CODEX_HOME'],'/dedicated')

    def test_changed_auth_is_checkpointed_even_when_model_execution_times_out(self):
        checkpoints=[]
        def timeout(*_a,**_k):raise subprocess.TimeoutExpired('codex',90)
        guard=GuardedRunner(SimpleNamespace(checkpoint=lambda:checkpoints.append(True)),timeout)
        with self.assertRaises(subprocess.TimeoutExpired):guard(['codex','exec','-'])
        self.assertEqual(checkpoints,[True])

    def test_writeback_failure_discards_model_result_and_stops_further_work(self):
        def failed():raise AuthStoreError('do not log secret response')
        invoked=[]
        def client(*_a,**_k):
            invoked.append(True)
            return SimpleNamespace(stdout='',returncode=0)
        guard=GuardedRunner(SimpleNamespace(checkpoint=failed),client)
        with self.assertRaisesRegex(ModelUnavailable,'STOP_WORK'):guard(['codex','exec','-'])
        with self.assertRaisesRegex(ModelUnavailable,'STOP_WORK'):guard(['codex','exec','-'])
        self.assertEqual(len(invoked),1)

    def test_status_does_not_publish_unexercised_refresh_metadata(self):
        guard=GuardedRunner(SimpleNamespace(checkpoint=lambda:self.fail('Status must not write credentials')),
                            lambda *_a,**_k:SimpleNamespace(stdout='Logged in using ChatGPT',returncode=0))
        self.assertEqual(guard(['codex','login','status']).returncode,0)

    def test_only_context_identity_is_retained_from_model_transport(self):
        raw=json.dumps({'type':'thread.started','thread_id':'fictional-context'})+'\n'+json.dumps({'type':'other','tokens':'fictional-ignored'})
        guard=GuardedRunner(SimpleNamespace(checkpoint=lambda:None),lambda *_a,**_k:SimpleNamespace(stdout=raw,returncode=0))
        guard(['codex','exec','-'])
        self.assertEqual(guard.contexts,['fictional-context'])


if __name__=='__main__':unittest.main()
