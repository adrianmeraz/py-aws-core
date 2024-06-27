import logging
from functools import wraps
from typing import Any, Dict, List

from botocore.exceptions import ClientError

from . import dynamodb, utils

logger = logging.getLogger(__name__)


def boto3_handler(raise_as, client_error_map: dict):
    def deco_func(func):
        @wraps(func)
        def wrapper_func(*args, **kwargs):
            try:
                response = func(*args, **kwargs)
                logger.debug(f'{__name__}, response: {response}')
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
                logger.debug(f'{func.__name__}, response: {response}')
                return response
            except ClientError as e:
                logger.error(f'ClientError detected: {e}')
                e_response = dynamodb.ErrorResponse(e.response)
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
