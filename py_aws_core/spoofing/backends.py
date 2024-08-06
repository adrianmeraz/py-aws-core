import logging
import random
import uuid
from abc import ABC

from httpx import Client

from . import const

logger = logging.getLogger(__name__)


class ProxyBackend(ABC):
    def __init__(self, session_id: uuid.UUID = None, **kwargs):
        self._session_id = session_id or uuid.uuid4()
        self.kwargs = kwargs

    def get_proxy_url(self):
        raise NotImplemented

    @staticmethod
    def _weighted_proxy_country():
        countries, weights = zip(const.PROXY_COUNTRY_WEIGHTS)
        return random.choices(population=countries, weights=weights, k=1)[0]


class CaptchaBackend(ABC):

    def get_captcha_id(self, client: Client, proxy, site_key: str, page_url: str):
        raise NotImplemented

    def get_gcaptcha_token(self, client: Client, captcha_id: str):
        raise NotImplemented

    def report_bad_captcha_id(self, client: Client, captcha_id: str):
        raise NotImplemented

    def report_good_captcha_id(self, client: Client, captcha_id: str):
        raise NotImplemented
