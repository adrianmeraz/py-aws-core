import random
from abc import ABC, abstractmethod

from py_aws_core import logs
from py_aws_core.secrets_manager import get_secrets_manager
from . import const

logger = logs.get_logger()
secrets_manager = get_secrets_manager()


class ProxyBackend(ABC):
    @classmethod
    @abstractmethod
    def get_proxy_url(cls, **kwargs) -> str:
        raise NotImplemented

    @staticmethod
    def get_weighted_country():
        countries, weights = zip(const.PROXY_COUNTRY_WEIGHTS)
        return random.choices(population=countries, weights=weights, k=1)[0]

    @classmethod
    def get_proxy_password(cls):
        return secrets_manager.get_secret(secret_name='PROXY_PASSWORD')

    @classmethod
    def get_proxy_username(cls):
        return secrets_manager.get_secret(secret_name='PROXY_USERNAME')
