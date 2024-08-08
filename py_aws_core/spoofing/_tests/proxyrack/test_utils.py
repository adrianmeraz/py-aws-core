from py_aws_core.testing import BaseTestFixture
from py_aws_core.spoofing.proxyrack import const, utils


class UtilTests(BaseTestFixture):
    """
    Utility Tests
    """

    def test_proxy_builder(self):
        config = utils.ProxyBuilder.Config(
            cities=['Seattle', 'New York', 'Los Angeles'],
            country='US',
            isps=['Verizon', 'Ipxo Limited'],
            proxy_ip='184.53.48.165',
            proxy_os=const.ProxyOs.LINUX,
            refresh_minutes=10,
            session_id='13ac97fe-0f26-45ff-aeb9-2801400326ec',
            missingKey=''
        )
        proxy_builder = utils.ProxyBuilder(
            username='proxyman123',
            password='goodpw567',
            netloc='megaproxy.rotating.proxyrack.net:10000',
            config=config
        )

        self.assertEqual(
            proxy_builder.http_url,
            'http://proxyman123;city=Seattle,NewYork,LosAngeles;country=US;isp=Verizon,IpxoLimited;osName=Linux;proxyIp=184.53.48.165;session=13ac97fe-0f26-45ff-aeb9-2801400326ec;refreshMinutes=10:goodpw567@megaproxy.rotating.proxyrack.net:10000'
        )
