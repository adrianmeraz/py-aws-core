import typing
from abc import ABC
from dataclasses import dataclass
from enum import Enum

from botocore.client import BaseClient

from py_aws_core import decorators, exceptions, logs, mixins

logger = logs.get_logger()


class AuthChallenge(Enum):
    SMS_MFA = 'SMS_MFA'
    EMAIL_OTP = 'EMAIL_OTP'
    SOFTWARE_TOKEN_MFA = 'SOFTWARE_TOKEN_MFA'
    SELECT_MFA_TYPE = 'SELECT_MFA_TYPE'
    MFA_SETUP = 'MFA_SETUP'
    PASSWORD_VERIFIER = 'PASSWORD_VERIFIER'
    CUSTOM_CHALLENGE = 'CUSTOM_CHALLENGE'
    DEVICE_SRP_AUTH = 'DEVICE_SRP_AUTH'
    DEVICE_PASSWORD_VERIFIER = 'DEVICE_PASSWORD_VERIFIER'
    ADMIN_NO_SRP_AUTH = 'ADMIN_NO_SRP_AUTH'
    NEW_PASSWORD_REQUIRED = 'NEW_PASSWORD_REQUIRED'


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
    @decorators.boto3_handler(raise_as=exceptions.CognitoException)
    def call(
        cls,
        cognito_client: BaseClient,
        cognito_pool_id: str,
        username: str,
        user_attributes: typing.List[typing.Dict],
        desired_delivery_mediums: typing.List[str],
    ):
        response = cognito_client.admin_create_user(
            DesiredDeliveryMediums=desired_delivery_mediums,
            Username=username,
            UserAttributes=user_attributes,
            UserPoolId=cognito_pool_id
        )
        logger.info('Cognito AdminCreateUser called', response=response)
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
            self.AuthenticationResult = self.AuthenticationResult(data.get('AuthenticationResult', dict()))


class UserPasswordAuth(ABCInitiateAuth):
    @classmethod
    @decorators.boto3_handler(raise_as=exceptions.CognitoException)
    def call(
        cls,
        cognito_client: BaseClient,
        cognito_pool_client_id: str,
        username: str,
        password: str,

    ):
        response = cognito_client.initiate_auth(
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password,
            },
            ClientId=cognito_pool_client_id,
        )
        logger.info('Cognito UserPasswordAuth called', response=response)
        return cls.Response(response)


class RefreshTokenAuth(ABCInitiateAuth):
    @classmethod
    @decorators.boto3_handler(raise_as=exceptions.CognitoException)
    def call(
        cls,
        cognito_client: BaseClient,
        cognito_pool_client_id: str,
        refresh_token: str,
    ):
        response = cognito_client.initiate_auth(
            AuthFlow='REFRESH_TOKEN',
            AuthParameters={
                'REFRESH_TOKEN': refresh_token,
            },
            ClientId=cognito_pool_client_id,
        )
        logger.info('Cognito RefreshTokenAuth called', response=response)
        return cls.Response(response)


@dataclass
class ABCChallengeResponse(ABC, mixins.AsDictMixin):
    pass


@dataclass
class NewPasswordChallengeResponse(ABCChallengeResponse):
    NEW_PASSWORD: str
    USERNAME: str
    user_attributes: dict

    def __post_init__(self):
        self.set_attrs_from_user_attributes()

    def set_attrs_from_user_attributes(self):
        for k, v in self.user_attributes.items():
            self.__dict__[f'userAttributes.{k}'] = v
        self.__dict__.pop('user_attributes')


class RespondToAuthChallenge(ABCInitiateAuth):
    @classmethod
    @decorators.boto3_handler(raise_as=exceptions.CognitoException)
    def call(
        cls,
        cognito_client: BaseClient,
        cognito_pool_client_id: str,
        challenge_name: AuthChallenge,
        challenge_responses: ABCChallengeResponse,
        session: str = '',
    ):
        response = cognito_client.respond_to_auth_challenge(
            ChallengeName=challenge_name.value,
            ChallengeResponses=challenge_responses.as_dict(),
            ClientId=cognito_pool_client_id,
            Session=session,
        )
        logger.info('Cognito RespondToAuthChallenge called', response=response)
        return cls.Response(response)
