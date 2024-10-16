import typing

from py_aws_core import logs
from py_aws_core.spoofing.proxy_interface import IProxy
from py_aws_core.spoofing.proxyrack import const, utils

logger = logs.get_logger()


class ProxyRackService(IProxy):
    def get_proxy_url(
        self,
        netloc: str,
        cities: typing.List[str] = None,
        country: str = None,
        isps: typing.List[str] = None,
        proxy_ip: str = None,
        proxy_os: const.ProxyOs = None,
        session_id: str = None,
        **kwargs
    ) -> str:
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
            username=self.proxy_username,
            password=self.proxy_password,
            netloc=netloc,
            config=config
        ).http_url
