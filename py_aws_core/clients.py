from httpx import Client, HTTPStatusError, TimeoutException, NetworkError, ProxyError

from . import decorators, logs

logger = logs.logger


class RetryClient(Client):
    """
    Http/2 Client
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

    def __init__(self, *args, **kwargs):
        super().__init__(
            follow_redirects=True,
            default_encoding="utf-8",
            *args,
            **kwargs
        )

    @decorators.retry(retry_exceptions=RETRY_EXCEPTIONS)
    @decorators.http_status_check(reraise_status_codes=RETRY_STATUS_CODES)
    def send(self, *args, **kwargs):
        return super().send(*args, **kwargs)
