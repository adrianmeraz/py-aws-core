import base64
import binascii
import pickle
from http.cookiejar import CookieJar

from httpx import Client, HTTPStatusError, TimeoutException, NetworkError, ProxyError

from . import decorators, exceptions, logs

logger = logs.logger


class RetryClient(Client):
    """
    Http/2 Client that retries for given exceptions and http status codes
    """
    RETRY_EXCEPTIONS = (
        HTTPStatusError,
        TimeoutException,
        NetworkError,
        ProxyError
    )

    RETRY_STATUS_CODES = (
        408,
        425,
        429,
        500,
        502,
        503,
        504,
    )

    def __init__(self, follow_redirects: bool = True, *args, **kwargs):

        super().__init__(
            follow_redirects=follow_redirects,
            default_encoding="utf-8",
            *args,
            **kwargs
        )

    @decorators.retry(retry_exceptions=RETRY_EXCEPTIONS)
    @decorators.http_status_check(reraise_status_codes=RETRY_STATUS_CODES)
    def send(self, *args, **kwargs):
        return super().send(*args, **kwargs)

    @property
    def b64_encoded_cookies(self) -> bytes:
        return base64.encodebytes(pickle.dumps([c for c in self.cookies.jar]))

    def b64_decode_and_set_cookies(self, b64_cookies: bytes):
        if not b64_cookies:
            logger.info(f'No Cookies To Restore: {b64_cookies}')
            self.cookies.jar = CookieJar()
        try:
            cookie_jar = CookieJar()
            decoded_bytes = base64.decodebytes(b64_cookies)
            for c in pickle.loads(decoded_bytes):
                cookie_jar.set_cookie(c)
            self.cookies.jar = cookie_jar
        except (pickle.PickleError, binascii.Error) as e:
            raise exceptions.CookieDecodingError(info=f'{b64_cookies}, Cookie Error: {str(e)}')
