import datetime
from unittest import mock, TestCase

from py_aws_core import dynamodb, utils


class ABCCommonAPITests(TestCase):
    @mock.patch.object(utils, 'get_now_timestamp')
    def test_calc_expire_at_timestamp(self, mocked_get_now_timestamp):
        dt = datetime.datetime(year=2003, month=9, day=5, hour=15, minute=33, second=28, tzinfo=datetime.timezone.utc)
        mocked_get_now_timestamp.return_value = dt
        val = dynamodb.ABCCommonAPI.calc_expire_at_timestamp(days=1)
        self.assertEqual(val, 1062862408)

        val = dynamodb.ABCCommonAPI.calc_expire_at_timestamp(days=180)
        self.assertEqual(val, 1078328008)

        val = dynamodb.ABCCommonAPI.calc_expire_at_timestamp(days=None)
        self.assertEqual(val, '')
