import typing
from dataclasses import dataclass

import boto3
from boto3.dynamodb.table import TableResource
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
from botocore.client import BaseClient

from py_aws_core import const, decorators, entities, exceptions, logs, utils

logger = logs.get_logger()


@dataclass
class UpdateField:
    expression_attr: str
    set_once: bool = False


def build_update_expression(fields: list[UpdateField]) -> str:
    n_fields = [f'#{f.expression_attr} = :{f.expression_attr}' for f in fields if not f.set_once]
    o_fields = [f'#{f.expression_attr} = if_not_exists(#{f.expression_attr}, :{f.expression_attr})' for f in fields
                if f.set_once]
    return f'SET {', '.join(n_fields + o_fields)}'


def get_batch_entity_create_map(
    cls,
    pk: str,
    sk: str,
    _type: str,
    created_by: str = '',
    expire_in_seconds: int | None = const.DB_DEFAULT_EXPIRES_IN_SECONDS,
    **kwargs,
) -> dict:
    return {
        'PK': pk,
        'SK': sk,
        'Type': _type,
        'CreatedAt': utils.to_iso_8601(),
        'CreatedBy': created_by,
        'ModifiedAt': '',
        'ModifiedBy': '',
        'ExpiresAt': cls.calc_expire_at_timestamp(expire_in_seconds=expire_in_seconds),
    } | kwargs


def get_entity_update_map(
    pk: str,
    sk: str,
    modified_by: str = '',
    **kwargs,
) -> dict:
    return {
        'PK': pk,
        'SK': sk,
        'ModifiedAt': utils.to_iso_8601(),
        'ModifiedBy': modified_by,
    } | kwargs


def get_put_item_map(
    pk: str,
    sk: str,
    _type: str,
    created_by: str = '',
    expire_in_seconds: int | None = const.DB_DEFAULT_EXPIRES_IN_SECONDS,
    **kwargs,
) -> dict:
    vals = {
       'PK': pk,
       'SK': sk,
       'Type': _type,
       'CreatedAt': utils.to_iso_8601(),
       'CreatedBy': created_by,
       'ModifiedAt': '',
       'ModifiedBy': '',
       'ExpiresAt': calc_expire_at_timestamp(expire_in_seconds=expire_in_seconds),
    } | kwargs
    return serialize_types(vals)


def batch_write_item_maps(table_resource: TableResource, item_maps: list[dict]) -> int:
    with table_resource.batch_writer() as batch:
        for _map in item_maps:
            batch.put_item(Item=_map)
    return len(item_maps)


def get_new_table_resource(table_name: str) -> TableResource:
    resource = boto3.resource('dynamodb')
    return resource.Table(table_name)


def serialize_types(data: dict):
    """
    Converts normalized json to low level dynamo json
    """
    return {k: TypeSerializer().serialize(v) for k, v in data.items()}


def deserialize_types(data: dict):
    """
    Converts low level dynamo json to normalized json
    """
    return {k: TypeDeserializer().deserialize(v) for k, v in data.items()}


def calc_expire_at_timestamp(expire_in_seconds: int = None) -> int | str:
    """
    Adds seconds to current unix timestamp to generate new unix timestamp
    Seconds set to None will result in empty string
    :param expire_in_seconds: Seconds to add to current timestamp
    :return:
    """
    if expire_in_seconds is None:
        return ''
    return utils.add_seconds_to_current_unix_timestamp(seconds=expire_in_seconds)


class ErrorResponse:
    class Error:
        def __init__(self, data):
            self.Message = data['Message']
            self.Code = data['Code']

    class CancellationReason:
        def __init__(self, data):
            self.Code = data['Code']
            self.Message = data.get('Message')

    def __init__(self, data):
        self.Error = self.Error(data.get('Error', dict()))
        self.ResponseMetadata = ResponseMetadata(data.get('ResponseMetadata', dict()))
        self.Message = data.get('Message')
        self.CancellationReasons = [self.CancellationReason(r) for r in data.get('CancellationReasons', list())]

    def raise_for_cancellation_reasons(self, error_maps: list[dict[str, typing.Any]]):
        for reason, error_map in zip(self.CancellationReasons, error_maps):
            if exc := error_map.get(reason.Code):
                raise exc


class ItemResponse:
    def __init__(self, data):
        self.Item = data.get('Item')
        self.ResponseMetadata = ResponseMetadata(data.get('ResponseMetadata', dict()))


class QueryResponse:
    def __init__(self, data):
        self._items = data.get('Items') or list()
        self.count = data.get('Count')
        self.scanned_count = data.get('ScannedCount')
        self.response_metadata = ResponseMetadata(data['ResponseMetadata'])

    def get_by_type(self, _type: str) -> list:
        if self._items:
            return [i for i in self._items if i['Type']['S'] == _type]
        return list()


class UpdateItemResponse:
    def __init__(self, data: dict):
        self.attributes = data['Attributes']


class TransactionResponse:
    def __init__(self, data):
        self._data = data
        self.Responses = data.get('Responses')

    @property
    def data(self):
        return self._data


class ResponseMetadata:
    class HTTPHeaders:
        def __init__(self, data):
            self.server = data.get('server')
            self.date = data.get('date')

    def __init__(self, data):
        self.RequestId = data.get('RequestId')
        self.HTTPStatusCode = data.get('HTTPStatusCode')
        self.HTTPHeaders = self.HTTPHeaders(data.get('HTTPHeaders', dict()))
        self.RetryAttempts = data.get('RetryAttempts')


class GetOrCreateSession:
    class Response(UpdateItemResponse):
        @property
        def session(self) -> entities.Session:
            return entities.Session(data=self.attributes)

    @decorators.dynamodb_handler(client_err_map=exceptions.ERR_CODE_MAP, cancellation_err_maps=[])
    def call(
        self,
        boto_client: BaseClient,
        table_name: str,
        session_id: str,
        created_at_datetime: str,
        expires_at: int = None
    ):
        pk = sk = entities.Session.create_key(_id=session_id)
        _type = entities.Session.type()
        update_fields = [
            UpdateField(expression_attr='ty'),
            UpdateField(expression_attr='si'),
            UpdateField(expression_attr='ma'),
            UpdateField(expression_attr='ea', set_once=True),
            UpdateField(expression_attr='ca', set_once=True),
        ]
        response = boto_client.update_item(
            TableName=table_name,
            Key=serialize_types({
                'PK': pk,
                'SK': sk,
            }),
            UpdateExpression=build_update_expression(update_fields),
            ExpressionAttributeNames={
                '#ty': 'Type',
                "#si": 'SessionId',
                '#ca': 'CreatedAt',
                '#ma': 'ModifiedAt',
                '#ea': 'ExpiresAt',
            },
            ExpressionAttributeValues=serialize_types({
                ':ty': _type,
                ':si': session_id,
                ':ca': created_at_datetime,
                ':ma': created_at_datetime,
                ':ea': expires_at,
            }),
            ReturnValues='ALL_NEW'
        )

        logger.debug(f'response: {response}')
        return self.Response(response)


class GetSessionItem:
    class Response(ItemResponse):
        @property
        def session(self) -> entities.Session:
            return entities.Session(data=self.Item)

    @decorators.dynamodb_handler(client_err_map=exceptions.ERR_CODE_MAP, cancellation_err_maps=[])
    def call(
        self,
        boto_client: BaseClient,
        table_name: str,
        session_id: str
    ) -> Response:
        pk = sk = entities.Session.create_key(_id=session_id)
        response = boto_client.get_item(
            TableName=table_name,
            Key=serialize_types({
                'PK': pk,
                'SK': sk
            }),
            ExpressionAttributeNames={
                "#pk": "PK",
                "#bc": "Base64Cookies",
                "#tp": "Type"
            },
            ProjectionExpression='#pk, #bc, #tp'
        )
        logger.debug(f'response: {response}')
        return self.Response(response)


class PutSession:
    @decorators.dynamodb_handler(client_err_map=exceptions.ERR_CODE_MAP, cancellation_err_maps=[])
    def call(
        self,
        boto_client: BaseClient,
        table_name: str,
        session_id: str,
        b64_cookies: bytes
    ):
        pk = sk = entities.Session.create_key(_id=session_id)
        _type = entities.Session.type()
        item = get_put_item_map(
            pk=pk,
            sk=sk,
            _type=_type,
            expire_in_seconds=None,
            Base64Cookies=b64_cookies,
            SessionId=session_id
        )
        response = boto_client.put_item(
            TableName=table_name,
            Item=item,
        )
        logger.debug(f'response: {response}')
        return response


class UpdateSessionCookies:
    class Response(UpdateItemResponse):
        @property
        def session(self) -> entities.Session:
            return entities.Session(self.attributes)

    @decorators.dynamodb_handler(client_err_map=exceptions.ERR_CODE_MAP, cancellation_err_maps=[])
    def call(
        self,
        boto_client: BaseClient,
        table_name: str,
        session_id: str,
        b64_cookies: bytes,
        now_datetime: str
    ):
        pk = sk = entities.Session.create_key(_id=session_id)
        response = boto_client.update_item(
            TableName=table_name,
            Key=serialize_types({
                'PK': pk,
                'SK': sk,
            }),
            UpdateExpression='SET #b64 = :b64, #mda = :mda',
            ExpressionAttributeNames={
                '#b64': 'Base64Cookies',
                '#mda': 'ModifiedAt',
            },
            ExpressionAttributeValues={
                ':b64': {'B': b64_cookies},
                ':mda': {'S': now_datetime}
            },
            ReturnValues='ALL_NEW'
        )
        logger.debug(f'response: {response}')
        return self.Response(response)
