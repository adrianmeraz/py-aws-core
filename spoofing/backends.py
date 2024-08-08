import logging
import random
from abc import ABC, abstractmethod

from httpx import Client

from py_aws_core.secrets_manager import get_secrets_manager
from . import const

logger = logging.getLogger(__name__)
secrets_manager = get_secrets_manager()


class ProxyBackend(ABC):
    @abstractmethod
    def get_proxy_url(self, **kwargs):
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


class CaptchaBackend(ABC):

    def get_captcha_id(self, client: Client, proxy: str, site_key: str, page_url: str, **kwargs):
        raise NotImplemented

    def get_gcaptcha_token(self, client: Client, captcha_id: str, **kwargs):
        raise NotImplemented

    def report_bad_captcha_id(self, client: Client, captcha_id: str, **kwargs):
        raise NotImplemented

    def report_good_captcha_id(self, client: Client, captcha_id: str, **kwargs):
        raise NotImplemented
