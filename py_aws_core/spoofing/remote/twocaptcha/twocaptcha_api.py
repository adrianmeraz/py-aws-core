import logging
from functools import wraps
from urllib.parse import urlparse

from py_aws_core.secrets_manager import get_secrets_manager
from . import decorators
from .exceptions import (CaptchaNotReady, CaptchaUnsolvable, CriticalError, WarnError, InvalidResponse,
                         TwoCaptchaException)

logger = logging.getLogger(__name__)
secrets_manager = get_secrets_manager()

API_KEY = secrets_manager.get_secret('CAPTCHA_PASSWORD')
BASE_URL = 'http://2captcha.com'

EXC_MAP = {
    'ERROR_WRONG_CAPTCHA_ID': WarnError,
    'MAX_USER_TURN': WarnError,
    'ERROR_NO_SLOT_AVAILABLE': WarnError,
    'ERROR_PROXY_FORMAT': CriticalError,
    'ERROR_WRONG_USER_KEY': CriticalError,
    'ERROR_KEY_DOES_NOT_EXIST': CriticalError,
    'ERROR_ZERO_BALANCE': CriticalError,
    'IP_BANNED': CriticalError,
    'ERROR_GOOGLEKEY': CriticalError,
    'ERROR_CAPTCHA_UNSOLVABLE': CaptchaUnsolvable,
    'CAPCHA_NOT_READY':  CaptchaNotReady
}


def error_check(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        r = func(*args, **kwargs)
        if exc := EXC_MAP.get(r.request):
            raise exc(*args, **kwargs)
        if r.status == 1:
            return r
        raise InvalidResponse(request=r.request, error_text=r.error_text)
    return wrapper_func


@error_check
def get_captcha_id(client, proxy, site_key, page_url, pingback=None):
    url = f'{BASE_URL}/in.php'
    proxy_parts = urlparse(proxy)
    proxy_type = proxy_parts.scheme.upper()

    params = {
        'key': API_KEY,
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

    return TwoCaptchaResponse(r.json())


@decorators.retry(retry_exceptions=(CaptchaNotReady,), tries=60, delay=5, backoff=1)
@error_check
def get_solved_token(client, captcha_id):
    url = f'{BASE_URL}/res.php'

    params = {
        'key': API_KEY,
        'action': 'get',
        'id': captcha_id,
        'json': 1,
    }

    r = client.get(url, params=params)

    return TwoCaptchaResponse(r.json())


def report_bad_captcha(client, captcha_id):
    r = report_captcha(client, captcha_id, is_good=False)
    logger.info(f'Reported bad captcha. id: {captcha_id}')
    return r


def report_good_captcha(client, captcha_id):
    r = report_captcha(client, captcha_id, is_good=True)
    logger.info(f'Reported good captcha. id: {captcha_id}')
    return r


@error_check
def report_captcha(client, captcha_id, is_good):
    url = f'{BASE_URL}/res.php'

    c_type = "good" if is_good else "bad"

    params = {
        'key': API_KEY,
        'action': f'report{c_type}',
        'id': captcha_id,
        'json': '1',
    }

    r = client.get(url, params=params)

    return TwoCaptchaResponse(r.json())


@decorators.retry(retry_exceptions=(CaptchaNotReady,))
@error_check
def register_pingback(client, addr):
    url = f'{BASE_URL}/res.php'

    params = {
        'key': API_KEY,
        'action': 'add_pingback',
        'addr': addr,
        'json': '1',
    }

    r = client.get(url, params=params)
    return TwoCaptchaResponse(r.json())


class TwoCaptchaResponse:
    def __init__(self, data):
        self.status = data['status']
        self.request = data['request']
        self.error_text = data.get('error_text')

    @property
    def is_captcha_reported(self):
        return self.request == 'OK_REPORT_RECORDED'