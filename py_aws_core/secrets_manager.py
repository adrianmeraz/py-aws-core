import json
import os

import boto3
from botocore.exceptions import ClientError

from py_aws_core import exceptions, logs

logger = logs.logger


class SecretsManager:
    """
    First checks environment variables for secrets.
    If secret not found, will attempt to pull from secrets manager
    """
    def __init__(self):
        self._boto_client = boto3.client('secretsmanager')
        self._secrets_map = dict()

    def get_secret(self, secret_name: str):
        if secret_value := os.environ.get(secret_name):
            logger.debug(f'Secret "{secret_name}" found in environment variables')
            return secret_value
        if val := self._secrets_map.get(secret_name):
            logger.debug(f'Secret "{secret_name}" found in cached secrets')
            return val
        try:
            r_secrets = self.boto_client.get_secret_value(SecretId=self.get_aws_secret_id)
            self._secrets_map = json.loads(r_secrets['SecretString'])
            return self._secrets_map[secret_name]
        except ClientError as e:
            # For a list of exceptions thrown, see
            # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
            raise exceptions.SecretsManagerException(e)

    @property
    def boto_client(self):
        return self._boto_client

    @boto_client.setter
    def boto_client(self, value):
        self._boto_client = value

    @property
    def get_aws_secret_id(self) -> str:
        try:
            return os.environ['AWS_SECRET_NAME']
        except KeyError:
            raise exceptions.SecretsManagerException('Missing environment variable "AWS_SECRET_NAME"')
