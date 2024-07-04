import os
from abc import ABC
from typing import Any, Dict, List

import boto3
from botocore.config import Config

from . import logs, secrets_manager, utils

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
    def get_table_name(cls):
        return secrets_manager.SecretsManager.get_secrets()['AWS_DYNAMO_DB_TABLE_NAME']

    @classmethod
    def query(cls, *args, **kwargs):
        return cls.get_client().query(*args, **kwargs)

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


class ABCCommonAPI(ABC):

    @classmethod
    def iso_8601_now_timestamp(cls) -> str:
        return utils.to_iso_8601()


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

    def raise_for_cancellation_reasons(self, error_maps: List[Dict[str, Any]]):
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
