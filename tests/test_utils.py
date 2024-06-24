import datetime
from unittest import TestCase

from py_aws_core import utils


class Iso8601NowTimestampTests(TestCase):
    def test_ok(self):
        dt = datetime.datetime(year=2003, month=9, day=5, hour=15, minute=33, second=28)
        val = utils.to_iso_8601(dt=dt)
        self.assertEqual(
            val,
            '2003-09-05T15:33:28'
        )
