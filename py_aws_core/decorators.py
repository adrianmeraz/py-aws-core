import logging
from functools import wraps
from typing import Any, Dict, List

from botocore.exceptions import ClientError

from . import dynamodb

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
                logger.error(f'boto3 client error response: {e.response}, error code: {error_code}')
                if exc := client_error_map.get(error_code):
                    raise exc(e)
                raise raise_as(str(e), error=error_code)
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
                    return e_response.raise_for_cancellation_reasons(error_maps=cancellation_err_maps)
                if exc := client_err_map.get(e_response.Error.Code):
                    raise exc(e)
            raise  # Raise all other exceptions as is
        return wrapper_func  # true decorator
    return deco_func
