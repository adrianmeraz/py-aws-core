import typing

from py_aws_core.spoofing.proxyrack import const


class ProxyBuilder:

    class Config:
        def __init__(
            self,
            cities: typing.List[str] = None,
            country: str = None,
            isps: typing.List[str] = None,
            proxy_ip: str = None,
            proxy_os: const.ProxyOs = None,
            refresh_minutes: int = 10,
            session_id: str | str = None,
            **kwargs
        ):
            self._cities = cities
            self._country = country
            self._isps = isps
            self._proxy_ip = proxy_ip
            self._proxy_os = proxy_os
            self._session_id = session_id
            self._refresh_minutes = refresh_minutes
            self._kwargs = kwargs

        @property
        def to_string(self) -> str:
            opts = {
                'city': self.to_str(self._cities),
                'country': self._country,
                'isp': self.to_str(self._isps),
                'osName': self._proxy_os.value,
                'proxyIp': self._proxy_ip,
                'session': self._session_id,
                'refreshMinutes': self._refresh_minutes
            } | self._kwargs
            return ';'.join([f'{k}={str(v).replace(" ", "")}' for k, v in opts.items() if v])

        @staticmethod
        def to_str(objs: typing.List[str]) -> str:
            if objs:
                return ','.join(objs)
            return ''

    def __init__(self, username: str, password: str, netloc: str, config: Config):
        self._username = username
        self._password = password
        self._netloc = netloc
        self._config = config

    @property
    def http_url(self) -> str:
        return f'http://{self.params}:{self._password}@{self._netloc}'

    @property
    def params(self):
        return ';'.join([self._username, self._config.to_string])
