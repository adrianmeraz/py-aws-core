from abc import ABC, abstractmethod

import boto3
from botocore.config import Config
from . secrets_interface import IDynamoDBSecrets


class ABCBotoClientFactory(ABC):
    CLIENT_CONNECT_TIMEOUT = 4.9
    CLIENT_READ_TIMEOUT = 4.9

    _boto3_session = boto3.Session()

    @classmethod
    def _get_config(cls):
        return Config(
            connect_timeout=cls.CLIENT_CONNECT_TIMEOUT,
            read_timeout=cls.CLIENT_READ_TIMEOUT,
            retries=dict(
                total_max_attempts=2,
            )
        )

    @abstractmethod
    def new_client(self, **kwargs):
        pass


class CognitoClientFactory(ABCBotoClientFactory):
    def new_client(self):
        return self._boto3_session.client(
            config=self._get_config(),
            service_name='cognito-idp',
        )


class DynamoTable(ABCBotoClientFactory):
    def __init__(self, ddb_secrets: IDynamoDBSecrets):
        self._ddb_secrets = ddb_secrets

    def new_client(self):
        return self._boto3_session.resource(
            service_name='dynamodb',
            config=self._get_config()
        ).Table(self._ddb_secrets.get_table_name())


class DynamoDBClientFactory(ABCBotoClientFactory):
    def new_client(self):
        return self._boto3_session.client(
            config=self._get_config(),
            service_name='dynamodb',
            verify=False  # Don't validate SSL certs for faster responses
        )


class SecretManagerClientFactory(ABCBotoClientFactory):
    def new_client(self):
        return self._boto3_session.client(
            config=self._get_config(),
            service_name='secretsmanager',
        )


class SSMClientFactory(ABCBotoClientFactory):
    def new_client(self):
        return self._boto3_session.client(
            config=self._get_config(),
            service_name='ssm',
        )
