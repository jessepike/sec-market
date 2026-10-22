import io
import unittest

from publisher_stage import verify_files


class Response(io.BytesIO):
    status = 200
    def __init__(self, body, url):
        super().__init__(body)
        self.url = url


class PublisherBytesTests(unittest.TestCase):
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
