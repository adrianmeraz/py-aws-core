import logging

from spoofing.backends import ProxyBackend
from spoofing.proxyrack import const, utils

logger = logging.getLogger(__name__)


class ProxyRackProxyBackend(ProxyBackend):
    def get_proxy_url(
        self,
        netloc: str,
        city: str = None,
        country: str = None,
        proxy_ip: str = None,
        proxy_os: const.ProxyOs = None,
        **kwargs
    ):
        config = utils.ProxyBuilder.Config(
            username=self.get_proxy_username(),
            cities=city,
            country=country,
            proxy_ip=proxy_ip,
            proxy_os=proxy_os,
            session_id=self._session_id,
            refresh_minutes=60
        )
        return utils.ProxyBuilder(
            password=self.get_proxy_password(),
            netloc=netloc,
            config=config
        ).http_url
