import json
import time
from importlib.resources import as_file
from unittest import mock

from py_aws_core import events
from py_aws_core.testing import BaseTestFixture


class DBEncoderTests(BaseTestFixture):
    def test_serialize_to_json(self):
        source = self.TEST_LAMBDA_RESOURCES_PATH.joinpath('event#api_gateway.json')
        with as_file(source) as event_json:
            mock_event = events.LambdaEvent(json.loads(event_json.read_text()))

        self.assertEqual("gzip, deflate, br", mock_event.headers["Accept-Encoding"])
        self.assertEqual("GET", mock_event.http_method)
        self.assertEqual("/get-travel-control-points", mock_event.path)
        self.assertEqual({'medium_transport_type': 'A'}, mock_event.query_string_parameters)
        self.assertIsNone(mock_event.body)
        self.assertEqual('owufix3875.execute-api.us-west-2.amazonaws.com', mock_event.request_context.domain_name)

    def test_multi_value_headers(self):
        source = self.TEST_LAMBDA_RESOURCES_PATH.joinpath('event#api_gateway.json')
        with as_file(source) as event_json:
            mock_event = events.LambdaEvent(json.loads(event_json.read_text()))

        multi_value_headers = mock_event.multi_value_headers
        self.assertEqual(
            'CfDJ8GcmGAmFYbdJgvkLq5_X6y4I3JNsdWDwMFwshaQcsrlqLZHWYA7yCFrr5H22IA4u-xXtksHExFYRhCe6tLTMekS-cnH_Ayh2DXQjU0118i_22okKT9t5_rVyRg-tFn-FT2yBjIPg0RpmUkvmvRO8wAo',
            multi_value_headers.cookies['travel#__RequestVerificationToken']
        )
        self.assertEqual(
            '668638a6-e262-4d07-a0d6-d200d88e3be2',
            multi_value_headers.cookies['session_id'],
        )
        self.assertEqual(multi_value_headers.accept, '*/*')
        self.assertEqual(multi_value_headers.accept_encoding, 'gzip, deflate, br')
        self.assertEqual(multi_value_headers.user_agent, 'PostmanRuntime/7.40.0')
        self.assertEqual(multi_value_headers.authorization, 'Bearer eyJraWQiOiJzNndrcytDXC84WGxNOVF2OHNYeVhGczNjV1VsOVFwVzZsdE9rMGt5R2dDVT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIzZTYyYzNjOC00OTcwLTRmYzctYTk5Ni04NjhkNGMxMzk3ZjYiLCJjdXN0b206cm9sZXMiOiJTVVBFUlVTRVIsTUVNQkVSLFNUQUZGIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy13ZXN0LTIuYW1hem9uYXdzLmNvbVwvdXMtd2VzdC0yX0N4VlFXNU1wVSIsImN1c3RvbTpncm91cCI6Indob2FkZXJlanIiLCJjb2duaXRvOnVzZXJuYW1lIjoiaGVsbG9tb3RvIiwib3JpZ2luX2p0aSI6ImFiMTNjM2NhLTEyYTMtNDJhNy05MTQzLTJhNDkwYmJmNjE2OCIsImF1ZCI6IjdtdWR1dGdiZGViY2g2YWVoMjF1ZXEyaDFtIiwiZXZlbnRfaWQiOiJmMjI5MWZkMC0xYTFkLTRkODktODU2OC04NmExYzUxMzJkNWYiLCJ0b2tlbl91c2UiOiJpZCIsImF1dGhfdGltZSI6MTcxNzcxNjIwMSwiZXhwIjoxNzE3NzE5ODAxLCJpYXQiOjE3MTc3MTYyMDEsImp0aSI6IjhlMDk2MmRjLWI5NzctNDc0Ni1iMGNjLTA5ZDJjZjEzZjczZiIsImVtYWlsIjoiYWRyaWFuQHJ5ZGVhcy5jb20ifQ.y09Ln6m44sJh_AYIoRgPokHg5WQfYu6eS9rgrcIIAHNMFIanTSJGgxua0W8ismFJvVWUBvxwVMVCxzdWZaBtSD1zDKWtPKizGKvayDQpAviGztKQICY_5k0pcG9Xg2zlM8_45FhRCYgZk8Fdu-vFvzRN47Bk7dFf1I9Bv50R3whsuEo2x4M0WwbKyJ6RXa7onVrGPuxComMTmXtZKvlHXHQus_VBWyy3gYDPKurumbRHf86OaGrlAcfC_SodSi7GqR8Q6glu7V3iKdJbvkAyuE-SJF7_5U_2VmuN-f-F9S7D1aJ1bO-6ZlfouJBZq9VWzW2Ve4Q3Cbc8w21tGotHUQ')

    @mock.patch.object(time, 'time')
    def test_cookies(self, mocked_time):
        mocked_time.return_value = 1062776008  # Fri, 05 Sep 2003 15:33:28 GMT

        source = self.TEST_LAMBDA_RESOURCES_PATH.joinpath('event#api_gateway.json')
        with as_file(source) as event_json:
            mock_event = events.LambdaEvent(json.loads(event_json.read_text()))

        cookie_header_1 = mock_event.generate_cookie_header(name='test_1', value='value_1', expires_in_seconds=43200)

        self.assertEqual(
            cookie_header_1,
            'test_1=value_1; Domain=owufix3875.execute-api.us-west-2.amazonaws.com; expires=Sat, 06 Sep 2003 03:33:28 GMT; Path=/; Secure'
        )

        cookie_1 = mock_event.get_cookie(cookie_name='session_id')
        self.assertEqual('668638a6-e262-4d07-a0d6-d200d88e3be2', cookie_1)

        self.assertEqual(1, mocked_time.call_count)
