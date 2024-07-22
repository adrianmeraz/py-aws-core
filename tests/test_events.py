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
        self.assertEqual(mock_event.httpMethod, "GET")
        self.assertEqual(mock_event.path, "/get-travel-control-points")
        self.assertEqual(mock_event.queryStringParameters, {'medium_transport_type': 'A'})
        self.assertIsNone(mock_event.body)
        self.assertEqual(mock_event.requestContext.domainName, 'owufix3875.execute-api.us-west-2.amazonaws.com')
