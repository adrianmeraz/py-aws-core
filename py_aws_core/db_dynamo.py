import os
import typing
from abc import ABC

import boto3
from botocore.config import Config

from py_aws_core import const, entities, logs, secrets_manager, utils

logger = logs.logger

DDB_CLIENT_CONNECT_TIMEOUT = 4.9
DDB_CLIENT_READ_TIMEOUT = 4.9


class DDBClient:
    __config = Config(
        connect_timeout=DDB_CLIENT_CONNECT_TIMEOUT,
        read_timeout=DDB_CLIENT_READ_TIMEOUT,
        retries=dict(
            total_max_attempts=2,
        )
    )
    __ddb_endpoint_url = os.environ.get('DDB_ENDPOINT')
    __ddb_session = boto3.Session()

    @classmethod
    def get_client(cls):
        logger.info(f'Getting new DynamoDB client')
        return cls.__ddb_session.client(
            config=cls.__config,
            service_name='dynamodb',
            endpoint_url=cls.__ddb_endpoint_url
        )

    @classmethod
    def get_table_resource(cls):
        dynamodb = boto3.resource('dynamodb', endpoint_url=cls.__ddb_endpoint_url)
        return dynamodb.Table(cls.get_table_name())

    @classmethod
    def get_table_name(cls):
        return secrets_manager.SecretsManager.get_secrets()['AWS_DYNAMO_DB_TABLE_NAME']

    @classmethod
    def query(cls, *args, **kwargs):
        return cls.get_client().query(*args, **kwargs)

    @classmethod
    def scan(cls, *args, **kwargs):
        return cls.get_client().scan(*args, **kwargs)

    @classmethod
    def get_item(cls, *args, **kwargs):
        return cls.get_client().get_item(*args, **kwargs)

    @classmethod
    def put_item(cls, *args, **kwargs):
        return cls.get_client().put_item(*args, **kwargs)

    @classmethod
    def delete_item(cls, *args, **kwargs):
        return cls.get_client().delete_item(*args, **kwargs)

    @classmethod
    def update_item(cls, *args, **kwargs):
        return cls.get_client().update_item(*args, **kwargs)

    @classmethod
    def batch_write_item(cls, *args, **kwargs):
        return cls.get_client().batch_write_item(*args, **kwargs)

    @classmethod
    def transact_write_items(cls, *args, **kwargs):
        return cls.get_client().transact_write_items(*args, **kwargs)

    @classmethod
    def batch_write_item_maps(cls, item_maps: typing.List[typing.Dict]) -> int:
        table = cls.get_table_resource()
        with table.batch_writer() as batch:
            for _map in item_maps:
                batch.put_item(Item=_map)
        return len(item_maps)

    @classmethod
    def write_maps_to_db(cls, item_maps: typing.List[typing.Dict]) -> int:
        return cls.batch_write_item_maps(item_maps=item_maps)


class QueryResponse(ABC):
    def __init__(self, data):
        self.Items = data.get('Items')
        self.Count = data.get('Count')
        self.ScannedCount = data.get('ScannedCount')
        self.ResponseMetadata = ResponseMetadata(data['ResponseMetadata'])

    def get_by_type(self, _type: const.EntityTypes) -> typing.List:
        if self.Items:
            return [item for item in self.Items if entities.BaseModel(item).Type == _type.value]
        return list()


class ABCCommonAPI(ABC):
    @classmethod
    def get_batch_entity_create_map(
        cls,
        pk: str,
        sk: str,
        _type: str,
        created_by: str = '',
        expire_in_seconds: int = const.DB_DEFAULT_EXPIRES_IN_SECONDS,
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


class DDBItemResponse(ABC):
    def __init__(self, data):
        self._data = data
        self.Type = data.get('__type')
        self.Item = data.get('Item')
        self.ResponseMetadata = ResponseMetadata(data.get('ResponseMetadata', dict()))


class DynamoDBTransactResponse(ABC):
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
