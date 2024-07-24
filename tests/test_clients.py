from unittest import mock, TestCase

from httpx import HTTPStatusError, NetworkError, Request, Response, codes

from py_aws_core.clients import RetryClient
from py_aws_core.exceptions import APIException


class RetryClientTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.request = Request(url='', method='')  # Must add a non null request to avoid raising Runtime exception
        cls.mocked_sleep = mock.patch('time.sleep', return_value=None).start()

    @mock.patch.object(RetryClient, '_send_handling_auth')
    def test_ok(self, mock_send):
        mock_send.return_value = Response(
            request=self.request,
            status_code=codes.OK,
            text='ok'
        )
        with RetryClient() as h_client:
            h_client.get('http://example.com')
            self.assertEqual(mock_send.call_count, 1)

    @mock.patch.object(RetryClient, '_send_handling_auth')
    def test_retry(self, mock_send):
        mock_send.side_effect = NetworkError(message='')
        with self.assertRaises(NetworkError):
            with RetryClient() as h_client:
                h_client.get('https://example.com')
        self.assertEqual(mock_send.call_count, 4)

    @mock.patch.object(RetryClient, '_send_handling_auth')
    def test_raise_api_error(self, mock_send):
        response = Response(
            request=self.request,
            status_code=codes.NOT_FOUND,
        )
        mock_send.side_effect = HTTPStatusError(message='test_123', request=self.request, response=response)
        with self.assertRaises(APIException):
            with RetryClient() as h_client:
                h_client.get('https://example.com')
        self.assertEqual(mock_send.call_count, 1)