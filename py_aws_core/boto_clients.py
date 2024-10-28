from abc import ABC

import boto3
from botocore.client import BaseClient
from botocore.config import Config

from .secrets_interface import IDynamoDBSecrets


class ABCBotoSession(ABC):
    CLIENT_CONNECT_TIMEOUT = 4.9
    CLIENT_READ_TIMEOUT = 4.9

    _boto3_session = boto3.Session()

    @classmethod
    def _get_config(cls, **kwargs):
        return Config(
            connect_timeout=cls.CLIENT_CONNECT_TIMEOUT,
            read_timeout=cls.CLIENT_READ_TIMEOUT,
            retries=dict(
                total_max_attempts=2,
            ),
            **kwargs
        )


class ABCBotoClient(ABCBotoSession):
    def __init__(self, service_name: str, verify: bool = True, **kwargs):
        self._boto_client = self._get_new_client(
            service_name=service_name,
            verify=verify,
            **kwargs
        )

    def _get_new_client(self, service_name: str, verify: bool, **kwargs) -> BaseClient:
        return self._boto3_session.client(
            config=self._get_config(),
            service_name=service_name,
            **kwargs
        )

    @property
    def boto_client(self) -> BaseClient:
        return self._boto_client


class ABCBotoResource(ABCBotoSession):
    def __init__(self, service_name: str, **kwargs):
        self._boto_resource = self._get_new_resource(
            service_name=service_name,
            **kwargs
        )

    def _get_new_resource(self, service_name: str, **kwargs) -> BaseClient:
        return self._boto3_session.resource(
            config=self._get_config(),
            service_name=service_name,
            **kwargs
        )

    @property
    def boto_resource(self) -> BaseClient:
        return self._boto_resource


class CognitoClient(ABCBotoClient):
    def __init__(self):
        super().__init__(service_name='cognito-idp')


class SecretManagerClient(ABCBotoClient):
    def __init__(self):
        super().__init__(service_name='secretsmanager')


class SSMClient(ABCBotoClient):
    def __init__(self):
        super().__init__(service_name='ssm')


class DynamoTable(ABCBotoResource):
    def __init__(self, ddb_secrets: IDynamoDBSecrets):
        super().__init__(service_name='dynamodb')
        self._ddb_secrets = ddb_secrets

    @property
    def client(self):
        return self.table.meta.client

    @property
    def table(self):
        return self.boto_resource.Table(self.table_name)

    @property
    def table_name(self):
        return self._ddb_secrets.get_table_name()
