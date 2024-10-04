import typing
from abc import ABC
from dataclasses import dataclass

import boto3
from boto3.dynamodb import types
from botocore.config import Config

from py_aws_core import const, logs, utils
from .secrets_manager import get_secrets_manager

secrets_manager = get_secrets_manager()

logger = logs.get_logger()

DDB_CLIENT_CONNECT_TIMEOUT = 4.9
DDB_CLIENT_READ_TIMEOUT = 4.9


class DDBClient:
    __config = Config(
        connect_timeout=DDB_CLIENT_CONNECT_TIMEOUT,
        read_timeout=DDB_CLIENT_READ_TIMEOUT,
        tcp_keepalive=True,  # Keep TCP connections open for faster response
        retries=dict(
            total_max_attempts=2,
        )
    )
    __boto3_session = boto3.Session()

    def __init__(self):
        self._boto_client = None
        self._table_resource = None

    @property
    def boto_client(self):
        if not self._boto_client:
            self._boto_client = self.get_new_client()
        return self._boto_client

    @boto_client.setter
    def boto_client(self, value):
        self._boto_client = value

    @property
    def table_resource(self):
        if not self._table_resource:
            self._table_resource = self.get_new_table_resource()
        return self._table_resource

    @classmethod
    def get_new_client(cls):
        logger.info(f'Getting new DynamoDB client')
        return cls.__boto3_session.client(
            config=cls.__config,
            service_name='dynamodb',
            verify=False  # Don't validate SSL certs for faster responses
        )

    @classmethod
    def get_table_name(cls):
        return secrets_manager.get_secret(secret_name='AWS_DYNAMO_DB_TABLE_NAME')

    def get_new_table_resource(self):
        dynamodb = boto3.resource('dynamodb')
        return dynamodb.Table(self.get_table_name())

    def query(self, *args, **kwargs):
        return self.boto_client.query(TableName=self.get_table_name(), *args, **kwargs)

    def scan(self, *args, **kwargs):
        return self.boto_client.scan(TableName=self.get_table_name(), *args, **kwargs)

    def get_item(self, *args, **kwargs):
        return self.boto_client.get_item(TableName=self.get_table_name(), *args, **kwargs)

    def put_item(self, *args, **kwargs):
        return self.boto_client.put_item(TableName=self.get_table_name(), *args, **kwargs)

    def delete_item(self, *args, **kwargs):
        return self.boto_client.delete_item(TableName=self.get_table_name(), *args, **kwargs)

    def update_item(self, *args, **kwargs):
        return self.boto_client.update_item(TableName=self.get_table_name(), *args, **kwargs)

    def batch_write_item(self, *args, **kwargs):
        return self.boto_client.batch_write_item(*args, **kwargs)

    def transact_write_items(self, *args, **kwargs):
        return self.boto_client.transact_write_items(*args, **kwargs)

    def batch_write_item_maps(self, item_maps: typing.List[typing.Dict]) -> int:
        with self.table_resource.batch_writer() as batch:
            for _map in item_maps:
                batch.put_item(Item=_map)
        return len(item_maps)

    def write_maps_to_db(self, item_maps: typing.List[typing.Dict]) -> int:
        return self.batch_write_item_maps(item_maps=item_maps)


__db_client = DDBClient()


def get_db_client():
    """
    Reuses db client across all modules for efficiency
    :return:
    """
    return __db_client


class ABCCommonAPI(ABC):
    """
        https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Expressions.ConditionExpressions.html
        If your primary key consists of both a partition key(pk) and a sort key(sk),
        the parameter will check whether attribute_not_exists(pk) AND attribute_not_exists(sk) evaluate to true or
        false before attempting the write operation.
    """
    @classmethod
    def get_batch_entity_create_map(
        cls,
        pk: str,
        sk: str,
        _type: str,
        created_by: str = '',
        expire_in_seconds: int | None = const.DB_DEFAULT_EXPIRES_IN_SECONDS,
        **kwargs,
    ):
        return {
            'PK': pk,
            'SK': sk,
            'Type': _type,
            'CreatedAt': cls.iso_8601_now_timestamp(),
            'CreatedBy': created_by,
            'ModifiedAt': '',
            'ModifiedBy': '',
            'ExpiresAt': cls.calc_expire_at_timestamp(expire_in_seconds=expire_in_seconds),
        } | kwargs

    @classmethod
    def get_entity_update_map(
        cls,
        pk: str,
        sk: str,
        modified_by: str = '',
        **kwargs,
    ):
        return {
            'PK': pk,
            'SK': sk,
            'ModifiedAt': cls.iso_8601_now_timestamp(),
            'ModifiedBy': modified_by,
        } | kwargs

    @classmethod
    def get_put_item_map(
        cls,
        pk: str,
        sk: str,
        _type: str,
        created_by: str = '',
        expire_in_seconds: int | None = const.DB_DEFAULT_EXPIRES_IN_SECONDS,
        **kwargs,
    ):
        vals = {
           'PK': pk,
           'SK': sk,
           'Type': _type,
           'CreatedAt': cls.iso_8601_now_timestamp(),
           'CreatedBy': created_by,
           'ModifiedAt': '',
           'ModifiedBy': '',
           'ExpiresAt': cls.calc_expire_at_timestamp(expire_in_seconds=expire_in_seconds),
        } | kwargs
        return cls.serialize_types(vals)

    @staticmethod
    def serialize_types(data: dict):
        """
        Converts normalized json to low level dynamo json
        """
        return {k: types.TypeSerializer().serialize(v) for k, v in data.items()}

    @staticmethod
    def deserialize_types(data: dict):
        """
        Converts low level dynamo json to normalized json
        """
        return {k: types.TypeDeserializer().deserialize(v) for k, v in data.items()}

    @classmethod
    def iso_8601_now_timestamp(cls) -> str:
        return utils.to_iso_8601()

    @classmethod
    def calc_expire_at_timestamp(cls, expire_in_seconds: int = None) -> int | str:
        """
        Adds seconds to current unix timestamp to generate new unix timestamp
        Seconds set to None will result in empty string
        :param expire_in_seconds: Seconds to add to current timestamp
        :return:
        """
        if expire_in_seconds is None:
            return ''
        return utils.add_seconds_to_current_unix_timestamp(seconds=expire_in_seconds)

    @dataclass
    class UpdateField:
        expression_attr: str
        set_once: bool = False

    @staticmethod
    def build_update_expression(fields: typing.List[UpdateField]):
        n_fields = [f'#{f.expression_attr} = :{f.expression_attr}' for f in fields if not f.set_once]
        o_fields = [f'#{f.expression_attr} = if_not_exists(#{f.expression_attr}, :{f.expression_attr})' for f in fields if f.set_once]
        return f'SET {', '.join(n_fields + o_fields)}'


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

    def raise_for_cancellation_reasons(self, error_maps: typing.List[typing.Dict[str, typing.Any]]):
        for reason, error_map in zip(self.CancellationReasons, error_maps):
            if exc := error_map.get(reason.Code):
                raise exc


class DDBItemResponse:
    def __init__(self, data):
        self.Item = data.get('Item')
        self.ResponseMetadata = ResponseMetadata(data.get('ResponseMetadata', dict()))


class QueryResponse:
    def __init__(self, data):
        self._items = data.get('Items') or list()
        self.count = data.get('Count')
        self.scanned_count = data.get('ScannedCount')
        self.response_metadata = ResponseMetadata(data['ResponseMetadata'])

    def get_by_type(self, _type: str) -> typing.List:
        if self._items:
            return [i for i in self._items if i['Type']['S'] == _type]
        return list()


class UpdateItemResponse:
    def __init__(self, data: typing.Dict):
        self.attributes = data['Attributes']


class DynamoDBTransactResponse:
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
