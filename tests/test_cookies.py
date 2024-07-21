import datetime
from unittest import mock, TestCase

from py_aws_core import cookies, utils


class BuildSetCookieHeaderTests(TestCase):
    @mock.patch.object(utils, 'get_now_datetime')
    def test_ok(self, mocked_get_now_datetime):
        dt = datetime.datetime(year=2003, month=9, day=5, hour=15, minute=33, second=28, tzinfo=datetime.timezone.utc)
        mocked_get_now_datetime.return_value = dt

        val = cookies.build_set_cookie_header_value_2(
            name='ipsum',
            domain='.example.com',
            value='lorem ipsum dolor sit',
            path='/',
            expires_in_seconds=86400
        )

        self.assertEqual(val, 'Set-Cookie: ipsum="lorem ipsum dolor sit"; Domain=.example.com; Path=/')
