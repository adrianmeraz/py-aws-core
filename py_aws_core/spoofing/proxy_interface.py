import random
from abc import ABC, abstractmethod

from py_aws_core import logs
from . import const

logger = logs.get_logger()


class IProxy(ABC):
    def __init__(self, proxy_username: str, proxy_password: str):
        self._proxy_username = proxy_username
        self._proxy_password = proxy_password

    @abstractmethod
    def get_proxy_url(self, **kwargs) -> str:
        raise NotImplemented

    @staticmethod
    def get_weighted_country():
        countries, weights = zip(const.PROXY_COUNTRY_WEIGHTS)
        return random.choices(population=countries, weights=weights, k=1)[0]

    @property
    def proxy_username(self):
        return self._proxy_username

    @property
    def proxy_password(self):
        return self._proxy_password
