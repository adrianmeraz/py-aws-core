import json

import boto3
from botocore.exceptions import ClientError

from . import exceptions, logs, utils

logger = logs.get_logger()


class SSMParameterStore:

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

    """
    First checks environment variables for secrets.
    If secret not found, will attempt to pull from secrets manager
    """
    AWS_SECRET_NAME_KEY = 'AWS_SECRET_NAME'

    def __init__(self):
        self._boto_client = None
        self._secrets_map = dict()

    def get_secret(self, secret_name: str):
        if secret_value := utils.get_environment_variable(secret_name):
            logger.debug(f'Secret "{secret_name}" found in environment variables')
            return secret_value
        if val := self._secrets_map.get(secret_name):
            logger.debug(f'Secret "{secret_name}" found in cached secrets')
            return val
        try:
            r_get_parameter = self.boto_client.get_parameter(Name=self.get_aws_secret_name)
            r_get_parameter = self.Response(r_get_parameter)
            self._secrets_map = r_get_parameter.parameter_json
            return self._secrets_map[secret_name]
        except ClientError as e:
            logger.exception(f'Error while trying to find secret "{secret_name}"')
            # For a list of exceptions thrown, see
            # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
            raise exceptions.SecretsManagerException(e)

    @property
    def boto_client(self):
        if not self._boto_client:
            self._boto_client = boto3.client('ssm')
        return self._boto_client

    @boto_client.setter
    def boto_client(self, value):
        self._boto_client = value

    def get_aws_secret_name(self) -> str:
        if aws_secret_id := utils.get_environment_variable(self.AWS_SECRET_NAME_KEY):
            return aws_secret_id
        raise exceptions.SecretsManagerException(f'Missing environment variable "{self.AWS_SECRET_NAME_KEY}"')


__secrets_manager = SSMParameterStore()


def get_secrets_manager() -> SSMParameterStore:
    """
    Reuses secrets manager across all modules for efficiency
    :return:
    """
    return __secrets_manager
