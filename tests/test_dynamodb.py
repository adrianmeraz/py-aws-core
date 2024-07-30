import datetime
from unittest import mock, TestCase

from py_aws_core import const, dynamodb, utils


class ABCCommonAPITests(TestCase):
    @mock.patch.object(utils, 'get_now_datetime')
    def test_calc_expire_at_timestamp(self, mocked_get_now_datetime):
        dt = datetime.datetime(year=2003, month=9, day=5, hour=15, minute=33, second=28, tzinfo=datetime.timezone.utc)
        mocked_get_now_datetime.return_value = dt
        val = dynamodb.ABCCommonAPI.calc_expire_at_timestamp(expire_in_seconds=1*const.SECONDS_IN_DAY)
        self.assertEqual(val, 1062862408)

        val = dynamodb.ABCCommonAPI.calc_expire_at_timestamp(expire_in_seconds=180*const.SECONDS_IN_DAY)
        self.assertEqual(val, 1078328008)

        val = dynamodb.ABCCommonAPI.calc_expire_at_timestamp(expire_in_seconds=None)
        self.assertEqual(val, '')
