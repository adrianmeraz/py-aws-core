import httpx
import respx
from httpx import Response, codes

from py_aws_core.testing import BaseTestFixture
from spoofing.proxyrack import backends, exceptions, proxyrack_api


# class ProxyRackProxyBackendTests(BaseTestFixture):
#     """
#         ProxyRackProxyBackend Tests
#     """
#
#     def test_proxy_url(self):
#         proxy_url = backends.ProxyRackProxyBackend(
#             session_id='user123',
#             city=ip.city,
#             country=ip.country,
#             address=ip.address,
#         ).get_proxy_url()
#
#         self.assertEquals(
#             proxy_url,
#             (f'http://{settings.PROXY_USERNAME};timeoutSeconds=60;session=user123;'
#              f'osName=Windows;city=Dallas;country=US;proxyIp=192.168.86.250:{settings.PROXY_PASSWORD}@test123:5000')
#         )
#
#
# class ValidatedProxyRackProxyBackendTests(BaseTestCase):
#     """
#         ValidatedProxyRackProxyBackend Tests
#     """
#
#     @classmethod
#     def setUpTestData(cls):
#         super().setUpTestData()
#         cls.proxy = models.Proxy.objects.create_rotating_proxy(
#             url='test123:5000',
#         )
#         cls.ip = models.IP.objects.create(
#             city='Dallas',
#             country='US',
#             isp='Spectrum',
#             address='192.168.86.250',
#         )
#
#     @respx.mock
#     def test_get_proxy_url_with_ip(self):
#         mocked_ipify_route = respx.get("https://api.ipify.org/").mock(
#             return_value=Response(status_code=codes.OK, json=self.ipify_json)
#         )
#         mocked_ipinfo_route = respx.get("https://ipinfo.io/json").mock(
#             return_value=Response(status_code=codes.OK, json=self.details_json)
#         )
#         fingerprint = models.SessionFingerprint.objects.create_desktop_default()
#         fingerprint.add_ip(self.ip)
#
#         proxy_url = backends.ValidatedProxyRackProxyBackend(fingerprint, session_id='user123').get_proxy_url()
#
#         self.assertEquals(
#             proxy_url,
#             (f'http://{settings.PROXY_USERNAME};timeoutSeconds=60;session=user123;'
#              f'osName=Windows;city=Dallas;country=US;proxyIp=192.168.86.250:{settings.PROXY_PASSWORD}@test123:5000')
#         )
#
#         self.assertEquals(mocked_ipify_route.call_count, 1)
#         self.assertEquals(mocked_ipinfo_route.call_count, 1)
#
#     @respx.mock
#     def test_get_proxy_url_no_prior_ip(self):
#         mocked_ipinfo_route = respx.get("https://ipinfo.io/json").mock(
#             return_value=Response(status_code=codes.OK, json=self.details_json)
#         )
#         fingerprint = models.SessionFingerprint.objects.create_desktop_default()
#         proxy_url = backends.ValidatedProxyRackProxyBackend(fingerprint).get_proxy_url()
#
#         self.assertEquals(
#             proxy_url,
#             (f'http://{settings.PROXY_USERNAME};timeoutSeconds=60;session=423582f8-4058-4c21-b993-31c62e8cbaed;'
#              f'osName=Windows;country=US:{settings.PROXY_PASSWORD}@test123:5000')
#         )
#
#         self.assertEquals(mocked_ipinfo_route.call_count, 1)
#
#     @respx.mock
#     def test_get_proxy_url_ProxyConnectionFailed_with_prior_ips(self):
#         mocked_ipify_route = respx.get("https://api.ipify.org/").mock(
#             side_effect=httpx.TransportError(message='')
#         )
#         mocked_ipinfo_route = respx.get("https://ipinfo.io/json").mock(
#             return_value=Response(status_code=codes.OK, json=self.details_json)
#         )
#
#         fingerprint = models.SessionFingerprint.objects.create_desktop_default()
#         fingerprint.add_ip(self.ip)
#
#         backends.ValidatedProxyRackProxyBackend(fingerprint).get_proxy_url()
#
#         self.assertEquals(mocked_ipify_route.call_count, 1)
#         self.assertEquals(mocked_ipinfo_route.call_count, 1)
