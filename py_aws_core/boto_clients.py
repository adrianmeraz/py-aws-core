from abc import ABC, abstractmethod

import boto3
from botocore.client import BaseClient
from botocore.config import Config


class ABCBotoClientFactory(ABC):
    CLIENT_CONNECT_TIMEOUT = 4.9
    CLIENT_READ_TIMEOUT = 4.9

    _boto3_session = boto3.Session()

    @classmethod
    @abstractmethod
    def new_client(cls, **kwargs) -> BaseClient:
        pass

    @classmethod
    def _get_config(cls):
        return Config(
            connect_timeout=cls.CLIENT_CONNECT_TIMEOUT,
            read_timeout=cls.CLIENT_READ_TIMEOUT,
            retries=dict(
                total_max_attempts=2,
            )
        )


class CognitoClientFactory(ABCBotoClientFactory):
    @classmethod
    def new_client(cls):
        return cls._boto3_session.client(
            config=cls._get_config(),
            service_name='cognito-idp',
        )


class DynamoTableFactory(ABCBotoClientFactory):
    @classmethod
    def new_client(cls, table_name: str):
        return cls._boto3_session.resource(
            service_name='dynamodb',
            config=cls._get_config()
        ).Table(table_name)


class DynamoDBClientFactory(ABCBotoClientFactory):
    @classmethod
    def new_client(cls):
        return cls._boto3_session.client(
            config=cls._get_config(),
            service_name='dynamodb',
            verify=False  # Don't validate SSL certs for faster responses
        )


class SecretManagerClientFactory(ABCBotoClientFactory):
    @classmethod
    def new_client(cls):
        return cls._boto3_session.client(
            config=cls._get_config(),
            service_name='secretsmanager',
        )


class SSMClientFactory(ABCBotoClientFactory):
    @classmethod
    def new_client(cls):
        return cls._boto3_session.client(
            config=cls._get_config(),
            service_name='ssm',
        )

