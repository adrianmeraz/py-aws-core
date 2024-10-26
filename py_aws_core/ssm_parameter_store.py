import json

from botocore.client import BaseClient
from botocore.exceptions import ClientError

from . import exceptions, logs, utils
from .secrets_interface import ISecrets

logger = logs.get_logger()


class SSMParameterStore(ISecrets):
    """
        First checks environment variables for secrets.
        Second, checks cached secrets
        Third, if secret not found, will attempt to pull from secrets manager
    """
    class Response:
        class Parameter:
            def __init__(self, data):
                self.Name = data['Name']
                self.Type = data['Type']
                self.Value = data['Value']
                self.Version = data['Version']
                self.Selector = data['Selector']
                self.SourceResult = data['SourceResult']
                self.LastModifiedDate = data['LastModifiedDate']
                self.ARN = data['ARN']
                self.DataType = data['DataType']

        def __init__(self, data):
            self.Parameter = self.Parameter(data['Parameter'])

        @property
        def parameter_json(self):
            return json.loads(self.Parameter.Value)

    AWS_SECRET_ID_KEY = 'AWS_SECRET_NAME'

    def __init__(self, boto_client: BaseClient, cached_secrets: dict = None):
        self._boto_client = boto_client
        self._cached_secrets = cached_secrets or dict()

    def get_secret(self, secret_name: str) -> str:
        if secret_value := utils.get_environment_variable(secret_name):
            logger.debug(f'Secret "{secret_name}" found in environment variables')
            return secret_value
        if val := self._cached_secrets.get(secret_name):
            logger.debug(f'Secret "{secret_name}" found in cached secrets')
            return val
        try:
            r_get_parameter = self._boto_client.get_parameter(Name=self.aws_secret_id)
            r_get_parameter = self.Response(r_get_parameter)
            self._cached_secrets = r_get_parameter.parameter_json
            return self._cached_secrets[secret_name]
        except ClientError as e:
            logger.exception(f'Error while trying to find secret "{secret_name}"')
            # For a list of exceptions thrown, see
            # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
            raise exceptions.SecretsManagerException(e)

    @property
    def aws_secret_id(self) -> str:
        if aws_secret_id := utils.get_environment_variable(self.AWS_SECRET_ID_KEY):
            return aws_secret_id
        raise exceptions.SecretsManagerException(f'Missing environment variable "{self.AWS_SECRET_ID_KEY}"')
