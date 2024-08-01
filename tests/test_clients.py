from http.cookiejar import CookieJar
from unittest import mock

from httpx import HTTPStatusError, NetworkError, Request, Response, codes

from py_aws_core.clients import RetryClient
from py_aws_core.exceptions import APIException
from py_aws_core.testing import BaseTestFixture


class RetryClientTests(BaseTestFixture):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.request = Request(url='', method='')  # Must add a non null request to avoid raising Runtime exception
        cls.mocked_sleep = mock.patch('py_aws_core.utils.sleep', return_value=None).start()

    @mock.patch.object(RetryClient, '_send_handling_auth')
    def test_ok(self, mock_send):
        mock_send.return_value = Response(
            request=self.request,
            status_code=codes.OK,
            text='ok'
        )
        with RetryClient() as retry_client:
            retry_client.get('http://example.com')
            self.assertEqual(mock_send.call_count, 1)

    @mock.patch.object(RetryClient, '_send_handling_auth')
    def test_retryable_exception(self, mock_send):
        mock_send.side_effect = NetworkError(message='')
        with self.assertRaises(NetworkError):
            with RetryClient() as h_client:
                h_client.get('https://example.com')
        self.assertEqual(mock_send.call_count, 4)

    @mock.patch.object(RetryClient, '_send_handling_auth')
    def test_non_retryable_http_status_code(self, mock_send):
        response = Response(
            request=self.request,
            status_code=404,  # Non-retryable
        )
        mock_send.side_effect = HTTPStatusError(message='test_123', request=self.request, response=response)
        with self.assertRaises(APIException):
            with RetryClient() as h_client:
                h_client.get('https://example.com')
        self.assertEqual(mock_send.call_count, 1)

    def test_cookies(self):
        client = RetryClient()
        self.assertEqual(len(client.cookies), 0)

        # Now add cookies to cookie jar
        cookie_jar = CookieJar()
        cookie_1 = self.create_test_cookie(name='cookie_1', value='value_1')
        cookie_2 = self.create_test_cookie(name='cookie_2', value='value_2')

        cookie_jar.set_cookie(cookie_1)
        cookie_jar.set_cookie(cookie_2)

        # Add cookie jar to client
        client = RetryClient(cookies=cookie_jar)

        self.assertEqual(client.b64_encoded_cookies,
                         b'gASVjAEAAAAAAABdlCiMDmh0dHAuY29va2llamFylIwGQ29va2lllJOUKYGUfZQojAd2ZXJzaW9u\nlEsBjARuYW1llIwIY29va2llXzGUjAV2YWx1ZZSMB3ZhbHVlXzGUjARwb3J0lE6MDnBvcnRfc3Bl\nY2lmaWVklImMBmRvbWFpbpSMD3d3dy5leGFtcGxlLmNvbZSMEGRvbWFpbl9zcGVjaWZpZWSUiIwS\nZG9tYWluX2luaXRpYWxfZG90lImMBHBhdGiUjAEvlIwOcGF0aF9zcGVjaWZpZWSUiIwGc2VjdXJl\nlIiMB2V4cGlyZXOUTRAOjAdkaXNjYXJklImMB2NvbW1lbnSUTowLY29tbWVudF91cmyUTowHcmZj\nMjEwOZSJjAVfcmVzdJR9lHViaAMpgZR9lChoBksBaAeMCGNvb2tpZV8ylGgJjAd2YWx1ZV8ylGgL\nTmgMiWgNjA93d3cuZXhhbXBsZS5jb22UaA+IaBCJaBFoEmgTiGgUiGgVTRAOaBaJaBdOaBhOaBmJ\naBp9lHViZS4=\n')

        # Verifying cookies are wiped
        client = RetryClient()
        self.assertEqual(len(client.cookies), 0)

        # Verify no cookies results in empty cookie jar
        client.b64_decode_and_set_cookies(b'')
        self.assertEqual(len(client.cookies), 0)

        # Now rehydrate cookies from binary
        client.b64_decode_and_set_cookies(
            b'gASVjAEAAAAAAABdlCiMDmh0dHAuY29va2llamFylIwGQ29va2lllJOUKYGUfZQojAd2ZXJzaW9u\nlEsBjARuYW1llIwIY29va2llXzGUjAV2YWx1ZZSMB3ZhbHVlXzGUjARwb3J0lE6MDnBvcnRfc3Bl\nY2lmaWVklImMBmRvbWFpbpSMD3d3dy5leGFtcGxlLmNvbZSMEGRvbWFpbl9zcGVjaWZpZWSUiIwS\nZG9tYWluX2luaXRpYWxfZG90lImMBHBhdGiUjAEvlIwOcGF0aF9zcGVjaWZpZWSUiIwGc2VjdXJl\nlIiMB2V4cGlyZXOUTRAOjAdkaXNjYXJklImMB2NvbW1lbnSUTowLY29tbWVudF91cmyUTowHcmZj\nMjEwOZSJjAVfcmVzdJR9lHViaAMpgZR9lChoBksBaAeMCGNvb2tpZV8ylGgJjAd2YWx1ZV8ylGgL\nTmgMiWgNjA93d3cuZXhhbXBsZS5jb22UaA+IaBCJaBFoEmgTiGgUiGgVTRAOaBaJaBdOaBhOaBmJ\naBp9lHViZS4=\n')
        self.assertEqual(len(client.cookies), 2)

        # Verify attrs on rehydrated cookies
        r_cookies = client.cookies.jar._cookies['www.example.com']['/']
        r_cookie_1 = r_cookies['cookie_1']
        self.assertEqual(r_cookie_1.name, 'cookie_1')
        self.assertEqual(r_cookie_1.value, 'value_1')

        r_cookie_2 = r_cookies['cookie_2']
        self.assertEqual(r_cookie_2.name, 'cookie_2')
        self.assertEqual(r_cookie_2.value, 'value_2')
