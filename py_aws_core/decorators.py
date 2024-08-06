import typing
from functools import wraps
from typing import Any, Dict, List

from botocore.exceptions import ClientError
from httpx import codes, HTTPStatusError

from py_aws_core import db_dynamo, exceptions, logs, utils

logger = logs.logger


def boto3_handler(raise_as, client_error_map: dict):
    def deco_func(func):
        @wraps(func)
        def wrapper_func(*args, **kwargs):
            try:
                response = func(*args, **kwargs)
                logger.debug(f'{func.__name__} -> response: {response}')
                return response
            except ClientError as e:
                error_code = e.response['Error']['Code']
                logger.error(f'boto3 client error: {str(e)}, response: {e.response}, error code: {error_code}')
                if exc := client_error_map.get(error_code):
                    raise exc(e)
                raise raise_as()
            except Exception:  # Raise all other exceptions as is
                raise
        return wrapper_func  # true decorator
    return deco_func


def dynamodb_handler(client_err_map: Dict[str, Any], cancellation_err_maps: List[Dict[str, Any]]):
    def deco_func(func):
        @wraps(func)
        def wrapper_func(*args, **kwargs):
            try:
                response = func(*args, **kwargs)
                logger.debug(f'{func.__name__} -> response: {response}')
                return response
            except ClientError as e:
                logger.error(f'ClientError detected -> {e}')
                e_response = db_dynamo.ErrorResponse(e.response)
                if e_response.CancellationReasons:
                    e_response.raise_for_cancellation_reasons(error_maps=cancellation_err_maps)
                if exc := client_err_map.get(e_response.Error.Code):
                    raise exc(e)
                raise
        return wrapper_func  # true decorator
    return deco_func


def lambda_response_handler(raise_as):
    """
    Passes through any exceptions that inherit from the
    :param raise_as:
    :return:
    """
    def deco_func(func):
        @wraps(func)
        def wrapper_func(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except raise_as as e:
                logger.exception(str(e))
                exc = e
            except Exception as e:
                logger.exception(str(e))
                exc = raise_as(e)
            return utils.build_lambda_response(
                status_code=400,
                exc=exc
            )
        return wrapper_func  # true decorator
    return deco_func


def retry(
    retry_exceptions: typing.Tuple,
    tries: int = 4,
    delay: float = 1.5,
    backoff: float = 2.0,
    jitter: float = 0.1
):
    """
    Retry calling the decorated function using an exponential backoff.

    Args:
        :param retry_exceptions: Exceptions to retry on before raise
        :param tries: Number of times to try (not retry) before giving up.
        :param delay: Initial delay between retries in seconds.
        :param backoff: Backoff multiplier (e.g. value of 2.0 will double the delay each retry).
        :param jitter: adds a standard deviation to delay
    """
    def deco_func(func):

        @wraps(func)
        def wrapper_func(*args, **kwargs):
            m_tries = 1
            m_delay = delay
            f_qname = getattr(func, "__qualname__", None)
            while m_tries < tries:
                try:
                    return func(*args, **kwargs)
                except retry_exceptions as e:
                    j_delay = utils.generate_jitter(midpoint=m_delay, floor=0, std_deviation=jitter)
                    logger.info(
                        f'{f_qname!r} -> Exception: {type(e)}, {str(e)}, Tries: {m_tries} / {tries}, Retrying in {j_delay:.3f} seconds...'
                    )
                    utils.sleep(j_delay)
                    m_tries += 1
                    m_delay *= backoff

            logger.warning(f'{f_qname!r} -> Max tries reached: {m_tries} / {tries}')
            return func(*args, **kwargs)

        return wrapper_func  # true decorator

    return deco_func


def http_status_check(reraise_status_codes: typing.Tuple[int, ...] = tuple()):
    def deco_func(func):
        @wraps(func)
        def wrapper_func(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except HTTPStatusError as e:
                status_code = e.response.status_code
                if status_code in reraise_status_codes:     # Retryable status codes
                    raise
                if status_code == codes.UNAUTHORIZED:
                    raise exceptions.NotAuthorizedException(*args, **kwargs, **e.__dict__)
                raise exceptions.APIException(*args, **kwargs, **e.__dict__)

        return wrapper_func

    return deco_func


def wrap_exceptions(raise_as):

    def deco_func(func):

        @wraps(func)
        def wrapper_func(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except raise_as:
                raise
            except Exception as e:
                raise raise_as(*args, **kwargs, **e.__dict__)

        return wrapper_func  # true decorator

    return deco_func
