import logging
from urllib.parse import urlparse

from httpx import Client

from py_aws_core import decorators as aws_decorators
from py_aws_core.secrets_manager import get_secrets_manager
from . import decorators
from .exceptions import CaptchaNotReady, TwoCaptchaException

logger = logging.getLogger(__name__)
secrets_manager = get_secrets_manager()

ROOT_URL = 'http://2captcha.com'


class TwoCaptchaAPI:
    _api_key = None

    @classmethod
    def get_api_key(cls):
        if not cls._api_key:
            cls._api_key = secrets_manager.get_secret('CAPTCHA_PASSWORD')
        return cls._api_key

    @classmethod
    def get_pingback_token(cls):
        if not cls._api_key:
            cls._api_key = secrets_manager.get_secret('TWOCAPTCHA_PINGBACK_TOKEN')
        return cls._api_key


class TwoCaptchaResponse:
    def __init__(self, data):
        self.status = data['status']
        self.request = data['request']
        self.error_text = data.get('error_text')

    @property
    def is_captcha_reported(self):
        return self.request == 'OK_REPORT_RECORDED'


class PingCaptchaId(TwoCaptchaAPI):
    class Response(TwoCaptchaResponse):
        pass

    @classmethod
    @decorators.error_check
    def call(cls, client: Client, proxy: str, site_key: str, page_url: str, pingback: str = None) -> Response:
        url = f'{ROOT_URL}/in.php'
        proxy_parts = urlparse(proxy)
        proxy_type = proxy_parts.scheme.upper()

        params = {
            'key': cls.get_api_key(),
            'method': 'userrecaptcha',
            'googlekey': site_key,
            'pageurl': page_url,
            'json': '1',
            'proxy': proxy_parts.netloc,
            'proxytype': proxy_type,
        }
        if pingback:
            params['pingback'] = pingback

        r = client.post(url, params=params, follow_redirects=False)  # Disable redirects to network splash pages
        if not r.status_code == 200:
            raise TwoCaptchaException(f'Non 200 Response. Proxy: {proxy}, Response: {r.text}')

        return cls.Response(r.json())


class GetSolvedToken(TwoCaptchaAPI):
    class Response(TwoCaptchaResponse):
        pass

    @classmethod
    @aws_decorators.retry(retry_exceptions=(CaptchaNotReady,), tries=60, delay=5, backoff=1)
    @decorators.error_check
    def call(cls, client: Client, captcha_id: int) -> Response:
        url = f'{ROOT_URL}/res.php'

        params = {
            'key': cls.get_api_key(),
            'action': 'get',
            'id': captcha_id,
            'json': 1,
        }

        r = client.get(url, params=params)

        return cls.Response(r.json())


class ReportCaptcha(TwoCaptchaAPI):
    class Response(TwoCaptchaResponse):
        pass

    @classmethod
    def call(cls, client: Client, captcha_id: int, is_good: bool) -> Response:
        url = f'{ROOT_URL}/res.php'

        action = 'reportgood' if is_good else 'reportbad'

        params = {
            'key': cls.get_api_key(),
            'action': action,
            'id': captcha_id,
            'json': '1',
        }

        r = client.get(url, params=params)

        return cls.Response(r.json())


class ReportBadCaptcha(ReportCaptcha):
    @classmethod
    @decorators.error_check
    def call(cls, client: Client, captcha_id: int, **kwargs):
        r = super().call(client=client, captcha_id=captcha_id, is_good=False)
        logger.info(f'Reported bad captcha. id: {captcha_id}')
        return r


class ReportGoodCaptcha(ReportCaptcha):
    @classmethod
    @decorators.error_check
    def call(cls, client: Client, captcha_id: int, **kwargs):
        r = super().call(client=client, captcha_id=captcha_id, is_good=True)
        logger.info(f'Reported good captcha. id: {captcha_id}')
        return r


class RegisterPingback(TwoCaptchaAPI):
    class Response(TwoCaptchaResponse):
        pass

    @classmethod
    @aws_decorators.retry(retry_exceptions=(CaptchaNotReady,))
    @decorators.error_check
    def call(cls, client: Client, addr: str) -> Response:
        url = f'{ROOT_URL}/res.php'

        params = {
            'key': cls.get_api_key(),
            'action': 'add_pingback',
            'addr': addr,
            'json': '1',
        }

        r = client.get(url, params=params)
        return cls.Response(r.json())
