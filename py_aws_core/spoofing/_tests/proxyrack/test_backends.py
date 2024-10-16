from unittest import mock

from py_aws_core.spoofing.proxyrack import const
from py_aws_core.spoofing.proxyrack.proxyrack_service import ProxyRackService
from py_aws_core.testing import BaseTestFixture


class ProxyRackProxyBackendTests(BaseTestFixture):
    """
        ProxyRackProxyBackend Tests
    """

    def test_proxy_url(self):
        proxy_service = ProxyRackService(proxy_username='user123', proxy_password='pass456')
        proxy_url = proxy_service.get_proxy_url(
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
