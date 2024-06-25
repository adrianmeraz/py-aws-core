import json
from datetime import datetime, timezone


def build_lambda_response(status_code: int, body: dict | str = None, exc: Exception = None):
    """
      Note - CORS response headers will NOT be present in response if using proxy type integration.
      CORS response headers must be set in lambda response
      See below for further details:
      https://stackoverflow.com/a/54089431
      https://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-cors.html#apigateway-enable-cors-proxy
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
    return {
        'isBase64Encoded': False,
        'statusCode': status_code,
        'body': body,  # body key value must be a json string
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Credentials': True,
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'DELETE,GET,POST,PUT'
        }
    }


def to_iso_8601(dt: datetime = None) -> str:
    # 2020-07-10 15:00:00.000
    if not dt:
        dt = datetime.now(tz=timezone.utc).replace(microsecond=0)
    return dt.isoformat()

