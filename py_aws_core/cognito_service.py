import typing
from abc import ABC

from botocore.client import BaseClient

from py_aws_core import logs

logger = logs.get_logger()


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
        boto_client: BaseClient,
        cognito_pool_id: str,
        username: str,
        user_attributes: typing.List[typing.Dict],
        desired_delivery_mediums: typing.List[str],
    ):
        response = boto_client.admin_create_user(
            DesiredDeliveryMediums=desired_delivery_mediums,
            Username=username,
            UserAttributes=user_attributes,
            UserPoolId=cognito_pool_id
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
        boto_client: BaseClient,
        cognito_pool_client_id: str,
        username: str,
        password: str,

    ):
        response = boto_client.initiate_auth(
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password,
            },
            ClientId=cognito_pool_client_id,
        )
        return cls.Response(response)


class RefreshTokenAuth(ABCInitiateAuth):
    @classmethod
    def call(
        cls,
        boto_client: BaseClient,
        cognito_pool_client_id: str,
        refresh_token: str,
    ):
        response = boto_client.initiate_auth(
            AuthFlow='REFRESH_TOKEN',
            AuthParameters={
                'REFRESH_TOKEN': refresh_token,
            },
            ClientId=cognito_pool_client_id,
        )
        return cls.Response(response)
