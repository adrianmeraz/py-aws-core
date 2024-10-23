class CoreException(Exception):
    HTTP_STATUS_CODE = 400
    ERROR_MESSAGE = 'A generic error has occurred'

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __str__(self):
        return self.build_str()

    def build_str(self):
        vals = [self.ERROR_MESSAGE]
        if self.args:
            vals += self.args
        if self.kwargs:
            vals += self.kwargs.values()
        return ', '.join([str(v) for v in vals])

# Boto3 Exceptions Located below:
# https://boto3.amazonaws.com/v1/documentation/api/latest/guide/error-handling.html#botocore-exceptions
# https://github.com/boto/botocore/blob/develop/botocore/exceptions.py


class APIException(CoreException):
    ERROR_MESSAGE = 'A generic API error occurred'


class NotAuthorizedException(APIException):
    HTTP_STATUS_CODE = 401
    ERROR_MESSAGE = 'Client is not authorized to take action'


class CookieDecodingError(APIException):
    ERROR_MESSAGE = 'Error while decoding binary cookies'


class MissingCookieException(APIException):
    ERROR_MESSAGE = 'Missing Cookie Exception'


class AWSCoreException(CoreException):
    ERROR_MESSAGE = 'A generic AWS error occurred'


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


class RouteAlreadyExists(CoreException):
    ERROR_MESSAGE = 'Route already exists'


class RouteNotFound(CoreException):
    HTTP_STATUS_CODE = 404
    ERROR_MESSAGE = 'Route Path Not Found'


class RouteMethodNotAllowed(CoreException):
    HTTP_STATUS_CODE = 405
    ERROR_MESSAGE = 'Route Method Not Allowed'


# Cognito Exceptions
class CognitoChallenge(CognitoException):
    ERROR_MESSAGE = 'Cognito Challenge Detected'


class InvalidRefreshToken(CognitoException):
    ERROR_MESSAGE = 'Invalid Refresh Token'


ERR_CODE_MAP = {
    'ConditionalCheckFailedException': DBConditionCheckFailed,
    'TransactionCanceledException': DBTransactionCanceledException
}
