import typing
from abc import ABC

import boto3
from botocore.config import Config

from . import logs, secrets_manager

logger = logs.logger

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

    def __init__(self):
        self.boto_client = self.get_cognito_idp_client()

    @classmethod
    def get_cognito_idp_client(cls):
        logger.info(f'Getting new Cognito client')
        return boto3.Session().client(
            config=cls.__CONFIG,
            service_name='cognito-idp',
        )

    @classmethod
    def aws_cognito_pool_client_id(cls):
        return secrets_manager.SecretsManager.get_secrets()['AWS_COGNITO_POOL_CLIENT_ID']

    @classmethod
    def aws_cognito_pool_id(cls):
        return secrets_manager.SecretsManager.get_secrets()['AWS_COGNITO_POOL_ID']

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
            UserPoolId=client.aws_cognito_pool_id()
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
            ClientId=client.aws_cognito_pool_client_id(),
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
            ClientId=client.aws_cognito_pool_client_id(),
        )
        return cls.Response(response)