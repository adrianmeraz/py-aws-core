import datetime
from unittest import mock, TestCase

from py_aws_core import cookies, utils


class BuildSetCookieHeaderTests(TestCase):
    @mock.patch.object(utils, 'get_now_datetime')
    def test_build_set_cookie_header(self, mocked_get_now_datetime):
        dt = datetime.datetime(year=2003, month=9, day=5, hour=15, minute=33, second=28, tzinfo=datetime.timezone.utc)
        mocked_get_now_datetime.return_value = dt

        val = cookies.CookieUtil.build_set_cookie_header(
            name='ipsum',
            domain='.example.com',
            value='lorem ipsum dolor sit',
            path='/',
            expires_in_seconds=86400
        )

        self.assertEqual(val, 'Set-Cookie: ipsum="lorem ipsum dolor sit"; Domain=.example.com; expires=Sat, 06 Sep 2003 15:33:28 GMT; Path=/')
        self.assertEqual(mocked_get_now_datetime.call_count, 1)

    @mock.patch.object(utils, 'get_now_datetime')
    def test_get_expiry_timestamp(self, mocked_get_now_datetime):
        dt = datetime.datetime(year=2003, month=9, day=5, hour=15, minute=33, second=28, tzinfo=datetime.timezone.utc)
        mocked_get_now_datetime.return_value = dt

        val = cookies.CookieUtil.get_expiry_timestamp(expire_in_seconds=9999888)

        self.assertEqual(val, 'Tue, 30 Dec 2003 09:18:16 GMT')
