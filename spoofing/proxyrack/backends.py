import logging
import typing
import uuid

from spoofing.backends import ProxyBackend
from spoofing.proxyrack import const, utils

logger = logging.getLogger(__name__)


class ProxyRackProxyBackend(ProxyBackend):
    def get_proxy_url(
        self,
        netloc: str,
        cities: typing.List[str] = None,
        country: str = None,
        isps: typing.List[str] = None,
        proxy_ip: str = None,
        proxy_os: const.ProxyOs = None,
        session_id: str | uuid.UUID = None,
        **kwargs
    ):
        config = utils.ProxyBuilder.Config(
            cities=cities,
            country=country,
            isps=isps,
            proxy_ip=proxy_ip,
            proxy_os=proxy_os,
            session_id=session_id,
            refresh_minutes=60
        )
        return utils.ProxyBuilder(
            username=self.get_proxy_username(),
            password=self.get_proxy_password(),
            netloc=netloc,
            config=config
        ).http_url
