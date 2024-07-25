import json
from importlib.resources import as_file
from unittest import TestCase

from py_aws_core import events
from tests import const as test_const


class DBEncoderTests(TestCase):
    def test_serialize_to_json(self):
        source = test_const.TEST_LAMBDA_RESOURCES_PATH.joinpath('event#api_gateway.json')
        with as_file(source) as event_json:
            mock_event = events.LambdaEvent(json.loads(event_json.read_text()))

        self.assertEqual(mock_event.headers["Accept-Encoding"], "gzip, deflate, br")
        self.assertEqual(mock_event.http_method, "GET")
        self.assertEqual(mock_event.path, "/get-travel-control-points")
        self.assertEqual(mock_event.query_string_parameters, {'medium_transport_type': 'A'})
        self.assertIsNone(mock_event.body)
        self.assertEqual(mock_event.request_context.domain_name, 'owufix3875.execute-api.us-west-2.amazonaws.com')

    def test_multi_value_headers(self):
        source = test_const.TEST_LAMBDA_RESOURCES_PATH.joinpath('event#api_gateway.json')
        with as_file(source) as event_json:
            mock_event = events.LambdaEvent(json.loads(event_json.read_text()))

        multi_value_headers = mock_event.multi_value_headers
        self.assertListEqual(
            multi_value_headers._cookies, ["__RequestVerificationToken=CfDJ8F_vZ7pnDCpAgEGmL1mJITKFEG29yE4jfeVaiNJqv-D6H-SWxLYSAtUxaCbNko-ykz0vEQdTDCvFYWvjYuaEFuoHYU1LUzF2eTkInqLzANdGhtQTtqlHFWC_0YQrWYp2Ac_t4qU8YgvHQKTLoULBXgg"]
        )
        self.assertEqual(multi_value_headers.accept, '*/*')
        self.assertEqual(multi_value_headers.accept_encoding, 'gzip, deflate, br')
        self.assertEqual(multi_value_headers.user_agent, 'PostmanRuntime/7.40.0')
        self.assertEqual(multi_value_headers._authorization, 'Bearer eyJraWQiOiJzNndrcytDXC84WGxNOVF2OHNYeVhGczNjV1VsOVFwVzZsdE9rMGt5R2dDVT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIzZTYyYzNjOC00OTcwLTRmYzctYTk5Ni04NjhkNGMxMzk3ZjYiLCJjdXN0b206cm9sZXMiOiJTVVBFUlVTRVIsTUVNQkVSLFNUQUZGIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy13ZXN0LTIuYW1hem9uYXdzLmNvbVwvdXMtd2VzdC0yX0N4VlFXNU1wVSIsImN1c3RvbTpncm91cCI6Indob2FkZXJlanIiLCJjb2duaXRvOnVzZXJuYW1lIjoiaGVsbG9tb3RvIiwib3JpZ2luX2p0aSI6ImFiMTNjM2NhLTEyYTMtNDJhNy05MTQzLTJhNDkwYmJmNjE2OCIsImF1ZCI6IjdtdWR1dGdiZGViY2g2YWVoMjF1ZXEyaDFtIiwiZXZlbnRfaWQiOiJmMjI5MWZkMC0xYTFkLTRkODktODU2OC04NmExYzUxMzJkNWYiLCJ0b2tlbl91c2UiOiJpZCIsImF1dGhfdGltZSI6MTcxNzcxNjIwMSwiZXhwIjoxNzE3NzE5ODAxLCJpYXQiOjE3MTc3MTYyMDEsImp0aSI6IjhlMDk2MmRjLWI5NzctNDc0Ni1iMGNjLTA5ZDJjZjEzZjczZiIsImVtYWlsIjoiYWRyaWFuQHJ5ZGVhcy5jb20ifQ.y09Ln6m44sJh_AYIoRgPokHg5WQfYu6eS9rgrcIIAHNMFIanTSJGgxua0W8ismFJvVWUBvxwVMVCxzdWZaBtSD1zDKWtPKizGKvayDQpAviGztKQICY_5k0pcG9Xg2zlM8_45FhRCYgZk8Fdu-vFvzRN47Bk7dFf1I9Bv50R3whsuEo2x4M0WwbKyJ6RXa7onVrGPuxComMTmXtZKvlHXHQus_VBWyy3gYDPKurumbRHf86OaGrlAcfC_SodSi7GqR8Q6glu7V3iKdJbvkAyuE-SJF7_5U_2VmuN-f-F9S7D1aJ1bO-6ZlfouJBZq9VWzW2Ve4Q3Cbc8w21tGotHUQ')
