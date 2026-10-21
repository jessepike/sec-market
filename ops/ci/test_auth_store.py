import json
import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from auth_store import AuthStore, AuthStoreError


def fictional_auth(refresh="fictional-refresh-one"):
    return json.dumps({"auth_mode": "chatgpt", "tokens": {"id_token": "fictional-id", "access_token": "fictional-access", "refresh_token": refresh}})


class AuthStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name) / "dedicated-account"

    def test_restore_is_private_and_unchanged_auth_makes_no_write(self):
        store = AuthStore(self.home, "fictional-secret-writer", runner=lambda *_a, **_k: self.fail("Unexpected secret write"))
        store.restore(fictional_auth())
        self.assertEqual(stat.S_IMODE(self.home.stat().st_mode), 0o700)
        self.assertEqual(stat.S_IMODE((self.home / "auth.json").stat().st_mode), 0o600)
        self.assertEqual(store.checkpoint(), {"saved": False, "reason": "unchanged"})
        with self.assertRaises(AuthStoreError): store.restore(fictional_auth())

    def test_rotated_auth_writes_latest_bytes_over_stdin_without_token_on_argv(self):
        calls = []
        def runner(args, **kwargs):
            calls.append((args, kwargs)); return SimpleNamespace(returncode=0)
        store = AuthStore(self.home, "fictional-secret-writer", runner)
        store.restore(fictional_auth())
        updated = fictional_auth("fictional-refreshed-two").encode()
        (self.home / "auth.json").write_bytes(updated)
        self.assertEqual(store.checkpoint(), {"saved": True})
        args, kwargs = calls[0]
        self.assertNotIn("fictional-secret-writer", " ".join(args))
        self.assertNotIn("fictional-refreshed-two", " ".join(args))
        self.assertEqual(kwargs["input"], updated)
        self.assertEqual(kwargs["env"]["GH_TOKEN"], "fictional-secret-writer")
        self.assertEqual(store.checkpoint(), {"saved": False, "reason": "unchanged"})

    def test_failed_persistence_does_not_acknowledge_or_revert_refreshed_auth(self):
        store = AuthStore(self.home, "fictional-secret-writer", lambda *_a, **_k: SimpleNamespace(returncode=1, stderr=b"do not expose raw client errors"))
        store.restore(fictional_auth())
        updated = fictional_auth("fictional-refreshed-two")
        (self.home / "auth.json").write_text(updated)
        previous = store.saved_sha
        with self.assertRaisesRegex(AuthStoreError, "stop model work"): store.checkpoint()
        self.assertEqual(store.saved_sha, previous)
        self.assertEqual((self.home / "auth.json").read_text(), updated)

    def test_api_and_host_integrated_auth_are_not_accepted_as_managed_account_auth(self):
        for value in [{"auth_mode": "apikey", "OPENAI_API_KEY": "fictional"}, {"auth_mode": "chatgptAuthTokens"}, {"auth_mode": "chatgpt", "tokens": {}}, []]:
            with self.assertRaises(AuthStoreError): AuthStore(self.home, "unused").restore(json.dumps(value))
        self.assertFalse(self.home.exists())

    def test_timeout_is_bounded_and_missing_writer_cannot_claim_persistence(self):
        def timeout(*_a, **_k): raise subprocess.TimeoutExpired("gh", 45)
        store = AuthStore(self.home, "fictional-secret-writer", timeout)
        store.restore(fictional_auth())
        (self.home / "auth.json").write_text(fictional_auth("fictional-refreshed-two"))
        with self.assertRaisesRegex(AuthStoreError, "stop model work"): store.checkpoint()
        store.token = ""
        with self.assertRaisesRegex(AuthStoreError, "secret-write permission"): store.checkpoint()

    def test_symlink_cannot_redirect_credential_storage(self):
        self.home.symlink_to(Path(self.temp.name), target_is_directory=True)
        with self.assertRaises(AuthStoreError): AuthStore(self.home, "unused").restore(fictional_auth())

    def test_repository_cannot_be_used_as_a_credential_directory(self):
        with self.assertRaisesRegex(AuthStoreError, "outside the repository"):
            AuthStore(Path(__file__).parent / "not-created-auth", "unused")


if __name__ == "__main__":
    unittest.main()
