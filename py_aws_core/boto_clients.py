from botocore.config import Config
import boto3

from abc import ABC, abstractmethod


class ABCBotoClientFactory(ABC):
    CLIENT_CONNECT_TIMEOUT = 4.9
    CLIENT_READ_TIMEOUT = 4.9

    __boto3_session = boto3.Session()

    @abstractmethod
    def new_client(self) -> dict:
        pass

    @classmethod
    def client_connect_timeout(cls):
        return cls.CLIENT_CONNECT_TIMEOUT

    @classmethod
    def client_read_timeout(cls):
        return cls.CLIENT_READ_TIMEOUT


class DynamoDBClientFactory(ABCBotoClientFactory):
    def new_client(self):
        return self.__boto3_session.client(
            config=self.get_config(),
            service_name='dynamodb',
            verify=False  # Don't validate SSL certs for faster responses
        )

    def get_config(self):
        return Config(
            connect_timeout=self.CLIENT_CONNECT_TIMEOUT,
            read_timeout=self.CLIENT_READ_TIMEOUT,
            retries=dict(
                total_max_attempts=2,
            )
        )
