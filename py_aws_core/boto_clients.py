from abc import ABC, abstractmethod

import boto3
from botocore.config import Config


class ABCBotoClient(ABC):
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

    @classmethod
    @abstractmethod
    def new_client(cls, **kwargs):
        pass


class CognitoClient(ABCBotoClient):
    @classmethod
    def new_client(cls):
        return cls._boto3_session.client(
            config=cls._get_config(),
            service_name='cognito-idp',
        )


class DynamoTable(ABCBotoClient):
    @classmethod
    def new_client(cls, table_name: str):
        return cls._boto3_session.resource(
            service_name='dynamodb',
            config=cls._get_config()
        ).Table(table_name)


class DynamoDBClient(ABCBotoClient):
    @classmethod
    def new_client(cls):
        return cls._boto3_session.client(
            config=cls._get_config(),
            service_name='dynamodb',
            verify=False  # Don't validate SSL certs for faster responses
        )


class SecretManagerClient(ABCBotoClient):
    @classmethod
    def new_client(cls):
        return cls._boto3_session.client(
            config=cls._get_config(),
            service_name='secretsmanager',
        )


class SSMClient(ABCBotoClient):
    @classmethod
    def new_client(cls):
        return cls._boto3_session.client(
            config=cls._get_config(),
            service_name='ssm',
        )
