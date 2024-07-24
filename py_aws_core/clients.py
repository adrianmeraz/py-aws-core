from httpx import Client, HTTPStatusError, TimeoutException, NetworkError, ProxyError

from . import decorators, logs

logger = logs.logger


RETRY_EXCEPTIONS = (
    HTTPStatusError,
    TimeoutException,
    NetworkError,
    ProxyError
)


class RetryClient(Client):
    """
    Http/2 Client
    """

    RETRYABLE_STATUS_CODES = [
        408,
        425,
        429,
        500,
        502,
        503,
        504,
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(
            follow_redirects=True,
            default_encoding="utf-8",
            *args,
            **kwargs
        )

    @decorators.retry(retry_exceptions=RETRY_EXCEPTIONS)
    @decorators.api_error_check
    def send(self, *args, **kwargs):
        return super().send(*args, **kwargs)