import json
from importlib.resources import as_file
from unittest import mock, TestCase

from py_aws_core import services
from py_aws_core.clients import RetryClient
from py_aws_core.db_dynamo import DDBClient
from tests import const as test_const


class ServiceTests(TestCase):
    @mock.patch.object(DDBClient, 'query')
    def test_rehydrate_session_from_database(
        self,
        mocked_query
    ):
        source = test_const.TEST_DB_RESOURCES_PATH.joinpath('db#query_sessions.json')
        with as_file(source) as query_sessions:
            _json = json.loads(query_sessions.read_text(encoding='utf-8'))
            session = _json['Items'][0]
            session['Base64Cookies']['B'] = bytes(session['Base64Cookies']['B'], 'utf-8')
            mocked_query.return_value = _json

        with RetryClient() as client:
            services.rehydrate_session_from_database(client)
            self.assertEqual(len(client.b64_encoded_cookies), 1241)

        self.assertEqual(mocked_query.call_count, 1)

    @mock.patch.object(DDBClient, 'batch_write_item_maps')
    def test_write_session_to_database(
        self,
        mocked_batch_write_item_maps
    ):
        mocked_batch_write_item_maps.return_value = 1

        with RetryClient() as client:
            services.write_session_to_database(client)

        self.assertEqual(mocked_batch_write_item_maps.call_count, 1)
