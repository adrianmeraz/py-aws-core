import json
from importlib.resources import as_file
from unittest import mock

from py_aws_core import db_session
from py_aws_core.db_dynamo import DDBClient
from py_aws_core.testing import BaseTestFixture
from tests import const as test_const


class DBSessionTests(BaseTestFixture):

    @mock.patch.object(DDBClient, 'get_item')
    def test_get_session_item(self, mocked_get_item):
        source = test_const.TEST_DB_RESOURCES_PATH.joinpath('db#get_session_item.json')
        with as_file(source) as get_session_item:
            session_json = json.loads(get_session_item.read_text(encoding='utf-8'))
            session_json['Item']['Base64Cookies']['B'] = self.to_utf8_bytes(session_json['Item']['Base64Cookies']['B'])
            mocked_get_item.return_value = session_json

        db_client = DDBClient()
        r_get_item = db_session.GetSessionItem.call(
            db_client=db_client,
            session_id='10c7676f77a34605b5ed76c210369c66'
        )
        self.assertEqual(len(r_get_item.session.Base64Cookies.value), 1241)
        self.assertEqual(mocked_get_item.call_count, 1)
