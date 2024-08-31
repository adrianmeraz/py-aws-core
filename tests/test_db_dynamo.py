import datetime
import json
from importlib.resources import as_file
from unittest import mock, TestCase

from py_aws_core import const, db_dynamo, utils
from py_aws_core.db_dynamo import DDBClient, GetItemResponse, ABCCommonAPI
from tests import const as test_const


class ABCCommonAPITests(TestCase):
    @mock.patch.object(utils, 'get_now_datetime')
    def test_calc_expire_at_timestamp(self, mocked_get_now_datetime):
        dt = datetime.datetime(year=2003, month=9, day=5, hour=15, minute=33, second=28, tzinfo=datetime.timezone.utc)
        mocked_get_now_datetime.return_value = dt
        val = db_dynamo.ABCCommonAPI.calc_expire_at_timestamp(expire_in_seconds=1*const.SECONDS_IN_DAY)
        self.assertEqual(val, 1062862408)

        val = db_dynamo.ABCCommonAPI.calc_expire_at_timestamp(expire_in_seconds=180*const.SECONDS_IN_DAY)
        self.assertEqual(val, 1078328008)

        val = db_dynamo.ABCCommonAPI.calc_expire_at_timestamp(expire_in_seconds=None)
        self.assertEqual(val, '')

    @mock.patch.object(DDBClient, 'query')
    def test_sessions(self, mocked_query):
        source = test_const.TEST_DB_RESOURCES_PATH.joinpath('db#query_sessions.json')
        with as_file(source) as query_sessions:
            _json = json.loads(query_sessions.read_text(encoding='utf-8'))
            session = _json['Items'][0]
            session['Base64Cookies']['B'] = bytes(session['Base64Cookies']['B'], 'utf-8')
            mocked_query.return_value = _json

    @mock.patch.object(DDBClient, 'get_item')
    def test_get_item_empty(self, mocked_get_item):
        source = test_const.TEST_DB_RESOURCES_PATH.joinpath('db#get_item#empty.json')
        with as_file(source) as get_item:
            _json = json.loads(get_item.read_text(encoding='utf-8'))
            mocked_get_item.return_value = _json
            val = GetItemResponse(_json)

        self.assertIsNone(val.item)

    @mock.patch.object(utils, 'get_now_datetime')
    def test_get_put_item_map(self, mocked_get_now_datetime):
        dt = datetime.datetime(year=2003, month=9, day=5, hour=15, minute=33, second=28, tzinfo=datetime.timezone.utc)
        mocked_get_now_datetime.return_value = dt

        pk = sk = 'TEST_ABC#999777555'
        val = ABCCommonAPI.get_put_item_map(
            _type='TEST_ABC',
            pk=pk,
            sk=sk,
            SessionId='a728b36c01f',
            NewData={
                'key_678': 'val_234',
                'key_234': 'val_090'
            }
        )
        self.maxDiff = None
        self.assertDictEqual(
            val,
            {
                'CreatedAt': {'S': '2003-09-05T15:33:28+00:00'},
                'CreatedBy': {'S': ''},
                'ExpiresAt': {'N': '1065368008'},
                'ModifiedAt': {'S': ''},
                'ModifiedBy': {'S': ''},
                'NewData': {'M': {'key_234': {'S': 'val_090'}, 'key_678': {'S': 'val_234'}}},
                'PK': {'S': 'TEST_ABC#999777555'},
                'SK': {'S': 'TEST_ABC#999777555'},
                'SessionId': {'S': 'a728b36c01f'},
                'Type': {'S': 'TEST_ABC'}
            }
        )
