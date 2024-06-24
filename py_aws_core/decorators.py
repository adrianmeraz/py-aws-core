import logging
from functools import wraps
from typing import Any, Dict, List

from botocore.exceptions import ClientError

from . import dynamodb

logger = logging.getLogger(__name__)


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
