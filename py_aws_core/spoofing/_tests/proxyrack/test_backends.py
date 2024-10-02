from unittest import mock


from py_aws_core.testing import BaseTestFixture
from py_aws_core.spoofing.proxyrack import const
from py_aws_core.spoofing.proxyrack.backends import ProxyRackProxyBackend


class ProxyRackProxyBackendTests(BaseTestFixture):
    """
        ProxyRackProxyBackend Tests
    """

    @mock.patch.object(ProxyRackProxyBackend, 'get_proxy_password')
    @mock.patch.object(ProxyRackProxyBackend, 'get_proxy_username')
    def test_proxy_url(self, mocked_get_proxy_username, mocked_get_proxy_password):
        mocked_get_proxy_username.return_value = 'user123'
        mocked_get_proxy_password.return_value = 'pass456'
        proxy_url = ProxyRackProxyBackend.get_proxy_url(
            cities=['Dallas'],
            netloc='megaproxy.rotating.proxyrack.net:10000',
            proxy_ip='192.168.86.250',
            proxy_os=const.ProxyOs.WINDOWS,
            session_id='user123',
        )

        self.assertEqual(
            'http://user123;city=Dallas;osName=Windows;proxyIp=192.168.86.250;session=user123;refreshMinutes=60:pass456@megaproxy.rotating.proxyrack.net:10000',
            proxy_url
        )
