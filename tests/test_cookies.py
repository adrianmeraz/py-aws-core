import time
from unittest import mock, TestCase

from py_aws_core import cookies


class BuildSetCookieHeaderTests(TestCase):
    @mock.patch.object(time, 'time')
    def test_build_set_cookie_header(self, mocked_time):
        mocked_time.return_value = 1062776008  # Fri, 05 Sep 2003 15:33:28 GMT

        val = cookies.CookieUtil.build_set_cookie_header(
            name='ipsum',
            domain='.example.com',
            value='lorem ipsum dolor sit',
            path='/',
            expires_in_seconds=86400*4  # 4 days
        )

        self.assertEqual(val, 'ipsum="lorem ipsum dolor sit"; Domain=.example.com; expires=Tue, 09 Sep 2003 15:33:28 GMT; Path=/; Secure')
        self.assertEqual(mocked_time.call_count, 1)
