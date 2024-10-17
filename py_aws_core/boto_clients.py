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
    def new_client(cls) -> BaseClient:
        pass

    @classmethod
    @abstractmethod
    def service_name(cls) -> str:
        pass

    @classmethod
    def get_config(cls):
        return Config(
            connect_timeout=cls.CLIENT_CONNECT_TIMEOUT,
            read_timeout=cls.CLIENT_READ_TIMEOUT,
            retries=dict(
                total_max_attempts=2,
            )
        )

    @classmethod
    def new_resource_client(cls):
        return cls._boto3_session.resource(service_name=cls.service_name())


class CognitoClientFactory(ABCBotoClientFactory):
    @classmethod
    def new_client(cls):
        return cls._boto3_session.client(
            config=cls.get_config(),
            service_name=cls.service_name(),
        )

    @classmethod
    def service_name(cls) -> str:
        return 'cognito-idp'


class DynamoDBClientFactory(ABCBotoClientFactory):
    @classmethod
    def new_client(cls):
        return cls._boto3_session.client(
            config=cls.get_config(),
            service_name=cls.service_name(),
            verify=False  # Don't validate SSL certs for faster responses
        )

    @classmethod
    def service_name(cls) -> str:
        return 'dynamodb'


class SecretManagerClientFactory(ABCBotoClientFactory):
    @classmethod
    def new_client(cls):
        return cls._boto3_session.client(
            service_name=cls.service_name(),
        )

    @classmethod
    def service_name(cls) -> str:
        return 'secretsmanager'
