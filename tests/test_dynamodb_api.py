import datetime
import json
from importlib.resources import as_file
from unittest import mock

from py_aws_core import const, utils, boto_responses
from py_aws_core.dynamodb_api import DynamoDBAPI
from py_aws_core.testing import BaseTestFixture


class DynamoDBAPITests(BaseTestFixture):
    @mock.patch.object(utils, 'get_now_datetime')
    def test_calc_expire_at_timestamp(self, mocked_get_now_datetime):
        dt = datetime.datetime(year=2003, month=9, day=5, hour=15, minute=33, second=28, tzinfo=datetime.timezone.utc)
        mocked_get_now_datetime.return_value = dt
        val = DynamoDBAPI.calc_expire_at_timestamp(expire_in_seconds=1 * const.SECONDS_IN_DAY)
        self.assertEqual(val, 1062862408)

        val = DynamoDBAPI.calc_expire_at_timestamp(expire_in_seconds=180 * const.SECONDS_IN_DAY)
        self.assertEqual(val, 1078328008)

        val = DynamoDBAPI.calc_expire_at_timestamp(expire_in_seconds=None)
        self.assertEqual(val, '')

    def test_get_item_empty(self):
        source = self.TEST_DB_RESOURCES_PATH.joinpath('db#get_item#empty.json')
        with as_file(source) as r_json:
            val = boto_responses.ItemResponse(json.loads(r_json.read_text(encoding='utf-8')))

        self.assertIsNone(val.Item)

    @mock.patch.object(utils, 'get_now_datetime')
    def test_get_put_item_map(self, mocked_get_now_datetime):
        dt = datetime.datetime(year=2003, month=9, day=5, hour=15, minute=33, second=28, tzinfo=datetime.timezone.utc)
        mocked_get_now_datetime.return_value = dt

        pk = sk = 'TEST_ABC#999777555'
        val = DynamoDBAPI.get_put_item_map(
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
                'PK': 'TEST_ABC#999777555',
                'SK': 'TEST_ABC#999777555',
                'Type': 'TEST_ABC',
                'CreatedAt': '2003-09-05T15:33:28+00:00',
                'CreatedBy': '',
                'ModifiedAt': '',
                'ModifiedBy': '',
                'ExpiresAt': 1065368008,
                'SessionId': 'a728b36c01f',
                'NewData': {
                    'key_678': 'val_234',
                    'key_234': 'val_090'
                }
            }
        )

    def test_serialize_types(self):
        val = DynamoDBAPI.serialize_types({
            ':ty': 'TEST_TYPE',
            ':si': '3b7529c92f',
            ':ea': 1000050000,
        })
        self.assertDictEqual(
            val,
            {
                ':ea': {'N': '1000050000'},
                ':si': {'S': '3b7529c92f'},
                ':ty': {'S': 'TEST_TYPE'}
            }
        )

        test_dict = {
            'request_token_1': 'test_token_1',
            'request_token_2': None,
            'request_token_3': 'test_token_3',
            'request_token_4': '',
        }
        val_1 = DynamoDBAPI.serialize_types(test_dict)
        self.assertEqual(
            val_1,
            {
                'request_token_1': {'S': 'test_token_1'},
                'request_token_2': {'NULL': True},
                'request_token_3': {'S': 'test_token_3'},
                'request_token_4': {'S': ''}
            }
        )

        val_2 = DynamoDBAPI.serialize_types({
            'PK': 'TEST#123456',
            'SK': 'SK#89076',
        })
        self.assertEqual(
            val_2,
            {
                'PK': {'S': 'TEST#123456'},
                'SK': {'S': 'SK#89076'}
            }
        )

    def test_build_update_expression(self):
        fields = [
            DynamoDBAPI.UpdateField(expression_attr='ab', set_once=True),
            DynamoDBAPI.UpdateField(expression_attr='gh', set_once=False),
            DynamoDBAPI.UpdateField(expression_attr='yu', set_once=True),
        ]
        val = DynamoDBAPI.build_update_expression(fields)
        self.assertEqual('SET #gh = :gh, #ab = if_not_exists(#ab, :ab), #yu = if_not_exists(#yu, :yu)', val)
