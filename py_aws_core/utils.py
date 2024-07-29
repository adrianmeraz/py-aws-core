import json
import random
import time
import typing
import uuid
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
        dt = get_now_datetime(tz=tz).replace(microsecond=0)
    return dt.isoformat()


def add_seconds_to_current_unix_timestamp(seconds: int, tz=timezone.utc) -> int:
    dt = get_now_datetime(tz=tz) + timedelta(seconds=seconds)
    return int(dt.timestamp())


def add_seconds_to_now_datetime(seconds: int, tz=timezone.utc) -> datetime:
    return get_now_datetime(tz=tz) + timedelta(seconds=seconds)


def get_now_datetime(tz=timezone.utc) -> datetime:
    return datetime.now(tz=tz)


def generate_jitter(midpoint: float, floor: float, std_deviation: float) -> float:
    return max(floor, midpoint + random.uniform(-std_deviation, +std_deviation))


def rand_int(num_a: int, num_b: int) -> int:
    return random.randint(num_a, num_b)


def sleep(seconds: float) -> None:
    return time.sleep(seconds)


def get_uuid() -> uuid.UUID:
    return uuid.uuid4()


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


def remove_whitespace(s: str) -> str:
    return ''.join([line.replace(' ', '') for line in s.split('\\r\\n')])
