from unittest import mock, TestCase
from py_aws_core import dynamodb

class ABCCommonAPITests(TestCase):
    def test_calc_expire_at_timestamp(self):
        val = dynamodb.ABCCommonAPI.calc_expire_at_timestamp()
        dt = datetime.datetime(year=2003, month=9, day=5, hour=15, minute=33, second=28, tzinfo=datetime.timezone.utc)
        mocked_get_now_timestamp.return_value = dt