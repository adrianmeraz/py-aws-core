import json
import random
import typing
from datetime import datetime, timezone, timedelta, UTC


def build_lambda_response(
    status_code: int,
    body: typing.Dict | str = None,
    multi_value_headers: typing.Dict[str, typing.List[str]] = None,
    exc: Exception = None
):
    """
      Note - CORS response headers will NOT be present in response if using proxy type integration.
      CORS response headers must be set in lambda response
      See below for further details:
      https://stackoverflow.com/a/54089431
      https://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-cors.html#apigateway-enable-cors-proxy
    :param multi_value_headers:
    :param status_code:
    :param body:
    :param exc:
    :return:
    """
    if not body:
        body = dict()
    if exc:
        body['error'] = f'{type(exc).__name__}: {str(exc)}'
    if isinstance(body, dict):
        body = json.dumps(body)
    response_headers = {
        'Content-Type': ['application/json'],
        'Access-Control-Allow-Credentials': [True],
        'Access-Control-Allow-Headers': ['Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'],
        'Access-Control-Allow-Origin': ['*'],
        'Access-Control-Allow-Methods': ['DELETE,GET,POST,PUT']
    }
    if multi_value_headers:
        response_headers |= multi_value_headers
    return {
        'isBase64Encoded': False,
        'statusCode': status_code,
        'body': body,  # body key value must be a json string
        'multiValueHeaders': response_headers
    }


def to_iso_8601(dt: datetime = None, tz=timezone.utc) -> str:
    """
    Example output 2020-07-10 15:00:00.000
    :param tz:
    :param dt:
    :return:
    """
    if not dt:
        dt = get_now_timestamp(tz=tz).replace(microsecond=0)
    return dt.isoformat()


def add_days_to_current_unix_timestamp(days: int, tz=timezone.utc) -> int:
    dt = get_now_timestamp(tz=tz) + timedelta(days=days)
    return int(dt.timestamp())


def get_now_timestamp(tz=timezone.utc):
    return datetime.now(tz=tz)


def rand_int(num_a: int, num_b: int) -> int:
    return random.randint(num_a, num_b)


def decode_unicode(s: str) -> str:
    """
    Per https://stackoverflow.com/a/33134946
    This is how to fix unicode decoding errors
    :param s: string to decode
    :return:
    """
    try:
        return s.encode('iso-8859-1').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s


def unix_timestamp_to_iso8601(unix_ts: int):
    return datetime.fromtimestamp(unix_ts, tz=UTC).isoformat()
