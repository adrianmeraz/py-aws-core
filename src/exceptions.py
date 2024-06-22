class AWSCoreException(Exception):
    ERROR_MESSAGE = 'A generic error has occurred'

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __str__(self):
        return self.ERROR_MESSAGE

# Boto3 Exceptions Located below:
# https://boto3.amazonaws.com/v1/documentation/api/latest/guide/error-handling.html#botocore-exceptions
# https://github.com/boto/botocore/blob/develop/botocore/exceptions.py


class CognitoException(AWSCoreException):
    ERROR_MESSAGE = 'An error occurred while attempting to access Cognito'


class DynamoDBException(AWSCoreException):
    ERROR_MESSAGE = 'An error occurred while attempting to access Dynamo DB'


class DBConditionCheckFailed(DynamoDBException):
    ERROR_MESSAGE = 'Condition Check Failed'


class DBTransactionCanceledException(DynamoDBException):
    ERROR_MESSAGE = 'Transaction cancelled'


class SecretsManagerException(AWSCoreException):
    ERROR_MESSAGE = 'An error occurred while fetching secrets'


ERR_CODE_MAP = {
    'ConditionalCheckFailedException': DBConditionCheckFailed,
    'TransactionCanceledException': DBTransactionCanceledException
}
