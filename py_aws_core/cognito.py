import typing
from abc import ABC

import boto3
from botocore.config import Config

from py_aws_core import logs
from py_aws_core.secrets_manager import get_secrets_manager

logger = logs.get_logger()
secrets_manager = get_secrets_manager()

COGNITO_CLIENT_CONNECT_TIMEOUT = 4.9
COGNITO_CLIENT_READ_TIMEOUT = 4.9


class CognitoClient:
    __CONFIG = Config(
        connect_timeout=COGNITO_CLIENT_CONNECT_TIMEOUT,
        read_timeout=COGNITO_CLIENT_READ_TIMEOUT,
        retries=dict(
            total_max_attempts=2,
        )
    )
    __boto3_session = boto3.Session()

    def __init__(self):
        self._boto_client = None

    @property
    def boto_client(self):
        if not self._boto_client:
            self._boto_client = self.get_new_client()
        return self._boto_client

    @boto_client.setter
    def boto_client(self, value):
        self._boto_client = value

    @classmethod
    def get_aws_cognito_pool_client_id(cls):
        return secrets_manager.get_secret(secret_name='AWS_COGNITO_POOL_CLIENT_ID')

    @classmethod
    def get_aws_cognito_pool_id(cls):
        return secrets_manager.get_secret(secret_name='AWS_COGNITO_POOL_ID')

    @classmethod
    def get_new_client(cls):
        logger.info(f'Getting new Cognito client')
        return cls.__boto3_session.client(
            config=cls.__CONFIG,
            service_name='cognito-idp',
        )

    def admin_create_user(self, *args, **kwargs):
        return self.boto_client.admin_create_user(*args, **kwargs)

    def initiate_auth(self, *args, **kwargs):
        return self.boto_client.initiate_auth(*args, **kwargs)


class AdminCreateUser:
    class Response:
        class User:
            class MFAOptions:
                def __init__(self, data: dict):
                    self.DeliveryMedium = data.get('DeliveryMedium')
                    self.AttributeName = data.get('AttributeName')

            class Attribute:
                def __init__(self, data: dict):
                    self.Name = data.get('Name')
                    self.Value = data.get('Value')

            def __init__(self, data: dict):
                self.Username = data.get('Username')
                self.Attributes = [self.Attribute(a) for a in data.get('Attributes')]
                self.UserCreateDate = data.get('UserCreateDate')
                self.UserLastModifiedDate = data.get('UserLastModifiedDate')
                self.Enabled = data.get('Enabled')
                self.UserStatus = data.get('UserStatus')
                self.MFAOptions = [self.MFAOptions(mfa) for mfa in data.get('MFAOptions')]

        def __init__(self, data: dict):
            self.User = self.User(data.get('User', dict()))

    @classmethod
    def call(
        cls,
        client: CognitoClient,
        username: str,
        user_attributes: typing.List[typing.Dict],
        desired_delivery_mediums: typing.List[str],
    ):
        response = client.admin_create_user(
            DesiredDeliveryMediums=desired_delivery_mediums,
            Username=username,
            UserAttributes=user_attributes,
            UserPoolId=client.get_aws_cognito_pool_id()
        )
        return cls.Response(response)


class ABCInitiateAuth(ABC):
    class Response:
        class AuthenticationResult:
            class NewDeviceMetadata:
                def __init__(self, data: dict):
                    self.DeviceKey = data.get('DeviceKey', dict())
                    self.DeviceGroupKey = data.get('DeviceGroupKey', dict())

            def __init__(self, data: dict):
                self._data = data
                self.AccessToken = data.get('AccessToken')
                self.ExpiresIn = data.get('ExpiresIn')
                self.TokenType = data.get('TokenType')
                self.RefreshToken = data.get('RefreshToken')
                self.IdToken = data.get('IdToken')
                self.NewDeviceMetadata = self.NewDeviceMetadata(data.get('NewDeviceMetadata', dict()))

        def __init__(self, data: dict):
            self.ChallengeName = data.get('ChallengeName')
            self.Session = data.get('Session')
            self.ChallengeParameters = data.get('ChallengeParameters')
            self.AuthenticationResult = self.AuthenticationResult(data['AuthenticationResult'])


class UserPasswordAuth(ABCInitiateAuth):
    @classmethod
    def call(
        cls,
        client: CognitoClient,
        username: str,
        password: str,
    ):
        response = client.initiate_auth(
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password,
            },
            ClientId=client.get_aws_cognito_pool_client_id(),
        )
        return cls.Response(response)


class RefreshTokenAuth(ABCInitiateAuth):
    @classmethod
    def call(
        cls,
        client: CognitoClient,
        refresh_token: str,
    ):
        response = client.initiate_auth(
            AuthFlow='REFRESH_TOKEN',
            AuthParameters={
                'REFRESH_TOKEN': refresh_token,
            },
            ClientId=client.get_aws_cognito_pool_client_id(),
        )
        return cls.Response(response)
