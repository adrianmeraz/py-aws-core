import json

from botocore.client import BaseClient
from botocore.exceptions import ClientError

from . import exceptions, logs, utils
from .secrets_interface import ISecrets

logger = logs.get_logger()


class SecretsManager(ISecrets):
    class Response:
        def __init__(self, data):
            self.ARN = data['ARN']
            self.Name = data['Name']
            self.VersionId = data['VersionId']
            self.SecretBinary = data['SecretBinary']
            self.SecretString = data['SecretString']
            self.VersionStages = data['VersionStages']

        @property
        def secret_json(self):
            return json.loads(self.SecretString)

    """
    First checks environment variables for secrets.
    If secret not found, will attempt to pull from secrets manager
    """
    AWS_SECRET_NAME = 'AWS_SECRET_NAME'

    def __init__(self, boto_client: BaseClient):
        self._boto_client = boto_client
        self._secrets_map = dict()

    def get_secret(self, secret_name: str):
        if secret_value := utils.get_environment_variable(secret_name):
            logger.debug(f'Secret "{secret_name}" found in environment variables')
            return secret_value
        if val := self._secrets_map.get(secret_name):
            logger.debug(f'Secret "{secret_name}" found in cached secrets')
            return val
        try:
            r_secrets = self.Response(self._boto_client.get_secret_value(SecretId=self.aws_secret_name))
            self._secrets_map = r_secrets.secret_json
            return self._secrets_map[secret_name]
        except ClientError as e:
            logger.exception(f'Error while trying to find secret "{secret_name}"')
            # For a list of exceptions thrown, see
            # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
            raise exceptions.SecretsManagerException(e)

    @property
    def aws_secret_name(self) -> str:
        if aws_secret_id := utils.get_environment_variable(self.AWS_SECRET_NAME):
            return aws_secret_id
        raise exceptions.SecretsManagerException(f'Missing environment variable "{self.AWS_SECRET_NAME}"')
