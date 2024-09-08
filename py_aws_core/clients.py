import base64
import binascii
import pickle
import ssl
from http.cookiejar import CookieJar

from httpx import Client, HTTPStatusError, TimeoutException, NetworkError, ProxyError

from py_aws_core import database, decorators, exceptions, logs, utils
from py_aws_core.db_dynamo import get_db_client
from py_aws_core.db_session import SessionDBAPI
from py_aws_core.sessions import ABCPersistSession

logger = logs.logger
db = database.DynamoDatabase()
# Using same ssl context for all clients to save on loading SSL bundles
# See https://github.com/python/cpython/issues/95031#issuecomment-1749489998
# Also results in _tests running about 9 times faster
SSL_CONTEXT = ssl.create_default_context()


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

    def __init__(self, session_id: str = None, follow_redirects: bool = True, verify: bool = None, *args, **kwargs):
        super().__init__(
            follow_redirects=follow_redirects,
            default_encoding="utf-8",
            verify=verify or SSL_CONTEXT,
            *args,
            **kwargs
        )
        self._session_id = session_id or utils.get_uuid_hex()

    @decorators.retry(retry_exceptions=RETRY_EXCEPTIONS)
    @decorators.http_status_check(reraise_status_codes=RETRY_STATUS_CODES)
    def send(self, *args, **kwargs):
        return super().send(*args, **kwargs)

    @property
    def session_id(self) -> str:
        return self._session_id

    @property
    def b64_encoded_cookies(self) -> bytes:
        return base64.encodebytes(pickle.dumps([c for c in self.cookies.jar]))

    def b64_decode_and_set_cookies(self, b64_cookies: bytes):
        if not b64_cookies:
            logger.info(f'Session ID: {self.session_id} -> No Cookies To Restore: {b64_cookies}')
            self.cookies.jar = CookieJar()
            return
        try:
            cookie_jar = CookieJar()
            decoded_bytes = base64.decodebytes(b64_cookies)
            for c in pickle.loads(decoded_bytes):
                logger.info(f'Session ID: {self.session_id} -> Setting CookieJar Cookie: "{c}"')
                cookie_jar.set_cookie(c)
            self.cookies.jar = cookie_jar
        except (pickle.PickleError, binascii.Error) as e:
            raise exceptions.CookieDecodingError(info=f'Session ID: {self.session_id} -> Cookie Error: {str(e)}')


class SessionPersistClient(RetryClient, ABCPersistSession):
    def __enter__(self):
        super().__enter__()
        self.read_session()
        return self

    def __exit__(self, *args, **kwargs):
        self.write_session(session_id=self.session_id)
        super().__exit__(*args, **kwargs)

    def read_session(self):
        session_id = self.session_id
        logger.info(f'Session ID: {session_id} -> Rehydrating session...')
        session = db.get_session(session_id=session_id)
        if not session:
            logger.info(f'Session ID: {session_id} -> No prior session found.')
            return
        self.b64_decode_and_set_cookies(b64_cookies=session.b64_cookies_bytes)
        logger.info(f'Session ID: {session_id} -> Rehydrated {len(self.cookies.jar)} cookies')

    def write_session(self, session_id):
        logger.info(f'Session ID: {session_id} -> Writing cookies to database...')
        db.put_session(session_id=session_id, b64_cookies=self.b64_encoded_cookies)
        logger.info(f'Session ID: {session_id} -> Wrote cookies to database')
