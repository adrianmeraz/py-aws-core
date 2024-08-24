import json
from importlib.resources import as_file
from unittest import mock, TestCase

from py_aws_core import db_session
from py_aws_core.db_dynamo import DDBClient
from tests import const as test_const


class DBSessionTests(TestCase):

    @mock.patch.object(DDBClient, 'query')
    def test_sessions(self, mocked_query):
        source = test_const.TEST_DB_RESOURCES_PATH.joinpath('db#query_sessions.json')
        with as_file(source) as query_sessions:
            _json = json.loads(query_sessions.read_text(encoding='utf-8'))
            session = _json['Items'][0]
            session['Base64Cookies']['B'] = bytes(session['Base64Cookies']['B'], 'utf-8')
            mocked_query.return_value = _json

        db_client = DDBClient()
        r_query = db_session.SessionDBAPI.GetSessionQuery.call(db_client=db_client, _id='10c7676f77a34605b5ed76c210369c66')
        self.assertEqual(len(r_query.session_b64_cookies), 1241)
        self.assertEqual(mocked_query.call_count, 1)
