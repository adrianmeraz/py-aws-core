import json
import os

import boto3
from botocore.exceptions import ClientError

from . import exceptions


class SecretsManager:
    __secrets = None

    @classmethod
    def __get_secrets(cls, secret_name: str):
        try:
            sm_client = boto3.client('secretsmanager')
            r_secrets = sm_client.get_secret_value(
                SecretId=secret_name
            )
            return json.loads(r_secrets['SecretString'])
        except ClientError as e:
            # For a list of exceptions thrown, see
            # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
            raise exceptions.SecretsManagerException(e)

    @classmethod
    def get_secrets(cls):
        if not cls.__secrets:
            cls.__secrets = cls.__get_secrets(secret_name=cls.get_aws_secret_name())
        return cls.__secrets

    @classmethod
    def get_aws_secret_name(cls) -> str:
        return os.environ['AWS_SECRET_NAME']
