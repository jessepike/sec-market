import io
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from vercel import VercelAdapter

from publisher_stage import verify_files


class Response(io.BytesIO):
    status = 200
    def __init__(self, body, url):
        super().__init__(body)
        self.url = url


class PublisherBytesTests(unittest.TestCase):
    def adapter(self, commands):
        def runner(args, **_kwargs):
            commands.append(args)
            return SimpleNamespace(returncode=0, stdout='https://exact.vercel.app', stderr='')
        return VercelAdapter(SimpleNamespace(read=lambda _key: {'releaseId': 'old'}),
                             'prj_123', 'team_123', 'pikeholdings', runner=runner)

    def manifest(self):
        return {'releaseId': 'r', 'appRevision': 'a'*40, 'snapshot': {'sha256': 's'},
                'artifact': {'sha256': 'a'}, 'contractSha256': 'c'}

    def test_normal_release_stages_production_target_without_domain_assignment(self):
        commands = []
        adapter = self.adapter(commands)
        with patch('vercel.stage_files', return_value={'static/index.html': b'exact'}):
            adapter.stage(self.manifest())
        self.assertIn('--prebuilt', commands[0])
        self.assertIn('--target=production', commands[0])
        self.assertIn('--skip-domain', commands[0])
        self.assertNotIn('--prod', commands[0])

    def test_smoke_payload_stays_preview(self):
        commands = []
        manifest = {**self.manifest(), 'mode': 'stage_only_smoke_test'}
        with patch('vercel.stage_files', return_value={'static/index.html': b'exact'}):
            self.adapter(commands).stage(manifest)
        self.assertNotIn('--target=production', commands[0])
        self.assertNotIn('--skip-domain', commands[0])

    def test_previous_served_deployment_uses_instant_rollback(self):
        commands = []
        self.adapter(commands).rollback('https://old.vercel.app')
        self.assertEqual(commands[0][1:4], ['rollback', 'https://old.vercel.app', '--yes'])

    def test_normal_probe_verifies_actual_static_bytes(self):
        adapter = self.adapter([])
        adapter.pending_files = {'static/index.html': b'exact'}
        with patch('vercel.urllib.request.urlopen', side_effect=lambda req, **_kw: Response(b'wrong', req.full_url)):
            with self.assertRaisesRegex(ValueError, 'DEPLOYED_STATIC_FILE_BYTES_DIFFER'):
                adapter.verify_static_files('https://exact.vercel.app')

    def test_every_static_file_including_detached_receipt_must_match_exact_bytes(self):
        files = {'config.json': b'{"version":3}', 'static/index.html': b'<html>Test</html>',
                 'static/deployment-receipt.json': b'{"ready":true}', 'static/file name.json': b'{}'}
        paths = []
        def opener(request, **_kwargs):
            paths.append(request.full_url)
            from urllib.parse import unquote
            path = unquote(request.full_url.removeprefix('https://fictional.vercel.app/'))
            return Response(files['static/' + path], request.full_url)
        result = verify_files('https://fictional.vercel.app', files, opener)
        self.assertEqual(len(result), 3)
        self.assertIn('https://fictional.vercel.app/file%20name.json', paths)

    def test_preview_html_injection_or_extra_bytes_fail_closed(self):
        files = {'static/index.html': b'<html>Exact</html>'}
        for body in [b'<html>Other</html>', files['static/index.html'] + b'<script>toolbar</script>']:
            with self.subTest(body=body), self.assertRaisesRegex(ValueError, 'STAGED_FILE_BYTES_DIFFER'):
                verify_files('https://fictional.vercel.app', files,
                             lambda req, **_kwargs: Response(body, req.full_url))

    def test_redirects_fail_even_when_body_matches(self):
        with self.assertRaisesRegex(ValueError, 'STAGED_FILE_REDIRECT_OR_HTTP_FAILURE'):
            verify_files('https://fictional.vercel.app', {'static/index.html': b'exact'},
                         lambda req, **_kwargs: Response(b'exact', 'https://other.vercel.app/index.html'))


if __name__ == '__main__':
    unittest.main()
